from __future__ import annotations

import re
from typing import Iterable

from .schemas import DocumentBlock, RuleCandidate


RULE_ID_PATTERN = re.compile(r"\b(R\s*[-：:]?\s*\d+(?:[-.]\w+)+)\b", re.I)


def reconcile_inventory(
    blocks: list[DocumentBlock], rules: list[RuleCandidate], inventory_pages: Iterable[int]
) -> dict:
    pages = sorted(set(inventory_pages))
    if not pages:
        return {
            "status": "skipped",
            "reason": "inventory pages were not specified",
            "inventory_rule_ids": [],
            "missing_from_extraction": [],
            "extracted_without_inventory_id": [],
        }
    inventory_ids = set()
    for block in blocks:
        if block.page not in pages:
            continue
        inventory_ids.update(
            _normalize_id(match.group(1)) for match in RULE_ID_PATTERN.finditer(block.text)
        )
    extracted_ids = {
        _normalize_id(rule.rule_id)
        for rule in rules
        if rule.rule_id
    }
    return {
        "status": "completed",
        "inventory_pages": pages,
        "inventory_rule_ids": sorted(inventory_ids),
        "missing_from_extraction": sorted(inventory_ids - extracted_ids),
        "extracted_without_inventory_id": [
            rule.main_title
            for rule in rules
            if not rule.rule_id or _normalize_id(rule.rule_id) not in inventory_ids
        ],
    }


def _normalize_id(value: str) -> str:
    return re.sub(r"\s+", "", value).upper()
