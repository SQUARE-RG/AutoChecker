"""CLI: one curated fix commit -> analysis -> independently validated query."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import time
import traceback
import json
import fcntl

from autoql.runtime import Limits, BudgetExceeded, write_json
from autoql.task_loader import load_task, PatchTask, UnsupportedInput
from autoql.timing import TimingRecorder, CURRENT, timing_span


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dataset', type=Path)
    parser.add_argument('--limits', type=Path, help='JSON overrides for default budgets/timeouts')
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Resume --output without resetting budgets/deadline')
    args = parser.parse_args()
    output = args.output or args.root / 'autoql_runs' / (args.commit[:12] + '-' + time.strftime('%Y%m%d-%H%M%S'))
    limits = Limits(**json.loads(args.limits.read_text())) if args.limits else Limits()
    deadline = time.time() + limits.task_wall_timeout_seconds
    final = {'final_status': 'infrastructure_error', 'manual_review': 'pending'}
    owned_run = False
    run_lock = None
    llm = None
    timing = TimingRecorder()
    timing_token = CURRENT.set(timing)
    session_span = timing.span('task.session', 'session')
    session_span.__enter__()
    try:
        if args.resume:
            if not args.output:
                raise ValueError('--resume requires --output')
            manifest = json.loads((output / 'manifest.json').read_text())
            if manifest['fix_commit'] != args.commit:
                raise ValueError('Resume commit does not match manifest')
            task = PatchTask(**{k: v for k, v in manifest.items() if k in PatchTask.__dataclass_fields__})
            limits = Limits(**json.loads((output / 'limits.json').read_text()))
            if (output / 'run_control.json').exists():
                deadline = json.loads((output / 'run_control.json').read_text())['deadline']
            if (output / 'budget.json').exists():
                deadline = json.loads((output / 'budget.json').read_text())['deadline']
            prior = json.loads((output / 'result.json').read_text()) if (output / 'result.json').exists() else {}
            if prior.get('final_status') == 'query_verified':
                final = prior
                return 0 
        else:
            task = load_task(args.commit, args.root.resolve(), output, args.dataset)
        run_lock = (output / '.run.lock').open('a')
        fcntl.flock(run_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        owned_run = True
        timing.attach(output, resume=args.resume)
        write_json(output / 'run_control.json', {'deadline': deadline})
        write_json(output / 'limits.json', asdict(limits))
        from autoql.query_agent.codeql import CodeQL
        from autoql.query_agent.evaluator import Evaluator
        with timing_span('preflight', 'stage'):
            codeql = CodeQL(output, limits, deadline)
            buggy = codeql.structure(task.buggy_db_path, 'buggy')
            fixed = codeql.structure(task.fixed_db_path, 'fixed')
            evaluator = Evaluator(task, buggy, fixed)
        write_json(output / 'preflight.json', {'buggy_functions': len(buggy), 'fixed_functions': len(fixed),
            'granularity': evaluator.granularity, 'fixed_mapping_unresolved': evaluator.mapping_unknown,
            'deleted_targets': evaluator.deleted, 'java_pack': str(codeql.java_pack)})
        if args.preflight_only:
            final['final_status'] = 'preflight_passed'
        else:
            from autoql.llm import StreamingLLM
            from autoql.analysis_agent.agent import AnalysisAgent
            from autoql.analysis_agent.evidence_registry import EvidenceRegistry
            from autoql.query_agent.tools import RetrievalContext
            from autoql.query_agent.graph import run_query
            llm = StreamingLLM(args.root, output, limits, deadline)
            analysis = AnalysisAgent(task, EvidenceRegistry(task), llm, limits)
            with timing_span('retrieval.index'):
                retrieval = RetrievalContext([codeql.java_pack, codeql.query_pack], output, limits)
            spec_path = output / 'vuln_spec.json'
            spec = json.loads(spec_path.read_text()) if args.resume and spec_path.exists() else analysis.run()
            initial = None
            if args.resume and (output / 'query_state.json').exists():
                from langchain_core.messages import messages_from_dict
                initial = json.loads((output / 'query_state.json').read_text())
                initial['messages'] = messages_from_dict(initial['messages'])
                # A parser upgrade can consume an already completed response;
                # do not call the model again or reset any budget/deadline.
                if (initial.get('final_status') == 'budget_exhausted' and
                        initial.get('route') == 'finish' and
                        initial.get('feedback', '').startswith('Return exactly one complete query_code:')):
                    from autoql.query_agent.nodes import extract_query
                    try:
                        extract_query(initial['messages'][-1].content)
                    except (ValueError, IndexError, TypeError):
                        pass
                    else:
                        write_json(output / 'parser_recovery.json', {
                            'reason': 'Accept unique typed code fence without optional query_code label',
                            'preserved_deadline': deadline, 'additional_model_calls': 0})
                        initial.update(route='extract', final_status='')
            refresh_path = output / 'evidence_refresh.json'
            refresh_count = json.loads(refresh_path.read_text())['count'] if refresh_path.exists() else 0
            for refresh in range(refresh_count, limits.evidence_refresh_limit + 1):
                if spec.get('status'):
                    final.update(final_status=spec['status'], reason=spec.get('reason'))
                    break
                state = run_query(task, spec, llm, retrieval, codeql, evaluator, limits, initial)
                final.update({k: v for k, v in state.items() if k not in ('messages', 'query_code')})
                if state['final_status'] != 'needs_evidence' or refresh == limits.evidence_refresh_limit:
                    break
                write_json(refresh_path, {'count': refresh + 1})
                spec = analysis.run('Query generation needs additional source evidence: ' + state['feedback'] +
                    '. Explore only what is missing, register it, and submit an updated AnalysisBrief.')
                initial = {**state, 'final_status': '', 'route': 'prep', 'feedback': 'Evidence refreshed; generate a complete query.'}
    except UnsupportedInput as exc:
        final.update(final_status='unsupported_input', reason=str(exc))
    except BudgetExceeded as exc:
        final.update(final_status='budget_exhausted', reason=str(exc))
    except Exception as exc:
        final.update(final_status='infrastructure_error', error_type=type(exc).__name__, reason=str(exc))
        traceback.print_exc()
    finally:
        if llm:
            try:
                llm.close()
            except Exception as exc:
                final['client_cleanup_error'] = type(exc).__name__
        session_span.__exit__(None, None, None)
        CURRENT.reset(timing_token)
        # Never replace an existing run; loader enforces a fresh output directory.
        if owned_run:
            timing.summarize(final['final_status'])
            write_json(output / 'result.json', final)
        if run_lock:
            run_lock.close()
        print('AutoQL status:', final['final_status'], 'Artifacts:', output, flush=True)
    return 0 if final['final_status'] in ('query_verified', 'preflight_passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
