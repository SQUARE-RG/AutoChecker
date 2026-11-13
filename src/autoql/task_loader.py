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
    cve_id: str
    dataset_dir: str
    input_kind: str = 'commit'


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


def select_project(rows: list[dict], commit: str | None = None,
                   cve: str | None = None) -> tuple[dict, str | None]:
    """Resolve exactly one project row from either a fix commit or CVE ID.

    For CVE input the concrete fix revision is selected later using the same
    timestamp rule as the database builder, so this returns ``None`` here.
    """
    if (commit is None) == (cve is None):
        raise UnsupportedInput('Provide exactly one of commit or CVE')

    if commit is not None:
        if not re.fullmatch(r'[0-9a-fA-F]{40}', commit):
            raise UnsupportedInput('Input must be a complete 40-character fix commit SHA')
        commit = commit.lower()
        matches = [row for row in rows
                   if commit in re.findall(r'\b[0-9a-fA-F]{40}\b',
                                           row.get('fix_commit_ids', '').lower())]
        if len(matches) != 1:
            raise UnsupportedInput(f'Expected one dataset match, found {len(matches)}')
        return matches[0], commit

    cve = cve.upper()
    if not re.fullmatch(r'CVE-\d{4}-\d{4,}', cve):
        raise UnsupportedInput('CVE input must use the form CVE-YYYY-NNNN')
    matches = [row for row in rows if row.get('cve_id', '').upper() == cve]
    if len(matches) != 1:
        raise UnsupportedInput(f'Expected one dataset match for {cve}, found {len(matches)}')
    return matches[0], None


def latest_fix_commit(repo: Path, commit_ids: list[str]) -> str:
    """Mirror build_codeql_dbs.py: select the commit with the latest timestamp."""
    latest = None
    latest_timestamp = 0
    for commit_id in commit_ids:
        try:
            timestamp = int(git(repo, 'show', '-s', '--format=%ct', commit_id).strip())
        except (subprocess.CalledProcessError, ValueError):
            continue
        if timestamp > latest_timestamp:
            latest_timestamp = timestamp
            latest = commit_id
    return latest or commit_ids[-1]


def validate_codeql_databases(task: PatchTask) -> list[dict]:
    """Fail closed unless both finalized Java databases match task revisions.

    Task loading deliberately does not call this function so analysis-only runs
    remain independent from CodeQL databases. Full/preflight mode owns this
    validation immediately before query infrastructure is initialized.
    """
    validated = []
    for side, raw_path, expected_sha in (
            ('buggy', task.buggy_db_path, task.buggy_commit),
            ('fixed', task.fixed_db_path, task.fix_commit)):
        path = Path(raw_path)
        metadata_path = path / 'codeql-database.yml'
        if not metadata_path.is_file():
            raise ValueError(f'Missing {side} CodeQL database metadata: {metadata_path}')
        try:
            metadata = yaml.safe_load(metadata_path.read_text(encoding='utf-8'))
        except (OSError, yaml.YAMLError) as exc:
            raise ValueError(
                f'Invalid {side} CodeQL database metadata: {metadata_path}') from exc
        if not isinstance(metadata, dict):
            raise ValueError(f'Invalid {side} CodeQL database metadata: {metadata_path}')
        actual_sha = metadata.get('creationMetadata', {}).get('sha')
        if actual_sha != expected_sha:
            raise ValueError(
                f'{side.capitalize()} CodeQL database revision mismatch: '
                f'expected {expected_sha}, found {actual_sha!r}')
        if metadata.get('finalised') is not True:
            raise ValueError(f'{side.capitalize()} CodeQL database is not finalized: {path}')
        if metadata.get('primaryLanguage') != 'java':
            raise ValueError(
                f'{side.capitalize()} CodeQL database is not Java: '
                f'{metadata.get("primaryLanguage")!r}')
        validated.append({
            'side': side,
            'path': str(path),
            'revision': actual_sha,
            'source_location_prefix': metadata.get('sourceLocationPrefix'),
        })
    return validated


@timed('input.prepare', 'stage')
def load_task(commit: str | None, root: Path, output: Path,
              dataset: Path | None = None, cve: str | None = None) -> PatchTask:
    dataset = (dataset or root / 'autoql_data').resolve()
    with (dataset / 'project_info.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    row, requested_commit = select_project(rows, commit=commit, cve=cve)
    case_dir = root / 'cves' / safe_relative(row['cve_id'])
    repo = case_dir / safe_relative(row['github_repository_name'])
    buggy = git(repo, 'rev-parse', row['buggy_commit_id'] + '^{commit}').strip()
    if requested_commit is None:
        fix_commits = [value.strip() for value in row['fix_commit_ids'].split(';') if value.strip()]
        if not fix_commits:
            raise UnsupportedInput(f"No fix commit is declared for {row['cve_id']}")
        requested_commit = latest_fix_commit(repo, fix_commits)
    fixed = git(repo, 'rev-parse', requested_commit + '^{commit}').strip()
    # Analysis only needs the repository revisions. Keep the conventional
    # database paths in the task manifest so full/query mode can validate and
    # consume them later, but do not touch the databases while preparing an
    # analysis task.
    dbs = [case_dir / (row['cve_id'] + suffix) for suffix in ('-vul', '-fix')]

    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    workspace = output / 'workspace'
    for name, sha in [('buggy', buggy), ('fixed', fixed)]:
        snapshot(repo, sha, workspace / name)
    diff = git(repo, 'diff', '--no-ext-diff', '--no-textconv', buggy, fixed)
    message = git(repo, 'show', '-s', '--format=%B', fixed).strip()
    diff_path = workspace / 'input' / 'patch.diff'
    write_text(diff_path, diff)
    (workspace / 'work').mkdir(parents=True)
    task = PatchTask('patch-' + fixed[:12], 'java', str(repo), buggy, fixed, message,
                     str(diff_path), str(dbs[0]), str(dbs[1]), str(output), str(workspace),
                     row['cve_id'], str(dataset), 'cve' if cve is not None else 'commit')
    write_json(output / 'manifest.json', {**asdict(task), 'diff_sha256': hashlib.sha256(diff.encode()).hexdigest()})
    return task
