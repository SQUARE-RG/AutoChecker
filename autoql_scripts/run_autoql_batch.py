#!/usr/bin/env python3
"""Run AutoQL analysis sequentially for CVEs listed in a text file.

Example:
    python autoql_scripts/run_autoql_batch.py cve.txt \
        --exclude CVE-2022-25842 --exclude CVE-2022-32287

The input and exclusion files accept one CVE per line, blank lines, and lines
whose first non-whitespace character is ``#``. ``--exclude`` may be repeated
and each value may contain comma-separated CVE IDs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Iterable


CVE_PATTERN = re.compile(r'CVE-\d{4}-\d{4,}', re.IGNORECASE)
ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def normalize_cve(value: str, source: str) -> str:
    value = value.strip().upper()
    if not CVE_PATTERN.fullmatch(value):
        raise ValueError(f'Invalid CVE ID in {source}: {value!r}')
    return value


def read_cve_file(path: Path) -> list[str]:
    values = []
    seen = set()
    for line_number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        value = raw.split('#', 1)[0].strip()
        if not value:
            continue
        cve = normalize_cve(value, f'{path}:{line_number}')
        if cve not in seen:
            seen.add(cve)
            values.append(cve)
    return values


def parse_exclusions(values: Iterable[str], files: Iterable[Path]) -> set[str]:
    result = set()
    for value in values:
        for part in value.split(','):
            if part.strip():
                result.add(normalize_cve(part, '--exclude'))
    for path in files:
        result.update(read_cve_file(path))
    return result


def write_json_atomic(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def stop_process(process: subprocess.Popen, grace_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait()


def child_command(args, cve: str, output: Path) -> list[str]:
    command = [
        str(args.python), '-m', 'autoql.run_patch',
        '--cve', cve,
        '--run-mode', 'analysis',
        '--root', str(args.root),
        '--output', str(output),
    ]
    if args.dataset:
        command.extend(['--dataset', str(args.dataset)])
    if args.limits:
        command.extend(['--limits', str(args.limits)])
    return command


def run_one(args, cve: str, output: Path, log_path: Path) -> dict:
    command = child_command(args, cve, output)
    environment = os.environ.copy()
    source_path = str(args.root / 'src')
    environment['PYTHONPATH'] = (
        source_path + os.pathsep + environment['PYTHONPATH']
        if environment.get('PYTHONPATH') else source_path)
    started_at = utc_now()
    start = time.monotonic()
    process = None
    status = 'failed'
    return_code = None
    error = ''

    with log_path.open('w', encoding='utf-8') as log:
        log.write('$ ' + ' '.join(command) + '\n\n')
        log.flush()
        try:
            process = subprocess.Popen(
                command,
                cwd=args.root,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            try:
                return_code = process.wait(timeout=args.timeout)
                status = 'succeeded' if return_code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                status = 'timed_out'
                error = f'exceeded batch timeout of {args.timeout} seconds'
                stop_process(process)
                return_code = process.returncode
            except KeyboardInterrupt:
                status = 'interrupted'
                error = 'batch runner received an interrupt while this CVE was running'
                stop_process(process)
                return_code = process.returncode
                print(f'\nInterrupted {cve}; continuing with the next CVE.', flush=True)
        except OSError as exc:
            error = f'{type(exc).__name__}: {exc}'
            log.write('\n' + error + '\n')
        finally:
            if process is not None and process.poll() is None:
                stop_process(process)

    return {
        'cve': cve,
        'status': status,
        'return_code': return_code,
        'started_at': started_at,
        'finished_at': utc_now(),
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'output_dir': str(output),
        'log': str(log_path),
        'error': error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cve_file', type=Path)
    parser.add_argument('--exclude', action='append', default=[],
                        help='CVE to skip; repeat or use comma-separated values')
    parser.add_argument('--exclude-file', type=Path, action='append', default=[],
                        help='file containing CVEs to skip; may be repeated')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--dataset', type=Path,
                        help='dataset directory passed to autoql.run_patch')
    parser.add_argument('--limits', type=Path,
                        help='limits JSON passed to autoql.run_patch')
    parser.add_argument('--python', type=Path, default=Path(sys.executable),
                        help='Python interpreter used for each AutoQL process')
    parser.add_argument('--timeout', type=float, default=None,
                        help='optional outer timeout in seconds for each CVE')
    parser.add_argument('--output', type=Path,
                        help='batch directory; default: autoql_runs/batch-TIMESTAMP')
    args = parser.parse_args()

    args.root = args.root.resolve()
    args.cve_file = args.cve_file.resolve()
    args.dataset = args.dataset.resolve() if args.dataset else None
    args.limits = args.limits.resolve() if args.limits else None
    args.python = args.python.resolve()
    if args.timeout is not None and args.timeout <= 0:
        parser.error('--timeout must be greater than zero')

    try:
        cves = read_cve_file(args.cve_file)
        exclusions = parse_exclusions(args.exclude, args.exclude_file)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if not cves:
        parser.error(f'No CVEs found in {args.cve_file}')

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    batch_dir = (args.output or args.root / 'autoql_runs' / f'batch-{timestamp}').resolve()
    if batch_dir.exists():
        parser.error(f'Batch output already exists: {batch_dir}')
    runs_dir = batch_dir / 'runs'
    logs_dir = batch_dir / 'logs'
    runs_dir.mkdir(parents=True)
    logs_dir.mkdir()

    runnable = [cve for cve in cves if cve not in exclusions]
    summary = {
        'started_at': utc_now(),
        'finished_at': None,
        'cve_file': str(args.cve_file),
        'batch_dir': str(batch_dir),
        'requested_count': len(cves),
        'excluded': [cve for cve in cves if cve in exclusions],
        'results': [],
    }
    summary_path = batch_dir / 'summary.json'
    write_json_atomic(summary_path, summary)
    print(f'CVEs: {len(cves)}; excluded: {len(summary["excluded"])}; '
          f'to run: {len(runnable)}', flush=True)
    print(f'Batch artifacts: {batch_dir}', flush=True)

    for index, cve in enumerate(runnable, 1):
        output = runs_dir / f'{index:03d}-{cve}'
        log_path = logs_dir / f'{index:03d}-{cve}.log'
        print(f'[{index}/{len(runnable)}] Starting {cve}', flush=True)
        result = run_one(args, cve, output, log_path)
        summary['results'].append(result)
        write_json_atomic(summary_path, summary)
        print(f'[{index}/{len(runnable)}] {cve}: {result["status"]} '
              f'({result["elapsed_seconds"]}s); log: {log_path}', flush=True)

    summary['finished_at'] = utc_now()
    counts = {}
    for result in summary['results']:
        counts[result['status']] = counts.get(result['status'], 0) + 1
    summary['counts'] = counts
    write_json_atomic(summary_path, summary)
    print('Summary: ' + ', '.join(f'{key}={value}' for key, value in sorted(counts.items())),
          flush=True)
    print(f'Summary file: {summary_path}', flush=True)
    return 0 if all(result['status'] == 'succeeded' for result in summary['results']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
