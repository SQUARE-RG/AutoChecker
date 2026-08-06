#!/usr/bin/env python3
"""Local repair mode for iterative Semgrep rule synthesis.

This module borrows the useful part of RuleRefiner's idea without depending on
its project layout: use Semgrep matching explanations as predicate profiling,
summarize the predicate paths for wrong/right BAD/GOOD examples, then ask the
LLM to make a local edit to the current rule instead of regenerating from
scratch.
"""

from __future__ import annotations

import json
import copy
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from llm_client import LLMClient
import semgrep_tool_common as guardian
from semgrep_rule_yaml_utils import normalize_yaml


REFERENCE_SKILL_DOC = guardian.SEMGREP_PROMPT_ROOT / "docs/semgrep_repair_skill.md"


@dataclass
class RepairModeConfig:
    requirement_text: str
    current_rule_yaml: Path
    eval_files: list[Path]
    truth_by_file: dict[str, Any]
    prev_eval: dict[str, Any]
    output_dir: Path
    semgrep_bin: str
    validate_timeout_seconds: float = guardian.DEFAULT_VALIDATE_TIMEOUT_SECONDS
    scan_timeout_seconds: float = guardian.DEFAULT_SCAN_TIMEOUT_SECONDS
    max_error_examples: int = 8
    max_reference_examples: int = 8
    rejected_repairs: list[dict[str, Any]] | None = None
    forced_focus: str = ""


FLOW_SOURCE_TOKENS = (
    "argv",
    "getenv",
    "getenvironmentvariable",
    "recv",
    "recvfrom",
    "read(",
    "fgets",
    "gets(",
    "scanf",
    "fscanf",
    "sscanf",
)

FLOW_SINK_TOKENS = (
    "setcomputername",
    "putenv",
    "system(",
    "popen",
    "exec",
    "spawn",
    "loadlibrary",
    "dlopen",
    "fopen",
    "open(",
    "createfile",
    "ldap_search",
    "printf",
    "fprintf",
    "syslog",
)

STRUCTURAL_REQUIREMENT_TOKENS = (
    "pointer scaling",
    "pointer subtraction",
    "memory layout",
    "assignment in condition",
    "same name",
    "global variable",
    "anonymous struct",
    "for loop",
    "else branch",
    "float convert int",
    "release",
    "not set null",
    "malloc",
    "unchecked pointer",
    "compare expr",
    "dependent call",
)

DANGEROUS_CARRIER_PRIORITY: dict[str, int] = {
    "casted_pointer_offset_write": 110,
    "sizeof_scaled_subscript_write": 105,
    "sizeof_scaled_subscript_read": 104,
    "casted_write": 100,
    "compound_assignment": 95,
    "member_array_write": 92,
    "array_subscript_write": 90,
    "casted_pointer_offset_read": 88,
    "pointer_arithmetic_read": 86,
    "pointer_dereference_or_member": 84,
    "casted_expression": 78,
    "return_expression": 72,
    "condition_expression": 68,
    "direct_call_argument": 45,
    "declaration_initializer": 38,
    "assignment": 35,
    "array_subscript": 30,
    "call_argument": 18,
    "compound_expression": 12,
}

LOW_SIGNAL_CARRIER_SHAPES = {"direct_call_argument", "call_argument", "compound_expression"}
DECLARATION_LIKE_CARRIER_SHAPES = {
    "declaration_initializer",
    "array_declaration_initializer",
    "pointer_declaration_initializer",
}
HIGH_SIGNAL_CARRIER_MIN_PRIORITY = 50


def _short(text: Any, limit: int) -> str:
    return guardian.shorten(str(text or ""), limit=limit).strip()


def _coverage_stage(prev_eval: dict[str, Any]) -> bool:
    return int(prev_eval.get("missed_bad_count", 0) or 0) > 0


def _repair_stage_summary(prev_eval: dict[str, Any]) -> dict[str, Any]:
    bad_total = int(prev_eval.get("bad_total", 0) or 0)
    bad_hit = int(prev_eval.get("bad_hit", 0) or 0)
    bad_recall = bad_hit / bad_total if bad_total else 0.0
    return {
        "stage": "coverage_then_precision" if _coverage_stage(prev_eval) else "precision_after_full_bad_coverage",
        "bad_hit": bad_hit,
        "bad_total": bad_total,
        "bad_recall": bad_recall,
    }


def _region_key(path: str, region: Any) -> tuple[str, str, int, int]:
    return (
        str(Path(path).expanduser().resolve()),
        str(getattr(region, "function_name", "") or ""),
        int(getattr(region, "start_line", 0) or 0),
        int(getattr(region, "end_line", 0) or 0),
    )


def _item_key(item: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(Path(str(item.get("path") or "")).expanduser().resolve()),
        str(item.get("function") or ""),
        int(item.get("start_line", 0) or 0),
        int(item.get("end_line", 0) or 0),
    )


