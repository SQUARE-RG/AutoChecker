import json
from pathlib import Path

import pytest

from scripts import classify_clang_tidy_rules as classifier


def test_classify_rules_creates_complete_disjoint_partitions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(classifier, "PREPROCESSOR_RULES", {"preprocessor-rule"})
    monkeypatch.setattr(classifier, "DATAFLOW_RULES", {"dataflow-rule"})
    monkeypatch.setattr(classifier, "REVIEW_RULES", {"review-rule"})
    rules = [
        {"rule_id": "S-1", "main_title": "ast-rule"},
        {"rule_id": "S-2", "main_title": "preprocessor-rule"},
        {"rule_id": "S-3", "main_title": "dataflow-rule"},
        {"rule_id": "S-4", "main_title": "review-rule"},
    ]
    input_path = tmp_path / "rules.json"
    input_path.write_text(
        json.dumps({"data": {"sample": rules}}), encoding="utf-8"
    )

    summary = classifier.classify_rules(input_path, tmp_path / "output")

    assert summary["total_rule_count"] == 4
    assert summary["counts"] == {
        "ast": 1,
        "preprocessor": 1,
        "dataflow": 1,
        "review": 1,
    }
    observed = set()
    for path in summary["outputs"].values():
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        titles = {item["main_title"] for item in payload["data"]["sample"]}
        assert observed.isdisjoint(titles)
        observed.update(titles)
    assert observed == {item["main_title"] for item in rules}


def test_classify_rules_rejects_stale_capability_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(classifier, "PREPROCESSOR_RULES", {"missing-rule"})
    monkeypatch.setattr(classifier, "DATAFLOW_RULES", set())
    monkeypatch.setattr(classifier, "REVIEW_RULES", set())
    input_path = tmp_path / "rules.json"
    input_path.write_text(
        json.dumps({"data": {"sample": [{"main_title": "ast-rule"}]}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="absent from the input"):
        classifier.classify_rules(input_path, tmp_path / "output")
