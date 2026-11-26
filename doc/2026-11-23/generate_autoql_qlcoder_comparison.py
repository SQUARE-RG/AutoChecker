#!/usr/bin/env python3
"""Compare AutoQL runs with the QLCoder baseline on their common CVEs."""

from __future__ import annotations

import re
from datetime import timedelta
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "doc" / "2026-11-23" / "qlcoder_batch_20261124_193002.xlsx"
AUTOQL = ROOT / "doc" / "2026-11-23" / "autoql_run_metrics.xlsx"
OUTPUT = ROOT / "doc" / "2026-11-23" / "autoql_vs_qlcoder_comparison.xlsx"

HEADERS = [
    "序号",
    "CWE",
    "CVE",
    "QLCoder Total Tokens",
    "AutoQL Total Tokens",
    "Tokens降低率",
    "QLCoder Runtime",
    "AutoQL Runtime",
    "Runtime降低率",
    "QLCoder Query Iterations",
    "AutoQL Query Iterations",
    "Iterations降低率",
    "QLCoder API Calls",
    "AutoQL API Calls",
    "API调用降低率",
    "QLCoder Cost (CNY)",
    "AutoQL Cost (CNY)",
    "Cost降低率",
    "AutoQL最终状态",
]


def id_number(value: str) -> tuple[int, ...]:
    numbers = re.findall(r"\d+", value or "")
    return tuple(int(number) for number in numbers) if numbers else (10**9,)


def duration_seconds(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, (int, float)):
        return float(value) * 86400
    raise TypeError(f"Unsupported Excel duration value: {value!r}")


def load_baseline() -> dict[str, dict]:
    sheet = load_workbook(BASELINE, read_only=True, data_only=True)["Summary"]
    headers = [cell.value for cell in sheet[1]]
    rows = {}
    for values in sheet.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, values))
        cve = row.get("CVE")
        if not isinstance(cve, str) or not cve.startswith("CVE-"):
            continue
        rows[cve] = {
            "CWE": row["CWE"],
            "CVE": cve,
            "Total Tokens": row["Total Tokens"],
            "Runtime seconds": row["Runtime (min)"] * 60,
            "Query Iterations": row["Query Iterations"],
            "API Calls": row["API Calls"],
            "Cost": row["Cost (RMB)"],
        }
    return rows


def load_autoql() -> dict[str, dict]:
    sheet = load_workbook(AUTOQL, read_only=True, data_only=True)["每个CVE运行指标"]
    headers = [cell.value for cell in sheet[1]]
    rows = {}
    for values in sheet.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, values))
        cve = row.get("CVE")
        if not isinstance(cve, str) or not cve.startswith("CVE-"):
            continue
        rows[cve] = {
            "CWE": row["CWE"],
            "CVE": cve,
            "Total Tokens": row["Total Tokens"],
            "Runtime seconds": duration_seconds(row["Runtime"]),
            "Query Iterations": row["Query Iterations"],
            "API Calls": row["API调用次数"],
            "Cost": row["Cost (CNY)"],
            "Status": row["最终状态"],
        }
    return rows


def reduction(baseline: float | int | None, autoql: float | int | None) -> float | None:
    if baseline in (None, 0) or autoql is None:
        return None
    return 1 - autoql / baseline


def build_rows(baseline: dict[str, dict], autoql: dict[str, dict]) -> list[dict]:
    rows = []
    for cve in baseline.keys() & autoql.keys():
        old, new = baseline[cve], autoql[cve]
        rows.append(
            {
                "CWE": new["CWE"] or old["CWE"],
                "CVE": cve,
                "QLCoder Total Tokens": old["Total Tokens"],
                "AutoQL Total Tokens": new["Total Tokens"],
                "Tokens降低率": reduction(old["Total Tokens"], new["Total Tokens"]),
                "QLCoder Runtime seconds": old["Runtime seconds"],
                "AutoQL Runtime seconds": new["Runtime seconds"],
                "Runtime降低率": reduction(old["Runtime seconds"], new["Runtime seconds"]),
                "QLCoder Query Iterations": old["Query Iterations"],
                "AutoQL Query Iterations": new["Query Iterations"],
                "Iterations降低率": reduction(old["Query Iterations"], new["Query Iterations"]),
                "QLCoder API Calls": old["API Calls"],
                "AutoQL API Calls": new["API Calls"],
                "API调用降低率": reduction(old["API Calls"], new["API Calls"]),
                "QLCoder Cost (CNY)": old["Cost"],
                "AutoQL Cost (CNY)": new["Cost"],
                "Cost降低率": reduction(old["Cost"], new["Cost"]),
                "AutoQL最终状态": new["Status"],
            }
        )
    rows.sort(key=lambda row: (id_number(row["CWE"]), id_number(row["CVE"])))
    return rows


def average(rows: list[dict], key: str) -> float:
    values = [row[key] for row in rows if row[key] is not None]
    return sum(values) / len(values) if values else 0


