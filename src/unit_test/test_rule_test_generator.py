import json
import re
import threading
import time
from pathlib import Path

import pytest

from input_processing import test_generator
from input_processing.test_generator import LanguageValidator, generate_rule_tests


def test_rule_workers_respect_llm_concurrency_and_preserve_order(tmp_path: Path):
    rules_path = tmp_path / "rules.json"
    output_dir = tmp_path / "test_cases"
    output_rules = tmp_path / "rules_with_tests.json"
    rules = [
        {
            "rule_id": f"S-{index}",
            "main_title": f"concurrent-rule-{index}",
            "description": f"rule {index}",
            "rule_type": "required",
            "examples": [],
            "rule_test_path": "",
        }
        for index in range(1, 5)
    ]
    rules_path.write_text(json.dumps({"data": {"sample": rules}}), encoding="utf-8")
    lock = threading.Lock()
    active_calls = 0
    max_active_calls = 0

    def fake_invoke(prompt: str, system: str) -> str:
        nonlocal active_calls, max_active_calls
        with lock:
            active_calls += 1
            max_active_calls = max(max_active_calls, active_calls)
        try:
            time.sleep(0.03)
            if "可行性评估Agent" in system:
                return json.dumps({"status": "supported", "reason": "supported"})
            title = re.search(r'"main_title": "([^"]+)"', prompt).group(1)
            number = title.rsplit("-", 1)[1]
            cases = []
            for case_id in re.findall(r'"case_id": "((?:negative|positive)_\d+)"', prompt):
                polarity = case_id.split("_", 1)[0]
                code = f"value_{number}_{case_id} = {number}"
                if polarity == "negative":
                    code += (
                        "  # CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: "
                        f"{{{{.*}}}} [sample-s-{number}]"
                    )
                cases.append({"case_id": case_id, "intent": case_id, "code": code})
            return json.dumps({"cases": cases})
        finally:
            with lock:
                active_calls -= 1

    summary = generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="python",
        negative_count=1,
        positive_count=1,
        batch_size=2,
        workers=4,
        llm_concurrency=2,
        invoke=fake_invoke,
    )

    assert summary["completed_rule_count"] == 4
    assert summary["failed_rule_count"] == 0
    assert max_active_calls == 2
    report = json.loads((output_dir / "generation_report.json").read_text())
    assert report["workers"] == 4
    assert report["llm_concurrency"] == 2
    assert [item["main_title"] for item in report["rules"]] == [
        f"concurrent-rule-{index}" for index in range(1, 5)
    ]


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("c", ["-std=c11", "-fsyntax-only"]),
        ("cpp", ["-std=c++17", "-fsyntax-only"]),
        ("python", ["-m", "py_compile"]),
        ("java", ["-proc:none", "-d"]),
    ],
)
def test_language_validator_commands(
    tmp_path: Path, monkeypatch, language: str, expected: list[str]
):
    commands = []

    def fake_which(name: str):
        return f"/tools/{name}"

    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        commands.append(command)
        return Completed()

    monkeypatch.setattr(test_generator.shutil, "which", fake_which)
    monkeypatch.setattr(test_generator.subprocess, "run", fake_run)
    validator = LanguageValidator(language)
    source = tmp_path / f"case{validator.extension}"
    source.write_text("", encoding="utf-8")

    result = validator.validate(source)

    assert result.success
    assert all(item in commands[0] for item in expected)


def test_generate_repair_and_resume_python_cases(tmp_path: Path):
    rules_path = tmp_path / "rules.json"
    output_dir = tmp_path / "test_cases"
    output_rules = tmp_path / "rules_with_tests.json"
    rules_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {
                            "rule_id": "S-1",
                            "main_title": "do-not-use-eval",
                            "description": "不得使用 eval 执行不可信输入。",
                            "rule_type": "required",
                            "source_chunks": ["chunk-0001"],
                            "examples": [],
                            "rule_test_path": "",
                        }
                    ]
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    calls = []

    def fake_invoke(prompt: str, system: str) -> str:
        calls.append(system)
        if "可行性评估Agent" in system:
            return json.dumps(
                {"status": "supported", "reason": "存在可编译的单文件负例"},
                ensure_ascii=False,
            )
        if "代码修复 Agent" in system:
            return json.dumps(
                {
                    "code": "def insecure(value):\n    return eval(value)  # CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [sample-s-1]"
                },
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "cases": [
                    {
                        "case_id": "negative_01",
                        "intent": "直接调用 eval",
                        "code": "def insecure(:\n    return eval(value)  # CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [sample-s-1]",
                    },
                    {
                        "case_id": "positive_01",
                        "intent": "使用整数转换代替 eval",
                        "code": "def safe(value):\n    return int(value)",
                    },
                ]
            },
            ensure_ascii=False,
        )

    summary = generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="python",
        negative_count=1,
        positive_count=1,
        batch_size=2,
        max_repair_attempts=2,
        invoke=fake_invoke,
    )

    assert summary["completed_rule_count"] == 1
    assert summary["failed_rule_count"] == 0
    assert len(calls) == 3
    rule_dir = output_dir / "do-not-use-eval"
    assert (rule_dir / "negative_01.py").exists()
    assert (rule_dir / "positive_01.py").exists()
    assert "CHECK-MESSAGES" in (rule_dir / "negative_01.py").read_text()
    assert "CHECK-MESSAGES" not in (rule_dir / "positive_01.py").read_text()
    output = json.loads(output_rules.read_text(encoding="utf-8"))
    rule = output["data"]["sample"][0]
    assert rule["rule_test_path"] == str(rule_dir.resolve())
    assert rule["negative_case_amount"] == 1
    assert rule["positive_case_amount"] == 1

    generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="python",
        negative_count=1,
        positive_count=1,
        batch_size=2,
        max_repair_attempts=2,
        invoke=fake_invoke,
    )
    assert len(calls) == 3


