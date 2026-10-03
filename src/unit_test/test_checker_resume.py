import json

import pytest

from generator import parse_logic_response
from main import load_checkpoint, should_skip_checkpoint, upsert_completed_rule


def test_parse_logic_response_requires_expected_non_empty_schema():
    valid = json.dumps(
        [
            {
                "logic_registerMatchers": ["match a declaration"],
                "logic_check": ["diagnose the bound declaration"],
            }
        ]
    )
    assert parse_logic_response(valid)[0]["logic_check"]

    for invalid in ("", "[]", "{}", '[{"logic_registerMatchers": []}]'):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_logic_response(invalid)


def test_checkpoint_load_upsert_and_skip_policy(tmp_path):
    rule_data = {
        "data": {
            "sample": [
                {"rule_id": "R-1", "main_title": "one"},
                {"rule_id": "R-2", "main_title": "two"},
            ]
        }
    }
    checkpoint_path = tmp_path / "checker_generation_result.json"
    checkpoint_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {"rule_id": "R-1", "issuccess": "True"},
                        {"rule_id": "R-2"},
                        {"rule_id": "OLD", "issuccess": "True"},
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    checkpoint = load_checkpoint(rule_data, str(checkpoint_path), resume=True)
    assert [item["rule_id"] for item in checkpoint["data"]["sample"]] == ["R-1"]
    assert should_skip_checkpoint(checkpoint["data"]["sample"][0], False)

    failed = {"rule_id": "R-2", "main_title": "two", "issuccess": "False"}
    upsert_completed_rule(checkpoint, rule_data, "sample", failed)
    assert [item["rule_id"] for item in checkpoint["data"]["sample"]] == [
        "R-1",
        "R-2",
    ]
    assert should_skip_checkpoint(failed, retry_failed=False)
    assert not should_skip_checkpoint(failed, retry_failed=True)
