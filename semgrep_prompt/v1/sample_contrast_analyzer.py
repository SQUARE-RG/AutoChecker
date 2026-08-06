#!/usr/bin/env python3
"""Generic BAD/GOOD paired sample contrast analysis for rule synthesis."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SENSITIVE_NAME_RE = re.compile(
    r"\b(password|passwd|secret|token|credential|api[_ -]?key|private|session|auth)\b",
    flags=re.IGNORECASE,
)

REDACTION_RE = re.compile(
    r"\b(redacted|masked|hidden|provided|present|failed|rejected|status|ok|success|denied)\b",
    flags=re.IGNORECASE,
)

CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_:]*)\s*\(")

CONTROL_WORDS = {"if", "for", "while", "switch", "return", "sizeof", "catch"}

BUILTIN_C_TYPES = [
    "unsigned long long",
    "long long",
    "unsigned int",
    "signed int",
    "unsigned short",
    "signed short",
    "unsigned char",
    "signed char",
    "long double",
    "size_t",
    "ptrdiff_t",
    "float",
    "double",
    "long",
    "short",
    "int",
    "char",
    "bool",
]

OPERATOR_IN_COMPARISON_RE = r"(?:<<|>>|[&|^+\-*/%])"
COMPARISON_RE = r"(?:==|!=|<=|>=|<|>)"

EXECUTABLE_SIGNAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "sizeof_in_pointer_offset",
        re.compile(
            r"(?:\*\s*\([^;\n]*\+\s*[^;\n]*sizeof\s*\([^;\n]*\)[^;\n]*\)|"
            r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\+=|=)\s*[^;\n]*\+\s*[^;\n]*sizeof\s*\([^;\n]*\)[^;\n]*;|"
            r"\b[A-Za-z_][A-Za-z0-9_]*\s*\+=\s*[^;\n]*sizeof\s*\([^;\n]*\)[^;\n]*;)"
        ),
    ),
    (
        "casted_pointer_write",
        re.compile(r"\*\s*\([^;\n]*\*\s*\)\s*\([^;\n]*\)\s*(?:=|\+=|-=|\|=|&=|\^=)"),
    ),
    (
        "casted_pointer_offset_carrier",
        re.compile(
            r"(?:=\s*\*\s*\([^;\n]*\*\s*\)\s*\([^;\n]*\+\s*[^;\n]*\)\s*;|"
            r"=\s*\([^;\n]*\*\s*\)\s*\([^;\n]*\+\s*[^;\n]*\)\s*;)"
        ),
    ),
    (
        "sizeof_in_array_subscript",
        re.compile(r"=\s*[A-Za-z_][A-Za-z0-9_]*\s*\[[^;\n]*sizeof\s*\([^;\n]*\)[^;\n]*\]\s*;"),
    ),
    (
        "alternate_view_member_or_index_write",
        re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.\w+|\[[^]]+\])+(?:\s*(?:=|\+=|-=|\|=|&=|\^=))"),
    ),
    (
        "release_call",
        re.compile(r"\b(?:free\s*\([^;\n]*\)|delete(?:\s*\[\])?\s+[A-Za-z_][A-Za-z0-9_]*)\s*;"),
    ),
    (
        "allocation_then_use",
        re.compile(r"\b(?:malloc|calloc|realloc|new)\b|(?:\*[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\s*\[)"),
    ),
    (
        "assignment_in_condition",
        re.compile(r"\b(?:if|while|for)\s*\([^;\n]*(?<![=!<>])=(?!=)[^;\n]*\)"),
    ),
    (
        "anonymous_record_declaration",
        re.compile(r"\b(?:struct|union)\s*\{"),
    ),
]


def read_text(path_raw: str) -> str:
    try:
        return Path(str(path_raw)).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def read_item_text(item: dict[str, Any]) -> str:
    """Read the region represented by an eval/example item when line bounds exist."""
    if not isinstance(item, dict):
        return ""
    path = str(item.get("path") or "")
    text = read_text(path)
    if not text:
        return ""

    try:
        start = int(item.get("start_line") or 0)
        end = int(item.get("end_line") or 0)
    except (TypeError, ValueError):
        start = 0
        end = 0

    if start <= 0 or end < start:
        return text

    lines = text.splitlines()
    if not lines:
        return text
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)
    if start_idx >= end_idx:
        return text
    return "\n".join(lines[start_idx:end_idx])


def compact_line(line: str, limit: int = 180) -> str:
    text = " ".join(str(line or "").strip().split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def extract_calls(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for match in CALL_RE.finditer(text or ""):
        name = match.group(1).split("::")[-1]
        lower = name.lower()
        if lower in CONTROL_WORDS or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def interesting_lines(text: str, limit: int = 10) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    for idx, raw in enumerate(str(text or "").splitlines()):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//") or line.startswith("/*"):
            continue
        if line in {"{", "}", "};"}:
            continue
        score = 0
        if extract_calls(line):
            score += 3
        if "=" in line:
            score += 2
        if re.search(r"\*\s*\(|\([A-Za-z_][A-Za-z0-9_\s]*\*\)", line):
            score += 5
        if re.search(r"=\s*\*?\s*\([^;\n]*\*\s*\)\s*\([^;\n]*\+\s*[^;\n]*\)", line):
            score += 7
        if re.search(r"\[[^]]*sizeof\s*\(", line):
            score += 7
        if re.search(r"\[[^]]+\]\s*(?:=|\+=|-=|\|=|&=|\^=)", line):
            score += 4
        if re.search(r"\.\w+(?:\.|\[)", line):
            score += 3
        if SENSITIVE_NAME_RE.search(line):
            score += 4
        if REDACTION_RE.search(line):
            score += 2
        if "%" in line and '"' in line:
            score += 2
        if score <= 0:
            continue
        scored.append((-score, idx, compact_line(line)))

    out: list[str] = []
    seen: set[str] = set()
    for _score, _idx, line in sorted(scored):
        if line in seen:
            continue
        seen.add(line)
        out.append(line)
        if len(out) >= max(1, int(limit)):
            break
    return out


def extract_type_tokens(text: str, limit: int = 12) -> list[str]:
    raw = str(text or "")
    tokens: list[str] = []
    seen: set[str] = set()
    for type_name in BUILTIN_C_TYPES:
        if re.search(rf"\b{re.escape(type_name)}\b", raw):
            if type_name not in seen:
                seen.add(type_name)
                tokens.append(type_name)
    for match in re.finditer(r"\b(?:struct|union)\s+([A-Za-z_][A-Za-z0-9_]*)\b", raw):
        token = f"{match.group(0)}"
        if token not in seen:
            seen.add(token)
            tokens.append(token)
    for match in re.finditer(r"\b(?:const\s+)?(?:unsigned\s+|signed\s+)?(?:char|short|int|long|float|double|bool|size_t|ptrdiff_t)\b", raw):
        token = re.sub(r"\s+", " ", match.group(0).strip())
        if token not in seen:
            seen.add(token)
            tokens.append(token)
    return tokens[: max(1, int(limit))]


def executable_bad_signal_lines(text: str, limit: int = 12) -> list[dict[str, str]]:
    """Return concrete BAD-token lines that can be translated directly to Semgrep.

    These are not templates. They are small generic syntax families extracted from
    the current paired examples so the generator can avoid inventing non-existent
    helper assignments or type-only placeholders.
    """
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw in str(text or "").splitlines():
        line = compact_line(raw, limit=220)
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        for family, regex in EXECUTABLE_SIGNAL_PATTERNS:
            if not regex.search(line):
                continue
            key = (family, line)
            if key in seen:
                continue
            seen.add(key)
            out.append({"family": family, "line": line})
            break
        if len(out) >= max(1, int(limit)):
            break
    return out


def prioritize_executable_signal_lines(items: list[dict[str, str]], limit: int = 30) -> list[dict[str, str]]:
    first_by_family: list[dict[str, str]] = []
    rest: list[dict[str, str]] = []
    seen_families: set[str] = set()
    seen_items: set[tuple[str, str]] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        family = str(item.get("family") or "").strip()
        line = str(item.get("line") or "").strip()
        if not family or not line:
            continue
        key = (family, line)
        if key in seen_items:
            continue
        seen_items.add(key)
        if family not in seen_families:
            seen_families.add(family)
            first_by_family.append(item)
        else:
            rest.append(item)
    return [*first_by_family, *rest][: max(1, int(limit))]


def feature_flags(text: str) -> dict[str, bool]:
    raw = str(text or "")
    return {
        "has_sensitive_names": bool(SENSITIVE_NAME_RE.search(raw)),
        "has_redaction_or_status_literals": bool(REDACTION_RE.search(raw)),
        "has_format_sensitive_field": bool(
            re.search(r"\"[^\"]*(password|token|secret|credential|api[_ -]?key)[^\"]*%[^;]*\"", raw, flags=re.IGNORECASE)
        ),
        "has_format_to_buffer": bool(re.search(r"\b(?:snprintf|sprintf|swprintf)\s*\(", raw)),
        "has_output_sink": bool(
            re.search(
                r"\b(?:fprintf|printf|dprintf|fwprintf|fputs|puts|perror|write|syslog|OutputDebugString|NSLog)\s*\(",
                raw,
                flags=re.IGNORECASE,
            )
        ),
        "has_direct_variable_output": bool(
            re.search(r"\b(?:fputs|perror|write)\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*,", raw)
        ),
        "has_cast_or_deref_write": bool(re.search(r"\*\s*\([^;]+\)\s*(?:=|\+=|-=|\|=|&=|\^=)", raw)),
        "has_casted_pointer_offset_carrier": bool(
            re.search(
                r"(?:=\s*\*\s*\([^;]*\*\s*\)\s*\([^;]*\+\s*[^;]*\)\s*;|=\s*\([^;]*\*\s*\)\s*\([^;]*\+\s*[^;]*\)\s*;)",
                raw,
            )
        ),
        "has_pointer_deref_write": bool(
            re.search(r"\*[A-Za-z_][A-Za-z0-9_]*\s*(?:=|\+=|-=|\|=|&=|\^=|\+\+|--)", raw)
        ),
        "has_pointer_deref_use": bool(re.search(r"\*[A-Za-z_][A-Za-z0-9_]*\b", raw)),
        "has_index_write": bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\[[^]]+\]\s*(?:=|\+=|-=|\|=|&=|\^=)", raw)),
        "has_nested_member_write": bool(
            re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\.\w+(?:\.|\[)[^;]*(?:=|\+=|-=|\|=|&=|\^=)", raw)
        ),
        "has_pointer_subtraction": bool(
            re.search(r"\bptrdiff_t\b", raw)
            or re.search(
                r"\b(?:ptr|pointer|begin|end|base|cursor|buf|buffer)[A-Za-z0-9_]*\s*-\s*(?:ptr|pointer|begin|end|base|cursor|buf|buffer)[A-Za-z0-9_]*\b",
                raw,
                flags=re.IGNORECASE,
            )
        ),
        "has_sizeof_pointer_arithmetic": bool(
            re.search(r"\*\s*\([^;]*\+\s*(?:\([^)]*\)\s*)?(?:[A-Za-z_][A-Za-z0-9_]*\s*\*\s*)?sizeof\s*\(", raw)
            or re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\+=|=)\s*[^;]*sizeof\s*\(", raw)
        ),
        "has_sizeof_array_subscript": bool(re.search(r"\[[^]]*sizeof\s*\(", raw)),
        "has_plain_element_pointer_arithmetic": bool(
            re.search(r"\*\s*\([^;]*\+\s*(?:[A-Za-z_][A-Za-z0-9_]*|\d+)\s*\)", raw)
            or re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\+=\s*(?:1|[A-Za-z_][A-Za-z0-9_]*)\s*;", raw)
        ),
        "has_wrapper_call": bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]*_(?:log|debug|print|write)\s*\(", raw)),
        "has_explicit_cast": bool(re.search(r"\([A-Za-z_][A-Za-z0-9_\s\*]*\)\s*[A-Za-z_][A-Za-z0-9_]*", raw)),
        "has_explicit_integer_cast": bool(
            re.search(r"\(\s*(?:signed\s+|unsigned\s+)?(?:char|short|int|long|long\s+long|size_t)\s*\)\s*[A-Za-z_][A-Za-z0-9_]*", raw)
        ),
        "has_float_decl_or_literal": bool(
            re.search(r"\b(?:float|double|long\s+double)\s+[A-Za-z_][A-Za-z0-9_]*\b", raw)
            or re.search(r"\b\d+\.\d+(?:[fFlL])?\b", raw)
        ),
        "has_integer_decl": bool(
            re.search(r"\b(?:signed\s+|unsigned\s+)?(?:char|short|int|long|long\s+long|size_t)\s+[A-Za-z_][A-Za-z0-9_]*\b", raw)
        ),
        "has_release_call": bool(re.search(r"\b(?:free|delete)\s*(?:\(|\[\]|\s)", raw)),
        "has_null_assignment": bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:NULL|nullptr)\s*;", raw)),
        "has_release_then_null_sequence": bool(
            re.search(
                r"\bfree\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*;\s*\1\s*=\s*(?:NULL|nullptr)\s*;",
                raw,
                flags=re.DOTALL,
            )
            or re.search(
                r"\bdelete(?:\s*\[\])?\s+([A-Za-z_][A-Za-z0-9_]*)\s*;\s*\1\s*=\s*(?:NULL|nullptr)\s*;",
                raw,
                flags=re.DOTALL,
            )
        ),
        "has_null_check": bool(
            re.search(r"\bif\s*\([^)]*(?:!=|==)\s*(?:NULL|nullptr)[^)]*\)", raw)
            or re.search(r"\bif\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\)", raw)
        ),
        "has_heap_allocation": bool(re.search(r"\b(?:malloc|calloc|realloc|new)\b", raw)),
        "has_allocation_then_pointer_use": bool(
            re.search(
                r"\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\([^)]*\)\s*)?(?:malloc|calloc|realloc)\s*\([^;]*\);\s*(?:(?!\bif\s*\().)*?(?:\*[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\s*\[)",
                raw,
                flags=re.DOTALL,
            )
            or re.search(
                r"\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*new\b[^;]*;\s*(?:(?!\bif\s*\().)*?(?:\*[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\s*\[)",
                raw,
                flags=re.DOTALL,
            )
        ),
        "has_unchecked_deref_after_alloc_shape": bool(
            re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\([^)]*\)\s*)?(?:malloc|calloc|realloc)\s*\([^;]*\);\s*(?![^{}]*\bif\s*\()[^{};]*\*[A-Za-z_][A-Za-z0-9_]*", raw, flags=re.DOTALL)
        ),
        "has_global_then_local_same_name_shape": has_global_local_shadow_shape(raw),
        "has_anonymous_nested_record": bool(
            re.search(r"\b(?:struct|union)\s+[A-Za-z_][A-Za-z0-9_]*\s*\{[^{}]*\b(?:struct|union)\s*\{", raw, flags=re.DOTALL)
        ),
        "has_named_nested_record": bool(
            re.search(r"\b(?:struct|union)\s+[A-Za-z_][A-Za-z0-9_]*\s*\{[^{}]*\b(?:struct|union)\s+[A-Za-z_][A-Za-z0-9_]*\s*\{", raw, flags=re.DOTALL)
        ),
        "has_sensitive_format_output": bool(
            re.search(
                r"\b(?:fprintf|printf|dprintf|fwprintf|snprintf|sprintf)\s*\([^;]*\"[^\"]*(?:password|token|secret|credential|api[_ -]?key)[^\"]*%[^;]*,\s*[A-Za-z_]",
                raw,
                flags=re.IGNORECASE,
            )
        ),
        "has_unparenthesized_operator_comparison": bool(
            re.search(
                rf"\b(?:if|while)\s*\([^;\n()]*{OPERATOR_IN_COMPARISON_RE}[^;\n()]*{COMPARISON_RE}[^;\n()]*\)",
                raw,
            )
        ),
        "has_parenthesized_operator_operand": bool(
            re.search(
                rf"\b(?:if|while)\s*\([^;\n]*\([^;\n()]*{OPERATOR_IN_COMPARISON_RE}[^;\n()]*\)\s*{COMPARISON_RE}",
                raw,
            )
            or re.search(
                rf"\b(?:if|while)\s*\([^;\n]*{COMPARISON_RE}\s*\([^;\n()]*{OPERATOR_IN_COMPARISON_RE}[^;\n()]*\)",
                raw,
            )
        ),
    }


def has_parenthesis_only_operator_contrast(bad_text: str, good_text: str) -> bool:
    bad_flags = feature_flags(bad_text)
    good_flags = feature_flags(good_text)
    if bad_flags.get("has_unparenthesized_operator_comparison") and good_flags.get("has_parenthesized_operator_operand"):
        return True
    bad_norm = re.sub(r"\s+", "", str(bad_text or ""))
    good_norm = re.sub(r"\s+", "", str(good_text or ""))
    if not bad_norm or not good_norm:
        return False
    good_without_paren = re.sub(r"\(([^()]+(?:<<|>>|[&|^+\-*/%])[^()]*)\)", r"\1", good_norm)
    return bad_norm in good_without_paren or good_without_paren in bad_norm


DECL_NAME_RE = re.compile(
    r"^\s*(?:static\s+)?(?:const\s+)?(?:unsigned\s+|signed\s+)?"
    r"(?:int|long|short|char|float|double|bool|size_t|ptrdiff_t|FILE|[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*\*)?\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;|\[)",
)


def has_global_local_shadow_shape(text: str) -> bool:
    globals_seen: set[str] = set()
    depth = 0
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        before_depth = depth
        opens = line.count("{")
        closes = line.count("}")
        if "(" in line and ")" in line and line.endswith("{"):
            depth += opens - closes
            continue
        match = DECL_NAME_RE.match(line)
        if match:
            name = match.group(1)
            if before_depth <= 0:
                globals_seen.add(name)
            elif name in globals_seen:
                return True
        depth += opens - closes
        if depth < 0:
            depth = 0
    return False


def analyze_pairs(counterexample_pairs: list[dict[str, Any]], max_pairs: int = 10) -> dict[str, Any]:
    bad_calls: set[str] = set()
    good_calls: set[str] = set()
    bad_lines: list[str] = []
    good_lines: list[str] = []
    bad_flags: dict[str, int] = {}
    good_flags: dict[str, int] = {}
    pair_contrast_counts: dict[str, int] = {}
    executable_bad_lines: list[dict[str, str]] = []

    def bump_flags(target: dict[str, int], flags: dict[str, bool]) -> None:
        for key, value in flags.items():
            if value:
                target[key] = target.get(key, 0) + 1

    for pair in (counterexample_pairs or [])[: max(1, int(max_pairs))]:
        if not isinstance(pair, dict):
            continue
        bad = pair.get("bad_example") if isinstance(pair.get("bad_example"), dict) else {}
        good = pair.get("good_example") if isinstance(pair.get("good_example"), dict) else {}
        bad_text = read_item_text(bad)
        good_text = read_item_text(good)
        bad_calls.update(extract_calls(bad_text))
        good_calls.update(extract_calls(good_text))
        for line in interesting_lines(bad_text, limit=4):
            if line not in bad_lines:
                bad_lines.append(line)
        for line in interesting_lines(good_text, limit=4):
            if line not in good_lines:
                good_lines.append(line)
        bump_flags(bad_flags, feature_flags(bad_text))
        bump_flags(good_flags, feature_flags(good_text))
        for item in executable_bad_signal_lines(bad_text, limit=4):
            if item not in executable_bad_lines:
                executable_bad_lines.append(item)
        if has_parenthesis_only_operator_contrast(bad_text, good_text):
            pair_contrast_counts["parenthesis_only_operator_precedence"] = (
                pair_contrast_counts.get("parenthesis_only_operator_precedence", 0) + 1
            )

    bad_only_features = sorted(key for key, count in bad_flags.items() if count > 0 and good_flags.get(key, 0) == 0)
    good_only_features = sorted(key for key, count in good_flags.items() if count > 0 and bad_flags.get(key, 0) == 0)
    shared_features = sorted(key for key, count in bad_flags.items() if count > 0 and good_flags.get(key, 0) > 0)
    hard_features = [
        key
        for key in ("has_wrapper_call", "has_format_to_buffer", "has_pointer_subtraction", "has_global_then_local_same_name_shape", "has_anonymous_nested_record")
        if bad_flags.get(key, 0) > 0
    ]
    if pair_contrast_counts.get("parenthesis_only_operator_precedence", 0) > 0:
        hard_features.append("requires_lexical_parenthesis_distinction")
    return {
        "bad_calls": sorted(bad_calls),
        "good_calls": sorted(good_calls),
        "bad_lines": bad_lines[:20],
        "good_lines": good_lines[:20],
        "bad_feature_counts": bad_flags,
        "good_feature_counts": good_flags,
        "bad_only_features": bad_only_features,
        "good_only_features": good_only_features,
        "shared_features": shared_features,
        "pair_contrast_counts": pair_contrast_counts,
        "executable_bad_signal_lines": prioritize_executable_signal_lines(executable_bad_lines, limit=30),
        "semgrep_difficulty_hints": hard_features,
    }


def render_contrast_for_prompt(analysis: dict[str, Any]) -> list[str]:
    lines = ["FRONT-LOADED paired contrast analysis (generic; infer semantics, do not create per-test branches):"]
    if analysis.get("bad_calls"):
        lines.append("- BAD calls/operators: " + ", ".join(str(x) for x in analysis.get("bad_calls", [])[:18]))
    if analysis.get("good_calls"):
        lines.append("- GOOD calls/operators: " + ", ".join(str(x) for x in analysis.get("good_calls", [])[:18]))
    if analysis.get("bad_calls"):
        lines.append(
            "- Evidence anchor policy: APIs/functions/operators listed above may be used directly when they represent the requirement's source, sink, sanitizer, or risky operation. Do not use paths, test ids, or line numbers."
        )
    if analysis.get("bad_only_features"):
        lines.append("- BAD-only feature families: " + ", ".join(str(x) for x in analysis.get("bad_only_features", [])))
    if analysis.get("good_only_features"):
        lines.append("- GOOD-only safe anchors: " + ", ".join(str(x) for x in analysis.get("good_only_features", [])))
    if analysis.get("shared_features"):
        lines.append("- Shared feature families needing distinguishing context: " + ", ".join(str(x) for x in analysis.get("shared_features", [])))
    if analysis.get("semgrep_difficulty_hints"):
        lines.append("- Potential Semgrep-difficult families: " + ", ".join(str(x) for x in analysis.get("semgrep_difficulty_hints", [])))
        lines.append(
            "- Difficulty policy: if these families require cross-scope symbols, interprocedural effects, deep alias/type reasoning, or proving a later statement is absent, keep them partial instead of broadening into GOOD false positives."
        )
    pair_contrast_counts = analysis.get("pair_contrast_counts") if isinstance(analysis.get("pair_contrast_counts"), dict) else {}
    if pair_contrast_counts.get("parenthesis_only_operator_precedence", 0):
        lines.append(
            "- Lexical-only contrast: BAD/GOOD differ by parentheses around an operator operand; normal AST `pattern` may erase this distinction, so prefer `pattern-regex` with tight context or mark partial."
        )
    if analysis.get("good_only_features"):
        safe = set(str(x) for x in analysis.get("good_only_features", []))
        if safe:
            lines.append(
                "- Safe-anchor policy: GOOD-only feature families are evidence of compliant context. Preserve the BAD core and add branch-local exclusions/guards around overlapping SAFE anchors instead of widening the trigger."
            )
        if any("sequence" in item or "check" in item or "assignment" in item or "release_then_null" in item for item in safe):
            lines.append(
                "- Ordered-context policy: if a SAFE anchor is an ordered statement sequence or guard, model it as local ordered context rather than as an unrelated sibling exclusion."
            )
        if "has_release_then_null_sequence" in safe:
            lines.append(
                "- Release-reset policy: a sibling `pattern-not: $P = NULL/nullptr` does not prove the reset occurs after the same release. Match a wider ordered release+reset safe block with the same `$P`, or keep the BAD trigger narrow/partial."
            )
        if "has_explicit_integer_cast" in safe:
            lines.append(
                "- Type-conversion policy: explicit casts are safe anchors. Semgrep metavariable names like `$INT` or `$FLOAT` are not type checks; use concrete type/cast syntax or `metavariable-type` where reliable."
            )
        if "has_plain_element_pointer_arithmetic" in safe:
            lines.append(
                "- Pointer-arithmetic policy: when GOOD uses plain element offsets and BAD uses size-based offsets, preserve the `sizeof(...)` token as the positive BAD signal instead of requiring a fully typed declaration context."
            )
    if analysis.get("bad_lines"):
        lines.append("- BAD signal lines: " + " | ".join(str(x) for x in analysis.get("bad_lines", [])[:16]))
    if analysis.get("bad_lines") or analysis.get("good_lines"):
        type_tokens = extract_type_tokens("\n".join([*(analysis.get("bad_lines") or []), *(analysis.get("good_lines") or [])]), limit=12)
        if type_tokens:
            lines.append("- Concrete C/C++ type tokens seen in examples: " + ", ".join(type_tokens))
            lines.append(
                "- Type-token policy: when a BAD carrier is parser-fragile with casts or pointer arithmetic, instantiate these concrete type alternatives directly in a small `pattern-either`; do not fall back to `$TYPE`/`$CAST` in type, cast, or `sizeof(...)` positions."
            )
    executable = analysis.get("executable_bad_signal_lines")
    if isinstance(executable, list) and executable:
        rendered = []
        families: set[str] = set()
        for item in executable[:14]:
            if not isinstance(item, dict):
                continue
            family = str(item.get("family") or "").strip()
            line = str(item.get("line") or "").strip()
            if family and line:
                families.add(family)
                rendered.append(f"{family}: {line}")
        if rendered:
            lines.append("- Executable BAD-token anchors: " + " | ".join(rendered))
            lines.append(
                "- Executable-anchor policy: translate these concrete token families into complete Semgrep statements/regexes before inventing extra declarations, helper assignments, or type-only metavariables."
            )
        carrier_shortlist: list[str] = []
        if "sizeof_in_pointer_offset" in families:
            carrier_shortlist.append("pointer-offset / sizeof carrier")
            lines.append(
                "- Pointer-offset policy: match the full assignment/write/call carrier around `sizeof(...)`; if the parseable AST shape is unstable, use a short line-local regex with concrete type names rather than `$TYPE` in the cast."
            )
        if "casted_pointer_write" in families:
            carrier_shortlist.append("casted write carrier")
            lines.append(
                "- Cast-write policy: preserve the casted write as the BAD core, but use concrete cast targets or a regex fallback around the whole write expression instead of a standalone cast metavariable."
            )
        if "casted_pointer_offset_carrier" in families:
            carrier_shortlist.append("casted pointer-offset read/initializer carrier")
            lines.append(
                "- Cast-offset policy: preserve the full casted pointer-offset read/initializer as its own branch; if paired GOOD uses the same cast with a safe offset expression, distinguish by the local offset expression rather than matching every cast."
            )
        if "sizeof_in_array_subscript" in families:
            carrier_shortlist.append("sizeof-scaled array-subscript carrier")
            lines.append(
                "- Array-subscript policy: match the full subscript carrier around `sizeof(...)`; do not use a bare `sizeof` or bare index-expression trigger."
            )
        if "alternate_view_member_or_index_write" in families:
            carrier_shortlist.append("alternate-view / index-write carrier")
        if "anonymous_record_declaration" in families:
            carrier_shortlist.append("anonymous record declaration carrier")
            lines.append(
                "- Anonymous-record policy: when an anonymous struct/union declaration is parser-fragile, keep the BAD carrier local and move the declaration portion to a short regex fallback if needed."
            )
        if carrier_shortlist:
            lines.append("- Carrier shortlist: " + "; ".join(carrier_shortlist))
            lines.append(
                "- Carrier policy: use the full outer statement/expression for the shortlisted family; do not promote the inner arithmetic, cast, or dereference fragment to the top-level trigger."
            )
    if analysis.get("good_lines"):
        lines.append("- GOOD/safe signal lines: " + " | ".join(str(x) for x in analysis.get("good_lines", [])[:16]))
    lines.extend(
        [
            "- Rule synthesis policy: first cover BAD-only features, then add distinguishing context for shared features.",
            "- Precision policy: when a high-recall branch has a few GOOD hits, preserve the branch and add narrow exclusions/guards for those GOOD contexts.",
            "- Locality policy: prefer evidence-backed local source/sink/operator/token coverage over abstract placeholders. Mark unsupported nonlocal relationships partial.",
        ]
    )
    return lines


def classify_eval_gaps(eval_report: dict[str, Any], rule_yaml_text: str = "") -> dict[str, Any]:
    missed = eval_report.get("missed_bad_examples") if isinstance(eval_report.get("missed_bad_examples"), list) else []
    flagged = eval_report.get("flagged_good_examples") if isinstance(eval_report.get("flagged_good_examples"), list) else []
    rule_text = str(rule_yaml_text or "")
    categories: dict[str, list[dict[str, Any]]] = {
        "missed_likely_semgrep_hard": [],
        "missed_likely_generation_coverage_gap": [],
        "false_positive_missing_safe_exclusion": [],
        "false_positive_overbroad_shared_feature": [],
    }

    for item in missed:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        text = read_item_text(item)
        flags = feature_flags(text)
        record = {"path": path, "features": [k for k, v in flags.items() if v]}
        if (
            flags.get("has_wrapper_call")
            or flags.get("has_pointer_subtraction")
            or flags.get("has_release_call")
            or flags.get("has_global_then_local_same_name_shape")
        ):
            categories["missed_likely_semgrep_hard"].append(record)
        elif flags.get("has_anonymous_nested_record"):
            categories["missed_likely_semgrep_hard"].append(record)
        elif flags.get("has_format_to_buffer") and "snprintf" not in rule_text and "sprintf" not in rule_text:
            categories["missed_likely_generation_coverage_gap"].append(record)
        elif flags.get("has_index_write") and "[" not in rule_text:
            categories["missed_likely_generation_coverage_gap"].append(record)
        else:
            categories["missed_likely_generation_coverage_gap"].append(record)

    for item in flagged:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        text = read_item_text(item)
        flags = feature_flags(text)
        record = {"path": path, "features": [k for k, v in flags.items() if v]}
        if flags.get("has_redaction_or_status_literals") or flags.get("has_explicit_cast") or flags.get("has_null_assignment") or flags.get("has_null_check"):
            categories["false_positive_missing_safe_exclusion"].append(record)
        else:
            categories["false_positive_overbroad_shared_feature"].append(record)

    summary = {key: len(value) for key, value in categories.items()}
    return {"summary": summary, "categories": categories}


def dumps_compact(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
