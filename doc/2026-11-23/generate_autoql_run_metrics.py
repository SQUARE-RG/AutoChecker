#!/usr/bin/env python3
"""Summarize the latest AutoQL full run for every CVE into an Excel workbook."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "autoql_runs"
PROJECT_INFO = ROOT / "autoql_data" / "project_info.csv"
OUTPUT = ROOT / "doc" / "2026-11-23" / "autoql_run_metrics.xlsx"
RUN_NAME = re.compile(r"^(CVE-\d{4}-\d+)-(\d{8}-\d{6})$")

DETAIL_HEADERS = [
    "序号",
    "CWE",
    "CVE",
    "Total Tokens",
    "Runtime",
    "Query Iterations",
    "API调用次数",
    "Cost (CNY)",
    "最终状态",
    "运行目录",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_projects() -> dict[str, dict[str, str]]:
    with PROJECT_INFO.open(encoding="utf-8-sig", newline="") as stream:
        return {row["cve_id"]: row for row in csv.DictReader(stream)}


def select_latest_runs() -> dict[str, Path]:
    selected: dict[str, tuple[str, Path]] = {}
    for result_path in RUNS_DIR.glob("CVE-*/result.json"):
        match = RUN_NAME.fullmatch(result_path.parent.name)
        if not match:
            continue
        cve, timestamp = match.groups()
        if cve not in selected or timestamp > selected[cve][0]:
            selected[cve] = (timestamp, result_path.parent)
    return {cve: item[1] for cve, item in selected.items()}


def collect_rows() -> list[dict]:
    projects = load_projects()
    rows = []
    for cve, run_dir in sorted(select_latest_runs().items()):
        result = read_json(run_dir / "result.json")
        timing_path = run_dir / "timing_summary.json"
        usage_path = run_dir / "usage_summary.json"
        timing = read_json(timing_path) if timing_path.exists() else {}
        usage = read_json(usage_path).get("total", {}) if usage_path.exists() else {}
        costs = usage.get("known_cost_by_currency", {})
        rows.append(
            {
                "CWE": projects.get(cve, {}).get("cwe_id", ""),
                "CVE": cve,
                "Total Tokens": usage.get("known_total_tokens", 0),
                "Runtime (seconds)": timing.get("wall_seconds"),
                "Query Iterations": result.get("candidate_count", 0) or 0,
                "API调用次数": usage.get("physical_requests", 0),
                "Cost (CNY)": costs.get("CNY", 0),
                "最终状态": result.get("final_status", "unknown"),
                "运行目录": str(run_dir.relative_to(ROOT)),
            }
        )
    def numeric_id(value: str) -> tuple[int, ...]:
        numbers = re.findall(r"\d+", value or "")
        return tuple(int(number) for number in numbers) if numbers else (10**9,)

    rows.sort(key=lambda row: (numeric_id(row["CWE"]), numeric_id(row["CVE"])))
    return rows


def style_header(sheet) -> None:
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")


def add_detail_sheet(workbook: Workbook, rows: list[dict]) -> None:
    sheet = workbook.active
    sheet.title = "每个CVE运行指标"
    sheet.append(DETAIL_HEADERS)
    for index, row in enumerate(rows, 1):
        runtime = row["Runtime (seconds)"]
        sheet.append(
            [
                index,
                row["CWE"],
                row["CVE"],
                row["Total Tokens"],
                runtime / 86400 if runtime is not None else None,
                row["Query Iterations"],
                row["API调用次数"],
                row["Cost (CNY)"],
                row["最终状态"],
                row["运行目录"],
            ]
        )

    count = len(rows)
    runtime_values = [row["Runtime (seconds)"] for row in rows if row["Runtime (seconds)"] is not None]
    sheet.append(
        [
            "Average",
            "",
            "",
            sum(row["Total Tokens"] for row in rows) / count if count else 0,
            (sum(runtime_values) / len(runtime_values) / 86400) if runtime_values else None,
            sum(row["Query Iterations"] for row in rows) / count if count else 0,
            sum(row["API调用次数"] for row in rows) / count if count else 0,
            sum(row["Cost (CNY)"] for row in rows) / count if count else 0,
            "",
            f"基于 {count} 个CVE",
        ]
    )

    style_header(sheet)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:J{count + 1}"
    widths = [8, 14, 20, 18, 20, 20, 16, 16, 22, 58]
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        row[4].number_format = "[h]:mm:ss"
        row[7].number_format = "0.000000"
    average_row = sheet.max_row
    for cell in sheet[average_row]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAF7")
    for column in (4, 6, 7):
        sheet.cell(average_row, column).number_format = "0.00"
    sheet.cell(average_row, 5).number_format = "[h]:mm:ss"
    sheet.cell(average_row, 8).number_format = "0.000000"


def add_summary_sheet(workbook: Workbook, rows: list[dict]) -> None:
    sheet = workbook.create_sheet("汇总与口径")
    sheet.append(["项目", "数值", "口径说明"])
    token_total = sum(row["Total Tokens"] for row in rows)
    runtime_values = [row["Runtime (seconds)"] for row in rows if row["Runtime (seconds)"] is not None]
    iteration_total = sum(row["Query Iterations"] for row in rows)
    api_total = sum(row["API调用次数"] for row in rows)
    cost_total = sum(row["Cost (CNY)"] for row in rows)
    items = [
        ("CVE数量", len(rows), "每个CVE选择时间戳最新且包含 result.json 的根级运行目录"),
        ("Total Tokens合计", token_total, "usage_summary.total.known_total_tokens"),
        ("Runtime合计(秒)", sum(runtime_values), "timing_summary.wall_seconds；完整任务墙钟时间"),
        ("Query Iterations合计", iteration_total, "result.candidate_count；生成的候选Query数量"),
        ("API调用次数合计", api_total, "usage_summary.total.physical_requests"),
        ("Cost合计(CNY)", cost_total, "usage_summary.total.known_cost_by_currency.CNY"),
        ("缺失usage的处理", "0", "流程在首次LLM调用前失败且没有 usage_summary.json 时，Token/API/Cost记为0"),
    ]
    for item in items:
        sheet.append(item)
    sheet.append([])
    sheet.append(["最终状态", "CVE数量", ""])
    for status, count in sorted(Counter(row["最终状态"] for row in rows).items()):
        sheet.append([status, count, ""])

    style_header(sheet)
    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 28
    sheet.column_dimensions["C"].width = 88
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for row_number in range(2, 8):
        sheet.cell(row_number, 2).number_format = "0.000000"


def verify(expected_rows: int) -> None:
    workbook = load_workbook(OUTPUT, read_only=True, data_only=True)
    assert workbook.sheetnames == ["每个CVE运行指标", "汇总与口径"]
    sheet = workbook["每个CVE运行指标"]
    assert sheet.max_row - 2 == expected_rows
    assert [cell.value for cell in sheet[1]] == DETAIL_HEADERS
    assert sheet.cell(sheet.max_row, 1).value == "Average"


def main() -> None:
    rows = collect_rows()
    workbook = Workbook()
    add_detail_sheet(workbook, rows)
    add_summary_sheet(workbook, rows)
    workbook.save(OUTPUT)
    verify(len(rows))
    print(f"Wrote {OUTPUT} with {len(rows)} CVEs")


if __name__ == "__main__":
    main()
