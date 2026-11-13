"""Experimental extraction of a vuln_spec evidence range as a CodeQL Java AST.

This module is deliberately independent from the AutoQL graph.  It lets us
evaluate the shape and size of CodeQL's ``PrintAst`` output before exposing it
as an agent tool.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

import yaml


AST_QUERY = r'''/**
 * @name AutoQL evidence AST
 * @description Print CodeQL Java AST nodes overlapping an evidence range.
 * @kind graph
 * @id autoql/evidence-ast
 */

import java
import semmle.code.java.PrintAst

external string evidenceFile();
external int evidenceStartLine();
external int evidenceEndLine();

class EvidenceAstConfiguration extends PrintAstConfiguration {
  override predicate shouldPrint(Element element, Location location) {
    super.shouldPrint(element, location) and
    location.getFile().getRelativePath() = evidenceFile() and
    location.getStartLine() <= evidenceEndLine() and
    location.getEndLine() >= evidenceStartLine()
  }
}

private predicate astNodeLocation(
  PrintAstNode node, string file,
  int startLine, int startColumn, int endLine, int endColumn
) {
  node.hasLocationInfo(file, startLine, startColumn, endLine, endColumn)
  or
  not exists(node.getLocation()) and
  file = "" and startLine = 0 and startColumn = 0 and endLine = 0 and endColumn = 0
}

private string astNodeId(PrintAstNode node) {
  exists(TopLevelPrintAstNode root |
    node = root and
    result = "r" + root.getProperty("semmle.order")
  )
  or
  exists(PrintAstNode parent, int childIndex |
    node = parent.getChild(childIndex) and
    result = astNodeId(parent) + "/" + childIndex.toString()
  )
}

private predicate semanticEdgeRole(
  PrintAstNode parent, PrintAstNode child, string role
) {
  exists(ElementNode p, ElementNode c, IfStmt stmt |
    parent = p and child = c and p.getElement() = stmt and
    (
      c.getElement() = stmt.getThen() and role = "then"
      or
      c.getElement() = stmt.getElse() and role = "else"
      or
      c.getElement() = stmt.getCondition() and role = "condition"
    )
  )
  or
  exists(ElementNode p, ElementNode c, LoopStmt stmt |
    parent = p and child = c and p.getElement() = stmt and
    (
      c.getElement() = stmt.getBody() and role = "body"
      or
      c.getElement() = stmt.getCondition() and role = "condition"
    )
  )
  or
  exists(ElementNode p, ElementNode c, TryStmt stmt |
    parent = p and child = c and p.getElement() = stmt and
    (
      c.getElement() = stmt.getBlock() and role = "try"
      or
      c.getElement() = stmt.getFinally() and role = "finally"
      or
      c.getElement() = stmt.getACatchClause() and role = "catch"
    )
  )
  or
  exists(ElementNode p, ElementNode c, CatchClause clause |
    parent = p and child = c and p.getElement() = clause and
    c.getElement() = clause.getBlock() and role = "body"
  )
}

private string astEdgeRole(PrintAstNode parent, PrintAstNode child) {
  semanticEdgeRole(parent, child, result)
  or
  not exists(string role | semanticEdgeRole(parent, child, role)) and result = ""
}

query predicate evidenceNodeInfo(
  string id, string label, string file,
  int startLine, int startColumn, int endLine, int endColumn
) {
  exists(PrintAstNode node |
    id = astNodeId(node) and label = node.toString() and
    astNodeLocation(node, file, startLine, startColumn, endLine, endColumn)
  )
}

query predicate evidenceEdgeInfo(
  string parentId, string childId, string label, int childIndex, string role
) {
  exists(PrintAstNode parent, PrintAstNode child |
    parentId = astNodeId(parent) and childId = astNodeId(child) and
    child = parent.getChild(childIndex) and label = parent.getChildEdgeLabel(childIndex) and
    role = astEdgeRole(parent, child)
  )
}
'''


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'Cannot read valid JSON from {path}: {exc}') from exc


def _safe_relative_file(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError('Evidence file must be a string')
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or '..' in path.parts or
            '\\' in value or any(ord(char) < 32 for char in value)):
        raise ValueError('Evidence file must be a repository-relative POSIX path')
    if path.suffix.lower() != '.java':
        raise ValueError('The evidence AST experiment currently supports Java files only')
    return str(path)


def load_evidence(vuln_spec_path: Path, evidence_id: str) -> dict:
    spec = _read_json(vuln_spec_path)
    rows = spec.get('evidence') if isinstance(spec, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f'{vuln_spec_path} does not contain an evidence list')
    matches = [row for row in rows
               if isinstance(row, dict) and row.get('id') == evidence_id]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one evidence named {evidence_id!r}, found {len(matches)}')
    evidence = dict(matches[0])
    evidence['file'] = _safe_relative_file(evidence.get('file'))
    revision = evidence.get('revision')
    if revision not in ('buggy', 'fix'):
        raise ValueError(f'Unsupported evidence revision {revision!r}; expected buggy or fix')
    start, end = evidence.get('start_line'), evidence.get('end_line')
    if (not isinstance(start, int) or isinstance(start, bool) or start < 1 or
            not isinstance(end, int) or isinstance(end, bool) or end < start):
        raise ValueError('Evidence lines must be positive integers with end_line >= start_line')
    return evidence


def select_database(manifest: dict, evidence: dict) -> tuple[Path, str, str]:
    if evidence['revision'] == 'buggy':
        side, path_key, commit_key = 'buggy', 'buggy_db_path', 'buggy_commit'
    else:
        side, path_key, commit_key = 'fixed', 'fixed_db_path', 'fix_commit'
    raw_path, expected_sha = manifest.get(path_key), manifest.get(commit_key)
    if not isinstance(raw_path, str) or not isinstance(expected_sha, str):
        raise ValueError(f'Manifest is missing {path_key} or {commit_key}')
    database = Path(raw_path).resolve()
    metadata_path = database / 'codeql-database.yml'
    try:
        metadata = yaml.safe_load(metadata_path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f'Cannot read CodeQL database metadata: {metadata_path}') from exc
    if not isinstance(metadata, dict):
        raise ValueError(f'Invalid CodeQL database metadata: {metadata_path}')
    actual_sha = metadata.get('creationMetadata', {}).get('sha')
    if actual_sha != expected_sha:
        raise ValueError(
            f'{side.capitalize()} database revision mismatch: '
            f'expected {expected_sha}, found {actual_sha!r}')
    if metadata.get('finalised') is not True:
        raise ValueError(f'{side.capitalize()} database is not finalized: {database}')
    if metadata.get('primaryLanguage') != 'java':
        raise ValueError(f'{side.capitalize()} database is not Java')
    return database, expected_sha, side


def _run(args: list[str], timeout: int) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError(f'Executable not found: {args[0]}') from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f'Command timed out after {timeout}s: {args[0]}') from exc
    if result.returncode:
        detail = (result.stderr or result.stdout)[-8000:]
        raise RuntimeError(f'Command failed ({result.returncode}): {" ".join(args[:3])}\n{detail}')
    return result.stdout


def _write_csv(path: Path, value: object) -> None:
    with path.open('w', encoding='utf-8', newline='') as handle:
        csv.writer(handle).writerow([value])


def _prepare_query_pack(codeql: str, cache: Path, timeout: int) -> Path:
    packs = json.loads(_run([codeql, 'resolve', 'qlpacks', '--format=json'], timeout))
    java_packs = packs.get('codeql/java-all')
    if not isinstance(java_packs, list) or not java_packs:
        raise RuntimeError('The CodeQL bundle does not provide codeql/java-all')
    java_pack_version = Path(java_packs[0]).name
    cache.mkdir(parents=True, exist_ok=True)
    qlpack = (
        'name: autoql/evidence-ast-experiment\n'
        'version: 0.0.1\n'
        'dependencies:\n'
        f'  codeql/java-all: "{java_pack_version}"\n'
    )
    query_path = cache / 'evidence-ast.ql'
    desired = {'qlpack.yml': qlpack, 'evidence-ast.ql': AST_QUERY}
    changed = any(not (cache / name).is_file() or
                  (cache / name).read_text(encoding='utf-8') != content
                  for name, content in desired.items())
    if changed:
        for name, content in desired.items():
            (cache / name).write_text(content, encoding='utf-8')
        lock = cache / 'codeql-pack.lock.yml'
        if lock.exists():
            lock.unlink()
    if changed or not (cache / 'codeql-pack.lock.yml').is_file():
        _run([codeql, 'pack', 'install', str(cache)], timeout)
    return query_path


def _decode_result(codeql: str, bqrs: Path, result_set: str,
                   destination: Path, timeout: int) -> list[list]:
    _run([codeql, 'bqrs', 'decode', str(bqrs), '--format=json',
          f'--result-set={result_set}', f'--output={destination}'], timeout)
    data = _read_json(destination)
    rows = data.get('tuples') if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f'Invalid BQRS JSON for {result_set}')
    return rows


def _scope(start: int, end: int, evidence_start: int, evidence_end: int) -> str:
    if start == 0 and end == 0:
        return 'synthetic'
    if start <= evidence_start and end >= evidence_end:
        return 'container'
    if start >= evidence_start and end <= evidence_end:
        return 'inside'
    return 'overlap'


def build_ast_result(evidence: dict, database: Path, database_sha: str,
                     side: str, node_rows: list[list], edge_rows: list[list]) -> dict:
    nodes: dict[str, dict] = {}
    class_pattern = re.compile(r'^\[([^]]+)](?:\s|$)')
    for row in node_rows:
        if not isinstance(row, list) or len(row) != 7:
            raise ValueError('Unexpected evidenceNodeInfo row')
        node_id, label, raw_file, start, start_column, end, end_column = row
        if not isinstance(node_id, str) or not node_id or node_id in nodes:
            raise ValueError(f'Duplicate or invalid AST node ID: {node_id!r}')
        match = class_pattern.match(label)
        nodes[node_id] = {
            'id': node_id,
            'ql_class': match.group(1) if match else 'Synthetic',
            'label': label,
            'file': evidence['file'] if raw_file else None,
            'start_line': start or None,
            'start_column': start_column or None,
            'end_line': end or None,
            'end_column': end_column or None,
            'scope': _scope(start, end, evidence['start_line'], evidence['end_line']),
            'parent_id': None,
            'child_index': None,
            'edge_label': None,
            'edge_role': None,
            'children': [],
        }
    for row in edge_rows:
        if not isinstance(row, list) or len(row) not in (4, 5):
            raise ValueError('Unexpected evidenceEdgeInfo row')
        parent_id, child_id, label, child_index = row[:4]
        role = row[4] if len(row) == 5 else ''
        if parent_id not in nodes or child_id not in nodes:
            raise ValueError(f'AST edge references an unknown node: {row!r}')
        child = nodes[child_id]
        if child['parent_id'] is not None:
            raise ValueError(f'AST node {child_id} has more than one parent')
        child['parent_id'] = parent_id
        child['child_index'] = child_index
        child['edge_label'] = label
        child['edge_role'] = role or None
        nodes[parent_id]['children'].append(child_id)
    for node in nodes.values():
        node['children'].sort(key=lambda value: nodes[value]['child_index'])
    roots = [node['id'] for node in nodes.values() if node['parent_id'] is None]
    scope_counts = Counter(node['scope'] for node in nodes.values())
    return {
        'evidence': {key: evidence[key] for key in
                     ('id', 'revision', 'file', 'start_line', 'end_line')},
        'source': {
            'start_line': evidence['start_line'],
            'code': evidence.get('code', ''),
        },
        'database': {'side': side, 'path': str(database), 'revision': database_sha},
        'ast': {
            'provider': 'CodeQL Java PrintAst',
            'roots': roots,
            'nodes': list(nodes.values()),
        },
        'stats': {
            'node_count': len(nodes),
            'edge_count': len(edge_rows),
            'root_count': len(roots),
            'scope_counts': dict(sorted(scope_counts.items())),
        },
    }


def render_full_ast_text(result: dict) -> str:
    """Render every extracted CodeQL PrintAst node for debugging."""
    evidence = result['evidence']
    ast = result['ast']
    nodes = {node['id']: node for node in ast['nodes']}
    lines = [
        f'Evidence AST: {evidence["id"]}',
        f'Revision: {evidence["revision"]}',
        f'File: {evidence["file"]}',
        f'Range: {evidence["start_line"]}-{evidence["end_line"]}',
        f'Provider: {ast["provider"]}',
        '',
    ]
    visited: set[str] = set()

    def location(node: dict) -> str:
        if node['start_line'] is None:
            return '<synthetic>'
        return (f'{node["start_line"]}:{node["start_column"]}-'
                f'{node["end_line"]}:{node["end_column"]}')

    def visit(node_id: str, prefix: str, connector: str) -> None:
        if node_id in visited:
            raise ValueError(f'CodeQL AST contains a repeated or cyclic node: {node_id}')
        visited.add(node_id)
        node = nodes.get(node_id)
        if node is None:
            raise ValueError(f'CodeQL AST references an unknown node: {node_id}')
        label = str(node['label']).replace('\r', ' ').replace('\n', ' ')
        lines.append(f'{prefix}{connector}{label}  @{location(node)}')
        children = node['children']
        for index, child_id in enumerate(children):
            last = index == len(children) - 1
            visit(child_id, prefix + ('    ' if connector == '└── ' else '│   '),
                  '└── ' if last else '├── ')

    roots = ast['roots']
    for index, root_id in enumerate(roots):
        visit(root_id, '', '└── ' if index == len(roots) - 1 else '├── ')
    if len(visited) != len(nodes):
        missing = sorted(set(nodes) - visited)
        raise ValueError(f'CodeQL AST contains unreachable nodes: {missing[:5]}')
    return '\n'.join(lines) + '\n'


_CONTROL_CLASSES = {
    'IfStmt': 'If',
    'WhileStmt': 'While',
    'DoStmt': 'Do',
    'ForStmt': 'For',
    'EnhancedForStmt': 'ForEach',
    'SwitchStmt': 'Switch',
    'TryStmt': 'Try',
    'CatchClause': 'Catch',
    'SynchronizedStmt': 'Synchronized',
    'ConstCase': 'Case',
    'PatternCase': 'Case',
    'DefaultCase': 'Default',
}
_STATEMENT_CLASSES = {
    'LocalVariableDeclStmt', 'ExprStmt', 'ReturnStmt', 'ThrowStmt',
    'BreakStmt', 'ContinueStmt', 'AssertStmt', 'YieldStmt', 'LabeledStmt',
}
_OPERATION_TAGS = (
    ('AssignExpr', 'Assign'),
    ('ClassInstanceExpr', 'Construct'),
    ('ArrayCreationExpr', 'Construct'),
    ('MethodCall', 'Call'),
)


def _source_slice(result: dict, node: dict) -> str:
    source = result.get('source', {})
    code = source.get('code', '')
    first_line = source.get('start_line')
    start, end = node.get('start_line'), node.get('end_line')
    if not code or not isinstance(first_line, int) or start is None or end is None:
        return ''
    lines = code.splitlines()
    start_index, end_index = start - first_line, end - first_line
    if start_index < 0 or end_index >= len(lines) or start_index > end_index:
        return ''
    selected = lines[start_index:end_index + 1]
    start_column, end_column = node.get('start_column'), node.get('end_column')
    if start_index == end_index:
        if start_column and end_column:
            selected[0] = selected[0][start_column - 1:end_column]
    else:
        if start_column:
            selected[0] = selected[0][start_column - 1:]
        if end_column:
            selected[-1] = selected[-1][:end_column]
    return '\n'.join(selected).strip()


def _source_line(result: dict, line_number: int | None) -> str:
    source = result.get('source', {})
    code, first_line = source.get('code', ''), source.get('start_line')
    if not code or not isinstance(first_line, int) or line_number is None:
        return ''
    lines = code.splitlines()
    index = line_number - first_line
    return lines[index].strip() if 0 <= index < len(lines) else ''


def _balanced_header(source: str, keyword: str) -> str:
    """Return a control header without including its statement body."""
    source = source.strip()
    if not source:
        return keyword.lower()
    lower = source.lower()
    keyword_index = lower.find(keyword.lower())
    if keyword_index < 0:
        return source.splitlines()[0].strip()
    open_index = source.find('(', keyword_index + len(keyword))
    if open_index < 0:
        return source[keyword_index:keyword_index + len(keyword)]
    depth = 0
    quote = None
    escaped = False
    for index in range(open_index, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return source[keyword_index:index + 1].strip()
    return source.splitlines()[0].strip()


def _compact_source(result: dict, node: dict) -> str:
    ql_class = node['ql_class']
    if ql_class == 'Method':
        line = _source_line(result, node['start_line'])
        return line.split('{', 1)[0].strip() if line else node['label']
    source = _source_slice(result, node)
    if ql_class in ('IfStmt', 'WhileStmt', 'ForStmt', 'EnhancedForStmt',
                    'SwitchStmt', 'SynchronizedStmt', 'CatchClause'):
        keyword = {
            'IfStmt': 'if', 'WhileStmt': 'while', 'ForStmt': 'for',
            'EnhancedForStmt': 'for', 'SwitchStmt': 'switch',
            'SynchronizedStmt': 'synchronized', 'CatchClause': 'catch',
        }[ql_class]
        return _balanced_header(source, keyword)
    if ql_class == 'TryStmt':
        return _balanced_header(source, 'try') if source.lstrip().startswith('try (') else 'try'
    if ql_class == 'DoStmt':
        return 'do'
    if ql_class in ('ConstCase', 'PatternCase', 'DefaultCase'):
        first = source.splitlines()[0].strip() if source else node['label']
        return first.split('{', 1)[0].strip()
    return source or node['label']


def _compact_tag(node: dict, descendant_classes: set[str]) -> str:
    ql_class = node['ql_class']
    if ql_class == 'Method':
        return 'Method'
    if ql_class in _CONTROL_CLASSES:
        return _CONTROL_CLASSES[ql_class]
    if ql_class == 'LocalVariableDeclStmt':
        tags = ['Declare']
    elif ql_class == 'ReturnStmt':
        tags = ['Return']
    elif ql_class == 'ThrowStmt':
        tags = ['Throw']
    elif ql_class == 'BreakStmt':
        tags = ['Break']
    elif ql_class == 'ContinueStmt':
        tags = ['Continue']
    elif ql_class == 'AssertStmt':
        tags = ['Assert']
    elif ql_class == 'YieldStmt':
        tags = ['Yield']
    elif ql_class == 'LabeledStmt':
        tags = ['Label']
    else:
        tags = []
    for operation_class, tag in _OPERATION_TAGS:
        if operation_class in descendant_classes and tag not in tags:
            tags.append(tag)
    return '|'.join(tags) if tags else 'Expression'


def render_compact_ast_text(result: dict) -> str:
    """Collapse PrintAst into a source-backed, statement-level semantic tree."""
    evidence = result['evidence']
    all_nodes = {node['id']: node for node in result['ast']['nodes']}

    def is_virtual_role(node: dict) -> bool:
        return node['ql_class'] == 'BlockStmt' and node.get('edge_role') in ('else', 'finally')

    retained = {
        node_id for node_id, node in all_nodes.items()
        if (node['ql_class'] == 'Method' or node['ql_class'] in _CONTROL_CLASSES or
            node['ql_class'] in _STATEMENT_CLASSES or is_virtual_role(node))
    }
    if not retained:
        raise ValueError('CodeQL AST has no statement-level nodes to render')

    compact_children: dict[str, list[str]] = {node_id: [] for node_id in retained}
    compact_parent: dict[str, str | None] = {}
    for node_id in retained:
        parent_id = all_nodes[node_id]['parent_id']
        while parent_id is not None and parent_id not in retained:
            parent_id = all_nodes[parent_id]['parent_id']
        compact_parent[node_id] = parent_id
        if parent_id is not None:
            compact_children[parent_id].append(node_id)

    def order_key(node_id: str):
        node = all_nodes[node_id]
        return (node['start_line'] or 0, node['start_column'] or 0,
                node['end_line'] or 0, node['child_index'] or 0)

    for children in compact_children.values():
        children.sort(key=order_key)

    def descendants(node_id: str) -> set[str]:
        result_classes = set()
        stack = list(all_nodes[node_id]['children'])
        while stack:
            child_id = stack.pop()
            child = all_nodes[child_id]
            result_classes.add(child['ql_class'])
            if child_id not in retained:
                stack.extend(child['children'])
        return result_classes

    def subtree_end_line(node_id: str) -> int | None:
        end_lines = []
        stack = [node_id]
        while stack:
            current_id = stack.pop()
            current = all_nodes[current_id]
            if current['end_line'] is not None:
                end_lines.append(current['end_line'])
            stack.extend(current['children'])
        return max(end_lines) if end_lines else None

    lines = [
        f'Evidence AST: {evidence["id"]}',
        f'Revision: {evidence["revision"]}',
        f'File: {evidence["file"]}',
        f'Range: {evidence["start_line"]}-{evidence["end_line"]}',
        'Provider: CodeQL Java PrintAst',
        'Mode: compact',
        '',
    ]
    visited: set[str] = set()

    def append_node(node_id: str, prefix: str, connector: str) -> None:
        if node_id in visited:
            raise ValueError(f'Compact AST contains a repeated or cyclic node: {node_id}')
        visited.add(node_id)
        node = all_nodes[node_id]
        if is_virtual_role(node):
            tag = 'Else' if node['edge_role'] == 'else' else 'Finally'
            source = ''
        else:
            tag = _compact_tag(node, descendants(node_id))
            source = _compact_source(result, node)
        display_end = (subtree_end_line(node_id)
                       if node['ql_class'] == 'Method' or node['ql_class'] in _CONTROL_CLASSES
                       else node['end_line'])
        location = (f'@{node["start_line"]}-{display_end}'
                    if node['start_line'] is not None else '@<synthetic>')
        source_lines = source.splitlines() or ['']
        first = source_lines[0].strip()
        lines.append(f'{prefix}{connector}[{tag}]' + (f' {first}' if first else '') + f'  {location}')
        continuation_prefix = prefix + ('    ' if connector == '└── ' else '│   ')
        for continuation in source_lines[1:]:
            if continuation.strip():
                lines.append(f'{continuation_prefix}    {continuation.strip()}')
        children = compact_children[node_id]
        for index, child_id in enumerate(children):
            append_node(child_id, continuation_prefix,
                        '└── ' if index == len(children) - 1 else '├── ')

    roots = [node_id for node_id in retained if compact_parent[node_id] is None]
    roots.sort(key=order_key)
    for index, root_id in enumerate(roots):
        append_node(root_id, '', '└── ' if index == len(roots) - 1 else '├── ')
    if visited != retained:
        raise ValueError('Compact AST contains unreachable retained nodes')
    return '\n'.join(lines) + '\n'


def render_ast_text(result: dict, detail: str = 'compact') -> str:
    if detail == 'compact':
        return render_compact_ast_text(result)
    if detail == 'full':
        return render_full_ast_text(result)
    raise ValueError(f'Unsupported AST detail: {detail!r}')


def extract_evidence_ast(run_dir: Path, evidence_id: str, output: Path,
                         codeql: str = 'codeql', timeout: int = 300,
                         threads: int = 2, ram: int = 4096,
                         output_format: str = 'text', detail: str = 'compact') -> dict:
    run_dir = run_dir.resolve()
    evidence = load_evidence(run_dir / 'vuln_spec.json', evidence_id)
    manifest = _read_json(run_dir / 'manifest.json')
    if not isinstance(manifest, dict):
        raise ValueError('Manifest must be a JSON object')
    database, database_sha, side = select_database(manifest, evidence)
    cache = run_dir / 'workspace' / 'evidence_ast_query'
    query = _prepare_query_pack(codeql, cache, timeout)
    with tempfile.TemporaryDirectory(prefix='autoql-evidence-ast-') as raw_tmp:
        tmp = Path(raw_tmp)
        _write_csv(tmp / 'file.csv', evidence['file'])
        _write_csv(tmp / 'start.csv', evidence['start_line'])
        _write_csv(tmp / 'end.csv', evidence['end_line'])
        bqrs = tmp / 'evidence-ast.bqrs'
        _run([
            codeql, 'query', 'run', str(query), f'--database={database}',
            f'--output={bqrs}', f'--threads={threads}', f'--ram={ram}',
            f'--external=evidenceFile={tmp / "file.csv"}',
            f'--external=evidenceStartLine={tmp / "start.csv"}',
            f'--external=evidenceEndLine={tmp / "end.csv"}',
        ], timeout)
        nodes = _decode_result(codeql, bqrs, 'evidenceNodeInfo',
                               tmp / 'nodes.json', timeout)
        edges = _decode_result(codeql, bqrs, 'evidenceEdgeInfo',
                               tmp / 'edges.json', timeout)
    if not nodes:
        raise ValueError(
            f'CodeQL found no AST nodes for {evidence_id} at '
            f'{evidence["file"]}:{evidence["start_line"]}-{evidence["end_line"]}')
    result = build_ast_result(evidence, database, database_sha, side, nodes, edges)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + '.tmp')
    if output_format == 'text':
        content = render_ast_text(result, detail)
    elif output_format == 'json':
        content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    else:
        raise ValueError(f'Unsupported output format: {output_format!r}')
    temporary.write_text(content, encoding='utf-8')
    os.replace(temporary, output)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Extract one vuln_spec evidence range using CodeQL Java PrintAst.')
    parser.add_argument('--run-dir', required=True, type=Path,
                        help='AutoQL run containing vuln_spec.json and manifest.json')
    parser.add_argument('--evidence-id', required=True,
                        help='Exact evidence ID, for example E1')
    parser.add_argument('--output', type=Path,
                        help='Output path (default: RUN_DIR/evidence_ast/ID.txt)')
    parser.add_argument('--format', choices=('text', 'json'), default='text',
                        help='Output representation; text is intended for prompts')
    parser.add_argument('--detail', choices=('compact', 'full'), default='compact',
                        help='Compact statement tree for prompts or full PrintAst for debugging')
    parser.add_argument('--codeql', default='codeql', help='CodeQL executable')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--ram', type=int, default=4096)
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.threads < 1 or args.ram < 2048:
        parser.error('--timeout/--threads must be positive and --ram must be at least 2048')
    if args.format == 'json':
        default_name = f'{args.evidence_id}.json'
    elif args.detail == 'full':
        default_name = f'{args.evidence_id}-full.txt'
    else:
        default_name = f'{args.evidence_id}.txt'
    output = args.output or args.run_dir / 'evidence_ast' / default_name
    try:
        result = extract_evidence_ast(
            args.run_dir, args.evidence_id, output.resolve(), args.codeql,
            args.timeout, args.threads, args.ram, args.format, args.detail)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f'evidence_ast: {exc}\n')
    if args.format == 'text':
        print(render_ast_text(result, args.detail), end='')
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
