import json
from pathlib import Path

from scripts.filter_clang_tidy_rules import filter_clang_tidy_rules


def _write_cases(directory: Path, *, negative: int, positive: int) -> None:
    directory.mkdir(parents=True)
    for index in range(negative):
        (directory / f"negative_{index + 1:02d}.cpp").write_text(
            "int main() { return 0; } // CHECK-MESSAGES: warning\n",
            encoding="utf-8",
        )
    for index in range(positive):
        (directory / f"positive_{index + 1:02d}.cpp").write_text(
            "int main() { return 0; }\n", encoding="utf-8"
        )


def test_filter_selects_complete_rules_and_adds_category(tmp_path: Path):
    complete = tmp_path / "complete"
    incomplete = tmp_path / "incomplete"
    _write_cases(complete, negative=1, positive=1)
    _write_cases(incomplete, negative=1, positive=0)
    rules_path = tmp_path / "rules.json"
    output_path = tmp_path / "supported.json"
    report_path = tmp_path / "report.json"
    rules_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {
                            "rule_id": "S-1",
                            "main_title": "complete-rule",
                            "description": "complete",
                            "rule_test_path": str(complete),
                        },
                        {
                            "rule_id": "S-2",
                            "main_title": "incomplete-rule",
                            "description": "incomplete",
                            "rule_test_path": str(incomplete),
                        },
                        {
                            "rule_id": "S-3",
                            "main_title": "missing-rule",
                            "description": "missing path",
                            "rule_test_path": "",
                        },
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = filter_clang_tidy_rules(
        rules_path,
        output_path,
        report_path,
        expected_negative=1,
        expected_positive=1,
    )

    assert report["supported_rule_count"] == 1
    assert report["excluded_rule_count"] == 2
    output = json.loads(output_path.read_text(encoding="utf-8"))
    selected = output["data"]["sample"][0]
    assert selected["main_title"] == "complete-rule"
    assert selected["category"] == "sample"
    assert selected["negative_case_amount"] == 1
    assert selected["positive_case_amount"] == 1
    reasons = {reason for item in report["excluded"] for reason in item["reasons"]}
    assert "unexpected_positive_case_count" in reasons
    assert "empty_rule_test_path" in reasons


def test_filter_reports_quality_warnings_without_excluding(tmp_path: Path):
    cases = tmp_path / "cases"
    cases.mkdir()
    (cases / "negative.cpp").write_text(
        '#include "vector"\n#if 0\nint hidden;\n#endif\n'
        "int main() { return 0; } // CHECK-MESSAGES: warning\n",
        encoding="utf-8",
    )
    (cases / "positive.cpp").write_text(
        "int main() { return 0; }\n", encoding="utf-8"
    )
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {
                            "rule_id": "S-1",
                            "main_title": "warning-rule",
                            "description": "warning",
                            "rule_test_path": str(cases),
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = filter_clang_tidy_rules(
        rules_path,
        tmp_path / "output.json",
        tmp_path / "report.json",
        expected_negative=1,
        expected_positive=1,
    )

    assert report["supported_rule_count"] == 1
    assert report["warning_rule_count"] == 1
    assert report["included"][0]["warnings"] == [
        "quoted_include_present",
        "if_zero_present",
    ]
