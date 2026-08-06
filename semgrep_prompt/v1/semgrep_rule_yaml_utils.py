#!/usr/bin/env python3
"""Semgrep YAML normalization helpers shared by generation pipelines."""

from __future__ import annotations

import copy
import json
import re
from typing import Any

import yaml


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:
        return True


def normalize_semgrep_operator_aliases(yaml_text: str) -> str:
    fixed = yaml_text
    fixed = re.sub(r"(?im)^(\s*(?:-\s*)?)patterns-either\s*:", r"\1pattern-either:", fixed)
    fixed = re.sub(r"(?im)^(\s*(?:-\s*)?)pattern-either-not\s*:", r"\1pattern-not:", fixed)
    fixed = re.sub(r"(?im)^(\s*(?:-\s*)?)pattern-not-either\s*:", r"\1pattern-not:", fixed)
    return fixed


def quote_problematic_plain_scalars(yaml_text: str) -> str:
    def _quote_match(match: re.Match[str]) -> str:
        prefix = match.group(1)
        value = match.group(2).strip()
        if not value or value[0] in {"'", '"', "|", ">", "{", "["}:
            return match.group(0)
        if ": " not in value and " #" not in value:
            return match.group(0)
        return prefix + json.dumps(value, ensure_ascii=False)

    return re.sub(
        r"(?m)^(\s*(?:message|id)\s*:\s*)([^#\n]*:\s+[^#\n]*)(?:\s*)$",
        _quote_match,
        yaml_text,
    )


def normalize_c_statement_pattern(pattern_text: str) -> str:
    text = str(pattern_text or "")
    stripped = text.strip()
    if not stripped or stripped.endswith(";") or "{" in stripped or "}" in stripped:
        return text
    if "\n" in stripped and "..." in stripped:
        return text
    looks_statement = bool(
        re.search(r"=", stripped)
        or re.match(
            r"^(?:const\s+)?(?:unsigned\s+)?(?:signed\s+)?(?:size_t|ptrdiff_t|int|long|char|wchar_t|short|float|double|bool|[A-Za-z_][A-Za-z0-9_]*\s*\*)\s+\$[A-Z]",
            stripped,
        )
    )
    if not looks_statement:
        return text
    return stripped + ";"


def dedupe_semgrep_pattern_lists(node: Any) -> Any:
    if isinstance(node, dict):
        normalized_dict = {key: dedupe_semgrep_pattern_lists(value) for key, value in node.items()}
        for pattern_key in ("pattern", "pattern-not"):
            value = normalized_dict.get(pattern_key)
            if isinstance(value, str):
                normalized_dict[pattern_key] = normalize_c_statement_pattern(value)
        patterns = normalized_dict.get("patterns")
        if isinstance(patterns, list):
            positive_patterns = {
                re.sub(r"\s+", " ", str(item.get("pattern") or "").strip())
                for item in patterns
                if isinstance(item, dict) and isinstance(item.get("pattern"), str)
            }
            if positive_patterns:
                filtered = []
                for item in patterns:
                    if isinstance(item, dict) and isinstance(item.get("pattern-not"), str):
                        not_key = re.sub(r"\s+", " ", str(item.get("pattern-not") or "").strip())
                        if not_key in positive_patterns:
                            continue
                    filtered.append(item)
                normalized_dict["patterns"] = filtered
        return normalized_dict
    if isinstance(node, list):
        out: list[Any] = []
        seen: set[str] = set()
        for item in node:
            normalized = dedupe_semgrep_pattern_lists(item)
            try:
                key = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
            except TypeError:
                key = repr(normalized)
            if key in seen:
                continue
            seen.add(key)
            out.append(normalized)
        return out
    return node


def hoist_single_pattern_either_from_patterns(node: Any) -> Any:
    if isinstance(node, dict):
        normalized = {key: hoist_single_pattern_either_from_patterns(value) for key, value in node.items()}
        rules = normalized.get("rules")
        if isinstance(rules, list):
            normalized["rules"] = [
                _hoist_single_pattern_either_in_rule(rule) if isinstance(rule, dict) else rule
                for rule in rules
            ]
        return normalized
    if isinstance(node, list):
        return [hoist_single_pattern_either_from_patterns(item) for item in node]
    return node


