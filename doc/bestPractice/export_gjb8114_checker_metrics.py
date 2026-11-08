#!/usr/bin/env python3
"""Export per-checker GJB 8114 generation and test metrics to Excel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS = (
    PROJECT_ROOT
    / "result_generation/clang-tidy/gjb8114_security_rules/checker_generation_result.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "doc/bestPractice/GJB8114-checker-metrics.xlsx"


def _is_success(rule: dict[str, Any]) -> bool:
    return str(rule.get("issuccess", "")).lower() == "true"


def _case_is_violation(path: Path) -> bool:
    return "CHECK-MESSAGES" in path.read_text(encoding="utf-8")


def collect_metrics(results_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    categories = payload.get("data")
    if not isinstance(categories, dict):
        raise ValueError("Result JSON must contain an object field 'data'")

    rows: list[dict[str, Any]] = []
    for category, rules in categories.items():
        if not isinstance(rules, list):
            raise ValueError(f"Category {category!r} must contain a rule array")
        for rule in rules:
            if not _is_success(rule):
                continue

            test_dir = Path(str(rule["rule_test_path"])).resolve()
            test_files = sorted(test_dir.glob("*.cpp"))
            successful = {str(Path(path).resolve()) for path in rule.get("success_case_list", [])}
            failed = {str(Path(path).resolve()) for path in rule.get("failed_case_list", [])}
            actual = {str(path.resolve()) for path in test_files}
            if successful & failed:
                raise ValueError(f"Overlapping test results for {rule['main_title']}")
            if successful | failed != actual:
                raise ValueError(f"Incomplete test results for {rule['main_title']}")

            tp = tn = fp = fn = 0
            for test_file in test_files:
                path = str(test_file.resolve())
                violation = _case_is_violation(test_file)
                correctly_classified = path in successful
                if violation and correctly_classified:
                    tp += 1
                elif violation:
                    fn += 1
                elif correctly_classified:
                    tn += 1
                else:
                    fp += 1

            usage = rule.get("usage") or {}
            precision = tp / (tp + fp) if tp + fp else None
            recall = tp / (tp + fn) if tp + fn else None
            specificity = tn / (tn + fp) if tn + fp else None
            accuracy = (tp + tn) / len(test_files) if test_files else None
            f1 = (
                2 * precision * recall / (precision + recall)
                if precision is not None and recall is not None and precision + recall
                else None
            )
            rows.append(
                {
                    "category": category,
                    "rule_id": rule.get("rule_id"),
                    "main_title": rule.get("main_title"),
                    "llm_calls": int(usage.get("llm_calls", 0)),
                    "time_seconds": float(rule.get("time", 0)),
                    "time_minutes": float(rule.get("time", 0)) / 60,
                    "cost_cny": float(usage.get("total_cost", 0)),
                    "tp": tp,
                    "tn": tn,
                    "fp": fp,
                    "fn": fn,
                    "precision": precision,
                    "recall": recall,
                    "specificity": specificity,
                    "accuracy": accuracy,
                    "f1": f1,
                    "performance": rule.get("performance"),
                    "test_suite": str(test_dir),
                }
            )
    return rows


def _style_header(worksheet, row: int = 1) -> None:
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in worksheet[row]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")


def write_workbook(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise ValueError("No successful checker results found")

    workbook = Workbook()
    workbook.properties.title = "GJB 8114 Clang-Tidy Checker Metrics"
    workbook.properties.subject = "Per-rule LLM usage, time, cost, and confusion matrix"
    summary = workbook.active
    summary.title = "Summary"

    count = len(rows)
    total_calls = sum(row["llm_calls"] for row in rows)
    total_time = sum(row["time_seconds"] for row in rows)
    total_cost = sum(row["cost_cny"] for row in rows)
    total_tp = sum(row["tp"] for row in rows)
    total_tn = sum(row["tn"] for row in rows)
    total_fp = sum(row["fp"] for row in rows)
    total_fn = sum(row["fn"] for row in rows)
    total_tests = total_tp + total_tn + total_fp + total_fn

    summary_rows = [
        ["Metric", "Total", "Average per Checker", "Unit/Definition"],
        ["Successful Checkers", count, None, "checker"],
        ["Test Cases", total_tests, total_tests / count, "case"],
        ["LLM Calls", total_calls, total_calls / count, "call"],
        ["Generation Time", total_time, total_time / count, "second"],
        ["Generation Cost", total_cost, total_cost / count, "CNY"],
        ["TP", total_tp, total_tp / count, "violating case reported"],
        ["TN", total_tn, total_tn / count, "compliant case not reported"],
        ["FP", total_fp, total_fp / count, "compliant case reported"],
        ["FN", total_fn, total_fn / count, "violating case not reported"],
        ["Global Precision", total_tp / (total_tp + total_fp), None, "TP/(TP+FP)"],
        ["Global Recall", total_tp / (total_tp + total_fn), None, "TP/(TP+FN)"],
        ["Global Accuracy", (total_tp + total_tn) / total_tests, None, "(TP+TN)/All"],
        ["Global F1", 2 * total_tp / (2 * total_tp + total_fp + total_fn), None, "2TP/(2TP+FP+FN)"],
    ]
    for row in summary_rows:
        summary.append(row)
    _style_header(summary)
    summary.freeze_panes = "A2"
    summary.auto_filter.ref = f"A1:D{summary.max_row}"
    summary.column_dimensions["A"].width = 24
    summary.column_dimensions["B"].width = 18
    summary.column_dimensions["C"].width = 22
    summary.column_dimensions["D"].width = 34
    for row_index in range(2, summary.max_row + 1):
        summary.cell(row_index, 2).number_format = "0.000000"
        summary.cell(row_index, 3).number_format = "0.000000"

    detail = workbook.create_sheet("Checker Metrics")
    headers = [
        "Index",
        "Category",
        "Rule ID",
        "Main Title",
        "LLM Calls",
        "Time (s)",
        "Time (min)",
        "Cost (CNY)",
        "TP",
        "TN",
        "FP",
        "FN",
        "Precision",
        "Recall",
        "Specificity",
        "Accuracy",
        "F1",
        "Performance",
        "Test Suite",
    ]
    detail.append(headers)
    for index, row in enumerate(rows, start=1):
        detail.append(
            [
                index,
                row["category"],
                row["rule_id"],
                row["main_title"],
                row["llm_calls"],
                row["time_seconds"],
                row["time_minutes"],
                row["cost_cny"],
                row["tp"],
                row["tn"],
                row["fp"],
                row["fn"],
                row["precision"],
                row["recall"],
                row["specificity"],
                row["accuracy"],
                row["f1"],
                row["performance"],
                row["test_suite"],
            ]
        )
    _style_header(detail)
    detail.freeze_panes = "A2"
    detail.auto_filter.ref = f"A1:S{detail.max_row}"
    widths = {
        "A": 8,
        "B": 12,
        "C": 14,
        "D": 48,
        "E": 12,
        "F": 14,
        "G": 14,
        "H": 14,
        "I": 8,
        "J": 8,
        "K": 8,
        "L": 8,
        "M": 12,
        "N": 12,
        "O": 12,
        "P": 12,
        "Q": 12,
        "R": 14,
        "S": 80,
    }
    for column, width in widths.items():
        detail.column_dimensions[column].width = width
    for row_index in range(2, detail.max_row + 1):
        detail.cell(row_index, 6).number_format = "0.00"
        detail.cell(row_index, 7).number_format = "0.0000"
        detail.cell(row_index, 8).number_format = "0.000000"
        for column in range(13, 18):
            detail.cell(row_index, column).number_format = "0.000000"
    table = Table(displayName="CheckerMetrics", ref=f"A1:S{detail.max_row}")
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    detail.add_table(table)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = collect_metrics(args.results.resolve())
    write_workbook(rows, args.output.resolve())
    print(
        json.dumps(
            {
                "checker_count": len(rows),
                "output": str(args.output.resolve()),
                "llm_calls": sum(row["llm_calls"] for row in rows),
                "time_seconds": round(sum(row["time_seconds"] for row in rows), 2),
                "cost_cny": sum(row["cost_cny"] for row in rows),
                "tp": sum(row["tp"] for row in rows),
                "tn": sum(row["tn"] for row in rows),
                "fp": sum(row["fp"] for row in rows),
                "fn": sum(row["fn"] for row in rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