def append_average(sheet, rows: list[dict]) -> None:
    base_tokens = average(rows, "QLCoder Total Tokens")
    auto_tokens = average(rows, "AutoQL Total Tokens")
    base_runtime = average(rows, "QLCoder Runtime seconds")
    auto_runtime = average(rows, "AutoQL Runtime seconds")
    base_iterations = average(rows, "QLCoder Query Iterations")
    auto_iterations = average(rows, "AutoQL Query Iterations")
    base_calls = average(rows, "QLCoder API Calls")
    auto_calls = average(rows, "AutoQL API Calls")
    base_cost = average(rows, "QLCoder Cost (CNY)")
    auto_cost = average(rows, "AutoQL Cost (CNY)")
    sheet.append(
        [
            "Average",
            "",
            "",
            base_tokens,
            auto_tokens,
            reduction(base_tokens, auto_tokens),
            base_runtime / 86400,
            auto_runtime / 86400,
            reduction(base_runtime, auto_runtime),
            base_iterations,
            auto_iterations,
            reduction(base_iterations, auto_iterations),
            base_calls,
            auto_calls,
            reduction(base_calls, auto_calls),
            base_cost,
            auto_cost,
            reduction(base_cost, auto_cost),
            f"基于 {len(rows)} 个共同CVE",
        ]
    )


def style_comparison(sheet, data_rows: int) -> None:
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    sheet.row_dimensions[1].height = 36
    sheet.freeze_panes = "D2"
    sheet.auto_filter.ref = f"A1:S{data_rows + 1}"

    widths = [8, 13, 20, 22, 21, 15, 20, 19, 16, 24, 23, 18, 19, 18, 17, 21, 20, 15, 22]
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width

    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        for column in (7, 8):
            row[column - 1].number_format = "[h]:mm:ss"
        for column in (6, 9, 12, 15, 18):
            row[column - 1].number_format = "0.00%"
        for column in (16, 17):
            row[column - 1].number_format = "0.000000"

    average_row = sheet.max_row
    for cell in sheet[average_row]:
        cell.fill = PatternFill("solid", fgColor="D9EAF7")
        cell.font = Font(bold=True)
    for column in (4, 5, 10, 11, 13, 14):
        sheet.cell(average_row, column).number_format = "0.00"


def add_notes(workbook: Workbook, baseline: dict[str, dict], autoql: dict[str, dict], rows: list[dict]) -> None:
    sheet = workbook.create_sheet("口径说明")
    sheet.append(["项目", "说明"])
    baseline_only = sorted(baseline.keys() - autoql.keys(), key=id_number)
    autoql_only = sorted(autoql.keys() - baseline.keys(), key=id_number)
    notes = [
        ("对比范围", f"两份工作簿共有的 {len(rows)} 个 CVE"),
        ("Baseline来源", str(BASELINE.relative_to(ROOT))),
        ("AutoQL来源", str(AUTOQL.relative_to(ROOT))),
        ("Baseline独有CVE", "、".join(baseline_only) or "无"),
        ("AutoQL独有CVE", "、".join(autoql_only) or "无"),
        ("降低率", "1 - AutoQL / QLCoder；正数表示AutoQL更低，负数表示AutoQL更高"),
        ("Average", "原始指标为10个共同CVE的算术平均；Average行降低率由两侧平均值计算"),
        ("Runtime", "均表示完整运行墙钟时间；Baseline原始值精确到0.1分钟，表中转换为[h]:mm:ss"),
        ("Query Iterations", "QLCoder为Phase 3 context window数量；AutoQL为候选Query数量，定义并不完全相同"),
        ("API调用", "QLCoder按assistant响应ID统计；AutoQL使用usage_summary.total.physical_requests"),
        ("成本", "RMB与CNY按同一币种并列比较，但模型和价格表可能不同"),
        (
            "失败运行",
            "AutoQL infrastructure_error且未调用LLM的运行保留为0 Token/0 API/0 Cost；"
            "needs_review和budget_exhausted也保留，因此资源降低率不等同于成功率提升",
        ),
    ]
    for note in notes:
        sheet.append(note)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
    sheet.column_dimensions["A"].width = 24
    sheet.column_dimensions["B"].width = 110
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def verify(expected_rows: int) -> None:
    workbook = load_workbook(OUTPUT, read_only=True, data_only=True)
    assert workbook.sheetnames == ["CVE对比", "口径说明"]
    sheet = workbook["CVE对比"]
    assert sheet.max_row == expected_rows + 2
    assert sheet.cell(sheet.max_row, 1).value == "Average"
    cwes = [int(sheet.cell(row, 2).value.split("-")[1]) for row in range(2, sheet.max_row)]
    assert cwes == sorted(cwes)


def main() -> None:
    baseline = load_baseline()
    autoql = load_autoql()
    rows = build_rows(baseline, autoql)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "CVE对比"
    sheet.append(HEADERS)
    for index, row in enumerate(rows, 1):
        sheet.append(
            [
                index,
                row["CWE"],
                row["CVE"],
                row["QLCoder Total Tokens"],
                row["AutoQL Total Tokens"],
                row["Tokens降低率"],
                row["QLCoder Runtime seconds"] / 86400,
                row["AutoQL Runtime seconds"] / 86400,
                row["Runtime降低率"],
                row["QLCoder Query Iterations"],
                row["AutoQL Query Iterations"],
                row["Iterations降低率"],
                row["QLCoder API Calls"],
                row["AutoQL API Calls"],
                row["API调用降低率"],
                row["QLCoder Cost (CNY)"],
                row["AutoQL Cost (CNY)"],
                row["Cost降低率"],
                row["AutoQL最终状态"],
            ]
        )
    append_average(sheet, rows)
    style_comparison(sheet, len(rows))
    add_notes(workbook, baseline, autoql, rows)
    workbook.save(OUTPUT)
    verify(len(rows))
    print(f"Wrote {OUTPUT} with {len(rows)} common CVEs")


if __name__ == "__main__":
    main()
