"""Explicit generate/retrieve/compile/verify/repair graph, independent of codeql_agent."""
import json
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage, messages_to_dict
from langgraph.graph import StateGraph, START, END

from autoql.runtime import BudgetExceeded, remaining, write_json, write_text
from .state import QueryState
from .prompt_renderer import render
from .policy import generation_issues
from .nodes import extract_needs_evidence, extract_query
from .tools import EvidenceAstContext
from autoql.timing import timed, timing_span


@timed('query', 'stage')
def run_query(task, spec, llm, retrieval, codeql, evaluator, limits, initial=None):
    output = Path(task.output_dir)
    ast_context = EvidenceAstContext(task, spec, limits)
    tools = retrieval.tools() + ast_context.tools()
    by_name = {t.name: t for t in tools}

    def persist(state):
        serial = dict(state)
        serial['messages'] = messages_to_dict(state.get('messages', []))
        write_json(output / 'query_state.json', serial)

    def checkpointed(fn):
        def wrapped(state):
            with timing_span(
                    'query.' + fn.__name__,
                    attempt=state.get('candidate_count', state.get('attempt', 0))):
                result = fn(state)
            persist({**state, **result})
            return result
        return wrapped

    def prep(state):
        candidate_count = state.get('candidate_count', state.get('attempt', 0))
        phase = state.get('generation_phase', 'initial')
        if candidate_count >= limits.max_query_attempts:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        if (phase == 'compile_repair' and
                state['compile_repairs'] >= limits.max_compile_repairs):
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        if (phase == 'semantic_repair' and
                state['semantic_repairs'] >= limits.max_semantic_repairs):
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        return {'messages': render(spec, state.get('query_code', ''), state.get('feedback', ''),
                    retrieval.summaries(), phase), 'calls': 0, 'tool_calls': 0,
                'parse_retries': 0, 'route': 'model'}

    def model(state):
        remaining(llm.deadline, 1)
        if state['calls'] >= limits.query_model_calls_per_attempt:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        available = tools if state['calls'] < limits.query_model_calls_per_attempt - 1 and state['tool_calls'] < limits.query_tool_calls_per_attempt else []
        messages = state['messages']
        if not available:
            messages = messages + [HumanMessage(
                content='Retrieval budget closed. Return the complete query now.')]
        # Reserve before invoking: a crash/restart must not replenish this attempt's calls.
        persist({**state, 'messages': messages, 'calls': state['calls'] + 1, 'route': 'model'})
        response = llm.call(messages, available, 'query')
        updated = {'messages': messages + [response], 'calls': state['calls'] + 1,
                   'route': 'tools' if response.tool_calls else 'extract'}
        persist({**state, **updated})
        return updated

    def call_tools(state):
        responses, count = [], state['tool_calls']
        for call in state['messages'][-1].tool_calls:
            if count >= limits.query_tool_calls_per_attempt or call['name'] not in by_name:
                text = 'Tool unavailable or budget exhausted; submit the query.'
            else:
                count += 1
                # Reserve before execution so an interrupted tool batch cannot
                # replenish retrieval allowances when this state is resumed.
                persist({**state, 'tool_calls': count, 'route': 'tools'})
                try:
                    text = by_name[call['name']].invoke(call['args'])
                except Exception as exc:
                    text = 'Retrieval failed: ' + type(exc).__name__
            responses.append(ToolMessage(content=text, tool_call_id=call['id']))
        return {'messages': state['messages'] + responses, 'tool_calls': count, 'route': 'model'}

    def extract(state):
        text = state['messages'][-1].content
        try:
            evidence_request = extract_needs_evidence(text)
        except ValueError:
            evidence_request = None
        if evidence_request is not None:
            phase = state.get('generation_phase', 'initial')
            candidate_count = state.get(
                'candidate_count', state.get('attempt', 0))
            request_count = state.get('evidence_request_count', 0)
            if phase == 'initial' and candidate_count == 0:
                if request_count >= limits.evidence_refresh_limit:
                    return {
                        'final_status': 'needs_review',
                        'feedback': (
                            'Evidence request limit reached. Last request: ' +
                            evidence_request.reason),
                        'route': 'finish',
                    }
                request = evidence_request.model_dump()
                return {
                    'final_status': 'needs_evidence',
                    'evidence_request': request,
                    'feedback': evidence_request.reason,
                    'route': 'finish',
                }
            error = (
                f'needs_evidence is not allowed during {phase}. '
                'Return exactly one complete ```query fenced block without '
                'additional text.')
            if (state['parse_retries'] < limits.query_parse_retries and
                    state['calls'] < limits.query_model_calls_per_attempt):
                return {
                    'messages': state['messages'] + [HumanMessage(content=error)],
                    'parse_retries': state['parse_retries'] + 1,
                    'route': 'model',
                }
            return {
                'final_status': 'budget_exhausted',
                'feedback': error,
                'route': 'finish',
            }
        try:
            query = extract_query(text)
        except ValueError as exc:
            if state['parse_retries'] < limits.query_parse_retries and state['calls'] < limits.query_model_calls_per_attempt:
                return {'messages': state['messages'] + [HumanMessage(content=str(exc))],
                        'parse_retries': state['parse_retries'] + 1, 'route': 'model'}
            return {'final_status': 'budget_exhausted', 'feedback': str(exc), 'route': 'finish'}
        phase = state.get('generation_phase', 'initial')
        candidate_count = state.get('candidate_count', state.get('attempt', 0)) + 1
        query_path = codeql.pack / f'candidate-{candidate_count}.ql'
        write_text(query_path, query)
        write_text(output / 'attempts' / str(candidate_count) / 'query.ql', query)
        # A later evidence-refresh may replace vuln_spec.json; keep the precise
        # model and source bundle that produced each historical candidate.
        write_json(output / 'attempts' / str(candidate_count) / 'vuln_spec.json', spec)
        write_json(output / 'attempts' / str(candidate_count) / 'messages.json', messages_to_dict(state['messages']))
        updates = {
            'query_code': query,
            'query_path': str(query_path),
            'candidate_count': candidate_count,
            # Compatibility alias for existing artifacts and consumers.
            'attempt': candidate_count,
            'route': 'compile',
        }
        if phase == 'compile_repair':
            updates['compile_repairs'] = state['compile_repairs'] + 1
        elif phase == 'semantic_repair':
            updates['semantic_repairs'] = state['semantic_repairs'] + 1
        return updates

    def compile_node(state):
        candidate = state['candidate_count']
        result = codeql.compile(state['query_path'], candidate)
        if result['returncode'] == 0:
            return {'last_compilable_query': state['query_code'], 'route': 'policy'}
        if state['compile_repairs'] >= limits.max_compile_repairs:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        feedback = '\n\n'.join(
            text.strip()
            for text in (result.get('stderr', ''), result.get('stdout', ''))
            if text.strip()
        ) or 'CodeQL compilation failed without diagnostic output.'
        return {
            'generation_phase': 'compile_repair',
            'feedback': feedback,
            'history': state['history'] + [
                f'Candidate {candidate}: compilation failed'],
            'route': 'prep',
        }

    def policy(state):
        candidate = state['candidate_count']
        issues = generation_issues(state['query_code'], spec, task)
        if issues:
            write_json(output / 'attempts' / str(candidate) / 'policy.json', {'issues': issues})
            if state['semantic_repairs'] >= limits.max_semantic_repairs:
                return {'final_status': 'budget_exhausted', 'route': 'finish'}
            return {
                'generation_phase': 'semantic_repair',
                'feedback': '\n'.join(issues),
                'history': state['history'] + [
                    f'Candidate {candidate}: generalization/safety policy failed'],
                'route': 'prep',
            }
        return {'route': 'verify'}

    def verify(state):
        candidate = state['candidate_count']
        old, old_run = codeql.analyze(task.buggy_db_path, state['query_path'], 'buggy', candidate)
        new, new_run = codeql.analyze(task.fixed_db_path, state['query_path'], 'fixed', candidate)
        with timing_span('query.evaluate', attempt=candidate):
            result = evaluator.evaluate(old, new)
        result['runs'] = {'buggy': old_run, 'fixed': new_run}
        write_json(output / 'attempts' / str(candidate) / 'evaluation.json', result)
        if result['verified']:
            return {'evaluation': result, 'final_status': 'query_verified',
                    'feedback': '', 'route': 'finish'}
        if result['fixed_target_status'] == 'unresolved':
            return {'evaluation': result, 'final_status': 'needs_review', 'route': 'finish'}
        if state['semantic_repairs'] >= limits.max_semantic_repairs:
            return {'evaluation': result, 'final_status': 'budget_exhausted', 'route': 'finish'}
        # No target names, coordinates, or hidden labels in model feedback.
        feedback = json.dumps({'target_hit': result['buggy']['hit_function'] if evaluator.granularity == 'function' else result['buggy']['hit_file'],
            'fixed_target_persists': result['fixed_target_status'] == 'still_present',
            'buggy_total_results': result['buggy']['num_results'], 'fixed_total_results': result['fixed']['num_results']})
        return {
            'evaluation': result,
            'generation_phase': 'semantic_repair',
            'feedback': feedback,
            'history': state['history'] + [
                f'Candidate {candidate}: target verification failed'],
            'route': 'prep',
        }

    def finish(state):
        persist(state)
        if state.get('final_status') == 'query_verified':
            write_text(output / 'final.ql', state['query_code'])
            return {'final_query_path': str(output / 'final.ql')}
        return {}

    graph = StateGraph(QueryState)
    for name, fn in [('prep', prep), ('model', model), ('tools', call_tools), ('extract', extract),
                     ('compile', compile_node), ('policy', policy), ('verify', verify), ('finish', finish)]:
        graph.add_node(name, checkpointed(fn))
    graph.add_conditional_edges(START, lambda s: s.get('route', 'prep'))
    for name in ('prep', 'model', 'tools', 'extract', 'compile', 'policy', 'verify'):
        graph.add_conditional_edges(name, lambda s: s['route'])
    graph.add_edge('finish', END)
    start = dict(initial or {})
    start.setdefault('candidate_count', start.get('attempt', 0))
    start.setdefault('attempt', start['candidate_count'])
    start.setdefault('compile_repairs', 0)
    start.setdefault('semantic_repairs', 0)
    start.setdefault('evidence_request_count', 0)
    start.setdefault('history', [])
    start.setdefault('query_code', '')
    if 'generation_phase' not in start:
        last_event = start['history'][-1] if start['history'] else ''
        if 'compilation failed' in last_event:
            start['generation_phase'] = 'compile_repair'
        elif start['candidate_count']:
            start['generation_phase'] = 'semantic_repair'
        else:
            start['generation_phase'] = 'initial'
    return graph.compile().invoke(start, {'recursion_limit': limits.query_graph_recursion_limit})
