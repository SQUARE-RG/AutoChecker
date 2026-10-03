"""Deep Agents file exploration; read-only source backend and bounded tool access."""
import json
import threading
from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.backends.protocol import WriteResult, EditResult
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage, ToolMessage, messages_to_dict, messages_from_dict
from langchain_core.tools import tool

from autoql.llm import TrackedChatModel
from autoql.runtime import BudgetExceeded, remaining, write_json
from autoql.timing import timed
from .prompts import explorer_system_prompt, spec_composer_prompt, spec_repair_prompt
from .schemas import AnalysisBrief, SPEC_SCHEMAS
from .validator import SpecValidationError, finalize, validate_brief


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
               'write_todos', 'capture_evidence', 'AnalysisBrief'}

    def __init__(self, llm, limits, output):
        self.llm, self.limits, self.output = llm, limits, Path(output)
        self.calls = 0
        self.lock = threading.RLock()
        if (self.output / 'analysis_budget.json').exists():
            self.calls = json.loads((self.output / 'analysis_budget.json').read_text())['tool_calls']

    def wrap_model_call(self, request, handler):
        write_json(self.output / 'analysis_messages.json', messages_to_dict(request.messages))
        tools = [t for t in request.tools if getattr(t, 'name', None) in self.ALLOWED]
        left = self.limits.analysis_max_model_calls - self.llm.counts['analysis']
        notice = f'Runtime budget: {left} model calls, {self.limits.analysis_max_tool_calls - self.calls} tool calls remain. '
        if left <= 6:
            notice += 'Stop broad exploration. Register necessary evidence and submit AnalysisBrief now.'
        if self.calls >= self.limits.analysis_max_tool_calls or self.llm.counts['analysis'] >= self.limits.analysis_max_model_calls - 1:
            tools = [t for t in tools if getattr(t, 'name', None) == 'AnalysisBrief']
        return handler(request.override(tools=tools, messages=request.messages + [HumanMessage(content=notice)]))

    def wrap_tool_call(self, request, handler):
        with self.lock:
            return self._tool_call(request, handler)

    @timed('analysis.tool')
    def _tool_call(self, request, handler):
        remaining(self.llm.deadline, 1)
        call = request.tool_call
        if call['name'] not in self.ALLOWED or self.calls >= self.limits.analysis_max_tool_calls:
            return ToolMessage(content='Tool unavailable/budget exhausted. Finish analysis.', tool_call_id=call['id'])
        self.calls += 1
        write_json(self.output / 'analysis_budget.json', {'tool_calls': self.calls})
        result = handler(request)
        with (self.output / 'analysis_tools.jsonl').open('a') as handle:
            handle.write(json.dumps({'name': call['name'], 'args': call['args'], 'result': str(result)}, ensure_ascii=False) + '\n')
        return result


class AnalysisAgent:
    def __init__(self, task, registry, llm, limits):
        self.task, self.registry, self.llm, self.limits = task, registry, llm, limits
        self.messages = []
        messages_path = Path(task.output_dir) / 'analysis_messages.json'
        if messages_path.exists():
            self.messages = messages_from_dict(json.loads(messages_path.read_text()))

        @tool
        def capture_evidence(revision: Literal['buggy', 'fix'], file: str, snippet: str) -> dict:
            """Register an exact continuous source snippet from a fixed Git revision; returns precise lines and ID."""
            return registry.capture(revision, file, snippet)

        self.policy = AnalysisPolicy(llm, limits, task.output_dir)
        self.agent = create_deep_agent(model=TrackedChatModel(gateway=llm),
            tools=[capture_evidence], system_prompt=explorer_system_prompt(),
            backend=ReadOnlySourceBackend(root_dir=task.workspace, virtual_mode=True),
            middleware=[self.policy], response_format=ToolStrategy(AnalysisBrief, handle_errors=True))

    def _evidence(self, ids):
        return [self.registry.entries[key] for key in dict.fromkeys(ids)]

    def _composition_input(self, brief, draft=None):
        value = {
            'analysis_brief': brief.model_dump(exclude_none=True),
            'registered_evidence': self._evidence(brief.evidence_ids),
        }
        if draft is not None:
            value['current_complete_spec'] = draft
        return json.dumps(value, ensure_ascii=False, indent=2)

    def _compose(self, brief, draft=None, issues=None):
        kind = brief.analysis_kind
        schema = SPEC_SCHEMAS[kind]
        prompt = (spec_repair_prompt(kind, issues) if issues is not None
                  else spec_composer_prompt(kind))
        composer = create_agent(model=TrackedChatModel(gateway=self.llm), tools=[],
            system_prompt=prompt, response_format=ToolStrategy(schema, handle_errors=True))
        result = composer.invoke({'messages': [HumanMessage(
            content=self._composition_input(brief, draft))]}, {'recursion_limit': 64})
        structured = result.get('structured_response')
        if structured is None:
            raise ValueError('Spec composer returned no structured response')
        return structured.model_dump(exclude_none=True) if hasattr(structured, 'model_dump') else structured

    @timed('analysis', 'stage')
    def run(self, additional_request=''):
        self.messages.append(HumanMessage(content=additional_request or
            'Analyze the patch at /input/patch.diff. Its commit message is at '
            '/input/fix_commit_message.txt. Explore /buggy and /fixed, register evidence, '
            'and submit the structured AnalysisBrief. Begin by reading the commit message.'))
        brief = None
        for correction in range(self.limits.spec_repair_limit + 1):
            result = self.agent.invoke({'messages': self.messages}, {'recursion_limit': 256})
            self.messages = result['messages']
            write_json(Path(self.task.output_dir) / 'analysis_messages.json', messages_to_dict(self.messages))
            structured = result.get('structured_response')
            if structured is None:
                raise ValueError('Analysis explorer returned no structured response')
            try:
                brief = validate_brief(structured, self.registry)
                break
            except SpecValidationError as exc:
                if correction == self.limits.spec_repair_limit:
                    raise BudgetExceeded('Analysis brief validation exhausted: ' + str(exc)) from exc
                self.messages.append(HumanMessage(content='AnalysisBrief evidence validation failed: ' +
                    json.dumps(exc.issues, ensure_ascii=False) +
                    '. Correct the brief, registering evidence if necessary.'))

        if brief.status != 'finding':
            terminal = {'status': brief.status, 'reason': brief.reason}
            write_json(Path(self.task.output_dir) / 'vuln_spec.json', terminal)
            return terminal

        repairs_path = Path(self.task.output_dir) / 'spec_repairs.json'
        used = json.loads(repairs_path.read_text())['count'] if repairs_path.exists() else 0
        draft = self._compose(brief)
        for repair in range(used, self.limits.spec_repair_limit + 1):
            try:
                spec = finalize(draft, self.registry)
                write_json(Path(self.task.output_dir) / 'vuln_spec.json', spec)
                return spec
            except SpecValidationError as exc:
                if repair == self.limits.spec_repair_limit:
                    raise BudgetExceeded('Spec validation exhausted: ' + str(exc)) from exc
                write_json(repairs_path, {'count': repair + 1})
                draft = self._compose(brief, draft=draft, issues=exc.issues)