def test_invoke_json_retries_timeout(monkeypatch):
    attempts = 0

    def flaky_invoke(prompt: str, system: str) -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError("temporary timeout")
        return '{"cases": []}'

    monkeypatch.setattr(test_generator.time, "sleep", lambda _: None)
    monkeypatch.setattr(test_generator.random, "uniform", lambda _a, _b: 0)

    payload, _ = test_generator._invoke_json(
        flaky_invoke,
        "prompt",
        "system",
        retries=3,
        retry_base_delay=0,
        retry_max_delay=0,
        phase="test",
    )

    assert payload == {"cases": []}
    assert attempts == 3


def test_rule_failure_is_recorded_and_next_rule_continues(tmp_path: Path):
    rules_path = tmp_path / "rules.json"
    output_dir = tmp_path / "test_cases"
    output_rules = tmp_path / "rules_with_tests.json"
    rules_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {
                            "rule_id": "S-1",
                            "main_title": "first-rule-fails",
                            "description": "first",
                            "rule_type": "required",
                            "examples": [],
                            "rule_test_path": "",
                        },
                        {
                            "rule_id": "S-2",
                            "main_title": "second-rule-succeeds",
                            "description": "second",
                            "rule_type": "required",
                            "examples": [],
                            "rule_test_path": "",
                        },
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    def fake_invoke(prompt: str, system: str) -> str:
        if "first-rule-fails" in prompt:
            raise RuntimeError("permanent provider error")
        if "可行性评估Agent" in system:
            return json.dumps(
                {"status": "supported", "reason": "存在可编译的单文件负例"}
            )
        return json.dumps(
            {
                "cases": [
                    {
                        "case_id": "negative_01",
                        "intent": "negative",
                        "code": "value = 1  # CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [sample-s-2]",
                    },
                    {
                        "case_id": "positive_01",
                        "intent": "positive",
                        "code": "value = 2",
                    },
                ]
            }
        )

    summary = generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="python",
        negative_count=1,
        positive_count=1,
        batch_size=2,
        max_repair_attempts=0,
        invoke=fake_invoke,
        retry_base_delay=0,
        retry_max_delay=0,
    )

    assert summary["completed_rule_count"] == 1
    assert summary["failed_rule_count"] == 1
    output = json.loads(output_rules.read_text(encoding="utf-8"))
    assert output["data"]["sample"][0]["rule_test_path"] == ""
    assert output["data"]["sample"][1]["negative_case_amount"] == 1
    report = json.loads((output_dir / "generation_report.json").read_text())
    assert report["status"] == "completed"
    assert report["rules"][0]["error_type"] == "RuntimeError"
    assert report["rules"][1]["success"] is True


@pytest.mark.parametrize(
    ("status", "expected_error"),
    [
        ("requires_multiple_files", "unsupported_single_file"),
        ("compile_error_only", "compile_valid_negative_not_possible"),
    ],
)
def test_feasibility_stops_rule_before_generation_and_resumes(
    tmp_path: Path, status: str, expected_error: str
):
    rules_path = tmp_path / "rules.json"
    output_dir = tmp_path / "test_cases"
    output_rules = tmp_path / "rules_with_tests.json"
    rules_path.write_text(
        json.dumps(
            {
                "data": {
                    "sample": [
                        {
                            "rule_id": "S-1",
                            "main_title": "unsupported-rule",
                            "description": "rule",
                            "rule_type": "required",
                            "examples": [],
                            "rule_test_path": "",
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    calls = []

    def fake_invoke(prompt: str, system: str) -> str:
        calls.append(system)
        assert "可行性评估Agent" in system
        return json.dumps({"status": status, "reason": "not supported"})

    first = generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="cpp",
        negative_count=1,
        positive_count=1,
        invoke=fake_invoke,
    )
    second = generate_rule_tests(
        rules_path,
        output_dir,
        output_rules,
        language="cpp",
        negative_count=1,
        positive_count=1,
        invoke=fake_invoke,
    )

    assert first["failed_rule_count"] == 1
    assert second["failed_rule_count"] == 1
    assert len(calls) == 1
    report = json.loads((output_dir / "generation_report.json").read_text())
    item = report["rules"][0]
    assert item["feasibility_status"] == status
    assert item["error_type"] == expected_error
    assert item["generation_rounds"] == 0
    assert not list(output_dir.glob("unsupported-rule/*"))
