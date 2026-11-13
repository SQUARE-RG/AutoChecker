"""CLI entry point for running AutoQL in a selected pipeline mode."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import time
import traceback
import json
import fcntl

from autoql.runtime import Limits, BudgetExceeded, write_json
from autoql.task_loader import (PatchTask, UnsupportedInput, load_task,
                                validate_codeql_databases)
from autoql.timing import CURRENT, TimingRecorder, timing_span


def _load_v2_spec(path: Path) -> dict:
    from autoql.analysis_agent.schemas import VulnerabilitySpec
    value = json.loads(path.read_text(encoding='utf-8'))
    return VulnerabilitySpec.model_validate(value).model_dump()


def _load_query_state(path: Path, deadline: float) -> dict | None:
    if not path.is_file():
        return None
    from langchain_core.messages import messages_from_dict
    state = json.loads(path.read_text(encoding='utf-8'))
    state['messages'] = messages_from_dict(state.get('messages', []))
    # A parser upgrade may be able to consume an already completed response
    # without spending another model call or changing the saved deadline.
    if (state.get('final_status') == 'budget_exhausted' and
            state.get('route') == 'finish' and
            state.get('feedback', '').startswith(
                'Return exactly one complete query_code:')):
        from autoql.query_agent.nodes import extract_query
        try:
            extract_query(state['messages'][-1].content)
        except (ValueError, IndexError, TypeError):
            pass
        else:
            write_json(path.parent / 'parser_recovery.json', {
                'reason': 'Parser now accepts the saved complete query response',
                'preserved_deadline': deadline,
                'additional_model_calls': 0,
            })
            state.update(route='extract', final_status='')
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--commit', help='Complete 40-character fix commit SHA')
    source.add_argument('--cve', help='CVE ID resolved through project_info.csv, for example CVE-2022-25842')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dataset', type=Path)
    parser.add_argument('--limits', type=Path, help='JSON overrides for default budgets/timeouts')
    parser.add_argument('--run-mode', choices=('analysis', 'full'), default='analysis',
                        help='analysis stops after vuln_spec; full continues through query verification')
    parser.add_argument('--preflight-only', action='store_true',
                        help='full mode only: validate databases, CodeQL and ground truth without LLM calls')
    parser.add_argument('--resume', action='store_true', help='Resume --output without resetting budgets/deadline')
    args = parser.parse_args()
    if args.preflight_only and args.run_mode != 'full':
        parser.error('--preflight-only belongs to full mode and is unavailable in analysis mode')
    input_label = args.commit[:12] if args.commit else args.cve.upper()
    output = args.output or args.root / 'autoql_runs' / (input_label + '-' + time.strftime('%Y%m%d-%H%M%S'))
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
            if args.commit and manifest['fix_commit'] != args.commit.lower():
                raise ValueError('Resume commit does not match manifest')
            if args.cve and manifest['cve_id'].upper() != args.cve.upper():
                raise ValueError('Resume CVE does not match manifest')
            task = PatchTask(**{k: v for k, v in manifest.items() if k in PatchTask.__dataclass_fields__})
            if args.cve:
                task.input_kind = 'cve'
            limits = Limits(**json.loads((output / 'limits.json').read_text()))
            if (output / 'run_control.json').exists():
                control = json.loads((output / 'run_control.json').read_text())
                deadline = control['deadline']
                saved_mode = control.get('run_mode', 'full')
                if saved_mode == 'full' and args.run_mode == 'analysis':
                    raise ValueError('Cannot resume a full run in analysis-only mode')
            if (output / 'budget.json').exists():
                deadline = json.loads((output / 'budget.json').read_text())['deadline']
            prior = json.loads((output / 'result.json').read_text()) if (output / 'result.json').exists() else {}
            completed = prior.get('final_status')
            if (completed == 'query_verified' or
                    args.run_mode == 'analysis' and completed == 'analysis_completed' or
                    args.preflight_only and completed == 'preflight_passed'):
                final = prior
                return 0
        else:
            task = load_task(args.commit, args.root.resolve(), output, args.dataset, cve=args.cve)
        run_lock = (output / '.run.lock').open('a')
        fcntl.flock(run_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        owned_run = True
        timing.attach(output, resume=args.resume)
        write_json(output / 'run_control.json', {'deadline': deadline, 'run_mode': args.run_mode})
        write_json(output / 'limits.json', asdict(limits))
        codeql = None
        evaluator = None
        if args.run_mode == 'full':
            from autoql.query_agent.codeql import CodeQL
            from autoql.query_agent.evaluator import Evaluator
            with timing_span('preflight', 'stage'):
                databases = validate_codeql_databases(task)
                codeql = CodeQL(output, limits, deadline)
                buggy_methods = codeql.structure(task.buggy_db_path, 'buggy')
                fixed_methods = codeql.structure(task.fixed_db_path, 'fixed')
                evaluator = Evaluator(task, buggy_methods, fixed_methods)
            write_json(output / 'preflight.json', {
                'databases': databases,
                'buggy_functions': len(buggy_methods),
                'fixed_functions': len(fixed_methods),
                'granularity': evaluator.granularity,
                'fixed_mapping_unresolved': evaluator.mapping_unknown,
                'deleted_targets': evaluator.deleted,
                'java_pack': str(codeql.java_pack),
            })

        if args.preflight_only:
            final['final_status'] = 'preflight_passed'
        else:
            from autoql.llm import StreamingLLM
            from autoql.analysis_agent.agent import AnalysisAgent
            from autoql.analysis_agent.evidence_registry import EvidenceRegistry
            from autoql.analysis_agent.vulnerability_metadata import load_vulnerability_metadata
            context_path = output / 'analysis_context.json'
            if args.resume and context_path.exists():
                vulnerability_metadata = json.loads(context_path.read_text())
            else:
                vulnerability_metadata = load_vulnerability_metadata(task)
                if vulnerability_metadata is not None:
                    write_json(context_path, vulnerability_metadata)
            llm = StreamingLLM(args.root, output, limits, deadline)
            analysis = AnalysisAgent(
                task, EvidenceRegistry(task), llm, limits,
                vulnerability_metadata)
            spec_path = output / 'vuln_spec.json'
            spec = (_load_v2_spec(spec_path)
                    if args.resume and spec_path.exists() else analysis.run())

            if args.run_mode == 'analysis':
                final.update(
                    final_status='analysis_completed',
                    evidence_count=len(spec['evidence']))
            else:
                from autoql.query_agent.graph import run_query
                from autoql.query_agent.tools import RetrievalContext
                retrieval = RetrievalContext(output, limits)
                initial = (_load_query_state(output / 'query_state.json', deadline)
                           if args.resume else None)
                refresh_path = output / 'evidence_refresh.json'
                refresh_count = (json.loads(refresh_path.read_text())['count']
                                 if refresh_path.exists() else 0)
                for refresh in range(
                        refresh_count, limits.evidence_refresh_limit + 1):
                    state = run_query(
                        task, spec, llm, retrieval, codeql, evaluator, limits,
                        initial)
                    final.update({
                        key: value for key, value in state.items()
                        if key not in ('messages', 'query_code')
                    })
                    if (state['final_status'] != 'needs_evidence' or
                            refresh == limits.evidence_refresh_limit):
                        break
                    write_json(refresh_path, {'count': refresh + 1})
                    spec = analysis.run(
                        'Query generation needs additional source evidence: ' +
                        state['feedback'] +
                        '. Explore only what is missing, register it, and submit '
                        'an updated AnalysisBrief.')
                    initial = {
                        **state,
                        'final_status': '',
                        'route': 'prep',
                        'feedback': (
                            'Evidence refreshed; generate a complete query.'),
                    }
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
    return 0 if final['final_status'] in (
        'query_verified', 'preflight_passed', 'analysis_completed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
