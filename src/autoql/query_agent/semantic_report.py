"""Bounded, non-oracular full-query results for semantic query repair."""
from pathlib import Path
import subprocess

import yaml

from autoql.task_loader import blob
from .evaluator import normalize_uri


MAX_RESULTS_PER_DATABASE = 5
MAX_LOCATIONS_PER_RESULT = 3
SNIPPET_CONTEXT_LINES = 2
MAX_SNIPPET_LINES = 7


def _source_root(database):
    try:
        metadata = yaml.safe_load(
            (Path(database) / 'codeql-database.yml').read_text(encoding='utf-8'))
        return metadata.get('sourceLocationPrefix', '') if isinstance(metadata, dict) else ''
    except (OSError, yaml.YAMLError):
        return ''


def _artifact(location, run):
    physical = location.get('physicalLocation', {})
    artifact = physical.get('artifactLocation', {})
    if not artifact.get('uri') and 'index' in artifact:
        artifacts = run.get('artifacts', [])
        index = artifact['index']
        if isinstance(index, int) and 0 <= index < len(artifacts):
            artifact = artifacts[index].get('location', {})
    return physical, artifact


def _position(location, run, source_root):
    physical, artifact = _artifact(location, run)
    if not artifact.get('uri'):
        return None
    try:
        file = normalize_uri(
            artifact['uri'], source_root, run.get('originalUriBaseIds', {}),
            artifact.get('uriBaseId'))
    except ValueError:
        return None
    region = physical.get('region', {})
    start = region.get('startLine')
    end = region.get('endLine', start)
    return {'file': file, 'start_line': start, 'end_line': end}


def _result_locations(result, run, source_root):
    """Return the primary location and bounded path endpoints, without truth data."""
    candidates = []
    main = result.get('locations') or []
    if main:
        candidates.append(('result', main[0]))

    path_locations = [
        item.get('location', {})
        for flow in (result.get('codeFlows') or [])
        for thread in flow.get('threadFlows', [])
        for item in thread.get('locations', [])
    ]
    if path_locations:
        candidates.append(('path start', path_locations[0]))
        if len(path_locations) > 1:
            candidates.append(('path end', path_locations[-1]))

    rendered, seen = [], set()
    for role, location in candidates:
        position = _position(location, run, source_root)
        if position is None:
            continue
        key = (position['file'], position['start_line'], position['end_line'])
        if key in seen:
            continue
        seen.add(key)
        message = location.get('message', {}).get('text')
        rendered.append({'role': role, 'message': message, **position})
        if len(rendered) >= MAX_LOCATIONS_PER_RESULT:
            break
    return rendered


def _snippet(task, commit, position, cache):
    file = position['file']
    start = position.get('start_line')
    if not isinstance(start, int) or start < 1:
        return '(source line unavailable)'
    end = position.get('end_line')
    if not isinstance(end, int) or end < start:
        end = start
    try:
        key = (commit, file)
        if key not in cache:
            cache[key] = blob(Path(task.repo_path), commit, file).decode(
                'utf-8', errors='replace').splitlines()
        lines = cache[key]
    except (AttributeError, OSError, ValueError, subprocess.CalledProcessError):
        return '(source unavailable at this revision)'
    if start > len(lines):
        return '(source line outside file at this revision)'
    first = max(1, start - SNIPPET_CONTEXT_LINES)
    last = min(
        len(lines), end + SNIPPET_CONTEXT_LINES,
        first + MAX_SNIPPET_LINES - 1)
    width = len(str(last))
    return '\n'.join(
        f'{line_no:>{width}} | {lines[line_no - 1]}'
        for line_no in range(first, last + 1))


def _message(result):
    return result.get('message', {}).get('text') or '(no result message)'


def _database_section(task, side, sarif, target_hit, cache):
    database = task.buggy_db_path if side == 'buggy' else task.fixed_db_path
    commit = task.buggy_commit if side == 'buggy' else task.fix_commit
    source_root = _source_root(database)
    rows = [
        (run, result)
        for run in sarif.get('runs', [])
        for result in run.get('results', [])
    ]
    lines = [
        f'{side.capitalize()} database:',
        f'Target hit: {str(bool(target_hit)).lower()}',
        f'Total results: {len(rows)}',
    ]
    if not rows:
        lines.extend(['', 'Returned result samples:', '(none)'])
        return '\n'.join(lines)

    shown = min(len(rows), MAX_RESULTS_PER_DATABASE)
    lines.extend(['', f'Returned result samples (showing {shown} of {len(rows)}):'])
    for index, (run, result) in enumerate(rows[:shown], 1):
        lines.extend(['', f'Result {index}:', f'Message: {_message(result)}'])
        locations = _result_locations(result, run, source_root)
        if not locations:
            lines.append('Locations: (no safe physical location available)')
            continue
        for location_index, location in enumerate(locations, 1):
            start, end = location['start_line'], location['end_line']
            if start is None:
                coordinates = location['file']
            elif end is not None and end != start:
                coordinates = f"{location['file']}:{start}-{end}"
            else:
                coordinates = f"{location['file']}:{start}"
            lines.append(f"Location {location_index} ({location['role']}): {coordinates}")
            if location.get('message'):
                lines.append('Location message: ' + location['message'])
            lines.extend(['Source:', _snippet(task, commit, location, cache)])
    return '\n'.join(lines)


def build_semantic_report(task, buggy_sarif, fixed_sarif, evaluation, granularity):
    """Render raw full-query SARIF samples without exposing target identities."""
    hit_key = 'hit_function' if granularity == 'function' else 'hit_file'
    cache = {}
    return '\n\n'.join([
        'FULL QUERY RESULTS',
        _database_section(
            task, 'buggy', buggy_sarif,
            evaluation.get('buggy', {}).get(hit_key, False), cache),
        _database_section(
            task, 'fixed', fixed_sarif,
            evaluation.get('fixed', {}).get(hit_key, False), cache),
    ]) + '\n'
