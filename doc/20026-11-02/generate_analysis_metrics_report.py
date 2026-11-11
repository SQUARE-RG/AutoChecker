#!/usr/bin/env python3
"""Generate per-CVE analysis usage and runtime metrics for cve_bak.txt."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
CVE_LIST = ROOT / "autoql_data" / "cve_bak.txt"
PROJECT_INFO = ROOT / "autoql_data" / "project_info.csv"
BATCH_RUNS = ROOT / "autoql_runs" / "batch-20261104-042207" / "runs"
OUTPUT = ROOT / "doc" / "20026-11-02" / "autoql_analysis_success_metrics.xlsx"

SEMANTIC_FAILURES = {
    "CVE-2022-32287": "修复机制分析错误",
    "CVE-2024-48944": "修复机制分析错误",
    "CVE-2025-26795": "跨 CVE 证据污染",
    "CVE-2025-26864": "跨 CVE 证据污染",
}


DETAIL_COLUMNS = [
    "序号",
    "CVE",
    "CWE",
    "CWE名称",
    "项目",
    "Total Tokens",
    "Input Tokens",
    "Output Tokens",
    "Cached Tokens",
    "Reasoning Tokens",
    "Runtime (seconds)",
    "Runtime (minutes)",
    "LLM Calls",
    "Cost",
    "Currency",
    "Cost是否估算",
    "运行目录",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_projects():
    with PROJECT_INFO.open(encoding="utf-8-sig", newline="") as stream:
        return {row["cve_id"]: row for row in csv.DictReader(stream)}


def load_requested_cves():
    return [
        line.strip()
        for line in CVE_LIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def selected_runs():
    result = {
        "CVE-2022-25842": ROOT / "autoql_runs" / "CVE-2022-25842-20261103-182319",
        "CVE-2022-32287": ROOT / "autoql_runs" / "CVE-2022-32287-20261104-030731",
    }
    for run_dir in sorted(BATCH_RUNS.iterdir()):
        manifest = read_json(run_dir / "manifest.json")
        result[manifest["cve_id"]] = run_dir
    return result


def cost_is_estimate(run_dir):
    path = run_dir / "usage.jsonl"
    flags = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("phase") == "analysis" and event.get("cost") is not None:
                flags.append(bool(event.get("cost_is_estimate")))
    if not flags:
        return "未知"
    return "是" if all(flags) else ("部分" if any(flags) else "否")


def collect():
    projects = load_projects()
    runs = selected_runs()
    successful = []
    skipped = []

    for cve in load_requested_cves():
        run_dir = runs.get(cve)
        if run_dir is None:
            skipped.append((cve, "没有运行目录"))
            continue
        result = read_json(run_dir / "result.json")
        if result.get("final_status") != "analysis_completed":
            skipped.append((cve, "结构化输出解析失败"))
            continue
        if cve in SEMANTIC_FAILURES:
            skipped.append((cve, SEMANTIC_FAILURES[cve]))
            continue

        usage = read_json(run_dir / "usage_summary.json")["analysis"]
        timing = read_json(run_dir / "timing_summary.json")
        runtime = timing["breakdown"]["analysis"]["duration_seconds"]
        costs = usage.get("known_cost_by_currency", {})
        if len(costs) == 1:
            currency, cost = next(iter(costs.items()))
        elif not costs:
            currency, cost = "", None
        else:
            currency = "+".join(sorted(costs))
            cost = None

        project = projects[cve]
        successful.append(
            {
                "CVE": cve,
                "CWE": project["cwe_id"],
                "CWE名称": project["cwe_name"],
                "项目": project["project_slug"],
                "Total Tokens": usage["known_total_tokens"],
                "Input Tokens": usage["known_input_tokens"],
                "Output Tokens": usage["known_output_tokens"],
                "Cached Tokens": usage["known_cached_tokens"],
                "Reasoning Tokens": usage["known_reasoning_tokens"],
                "Runtime (seconds)": runtime,
                "Runtime (minutes)": runtime / 60,
                "LLM Calls": usage["physical_requests"],
                "Cost": cost,
                "Currency": currency,
                "Cost是否估算": cost_is_estimate(run_dir),
                "运行目录": str(run_dir.relative_to(ROOT)),
            }
        )
    return successful, skipped


def style_sheet(sheet, widths):
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in sheet[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width


def add_details(workbook, rows):
    sheet = workbook.create_sheet("成功CVE指标")
    sheet.append(DETAIL_COLUMNS)
    value_columns = DETAIL_COLUMNS[1:]
    for index, row in enumerate(rows, 1):
        sheet.append([index] + [row[column] for column in value_columns])
    style_sheet(
        sheet,
        [8, 19, 14, 55, 38, 17, 17, 17, 17, 18, 20, 20, 14, 16, 12, 16, 65],
    )
    for row in range(2, sheet.max_row + 1):
        sheet.cell(row, 11).number_format = "0.000"
        sheet.cell(row, 12).number_format = "0.000"
        sheet.cell(row, 14).number_format = "0.000000"


def add_cwe_summary(workbook, rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["CWE"], row["CWE名称"])].append(row)
    sheet = workbook.create_sheet("按CWE汇总")
    headers = [
        "CWE",
        "CWE名称",
        "CVE数量",
        "Total Tokens",
        "平均Tokens/CVE",
        "Runtime (seconds)",
        "平均Runtime/CVE",
        "LLM Calls",
        "平均Calls/CVE",
        "Cost (CNY)",
        "平均Cost/CVE",
    ]
    sheet.append(headers)
    for (cwe, name), items in sorted(grouped.items()):
        count = len(items)
        tokens = sum(row["Total Tokens"] for row in items)
        runtime = sum(row["Runtime (seconds)"] for row in items)
        calls = sum(row["LLM Calls"] for row in items)
        cost = sum((row["Cost"] or 0) for row in items if row["Currency"] == "CNY")
        sheet.append(
            [
                cwe,
                name,
                count,
                tokens,
                tokens / count,
                runtime,
                runtime / count,
                calls,
                calls / count,
                cost,
                cost / count,
            ]
        )
    style_sheet(sheet, [14, 60, 14, 18, 20, 22, 22, 15, 18, 18, 18])
    for row in range(2, sheet.max_row + 1):
        for column in [5, 6, 7, 9, 10, 11]:
            sheet.cell(row, column).number_format = "0.000000"


def add_summary(workbook, rows, skipped):
    sheet = workbook.create_sheet("汇总与口径")
    total_tokens = sum(row["Total Tokens"] for row in rows)
    total_runtime = sum(row["Runtime (seconds)"] for row in rows)
    total_calls = sum(row["LLM Calls"] for row in rows)
    total_cost = sum((row["Cost"] or 0) for row in rows if row["Currency"] == "CNY")
    metrics = [
        ("指标", "数值", "说明"),
        ("cve_bak.txt CVE数", len(load_requested_cves()), "输入范围"),
        ("成功分析CVE数", len(rows), "运行完成且通过上一轮人工语义审查"),
        ("失败CVE数", len(skipped), "6个结构化输出失败 + 4个语义失败"),
        ("Total Tokens合计", total_tokens, "usage_summary.analysis.known_total_tokens"),
        ("Total Tokens平均值", total_tokens / len(rows), "成功CVE平均"),
        ("Runtime合计(秒)", total_runtime, "analysis stage，不含 input.prepare"),
        ("Runtime平均值(秒)", total_runtime / len(rows), "成功CVE平均"),
        ("LLM Calls合计", total_calls, "analysis.physical_requests"),
        ("LLM Calls平均值", total_calls / len(rows), "成功CVE平均"),
        ("Cost合计(CNY)", total_cost, "usage中记录的估算成本"),
        ("Cost平均值(CNY)", total_cost / len(rows), "成功CVE平均"),
        (
            "运行选择",
            "CVE-2022-25842 使用 20261103-182319；其余成功项使用 batch-20261104-042207。CVE-2022-32287 已按语义失败排除。",
            "",
        ),
        (
            "成功口径",
            "final_status == analysis_completed，并排除上一轮人工审查认定的修复机制错误和跨CVE证据污染。",
            "因此共有24个成功CVE",
        ),
    ]
    for row in metrics:
        sheet.append(row)
    sheet.append([])
    sheet.append(["失败CVE", "失败类型", ""])
    for cve, reason in skipped:
        sheet.append([cve, reason, ""])
    style_sheet(sheet, [32, 95, 55])
    for row in range(2, 13):
        sheet.cell(row, 2).number_format = "0.000000"


def create_workbook(rows, skipped):
    workbook = Workbook()
    workbook.remove(workbook.active)
    add_details(workbook, rows)
    add_cwe_summary(workbook, rows)
    add_summary(workbook, rows, skipped)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(OUTPUT)


def verify(expected_rows):
    workbook = load_workbook(OUTPUT, read_only=True, data_only=True)
    assert workbook.sheetnames == ["成功CVE指标", "按CWE汇总", "汇总与口径"]
    assert workbook["成功CVE指标"].max_row - 1 == expected_rows


def main():
    rows, skipped = collect()
    create_workbook(rows, skipped)
    verify(len(rows))
    print(f"wrote {OUTPUT} ({len(rows)} successful CVEs, {len(skipped)} unsuccessful)")


if __name__ == "__main__":
    main()
