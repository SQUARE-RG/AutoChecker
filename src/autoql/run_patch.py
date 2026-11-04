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
from autoql.task_loader import load_task, PatchTask, UnsupportedInput
from autoql.timing import TimingRecorder, CURRENT


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
                        help='Pipeline scope; full mode is reserved for the query pipeline')
    parser.add_argument('--preflight-only', action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('--resume', action='store_true', help='Resume --output without resetting budgets/deadline')
    args = parser.parse_args()
    if args.run_mode == 'full':
        parser.error('--run-mode full is not implemented yet; use --run-mode analysis')
    if args.preflight_only:
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
                deadline = json.loads((output / 'run_control.json').read_text())['deadline']
            if (output / 'budget.json').exists():
                deadline = json.loads((output / 'budget.json').read_text())['deadline']
            prior = json.loads((output / 'result.json').read_text()) if (output / 'result.json').exists() else {}
            if prior.get('final_status') in ('query_verified', 'analysis_completed'):
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
            task, EvidenceRegistry(task), llm, limits, vulnerability_metadata)
        spec_path = output / 'vuln_spec.json'
        if args.resume and spec_path.exists():
            spec = json.loads(spec_path.read_text())
            if set(spec) != {'vulnerability_summary', 'evidence'}:
                raise ValueError('Existing vuln_spec.json does not use the Analysis V2 format')
        else:
            spec = analysis.run()
        final.update(final_status='analysis_completed', evidence_count=len(spec['evidence']))
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
