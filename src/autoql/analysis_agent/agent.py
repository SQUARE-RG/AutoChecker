"""Deep Agents repository exploration followed by fresh-context evidence validation."""
import json
import threading
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.backends.protocol import WriteResult, EditResult
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage, ToolMessage, messages_to_dict, messages_from_dict

from autoql.llm import TrackedChatModel
from autoql.runtime import BudgetExceeded, remaining, write_json
from autoql.timing import timed
from .prompts import explorer_system_prompt, spec_composer_prompt, spec_repair_prompt
from .schemas import AnalysisBrief
from .validator import (SpecValidationError, enriched_brief, finalize,
                        validate_brief)
from .vulnerability_metadata import prompt_section


class ReadOnlySourceBackend(FilesystemBackend):
    def write(self, file_path, content):
        if not file_path.startswith('/work/'):
            return WriteResult(error='Read-only input/source snapshot')
        return super().write(file_path, content)

    def edit(self, file_path, old_string, new_string, replace_all=False):
        if not file_path.startswith('/work/'):
            return EditResult(error='Read-only input/source snapshot')
        return super().edit(file_path, old_string, new_string, replace_all)


class AnalysisPolicy(AgentMiddleware):
    ALLOWED = {'ls', 'glob', 'grep', 'read_file', 'write_file', 'edit_file',
               'write_todos', 'AnalysisBrief'}

    def __init__(self, llm, limits, output):
        self.llm, self.limits, self.output = llm, limits, Path(output)
        self.calls = 0
        self.lock = threading.RLock()
        if (self.output / 'analysis_budget.json').exists():
            self.calls = json.loads((self.output / 'analysis_budget.json').read_text())['tool_calls']

    def wrap_model_call(self, request, handler):
        write_json(self.output / 'analysis_messages.json', messages_to_dict(request.messages))
        tools = [tool for tool in request.tools if getattr(tool, 'name', None) in self.ALLOWED]
        left = self.limits.analysis_max_model_calls - self.llm.counts['analysis']
        notice = (f'Runtime budget: {left} model calls, '
                  f'{self.limits.analysis_max_tool_calls - self.calls} tool calls remain. ')
        if left <= 6:
            notice += 'Stop broad exploration and submit AnalysisBrief with exact source coordinates now.'
        if (self.calls >= self.limits.analysis_max_tool_calls or
                self.llm.counts['analysis'] >= self.limits.analysis_max_model_calls - 1):
            tools = [tool for tool in tools if getattr(tool, 'name', None) == 'AnalysisBrief']
        return handler(request.override(
            tools=tools, messages=request.messages + [HumanMessage(content=notice)]))

    def wrap_tool_call(self, request, handler):
        with self.lock:
            return self._tool_call(request, handler)

    @timed('analysis.tool')
    def _tool_call(self, request, handler):
        remaining(self.llm.deadline, 1)
        call = request.tool_call
        if call['name'] not in self.ALLOWED or self.calls >= self.limits.analysis_max_tool_calls:
            return ToolMessage(content='Tool unavailable/budget exhausted. Finish analysis.',
                               tool_call_id=call['id'])
        self.calls += 1
        write_json(self.output / 'analysis_budget.json', {'tool_calls': self.calls})
        result = handler(request)
        with (self.output / 'analysis_tools.jsonl').open('a') as handle:
            handle.write(json.dumps({'name': call['name'], 'args': call['args'],
                                     'result': str(result)}, ensure_ascii=False) + '\n')
        return result


class AnalysisAgent:
    def __init__(self, task, registry, llm, limits, vulnerability_metadata=None):
        self.task, self.registry, self.llm, self.limits = task, registry, llm, limits
        self.vulnerability_metadata = vulnerability_metadata
        self.messages = []
        messages_path = Path(task.output_dir) / 'analysis_messages.json'
        if messages_path.exists():
            self.messages = messages_from_dict(json.loads(messages_path.read_text()))

        self.policy = AnalysisPolicy(llm, limits, task.output_dir)
        self.agent = create_deep_agent(
            model=TrackedChatModel(gateway=llm), tools=[],
            system_prompt=explorer_system_prompt(),
            backend=ReadOnlySourceBackend(root_dir=task.workspace, virtual_mode=True),
            middleware=[self.policy],
            response_format=ToolStrategy(AnalysisBrief, handle_errors=True))

    @staticmethod
    def _composition_input(brief, current=None):
        value = {'analysis_brief': brief}
        if current is not None:
            value['current_output'] = current
        return json.dumps(value, ensure_ascii=False, indent=2)

    def _compose(self, brief, current=None, issues=None):
        prompt = spec_repair_prompt(issues) if issues is not None else spec_composer_prompt()
        composer = create_agent(
            model=TrackedChatModel(gateway=self.llm), tools=[], system_prompt=prompt,
            response_format=ToolStrategy(AnalysisBrief, handle_errors=True))
        result = composer.invoke({'messages': [HumanMessage(
            content=self._composition_input(brief, current))]}, {'recursion_limit': 64})
        structured = result.get('structured_response')
        if structured is None:
            raise ValueError('Spec composer returned no structured response')
        return (structured.model_dump(exclude_none=True)
                if hasattr(structured, 'model_dump') else structured)

    def _initial_request(self, additional_request):
        sections = []
        metadata = prompt_section(getattr(self, 'vulnerability_metadata', None))
        if metadata:
            sections.append(metadata)
        sections.append(
            '## Commit message:\n' +
            json.dumps(self.task.fix_commit_message, ensure_ascii=False) +
            '\n\nPatch: /input/patch.diff\nBuggy source: /buggy\nFixed source: /fixed\n\n'
            'Analyze the patch and return vulnerability_summary with exact evidence locations. '
            'Use the displayed source line numbers for start_line and end_line.')
        request = '\n\n'.join(sections)
        if additional_request:
            request += '\n\nAdditional validation request:\n' + additional_request
        return request

    @timed('analysis', 'stage')
    def run(self, additional_request=''):
        self.messages.append(HumanMessage(content=self._initial_request(additional_request)))
        brief = None
        for correction in range(self.limits.spec_repair_limit + 1):
            result = self.agent.invoke({'messages': self.messages}, {'recursion_limit': 256})
            self.messages = result['messages']
            write_json(Path(self.task.output_dir) / 'analysis_messages.json',
                       messages_to_dict(self.messages))
            structured = result.get('structured_response')
            if structured is None:
                raise ValueError('Analysis explorer returned no structured response')
            try:
                brief = validate_brief(structured, self.registry)
                break
            except SpecValidationError as exc:
                if correction == self.limits.spec_repair_limit:
                    raise BudgetExceeded(
                        'Analysis brief validation exhausted: ' + str(exc)) from exc
                self.messages.append(HumanMessage(
                    content='AnalysisBrief location validation failed: ' +
                    json.dumps(exc.issues, ensure_ascii=False) +
                    '. Correct the summary and evidence coordinates.'))

        complete_brief = enriched_brief(brief, self.registry)
        write_json(Path(self.task.output_dir) / 'analysis_brief.json', complete_brief)

        # Spec Composer is intentionally disabled. The explorer already returns
        # the complete AnalysisBrief semantics; the program validates its source
        # locations, extracts canonical code from Git, and persists that result
        # directly. Keep _compose() available for a future optional validator.
        #
        # Previous flow (disabled):
        #   draft = self._compose(complete_brief)
        #   spec = finalize(draft, brief, self.registry)
        spec = finalize(brief, brief, self.registry)
        write_json(Path(self.task.output_dir) / 'vuln_spec.json', spec)
        return spec
