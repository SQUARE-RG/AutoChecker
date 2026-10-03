"""File/function recall only, with no hidden truth sent to synthesis prompts."""
import csv
from pathlib import PurePosixPath, Path
from urllib.parse import unquote, urlparse, urljoin
import re

import yaml


def normalize_uri(uri, source_root, bases=None, base_id=None):
    bases = bases or {}
    if base_id:
        base = bases.get(base_id)
        if base is None:
            if base_id == '%SRCROOT%':
                # CodeQL intentionally omits originalUriBaseIds for portable results.
                base = {'uri': Path(source_root).as_uri().rstrip('/') + '/'}
            else:
                raise ValueError('Unknown SARIF uriBaseId')
        uri = urljoin(base.get('uri', ''), uri)
    parsed = urlparse(uri)
    if parsed.scheme not in ('', 'file'):
        raise ValueError('Unsupported SARIF URI scheme')
    path = unquote(parsed.path).replace('\\', '/')
    root = str(source_root).replace('\\', '/').rstrip('/')
    if path.startswith('/'):
        if not path.startswith(root + '/'):
            raise ValueError('SARIF location outside database source root')
        path = path[len(root) + 1:]
    result = PurePosixPath(path)
    if '..' in result.parts:
        raise ValueError('Unsafe SARIF path')
    return str(result)


def location_points(sarif, source_root):
    for run_index, run in enumerate(sarif.get('runs', [])):
        bases = run.get('originalUriBaseIds', {})
        artifacts = run.get('artifacts', [])
        for result_index, result in enumerate(run.get('results', [])):
            main = result.get('locations', [])
            paths = result.get('codeFlows') or []
            groups = []
            if paths:
                for pi, flow in enumerate(paths):
                    locations = [loc.get('location', {}) for thread in flow.get('threadFlows', [])
                                 for loc in thread.get('locations', [])]
                    groups.append((pi, 'path', locations))
            else:
                groups.append((None, 'primary', main))
            for pi, basis, locations in groups + ([(None, 'primary_auxiliary', main)] if paths else []):
                for loc in locations:
                    physical = loc.get('physicalLocation', {})
                    art = physical.get('artifactLocation', {})
                    if not art.get('uri') and 'index' in art:
                        art = artifacts[art['index']]['location']
                    if not art.get('uri'):
                        continue
                    yield {'result_id': [run_index, result_index], 'path_id': pi, 'basis': basis,
                        'file': normalize_uri(art['uri'], source_root, bases, art.get('uriBaseId')),
                        'line': physical.get('region', {}).get('startLine')}


def enclosing(point, methods):
    if point['line'] is None:
        raise ValueError('Function evaluation requires a physical location line')
    candidates = [m for m in methods if m['file'] == point['file'] and
                  m['start_line'] <= point['line'] <= m['end_line']]
    if not candidates:
        return None  # Class/field locations legitimately have no enclosing callable.
    candidates.sort(key=lambda m: m['end_line'] - m['start_line'])
    if len(candidates) > 1 and candidates[0]['start_line'] == candidates[1]['start_line'] and candidates[0]['end_line'] == candidates[1]['end_line']:
        raise ValueError('Ambiguous enclosing callable')
    return candidates[0]


def method_key(row):
    return (row['file'], row['class_name'], row['signature'])


class Evaluator:
    def __init__(self, task, buggy_methods, fixed_methods):
        self.task = task
        self.methods = {'buggy': buggy_methods, 'fixed': fixed_methods}
        with (Path(task.dataset_dir) / 'fix_info.csv').open() as handle:
            self.truth = [r for r in csv.DictReader(handle) if r['cve_id'] == task.cve_id]
        if not self.truth or any(r['commit'] != task.buggy_commit for r in self.truth):
            raise ValueError('Missing ground truth or mismatched buggy revision')
        self.files = {r['file'] for r in self.truth}
        self.granularity = 'function' if all(r.get('method') for r in self.truth) else 'file'
        self.targets = []
        self.fixed_targets = []
        self.mapping_unknown = False
        self.deleted = []
        if self.granularity == 'function':
            for row in self.truth:
                candidates = [m for m in buggy_methods if m['file'] == row['file'] and
                    m['class_name'] == row['class'] and m['method'] == row['method']]
                # Curated boundaries identify the overload, not the alert location.
                if row.get('method_start'):
                    candidates = [m for m in candidates if m['start_line'] == int(row['method_start'])]
                if len(candidates) != 1:
                    raise ValueError('Ground truth cannot be resolved to a unique extracted function')
                target = candidates[0]
                self.targets.append(target)
                exact = [m for m in fixed_methods if method_key(m) == method_key(target)]
                if exact:
                    self.fixed_targets.extend(exact)
                else:
                    # Conservatively reject possible moves; verify actual removal in Git patch.
                    similar = [m for m in fixed_methods if m['method'] == target['method']]
                    from autoql.task_loader import git
                    patch = git(Path(task.repo_path), 'diff', '--unified=0', task.buggy_commit,
                                task.fix_commit, '--', target['file'])
                    deleted_lines = set()
                    for start, length in re.findall(r'^@@ -(\d+)(?:,(\d+))? \+[^\n]+@@', patch, re.M):
                        a, n = int(start), int(length or 1)
                        deleted_lines.update(range(a, a + n))
                    if not similar and set(range(target['start_line'], target['end_line'] + 1)) <= deleted_lines:
                        self.deleted.append(target)
                    else:
                        self.mapping_unknown = True

    def hits(self, data, side):
        db = self.task.buggy_db_path if side == 'buggy' else self.task.fixed_db_path
        root = yaml.safe_load((Path(db) / 'codeql-database.yml').read_text())['sourceLocationPrefix']
        targets = self.targets if side == 'buggy' else self.fixed_targets
        keys = {method_key(t) for t in targets}
        hits = []
        for point in location_points(data, root):
            function_hit = False
            if self.granularity == 'function' and point['file'] in {t['file'] for t in targets}:
                method = enclosing(point, self.methods[side])
                function_hit = method is not None and method_key(method) in keys
            if point['file'] in self.files or function_hit:
                hits.append({**point, 'file_hit': point['file'] in self.files, 'function_hit': function_hit})
        counted = [p for p in hits if p['basis'] != 'primary_auxiliary']
        return {'hit_file': any(p['file_hit'] for p in counted),
                'hit_function': any(p['function_hit'] for p in counted), 'hits': hits,
                'num_results': sum(len(r.get('results', [])) for r in data.get('runs', []))}

    def evaluate(self, buggy, fixed):
        old, new = self.hits(buggy, 'buggy'), self.hits(fixed, 'fixed')
        key = 'hit_function' if self.granularity == 'function' else 'hit_file'
        status = 'unresolved' if self.mapping_unknown else ('still_present' if new[key] else
                 ('target_deleted' if self.deleted and not self.fixed_targets else 'disappeared'))
        return {'evaluation_granularity': self.granularity, 'buggy': old, 'fixed': new,
                'fixed_target_status': status, 'verified': old[key] and status in ('disappeared', 'target_deleted'),
                'manual_review': 'pending', 'deleted_targets': self.deleted}
