"""Resolve a fix commit through the curated dataset, never through CVE inference."""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess

import yaml

from .runtime import command, write_json, write_text
from .timing import timed


class UnsupportedInput(ValueError):
    """Input cannot be resolved unambiguously by the supported dataset workflow."""


@dataclass
class PatchTask:
    task_id: str
    language: str
    repo_path: str
    buggy_commit: str
    fix_commit: str
    fix_commit_message: str
    diff_path: str
    buggy_db_path: str
    fixed_db_path: str
    output_dir: str
    workspace: str
    cve_id: str  # evaluator only; never rendered into agent prompts
    dataset_dir: str


def git(repo: Path, *args: str) -> str:
    return command(['git', '-C', str(repo), *args])


def safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError('Expected a repository-relative POSIX path')
    return str(path)


def blob(repo: Path, commit: str, file: str) -> bytes:
    file = safe_relative(file)
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{file}'])


def snapshot(repo: Path, sha: str, destination: Path):
    """Materialize regular Git blobs only; never follow symlinks/submodules."""
    entries = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-rz', sha])
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        meta, raw_path = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            continue
        target = destination / safe_relative(raw_path.decode('utf-8'))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(['git', '-C', str(repo), 'cat-file', 'blob', oid]))
        target.chmod(0o444)


@timed('input.prepare', 'stage')
def load_task(commit: str, root: Path, output: Path, dataset: Path | None = None) -> PatchTask:
    if not re.fullmatch(r'[0-9a-fA-F]{40}', commit):
        raise UnsupportedInput('Input must be a complete 40-character fix commit SHA')
    commit = commit.lower()
    dataset = (dataset or root / 'autoql_data').resolve()
    with (dataset / 'project_info.csv').open(newline='') as handle:
        matches = [r for r in csv.DictReader(handle)
                   if commit in re.findall(r'\b[0-9a-fA-F]{40}\b', r['fix_commit_ids'].lower())]
    if len(matches) != 1:
        raise UnsupportedInput(f'Expected one dataset match, found {len(matches)}')
    row = matches[0]
    case_dir = root / 'cves' / safe_relative(row['cve_id'])
    repo = case_dir / safe_relative(row['github_repository_name'])
    buggy = git(repo, 'rev-parse', row['buggy_commit_id'] + '^{commit}').strip()
    fixed = git(repo, 'rev-parse', commit + '^{commit}').strip()
    dbs = [case_dir / (row['cve_id'] + suffix) for suffix in ('-vul', '-fix')]
    for db, sha in zip(dbs, (buggy, fixed)):
        meta = yaml.safe_load((db / 'codeql-database.yml').read_text())
        if meta.get('creationMetadata', {}).get('sha') != sha or not meta.get('finalised'):
            raise ValueError('Database revision/finalization mismatch: ' + str(db))
        if meta.get('primaryLanguage') != 'java':
            raise ValueError('First release supports Java databases only')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    workspace = output / 'workspace'
    for name, sha in [('buggy', buggy), ('fixed', fixed)]:
        snapshot(repo, sha, workspace / name)
    diff = git(repo, 'diff', '--no-ext-diff', '--no-textconv', buggy, fixed)
    message = git(repo, 'show', '-s', '--format=%B', fixed).strip()
    diff_path = workspace / 'input' / 'patch.diff'
    write_text(diff_path, diff)
    write_text(workspace / 'input' / 'fix_commit_message.txt', message)
    (workspace / 'work').mkdir(parents=True)
    task = PatchTask('patch-' + fixed[:12], 'java', str(repo), buggy, fixed, message,
                     str(diff_path), str(dbs[0]), str(dbs[1]), str(output), str(workspace),
                     row['cve_id'], str(dataset))
    write_json(output / 'manifest.json', {**asdict(task), 'diff_sha256': hashlib.sha256(diff.encode()).hexdigest()})
    return task
