from __future__ import annotations

import re
from difflib import SequenceMatcher

from .schemas import RuleCandidate, RuleExample


def merge_rules(rules: list[RuleCandidate]) -> list[RuleCandidate]:
    merged: list[RuleCandidate] = []
    for candidate in rules:
        duplicate = next((item for item in merged if _same_rule(item, candidate)), None)
        if duplicate is None:
            merged.append(candidate)
        else:
            _merge_into(duplicate, candidate)
    _make_titles_unique(merged)
    return merged


def _same_rule(left: RuleCandidate, right: RuleCandidate) -> bool:
    if left.rule_id and right.rule_id:
        return _normalize_id(left.rule_id) == _normalize_id(right.rule_id)
    if left.rule_id or right.rule_id:
        return False
    if left.main_title == right.main_title:
        return True
    return SequenceMatcher(
        None, _normalize(left.description), _normalize(right.description)
    ).ratio() >= 0.9


def _merge_into(target: RuleCandidate, source: RuleCandidate) -> None:
    if _descriptions_are_distinct(target.description, source.description):
        target.description = _combine_descriptions(target.description, source.description)
        target.main_title = _combine_titles(target.main_title, source.main_title)
    elif len(source.description) > len(target.description):
        target.description = source.description
        target.main_title = source.main_title

    if source.rule_type == "required":
        target.rule_type = "required"
    target.source_chunks = sorted(set(target.source_chunks) | set(source.source_chunks))
    target.examples = _merge_examples(target.examples, source.examples)


def _merge_examples(
    target: list[RuleExample], source: list[RuleExample]
) -> list[RuleExample]:
    merged = list(target)
    seen = {_example_key(example) for example in merged}
    for example in source:
        key = _example_key(example)
        if key not in seen:
            merged.append(example)
            seen.add(key)
    return merged


def _example_key(example: RuleExample) -> tuple[str, str]:
    return example.type, re.sub(r"\s+", "", example.code)


def _make_titles_unique(rules: list[RuleCandidate]) -> None:
    used: dict[str, int] = {}
    for rule in rules:
        base = rule.main_title
        used[base] = used.get(base, 0) + 1
        if used[base] > 1:
            suffix = _normalize_id(rule.rule_id or str(used[base])).lower()
            suffix = re.sub(r"[^a-z0-9]+", "-", suffix).strip("-") or str(used[base])
            rule.main_title = f"{base}-{suffix}"


def _descriptions_are_distinct(left: str, right: str) -> bool:
    normalized_left, normalized_right = _normalize(left), _normalize(right)
    if not normalized_left or not normalized_right:
        return False
    if normalized_left in normalized_right or normalized_right in normalized_left:
        return False
    return SequenceMatcher(None, normalized_left, normalized_right).ratio() < 0.8


def _combine_descriptions(left: str, right: str) -> str:
    left = left.strip().rstrip("。；;，,")
    right = right.strip()
    return f"{left}；同时，{right}"


def _combine_titles(left: str, right: str) -> str:
    if left == right:
        return left
    left_parts, right_parts = left.split("-"), right.split("-")
    common_length = 0
    for left_part, right_part in zip(left_parts, right_parts):
        if left_part != right_part:
            break
        common_length += 1
    if common_length:
        parts = (
            left_parts[:common_length]
            + left_parts[common_length:]
            + ["and"]
            + right_parts[common_length:]
        )
    else:
        parts = left_parts + ["and"] + right_parts
    return "-".join(part for part in parts if part)


def _normalize(value: str) -> str:
    return re.sub(r"[\W_]+", "", value or "", flags=re.UNICODE).lower()


def _normalize_id(value: str) -> str:
    return re.sub(r"\s+", "", value).upper()
