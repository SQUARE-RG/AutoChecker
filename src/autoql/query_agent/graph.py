"""Explicit generate/retrieve/compile/verify/repair graph, independent of codeql_agent."""
import json
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage, messages_to_dict
from langgraph.graph import StateGraph, START, END

from autoql.runtime import BudgetExceeded, remaining, write_json, write_text
from .state import QueryState
from .prompt_renderer import render
from .policy import generation_issues
from .nodes import extract_query
from autoql.timing import timed, timing_span


@timed('query', 'stage')
def run_query(task, spec, llm, retrieval, codeql, evaluator, limits, initial=None):
    output = Path(task.output_dir)
    tools = retrieval.tools()
    by_name = {t.name: t for t in tools}

    def persist(state):
        serial = dict(state)
        serial['messages'] = messages_to_dict(state.get('messages', []))
        write_json(output / 'query_state.json', serial)

    def checkpointed(fn):
        def wrapped(state):
            with timing_span('query.' + fn.__name__, attempt=state.get('attempt', 0)):
                result = fn(state)
            persist({**state, **result})
            return result
        return wrapped

    def prep(state):
        if state['attempt'] >= limits.max_query_attempts:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        return {'messages': render(spec, state.get('query_code', ''), state.get('feedback', ''),
                    state['history'], retrieval.summaries()), 'calls': 0, 'tool_calls': 0,
                'parse_retries': 0, 'route': 'model'}

    def model(state):
        remaining(llm.deadline, 1)
        if state['calls'] >= limits.query_model_calls_per_attempt:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        available = tools if state['calls'] < limits.query_model_calls_per_attempt - 1 and state['tool_calls'] < limits.query_tool_calls_per_attempt else []
        messages = state['messages']
        if not available:
            messages = messages + [HumanMessage(content='Retrieval budget closed. Return the complete query now or needs_evidence.')]
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
            from autoql.analysis_agent.validator import parse_json
            status = parse_json(text)
            if status.get('status') == 'needs_evidence':
                return {'final_status': 'needs_evidence', 'feedback': status.get('reason', ''), 'route': 'finish'}
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            query = extract_query(text)
        except ValueError as exc:
            if state['parse_retries'] < limits.query_parse_retries and state['calls'] < limits.query_model_calls_per_attempt:
                return {'messages': state['messages'] + [HumanMessage(content=str(exc))],
                        'parse_retries': state['parse_retries'] + 1, 'route': 'model'}
            return {'final_status': 'budget_exhausted', 'feedback': str(exc), 'route': 'finish'}
        attempt = state['attempt'] + 1
        query_path = codeql.pack / f'candidate-{attempt}.ql'
        write_text(query_path, query)
        write_text(output / 'attempts' / str(attempt) / 'query.ql', query)
        # A later evidence-refresh may replace vuln_spec.json; keep the precise
        # model and source bundle that produced each historical candidate.
        write_json(output / 'attempts' / str(attempt) / 'vuln_spec.json', spec)
        write_json(output / 'attempts' / str(attempt) / 'messages.json', messages_to_dict(state['messages']))
        return {'query_code': query, 'query_path': str(query_path), 'attempt': attempt, 'route': 'compile'}

    def compile_node(state):
        issues = generation_issues(state['query_code'], spec, task)
        if issues:
            write_json(output / 'attempts' / str(state['attempt']) / 'policy.json', {'issues': issues})
            if state['semantic_repairs'] >= limits.max_semantic_repairs:
                return {'final_status': 'budget_exhausted', 'route': 'finish'}
            return {'semantic_repairs': state['semantic_repairs'] + 1, 'feedback': '\n'.join(issues),
                    'history': state['history'] + [f"Attempt {state['attempt']}: generalization/safety policy failed"], 'route': 'prep'}
        result = codeql.compile(state['query_path'], state['attempt'])
        if result['returncode'] == 0:
            return {'last_compilable_query': state['query_code'], 'route': 'verify'}
        if state['compile_repairs'] >= limits.max_compile_repairs:
            return {'final_status': 'budget_exhausted', 'route': 'finish'}
        feedback = (result['stderr'] + result['stdout'])[-16000:]
        return {'compile_repairs': state['compile_repairs'] + 1, 'feedback': feedback,
                'history': state['history'] + [f"Attempt {state['attempt']}: compilation failed"], 'route': 'prep'}

    def verify(state):
        old, old_run = codeql.analyze(task.buggy_db_path, state['query_path'], 'buggy', state['attempt'])
        new, new_run = codeql.analyze(task.fixed_db_path, state['query_path'], 'fixed', state['attempt'])
        with timing_span('query.evaluate', attempt=state['attempt']):
            result = evaluator.evaluate(old, new)
        result['runs'] = {'buggy': old_run, 'fixed': new_run}
        write_json(output / 'attempts' / str(state['attempt']) / 'evaluation.json', result)
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
        return {'evaluation': result, 'semantic_repairs': state['semantic_repairs'] + 1,
                'feedback': feedback, 'history': state['history'] + [f"Attempt {state['attempt']}: target verification failed"], 'route': 'prep'}

    def finish(state):
        persist(state)
        if state.get('final_status') == 'query_verified':
            write_text(output / 'final.ql', state['query_code'])
            return {'final_query_path': str(output / 'final.ql')}
        return {}

    graph = StateGraph(QueryState)
    for name, fn in [('prep', prep), ('model', model), ('tools', call_tools), ('extract', extract),
                     ('compile', compile_node), ('verify', verify), ('finish', finish)]:
        graph.add_node(name, checkpointed(fn))
    graph.add_conditional_edges(START, lambda s: s.get('route', 'prep'))
    for name in ('prep', 'model', 'tools', 'extract', 'compile', 'verify'):
        graph.add_conditional_edges(name, lambda s: s['route'])
    graph.add_edge('finish', END)
    start = initial or {'attempt': 0, 'compile_repairs': 0, 'semantic_repairs': 0, 'history': [], 'query_code': ''}
    return graph.compile().invoke(start, {'recursion_limit': limits.query_graph_recursion_limit})