def _hoist_single_pattern_either_in_rule(rule: dict[str, Any]) -> dict[str, Any]:
    patterns = rule.get("patterns")
    if not isinstance(patterns, list) or len(patterns) != 1:
        return rule
    only = patterns[0]
    if not isinstance(only, dict):
        return rule
    branches = only.get("pattern-either")
    if not isinstance(branches, list):
        return rule
    extra_keys = set(only) - {"pattern-either"}
    if extra_keys:
        return rule
    if "pattern-either" in rule:
        return rule
    out = dict(rule)
    out.pop("patterns", None)
    out["pattern-either"] = branches
    return out


def flatten_nested_pattern_either_in_rules(node: Any) -> Any:
    if isinstance(node, dict):
        normalized = {key: flatten_nested_pattern_either_in_rules(value) for key, value in node.items()}
        rules = normalized.get("rules")
        if isinstance(rules, list):
            normalized["rules"] = [
                _flatten_nested_pattern_either_in_rule(rule) if isinstance(rule, dict) else rule
                for rule in rules
            ]
        return normalized
    if isinstance(node, list):
        return [flatten_nested_pattern_either_in_rules(item) for item in node]
    return node


def _flatten_nested_pattern_either_in_rule(rule: dict[str, Any]) -> dict[str, Any]:
    if str(rule.get("mode") or "").strip().lower() == "taint":
        return rule
    out = dict(rule)
    if isinstance(out.get("pattern-either"), list):
        flat: list[Any] = []
        changed = False
        for branch in out.get("pattern-either", []):
            expanded = _expand_patterns_branch(branch)
            flat.extend(expanded)
            changed = changed or len(expanded) != 1 or expanded[0] != branch
        if changed and len(flat) <= 48:
            out["pattern-either"] = flat
    elif isinstance(out.get("patterns"), list):
        expanded = _expand_patterns_branch({"patterns": out.get("patterns")})
        if len(expanded) > 1 and len(expanded) <= 48:
            out.pop("patterns", None)
            out["pattern-either"] = expanded
    return out


def _expand_patterns_branch(branch: Any) -> list[Any]:
    if not isinstance(branch, dict):
        return [branch]
    patterns = branch.get("patterns")
    if not isinstance(patterns, list):
        return [branch]

    combinations: list[list[Any]] = [[]]
    changed = False
    for item in patterns:
        if isinstance(item, dict) and isinstance(item.get("pattern-either"), list):
            changed = True
            choices: list[list[Any]] = []
            for child in item.get("pattern-either", []):
                if isinstance(child, dict) and isinstance(child.get("patterns"), list):
                    choices.append(child.get("patterns", []))
                else:
                    choices.append([child])
            next_combinations: list[list[Any]] = []
            for prefix in combinations:
                for choice in choices:
                    next_combinations.append([copy.deepcopy(x) for x in prefix + choice])
                    if len(next_combinations) > 48:
                        return [branch]
            combinations = next_combinations
            continue
        combinations = [[*prefix, copy.deepcopy(item)] for prefix in combinations]

    if not changed:
        return [branch]

    rest = {key: value for key, value in branch.items() if key != "patterns"}
    return [{**rest, "patterns": combo} for combo in combinations]


def normalize_yaml_structure(yaml_text: str) -> str:
    try:
        payload = yaml.safe_load(yaml_text)
    except Exception:
        return yaml_text
    if not isinstance(payload, dict):
        return yaml_text
    normalized = flatten_nested_pattern_either_in_rules(hoist_single_pattern_either_from_patterns(dedupe_semgrep_pattern_lists(payload)))
    try:
        return yaml.dump(normalized, Dumper=NoAliasSafeDumper, allow_unicode=True, sort_keys=False)
    except Exception:
        return yaml_text


def normalize_yaml(yaml_text: str) -> str:
    fixed = normalize_semgrep_operator_aliases((yaml_text or "").strip() + "\n")
    fixed = quote_problematic_plain_scalars(fixed)
    fixed = re.sub(
        r"(?im)^(\s*severity\s*:\s*)(error|warning|info|critical|high|medium|low)\s*$",
        lambda m: f"{m.group(1)}{m.group(2).upper()}",
        fixed,
    )
    fixed = normalize_yaml_structure(fixed)
    return fixed.strip() + "\n"
