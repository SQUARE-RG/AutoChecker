from __future__ import annotations

from .schemas import RuleCandidate


def build_autochecker_rules(rules: list[RuleCandidate], *, category: str) -> dict:
    return {
        "data": {
            category: [
                {
                    "rule_id": rule.rule_id,
                    "main_title": rule.main_title,
                    "description": rule.description,
                    "rule_type": rule.rule_type,
                    "source_chunks": rule.source_chunks,
                    "examples": [example.to_dict() for example in rule.examples],
                    "rule_test_path": "",
                }
                for rule in rules
            ]
        }
    }
