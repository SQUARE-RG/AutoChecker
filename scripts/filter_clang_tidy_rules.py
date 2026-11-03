#!/usr/bin/env python3
"""Filter Stage-3 rules into an input accepted by the Clang-Tidy generator."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES = (
    PROJECT_ROOT / "experiment/gjb8114-all/gjb8114_rules_with_tests.json"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json"
)
DEFAULT_REPORT = (
    PROJECT_ROOT
    / "experiment/gjb8114-all/gjb8114_clang_tidy_filter_report.json"
)

SAFE_TITLE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LOCAL_INCLUDE = re.compile(r'^\s*#\s*include\s*"[^"]+"', re.MULTILINE)
DISABLED_CODE = re.compile(r"^\s*#\s*if\s+0(?:\s|$)", re.MULTILINE)
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".c++"}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Rules file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Rules JSON root must be an object")
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _resolve_test_dir(raw_path: str, rules_path: Path) -> Path:
    test_dir = Path(raw_path).expanduser()
    if not test_dir.is_absolute():
        test_dir = rules_path.parent / test_dir
    return test_dir.resolve()


def _inspect_rule(
    rule: Any,
    *,
    category: str,
    rules_path: Path,
    expected_negative: int,
    expected_positive: int,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(rule, dict):
        return None, {
            "category": category,
            "rule_id": None,
            "main_title": None,
            "reasons": ["rule_not_object"],
            "warnings": [],
        }

    rule_id = str(rule.get("rule_id") or "").strip()
    main_title = str(rule.get("main_title") or "").strip()
    reasons: list[str] = []
    warnings: list[str] = []

    if not rule_id:
        reasons.append("missing_rule_id")
    if not main_title:
        reasons.append("missing_main_title")
    elif not SAFE_TITLE.fullmatch(main_title):
        reasons.append("invalid_main_title")
    if not str(rule.get("description") or "").strip():
        reasons.append("missing_description")

    raw_test_path = str(rule.get("rule_test_path") or "").strip()
    if not raw_test_path:
        reasons.append("empty_rule_test_path")
        test_dir = None
    else:
        test_dir = _resolve_test_dir(raw_test_path, rules_path)
        if not test_dir.is_dir():
            reasons.append("test_directory_not_found")

    cpp_files: list[Path] = []
    negative_count = 0
    positive_count = 0
    quoted_include_files: list[str] = []
    disabled_code_files: list[str] = []
    if test_dir is not None and test_dir.is_dir():
        cpp_files = sorted(
            path for path in test_dir.iterdir() if path.is_file() and path.suffix == ".cpp"
        )
        other_sources = sorted(
            path.name
            for path in test_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in SOURCE_SUFFIXES
            and path.suffix != ".cpp"
        )
        if other_sources:
            reasons.append("unsupported_source_extension")

        for source in cpp_files:
            try:
                content = source.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                reasons.append("unreadable_cpp_file")
                continue
            if "CHECK-MESSAGES" in content:
                negative_count += 1
            else:
                positive_count += 1
            if LOCAL_INCLUDE.search(content):
                quoted_include_files.append(source.name)
            if DISABLED_CODE.search(content):
                disabled_code_files.append(source.name)

        if negative_count != expected_negative:
            reasons.append("unexpected_negative_case_count")
        if positive_count != expected_positive:
            reasons.append("unexpected_positive_case_count")
        if len(cpp_files) != expected_negative + expected_positive:
            reasons.append("unexpected_cpp_file_count")

    if quoted_include_files:
        warnings.append("quoted_include_present")
    if disabled_code_files:
        warnings.append("if_zero_present")

    detail: dict[str, Any] = {
        "category": category,
        "rule_id": rule_id or None,
        "main_title": main_title or None,
        "rule_test_path": str(test_dir) if test_dir is not None else "",
        "cpp_file_count": len(cpp_files),
        "negative_case_amount": negative_count,
        "positive_case_amount": positive_count,
        "reasons": list(dict.fromkeys(reasons)),
        "warnings": warnings,
    }
    if quoted_include_files:
        detail["quoted_include_files"] = quoted_include_files
    if disabled_code_files:
        detail["if_zero_files"] = disabled_code_files

    if reasons:
        return None, detail

    selected = deepcopy(rule)
    selected["category"] = category
    selected["rule_test_path"] = str(test_dir)
    selected["negative_case_amount"] = negative_count
    selected["positive_case_amount"] = positive_count
    return selected, detail


def filter_clang_tidy_rules(
    rules_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    expected_negative: int = 10,
    expected_positive: int = 10,
) -> dict[str, Any]:
    if expected_negative < 1 or expected_positive < 1:
        raise ValueError("Expected positive and negative counts must both be positive")

    rules_path = rules_path.resolve()
    output_path = output_path.resolve()
    report_path = report_path.resolve()
    if output_path == rules_path:
        raise ValueError("Output file must not overwrite the input rules file")
    if report_path in {rules_path, output_path}:
        raise ValueError("Report path must differ from input and output paths")

    payload = _read_json(rules_path)
    categories = payload.get("data")
    if not isinstance(categories, dict):
        raise ValueError("Rules JSON must contain an object field 'data'")

    output: dict[str, Any] = {"data": {}}
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    seen_rule_ids: set[str] = set()
    seen_titles: set[str] = set()

    for category, rules in categories.items():
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category names must be non-empty strings")
        if not isinstance(rules, list):
            raise ValueError(f"Category {category!r} must contain a rule array")
        selected_rules: list[dict[str, Any]] = []
        for rule in rules:
            selected, detail = _inspect_rule(
                rule,
                category=category,
                rules_path=rules_path,
                expected_negative=expected_negative,
                expected_positive=expected_positive,
            )
            rule_id = detail.get("rule_id")
            main_title = detail.get("main_title")
            duplicate_reasons = []
            if rule_id and rule_id in seen_rule_ids:
                duplicate_reasons.append("duplicate_rule_id")
            if main_title and main_title in seen_titles:
                duplicate_reasons.append("duplicate_main_title")
            if rule_id:
                seen_rule_ids.add(rule_id)
            if main_title:
                seen_titles.add(main_title)
            if duplicate_reasons:
                detail["reasons"].extend(duplicate_reasons)
                selected = None

            if selected is None:
                excluded.append(detail)
            else:
                selected_rules.append(selected)
                included.append(detail)
        output["data"][category] = selected_rules

    warning_rule_count = sum(bool(item["warnings"]) for item in included)
    report = {
        "schema_version": 1,
        "input_rules": str(rules_path),
        "output_rules": str(output_path),
        "expected_negative_case_amount": expected_negative,
        "expected_positive_case_amount": expected_positive,
        "total_rule_count": len(included) + len(excluded),
        "supported_rule_count": len(included),
        "excluded_rule_count": len(excluded),
        "warning_rule_count": warning_rule_count,
        "included": included,
        "excluded": excluded,
    }
    _write_json_atomic(output_path, output)
    _write_json_atomic(report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Filter validated Stage-3 C++ test suites into rules accepted by "
            "the AutoChecker Clang-Tidy generator."
        )
    )
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--output-rules", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--negative-count", type=int, default=10)
    parser.add_argument("--positive-count", type=int, default=10)
    args = parser.parse_args()

    report = filter_clang_tidy_rules(
        args.rules,
        args.output_rules,
        args.report,
        expected_negative=args.negative_count,
        expected_positive=args.positive_count,
    )
    print(
        json.dumps(
            {
                "total_rule_count": report["total_rule_count"],
                "supported_rule_count": report["supported_rule_count"],
                "excluded_rule_count": report["excluded_rule_count"],
                "warning_rule_count": report["warning_rule_count"],
                "output_rules": report["output_rules"],
                "report": str(args.report.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