def _all_region_records(truth_by_file: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path, regions in truth_by_file.items():
        if not isinstance(regions, list):
            continue
        path = str(Path(str(raw_path)).expanduser().resolve())
        for region in regions:
            records.append(
                {
                    "path": path,
                    "function": str(getattr(region, "function_name", "") or ""),
                    "start_line": int(getattr(region, "start_line", 0) or 0),
                    "end_line": int(getattr(region, "end_line", 0) or 0),
                    "label": str(getattr(region, "label", "") or "").lower(),
                    "key": _region_key(path, region),
                }
            )
    return records


def _read_excerpt(path_raw: str, start_line: int, end_line: int, max_lines: int = 18, max_chars: int = 900) -> str:
    path = Path(str(path_raw)).expanduser().resolve()
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if not lines:
        return ""
    start = max(1, int(start_line or 1))
    end = int(end_line or start)
    if end < start:
        end = start
    end = min(len(lines), end)
    max_lines = max(1, int(max_lines))
    if end - start + 1 > max_lines:
        head = max(1, max_lines // 2)
        tail = max(1, max_lines - head)
        block = lines[start - 1 : start - 1 + head] + ["..."] + lines[max(start - 1, end - tail) : end]
    else:
        block = lines[start - 1 : end]
    text = "\n".join(block).strip()
    if not text:
        return ""
    return f"{path}:{start}-{end}\n{_short(text, max_chars)}"


def _read_region_code(path_raw: str, start_line: int, end_line: int, max_lines: int = 28, max_chars: int = 1600) -> str:
    path = Path(str(path_raw)).expanduser().resolve()
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if not lines:
        return ""
    start = max(1, int(start_line or 1))
    end = int(end_line or start)
    if end < start:
        end = start
    end = min(len(lines), end)
    block = lines[start - 1 : end]
    if len(block) > max_lines:
        head = max(1, max_lines // 2)
        tail = max(1, max_lines - head)
        block = block[:head] + ["..."] + block[-tail:]
    return _short("\n".join(block).strip(), max_chars)


def _safe_json_loads(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def run_semgrep_explanation(
    semgrep_bin: str,
    rule_yaml: Path,
    target: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    cmd = [
        semgrep_bin,
        "scan",
        "--matching-explanations",
        "--json",
        "--metrics=off",
        "--timeout",
        "0",
        "--config",
        str(rule_yaml),
        str(target),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds if timeout_seconds > 0 else None,
        )
        payload = _safe_json_loads(proc.stdout)
        payload["_runner"] = {
            "command": " ".join(cmd),
            "returncode": proc.returncode,
            "stderr": proc.stderr or "",
            "timed_out": False,
        }
        return payload
    except subprocess.TimeoutExpired as exc:
        payload = _safe_json_loads(exc.stdout or "")
        payload["_runner"] = {
            "command": " ".join(cmd),
            "returncode": 124,
            "stderr": exc.stderr or "",
            "timed_out": True,
        }
        return payload


def _op_text(op: Any) -> str:
    if isinstance(op, list):
        return " ".join(str(x) for x in op if str(x).strip())
    return str(op or "")


def _predicate_label(expl: dict[str, Any]) -> str:
    op = expl.get("op")
    if isinstance(op, list) and len(op) >= 2:
        return f"{op[0]}: {_short(op[1], 180)}"
    op_text = _op_text(op)
    children = expl.get("children")
    if op_text in {"Negation", "Inside"} and isinstance(children, list) and children:
        child = children[0]
        if isinstance(child, dict):
            return f"{op_text} -> {_predicate_label(child)}"
    return _op_text(op)


def _predicate_key(label: str) -> str:
    return re.sub(r"\s+", " ", str(label or "").strip()).lower()[:220]


def _match_count(expl: dict[str, Any]) -> int:
    matches = expl.get("matches")
    return len(matches) if isinstance(matches, list) else 0


def _is_leaf_predicate(expl: dict[str, Any]) -> bool:
    op_text = _op_text(expl.get("op"))
    children = expl.get("children")
    if not isinstance(children, list) or not children:
        return True
    return any(token in op_text for token in ("XPat", "Filter", "Negation", "Inside"))


def _predicate_from_expl(expl: dict[str, Any]) -> dict[str, Any]:
    label = _predicate_label(expl)
    matches = _match_count(expl)
    return {
        "label": label,
        "key": _predicate_key(label),
        "truth": bool(matches > 0),
        "match_count": matches,
    }


def _combine_sequential(left: list[list[dict[str, Any]]], right: list[list[dict[str, Any]]]) -> list[list[dict[str, Any]]]:
    if not left:
        return right
    if not right:
        return left
    out: list[list[dict[str, Any]]] = []
    for a in left:
        for b in right:
            out.append([*a, *b])
            if len(out) > 200:
                return out
    return out


def explanation_predicate_paths(expl: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Turn a Semgrep explanation tree into Start->End-like predicate paths."""
    if not isinstance(expl, dict):
        return []
    if _is_leaf_predicate(expl):
        return [[_predicate_from_expl(expl)]]

    op = _op_text(expl.get("op"))
    children = [c for c in expl.get("children", []) if isinstance(c, dict)]
    if not children:
        return [[_predicate_from_expl(expl)]]

    if op in {"And", "Taint"}:
        paths: list[list[dict[str, Any]]] = [[]]
        for child in children:
            paths = _combine_sequential(paths, explanation_predicate_paths(child))
        return paths[:200]

    if op in {"Or", "TaintSource", "TaintSink", "TaintSanitizer"}:
        paths = []
        for child in children:
            paths.extend(explanation_predicate_paths(child))
            if len(paths) > 200:
                break
        return paths[:200]

    paths = []
    for child in children:
        paths = _combine_sequential(paths or [[]], explanation_predicate_paths(child))
    return paths[:200]


def _normalize_pattern_text(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _rule_predicate_index(rule_yaml: str) -> dict[str, Any]:
    """Build a lightweight YAML predicate index for RuleRefiner-style alignment."""
    try:
        payload = yaml.safe_load(rule_yaml)
    except Exception:
        payload = None
    indexed: list[dict[str, Any]] = []
    path_lookup: dict[str, dict[str, Any]] = {}
    text_lookup: dict[str, dict[str, Any]] = {}
    predicate_keys = {
        "pattern",
        "pattern-not",
        "pattern-inside",
        "pattern-not-inside",
        "pattern-regex",
        "pattern-not-regex",
        "focus-metavariable",
        "metavariable-regex",
        "metavariable-pattern",
        "metavariable-comparison",
    }

    def record(key: str, value: Any, path: str) -> None:
        text = _normalize_pattern_text(value)
        item = {
            "id": len(indexed),
            "yaml_key": key,
            "yaml_path": path,
            "text": text,
            "summary": f"{path}{key}: {_short(text, 220)}",
        }
        indexed.append(item)
        path_lookup[f"{path}{key}"] = item
        if text:
            text_lookup.setdefault(text, item)

    def visit(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                next_path = f"{path}{key}."
                if key in predicate_keys:
                    record(key, value, path)
                visit(value, next_path)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                visit(item, f"{path}{idx}.")

    visit(payload)
    return {
        "predicates": indexed,
        "path_lookup": path_lookup,
        "text_lookup": text_lookup,
    }


def _aligned_predicate_from_expl(expl: dict[str, Any], rule_index: dict[str, Any]) -> dict[str, Any]:
    node = _predicate_from_expl(expl)
    op = expl.get("op")
    op_name = ""
    op_value = ""
    if isinstance(op, list):
        op_name = str(op[0] if op else "")
        op_value = _normalize_pattern_text(op[1] if len(op) > 1 else "")
    else:
        op_name = str(op or "")
    aligned = None
    text_lookup = rule_index.get("text_lookup") if isinstance(rule_index, dict) else {}
    if op_value and isinstance(text_lookup, dict):
        aligned = text_lookup.get(op_value)
    if isinstance(aligned, dict):
        node["yaml_predicate"] = {
            "id": aligned.get("id"),
            "yaml_key": aligned.get("yaml_key"),
            "yaml_path": aligned.get("yaml_path"),
            "text": aligned.get("text"),
            "summary": aligned.get("summary"),
        }
        node["yaml_predicate_key"] = str(aligned.get("summary") or "")
    else:
        node["yaml_predicate"] = None
        node["yaml_predicate_key"] = ""
    node["op_name"] = op_name
    return node


def aligned_explanation_predicate_paths(
    expl: dict[str, Any],
    rule_index: dict[str, Any],
) -> list[list[dict[str, Any]]]:
    """Semgrep explanation paths with best-effort YAML AST predicate alignment."""
    if not isinstance(expl, dict):
        return []
    if _is_leaf_predicate(expl):
        return _fill_path_alignment_context([[_aligned_predicate_from_expl(expl, rule_index)]], rule_index)

    op = _op_text(expl.get("op"))
    children = [c for c in expl.get("children", []) if isinstance(c, dict)]
    if not children:
        return _fill_path_alignment_context([[_aligned_predicate_from_expl(expl, rule_index)]], rule_index)

    if op in {"And", "Taint"}:
        paths: list[list[dict[str, Any]]] = [[]]
        for child in children:
            paths = _combine_sequential(paths, aligned_explanation_predicate_paths(child, rule_index))
        return _fill_path_alignment_context(paths[:200], rule_index)

    if op in {"Or", "TaintSource", "TaintSink", "TaintSanitizer"}:
        paths = []
        for child in children:
            paths.extend(aligned_explanation_predicate_paths(child, rule_index))
            if len(paths) > 200:
                break
        return _fill_path_alignment_context(paths[:200], rule_index)

    paths = []
    for child in children:
        paths = _combine_sequential(paths or [[]], aligned_explanation_predicate_paths(child, rule_index))
    return _fill_path_alignment_context(paths[:200], rule_index)


def _branch_prefix(yaml_path: str) -> str:
    text = str(yaml_path or "")
    marker = ".patterns."
    if marker in text:
        return text.split(marker, 1)[0] + "."
    return text


def _positive_sibling_for_yaml_path(inventory: list[dict[str, Any]], yaml_path: str) -> dict[str, Any] | None:
    """Return the positive trigger for the same local branch as a YAML path."""
    prefix = _branch_prefix(yaml_path)
    if not prefix:
        return None
    for item in inventory:
        if not isinstance(item, dict):
            continue
        if str(item.get("yaml_key") or "") not in {"pattern", "pattern-regex"}:
            continue
        if str(item.get("yaml_path") or "").startswith(prefix):
            return item
    return None


def _filter_yaml_key_for_node(node: dict[str, Any]) -> str:
    label = str(node.get("label") or "").lower()
    if "metavariable-pattern" in label:
        return "metavariable-pattern"
    if "metavariable-regex" in label:
        return "metavariable-regex"
    if "metavariable-comparison" in label or "metavariable-analysis" in label:
        return "metavariable-comparison"
    if "metavariable-focus" in label or "focus" in label:
        return "focus-metavariable"
    return ""


def _attach_yaml_predicate(node: dict[str, Any], item: dict[str, Any]) -> None:
    node["yaml_predicate"] = {
        "id": item.get("id"),
        "yaml_key": item.get("yaml_key"),
        "yaml_path": item.get("yaml_path"),
        "text": item.get("text"),
        "summary": item.get("summary"),
    }
    node["yaml_predicate_key"] = str(item.get("summary") or "")


def _fill_path_alignment_context(
    paths: list[list[dict[str, Any]]],
    rule_index: dict[str, Any],
) -> list[list[dict[str, Any]]]:
    predicates = rule_index.get("predicates") if isinstance(rule_index, dict) else []
    if not isinstance(predicates, list):
        return paths
    for path in paths:
        for idx, node in enumerate(path):
            if node.get("yaml_predicate"):
                continue
            wanted_key = _filter_yaml_key_for_node(node)
            if not wanted_key:
                continue
            neighbor_prefixes: list[str] = []
            for neighbor in [*reversed(path[:idx]), *path[idx + 1 :]]:
                yaml_pred = neighbor.get("yaml_predicate") if isinstance(neighbor.get("yaml_predicate"), dict) else {}
                prefix = _branch_prefix(str(yaml_pred.get("yaml_path") or ""))
                if prefix and prefix not in neighbor_prefixes:
                    neighbor_prefixes.append(prefix)
            for prefix in neighbor_prefixes:
                match = next(
                    (
                        item
                        for item in predicates
                        if item.get("yaml_key") == wanted_key and str(item.get("yaml_path") or "").startswith(prefix)
                    ),
                    None,
                )
                if isinstance(match, dict):
                    _attach_yaml_predicate(node, match)
                    break
    return paths


def _path_is_positive(path: list[dict[str, Any]]) -> bool:
    return all(bool(node.get("truth")) for node in path)


def _summarize_paths(paths: list[list[dict[str, Any]]]) -> dict[str, Any]:
    positive = [path for path in paths if _path_is_positive(path)]
    negative = [path for path in paths if not _path_is_positive(path)]
    true_counter: dict[str, tuple[str, int]] = {}
    false_counter: dict[str, tuple[str, int]] = {}
    for path in paths:
        for node in path:
            key = str(node.get("key") or "")
            label = str(node.get("label") or "")
            if not key:
                continue
            target = true_counter if bool(node.get("truth")) else false_counter
            prev = target.get(key, (label, 0))
            target[key] = (prev[0], prev[1] + 1)

    def _rank(counter: dict[str, tuple[str, int]]) -> list[dict[str, Any]]:
        return [
            {"label": label, "count": count}
            for _key, (label, count) in sorted(counter.items(), key=lambda item: (-item[1][1], item[1][0]))[:10]
        ]

    return {
        "path_count": len(paths),
        "positive_path_count": len(positive),
        "negative_path_count": len(negative),
        "true_predicates": _rank(true_counter),
        "false_predicates": _rank(false_counter),
    }


def _alignment_key(node: dict[str, Any]) -> str:
    yaml_key = str(node.get("yaml_predicate_key") or "")
    if yaml_key:
        return "yaml:" + yaml_key
    return "expl:" + str(node.get("key") or "")


def _path_diff(
    faulty_path: list[dict[str, Any]],
    reference_path: list[dict[str, Any]],
) -> dict[str, Any] | None:
    ref_index: dict[str, int] = {}
    for idx, node in enumerate(reference_path):
        key = _alignment_key(node)
        if key and key not in ref_index:
            ref_index[key] = idx

    intersections: list[tuple[int, int]] = []
    last_ref = -1
    for idx, node in enumerate(faulty_path):
        key = _alignment_key(node)
        ref_idx = ref_index.get(key, -1)
        if ref_idx < 0 or ref_idx < last_ref:
            continue
        intersections.append((idx, ref_idx))
        last_ref = ref_idx

    differences: list[dict[str, Any]] = []
    for left_idx, right_idx in intersections:
        left = faulty_path[left_idx]
        right = reference_path[right_idx]
        if bool(left.get("truth")) == bool(right.get("truth")):
            continue
        differences.append(
            {
                "kind": "predicate_truth_diff",
                "faulty_truth": bool(left.get("truth")),
                "reference_truth": bool(right.get("truth")),
                "predicate": str(left.get("label") or right.get("label") or ""),
                "yaml_predicate": left.get("yaml_predicate") or right.get("yaml_predicate"),
            }
        )

    prev_left = 0
    prev_right = 0
    intervals: list[tuple[list[dict[str, Any]], list[dict[str, Any]]]] = []
    for left_idx, right_idx in intersections:
        left_segment = faulty_path[prev_left:left_idx]
        right_segment = reference_path[prev_right:right_idx]
        if left_segment or right_segment:
            intervals.append((left_segment, right_segment))
        prev_left = left_idx + 1
        prev_right = right_idx + 1
    if prev_left < len(faulty_path) or prev_right < len(reference_path):
        intervals.append((faulty_path[prev_left:], reference_path[prev_right:]))

    for left_segment, right_segment in intervals:
        if not left_segment and not right_segment:
            continue
        left_positive = all(bool(node.get("truth")) for node in left_segment) if left_segment else True
        right_positive = all(bool(node.get("truth")) for node in right_segment) if right_segment else True
        if left_positive == right_positive:
            continue
        suspect_nodes = left_segment if left_segment else right_segment
        differences.append(
            {
                "kind": "interval_truth_diff",
                "faulty_truth": left_positive,
                "reference_truth": right_positive,
                "predicate": " -> ".join(str(node.get("label") or "") for node in suspect_nodes[:4]),
                "yaml_predicate": next(
                    (node.get("yaml_predicate") for node in suspect_nodes if node.get("yaml_predicate")),
                    None,
                ),
            }
        )

    if not differences:
        return None

    denominator = max(1, len(differences))
    priority = round((len(intersections) + len(intervals) - len(differences)) / denominator, 4)
    return {
        "priority": priority,
        "intersection_count": len(intersections),
        "interval_count": len(intervals),
        "difference_count": len(differences),
        "differences": differences[:6],
    }


def _select_paths_for_state(paths_by_path: dict[str, list[list[dict[str, Any]]]], group: list[dict[str, Any]], want_positive: bool) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for item in group:
        path_raw = str(Path(str(item.get("path") or "")).resolve())
        paths = paths_by_path.get(path_raw, [])
        filtered = [path for path in paths if _path_is_positive(path) == want_positive]
        if not filtered:
            filtered = paths[:1]
        for pred_path in filtered[:4]:
            selected.append({"case": item, "path": pred_path})
            if len(selected) >= 24:
                return selected
    return selected


def _case_label(item: dict[str, Any]) -> str:
    path = str(item.get("path") or "")
    return "{}:{}-{} {}".format(
        path,
        item.get("start_line"),
        item.get("end_line"),
        item.get("function") or "",
    ).strip()


def _code_for_record(record: dict[str, Any], max_lines: int = 28, max_chars: int = 1600) -> str:
    return _read_region_code(
        path_raw=str(record.get("path") or ""),
        start_line=int(record.get("start_line", 0) or 0),
        end_line=int(record.get("end_line", 0) or 0),
        max_lines=max_lines,
        max_chars=max_chars,
    )


def _strip_comments_for_shape(code: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", str(code or ""), flags=re.S)
    text = re.sub(r"//.*", " ", text)
    return text


def _looks_like_call_statement(line: str) -> bool:
    stripped = line.strip()
    if not stripped or not stripped.endswith(";"):
        return False
    if re.match(r"^(if|while|for|switch|return)\b", stripped):
        return False
    if re.match(r"^(?:void|char|short|int|long|float|double|size_t|ptrdiff_t|bool|unsigned|signed|struct|union|enum)\b", stripped):
        return False
    return bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\s*::\s*[A-Za-z_][A-Za-z0-9_]*)?\s*\(", stripped))


def _carrier_priority(shape: str) -> int:
    return int(DANGEROUS_CARRIER_PRIORITY.get(str(shape or ""), 0))


def _carrier_item_sort_key(item: dict[str, Any]) -> tuple[int, float, str]:
    shape = str(item.get("shape") or "")
    confidence = float(item.get("confidence", 0.0) or 0.0)
    evidence = str(item.get("evidence") or "")
    return (-_carrier_priority(shape), -confidence, evidence)


def _carrier_shapes_for_code(code: str) -> list[dict[str, Any]]:
    """Extract generic local carrier shapes from C/C++ snippets.

    This is intentionally CWE-agnostic. It records where the suspicious
    expression lives, so coverage repair can add a branch for a real missed-BAD
    carrier instead of tweaking an unrelated explanation predicate.
    """
    text = _strip_comments_for_shape(code)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    joined = "\n".join(lines)
    shapes: list[dict[str, Any]] = []

    def add(shape: str, evidence: str, confidence: float = 1.0) -> None:
        evidence = re.sub(r"\s+", " ", evidence).strip()
        if not shape or not evidence:
            return
        shapes.append({"shape": shape, "evidence": _short(evidence, 220), "confidence": round(float(confidence), 3)})

    type_prefix = (
        r"(?:const\s+|volatile\s+|static\s+|unsigned\s+|signed\s+|long\s+|short\s+|struct\s+\w+\s+|"
        r"enum\s+\w+\s+|[A-Za-z_][A-Za-z0-9_:<>]*\s+)+[*&\s]*"
    )
    array_decl_re = re.compile(rf"^\s*{type_prefix}[A-Za-z_][A-Za-z0-9_]*\s*\[[^\]]+\]\s*(?:=\s*[^;]+)?;")
    declaration_re = re.compile(rf"^\s*{type_prefix}[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^;]+;")
    pointer_declaration_re = re.compile(rf"^\s*{type_prefix}\*\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^;]+;")
    for line in lines:
        is_array_declaration = bool(array_decl_re.search(line))
        is_declaration_initializer = bool(declaration_re.search(line))
        is_pointer_declaration_initializer = bool(pointer_declaration_re.search(line))
        if is_array_declaration:
            add("array_declaration_initializer", line, 0.62)
        elif is_pointer_declaration_initializer:
            add("pointer_declaration_initializer", line, 0.64)
        elif is_declaration_initializer:
            add("declaration_initializer", line)
        has_assignment = bool(
            (not is_array_declaration)
            and re.search(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\s*(?:->|\.)\s*[A-Za-z_][A-Za-z0-9_]*)?\s*=\s*[^=][^;]+;", line)
        )
        if re.search(r"\*\s*\([^;]*\*\s*\)\s*\([^;]*\+\s*[^;]*sizeof\s*\([^;]+\)[^;]*\)\s*=", line):
            add("casted_pointer_offset_write", line, 1.0)
        elif re.search(r"\*\s*\([^;]*\*\s*\)\s*[^;]+\s*=", line):
            add("casted_write", line, 0.98)
        if re.search(r"\[[^\]]*sizeof\s*\([^]]+\)[^\]]*\]\s*=", line):
            add("sizeof_scaled_subscript_write", line, 0.98)
        if re.search(r"=\s*[^;]*\[[^\]]*sizeof\s*\([^]]+\)[^\]]*\]\s*;", line):
            add("sizeof_scaled_subscript_read", line, 0.96)
        if re.search(r"=\s*\*\s*\([^;]*\*\s*\)\s*\([^;]*\+\s*[^;]*sizeof\s*\([^;]+\)[^;]*\)\s*;", line):
            add("casted_pointer_offset_read", line, 0.96)
        if re.search(r"=\s*[^;]*(?:\*|\w+)\s*\([^;]*\+\s*[^;]*(?:sizeof\s*\([^;]+\)|\b[A-Za-z_][A-Za-z0-9_]*\b)[^;]*\)\s*;", line):
            add("pointer_arithmetic_read", line, 0.82)
        if re.search(r"=\s*\*\s*\([^;]*\+\s*[^;]*\)\s*;", line):
            add("pointer_arithmetic_read", line, 0.82)
        if (not is_array_declaration) and re.search(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\s*(?:->|\.)\s*[A-Za-z_][A-Za-z0-9_]*)+\s*(?:\[[^\]]+\]\s*)?=", line):
            add("member_array_write", line, 0.94)
        if (not is_array_declaration) and re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\[[^\]]+\])+\s*=", line):
            add("array_subscript_write", line, 0.93)
        if has_assignment:
            add("assignment", line, 0.55)
        if (not is_array_declaration) and re.search(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\s*(?:->|\.)\s*[A-Za-z_][A-Za-z0-9_]*)*\s*(?:\+=|-=|\*=|/=|%=|<<=|>>=|&=|\|=|\^=)\s*[^;]+;", line):
            add("compound_assignment", line, 0.95)
        if re.search(r"\breturn\b\s+[^;]+;", line):
            add("return_expression", line, 0.9)
        if _looks_like_call_statement(line):
            add("direct_call_argument", line, 0.88)
        if re.search(r"\b(?:if|while|for|switch)\s*\([^)]*(?:[+\-*/%]|==|!=|<=|>=|<|>|&&|\|\|)[^)]*\)", line):
            add("condition_expression", line, 0.84)
        if (not is_array_declaration) and re.search(r"\[[^\]]+\]", line):
            add("array_subscript", line, 0.82)
        if re.search(r"(?:\*[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\s*->\s*[A-Za-z_][A-Za-z0-9_]*)", line):
            add("pointer_dereference_or_member", line, 0.8)
        if re.search(r"\([A-Za-z_][A-Za-z0-9_:<>]*(?:\s*[*&])?\)\s*[A-Za-z_0-9(*&]", line):
            add("casted_expression", line, 0.78)

    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\([^;{}]*\)", joined):
        add("call_argument", re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\([^;{}]*\)", joined).group(0), 0.7)
    if re.search(r"[+\-*/%]|<<|>>", joined):
        add("compound_expression", re.search(r".{0,80}(?:[+\-*/%]|<<|>>).{0,80}", joined).group(0), 0.65)

    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for item in sorted(shapes, key=_carrier_item_sort_key):
        key = (str(item.get("shape") or ""), str(item.get("evidence") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= 10:
            break
    return out


def _carrier_shape_catalog(records: list[dict[str, Any]], limit_records: int = 8) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = {}
    confidence_sum: Counter[str] = Counter()
    for record in records[: max(1, int(limit_records))]:
        code = _code_for_record(record)
        for item in _carrier_shapes_for_code(code):
            shape = str(item.get("shape") or "")
            if not shape:
                continue
            counter[shape] += 1
            confidence_sum[shape] += float(item.get("confidence", 0.0) or 0.0)
            bucket = examples.setdefault(shape, [])
            if len(bucket) < 3:
                bucket.append(
                    {
                        "case": _case_label(record),
                        "evidence": item.get("evidence"),
                        "confidence": item.get("confidence"),
                    }
                )
    raw_items = [
        {
            "shape": shape,
            "count": count,
            "priority": _carrier_priority(shape),
            "avg_confidence": round(confidence_sum[shape] / max(1, count), 3),
            "examples": examples.get(shape, []),
        }
        for shape, count in counter.items()
    ]
    high_signal = [
        item
        for item in raw_items
        if int(item.get("priority", 0) or 0) >= HIGH_SIGNAL_CARRIER_MIN_PRIORITY
        and str(item.get("shape") or "") not in DECLARATION_LIKE_CARRIER_SHAPES
    ]
    selected = high_signal if high_signal else raw_items
    selected = sorted(
        selected,
        key=lambda item: (
            -int(item.get("priority", 0) or 0),
            -int(item.get("count", 0) or 0),
            -float(item.get("avg_confidence", 0.0) or 0.0),
            str(item.get("shape") or ""),
        ),
    )
    return selected[:12]


def _extract_call_names(code: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", _strip_comments_for_shape(code)):
        name = match.group(1)
        if name in {"if", "while", "for", "switch", "return", "sizeof", "catch", "bad", "good"}:
            continue
        names.append(name)
    return names


def _extract_string_literals(code: str) -> list[str]:
    return [_short(match.group(0), 120) for match in re.finditer(r'"(?:\\.|[^"\\]){0,80}"', str(code or ""))]


def _operator_tokens(code: str) -> list[str]:
    tokens = []
    for op in ("->", "<<=", ">>=", "==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "<<", ">>", "+", "-", "*", "/", "%", "<", ">"):
        if op in code:
            tokens.append(op)
    return tokens


def _argument_position_hints(code: str) -> list[str]:
    hints: list[str] = []
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(([^;{}()]*)\)", _strip_comments_for_shape(code)):
        if match.group(1) in {"if", "while", "for", "switch", "return", "sizeof", "catch", "bad", "good"}:
            continue
        args = [arg.strip() for arg in match.group(2).split(",") if arg.strip()]
        if not args:
            continue
        summary = ", ".join(f"arg{idx + 1}={_short(arg, 60)}" for idx, arg in enumerate(args[:4]))
        hints.append(f"{match.group(1)}({summary})")
        if len(hints) >= 8:
            break
    return hints


def _provenance_relation_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code)
    hints: set[str] = set()
    for match in re.finditer(
        r"\b(?:size_t|ptrdiff_t|int|long|short)\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\([^)]*\)\s*)?\(?\s*([A-Za-z_][A-Za-z0-9_]*)\s*-\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)?\s*;",
        text,
    ):
        left, right = match.group(1), match.group(2)
        right_alias = ""
        right_assign = re.search(rf"\b{re.escape(right)}\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*;", text)
        if right_assign:
            right_alias = right_assign.group(1)
        left_source = ""
        left_assign = re.search(
            rf"\b{re.escape(left)}\s*=\s*(?:[A-Za-z_][A-Za-z0-9_]*\s*\()?&?\s*([A-Za-z_][A-Za-z0-9_]*)",
            text,
        )
        if left_assign:
            left_source = left_assign.group(1)
        if right_alias and left_source:
            hints.add("subtraction_operands_share_base" if right_alias == left_source else "subtraction_operands_different_base")
        elif right_alias:
            hints.add("subtraction_right_operand_is_alias")
    array_decls = set(
        re.findall(
            r"\b(?:char|wchar_t|unsigned\s+char|int|long|short|float|double|struct\s+[A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[",
            text,
        )
    )
    if len(array_decls) >= 2:
        hints.add("multiple_local_array_objects")
    return sorted(hints)[:8]


def _control_flow_shape_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code).lower()
    hints: set[str] = set()
    if re.search(r"\belse\s+if\s*\(", text):
        hints.add("has_else_if_chain")
    if re.search(r"\belse\s*\{", text):
        hints.add("has_final_else_block")
    elif re.search(r"\belse\s+if\s*\(", text):
        hints.add("else_if_chain_without_final_else_block")
    if re.search(r"\belse\s*\{[^{}]*\b(?:return|break|continue|goto|printf|puts|exit)\b", text, re.S):
        hints.add("final_else_has_action")
    return sorted(hints)[:8]


def _conversion_shape_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code)
    hints: set[str] = set()
    float_names = set(
        re.findall(
            r"\b(?:float|double|long\s+double)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;|,)",
            text,
        )
    )
    int_names = set(
        re.findall(
            r"\b(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;|,)",
            text,
        )
    )
    if re.search(r"\b(?:float|double|long\s+double)\s+[A-Za-z_][A-Za-z0-9_]*", text):
        hints.add("declares_float_like_value")
    if re.search(r"\b(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s+[A-Za-z_][A-Za-z0-9_]*", text):
        hints.add("declares_integer_like_value")
    if re.search(
        r"=\s*\(\s*(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s*\)\s*[^;]+;",
        text,
    ):
        hints.add("explicit_integer_cast_assignment")
    if re.search(
        r"return\s+\(\s*(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s*\)\s*[^;]+;",
        text,
    ):
        hints.add("explicit_integer_cast_return")
    for lhs in int_names:
        for rhs in float_names:
            if re.search(rf"\b{re.escape(lhs)}\s*=\s*{re.escape(rhs)}\s*;", text):
                hints.add("implicit_float_to_integer_assignment")
            if re.search(
                rf"\b(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s+{re.escape(lhs)}\s*=\s*{re.escape(rhs)}\s*;",
                text,
            ):
                hints.add("implicit_float_to_integer_initializer")
            if re.search(rf"\b{re.escape(lhs)}\s*[+\-*/%]?=\s*\(\s*(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s*\)\s*{re.escape(rhs)}\b", text):
                hints.add("explicit_integer_cast_assignment")
    if re.search(
        r"(?:\b(?:int|short|long|long\s+long|unsigned\s+int|unsigned\s+short|unsigned\s+long)\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*|\b[A-Za-z_][A-Za-z0-9_]*\s*=)\s*(?!\s*\()"
        r"(?:[A-Za-z_][A-Za-z0-9_]*|[0-9]+\.[0-9]+f?|[0-9]+f)\s*;",
        text,
    ):
        hints.add("assignment_without_explicit_cast")
    return sorted(hints)[:8]


def _lifetime_shape_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code)
    hints: set[str] = set()
    release_names: set[str] = set()
    reset_names: set[str] = set()
    for match in re.finditer(r"\bfree\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*;", text):
        release_names.add(match.group(1))
        tail = text[match.end() : match.end() + 220]
        if re.search(rf"\b{re.escape(match.group(1))}\s*=\s*(?:NULL|nullptr|0)\s*;", tail):
            hints.add("release_then_null_reset_same_pointer")
        else:
            hints.add("release_without_nearby_null_reset")
    for match in re.finditer(r"\bdelete(?:\s*\[\])?\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", text):
        release_names.add(match.group(1))
        tail = text[match.end() : match.end() + 220]
        if re.search(rf"\b{re.escape(match.group(1))}\s*=\s*(?:NULL|nullptr|0)\s*;", tail):
            hints.add("release_then_null_reset_same_pointer")
        else:
            hints.add("release_without_nearby_null_reset")
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:NULL|nullptr|0)\s*;", text):
        reset_names.add(match.group(1))
    if release_names:
        hints.add("has_release_call")
    if reset_names:
        hints.add("has_null_reset")
    if release_names & reset_names:
        hints.add("released_pointer_is_reset_somewhere")
    return sorted(hints)[:8]


def _null_guard_shape_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code)
    hints: set[str] = set()
    if re.search(r"\bif\s*\(\s*![A-Za-z_][A-Za-z0-9_]*\s*\)\s*(?:\{[^{}]*\})?\s*(?:return|goto|break|continue)\b", text, re.S):
        hints.add("null_guard_early_exit")
    if re.search(r"\bif\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*(?:!=\s*(?:NULL|nullptr|0))?\s*\)\s*\{", text):
        hints.add("nonnull_guard_block")
    if re.search(r"\bif\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*(?:!=\s*(?:NULL|nullptr|0))?\s*\)\s*[A-Za-z_(*]", text):
        hints.add("nonnull_guard_statement")
    if re.search(r"\bif\s*\(\s*(?:!!|\(\s*bool\s*\)|static_cast\s*<\s*bool\s*>\s*\()\s*[A-Za-z_][A-Za-z0-9_]*", text):
        hints.add("nonnull_bool_cast_guard")
    if re.search(r"\bbool\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*\(?\s*[A-Za-z_][A-Za-z0-9_]*\s*!=\s*(?:NULL|nullptr|0)\s*\)?\s*;", text):
        hints.add("nonnull_bool_alias_guard")
    return sorted(hints)[:8]


def _scope_symbol_relation_hints(code: str) -> list[str]:
    text = _strip_comments_for_shape(code)
    hints: set[str] = set()
    global_names = set(
        re.findall(
            r"(?m)^(?:static\s+)?(?:const\s+)?(?:int|short|long|float|double|char|bool|struct\s+[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_:<>]*)\s+\*?\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[|\=|;)",
            text,
        )
    )
    local_names: set[str] = set()
    parameter_names: set[str] = set()
    for func_match in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_:<>*\s]*\s+[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)\s*\{(.*?)\n\}", text, flags=re.S):
        params, body = func_match.group(1), func_match.group(2)
        for param in params.split(","):
            param_match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?\s*$", param.strip())
            if param_match and param_match.group(1) not in {"void", "const"}:
                parameter_names.add(param_match.group(1))
        for decl_match in re.finditer(
            r"\b(?:static\s+)?(?:const\s+)?(?:int|short|long|float|double|char|bool|struct\s+[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_:<>]*)\s+\*?\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[|\=|;)",
            body,
        ):
            local_names.add(decl_match.group(1))
    if global_names & local_names:
        hints.add("local_declaration_shadows_global_name")
    if global_names & parameter_names:
        hints.add("parameter_shadows_global_name")
    if not ((global_names & local_names) or (global_names & parameter_names)) and global_names:
        hints.add("no_local_or_parameter_shadow_of_global_name")
    return sorted(hints)[:8]


def _local_feature_profile(record: dict[str, Any]) -> dict[str, Any]:
    code = _code_for_record(record)
    lowered = code.lower()
    return {
        "case": _case_label(record),
        "calls": sorted(set(_extract_call_names(code)))[:12],
        "strings": sorted(set(_extract_string_literals(code)))[:8],
        "operators": _operator_tokens(code),
        "carriers": [item.get("shape") for item in _carrier_shapes_for_code(code)[:8]],
        "provenance_relations": _provenance_relation_hints(code),
        "control_flow_shapes": _control_flow_shape_hints(code),
        "conversion_shapes": _conversion_shape_hints(code),
        "lifetime_shapes": _lifetime_shape_hints(code),
        "guard_shapes": _null_guard_shape_hints(code),
        "scope_symbol_relations": _scope_symbol_relation_hints(code),
        "has_constant": bool(re.search(r"\b(?:0|1|null|nullptr|true|false)\b|\"(?:\\.|[^\"\\])*\"", lowered)),
        "has_variable_like": bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\b", code)),
        "has_guard_or_check": bool(re.search(r"\b(if|assert|check|validate|is[A-Z_]|!=\s*NULL|!=\s*nullptr|==\s*NULL|==\s*nullptr)\b", code)),
        "has_reset_or_safe_api": bool(re.search(r"\b(memset|strncpy|snprintf|free|delete|close|reset|clear|sanitize|validate)\b|=\s*(?:0|NULL|nullptr)\s*;", code, re.I)),
        "argument_positions": _argument_position_hints(code),
        "excerpt": _short(code, 700),
    }


def _flatten_feature_values(profile: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for key in (
        "calls",
        "strings",
        "operators",
        "carriers",
        "argument_positions",
        "provenance_relations",
        "control_flow_shapes",
        "conversion_shapes",
        "lifetime_shapes",
        "guard_shapes",
        "scope_symbol_relations",
    ):
        raw = profile.get(key)
        if isinstance(raw, list):
            for item in raw:
                text = str(item or "").strip()
                if text:
                    values.add(f"{key}:{text.lower()}")
    for key in ("has_constant", "has_variable_like", "has_guard_or_check", "has_reset_or_safe_api"):
        values.add(f"{key}:{bool(profile.get(key))}")
    return values


def _feature_label(feature: str) -> str:
    if ":" not in feature:
        return feature
    key, value = feature.split(":", 1)
    return f"{key}={value}"


def _contrast_feature_priority(feature: str) -> int:
    text = str(feature or "")
    if text.startswith("provenance_relations="):
        return 100
    if text.startswith("control_flow_shapes="):
        return 95
    if text.startswith("conversion_shapes="):
        return 95
    if text.startswith("lifetime_shapes="):
        return 94
    if text.startswith("guard_shapes="):
        return 93
    if text.startswith("scope_symbol_relations="):
        return 92
    if text.startswith("argument_positions="):
        return 70
    if text.startswith("calls="):
        return 60
    if text.startswith("carriers="):
        return 45
    if text.startswith("operators="):
        return 30
    if text.startswith("strings="):
        return 25
    if text.startswith("has_"):
        return 10
    return 20


def _rank_contrast_items(items: list[dict[str, Any]], count_key: str) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            -_contrast_feature_priority(str(item.get("feature") or "")),
            -int(item.get(count_key, 0) or 0),
            str(item.get("feature") or ""),
        ),
    )


def _branch_local_contrast(flagged_good: list[dict[str, Any]], hit_bad: list[dict[str, Any]]) -> dict[str, Any]:
    good_profiles = [_local_feature_profile(record) for record in flagged_good[:8]]
    bad_profiles = [_local_feature_profile(record) for record in hit_bad[:8]]
    good_counter: Counter[str] = Counter()
    bad_counter: Counter[str] = Counter()
    for profile in good_profiles:
        good_counter.update(_flatten_feature_values(profile))
    for profile in bad_profiles:
        bad_counter.update(_flatten_feature_values(profile))

    good_only: list[dict[str, Any]] = []
    bad_only: list[dict[str, Any]] = []
    for feature, count in good_counter.most_common():
        if bad_counter.get(feature, 0) == 0:
            good_only.append({"feature": _feature_label(feature), "flagged_good_count": count, "hit_bad_count": 0})
    for feature, count in bad_counter.most_common():
        if good_counter.get(feature, 0) == 0:
            bad_only.append({"feature": _feature_label(feature), "hit_bad_count": count, "flagged_good_count": 0})
    good_only = _rank_contrast_items(good_only, "flagged_good_count")[:12]
    bad_only = _rank_contrast_items(bad_only, "hit_bad_count")[:12]
    shared: list[dict[str, Any]] = []
    for feature, count in (good_counter & bad_counter).most_common(12):
        shared.append({"feature": _feature_label(feature), "flagged_good_count": count, "hit_bad_count": bad_counter.get(feature, 0)})
    return {
        "flagged_good_profiles": good_profiles[:4],
        "hit_bad_profiles": bad_profiles[:4],
        "flagged_good_only_features": good_only,
        "hit_bad_only_features": bad_only,
        "shared_features": shared,
        "precision_hint": (
            "Use hit_bad_only_features as positive BAD context, or flagged_good_only_features as branch-local safe exclusions. "
            "Shared features alone are weak triggers."
        ),
    }


def _localization_record(
    focus: str,
    faulty: dict[str, Any],
    reference: dict[str, Any],
    diff: dict[str, Any],
) -> dict[str, Any]:
    first_diff = {}
    differences = diff.get("differences") if isinstance(diff.get("differences"), list) else []
    if differences and isinstance(differences[0], dict):
        first_diff = differences[0]
    return {
        "focus": focus,
        "priority": diff.get("priority"),
        "intersection_count": diff.get("intersection_count"),
        "difference_count": diff.get("difference_count"),
        "faulty_case": _case_label(faulty.get("case", {})),
        "reference_case": _case_label(reference.get("case", {})),
        "first_difference_kind": first_diff.get("kind"),
        "faulty_truth": first_diff.get("faulty_truth"),
        "reference_truth": first_diff.get("reference_truth"),
        "predicate": _short(first_diff.get("predicate") or "", 260),
        "yaml_predicate": first_diff.get("yaml_predicate"),
        "faulty_record": faulty.get("case", {}),
        "reference_record": reference.get("case", {}),
        "differences": differences[:4],
    }


def _paired_counterpart_for_record(records: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    path = str(record.get("path") or "")
    label = str(record.get("label") or "").lower()
    if not path or label not in {"bad", "good"}:
        return {}
    if f"/{label}/" not in path:
        return {}
    opposite = "good" if label == "bad" else "bad"
    target_path = path.replace(f"/{label}/", f"/{opposite}/")
    for candidate in records:
        if str(candidate.get("path") or "") == target_path and str(candidate.get("label") or "").lower() == opposite:
            return candidate
    return {}


def _attach_paired_counterparts(alignment: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(alignment, dict):
        return alignment
    for key in ("coverage_alignments", "precision_alignments"):
        items = alignment.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            faulty_record = item.get("faulty_record") if isinstance(item.get("faulty_record"), dict) else {}
            counterpart = _paired_counterpart_for_record(records, faulty_record)
            if counterpart:
                item["paired_counterpart_record"] = counterpart
                item["paired_counterpart_case"] = _case_label(counterpart)
    return alignment


def _rule_refiner_path_alignments(
    paths_by_path: dict[str, list[list[dict[str, Any]]]],
    cases: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    missed_bad = _select_paths_for_state(paths_by_path, cases.get("missed_bad", []), want_positive=False)
    hit_bad = _select_paths_for_state(paths_by_path, cases.get("hit_bad_reference", []), want_positive=True)
    flagged_good = _select_paths_for_state(paths_by_path, cases.get("flagged_good", []), want_positive=True)
    clean_good = _select_paths_for_state(paths_by_path, cases.get("clean_good_reference", []), want_positive=False)

    coverage: list[dict[str, Any]] = []
    for faulty in missed_bad:
        for reference in hit_bad:
            diff = _path_diff(faulty["path"], reference["path"])
            if diff:
                coverage.append(_localization_record("too_narrow_coverage", faulty, reference, diff))

    precision: list[dict[str, Any]] = []
    for faulty in flagged_good:
        for reference in clean_good:
            diff = _path_diff(faulty["path"], reference["path"])
            if diff:
                precision.append(_localization_record("too_broad_precision", faulty, reference, diff))

    def rank(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            items,
            key=lambda item: (
                -float(item.get("priority", 0.0) or 0.0),
                int(item.get("difference_count", 0) or 0),
                -int(item.get("intersection_count", 0) or 0),
                str(item.get("predicate") or ""),
            ),
        )[:12]

    return {
        "coverage_alignments": rank(coverage),
        "precision_alignments": rank(precision),
        "coverage_pair_count": len(coverage),
        "precision_pair_count": len(precision),
    }


def _repair_action_plan(prev_eval: dict[str, Any], analysis: dict[str, Any], focus: str) -> list[str]:
    diagnostics = analysis.get("rule_shape_diagnostics")
    if not isinstance(diagnostics, list):
        diagnostics = []
    diagnostic_text = "\n".join(str(item) for item in diagnostics).lower()
    current = analysis.get("previous_metrics") if isinstance(analysis.get("previous_metrics"), dict) else {}
    bad_recall = float(current.get("bad_recall", 0.0) or 0.0)
    good_fp = float(current.get("good_false_positive_rate", 0.0) or 0.0)
    plan: list[str] = []

    if "dataflow_without_taint" in diagnostic_text:
        plan.append(
            "Dataflow action: convert or repair using taint mode with real pattern-sources, pattern-sinks, visible propagators, and GOOD-derived sanitizers."
        )
    elif _looks_like_dataflow_requirement(prev_eval):
        plan.append(
            "Dataflow action: prefer taint-mode edits for source-to-sink flow; use search mode only for local non-flow branches."
        )

    if focus == "too_narrow_coverage":
        plan.append(
            "Coverage action: add one sibling branch for the most common missed BAD carrier shape; keep current hit-BAD branches unchanged."
        )
        plan.append(
            "Coverage guard: if the new branch uses a shared operator/API, include BAD-only context when visible; precision cleanup is handled after BAD coverage is recovered."
        )
    elif focus == "too_broad_precision":
        plan.append(
            "Precision action: locate the shared trigger that fires on flagged GOOD and replace/constrain that branch, not the whole rule."
        )
        plan.append(
            "Precision guard: prefer positive BAD-only context or branch-local safe-region exclusions; do not add broad pattern-not with fresh metavariables."
        )
    else:
        plan.append("Mixed action: edit only the localized branch that improves total correctness with the least regression risk.")

    if "pseudo_metavariable_semantics" in diagnostic_text:
        plan.append("Type/scope action: replace pseudo names like $INT/$FLOAT/$TYPE/$GLOBAL with concrete syntax, metavariable-type, or local structural evidence.")
    if "bare_operator_trigger" in diagnostic_text:
        plan.append("Operator action: bare arithmetic/operator triggers are shared by GOOD; require the unsafe operand relationship or surrounding BAD carrier.")
    if "possible_weak_pattern_not" in diagnostic_text:
        plan.append("Negative-pattern action: remove broad pattern-not and use a narrower overlapping safe subset with bound metavariables.")
    if "allocation_to_use_span_guard_risk" in diagnostic_text:
        plan.append("Span action: if GOOD guards enclose only the dereference/subscript use, make that use the positive finding and move allocation/producer to pattern-inside context before adding guard exclusions.")
    if bad_recall <= 0.2 and good_fp <= 0.05:
        plan.append("Regenerate-like action: current rule is almost empty; a local repair may replace the main branch while preserving any valid syntax lessons.")
    if good_fp >= 0.5:
        if _coverage_stage(prev_eval):
            plan.append("High-FP BAD-first action: only add coverage branches with strong BAD-only evidence and avoid near-all GOOD matches.")
        else:
            plan.append("High-FP action: do not add coverage branches until precision is fixed.")
    return plan[:8]


def _alignment_items_for_focus(analysis: dict[str, Any], focus: str) -> list[dict[str, Any]]:
    alignment = analysis.get("rule_refiner_path_alignment") if isinstance(analysis.get("rule_refiner_path_alignment"), dict) else {}
    coverage = alignment.get("coverage_alignments_discriminative") if isinstance(alignment, dict) else []
    precision = alignment.get("precision_alignments_discriminative") if isinstance(alignment, dict) else []
    if not coverage:
        coverage = alignment.get("coverage_alignments") if isinstance(alignment, dict) else []
    if not precision:
        precision = alignment.get("precision_alignments") if isinstance(alignment, dict) else []
    if not isinstance(coverage, list):
        coverage = []
    if not isinstance(precision, list):
        precision = []
    if focus in {"too_narrow_coverage", "missed_bad"}:
        return [item for item in coverage if isinstance(item, dict)]
    if focus in {"too_broad_precision", "flagged_good"}:
        return [item for item in precision if isinstance(item, dict)]
    return [item for item in precision + coverage if isinstance(item, dict)]


def _state_truth_rate(predicate_truth_by_state: dict[str, dict[str, dict[str, int | str]]], state: str, key: str) -> float | None:
    item = predicate_truth_by_state.get(state, {}).get(key)
    if not isinstance(item, dict):
        return None
    true_count = int(item.get("true", 0) or 0)
    false_count = int(item.get("false", 0) or 0)
    total = true_count + false_count
    if total <= 0:
        return None
    return true_count / total


def _predicate_discriminative_scores(
    predicate_truth_by_state: dict[str, dict[str, dict[str, int | str]]],
) -> dict[str, list[dict[str, Any]]]:
    labels: dict[str, str] = {}
    for state_map in predicate_truth_by_state.values():
        for key, item in state_map.items():
            if isinstance(item, dict) and key not in labels:
                labels[key] = str(item.get("label") or key)

    coverage: list[dict[str, Any]] = []
    precision: list[dict[str, Any]] = []
    for key, label in labels.items():
        missed_true = _state_truth_rate(predicate_truth_by_state, "missed_bad", key)
        hit_true = _state_truth_rate(predicate_truth_by_state, "hit_bad_reference", key)
        flagged_true = _state_truth_rate(predicate_truth_by_state, "flagged_good", key)
        clean_true = _state_truth_rate(predicate_truth_by_state, "clean_good_reference", key)

        if missed_true is not None and hit_true is not None:
            missed_false = 1.0 - missed_true
            cov_score = missed_false * hit_true
            if cov_score >= 0.20 and abs(hit_true - missed_true) >= 0.30:
                coverage.append(
                    {
                        "predicate_key": key,
                        "predicate": label,
                        "score": round(cov_score, 4),
                        "missed_bad_true_rate": round(missed_true, 4),
                        "hit_bad_true_rate": round(hit_true, 4),
                        "interpretation": "predicate blocks missed BAD but holds for hit BAD",
                    }
                )

        if flagged_true is not None and hit_true is not None:
            bad_only_score = hit_true * (1.0 - flagged_true)
            good_only_score = flagged_true * (1.0 - hit_true)
            score = max(bad_only_score, good_only_score)
            if score >= 0.20 and abs(flagged_true - hit_true) >= 0.30:
                precision.append(
                    {
                        "predicate_key": key,
                        "predicate": label,
                        "score": round(score, 4),
                        "flagged_good_true_rate": round(flagged_true, 4),
                        "hit_bad_true_rate": round(hit_true, 4),
                        "clean_good_true_rate": round(clean_true, 4) if clean_true is not None else None,
                        "preferred_use": "positive_bad_context" if bad_only_score >= good_only_score else "branch_local_good_exclusion",
                    }
                )

    return {
        "coverage": sorted(coverage, key=lambda item: (-float(item.get("score", 0.0) or 0.0), str(item.get("predicate") or "")))[:16],
        "precision": sorted(precision, key=lambda item: (-float(item.get("score", 0.0) or 0.0), str(item.get("predicate") or "")))[:16],
    }


def _alignment_has_discriminative_predicate(item: dict[str, Any], scores: list[dict[str, Any]]) -> bool:
    if not isinstance(item, dict) or not scores:
        return False
    keys = {
        str(item.get("predicate") or "").strip().lower(),
    }
    yaml_pred = item.get("yaml_predicate") if isinstance(item.get("yaml_predicate"), dict) else {}
    if yaml_pred:
        keys.add(str(yaml_pred.get("summary") or "").strip().lower())
        keys.add(str(yaml_pred.get("text") or "").strip().lower())
    for score in scores:
        pred = str(score.get("predicate") or "").strip().lower()
        if pred and any(pred in key or key in pred for key in keys if key):
            return True
    return False


def _alignment_discriminative_score(item: dict[str, Any], scores: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(item, dict) or not scores:
        return {}
    candidates = [
        str(item.get("predicate") or "").strip().lower(),
    ]
    yaml_pred = item.get("yaml_predicate") if isinstance(item.get("yaml_predicate"), dict) else {}
    if yaml_pred:
        candidates.extend(
            [
                str(yaml_pred.get("summary") or "").strip().lower(),
                str(yaml_pred.get("text") or "").strip().lower(),
            ]
        )
    best: dict[str, Any] = {}
    for score in scores:
        pred = str(score.get("predicate") or "").strip().lower()
        if not pred:
            continue
        if any(pred in candidate or candidate in pred for candidate in candidates if candidate):
            if not best or float(score.get("score", 0.0) or 0.0) > float(best.get("score", 0.0) or 0.0):
                best = score
    return best


def _filter_alignments_by_discriminative_scores(alignment: dict[str, Any], scores: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if not isinstance(alignment, dict):
        return alignment
    out = dict(alignment)
    coverage_scores = scores.get("coverage") if isinstance(scores.get("coverage"), list) else []
    precision_scores = scores.get("precision") if isinstance(scores.get("precision"), list) else []
    coverage = alignment.get("coverage_alignments") if isinstance(alignment.get("coverage_alignments"), list) else []
    precision = alignment.get("precision_alignments") if isinstance(alignment.get("precision_alignments"), list) else []
    if coverage_scores:
        kept = [item for item in coverage if _alignment_has_discriminative_predicate(item, coverage_scores)]
        out["coverage_alignments_discriminative"] = kept
    else:
        out["coverage_alignments_discriminative"] = []
    if precision_scores:
        kept = [item for item in precision if _alignment_has_discriminative_predicate(item, precision_scores)]
        out["precision_alignments_discriminative"] = kept
    else:
        out["precision_alignments_discriminative"] = []
    return out


def _meaningful_contrast_features(contrast: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(contrast, dict):
        return []
    raw = []
    for key in ("hit_bad_only_features", "flagged_good_only_features"):
        value = contrast.get(key)
        if isinstance(value, list):
            raw.extend(item for item in value if isinstance(item, dict))
    weak_prefixes = ("has_variable_like=",)
    weak_exact = {"has_constant=false", "has_constant=true"}
    meaningful: list[dict[str, Any]] = []
    for item in raw:
        feature = str(item.get("feature") or "").strip()
        if not feature:
            continue
        if feature in weak_exact or feature.startswith(weak_prefixes):
            continue
        meaningful.append(item)
    return meaningful[:12]


def _ordinary_identifier_constraint_is_weak(analysis: dict[str, Any]) -> bool:
    contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    meaningful = _meaningful_contrast_features(contrast)
    if meaningful:
        return False
    return True


def _repair_gate(analysis: dict[str, Any], focus: str) -> dict[str, Any]:
    """Decide whether local repair has enough evidence to be worth an LLM call."""
    scores = analysis.get("predicate_discriminative_scores") if isinstance(analysis.get("predicate_discriminative_scores"), dict) else {}
    carrier_catalog = analysis.get("missed_bad_carrier_shape_catalog")
    contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    if not isinstance(carrier_catalog, list):
        carrier_catalog = []
    coverage_scores = scores.get("coverage") if isinstance(scores.get("coverage"), list) else []
    precision_scores = scores.get("precision") if isinstance(scores.get("precision"), list) else []
    meaningful_contrast = _meaningful_contrast_features(contrast)
    alignment = analysis.get("rule_refiner_path_alignment") if isinstance(analysis.get("rule_refiner_path_alignment"), dict) else {}
    coverage_aligned = alignment.get("coverage_alignments_discriminative") if isinstance(alignment.get("coverage_alignments_discriminative"), list) else []
    precision_aligned = alignment.get("precision_alignments_discriminative") if isinstance(alignment.get("precision_alignments_discriminative"), list) else []

    if focus in {"too_narrow_coverage", "missed_bad"}:
        if not carrier_catalog:
            return {
                "should_repair": False,
                "reason": "coverage repair skipped: no real missed-BAD carrier shape was extracted",
                "fallback": "fresh_generation",
            }
        return {
            "should_repair": True,
            "reason": (
                "coverage repair has missed-BAD carrier evidence and discriminative YAML alignment"
                if coverage_aligned
                else "coverage repair has missed-BAD carrier evidence; add one evidence-backed sibling branch conservatively"
            ),
            "fallback": "",
            "carrier_shapes_available": True,
            "coverage_score_count": len(coverage_scores),
            "yaml_aligned_predicate_count": len(coverage_aligned),
        }

    if focus in {"too_broad_precision", "flagged_good"}:
        if not precision_scores and not meaningful_contrast:
            return {
                "should_repair": False,
                "reason": "precision repair skipped: no discriminative predicate or branch-local GOOD/BAD contrast",
                "fallback": "fresh_generation",
            }
        return {
            "should_repair": True,
            "reason": (
                "precision repair has discriminative YAML-aligned predicate"
                if precision_aligned
                else "precision repair has branch-local contrast but no YAML alignment; use conservative branch-local guard only"
            ),
            "fallback": "",
            "meaningful_contrast_count": len(meaningful_contrast),
            "yaml_aligned_predicate_count": len(precision_aligned),
        }

    if not coverage_scores and not precision_scores and not carrier_catalog and not meaningful_contrast:
        return {
            "should_repair": False,
            "reason": "repair skipped: no discriminative local evidence",
            "fallback": "fresh_generation",
        }
    return {"should_repair": True, "reason": "mixed repair has some local evidence", "fallback": ""}


def _rejected_repair_entries(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    rejected = analysis.get("recent_rejected_repairs")
    if not isinstance(rejected, list):
        return []
    return [item for item in rejected if isinstance(item, dict)]


def _rejected_localized_keys(analysis: dict[str, Any], focus: str) -> set[str]:
    keys: set[str] = set()
    for item in _rejected_repair_entries(analysis):
        if focus and str(item.get("focus") or "") not in {"", focus}:
            continue
        for key in ("localized_predicate", "localized_target_summary"):
            value = str(item.get(key) or "").strip()
            if value:
                keys.add(value)
    return keys


def _recent_rejected_count(analysis: dict[str, Any], focus: str, action_prefix: str = "") -> int:
    count = 0
    for item in _rejected_repair_entries(analysis):
        if focus and str(item.get("focus") or "") not in {"", focus}:
            continue
        if action_prefix and not str(item.get("edit_action") or "").startswith(action_prefix):
            continue
        count += 1
    return count


def _recent_coverage_no_gain_count(analysis: dict[str, Any]) -> int:
    count = 0
    for item in _rejected_repair_entries(analysis):
        if str(item.get("focus") or "") != "too_narrow_coverage":
            continue
        try:
            bad_gain = int(item.get("bad_gain", 0) or 0)
        except (TypeError, ValueError):
            bad_gain = 0
        if bad_gain <= 0:
            count += 1
    return count


def _recent_precision_failure_classes(analysis: dict[str, Any]) -> set[str]:
    classes: set[str] = set()
    for item in _rejected_repair_entries(analysis):
        if str(item.get("focus") or "") != "too_broad_precision":
            continue
        value = str(item.get("failure_class") or "").strip()
        if value:
            classes.add(value)
        reason = str(item.get("reason") or "").lower()
        action = str(item.get("edit_action") or "")
        if "bad hit dropped" in reason:
            classes.add("precision_overcut_bad")
        if "did not reduce good" in reason or "no good fp reduction" in reason:
            classes.add("precision_no_fp_delta")
            if action in {"add_branch_local_pattern_not", "add_pattern_not_inside"}:
                classes.add("exclusion_not_overlapping")
            if action == "replace_overbroad_trigger_with_bad_context":
                classes.add("replacement_not_discriminative")
    return classes


def _contrast_has_stable_bad_context(analysis: dict[str, Any], min_count: int = 2) -> bool:
    contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    bad_only = contrast.get("hit_bad_only_features") if isinstance(contrast.get("hit_bad_only_features"), list) else []
    for item in bad_only:
        if not isinstance(item, dict):
            continue
        feature = str(item.get("feature") or "")
        try:
            count = int(item.get("hit_bad_count", 0) or 0)
        except (TypeError, ValueError):
            count = 0
        if count < max(1, int(min_count)):
            continue
        if feature.startswith(("has_variable_like=", "has_constant=")):
            continue
        return True
    return False


def _contrast_feature_texts(analysis: dict[str, Any], key: str) -> list[str]:
    contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    items = contrast.get(key) if isinstance(contrast.get(key), list) else []
    return [str(item.get("feature") or "") for item in items if isinstance(item, dict)]


def _has_contrast_feature(analysis: dict[str, Any], needle: str, key: str = "") -> bool:
    keys = [key] if key else ["hit_bad_only_features", "flagged_good_only_features", "shared_features"]
    contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    for current_key in keys:
        for feature in _contrast_feature_texts(analysis, current_key):
            if needle in feature:
                return True
        profile_key = ""
        if current_key.startswith("flagged_good"):
            profile_key = "flagged_good_profiles"
        elif current_key.startswith("hit_bad"):
            profile_key = "hit_bad_profiles"
        if profile_key:
            profiles = contrast.get(profile_key) if isinstance(contrast.get(profile_key), list) else []
            for profile in profiles:
                if isinstance(profile, dict) and needle in json.dumps(profile, ensure_ascii=False).lower():
                    return True
    return False


def _precision_action_memory_counts(analysis: dict[str, Any]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in _rejected_repair_entries(analysis):
        if str(item.get("focus") or "") == "too_broad_precision":
            action = str(item.get("edit_action") or "").strip()
            if action:
                counter[action] += 1
    return counter


def _target_prefers_good_exclusion(target: dict[str, Any]) -> bool:
    disc = target.get("discriminative_score") if isinstance(target.get("discriminative_score"), dict) else {}
    return str(disc.get("preferred_use") or "") == "branch_local_good_exclusion"


def _action_allowed_by_failure_memory(action: str, failure_classes: set[str], target: dict[str, Any], has_stable_bad_context: bool) -> bool:
    if action in {"replace_overbroad_trigger_with_bad_context", "add_pattern_inside"}:
        if "precision_overcut_bad" in failure_classes:
            return False
        if _target_prefers_good_exclusion(target) and not has_stable_bad_context:
            return False
    if (
        action == "replace_overbroad_trigger_with_bad_context"
        and "replacement_not_discriminative" in failure_classes
        and not has_stable_bad_context
    ):
        return False
    return True


def _strip_explanation_operator_prefix(text: str) -> str:
    out = str(text or "").strip()
    changed = True
    while changed:
        changed = False
        for prefix in ("Negation ->", "Inside ->", "XPat:", "Filter:"):
            if out.lower().startswith(prefix.lower()):
                out = out[len(prefix) :].strip()
                changed = True
    return out


def _summary_pattern_text(summary: str) -> str:
    text = str(summary or "")
    if ": " in text:
        text = text.split(": ", 1)[1]
    return _strip_explanation_operator_prefix(text)


def _target_from_overbroad_inventory(analysis: dict[str, Any]) -> dict[str, Any] | None:
    """Fallback from predicate frequency to a concrete YAML branch.

    Semgrep explanation alignment can miss parse-equivalent predicates. When a
    high-frequency overbroad predicate is textually the same as a current rule
    pattern, still give repair a real branch path instead of an empty
    branch-local contrast target.
    """
    overbroad = analysis.get("localized_overbroad_predicates")
    inventory = analysis.get("rule_predicate_index")
    if not isinstance(overbroad, list) or not isinstance(inventory, list):
        return None

    def norm(value: str) -> str:
        return _normalize_pattern_text(_strip_explanation_operator_prefix(value)).lower()

    positive_overbroad = [
        item for item in overbroad
        if isinstance(item, dict) and not str(item.get("predicate") or "").lstrip().lower().startswith("negation")
    ]
    candidates = positive_overbroad or [item for item in overbroad if isinstance(item, dict)]
    for pred_item in candidates:
        predicate_raw = str(pred_item.get("predicate") or "")
        predicate_norm = norm(predicate_raw)
        if not predicate_norm:
            continue
        prefers_negative = predicate_raw.lstrip().lower().startswith("negation")
        wanted_keys = {"pattern-not", "pattern-not-inside", "pattern-not-regex"} if prefers_negative else {"pattern", "pattern-regex"}
        for inv in inventory:
            if not isinstance(inv, dict):
                continue
            yaml_key = str(inv.get("yaml_key") or "")
            if yaml_key not in wanted_keys:
                continue
            summary = str(inv.get("summary") or "")
            text_norm = norm(_summary_pattern_text(summary))
            if not text_norm:
                continue
            if predicate_norm == text_norm or predicate_norm in text_norm or text_norm in predicate_norm:
                matched_yaml_key = yaml_key
                matched_summary = summary
                matched_pattern_text = _summary_pattern_text(summary)
                matched_yaml_path = str(inv.get("yaml_path") or "")
                target_inv = inv
                if prefers_negative:
                    positive_sibling = _positive_sibling_for_yaml_path(inventory, matched_yaml_path)
                    if isinstance(positive_sibling, dict):
                        target_inv = positive_sibling
                yaml_path = str(target_inv.get("yaml_path") or "")
                target_summary = str(target_inv.get("summary") or "")
                target_yaml_key = str(target_inv.get("yaml_key") or "")
                return {
                    "source": "overbroad_inventory_text_match",
                    "summary": target_summary,
                    "yaml_key": target_yaml_key,
                    "yaml_path": yaml_path,
                    "branch_prefix": _branch_prefix(yaml_path),
                    "pattern_text": _summary_pattern_text(target_summary),
                    "faulty_case": "",
                    "reference_case": "",
                    "faulty_record": {},
                    "reference_record": {},
                    "paired_counterpart_case": "",
                    "paired_counterpart_record": {},
                    "faulty_truth": None,
                    "reference_truth": None,
                    "difference_kind": "overbroad_inventory_text_match",
                    "discriminative_score": {},
                    "overbroad_predicate": pred_item,
                    "matched_overbroad_yaml_key": matched_yaml_key,
                    "matched_overbroad_summary": matched_summary,
                    "matched_overbroad_pattern_text": matched_pattern_text,
                }
    return None


def _top_localized_target(analysis: dict[str, Any], focus: str) -> dict[str, Any]:
    """Pick the RuleRefiner-style local edit target for the repair contract."""
    rejected_keys = _rejected_localized_keys(analysis, focus)
    deferred: list[dict[str, Any]] = []
    carrier_catalog = analysis.get("missed_bad_carrier_shape_catalog")
    top_carrier = carrier_catalog[0] if isinstance(carrier_catalog, list) and carrier_catalog and isinstance(carrier_catalog[0], dict) else {}
    if top_carrier and focus in {"too_narrow_coverage", "missed_bad"}:
        return {
            "source": "missed_bad_carrier_shape",
            "summary": "Add a sibling branch for missed BAD carrier shape: {}".format(top_carrier.get("shape") or ""),
            "yaml_key": "",
            "yaml_path": "",
            "branch_prefix": "",
            "pattern_text": str(top_carrier.get("shape") or ""),
            "coverage_carrier_shape": top_carrier,
            "faulty_case": "",
            "reference_case": "",
            "faulty_record": {},
            "reference_record": {},
            "paired_counterpart_case": "",
            "paired_counterpart_record": {},
            "faulty_truth": None,
            "reference_truth": None,
            "difference_kind": "carrier_shape_gap",
        }
    scores = analysis.get("predicate_discriminative_scores") if isinstance(analysis.get("predicate_discriminative_scores"), dict) else {}
    score_items = scores.get("precision" if focus in {"too_broad_precision", "flagged_good"} else "coverage")
    if not isinstance(score_items, list):
        score_items = []
    alignment_items = _alignment_items_for_focus(analysis, focus)
    alignment_items = sorted(
        alignment_items,
        key=lambda item: (
            -float(_alignment_discriminative_score(item, score_items).get("score", 0.0) or 0.0),
            -float(item.get("priority", 0.0) or 0.0),
            str(item.get("predicate") or ""),
        ),
    )
    for item in alignment_items:
        yaml_pred = item.get("yaml_predicate") if isinstance(item.get("yaml_predicate"), dict) else {}
        if yaml_pred:
            disc = _alignment_discriminative_score(item, score_items)
            target = {
                "source": "path_alignment",
                "summary": str(yaml_pred.get("summary") or ""),
                "yaml_key": str(yaml_pred.get("yaml_key") or ""),
                "yaml_path": str(yaml_pred.get("yaml_path") or ""),
                "branch_prefix": _branch_prefix(str(yaml_pred.get("yaml_path") or "")),
                "pattern_text": str(yaml_pred.get("text") or ""),
                "faulty_case": str(item.get("faulty_case") or ""),
                "reference_case": str(item.get("reference_case") or ""),
                "faulty_record": item.get("faulty_record") if isinstance(item.get("faulty_record"), dict) else {},
                "reference_record": item.get("reference_record") if isinstance(item.get("reference_record"), dict) else {},
                "paired_counterpart_case": str(item.get("paired_counterpart_case") or ""),
                "paired_counterpart_record": item.get("paired_counterpart_record") if isinstance(item.get("paired_counterpart_record"), dict) else {},
                "faulty_truth": item.get("faulty_truth"),
                "reference_truth": item.get("reference_truth"),
                "difference_kind": str(item.get("first_difference_kind") or ""),
                "discriminative_score": disc,
            }
            if str(target.get("summary") or "") in rejected_keys:
                deferred.append(target)
                continue
            return target
    if deferred:
        target = dict(deferred[0])
        target["previously_rejected"] = True
        return target
    meaningful_contrast = _meaningful_contrast_features(
        analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    )
    if meaningful_contrast and focus in {"too_broad_precision", "flagged_good"}:
        inventory_target = _target_from_overbroad_inventory(analysis)
        if inventory_target:
            return inventory_target
        return {
            "source": "branch_local_contrast",
            "summary": "Use branch-local contrast feature: {}".format(meaningful_contrast[0].get("feature") or ""),
            "yaml_key": "",
            "yaml_path": "",
            "branch_prefix": "",
            "pattern_text": str(meaningful_contrast[0].get("feature") or ""),
            "contrast_feature": meaningful_contrast[0],
            "faulty_case": "",
            "reference_case": "",
            "faulty_record": {},
            "reference_record": {},
            "paired_counterpart_case": "",
            "paired_counterpart_record": {},
            "faulty_truth": None,
            "reference_truth": None,
            "difference_kind": "branch_local_contrast",
        }
    fallback_key = "localized_overbroad_predicates" if focus == "too_broad_precision" else "localized_too_narrow_predicates"
    fallback = analysis.get(fallback_key)
    if isinstance(fallback, list) and fallback:
        item = fallback[0] if isinstance(fallback[0], dict) else {}
        return {
            "source": "predicate_frequency",
            "summary": str(item.get("predicate") or ""),
            "yaml_key": "",
            "yaml_path": "",
            "branch_prefix": "",
            "pattern_text": str(item.get("predicate") or ""),
            "faulty_case": "",
            "reference_case": "",
            "faulty_record": {},
            "reference_record": {},
            "paired_counterpart_case": "",
            "paired_counterpart_record": {},
            "faulty_truth": None,
            "reference_truth": None,
            "difference_kind": "",
        }
    return {
        "source": "case_contrast",
        "summary": "No aligned YAML predicate found; infer the smallest branch-local edit from BAD/GOOD contrast.",
        "yaml_key": "",
        "yaml_path": "",
        "branch_prefix": "",
        "pattern_text": "",
        "faulty_case": "",
        "reference_case": "",
        "faulty_record": {},
        "reference_record": {},
        "paired_counterpart_case": "",
        "paired_counterpart_record": {},
        "faulty_truth": None,
        "reference_truth": None,
        "difference_kind": "",
    }


def _rule_uses_taint(rule_yaml: str) -> bool:
    try:
        payload = yaml.safe_load(rule_yaml)
    except Exception:
        return False
    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if str(node.get("mode") or "").strip().lower() == "taint":
                return True
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return False


def _looks_like_dataflow_from_metrics_and_rule(analysis: dict[str, Any], current_rule_yaml: str) -> bool:
    diagnostics = "\n".join(str(item) for item in analysis.get("rule_shape_diagnostics", []) if item).lower()
    if "dataflow_without_taint" in diagnostics or "source-to-sink" in diagnostics:
        return True
    if _rule_uses_taint(current_rule_yaml):
        return True
    return False


def _repair_contract_actions(
    focus: str,
    target: dict[str, Any],
    current_rule_yaml: str,
    analysis: dict[str, Any],
) -> list[str]:
    actions: list[str]
    yaml_key = str(target.get("yaml_key") or "")
    dataflow_like = _looks_like_dataflow_from_metrics_and_rule(analysis, current_rule_yaml)

    if focus in {"too_narrow_coverage", "missed_bad"}:
        actions = ["add_sibling_branch_to_pattern_either"]
        if yaml_key in {"pattern-not", "pattern-not-inside", "pattern-not-regex"} or "pattern-not" in yaml_key:
            actions.insert(0, "weaken_overblocking_exclusion")
        if dataflow_like:
            actions.append("add_taint_source_sink_or_propagator")
        if str(target.get("source") or "") != "missed_bad_carrier_shape":
            actions.append("generalize_local_positive_predicate")
    elif focus in {"too_broad_precision", "flagged_good"}:
        rejected = _rejected_repair_entries(analysis)
        failure_classes = _recent_precision_failure_classes(analysis)
        action_counts = _precision_action_memory_counts(analysis)
        saw_overcut = "precision_overcut_bad" in failure_classes
        saw_exclusion_noop = "exclusion_not_overlapping" in failure_classes or bool(
            action_counts.get("add_branch_local_pattern_not") or action_counts.get("add_pattern_not_inside")
        )
        saw_replacement_noop = "replacement_not_discriminative" in failure_classes or bool(
            action_counts.get("replace_overbroad_trigger_with_bad_context")
        )
        weak_identifier_constraint = _ordinary_identifier_constraint_is_weak(analysis)
        gate = analysis.get("repair_gate") if isinstance(analysis.get("repair_gate"), dict) else {}
        no_yaml_alignment = int(gate.get("yaml_aligned_predicate_count", 0) or 0) <= 0
        disc = target.get("discriminative_score") if isinstance(target.get("discriminative_score"), dict) else {}
        target_yaml_key = str(target.get("yaml_key") or "")
        has_stable_bad_context = _contrast_has_stable_bad_context(analysis)
        prefers_good_exclusion = _target_prefers_good_exclusion(target)
        release_reset = _has_contrast_feature(analysis, "release_then_null_reset_same_pointer", "flagged_good_only_features")
        explicit_cast = _has_contrast_feature(analysis, "explicit_integer_cast", "flagged_good_only_features")
        final_else = _has_contrast_feature(analysis, "has_final_else_block", "flagged_good_only_features")
        same_base_pointer = _has_contrast_feature(analysis, "subtraction_operands_share_base", "flagged_good_only_features")
        guard_shape = _has_contrast_feature(analysis, "guard_shapes=", "flagged_good_only_features")
        good_only_positive = (
            target_yaml_key in {"pattern", "pattern-regex"}
            and str(disc.get("preferred_use") or "") == "branch_local_good_exclusion"
            and float(disc.get("hit_bad_true_rate", 1.0) or 0.0) <= 0.05
            and float(disc.get("flagged_good_true_rate", 0.0) or 0.0) >= 0.20
        )
        if dataflow_like:
            actions = [
                "add_taint_sanitizer_or_scope_guard",
                "add_pattern_not_inside",
                "add_branch_local_pattern_not",
            ]
            if has_stable_bad_context and not saw_overcut:
                actions.append("replace_overbroad_trigger_with_bad_context")
        elif explicit_cast:
            actions = [
                "add_branch_local_pattern_not",
                "add_pattern_not_inside",
                "add_metavariable_constraint",
            ]
            if has_stable_bad_context and not saw_overcut:
                actions.append("replace_overbroad_trigger_with_bad_context")
        elif release_reset or same_base_pointer or guard_shape:
            actions = [
                "add_pattern_not_inside",
                "add_branch_local_pattern_not",
                "replace_overbroad_trigger_with_bad_context",
            ]
        elif final_else:
            actions = [
                "replace_overbroad_trigger_with_bad_context",
                "add_branch_local_pattern_not",
                "add_pattern_not_inside",
            ]
        elif prefers_good_exclusion:
            actions = [
                "add_pattern_not_inside",
                "add_branch_local_pattern_not",
            ]
            if has_stable_bad_context and not saw_overcut:
                actions.extend(["replace_overbroad_trigger_with_bad_context", "add_pattern_inside"])
        elif saw_overcut:
            actions = [
                "add_pattern_not_inside",
                "add_branch_local_pattern_not",
                "add_taint_sanitizer_or_scope_guard",
            ]
        elif no_yaml_alignment and not has_stable_bad_context:
            actions = [
                "add_branch_local_pattern_not",
                "add_pattern_not_inside",
            ]
        else:
            actions = [
                "replace_overbroad_trigger_with_bad_context",
                "add_pattern_not_inside",
                "add_branch_local_pattern_not",
                "add_pattern_inside",
            ]
        if good_only_positive:
            actions.insert(0, "remove_good_only_positive_branch")
        if not weak_identifier_constraint:
            actions.append("add_metavariable_constraint")
        if dataflow_like:
            actions.append("add_taint_sanitizer_or_scope_guard")
        if saw_exclusion_noop and not saw_overcut:
            promoted: list[str] = []
            if dataflow_like:
                promoted.append("add_taint_sanitizer_or_scope_guard")
            if (not weak_identifier_constraint) and not prefers_good_exclusion:
                promoted.append("add_metavariable_constraint")
            if has_stable_bad_context and not prefers_good_exclusion:
                promoted.extend(["replace_overbroad_trigger_with_bad_context", "add_pattern_inside"])
            for action in reversed(promoted):
                if action not in actions:
                    actions.insert(0, action)
        if saw_replacement_noop and not saw_overcut:
            for action in ("add_pattern_not_inside", "add_branch_local_pattern_not", "add_metavariable_constraint"):
                if action not in actions:
                    actions.insert(0, action)
        filtered = [
            action for action in actions
            if _action_allowed_by_failure_memory(action, failure_classes, target, has_stable_bad_context)
        ]
        if filtered:
            actions = filtered
        elif dataflow_like:
            actions = ["add_taint_sanitizer_or_scope_guard", "add_pattern_not_inside", "add_branch_local_pattern_not"]
        elif saw_overcut or prefers_good_exclusion:
            actions = ["add_pattern_not_inside", "add_branch_local_pattern_not"]
    else:
        actions = [
            "replace_overbroad_trigger_with_bad_context",
            "add_sibling_branch_to_pattern_either",
            "add_branch_local_pattern_not",
        ]
        if dataflow_like:
            actions.extend(["add_taint_source_sink_or_propagator", "add_taint_sanitizer_or_scope_guard"])
        actions.append("generalize_local_positive_predicate")

    out: list[str] = []
    seen: set[str] = set()
    rejected_actions = {
        str(item.get("edit_action") or "")
        for item in _rejected_repair_entries(analysis)
        if str(item.get("focus") or "") in {"", focus}
    }
    for action in actions:
        if action in seen:
            continue
        if action in rejected_actions and len(actions) > 1:
            continue
        seen.add(action)
        out.append(action)
    if not out:
        out = [action for action in actions if action]
    return out


def build_repair_edit_contract(
    current_rule_yaml: str,
    analysis: dict[str, Any],
    focus: str,
) -> dict[str, Any]:
    """Create a constrained, RuleRefiner-style local edit contract for the LLM.

    RuleRefiner's strongest useful constraint is not merely "look at the
    explanation"; it localizes a faulty/reference path diff, then asks for one
    template-like edit around that predicate. This contract makes that explicit
    without adding CWE-specific recipes.
    """
    target = _top_localized_target(analysis, focus)
    actions = _repair_contract_actions(focus, target, current_rule_yaml, analysis)
    if focus in {"too_narrow_coverage", "missed_bad"}:
        objective = "BAD-first stage: increase BAD coverage by extending or unblocking the localized branch; postpone precision-only GOOD cleanup until BAD coverage reaches the target floor."
        required_effect = "BAD hit count must increase. GOOD false positives are recorded as a follow-up precision issue, not the acceptance criterion for this coverage repair."
        forbidden = [
            "Do not replace a working branch with a broad catch-all.",
            "Do not remove precision guards except when the localized guard is proven to overblock BAD and is replaced by a narrower safe subset.",
            "Do not use one branch per sample.",
            "Do not edit an already-working sibling branch when the contract source is missed_bad_carrier_shape; add one new evidence-backed sibling branch instead.",
        ]
    elif focus in {"too_broad_precision", "flagged_good"}:
        objective = "Reduce GOOD false positives by constraining the localized overbroad branch; do not chase new BAD coverage in this repair."
        required_effect = "GOOD false positives must decrease and BAD hit count must not decrease."
        forbidden = [
            "Do not add new coverage branches in a precision repair.",
            "Do not add global pattern-not exclusions that suppress unrelated BAD branches.",
            "Do not keep an all-metavariable API/operator trigger as the only positive evidence.",
            "Do not replace the whole rule with a narrower rule that loses current BAD hits.",
        ]
    else:
        objective = "Improve total correctness with one localized edit; choose precision if broad FP and coverage if low BAD recall conflict."
        required_effect = "BAD hit count must not decrease, GOOD false positives must not increase, and at least one metric must improve."
        forbidden = [
            "Do not rewrite the entire rule unless the localized target is syntactically invalid or empty.",
            "Do not add sample-specific branches or benchmark identity anchors.",
        ]

    template_shapes = {
        "add_sibling_branch_to_pattern_either": (
            "Wrap the current positive branch and one new evidence-backed BAD branch in a flat pattern-either; "
            "the new branch must implement the localized missed-BAD carrier shape using the catalog evidence/examples; keep all old branches unchanged."
        ),
        "generalize_local_positive_predicate": (
            "Change only the localized positive pattern so it covers a semantic sibling carrier/API/operator; "
            "preserve branch-local guards."
        ),
        "weaken_overblocking_exclusion": (
            "Replace a broad localized pattern-not/pattern-not-inside with a narrower overlapping safe subset, "
            "or move the distinction into positive BAD-only context."
        ),
        "add_taint_source_sink_or_propagator": (
            "In taint mode, add one missing source, sink, propagator, or side-effect focus entry tied to the same data metavariable."
        ),
        "replace_overbroad_trigger_with_bad_context": (
            "Keep the branch but replace/augment the broad trigger with BAD-only argument, operand, type, API, or local context."
        ),
        "remove_good_only_positive_branch": (
            "Remove the localized positive branch only when predicate profiling shows it fires on flagged GOOD and essentially never on hit BAD."
        ),
        "add_branch_local_pattern_not": (
            "Add a branch-local pattern-not only when it is a narrower safe subset of the positive branch and uses bound metavariables."
        ),
        "add_pattern_inside": "Add branch-local required surrounding context that is present in BAD and absent in flagged GOOD.",
        "add_pattern_not_inside": "Exclude a local ordered safe region that contains the matched trigger and uses the same bound metavariable.",
        "add_metavariable_constraint": (
            "Use metavariable-regex/comparison/pattern only for a bound metavariable when it expresses a concrete BAD/GOOD separator; never use it only to constrain ordinary identifier spelling."
        ),
        "add_taint_sanitizer_or_scope_guard": (
            "In taint mode, add a sanitizer/scope guard for validation, trusted constant overwrite, or allowlist behavior seen in GOOD."
        ),
    }
    return {
        "contract_version": "repair-edit-contract-v1",
        "focus": focus,
        "objective": objective,
        "localized_target": target,
        "missed_bad_carrier_shape_catalog": analysis.get("missed_bad_carrier_shape_catalog"),
        "branch_local_contrast": analysis.get("branch_local_contrast"),
        "predicate_discriminative_scores": analysis.get("predicate_discriminative_scores"),
        "repair_gate": analysis.get("repair_gate"),
        "allowed_actions": actions,
        "choose_exactly_one_action": True,
        "required_effect": required_effect,
        "forbidden_edits": forbidden,
        "template_action_guidance": {action: template_shapes.get(action, "") for action in actions},
        "response_fields_required": [
            "edit_action",
            "localized_predicate",
            "regression_expectation",
            "patch_fragment_yaml",
            "semgrep_rule_yaml",
            "notes",
        ],
    }


def _case_state_sets(prev_eval: dict[str, Any], truth_by_file: dict[str, Any]) -> dict[str, set[tuple[str, str, int, int]]]:
    all_records = _all_region_records(truth_by_file)
    all_bad = {tuple(record["key"]) for record in all_records if record.get("label") == "bad"}
    all_good = {tuple(record["key"]) for record in all_records if record.get("label") == "good"}
    missed_bad = {
        _item_key(item)
        for item in prev_eval.get("missed_bad_examples", [])
        if isinstance(item, dict) and str(item.get("path") or "").strip()
    }
    flagged_good = {
        _item_key(item)
        for item in prev_eval.get("flagged_good_examples", [])
        if isinstance(item, dict) and str(item.get("path") or "").strip()
    }
    return {
        "missed_bad": missed_bad,
        "flagged_good": flagged_good,
        "hit_bad": all_bad - missed_bad,
        "clean_good": all_good - flagged_good,
    }


def _record_for_key(records: list[dict[str, Any]], key: tuple[str, str, int, int]) -> dict[str, Any] | None:
    for record in records:
        if tuple(record.get("key", ())) == key:
            return record
    return None


def _extract_rule_patterns(rule_yaml: str) -> list[str]:
    try:
        payload = yaml.safe_load(rule_yaml)
    except Exception:
        return []
    out: list[str] = []

    def visit(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {
                    "pattern",
                    "pattern-not",
                    "pattern-inside",
                    "pattern-not-inside",
                    "pattern-regex",
                    "pattern-not-regex",
                    "focus-metavariable",
                    "metavariable-regex",
                    "metavariable-pattern",
                    "metavariable-comparison",
                }:
                    out.append(f"{path}{key}: {_short(value, 220)}")
                else:
                    visit(value, f"{path}{key}.")
        elif isinstance(node, list):
            for item in node:
                visit(item, path)

    visit(payload)
    seen: set[str] = set()
    unique: list[str] = []
    for item in out:
        key = re.sub(r"\s+", " ", item.strip())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique[:80]


def _semantic_pattern_signature(rule_yaml: str) -> list[str]:
    try:
        payload = yaml.safe_load(rule_yaml)
    except Exception:
        return []
    parts: list[str] = []
    keys = {
        "pattern",
        "pattern-not",
        "pattern-inside",
        "pattern-not-inside",
        "pattern-regex",
        "pattern-not-regex",
        "focus-metavariable",
        "metavariable-regex",
        "metavariable-pattern",
        "metavariable-comparison",
        "mode",
        "pattern-sources",
        "pattern-sinks",
        "pattern-sanitizers",
        "pattern-propagators",
        "metavariable",
        "regex",
        "from",
        "to",
        "by-side-effect",
    }

    def norm(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return re.sub(r"\s+", " ", yaml.safe_dump(value, sort_keys=True, allow_unicode=True)).strip()
        return re.sub(r"\s+", " ", str(value or "")).strip()

    def visit(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                next_path = f"{path}{key}."
                if key in keys:
                    parts.append(f"{path}{key}={norm(value)}")
                visit(value, next_path)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                visit(item, f"{path}{idx}.")

    visit(payload)
    return sorted(parts)


def _repair_candidate_is_semantic_noop(base_rule_yaml: str, candidate_rule_yaml: str) -> bool:
    base_sig = _semantic_pattern_signature(base_rule_yaml)
    cand_sig = _semantic_pattern_signature(candidate_rule_yaml)
    return bool(base_sig and cand_sig and base_sig == cand_sig)


def _payload_patch_fragment(payload: dict[str, Any]) -> Any:
    raw = payload.get("patch_fragment_yaml") if isinstance(payload, dict) else ""
    parsed: Any
    if isinstance(raw, (dict, list)):
        return _normalize_fragment_scalars(raw)
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        parsed = yaml.safe_load(raw)
        return _normalize_fragment_scalars(parsed)
    except Exception:
        try:
            parsed = yaml.safe_load("- " + raw.strip())
            return _normalize_fragment_scalars(parsed)
        except Exception:
            return None


def _as_branch_item(fragment: Any) -> dict[str, Any] | None:
    if isinstance(fragment, dict):
        if "patterns" in fragment or "pattern" in fragment or "pattern-either" in fragment:
            return fragment
        return None
    if isinstance(fragment, list):
        if len(fragment) == 1 and isinstance(fragment[0], dict):
            return _as_branch_item(fragment[0])
        if all(isinstance(item, dict) for item in fragment):
            return {"patterns": fragment}
    return None


def _as_constraint_item(fragment: Any) -> dict[str, Any] | None:
    if isinstance(fragment, dict):
        allowed = {
            "pattern",
            "pattern-not",
            "pattern-inside",
            "pattern-not-inside",
            "pattern-regex",
            "pattern-not-regex",
            "metavariable-regex",
            "metavariable-pattern",
            "metavariable-comparison",
        }
        if any(key in fragment for key in allowed):
            return fragment
    if isinstance(fragment, list) and len(fragment) == 1 and isinstance(fragment[0], dict):
        return _as_constraint_item(fragment[0])
    return None


def _first_rule_node(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules or not isinstance(rules[0], dict):
        return None
    return rules[0]


def _yaml_path_tokens(path: str) -> list[str]:
    return [token for token in str(path or "").strip(".").split(".") if token != ""]


def _node_at_yaml_path(root: Any, path: str) -> Any:
    node = root
    for token in _yaml_path_tokens(path):
        if isinstance(node, dict):
            if token not in node:
                return None
            node = node[token]
            continue
        if isinstance(node, list):
            try:
                index = int(token)
            except ValueError:
                return None
            if index < 0 or index >= len(node):
                return None
            node = node[index]
            continue
        return None
    return node


def _localized_target_from_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    contract = analysis.get("repair_edit_contract") if isinstance(analysis.get("repair_edit_contract"), dict) else {}
    target = contract.get("localized_target") if isinstance(contract.get("localized_target"), dict) else {}
    return target if isinstance(target, dict) else {}


def _localized_branch_node(root: Any, target: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("branch_prefix", "yaml_path"):
        path = str(target.get(key) or "")
        while path:
            node = _node_at_yaml_path(root, path)
            if isinstance(node, dict) and ("pattern" in node or "patterns" in node or "pattern-either" in node):
                return node
            path = ".".join(_yaml_path_tokens(path)[:-1]) + "."
    return None


def _localized_parent_pattern_either(root: Any, target: dict[str, Any]) -> list[Any] | None:
    tokens = _yaml_path_tokens(str(target.get("branch_prefix") or target.get("yaml_path") or ""))
    for end in range(len(tokens), 0, -1):
        parent = _node_at_yaml_path(root, ".".join(tokens[:end]))
        if isinstance(parent, dict) and isinstance(parent.get("pattern-either"), list):
            return parent["pattern-either"]
        if isinstance(parent, list) and end > 0 and tokens[end - 1] == "pattern-either":
            return parent
    rule = _first_rule_node(root)
    if isinstance(rule, dict) and isinstance(rule.get("pattern-either"), list):
        return rule["pattern-either"]
    return None


def _insert_branch_local(rule: dict[str, Any], branch_item: dict[str, Any]) -> bool:
    if "pattern-either" in rule and isinstance(rule.get("pattern-either"), list):
        rule["pattern-either"].append(branch_item)
        return True
    if "patterns" in rule and isinstance(rule.get("patterns"), list):
        old = {"patterns": rule.pop("patterns")}
        rule["pattern-either"] = [old, branch_item]
        return True
    if "pattern" in rule:
        old = {"pattern": rule.pop("pattern")}
        rule["pattern-either"] = [old, branch_item]
        return True
    return False


def _insert_branch_near_localized_target(root: Any, target: dict[str, Any], branch_item: dict[str, Any]) -> bool:
    parent = _localized_parent_pattern_either(root, target)
    if isinstance(parent, list):
        insert_at = None
        tokens = _yaml_path_tokens(str(target.get("branch_prefix") or target.get("yaml_path") or ""))
        for idx, token in enumerate(tokens[:-1]):
            if token == "pattern-either":
                try:
                    insert_at = int(tokens[idx + 1]) + 1
                except ValueError:
                    insert_at = None
                break
        if insert_at is None or insert_at < 0 or insert_at > len(parent):
            parent.append(branch_item)
        else:
            parent.insert(insert_at, branch_item)
        return True

    rule = _first_rule_node(root)
    return _insert_branch_local(rule, branch_item) if isinstance(rule, dict) else False


def _append_constraint_to_first_branch(rule: dict[str, Any], constraint: dict[str, Any]) -> bool:
    branches = rule.get("pattern-either")
    if isinstance(branches, list):
        for branch in branches:
            if isinstance(branch, dict) and isinstance(branch.get("patterns"), list):
                branch["patterns"].append(constraint)
                return True
            if isinstance(branch, dict) and "pattern" in branch:
                pattern = branch.pop("pattern")
                branch["patterns"] = [{"pattern": pattern}, constraint]
                return True
    if isinstance(rule.get("patterns"), list):
        rule["patterns"].append(constraint)
        return True
    if "pattern" in rule:
        pattern = rule.pop("pattern")
        rule["patterns"] = [{"pattern": pattern}, constraint]
        return True
    return False


def _append_constraint_to_branch(branch: dict[str, Any], constraint: dict[str, Any]) -> bool:
    if isinstance(branch.get("patterns"), list):
        branch["patterns"].append(constraint)
        return True
    if "pattern" in branch:
        pattern = branch.pop("pattern")
        branch["patterns"] = [{"pattern": pattern}, constraint]
        return True
    if "pattern-regex" in branch:
        pattern_regex = branch.pop("pattern-regex")
        branch["patterns"] = [{"pattern-regex": pattern_regex}, constraint]
        return True
    return False


def _replace_localized_branch(root: Any, target: dict[str, Any], branch_item: dict[str, Any]) -> bool:
    path = str(target.get("branch_prefix") or target.get("yaml_path") or "")
    tokens = _yaml_path_tokens(path)
    if not tokens:
        return False
    for end in range(len(tokens), 0, -1):
        parent_path = ".".join(tokens[: end - 1])
        last = tokens[end - 1]
        parent = _node_at_yaml_path(root, parent_path)
        if isinstance(parent, list):
            try:
                index = int(last)
            except ValueError:
                continue
            if 0 <= index < len(parent):
                parent[index] = branch_item
                return True
        if isinstance(parent, dict) and last in parent and isinstance(parent[last], dict):
            parent[last] = branch_item
            return True
    return False


def _remove_localized_branch(root: Any, target: dict[str, Any]) -> bool:
    path = str(target.get("branch_prefix") or target.get("yaml_path") or "")
    tokens = _yaml_path_tokens(path)
    if not tokens:
        return False
    for end in range(len(tokens), 0, -1):
        parent_path = ".".join(tokens[: end - 1])
        last = tokens[end - 1]
        parent = _node_at_yaml_path(root, parent_path)
        if isinstance(parent, list):
            try:
                index = int(last)
            except ValueError:
                continue
            if 0 <= index < len(parent):
                del parent[index]
                return True
        if isinstance(parent, dict) and last in parent:
            del parent[last]
            return True
    return False


def _append_constraint_to_localized_target(root: Any, target: dict[str, Any], constraint: dict[str, Any]) -> bool:
    branch = _localized_branch_node(root, target)
    if isinstance(branch, dict) and _append_constraint_to_branch(branch, constraint):
        return True
    rule = _first_rule_node(root)
    return _append_constraint_to_first_branch(rule, constraint) if isinstance(rule, dict) else False


def _branch_item_single_constraint(branch_item: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(branch_item, dict):
        return None
    if len(branch_item) == 1 and any(
        key in branch_item
        for key in (
            "pattern-not",
            "pattern-not-regex",
            "pattern-inside",
            "pattern-not-inside",
            "metavariable-regex",
            "metavariable-pattern",
            "metavariable-comparison",
        )
    ):
        return branch_item
    patterns = branch_item.get("patterns")
    if isinstance(patterns, list) and len(patterns) == 1 and isinstance(patterns[0], dict):
        return _as_constraint_item(patterns[0])
    return None


def _constraint_from_branch_for_action(branch_item: dict[str, Any], action: str) -> dict[str, Any] | None:
    if not isinstance(branch_item, dict):
        return None
    action_keys = {
        "replace_overbroad_trigger_with_bad_context": {"pattern-not", "pattern-not-regex", "pattern-not-inside"},
        "add_branch_local_pattern_not": {"pattern-not", "pattern-not-regex"},
        "add_pattern_not_inside": {"pattern-not-inside"},
        "add_pattern_inside": {"pattern-inside", "pattern-not-inside"},
        "add_metavariable_constraint": {"metavariable-regex", "metavariable-pattern", "metavariable-comparison"},
        "add_taint_sanitizer_or_scope_guard": {"pattern-not", "pattern-not-inside", "pattern-sanitizers"},
    }
    keys = action_keys.get(action, set())
    if not keys:
        return None

    def visit(node: Any) -> dict[str, Any] | None:
        if isinstance(node, dict):
            if len(node) == 1 and next(iter(node.keys())) in keys:
                return copy.deepcopy(node)
            for key, value in node.items():
                if key in keys:
                    return {key: copy.deepcopy(value)}
                found = visit(value)
                if found:
                    return found
        elif isinstance(node, list):
            for item in node:
                found = visit(item)
                if found:
                    return found
        return None

    return visit(branch_item)


def _positive_patterns_from_branch(branch: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if not isinstance(branch, dict):
        return out
    if isinstance(branch.get("pattern"), str):
        out.append(str(branch.get("pattern") or ""))
    if isinstance(branch.get("pattern-regex"), str):
        out.append(str(branch.get("pattern-regex") or ""))
    patterns = branch.get("patterns")
    if isinstance(patterns, list):
        for item in patterns:
            if isinstance(item, dict):
                if isinstance(item.get("pattern"), str):
                    out.append(str(item.get("pattern") or ""))
                if isinstance(item.get("pattern-regex"), str):
                    out.append(str(item.get("pattern-regex") or ""))
    return out


def _extract_single_call_arg(pattern: str, func_name: str) -> str:
    match = re.search(rf"\b{re.escape(func_name)}\s*\(\s*([^,)]+?)\s*\)\s*;?", str(pattern or ""))
    return match.group(1).strip() if match else ""


def _release_positive_pointer_patterns(branch: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for pattern in _positive_patterns_from_branch(branch):
        free_arg = _extract_single_call_arg(pattern, "free")
        if free_arg:
            out.append(("free", free_arg))
        match = re.search(r"\bdelete(?:\s*\[\])?\s+([^;]+?)\s*;?\s*$", pattern.strip())
        if match:
            out.append(("delete", match.group(1).strip()))
    return out


def _constraint_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)


def _normalize_fragment_scalar_text(text: str) -> str:
    out = str(text or "")
    if "\\n" in out or "\\t" in out:
        try:
            out = out.encode("utf-8").decode("unicode_escape")
        except UnicodeDecodeError:
            out = out.replace("\\n", "\n").replace("\\t", "\t")
    out = re.sub(r"(?m)^(\s*[^;\n]+;)\s*;\s*$", r"\1", out)
    return out


def _normalize_fragment_scalars(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _normalize_fragment_scalars(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_normalize_fragment_scalars(item) for item in node]
    if isinstance(node, str):
        return _normalize_fragment_scalar_text(node)
    return node


def _release_reset_precision_constraints(branch: dict[str, Any]) -> list[dict[str, str]]:
    constraints: list[dict[str, str]] = []
    for release_kind, ptr in _release_positive_pointer_patterns(branch):
        if not ptr or ptr == "...":
            continue
        resets = ["NULL", "nullptr", "0"]
        if release_kind == "delete":
            release_stmt = f"delete {ptr};"
        else:
            release_stmt = f"free({ptr});"
        for reset in resets:
            constraints.append(
                {
                    "pattern-not-inside": (
                        "if (...) {\n"
                        "  ...\n"
                        f"  {release_stmt}\n"
                        "  ...\n"
                        f"  {ptr} = {reset};\n"
                        "  ...\n"
                        "}"
                    )
                }
            )
            constraints.append(
                {
                    "pattern-not-inside": (
                        f"{release_stmt}\n"
                        "...\n"
                        f"{ptr} = {reset};"
                    )
                }
            )
    return constraints


def _ensure_release_pointer_bound(branch: dict[str, Any]) -> bool:
    """Turn broad release triggers into same-pointer-bindable triggers."""
    if not isinstance(branch, dict):
        return False
    changed = False

    def bind_pattern(text: str) -> tuple[str, bool]:
        stripped = str(text or "").strip()
        if re.fullmatch(r"free\s*\(\s*\.\.\.\s*\)\s*;?", stripped):
            return "free($P);", True
        if re.fullmatch(r"delete\s+\.\.\.\s*;?", stripped):
            return "delete $P;", True
        if re.fullmatch(r"delete\s*\[\]\s+\.\.\.\s*;?", stripped):
            return "delete[] $P;", True
        return text, False

    for key in ("pattern",):
        if isinstance(branch.get(key), str):
            new_value, did_change = bind_pattern(str(branch.get(key) or ""))
            if did_change:
                branch[key] = new_value
                changed = True
    patterns = branch.get("patterns")
    if isinstance(patterns, list):
        for item in patterns:
            if isinstance(item, dict) and isinstance(item.get("pattern"), str):
                new_value, did_change = bind_pattern(str(item.get("pattern") or ""))
                if did_change:
                    item["pattern"] = new_value
                    changed = True
    return changed


def _append_constraints_to_localized_target(root: Any, target: dict[str, Any], constraints: list[dict[str, Any]]) -> bool:
    changed = False
    for constraint in constraints:
        if not isinstance(constraint, dict):
            continue
        if _append_constraint_to_localized_target(root, target, constraint):
            changed = True
    return changed


def _append_release_reset_constraints(root: Any, target: dict[str, Any]) -> bool:
    branch = _localized_branch_node(root, target)
    if not isinstance(branch, dict):
        return False
    changed = _ensure_release_pointer_bound(branch)
    constraints = _release_reset_precision_constraints(branch)
    if not constraints:
        return changed
    existing = {
        (key, re.sub(r"\s+", " ", _constraint_text(value)).strip())
        for item in branch.get("patterns", [])
        if isinstance(item, dict)
        for key, value in item.items()
        if key in {"pattern-not-inside", "pattern-not"}
    } if isinstance(branch.get("patterns"), list) else set()
    new_constraints = []
    for constraint in constraints:
        key, value = next(iter(constraint.items()))
        signature = (key, re.sub(r"\s+", " ", _constraint_text(value)).strip())
        if signature not in existing:
            new_constraints.append(constraint)
            existing.add(signature)
    return _append_constraints_to_localized_target(root, target, new_constraints) or changed


def _append_release_reset_constraints_to_release_siblings(root: Any, target: dict[str, Any]) -> bool:
    parent = _localized_parent_pattern_either(root, target)
    branches = [branch for branch in parent if isinstance(branch, dict)] if isinstance(parent, list) else []
    if not branches:
        branch = _localized_branch_node(root, target)
        branches = [branch] if isinstance(branch, dict) else []
    changed = False
    for branch in branches:
        positives = "\n".join(_positive_patterns_from_branch(branch)).lower()
        if "free" not in positives and "delete" not in positives:
            continue
        changed = _ensure_release_pointer_bound(branch) or changed
        constraints = _release_reset_precision_constraints(branch)
        if not constraints:
            continue
        existing = {
            (key, re.sub(r"\s+", " ", _constraint_text(value)).strip())
            for item in branch.get("patterns", [])
            if isinstance(item, dict)
            for key, value in item.items()
            if key in {"pattern-not-inside", "pattern-not"}
        } if isinstance(branch.get("patterns"), list) else set()
        new_constraints = []
        for constraint in constraints:
            key, value = next(iter(constraint.items()))
            signature = (key, re.sub(r"\s+", " ", _constraint_text(value)).strip())
            if signature not in existing:
                new_constraints.append(constraint)
                existing.add(signature)
        for constraint in new_constraints:
            changed = _append_constraint_to_branch(branch, constraint) or changed
    return changed


def _positive_pattern_strings(branch: dict[str, Any]) -> list[str]:
    if not isinstance(branch, dict):
        return []
    out: list[str] = []
    if isinstance(branch.get("pattern"), str):
        out.append(str(branch.get("pattern") or ""))
    patterns = branch.get("patterns")
    if isinstance(patterns, list):
        for item in patterns:
            if isinstance(item, dict) and isinstance(item.get("pattern"), str):
                out.append(str(item.get("pattern") or ""))
    return out


def _branch_pattern_texts(branch: dict[str, Any], keys: set[str] | None = None) -> list[str]:
    if not isinstance(branch, dict):
        return []
    wanted = keys or {"pattern", "pattern-inside", "pattern-regex"}
    out: list[str] = []
    for key in wanted:
        if isinstance(branch.get(key), str):
            out.append(str(branch.get(key) or ""))
    patterns = branch.get("patterns")
    if isinstance(patterns, list):
        for item in patterns:
            if not isinstance(item, dict):
                continue
            for key in wanted:
                if isinstance(item.get(key), str):
                    out.append(str(item.get(key) or ""))
    return out


def _branch_has_any_constraint(branch: dict[str, Any], key: str, text: str) -> bool:
    wanted = re.sub(r"\s+", " ", str(text or "")).strip()
    if not wanted:
        return False
    if isinstance(branch.get(key), str):
        current = re.sub(r"\s+", " ", str(branch.get(key) or "")).strip()
        if current == wanted:
            return True
    patterns = branch.get("patterns")
    if not isinstance(patterns, list):
        return False
    for item in patterns:
        if not isinstance(item, dict) or key not in item:
            continue
        current = re.sub(r"\s+", " ", _constraint_text(item.get(key))).strip()
        if current == wanted:
            return True
    return False


def _branch_has_constraint(branch: dict[str, Any], key: str, text: str) -> bool:
    wanted = re.sub(r"\s+", " ", str(text or "")).strip()
    patterns = branch.get("patterns")
    if not isinstance(patterns, list):
        return False
    for item in patterns:
        if not isinstance(item, dict) or key not in item:
            continue
        current = re.sub(r"\s+", " ", _constraint_text(item.get(key))).strip()
        if current == wanted:
            return True
    return False


def _append_unique_constraint_to_branch(branch: dict[str, Any], constraint: dict[str, Any]) -> bool:
    if not isinstance(branch, dict) or not isinstance(constraint, dict) or len(constraint) != 1:
        return False
    key, value = next(iter(constraint.items()))
    if _branch_has_any_constraint(branch, str(key), _constraint_text(value)):
        return False
    return _append_constraint_to_branch(branch, constraint)



def _final_else_exclusion_for_pattern(pattern: str) -> str:
    text = str(pattern or "").strip()
    if "else if" not in text or re.search(r"\belse\s*\{", text):
        return ""
    lines = text.splitlines()
    while lines and lines[-1].strip() == "...":
        lines.pop()
    text = "\n".join(lines).rstrip()
    if not text:
        return ""
    return text + " else {\n  ...\n}"


def _append_final_else_exclusions_to_control_flow_siblings(root: Any, target: dict[str, Any]) -> bool:
    parent = _localized_parent_pattern_either(root, target)
    if not isinstance(parent, list):
        return False
    changed = False
    for branch in parent:
        if not isinstance(branch, dict):
            continue
        for positive in _positive_pattern_strings(branch):
            exclusion = _final_else_exclusion_for_pattern(positive)
            if not exclusion:
                continue
            constraint = {"pattern-not-inside": exclusion}
            if _branch_has_constraint(branch, "pattern-not-inside", exclusion):
                continue
            if _append_constraint_to_branch(branch, constraint):
                changed = True
            break
    return changed


INTEGER_CAST_TYPES = ("int", "short", "long", "long long", "unsigned int", "unsigned short", "unsigned long")
INTEGER_CAST_REGEX = r"=\s*[^;\n]*\(\s*(?:int|short|long(?:\s+long)?|unsigned\s+(?:int|short|long))\s*\)"
INTEGER_CAST_RETURN_REGEX = r"\breturn\s+\(\s*(?:int|short|long(?:\s+long)?|unsigned\s+(?:int|short|long))\s*\)"
INTEGER_CAST_METAVAR_NEGATIVE_REGEX = r"^(?!\s*\(\s*(?:int|short|long(?:\s+long)?|unsigned\s+(?:int|short|long))\s*\))"


def _conversion_rhs_metavariables(pattern: str) -> list[str]:
    text = re.sub(r"\s+", " ", str(pattern or "").strip())
    if not text:
        return []
    rhs = ""
    if "=" in text and not re.search(r"(?:==|!=|<=|>=)", text):
        rhs = text.split("=", 1)[1]
    else:
        return_match = re.search(r"\breturn\s+(.+)", text)
        if return_match:
            rhs = return_match.group(1)
    if not rhs:
        return []
    names = re.findall(r"\$[A-Z][A-Z0-9_]*", rhs)
    out: list[str] = []
    for name in names:
        if name not in out:
            out.append(name)
    return out[:4]


def _explicit_cast_exclusions_for_pattern(pattern: str) -> list[dict[str, Any]]:
    text = str(pattern or "").strip()
    if not text:
        return []
    stripped = text.rstrip(";").strip()
    exclusions: list[dict[str, Any]] = []
    assignment_like = "=" in stripped and not re.search(r"(?:==|!=|<=|>=)", stripped)
    return_like = bool(re.search(r"\breturn\b", stripped))
    for metavariable in _conversion_rhs_metavariables(stripped):
        exclusions.append(
            {
                "metavariable-regex": {
                    "metavariable": metavariable,
                    "regex": INTEGER_CAST_METAVAR_NEGATIVE_REGEX,
                }
            }
        )
    # Put the local lexical guards first. Exact structural exclusions are useful
    # for simple same-span cases, but a compound cast such as `(int)a + (int)b`
    # is often only distinguishable with a line-local regex.
    if assignment_like:
        exclusions.append({"pattern-not-regex": INTEGER_CAST_REGEX})
    if return_like:
        exclusions.append({"pattern-not-regex": INTEGER_CAST_RETURN_REGEX})
    if "\n" in text or "..." in text:
        return exclusions
    if assignment_like:
        lhs, rhs = stripped.split("=", 1)
        lhs = lhs.strip()
        rhs = rhs.strip()
        if lhs and rhs and not rhs.startswith("("):
            for cast_type in INTEGER_CAST_TYPES:
                exclusions.append({"pattern-not": f"{lhs} = ({cast_type}) {rhs};"})
                exclusions.append({"pattern-not": f"{lhs} = ({cast_type})({rhs});"})
    return_match = re.fullmatch(r"return\s+(.+)", stripped)
    if return_match:
        rhs = return_match.group(1).strip()
        if rhs and not rhs.startswith("("):
            for cast_type in INTEGER_CAST_TYPES:
                exclusions.append({"pattern-not": f"return ({cast_type}) {rhs};"})
                exclusions.append({"pattern-not": f"return ({cast_type})({rhs});"})
    return exclusions


def _append_explicit_cast_exclusions_to_conversion_siblings(root: Any, target: dict[str, Any]) -> bool:
    parent = _localized_parent_pattern_either(root, target)
    branches = [branch for branch in parent if isinstance(branch, dict)] if isinstance(parent, list) else []
    if not branches:
        branch = _localized_branch_node(root, target)
        branches = [branch] if isinstance(branch, dict) else []
    changed = False
    for branch in branches:
        for positive in _positive_pattern_strings(branch):
            for constraint in _explicit_cast_exclusions_for_pattern(positive)[:8]:
                changed = _append_unique_constraint_to_branch(branch, constraint) or changed
    return changed


def _allocator_names_from_pattern(pattern: str) -> list[str]:
    text = str(pattern or "").lower()
    names = []
    for name in ("malloc", "calloc", "realloc"):
        if re.search(rf"\b{name}\s*\(", text):
            names.append(name)
    return names


def _use_shapes_from_pattern(pattern: str) -> list[str]:
    text = str(pattern or "")
    shapes: list[str] = []
    if re.search(r"\*\s*\$[A-Z0-9_]+\s*=", text):
        shapes.append("deref_write")
    if re.search(r"\$[A-Z0-9_]+\s*\[[^\]]*\]\s*=", text):
        shapes.append("subscript_write")
    return shapes


def _pointer_metavariable_from_use_patterns(patterns: list[str]) -> str:
    joined = "\n".join(str(pattern or "") for pattern in patterns)
    for regex in (
        r"\*\s*(\$[A-Z0-9_]+)\s*=",
        r"(\$[A-Z0-9_]+)\s*\[[^\]]*\]\s*=",
        r"\*\s*(\$[A-Z0-9_]+)\b",
    ):
        match = re.search(regex, joined)
        if match:
            return match.group(1)
    for regex in (
        r"\*\s*(\$[A-Z0-9_]+)\s*=\s*(?:\([^)]*\)\s*)?(?:malloc|calloc|realloc)\s*\(",
        r"(\$[A-Z0-9_]+)\s*=\s*(?:\([^)]*\)\s*)?(?:malloc|calloc|realloc)\s*\(",
    ):
        match = re.search(regex, joined)
        if match:
            return match.group(1)
    return ""


def _use_statements_for_pointer(patterns: list[str], ptr: str) -> list[str]:
    out: list[str] = []
    if not ptr:
        return out
    ptr_re = re.escape(ptr)
    for pattern in patterns:
        text = str(pattern or "")
        for regex in (
            rf"\*\s*{ptr_re}\s*=\s*[^;]+;",
            rf"{ptr_re}\s*\[[^\]]*\]\s*=\s*[^;]+;",
        ):
            for match in re.finditer(regex, text):
                stmt = re.sub(r"\s+", " ", match.group(0)).strip()
                if any(name in stmt.lower() for name in ("malloc", "calloc", "realloc")):
                    continue
                if stmt and stmt not in out:
                    out.append(stmt)
    return out[:4]


def _malloc_guard_exclusions_for_branch(branch: dict[str, Any]) -> list[dict[str, str]]:
    positives = _branch_pattern_texts(branch, {"pattern", "pattern-inside", "pattern-regex"})
    if not positives:
        return []
    joined = "\n".join(positives)
    if not any(_allocator_names_from_pattern(pattern) for pattern in positives):
        return []
    if not any(_use_shapes_from_pattern(pattern) for pattern in positives):
        return []
    ptr = _pointer_metavariable_from_use_patterns(positives)
    if not ptr:
        return []
    use_patterns = _use_statements_for_pointer(positives, ptr)
    if not use_patterns:
        use_patterns = [f"*{ptr} = ...;", f"{ptr}[...] = ...;"]

    constraints: list[dict[str, str]] = []
    for use in use_patterns[:3]:
        use = use.strip()
        if not use.endswith(";"):
            use += ";"
        constraints.extend(
            [
                {
                    "pattern-not-inside": (
                        f"if (!{ptr})\n"
                        "  return;\n"
                        "...\n"
                        f"{use}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if (!{ptr}) {{\n"
                        "  ...\n"
                        "  return;\n"
                        "}\n"
                        "...\n"
                        f"{use}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if ({ptr} == NULL)\n"
                        "  return;\n"
                        "...\n"
                        f"{use}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if ({ptr} == nullptr)\n"
                        "  return;\n"
                        "...\n"
                        f"{use}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if ({ptr} != NULL) {{\n"
                        "  ...\n"
                        f"  {use}\n"
                        "  ...\n"
                        "}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if ({ptr}) {{\n"
                        "  ...\n"
                        f"  {use}\n"
                        "  ...\n"
                        "}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if ((bool){ptr}) {{\n"
                        "  ...\n"
                        f"  {use}\n"
                        "  ...\n"
                        "}"
                    )
                },
                {
                    "pattern-not-inside": (
                        f"if (static_cast<bool>({ptr})) {{\n"
                        "  ...\n"
                        f"  {use}\n"
                        "  ...\n"
                        "}"
                    )
                },
            ]
        )
    return constraints


def _allocator_context_from_patterns(patterns: list[str], ptr: str) -> str:
    if not ptr:
        return ""
    ptr_re = re.escape(ptr)
    for pattern in patterns:
        text = str(pattern or "")
        match = re.search(
            rf"{ptr_re}\s*=\s*(?:\([^;\n]*\)\s*)?(?:malloc|calloc|realloc)\s*\([^;\n]*\)\s*;",
            text,
            flags=re.S,
        )
        if match:
            stmt = re.sub(r"\s+", " ", match.group(0)).strip()
            return f"{stmt}\n..."
    for pattern in patterns:
        text = str(pattern or "")
        match = re.search(
            rf"(?:malloc|calloc|realloc)\s*\([^;\n]*\)",
            text,
            flags=re.S,
        )
        if match:
            return f"... {match.group(0).strip()} ...\n..."
    return ""


def _reshape_allocator_use_branch_to_use_span(branch: dict[str, Any]) -> bool:
    positives = _positive_pattern_strings(branch)
    if not positives:
        return False
    if not any(_allocator_names_from_pattern(pattern) for pattern in positives):
        return False
    if not any(_use_shapes_from_pattern(pattern) for pattern in positives):
        return False
    ptr = _pointer_metavariable_from_use_patterns(positives)
    if not ptr:
        return False
    use_patterns = _use_statements_for_pointer(positives, ptr)
    if not use_patterns:
        return False
    allocator_context = _allocator_context_from_patterns(positives, ptr)
    if not allocator_context:
        return False

    constraints = []
    existing_patterns = branch.get("patterns") if isinstance(branch.get("patterns"), list) else []
    for item in existing_patterns:
        if not isinstance(item, dict):
            continue
        if "pattern-not-inside" in item or "pattern-not" in item or "metavariable-" in " ".join(item.keys()):
            constraints.append(copy.deepcopy(item))
    branch.pop("pattern", None)
    branch["patterns"] = [{"pattern-inside": allocator_context}, {"pattern": use_patterns[0]}, *constraints]
    return True


def _append_malloc_guard_exclusions_to_siblings(root: Any, target: dict[str, Any]) -> bool:
    return _append_malloc_guard_exclusions_to_siblings_with_options(root, target, reshape_span=True)


def _append_malloc_guard_exclusions_to_siblings_with_options(
    root: Any,
    target: dict[str, Any],
    *,
    reshape_span: bool,
) -> bool:
    parent = _localized_parent_pattern_either(root, target)
    branches = [branch for branch in parent if isinstance(branch, dict)] if isinstance(parent, list) else []
    if not branches:
        branch = _localized_branch_node(root, target)
        branches = [branch] if isinstance(branch, dict) else []
    changed = False
    for branch in branches:
        if reshape_span and _reshape_allocator_use_branch_to_use_span(branch):
            changed = True
        for constraint in _malloc_guard_exclusions_for_branch(branch):
            changed = _append_unique_constraint_to_branch(branch, constraint) or changed
    return changed


def _safe_replacement_allowed(action: str, target: dict[str, Any], analysis: dict[str, Any]) -> bool:
    if action != "replace_overbroad_trigger_with_bad_context":
        return True
    if _target_prefers_good_exclusion(target):
        return False
    if "precision_overcut_bad" in _recent_precision_failure_classes(analysis):
        return False
    return _contrast_has_stable_bad_context(analysis)


def _inside_constraint_allowed_for_precision(action: str, analysis: dict[str, Any]) -> bool:
    if action != "add_pattern_inside":
        return True
    if "precision_overcut_bad" in _recent_precision_failure_classes(analysis):
        return False
    return _contrast_has_stable_bad_context(analysis)


def _action_is_constraint_like(action: str) -> bool:
    return action in {
        "add_branch_local_pattern_not",
        "add_pattern_inside",
        "add_pattern_not_inside",
        "add_metavariable_constraint",
        "add_taint_sanitizer_or_scope_guard",
    }


def apply_template_patch_from_payload(
    base_rule_yaml: str,
    payload: dict[str, Any],
    analysis: dict[str, Any],
) -> str:
    """Best-effort deterministic local patching inspired by RuleRefiner templates."""
    contract = analysis.get("repair_edit_contract") if isinstance(analysis.get("repair_edit_contract"), dict) else {}
    action = str(payload.get("edit_action") or "").strip()
    if not action:
        return ""
    fragment = _payload_patch_fragment(payload)
    if fragment is None:
        return ""
    try:
        base = yaml.safe_load(base_rule_yaml)
    except Exception:
        return ""
    rule = _first_rule_node(base)
    if rule is None:
        return ""

    changed = False
    target = _localized_target_from_analysis(analysis)
    if action in {"add_sibling_branch_to_pattern_either", "add_taint_source_sink_or_propagator"}:
        branch = _as_branch_item(fragment)
        if branch:
            changed = _insert_branch_near_localized_target(base, target, branch)
    elif action == "remove_good_only_positive_branch":
        changed = _remove_localized_branch(base, target)
    elif action in {"weaken_overblocking_exclusion", "generalize_local_positive_predicate"}:
        constraint = _as_constraint_item(fragment)
        branch = _as_branch_item(fragment)
        if branch and action == "generalize_local_positive_predicate":
            changed = _replace_localized_branch(base, target, branch) or _insert_branch_near_localized_target(base, target, branch)
        elif constraint:
            changed = _append_constraint_to_localized_target(base, target, constraint)
    elif action in {
        "replace_overbroad_trigger_with_bad_context",
        "add_branch_local_pattern_not",
        "add_pattern_inside",
        "add_pattern_not_inside",
        "add_metavariable_constraint",
        "add_taint_sanitizer_or_scope_guard",
    }:
        branch = _as_branch_item(fragment)
        constraint = _as_constraint_item(fragment)
        if branch and action == "replace_overbroad_trigger_with_bad_context":
            if _safe_replacement_allowed(action, target, analysis):
                changed = _replace_localized_branch(base, target, branch)
            else:
                branch_constraint = _branch_item_single_constraint(branch)
                if branch_constraint:
                    changed = _append_constraint_to_localized_target(base, target, branch_constraint)
                else:
                    extracted = _constraint_from_branch_for_action(branch, action)
                    if extracted:
                        changed = _append_constraint_to_localized_target(base, target, extracted)
            if not changed and _has_contrast_feature(analysis, "release_then_null_reset_same_pointer", "flagged_good_only_features"):
                changed = _append_release_reset_constraints_to_release_siblings(base, target)
        elif branch and action in {
            "add_branch_local_pattern_not",
            "add_pattern_inside",
            "add_pattern_not_inside",
            "add_metavariable_constraint",
            "add_taint_sanitizer_or_scope_guard",
        }:
            extracted = _constraint_from_branch_for_action(branch, action)
            if extracted and _inside_constraint_allowed_for_precision(action, analysis):
                changed = _append_constraint_to_localized_target(base, target, extracted)
        elif constraint:
            if _inside_constraint_allowed_for_precision(action, analysis):
                changed = _append_constraint_to_localized_target(base, target, constraint)
        if not changed and action in {"add_pattern_not_inside", "add_branch_local_pattern_not", "replace_overbroad_trigger_with_bad_context"}:
            if _has_contrast_feature(analysis, "release_then_null_reset_same_pointer", "flagged_good_only_features"):
                changed = _append_release_reset_constraints_to_release_siblings(base, target)
        if _action_is_constraint_like(action) or action == "replace_overbroad_trigger_with_bad_context":
            if _has_contrast_feature(analysis, "explicit_integer_cast", "flagged_good_only_features"):
                changed = _append_explicit_cast_exclusions_to_conversion_siblings(base, target) or changed
            if _has_contrast_feature(analysis, "guard_shapes=", "flagged_good_only_features"):
                changed = _append_malloc_guard_exclusions_to_siblings_with_options(
                    base,
                    target,
                    reshape_span="precision_overcut_bad" not in _recent_precision_failure_classes(analysis),
                ) or changed
        if action in {"add_pattern_not_inside", "add_branch_local_pattern_not", "replace_overbroad_trigger_with_bad_context"}:
            if _has_contrast_feature(analysis, "has_final_else_block", "flagged_good_only_features"):
                changed = _append_final_else_exclusions_to_control_flow_siblings(base, target) or changed
    if not changed:
        return ""

    rendered = yaml.safe_dump(base, allow_unicode=True, sort_keys=False)
    if _repair_candidate_is_semantic_noop(base_rule_yaml, rendered):
        return ""
    return normalize_yaml(rendered)


def _diagnose_rule_shape(rule_yaml: str, prev_eval: dict[str, Any]) -> list[str]:
    text = str(rule_yaml or "")
    lowered = text.lower()
    diagnostics: list[str] = []
    bad_total = int(prev_eval.get("bad_total", 0) or 0)
    good_total = int(prev_eval.get("good_total", 0) or 0)
    bad_hit = int(prev_eval.get("bad_hit", 0) or 0)
    good_hit = int(prev_eval.get("good_hit", 0) or 0)
    if good_total > 0 and good_hit >= good_total:
        diagnostics.append("all_good_flagged: current rule matches every GOOD example; precision repair must replace/constrain the shared trigger, not only add weak exclusions")
    if bad_total > 0 and (bad_hit / bad_total) <= 0.2:
        diagnostics.append("very_low_bad_recall: current rule is too narrow; coverage repair needs sibling branches for missed BAD carrier shapes")

    if re.search(r"\$(INT|FLOAT|DOUBLE|PTR|TYPE|GLOBAL|LOCAL)\b", text):
        diagnostics.append("pseudo_metavariable_semantics: metavariable names such as $INT/$FLOAT/$TYPE/$GLOBAL/$LOCAL do not impose C/C++ type or scope semantics")
    if re.search(r"pattern:\s*[\"']?\$[A-Z0-9_]+\s*[-+]\s*\$[A-Z0-9_]+", text):
        diagnostics.append("bare_operator_trigger: a shared arithmetic/operator expression is likely overbroad without BAD-only operand/context evidence")
    if re.search(r"pattern:\s*[\"']?\$[A-Z0-9_]+\s*=\s*\$[A-Z0-9_]+;?", text):
        diagnostics.append("all_metavariable_assignment: assignment-only trigger is likely overbroad unless another branch-local predicate supplies concrete BAD context")
    if "pattern-regex" in lowered:
        diagnostics.append("regex_present: regex must stay local to a BAD signal line and should not be the primary way to model dataflow, type, or scope relations")
    if "pattern-not:" in lowered and re.search(r"pattern-not:\s*[\"']?\$[A-Z0-9_]+\s*=", text):
        diagnostics.append("possible_weak_pattern_not: pattern-not with broad metavariable assignment may not express the safe subset intended")
    if (
        re.search(r"\b(?:malloc|calloc|realloc)\s*\(", lowered)
        and re.search(r"\.\.\.", text)
        and ("pattern-not-inside" in lowered or "pattern-not:" in lowered)
        and re.search(r"\*\s*\$[A-Z0-9_]+|\$[A-Z0-9_]+\s*\[", text)
    ):
        diagnostics.append(
            "allocation_to_use_span_guard_risk: if the positive pattern spans allocation through use, guard exclusions around only the use statement may not overlap; focus the finding on the dereference/subscript use and move allocation to pattern-inside context"
        )
    if _looks_like_dataflow_requirement(prev_eval) and "mode: taint" not in lowered:
        diagnostics.append("dataflow_without_taint: requirement/evidence looks like source-to-sink flow; repair should consider converting the rule to taint mode")
    return diagnostics[:12]


def _looks_like_dataflow_requirement(prev_eval: dict[str, Any]) -> bool:
    chunks: list[str] = []
    for key in ("requirement_text", "description", "cwe_dir"):
        value = prev_eval.get(key)
        if isinstance(value, str):
            chunks.append(value)
    for key in ("missed_bad_examples", "flagged_good_examples", "counterexample_pairs"):
        value = prev_eval.get(key)
        if isinstance(value, (list, dict)):
                chunks.append(json.dumps(value, ensure_ascii=False)[:6000])
    text = "\n".join(chunks).lower()
    req_chunks: list[str] = []
    for key in ("requirement_text", "description", "cwe_dir"):
        value = prev_eval.get(key)
        if isinstance(value, str):
            req_chunks.append(value)
    req_text = "\n".join(req_chunks).lower()
    normalized_req_text = req_text.replace("_", " ").replace("-", " ")
    if any(token in normalized_req_text for token in STRUCTURAL_REQUIREMENT_TOKENS):
        return False
    if "untrusted" in req_text and any(token in text for token in FLOW_SINK_TOKENS):
        return True
    if "source-to-sink" in req_text and any(token in text for token in FLOW_SOURCE_TOKENS) and any(token in text for token in FLOW_SINK_TOKENS):
        return True
    return any(token in text for token in FLOW_SOURCE_TOKENS) and any(token in text for token in FLOW_SINK_TOKENS)


def build_repair_analysis(config: RepairModeConfig) -> dict[str, Any]:
    records = _all_region_records(config.truth_by_file)
    state_sets = _case_state_sets(config.prev_eval, config.truth_by_file)
    current_rule_text = config.current_rule_yaml.read_text(encoding="utf-8", errors="replace")
    rule_index = _rule_predicate_index(current_rule_text)

    def _take(state: str, limit: int) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for key in sorted(state_sets.get(state, set()), key=lambda item: (item[0], item[2], item[1])):
            record = _record_for_key(records, key)
            if record is not None:
                selected.append(record)
            if len(selected) >= max(1, int(limit)):
                break
        return selected

    cases = {
        "missed_bad": _take("missed_bad", config.max_error_examples),
        "flagged_good": _take("flagged_good", config.max_error_examples),
        "hit_bad_reference": _take("hit_bad", config.max_reference_examples),
        "clean_good_reference": _take("clean_good", config.max_reference_examples),
    }
    wanted_paths = {
        str(Path(item["path"]).resolve())
        for group in cases.values()
        for item in group
        if isinstance(item, dict) and item.get("path")
    }

    explanation_by_path: dict[str, dict[str, Any]] = {}
    path_summaries: dict[str, dict[str, Any]] = {}
    aligned_paths_by_path: dict[str, list[list[dict[str, Any]]]] = {}
    predicate_truth_by_state: dict[str, dict[str, dict[str, int | str]]] = {}

    state_by_path: dict[str, set[str]] = {}
    for state, group in cases.items():
        for item in group:
            state_by_path.setdefault(str(Path(item["path"]).resolve()), set()).add(state)

    for path_raw in sorted(wanted_paths):
        path = Path(path_raw)
        payload = run_semgrep_explanation(
            semgrep_bin=config.semgrep_bin,
            rule_yaml=config.current_rule_yaml,
            target=path,
            timeout_seconds=max(1.0, float(config.scan_timeout_seconds)),
        )
        explanation_by_path[path_raw] = payload
        explanations = payload.get("explanations") if isinstance(payload.get("explanations"), list) else []
        if explanations and isinstance(explanations[0], dict):
            paths = aligned_explanation_predicate_paths(explanations[0], rule_index)
        else:
            paths = []
        aligned_paths_by_path[path_raw] = paths
        path_summaries[path_raw] = _summarize_paths(paths)
        for state in state_by_path.get(path_raw, set()):
            target = predicate_truth_by_state.setdefault(state, {})
            for pred_path in paths:
                for node in pred_path:
                    key = str(node.get("key") or "")
                    if not key:
                        continue
                    rec = target.setdefault(
                        key,
                        {
                            "label": str(node.get("label") or ""),
                            "true": 0,
                            "false": 0,
                        },
                    )
                    truth_key = "true" if bool(node.get("truth")) else "false"
                    rec[truth_key] = int(rec.get(truth_key, 0) or 0) + 1

    too_narrow: list[dict[str, Any]] = []
    missed_pred = predicate_truth_by_state.get("missed_bad", {})
    hit_pred = predicate_truth_by_state.get("hit_bad_reference", {})
    for key, missed in missed_pred.items():
        hit = hit_pred.get(key, {})
        if int(missed.get("false", 0) or 0) <= 0:
            continue
        if hit_pred and int(hit.get("true", 0) or 0) <= 0:
            continue
        too_narrow.append(
            {
                "predicate": str(missed.get("label") or key),
                "missed_bad_false": int(missed.get("false", 0) or 0),
                "hit_bad_true": int(hit.get("true", 0) or 0),
            }
        )
    too_narrow = sorted(too_narrow, key=lambda item: (-int(item["missed_bad_false"]), str(item["predicate"])))[:12]

    overbroad: list[dict[str, Any]] = []
    flagged_pred = predicate_truth_by_state.get("flagged_good", {})
    clean_pred = predicate_truth_by_state.get("clean_good_reference", {})
    for key, flagged in flagged_pred.items():
        if int(flagged.get("true", 0) or 0) <= 0:
            continue
        clean = clean_pred.get(key, {})
        hit = hit_pred.get(key, {})
        overbroad.append(
            {
                "predicate": str(flagged.get("label") or key),
                "flagged_good_true": int(flagged.get("true", 0) or 0),
                "hit_bad_true": int(hit.get("true", 0) or 0),
                "clean_good_true": int(clean.get("true", 0) or 0),
            }
        )
    overbroad = sorted(
        overbroad,
        key=lambda item: (
            -int(item["flagged_good_true"]),
            -int(item["hit_bad_true"]),
            int(item["clean_good_true"]),
            str(item["predicate"]),
        ),
    )[:12]

    predicate_scores = _predicate_discriminative_scores(predicate_truth_by_state)
    rule_refiner_alignment = _attach_paired_counterparts(_rule_refiner_path_alignments(aligned_paths_by_path, cases), records)
    rule_refiner_alignment = _filter_alignments_by_discriminative_scores(rule_refiner_alignment, predicate_scores)
    carrier_catalog = _carrier_shape_catalog(cases.get("missed_bad", []), limit_records=config.max_error_examples)
    branch_contrast = _branch_local_contrast(
        flagged_good=cases.get("flagged_good", []),
        hit_bad=cases.get("hit_bad_reference", []),
    )
    analysis = {
        "mode": "semgrep_explanation_predicate_graph_repair",
        "current_rule_yaml": str(config.current_rule_yaml.resolve()),
        "recent_rejected_repairs": list(config.rejected_repairs or [])[-6:],
        "previous_metrics": {
            "bad_hit": config.prev_eval.get("bad_hit"),
            "bad_total": config.prev_eval.get("bad_total"),
            "bad_recall": config.prev_eval.get("bad_recall"),
            "good_hit": config.prev_eval.get("good_hit"),
            "good_total": config.prev_eval.get("good_total"),
            "good_false_positive_rate": config.prev_eval.get("good_false_positive_rate"),
            "semgrep_findings_total": config.prev_eval.get("semgrep_findings_total"),
        },
        "repair_stage": _repair_stage_summary(config.prev_eval),
        "case_counts": {state: len(group) for state, group in cases.items()},
        "rule_predicate_index": [
            {
                "id": item.get("id"),
                "yaml_key": item.get("yaml_key"),
                "yaml_path": item.get("yaml_path"),
                "summary": item.get("summary"),
            }
            for item in rule_index.get("predicates", [])[:80]
        ],
        "rule_pattern_inventory": _extract_rule_patterns(current_rule_text),
        "rule_shape_diagnostics": _diagnose_rule_shape(current_rule_text, config.prev_eval),
        "rule_refiner_path_alignment": rule_refiner_alignment,
        "predicate_discriminative_scores": predicate_scores,
        "missed_bad_carrier_shape_catalog": carrier_catalog,
        "branch_local_contrast": branch_contrast,
        "localized_too_narrow_predicates": too_narrow,
        "localized_overbroad_predicates": overbroad,
        "cases": cases,
        "path_summaries": path_summaries,
        "semgrep_hard_note": (
            "Do not chase examples whose distinction needs cross-function flow, deep alias/type reasoning, "
            "cross-scope symbol resolution, or proof that a later statement is absent. Keep those partial."
        ),
    }
    focus = str(config.forced_focus or "").strip() or choose_repair_focus(config.prev_eval, analysis)
    analysis["suggested_focus"] = focus
    analysis["repair_gate"] = _repair_gate(analysis, focus)
    analysis["repair_action_plan"] = _repair_action_plan(config.prev_eval, analysis, focus)
    analysis["repair_edit_contract"] = build_repair_edit_contract(current_rule_text, analysis, focus)
    return analysis


def choose_repair_focus(prev_eval: dict[str, Any], analysis: dict[str, Any]) -> str:
    missed = int(prev_eval.get("missed_bad_count", 0) or 0)
    flagged = int(prev_eval.get("flagged_good_count", 0) or 0)
    if missed > 0:
        return "too_narrow_coverage"
    if flagged > 0:
        return "too_broad_precision"
    return "mixed_balance"


def _render_case_group(title: str, cases: list[dict[str, Any]], limit: int = 4) -> list[str]:
    lines: list[str] = [title]
    for idx, item in enumerate(cases[: max(1, int(limit))], start=1):
        lines.append(
            "{}. {} {}:{}-{} label={}".format(
                idx,
                item.get("function") or "(unknown)",
                item.get("path"),
                item.get("start_line"),
                item.get("end_line"),
                item.get("label"),
            )
        )
        excerpt = _read_excerpt(
            path_raw=str(item.get("path") or ""),
            start_line=int(item.get("start_line", 0) or 0),
            end_line=int(item.get("end_line", 0) or 0),
            max_lines=16,
            max_chars=760,
        )
        if excerpt:
            lines.append(excerpt)
    return lines


def _render_predicates(title: str, items: list[dict[str, Any]], limit: int = 10) -> list[str]:
    lines = [title]
    if not items:
        lines.append("- none localized; rely on BAD/GOOD code contrast and current rule inventory")
        return lines
    for item in items[: max(1, int(limit))]:
        parts = [str(item.get("predicate") or "")]
        for key, value in item.items():
            if key == "predicate":
                continue
            parts.append(f"{key}={value}")
        lines.append("- " + "; ".join(parts))
    return lines


def _render_alignment_items(title: str, items: list[dict[str, Any]], limit: int = 6) -> list[str]:
    lines = [title]
    if not items:
        lines.append("- none localized by path alignment")
        return lines
    for item in items[: max(1, int(limit))]:
        yaml_pred = item.get("yaml_predicate") if isinstance(item.get("yaml_predicate"), dict) else {}
        yaml_summary = str(yaml_pred.get("summary") or "")
        if not yaml_summary:
            yaml_summary = "(no YAML predicate mapping)"
        lines.append(
            "- priority={}; kind={}; faulty_truth={}; reference_truth={}; predicate={}; yaml={}".format(
                item.get("priority"),
                item.get("first_difference_kind"),
                item.get("faulty_truth"),
                item.get("reference_truth"),
                _short(item.get("predicate") or "", 220),
                _short(yaml_summary, 260),
            )
        )
        faulty = str(item.get("faulty_case") or "")
        reference = str(item.get("reference_case") or "")
        if faulty or reference:
            lines.append(f"  faulty={_short(faulty, 240)}")
            lines.append(f"  reference={_short(reference, 240)}")
    return lines


def _render_local_profiles(title: str, profiles: list[dict[str, Any]], limit: int = 3) -> list[str]:
    lines = [title]
    if not profiles:
        lines.append("- none")
        return lines
    keys = (
        "calls",
        "operators",
        "carriers",
        "argument_positions",
        "provenance_relations",
        "control_flow_shapes",
        "conversion_shapes",
        "lifetime_shapes",
        "guard_shapes",
        "scope_symbol_relations",
    )
    for profile in profiles[: max(1, int(limit))]:
        if not isinstance(profile, dict):
            continue
        parts = [f"case={_short(profile.get('case') or '', 180)}"]
        for key in keys:
            value = profile.get(key)
            if isinstance(value, list) and value:
                parts.append(f"{key}={_short(value, 220)}")
        for key in ("has_guard_or_check", "has_reset_or_safe_api", "has_constant"):
            if profile.get(key):
                parts.append(f"{key}=true")
        lines.append("- " + "; ".join(parts))
    return lines


def _load_reference_doc(limit: int = 3600) -> str:
    if not REFERENCE_SKILL_DOC.is_file():
        return ""
    try:
        return guardian.shorten(REFERENCE_SKILL_DOC.read_text(encoding="utf-8", errors="replace"), limit=limit)
    except OSError:
        return ""


def _render_rule_refiner_localization_block(analysis: dict[str, Any], focus: str) -> list[str]:
    """Render localization context in the same spirit as RuleRefiner prompts."""
    inventory = analysis.get("rule_pattern_inventory")
    diagnostics = analysis.get("rule_shape_diagnostics")
    action_plan = analysis.get("repair_action_plan")
    repair_stage = analysis.get("repair_stage") if isinstance(analysis.get("repair_stage"), dict) else {}
    repair_gate = analysis.get("repair_gate") if isinstance(analysis.get("repair_gate"), dict) else {}
    carrier_catalog = analysis.get("missed_bad_carrier_shape_catalog")
    predicate_scores = analysis.get("predicate_discriminative_scores") if isinstance(analysis.get("predicate_discriminative_scores"), dict) else {}
    branch_contrast = analysis.get("branch_local_contrast") if isinstance(analysis.get("branch_local_contrast"), dict) else {}
    too_narrow = analysis.get("localized_too_narrow_predicates")
    overbroad = analysis.get("localized_overbroad_predicates")
    alignment = analysis.get("rule_refiner_path_alignment") if isinstance(analysis.get("rule_refiner_path_alignment"), dict) else {}
    if not isinstance(inventory, list):
        inventory = []
    if not isinstance(diagnostics, list):
        diagnostics = []
    if not isinstance(action_plan, list):
        action_plan = []
    if not isinstance(carrier_catalog, list):
        carrier_catalog = []
    if not isinstance(too_narrow, list):
        too_narrow = []
    if not isinstance(overbroad, list):
        overbroad = []
    coverage_alignments = alignment.get("coverage_alignments") if isinstance(alignment, dict) else []
    precision_alignments = alignment.get("precision_alignments") if isinstance(alignment, dict) else []
    if not isinstance(coverage_alignments, list):
        coverage_alignments = []
    if not isinstance(precision_alignments, list):
        precision_alignments = []

    lines = [
        "RuleRefiner-style localization context:",
        "- Treat Semgrep explanation predicates as a predicate graph: true predicates are satisfied on a case; false predicates blocked that case.",
        "- Use path alignment first: compare a faulty path with a correctly handled reference path, then edit the first localized YAML predicate/branch that differs.",
        "- If alignment and frequency disagree, trust the aligned YAML predicate when it maps to a concrete current rule pattern.",
        "- Localize the edit to the suspicious predicate/branch; avoid whole-rule rewrites.",
        "",
        "Repair stage:",
        "- stage={}; bad_recall={}".format(
            repair_stage.get("stage") or "",
            repair_stage.get("bad_recall") or "",
        ),
        "- If any BAD examples are still missed, repair only BAD coverage first.",
        "- Once BAD coverage has no misses, preserve BAD hits and reduce GOOD false positives.",
        "",
        "Current rule pattern inventory:",
    ]
    if inventory:
        for item in inventory[:24]:
            lines.append(f"- {item}")
    else:
        lines.append("- no extractable inventory; rely on current YAML and examples")

    lines.extend(["", "Rule shape diagnostics:"])
    if diagnostics:
        for item in diagnostics[:10]:
            lines.append(f"- {item}")
    else:
        lines.append("- no obvious shape diagnostic; use predicate graph and case contrast")

    lines.extend(["", "RuleRefiner repair action plan:"])
    if action_plan:
        for item in action_plan[:8]:
            lines.append(f"- {item}")
    else:
        lines.append("- no action plan inferred; use localized predicate/path contrast")

    lines.extend(["", "Repair evidence gate:"])
    if repair_gate:
        lines.append(
            "- should_repair={}; reason={}".format(
                repair_gate.get("should_repair"),
                _short(repair_gate.get("reason") or "", 420),
            )
        )
    else:
        lines.append("- no gate result recorded")

    if focus in {"too_narrow_coverage", "mixed_balance", "missed_bad", "balanced_local_repair"}:
        lines.extend(["", "Missed BAD carrier shape catalog:"])
        if carrier_catalog:
            for item in carrier_catalog[:8]:
                lines.append(
                    "- shape={}; count={}; priority={}".format(
                        item.get("shape"),
                        item.get("count"),
                        item.get("priority", ""),
                    )
                )
                examples = item.get("examples") if isinstance(item.get("examples"), list) else []
                for example in examples[:2]:
                    if isinstance(example, dict):
                        lines.append("  evidence={}".format(_short(example.get("evidence") or "", 240)))
        else:
            lines.append("- none extracted")
        coverage_scores = predicate_scores.get("coverage") if isinstance(predicate_scores.get("coverage"), list) else []
        lines.extend(["", "Discriminative predicates for coverage:"])
        if coverage_scores:
            for item in coverage_scores[:8]:
                lines.append(
                    "- score={}; predicate={}; missed_bad_true_rate={}; hit_bad_true_rate={}".format(
                        item.get("score"),
                        _short(item.get("predicate") or "", 220),
                        item.get("missed_bad_true_rate"),
                        item.get("hit_bad_true_rate"),
                    )
                )
        else:
            lines.append("- none")
        lines.extend([""])
        lines.extend(_render_alignment_items("RuleRefiner path-alignment suspects for missed BAD:", coverage_alignments))
        lines.extend(["", "Faulty/too-narrow predicates for missed BAD:"])
        if too_narrow:
            for item in too_narrow[:8]:
                lines.append(
                    "- predicate={}; missed_bad_false={}; hit_bad_true={}".format(
                        item.get("predicate"),
                        item.get("missed_bad_false"),
                        item.get("hit_bad_true"),
                    )
                )
        else:
            lines.append("- none localized; infer from missed BAD vs hit BAD code contrast")

    if focus in {"too_broad_precision", "mixed_balance", "flagged_good", "balanced_local_repair"}:
        precision_scores = predicate_scores.get("precision") if isinstance(predicate_scores.get("precision"), list) else []
        lines.extend(["", "Discriminative predicates for precision:"])
        if precision_scores:
            for item in precision_scores[:8]:
                lines.append(
                    "- score={}; preferred_use={}; predicate={}; flagged_good_true_rate={}; hit_bad_true_rate={}".format(
                        item.get("score"),
                        item.get("preferred_use"),
                        _short(item.get("predicate") or "", 220),
                        item.get("flagged_good_true_rate"),
                        item.get("hit_bad_true_rate"),
                    )
                )
        else:
            lines.append("- none")
        lines.extend(["", "Branch-local GOOD/BAD contrast:"])
        lines.append("- Use BAD-only candidates as positive context that should keep current BAD hits.")
        lines.append("- Use GOOD-only candidates as branch-local exclusions/sanitizers only when they overlap the overbroad branch.")
        lines.append("- Treat shared features as weak triggers to constrain, not as sufficient evidence by themselves.")
        for key, title in (
            ("hit_bad_only_features", "BAD-only positive context candidates"),
            ("flagged_good_only_features", "GOOD-only exclusion candidates"),
            ("shared_features", "Shared weak triggers"),
        ):
            lines.append(f"- {title}:")
            values = branch_contrast.get(key) if isinstance(branch_contrast.get(key), list) else []
            if values:
                for item in values[:6]:
                    if isinstance(item, dict):
                        lines.append("  - {}".format(_short(item.get("feature") or "", 220)))
            else:
                lines.append("  - none")
        flagged_profiles = branch_contrast.get("flagged_good_profiles") if isinstance(branch_contrast.get("flagged_good_profiles"), list) else []
        hit_bad_profiles = branch_contrast.get("hit_bad_profiles") if isinstance(branch_contrast.get("hit_bad_profiles"), list) else []
        lines.extend(["", "High-signal local profiles for precision:"])
        lines.extend(_render_local_profiles("Flagged GOOD local profiles:", flagged_profiles, limit=3))
        lines.extend(_render_local_profiles("Hit BAD local profiles to preserve:", hit_bad_profiles, limit=3))
        lines.extend([""])
        lines.extend(_render_alignment_items("RuleRefiner path-alignment suspects for flagged GOOD:", precision_alignments))
        lines.extend(["", "Faulty/overbroad predicates for flagged GOOD:"])
        if overbroad:
            for item in overbroad[:8]:
                lines.append(
                    "- predicate={}; flagged_good_true={}; hit_bad_true={}; clean_good_true={}".format(
                        item.get("predicate"),
                        item.get("flagged_good_true"),
                        item.get("hit_bad_true"),
                        item.get("clean_good_true"),
                    )
                )
        else:
            lines.append("- none localized; infer from flagged GOOD vs clean GOOD/BAD code contrast")
    return lines


def _render_rule_refiner_fix_hint(focus: str) -> list[str]:
    common = [
        "Local repair workflow:",
        "1. In notes, briefly state the root cause: too narrow, overbroad, wrong mode, invalid Semgrep shape, or Semgrep-hard.",
        "2. Name the localized predicate/branch being edited.",
        "3. Apply the smallest YAML change that fixes the focused misclassification.",
        "4. Check regression mentally against hit BAD and clean GOOD references before returning.",
        "",
    ]
    if focus in {"too_narrow_coverage", "missed_bad"}:
        return common + [
            "TOO NARROW / COVERAGE repair prompt:",
            "- Diagnosis: the rule is too narrow when BAD recall is low and GOOD false positives are already low.",
            "- Primary objective: increase BAD hits; GOOD false positives are a regression guard, not the main objective before the BAD floor is reached.",
            "- Coverage repair is accepted when BAD hits increase; GOOD false positives are recorded for the later precision stage.",
            "- Prefer adding a sibling branch with `pattern-either` or adding one evidence-backed carrier/API/operator/type shape to the localized branch.",
            "- Do not combine independent missed-BAD carrier alternatives in one `patterns:` list; `patterns:` is AND, so alternative carriers must be separate rule-level `pattern-either` siblings.",
            "- The new branch must be based on one carrier shape from the missed BAD carrier catalog, not only on a guessed predicate name.",
            "- The carrier catalog is priority-ordered; choose the highest-priority executable BAD write/use carrier before low-signal output calls, helper calls, ordinary declarations, or generic expressions.",
            "- If no YAML-aligned predicate exists, add exactly one evidence-backed sibling branch from missed BAD carrier evidence and keep existing working branches unchanged.",
            "- Keep the old working branch unchanged when it already hits BAD.",
            "- Read missed BAD excerpts first and extract concrete carrier shapes: declaration initializer, reassignment, call argument, return expression, array subscript read/write, pointer arithmetic read/write, pointer dereference, compound assignment, casted expression, or side-effect source/sink.",
            "- For pointer-scaling, cast, or parser-fragile carriers, instantiate concrete type tokens from the missed BAD evidence directly; do not collapse them into a generic $TYPE/$CAST placeholder if the concrete token list is already available.",
            "- Never repair a C/C++ `sizeof(...)` carrier with a bare type metavariable such as `sizeof($T)`; use concrete type tokens, `sizeof(*$PTR)`, or a short full-carrier regex.",
            "- For dataflow missed BAD, prefer adding taint sources/sinks/propagators/sanitizers instead of search-mode source/sink conjunctions.",
            "- Add only carrier/API/operator/type variants that appear in missed BAD or are direct semantic siblings of already-hit BAD.",
            "- If a predicate is too specific, generalize only that predicate; do not replace semantic APIs/operators with `$FUNC(...)`/`$SINK(...)` placeholders.",
            "- If GOOD shares the same surface, include the BAD-only context in the new sibling branch immediately.",
            "- Do not remove existing precision guards just to raise BAD recall.",
            "- If a missed BAD needs cross-function flow, deep alias/type reasoning, cross-scope symbol comparison, or proof of absent later statements, mark it partial in notes and do not broaden.",
            "",
        ]
    if focus in {"too_broad_precision", "flagged_good"}:
        return common + [
            "TOO BROAD / PRECISION repair prompt:",
            "- Diagnosis: the rule is too broad when it matches many GOOD examples, especially when BAD and GOOD share the same API/operator/syntax surface.",
            "- Primary objective: reduce GOOD false positives while preserving BAD hits; do not chase new missed BAD in this repair.",
            "- A precision repair is accepted only if GOOD false positives decrease and BAD hit count does not decrease.",
            "- Choose one precision strategy: safe exclusion, taint sanitizer/scope guard, or BAD-only positive context. Do not mix broad rewrites with exclusions.",
            "- Use safe exclusion when the localized predicate is shared by GOOD and BAD and the discriminative score says `branch_local_good_exclusion`.",
            "- Use taint sanitizer/scope guard for taint-mode rules; do not add `pattern-not-inside` inside `pattern-sources` unless it overlaps the source finding span.",
            "- Use BAD-only positive context only when hit BAD references repeatedly show that context; otherwise it will overcut BAD.",
            "- If GOOD false positives are very high, still preserve all current BAD hits; do not trade BAD recall for precision.",
            "- A 100% BAD / near-100% GOOD-FP rule is not a useful final precision state, but the fix must remove shared GOOD matches without losing current BAD hits.",
            "- First identify the overbroad shared trigger. If the trigger is only a shared API/operator/type-looking metavariable, replace or constrain that branch; exclusions alone are usually not enough.",
            "- If predicate profiling shows a positive branch fires on flagged GOOD and essentially never on hit BAD, remove that branch instead of adding weak exclusions around other branches.",
            "- If the evidence gate says there is no YAML-aligned predicate, do not replace the whole rule or main trigger. Add only a conservative branch-local guard/exclusion backed by GOOD/BAD contrast.",
            "- Use branch-local contrast in this order: hit_bad_only_features as required positive context, flagged_good_only_features as safe exclusions, shared_features only as the trigger being constrained.",
            "- If the previous failure class is precision_no_fp_delta, replacement_not_discriminative, or exclusion_not_overlapping, the new patch must state why it overlaps the flagged GOOD matched statement/expression.",
            "- If the previous failure class is precision_overcut_bad, do not use `replace_overbroad_trigger_with_bad_context` or `add_pattern_inside`; use a safe exclusion/sanitizer that preserves all current BAD branches.",
            "- Do not use `add_pattern_inside` unless the BAD-only context appears repeatedly in current hit BAD and is absent from flagged GOOD; otherwise it usually overcuts BAD.",
            "- Prefer adding positive BAD-only context to the overbroad branch: sensitive argument, unsafe operand relation, unguarded use, missing local check, risky cast/use, concrete standard API, or branch-local surrounding statement.",
            "- For pointer/index/arithmetic false positives, provenance contrast is stronger than the shared operator: different local bases/containers are BAD-positive context; same-base local derivation is GOOD/safe context.",
            "- For check-before-use false positives, ensure the Semgrep finding span is the dereference/subscript use statement. Put the allocation/source as `pattern-inside` context; otherwise a guard around only the use will not overlap and `pattern-not-inside` becomes a no-op.",
            "- For control-flow false positives, a final `else` block is a strong GOOD-only exclusion for an overbroad `if/else if` chain trigger.",
            "- For final-else requirements, prefer replacing the broad chain trigger with a parseable BAD-positive branch for `else if` chains without a final `else`; if that is not parseable, keep this branch partial instead of matching all chains.",
            "- If the current rule has several sibling `else if` chain lengths, apply the final-else exclusion to each sibling branch, not only one chain-length branch.",
            "- For conversion false positives, an explicit cast on the assigned/returned expression is a strong GOOD-only exclusion; the BAD trigger should be the assignment/initializer expression itself plus a cast exclusion, not a declaration+assignment sequence.",
            "- If structural cast exclusions do not change behavior, treat the cast distinction as parser/span-sensitive. Use a small line-local `pattern-regex` only when it directly matches the assignment/return signal and does not enumerate sample names; otherwise keep the branch partial.",
            "- For lifetime/reset false positives, first bind the released pointer in the positive trigger (`free($P);` or `delete $P;`). Then exclude an ordered enclosing region that contains that same release and later `$P = NULL/nullptr/0`; do not use `free(...)` or an unbound reset variable.",
            "- For scope/name false positives, local/global name equality is the semantic target; broad global declaration matching without a same-name local or parameter relation is only a weak surface.",
            "- Do not use add_metavariable_constraint for ordinary identifier spelling; use it only when the branch-local contrast shows a real semantic separator on an already-bound metavariable.",
            "- For dataflow false positives, prefer taint sanitizers for validation/allowlist/trusted constant overwrite rather than broad `pattern-not` exclusions.",
            "- Use `pattern-not`, `pattern-inside`, `pattern-not-inside`, `metavariable-pattern`, or `metavariable-comparison` only when they express an overlapping safe subset.",
            "- Prefer positive BAD-only context when GOOD shares the same API/operator and a negative exclusion would need fresh metavariables.",
            "- In regression_expectation, explicitly state that BAD hit count is expected to stay unchanged or increase, and why the GOOD finding span should stop matching.",
            "- Keep restrictions local to the offending branch; do not add global exclusions that suppress valid BAD branches.",
            "- Every `pattern-not` must be a narrower overlapping safe subset with bound metavariables or concrete syntax.",
            "- Do not rely on metavariable names such as `$INT`, `$FLOAT`, `$PTR`, `$TYPE`, `$GLOBAL`, or `$LOCAL` to mean types or scopes.",
            "- If precision requires pointer provenance, exact C/C++ type category, or global/local symbol equality beyond local syntax, keep a high-confidence subset and say partial in notes.",
            "",
        ]
    return common + [
        "MIXED repair prompt:",
        "- First preserve useful BAD coverage.",
        "- Add missed BAD sibling branches only when the local contrast is clear.",
        "- Add GOOD guards only to predicates that the localization marks overbroad.",
        "- If the two goals conflict, choose the smaller change that improves total correctness without obvious BAD regression.",
        "",
    ]


def _render_repair_edit_contract(contract: dict[str, Any]) -> list[str]:
    lines = ["Constrained local edit contract:"]
    if not isinstance(contract, dict) or not contract:
        lines.append("- No contract was produced; still make exactly one local edit from the faulty/reference contrast.")
        return lines

    target = contract.get("localized_target") if isinstance(contract.get("localized_target"), dict) else {}
    actions = contract.get("allowed_actions") if isinstance(contract.get("allowed_actions"), list) else []
    guidance = contract.get("template_action_guidance") if isinstance(contract.get("template_action_guidance"), dict) else {}
    forbidden = contract.get("forbidden_edits") if isinstance(contract.get("forbidden_edits"), list) else []
    carrier = target.get("coverage_carrier_shape") if isinstance(target.get("coverage_carrier_shape"), dict) else {}
    contrast = contract.get("branch_local_contrast") if isinstance(contract.get("branch_local_contrast"), dict) else {}

    lines.extend(
        [
            f"- objective: {contract.get('objective')}",
            f"- required_effect: {contract.get('required_effect')}",
            "- localized_target:",
            f"  source={target.get('source') or ''}",
            f"  yaml={_short(target.get('summary') or '', 360)}",
            f"  branch_prefix={_short(target.get('branch_prefix') or '', 220)}",
            f"  faulty_case={_short(target.get('faulty_case') or '', 260)}",
            f"  reference_case={_short(target.get('reference_case') or '', 260)}",
            f"  discriminative_score={_short(target.get('discriminative_score') or '', 360)}",
            "- You must choose exactly one edit_action from this list and implement only that kind of local edit:",
        ]
    )
    if carrier:
        examples = carrier.get("examples") if isinstance(carrier.get("examples"), list) else []
        lines.append(
            "  coverage_carrier_shape={} count={}".format(
                carrier.get("shape") or "",
                carrier.get("count") or "",
            )
        )
        for example in examples[:2]:
            if isinstance(example, dict):
                lines.append("  carrier_evidence={}".format(_short(example.get("evidence") or "", 280)))
    meaningful_contrast = _meaningful_contrast_features(contrast)
    if meaningful_contrast:
        lines.append("- Meaningful branch-local contrast candidates:")
        for item in meaningful_contrast[:8]:
            lines.append("  - {}".format(_short(item.get("feature") or "", 240)))
    if any("release_then_null_reset_same_pointer" in str(item.get("feature") or "") for item in meaningful_contrast):
        lines.append("- Same-pointer reset contrast: bind the release argument in the positive branch and reuse that exact metavariable in the ordered reset exclusion.")
    if any("guard_shapes=" in str(item.get("feature") or "") for item in meaningful_contrast):
        lines.append("- Guard contrast: the exclusion must cover the guarded dereference/subscript statement with the same pointer metavariable, not only the allocation statement.")
    if any("explicit_integer_cast" in str(item.get("feature") or "") for item in meaningful_contrast):
        lines.append("- Explicit-cast contrast: the safe form is the casted RHS/return expression itself; do not subtract a wider declaration+assignment region.")
    if any("has_final_else_block" in str(item.get("feature") or "") for item in meaningful_contrast):
        lines.append("- Final-else contrast: GOOD has an enclosing chain with a final `else`; the exclusion must contain the same if/else-if trigger plus final else.")
    if any("subtraction_operands_share_base" in str(item.get("feature") or "") for item in meaningful_contrast):
        lines.append("- Same-base pointer contrast: GOOD uses two pointers derived from the same array/object; BAD context must not be the bare subtraction operator alone.")
    if actions:
        for action in actions:
            lines.append(f"  - {action}: {_short(guidance.get(action) or '', 420)}")
    else:
        lines.append("  - local_refinement: make the smallest branch-local correction")

    if forbidden:
        lines.append("- Forbidden edits for this contract:")
        for item in forbidden[:8]:
            lines.append(f"  - {item}")

    lines.extend(
        [
            "- Contract discipline:",
            "  - For a coverage edit, keep existing successful branch semantics and add/adjust only the localized branch.",
            "  - For a precision edit, constrain the overbroad branch; do not add coverage branches.",
            "  - If the localized target is a `pattern-not`, first ask whether it is overblocking BAD or trying to subtract GOOD too broadly.",
            "  - If the localized target is a broad positive pattern, first ask what BAD-only context is missing.",
            "  - The repair must be behaviorally non-trivial: returning formatting-only YAML or the same effective predicates is a failed repair.",
        ]
    )
    return lines


def _render_template_patch_examples(contract: dict[str, Any]) -> list[str]:
    if not isinstance(contract, dict):
        return []
    actions = contract.get("allowed_actions") if isinstance(contract.get("allowed_actions"), list) else []
    actions = [str(item) for item in actions if str(item).strip()]
    focus = str(contract.get("focus") or "")
    lines = ["Template-local edit shapes:"]
    if focus in {"too_narrow_coverage", "missed_bad"} or "add_sibling_branch_to_pattern_either" in actions:
        lines.extend(
            [
                "- Coverage template: add a complete sibling branch, not a fragment and not a formatting-only rewrite.",
                "- If the missed carrier is an alternative to the old carrier, keep it as a separate sibling branch; do not put old and new carrier patterns in the same `patterns:` list.",
                "  Before:",
                "    pattern-either:",
                "      - patterns:",
                "          - pattern: OLD_BAD_CARRIER(...);",
                "          - pattern-not: OLD_SAFE_SUBSET(...);",
                "  After:",
                "    pattern-either:",
                "      - patterns:",
                "          - pattern: OLD_BAD_CARRIER(...);",
                "          - pattern-not: OLD_SAFE_SUBSET(...);",
                "      - patterns:",
                "          - pattern: NEW_BAD_CARRIER(...);",
                "          - pattern-inside: LOCAL_BAD_CONTEXT_IF_NEEDED",
                "- The new branch must contain the full missed BAD carrier statement/expression, such as declaration initializer, assignment, condition, call argument, dereference, return, subscript, casted use, or compound assignment.",
            ]
        )
    if focus in {"too_broad_precision", "flagged_good"} or "replace_overbroad_trigger_with_bad_context" in actions:
        lines.extend(
            [
                "- Precision template: constrain the branch that matched flagged GOOD; do not append unrelated branches.",
                "  Before:",
                "    - patterns:",
                "        - pattern: BROAD_SHARED_TRIGGER(...);",
                "  After:",
                "    - patterns:",
                "        - pattern: BROAD_SHARED_TRIGGER_WITH_BAD_ONLY_ARGUMENT_OR_CONTEXT(...);",
                "        - pattern-not-inside: LOCAL_SAFE_REGION_WITH_SAME_BOUND_METAVARIABLE",
                "- If GOOD and BAD share the same operator/API, use positive BAD-only context first; use pattern-not only for a narrower overlapping safe subset.",
                "- If branch-local contrast includes `control_flow_shapes=else_if_chain_without_final_else_block`, the positive trigger must represent missing-final-else shape, not any if/else-if chain.",
                "- When the rule has multiple if/else-if sibling branches, add the matching final-else exclusion to all same-family siblings; fixing only one sibling leaves GOOD matches through the others.",
                "- If branch-local contrast includes `lifetime_shapes=release_then_null_reset_same_pointer`, bind the positive release as `free($P);` or `delete $P;`, then exclude a same-metavariable ordered safe region such as `if (...) { ... free($P); ... $P = NULL; ... }` or `delete $P; ... $P = nullptr;`.",
                "- If branch-local contrast includes `provenance_relations=subtraction_operands_share_base`, exclude or avoid same-base subtraction; BAD-positive context should require different bases or multiple local array/object origins when visible.",
                "- For allocation/check/use rules, prefer a replacement branch shaped as `pattern: *$P = ...;` or `pattern: $P[...] = ...;` plus `pattern-inside: $P = allocator(...); ...`; then add guard exclusions around the use statement.",
            ]
        )
    if "remove_good_only_positive_branch" in actions:
        lines.extend(
            [
                "- Good-only branch removal template: use this only when the localized positive branch has flagged_good_true_rate high and hit_bad_true_rate near zero.",
                "- Return edit_action `remove_good_only_positive_branch` and patch_fragment_yaml `remove localized branch`; the complete semgrep_rule_yaml should omit only that localized branch.",
                "- Do not remove a branch that contributes meaningful BAD coverage; the acceptance gate will reject BAD regression.",
            ]
        )
    if "add_taint_source_sink_or_propagator" in actions or "add_taint_sanitizer_or_scope_guard" in actions:
        lines.extend(
            [
                "- Taint template: use taint edits only when the current rule is taint-mode or the evidence has real trust-boundary source -> sink flow.",
                "- Do not create taint sources from ordinary parameters, local variables, assignments, casts, arithmetic, or sensitive names.",
                "- For coverage, add one real missing source/sink/propagator tied to the same tainted metavariable; for precision, add a sanitizer or trusted overwrite seen in GOOD.",
            ]
        )
    return lines


def _render_primary_fault_pair(contract: dict[str, Any]) -> list[str]:
    if not isinstance(contract, dict):
        return []
    target = contract.get("localized_target") if isinstance(contract.get("localized_target"), dict) else {}
    faulty = target.get("faulty_record") if isinstance(target.get("faulty_record"), dict) else {}
    reference = target.get("reference_record") if isinstance(target.get("reference_record"), dict) else {}
    counterpart = target.get("paired_counterpart_record") if isinstance(target.get("paired_counterpart_record"), dict) else {}
    if not faulty and not reference and not counterpart:
        return []

    lines = [
        "Primary RuleRefiner fault pair:",
        "- Treat this pair as the main repair target; other examples are regression checks.",
        f"- localized YAML predicate: {_short(target.get('summary') or '', 420)}",
    ]
    if faulty:
        lines.append(
            "- faulty case: {} {}:{}-{} label={}".format(
                faulty.get("function") or "(unknown)",
                faulty.get("path") or "",
                faulty.get("start_line") or "",
                faulty.get("end_line") or "",
                faulty.get("label") or "",
            )
        )
        excerpt = _read_excerpt(
            path_raw=str(faulty.get("path") or ""),
            start_line=int(faulty.get("start_line", 0) or 0),
            end_line=int(faulty.get("end_line", 0) or 0),
            max_lines=18,
            max_chars=900,
        )
        if excerpt:
            lines.append("faulty excerpt:")
            lines.append(excerpt)
    if reference:
        lines.append(
            "- reference case: {} {}:{}-{} label={}".format(
                reference.get("function") or "(unknown)",
                reference.get("path") or "",
                reference.get("start_line") or "",
                reference.get("end_line") or "",
                reference.get("label") or "",
            )
        )
        excerpt = _read_excerpt(
            path_raw=str(reference.get("path") or ""),
            start_line=int(reference.get("start_line", 0) or 0),
            end_line=int(reference.get("end_line", 0) or 0),
            max_lines=18,
            max_chars=900,
        )
        if excerpt:
            lines.append("reference excerpt:")
            lines.append(excerpt)
    if counterpart:
        lines.append(
            "- paired counterpart case: {} {}:{}-{} label={}".format(
                counterpart.get("function") or "(unknown)",
                counterpart.get("path") or "",
                counterpart.get("start_line") or "",
                counterpart.get("end_line") or "",
                counterpart.get("label") or "",
            )
        )
        excerpt = _read_excerpt(
            path_raw=str(counterpart.get("path") or ""),
            start_line=int(counterpart.get("start_line", 0) or 0),
            end_line=int(counterpart.get("end_line", 0) or 0),
            max_lines=18,
            max_chars=900,
        )
        if excerpt:
            lines.append("paired counterpart excerpt:")
            lines.append(excerpt)
        lines.append("- The repair must preserve the BAD/GOOD distinction in this paired counterpart, not just the generic reference case.")
    return lines


def build_repair_prompt(
    requirement_text: str,
    current_rule_yaml: str,
    analysis: dict[str, Any],
    focus: str,
) -> str:
    cases = analysis.get("cases") if isinstance(analysis.get("cases"), dict) else {}
    current_metrics = analysis.get("previous_metrics") if isinstance(analysis.get("previous_metrics"), dict) else {}
    edit_contract = analysis.get("repair_edit_contract") if isinstance(analysis.get("repair_edit_contract"), dict) else {}
    repair_stage = analysis.get("repair_stage") if isinstance(analysis.get("repair_stage"), dict) else {}
    prompt_lines = [
        "You are an expert Semgrep rule engineer repairing one existing Semgrep OSS rule for C/C++.",
        "Return STRICT JSON only with these keys:",
        "- edit_action: one string chosen exactly from the allowed actions in the edit contract",
        "- localized_predicate: short string naming the YAML predicate/branch you edited",
        "- regression_expectation: short string saying how BAD/GOOD counts should change",
        "- patch_fragment_yaml: local YAML fragment for the edit action; for coverage return one branch item, for precision return one constraint item or replacement branch",
        "- semgrep_rule_yaml: string containing one complete YAML file",
        "- notes: short string with root cause, localized predicate/branch, local edit, and regression guard",
        "",
        "Task: fix the current misclassification by local rule refinement, not by rewriting from scratch.",
        "Use the RuleRefiner method: compare faulty cases with correctly handled reference cases, inspect the localized predicate graph, select one edit action from the contract, then edit only the suspicious pattern/branch.",
        "Allowed concrete evidence: standard/library/framework/security API names, operators, type names, field names, source APIs, sink APIs, and language tokens may be used directly when they carry semantic meaning.",
        "Do not anchor on user-defined helper/wrapper names just because they appear in samples; use a wrapper only when its visible body is the local semantic evidence.",
        "Forbidden identity evidence: paths, filenames, test IDs, line numbers, one-off literals, and one branch per sample.",
        "",
        f"Repair focus: {focus}",
        "Repair stage: stage={}; coverage is attempted before precision cleanup".format(
            repair_stage.get("stage") or "",
        ),
        "Previous metrics: "
        + ", ".join(f"{key}={value}" for key, value in current_metrics.items()),
        "",
    ]
    prompt_lines.extend(_render_rule_refiner_fix_hint(focus))
    prompt_lines.extend(_render_repair_edit_contract(edit_contract))
    rejected_repairs = _rejected_repair_entries(analysis)
    if rejected_repairs:
        prompt_lines.extend(["", "Recently rejected repair attempts to avoid repeating:"])
        for item in rejected_repairs[-4:]:
            failure_class = str(item.get("failure_class") or "").strip()
            prompt_lines.append(
                "- class={}; focus={}; action={}; localized={}; reason={}".format(
                    _short(failure_class, 80),
                    _short(item.get("focus") or "", 80),
                    _short(item.get("edit_action") or "", 80),
                    _short(item.get("localized_predicate") or item.get("localized_target_summary") or "", 220),
                    _short(item.get("reason") or "", 360),
                )
            )
            patch_fragment = str(item.get("patch_fragment_yaml") or "").strip()
            if patch_fragment:
                prompt_lines.append("  previous_patch={}".format(_short(patch_fragment, 420)))
        prompt_lines.extend(
            [
                "- If class=precision_overcut_bad, avoid positive narrowing actions and preserve every current BAD branch.",
                "- If class=exclusion_not_overlapping, you may still use a safe exclusion, but it must reuse the same bound metavariable from the positive trigger and the excluded region must contain the exact flagged GOOD finding statement/expression.",
                "- If class=replacement_not_discriminative, do not replace the same trigger with another shared surface; use safe exclusion/sanitizer or a different stable BAD-only context.",
                "- If class=precision_no_fp_delta, choose a different localized predicate or a patch that visibly overlaps the flagged GOOD finding span.",
                "- Choose a different localized predicate or a different allowed action unless the previous attempt failed only from YAML syntax.",
            ]
        )
    prompt_lines.extend(_render_template_patch_examples(edit_contract))
    prompt_lines.append("")
    primary_pair_lines = _render_primary_fault_pair(edit_contract)
    if primary_pair_lines:
        prompt_lines.extend(primary_pair_lines)
        prompt_lines.append("")

    prompt_lines.extend(
        [
            "Acceptance target:",
            "- YAML must validate with Semgrep.",
            "- Two-stage policy: before BAD reaches the target floor, repair coverage first; after BAD reaches the floor, repair precision.",
            "- For too-narrow repairs in BAD-first stage: BAD hits must increase. GOOD FP movement is recorded for later precision cleanup.",
            "- For too-broad repairs after BAD floor: GOOD false positives must decrease and BAD hit count must not decrease.",
            "- When GOOD false positives are very high, still preserve every current BAD hit; do not trade BAD recall for FP reduction.",
            "- For mixed repairs: BAD hit count must not decrease, GOOD FP must not increase, and at least one metric should improve.",
            "- Semgrep-hard examples do not need forced coverage.",
            "- For source-to-sink dataflow, prefer taint mode or local taint-mode edits; model side-effect buffer sources and sanitizers explicitly.",
            "- Do not rely on metavariable names such as $INT/$FLOAT/$TYPE as C/C++ type constraints.",
            "- Do not use all-metavariable assignment/arithmetic as a whole trigger unless another positive predicate supplies concrete BAD-only context.",
            "- A sibling pattern-not cannot prove that a reset/check/cast does not occur later; model ordered safe regions with the same metavariable or keep the branch partial.",
            "- For immediate release/reset safe forms, prefer branch-local pattern-not-inside over unordered pattern-not, e.g. exclude the ordered region `free($P);` followed by `$P = NULL;`.",
            "- Prefer structural patterns for repairs. Use pattern-regex only as a local fallback for lexical/parser-fragile BAD signal lines.",
            "- In pattern-regex, use portable classes such as [A-Za-z_][A-Za-z0-9_]*; avoid POSIX bracket classes such as [[:space:]] and [[:alnum:]].",
            "",
            "Current rule YAML:",
            guardian.shorten(current_rule_yaml, limit=7600),
            "",
        ]
    )
    prompt_lines.extend(_render_rule_refiner_localization_block(analysis, focus))
    prompt_lines.extend(
        [
            "",
            "Semgrep explanation / predicate graph localization summary:",
            guardian.shorten(
                json.dumps(
                    {
                        "localized_too_narrow_predicates": analysis.get("localized_too_narrow_predicates"),
                        "localized_overbroad_predicates": analysis.get("localized_overbroad_predicates"),
                        "predicate_discriminative_scores": analysis.get("predicate_discriminative_scores"),
                        "missed_bad_carrier_shape_catalog": analysis.get("missed_bad_carrier_shape_catalog"),
                        "branch_local_contrast": analysis.get("branch_local_contrast"),
                        "rule_refiner_path_alignment": analysis.get("rule_refiner_path_alignment"),
                        "rule_shape_diagnostics": analysis.get("rule_shape_diagnostics"),
                        "repair_action_plan": analysis.get("repair_action_plan"),
                        "repair_edit_contract": analysis.get("repair_edit_contract"),
                        "repair_gate": analysis.get("repair_gate"),
                        "path_summaries": analysis.get("path_summaries"),
                        "semgrep_hard_note": analysis.get("semgrep_hard_note"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                limit=6200,
            ),
            "",
        ]
    )
    prompt_lines.extend(_render_predicates("Too-narrow predicate details:", analysis.get("localized_too_narrow_predicates", [])))
    prompt_lines.extend(_render_predicates("Overbroad predicate details:", analysis.get("localized_overbroad_predicates", [])))
    prompt_lines.extend(["", "Problematic cases to fix:"])
    if focus in {"too_broad_precision", "flagged_good"}:
        prompt_lines.extend(_render_case_group("Flagged GOOD examples:", cases.get("flagged_good", []) if isinstance(cases, dict) else []))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Hit BAD reference examples to preserve:", cases.get("hit_bad_reference", []) if isinstance(cases, dict) else [], limit=3))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Clean GOOD reference examples to preserve:", cases.get("clean_good_reference", []) if isinstance(cases, dict) else [], limit=3))
    elif focus in {"too_narrow_coverage", "missed_bad"}:
        prompt_lines.extend(_render_case_group("Missed BAD examples:", cases.get("missed_bad", []) if isinstance(cases, dict) else []))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Clean GOOD reference examples to preserve:", cases.get("clean_good_reference", []) if isinstance(cases, dict) else [], limit=3))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Hit BAD reference examples to preserve:", cases.get("hit_bad_reference", []) if isinstance(cases, dict) else [], limit=3))
    else:
        prompt_lines.extend(_render_case_group("Missed BAD examples:", cases.get("missed_bad", []) if isinstance(cases, dict) else []))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Flagged GOOD examples:", cases.get("flagged_good", []) if isinstance(cases, dict) else []))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Hit BAD reference examples to preserve:", cases.get("hit_bad_reference", []) if isinstance(cases, dict) else [], limit=3))
        prompt_lines.extend([""])
        prompt_lines.extend(_render_case_group("Clean GOOD reference examples to preserve:", cases.get("clean_good_reference", []) if isinstance(cases, dict) else [], limit=3))
    prompt_lines.extend([""])
    prompt_lines.extend(
        [
            "",
            "Original requirement and prior iteration feedback:",
            guardian.shorten(requirement_text, limit=5200),
        ]
    )
    reference_doc = _load_reference_doc()
    if reference_doc:
        prompt_lines.extend(["", "Compact Semgrep repair syntax reference:", reference_doc])
    prompt_lines.extend(
        [
            "",
            "Output constraints:",
            "- Return exactly one complete YAML file under semgrep_rule_yaml.",
            "- Keep top-level `rules:` with exactly one rule.",
            "- Use valid Semgrep OSS syntax only.",
            "- No alternatives, candidates, fallback rules, markdown, or placeholders.",
            "- edit_action must exactly match one allowed action from the contract.",
            "- localized_predicate must name the branch or predicate changed; do not leave it blank.",
            "- regression_expectation must state the expected BAD/GOOD movement in one sentence.",
            "- patch_fragment_yaml must be a local YAML fragment matching edit_action, even when semgrep_rule_yaml is complete.",
            "- In notes, do not include long chain-of-thought; provide only a compact repair summary.",
        ]
    )
    return "\n".join(prompt_lines)


def build_validation_repair_prompt(requirement_text: str, candidate_yaml: str, validation_error: str) -> str:
    return f"""Repair only YAML/Semgrep syntax errors in this candidate rule.

Return STRICT JSON only with key:
- semgrep_rule_yaml: string containing one complete YAML file

Validation error:
{guardian.shorten(validation_error, limit=2200)}

Requirement summary:
{guardian.shorten(requirement_text, limit=2600)}

Candidate YAML:
{guardian.shorten(candidate_yaml, limit=7000)}

Rules:
- Preserve the intended local repair semantics.
- Keep exactly one rule under top-level rules:.
- Flatten invalid pattern-either/patterns structures.
- pattern-not must be a scalar and may only use already-bound metavariables or concrete syntax.
- Use block scalars for C/C++ patterns starting with * or &.
- For C/C++ block/control-flow patterns, do not use fake whole-block metavariables such as $BODY/$THEN/$ELSE. Use ... inside real braces or match the decisive local condition/statement.
- Do not use ellipsis-only context such as `pattern-inside: ...`; it is a no-op and must be replaced with real local context or removed.
- Avoid unconstrained C/C++ type/cast metavariables such as `($CAST)($EXPR)`, `($TYPE *)$PTR`, or `sizeof($TYPE)` as the repaired trigger. Use concrete parseable type alternatives or a short line-local regex fallback tied to the risky expression.
- If an if/else-if/else chain does not parse as one pattern, keep the same intent by using smaller parseable structural patterns.
    """


def _extract_yaml_from_payload(payload: dict[str, Any]) -> str:
    raw = payload.get("semgrep_rule_yaml")
    if isinstance(raw, str):
        return normalize_yaml(raw)
    if isinstance(raw, dict):
        return normalize_yaml(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False))
    return normalize_yaml(str(raw or ""))


def _repair_contract_compliance(payload: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    contract = analysis.get("repair_edit_contract") if isinstance(analysis.get("repair_edit_contract"), dict) else {}
    allowed = contract.get("allowed_actions") if isinstance(contract.get("allowed_actions"), list) else []
    allowed_actions = [str(item) for item in allowed if str(item).strip()]
    edit_action = str(payload.get("edit_action") or "").strip() if isinstance(payload, dict) else ""
    localized_predicate = str(payload.get("localized_predicate") or "").strip() if isinstance(payload, dict) else ""
    regression_expectation = str(payload.get("regression_expectation") or "").strip() if isinstance(payload, dict) else ""
    patch_fragment_yaml = str(payload.get("patch_fragment_yaml") or "").strip() if isinstance(payload, dict) else ""
    issues: list[str] = []
    if not edit_action:
        issues.append("missing edit_action")
    elif allowed_actions and edit_action not in allowed_actions:
        issues.append(f"edit_action not in contract: {edit_action}")
    if not localized_predicate:
        issues.append("missing localized_predicate")
    if not regression_expectation:
        issues.append("missing regression_expectation")
    if not patch_fragment_yaml:
        issues.append("missing patch_fragment_yaml")
    return {
        "ok": not issues,
        "issues": issues,
        "edit_action": edit_action,
        "localized_predicate": localized_predicate,
        "regression_expectation": regression_expectation,
        "has_patch_fragment_yaml": bool(patch_fragment_yaml),
        "allowed_actions": allowed_actions,
    }


def run_semgrep_repair_mode(llm: LLMClient, config: RepairModeConfig) -> dict[str, Any]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    current_rule_text = config.current_rule_yaml.read_text(encoding="utf-8", errors="replace")
    base_snapshot_path = config.output_dir / "base_rule_snapshot.yml"
    base_snapshot_path.write_text(current_rule_text, encoding="utf-8")
    analysis = build_repair_analysis(config)
    focus = str(config.forced_focus or "").strip() or choose_repair_focus(config.prev_eval, analysis)
    gate = analysis.get("repair_gate") if isinstance(analysis.get("repair_gate"), dict) else {}
    if gate and not bool(gate.get("should_repair", True)):
        guardian.write_json(config.output_dir / "repair_analysis.json", analysis)
        report = {
            "mode": "repair",
            "focus": focus,
            "base_rule_yaml": str(base_snapshot_path.resolve()),
            "source_base_rule_yaml": str(config.current_rule_yaml.resolve()),
            "candidate_rule_yaml": "",
            "validation": {
                "ok": False,
                "returncode": 0,
                "stdout": "",
                "stderr": str(gate.get("reason") or "repair skipped by evidence gate"),
                "timed_out": False,
            },
            "validation_ok": False,
            "repair_skipped": True,
            "repair_skip_reason": str(gate.get("reason") or "repair skipped by evidence gate"),
            "repair_skip_fallback": str(gate.get("fallback") or "fresh_generation"),
            "analysis_path": str((config.output_dir / "repair_analysis.json").resolve()),
            "repair_edit_contract": analysis.get("repair_edit_contract"),
            "contract_compliance": {"ok": False, "issues": ["repair skipped by evidence gate"]},
            "edit_action": "skip_to_fresh_generation",
            "localized_predicate": "",
            "regression_expectation": "",
            "raw_error": "",
        }
        guardian.write_json(config.output_dir / "repair_report.json", report)
        print(
            "[repair_mode] skipped local repair; switching to fresh generation. reason={}".format(
                guardian.shorten(str(gate.get("reason") or ""), 500)
            ),
            flush=True,
        )
        return report
    prompt = build_repair_prompt(
        requirement_text=config.requirement_text,
        current_rule_yaml=current_rule_text,
        analysis=analysis,
        focus=focus,
    )
    (config.output_dir / "repair_prompt.txt").write_text(prompt, encoding="utf-8")
    guardian.write_json(config.output_dir / "repair_analysis.json", analysis)

    payload: dict[str, Any] = {}
    raw_error = ""
    try:
        payload = llm.ask_json(prompt, retries=2)
    except Exception as exc:
        raw_error = f"repair_llm_error: {exc}"
    guardian.write_json(config.output_dir / "repair_payload.json", payload)
    contract_compliance = _repair_contract_compliance(payload, analysis)

    template_patch_yaml = apply_template_patch_from_payload(current_rule_text, payload, analysis) if payload else ""
    if template_patch_yaml.strip():
        (config.output_dir / "repair_template_candidate.yml").write_text(template_patch_yaml, encoding="utf-8")
    candidate_yaml = template_patch_yaml or (_extract_yaml_from_payload(payload) if payload else "")
    candidate_path = config.output_dir / "repair_candidate.yml"
    candidate_path.write_text(candidate_yaml, encoding="utf-8")

    if candidate_yaml.strip():
        validation = guardian.validate_rule_yaml(
            semgrep_bin=config.semgrep_bin,
            yaml_path=candidate_path,
            timeout_seconds=max(1.0, float(config.validate_timeout_seconds)),
        )
    else:
        validation = {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": raw_error or "empty repair semgrep_rule_yaml",
            "timed_out": False,
        }

    repaired_syntax = False
    if (not validation.get("ok")) and candidate_yaml.strip():
        validation_error = str(validation.get("stderr") or validation.get("stdout") or "")
        print(
            "[repair_mode] invalid repaired YAML; attempting syntax-only repair. error={}".format(
                guardian.shorten(validation_error.replace("\n", " "), 500)
            ),
            flush=True,
        )
        syntax_prompt = build_validation_repair_prompt(
            requirement_text=config.requirement_text,
            candidate_yaml=candidate_yaml,
            validation_error=validation_error,
        )
        (config.output_dir / "repair_syntax_prompt.txt").write_text(syntax_prompt, encoding="utf-8")
        try:
            syntax_payload = llm.ask_json(syntax_prompt, retries=1)
            guardian.write_json(config.output_dir / "repair_syntax_payload.json", syntax_payload)
            syntax_yaml = _extract_yaml_from_payload(syntax_payload)
            if syntax_yaml.strip():
                candidate_path.write_text(syntax_yaml, encoding="utf-8")
                candidate_yaml = syntax_yaml
                validation = guardian.validate_rule_yaml(
                    semgrep_bin=config.semgrep_bin,
                    yaml_path=candidate_path,
                    timeout_seconds=max(1.0, float(config.validate_timeout_seconds)),
                )
                repaired_syntax = bool(validation.get("ok"))
        except Exception as exc:
            raw_error = f"repair_syntax_llm_error: {exc}"

    semantic_noop = False
    if validation.get("ok") and candidate_yaml.strip():
        semantic_noop = _repair_candidate_is_semantic_noop(current_rule_text, candidate_yaml)
        if semantic_noop:
            validation = {
                "ok": False,
                "returncode": -2,
                "stdout": "",
                "stderr": "repair candidate is a semantic no-op: pattern/operator signature is unchanged from the base rule",
                "timed_out": False,
            }

    report = {
        "mode": "repair",
        "focus": focus,
        "base_rule_yaml": str(base_snapshot_path.resolve()),
        "source_base_rule_yaml": str(config.current_rule_yaml.resolve()),
        "candidate_rule_yaml": str(candidate_path.resolve()) if bool(validation.get("ok")) else "",
        "validation": validation,
        "validation_ok": bool(validation.get("ok")),
        "syntax_repaired": repaired_syntax,
        "semantic_noop": semantic_noop,
        "template_patch_applied": bool(template_patch_yaml.strip()),
        "template_patch_candidate_yaml": str((config.output_dir / "repair_template_candidate.yml").resolve()) if template_patch_yaml.strip() else "",
        "analysis_path": str((config.output_dir / "repair_analysis.json").resolve()),
        "prompt_path": str((config.output_dir / "repair_prompt.txt").resolve()),
        "repair_edit_contract": analysis.get("repair_edit_contract"),
        "contract_compliance": contract_compliance,
        "edit_action": contract_compliance.get("edit_action"),
        "localized_predicate": contract_compliance.get("localized_predicate"),
        "regression_expectation": contract_compliance.get("regression_expectation"),
        "raw_error": raw_error,
    }
    guardian.write_json(config.output_dir / "repair_report.json", report)
    if not validation.get("ok"):
        validation_error = str(validation.get("stderr") or validation.get("stdout") or raw_error or "")
        print(
            "[repair_mode] invalid Semgrep YAML/rule validation; attempt will not be counted. error={}".format(
                guardian.shorten(validation_error.replace("\n", " "), 700)
            ),
            flush=True,
        )
    return report


def _overall_correct(report: dict[str, Any]) -> int:
    bad_hit = int(report.get("bad_hit", 0) or 0)
    good_total = int(report.get("good_total", 0) or 0)
    good_hit = int(report.get("good_hit", 0) or 0)
    return bad_hit + max(0, good_total - good_hit)


def evaluate_repair_acceptance(
    base_eval: dict[str, Any] | None,
    candidate_eval: dict[str, Any],
    repair_focus: str = "",
) -> dict[str, Any]:
    if not isinstance(base_eval, dict) or not base_eval:
        return {
            "accepted": True,
            "reason": "no base eval available; valid candidate is usable",
            "repair_focus": repair_focus,
        }

    focus = str(repair_focus or "").strip()
    base_bad_hit = int(base_eval.get("bad_hit", 0) or 0)
    cand_bad_hit = int(candidate_eval.get("bad_hit", 0) or 0)
    base_good_hit = int(base_eval.get("good_hit", 0) or 0)
    cand_good_hit = int(candidate_eval.get("good_hit", 0) or 0)
    good_total = max(int(base_eval.get("good_total", 0) or 0), int(candidate_eval.get("good_total", 0) or 0))

    good_fp_down = cand_good_hit < base_good_hit
    good_fp_up = cand_good_hit > base_good_hit

    base_correct = _overall_correct(base_eval)
    cand_correct = _overall_correct(candidate_eval)
    overall_improved = cand_correct > base_correct
    overall_gain = cand_correct - base_correct
    bad_gain = cand_bad_hit - base_bad_hit
    good_fp_drop = max(0, base_good_hit - cand_good_hit)
    good_fp_increase = max(0, cand_good_hit - base_good_hit)
    bad_dropped = cand_bad_hit < base_bad_hit
    bad_preserved = cand_bad_hit >= base_bad_hit
    good_fp_preserved = cand_good_hit <= base_good_hit

    if focus == "too_narrow_coverage":
        accepted = bool(cand_bad_hit > base_bad_hit)
    elif focus == "too_broad_precision":
        accepted = bool(bad_preserved and good_fp_down)
    else:
        accepted = bool(
            bad_preserved
            and good_fp_preserved
            and (cand_bad_hit > base_bad_hit or good_fp_down or overall_improved)
        )
    reasons: list[str] = []
    if bad_dropped:
        reasons.append(f"BAD hit dropped from {base_bad_hit} to {cand_bad_hit}; no BAD drop is allowed")
    if focus == "too_narrow_coverage" and cand_bad_hit <= base_bad_hit:
        reasons.append(f"too-narrow repair did not increase BAD hits ({base_bad_hit} -> {cand_bad_hit})")
    if focus == "too_broad_precision" and accepted:
        reasons.append(
            f"precision accepted with BAD preserved: BAD {base_bad_hit}->{cand_bad_hit}, GOOD FP {base_good_hit}->{cand_good_hit}"
        )
    if focus == "too_broad_precision" and not good_fp_down:
        reasons.append(f"too-broad repair did not reduce GOOD false positives ({base_good_hit} -> {cand_good_hit})")
    if focus not in {"too_narrow_coverage", "too_broad_precision"} and not good_fp_preserved:
        reasons.append(f"mixed repair increased GOOD false positives ({base_good_hit} -> {cand_good_hit})")
    if focus not in {"too_narrow_coverage", "too_broad_precision"} and not (
        cand_bad_hit > base_bad_hit or good_fp_down or overall_improved
    ):
        reasons.append("mixed repair made no accepted metric improvement")
    if good_fp_down:
        reasons.append(f"GOOD false positives decreased from {base_good_hit} to {cand_good_hit}")
    if good_fp_up:
        reasons.append(f"GOOD false positives increased from {base_good_hit} to {cand_good_hit}")
    if overall_improved:
        reasons.append(f"overall correct improved from {base_correct} to {cand_correct}")
    if focus == "too_narrow_coverage" and bad_gain > 0:
        reasons.append(f"coverage tradeoff: BAD gain {bad_gain}, GOOD FP increase {good_fp_increase}, net gain {overall_gain}")
    if focus != "too_narrow_coverage" and not (good_fp_down or overall_improved):
        reasons.append("no GOOD FP reduction or total-correct improvement")

    return {
        "accepted": accepted,
        "reason": "; ".join(reasons) or "accepted",
        "repair_focus": focus,
        "base_bad_hit": base_bad_hit,
        "candidate_bad_hit": cand_bad_hit,
        "base_good_hit": base_good_hit,
        "candidate_good_hit": cand_good_hit,
        "base_overall_correct": base_correct,
        "candidate_overall_correct": cand_correct,
        "overall_gain": overall_gain,
        "bad_gain": bad_gain,
        "good_fp_drop": good_fp_drop,
        "good_fp_increase": good_fp_increase,
        "bad_not_obvious_drop": bad_preserved,
        "bad_preserved": bad_preserved,
        "good_fp_preserved": good_fp_preserved,
        "bad_dropped": bad_dropped,
        "bad_drop_requires_overall_gain": False,
        "good_fp_down": good_fp_down,
        "good_fp_up": good_fp_up,
        "overall_improved": overall_improved,
    }
