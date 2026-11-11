#!/usr/bin/env python3
"""Export evidence from manually accepted AutoQL analysis runs to Excel."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "doc" / "20026-11-02" / "autoql_analysis_success_evidence.xlsx"
BATCH_RUNS = ROOT / "autoql_runs" / "batch-20261104-042207" / "runs"

# These runs completed mechanically but failed the preceding semantic review.
SEMANTIC_FAILURES = {
    "CVE-2022-32287",
    "CVE-2024-48944",
    "CVE-2025-26795",
    "CVE-2025-26864",
}

# Exact source_sink_detect.csv columns after removing all Found Source/Sink variants.
COMPATIBLE_COLUMNS = [
    "project_slug",
    "cve_id",
    "github_username",
    "github_repository_name",
    "commit",
    "file",
    "class",
    "class_start",
    "class_end",
    "method",
    "method_start",
    "method_end",
    "signature",
    "class_length",
]

RAW_COLUMNS = [
    "project_slug",
    "cve_id",
    "github_username",
    "github_repository_name",
    "commit",
    "evidence_id",
    "revision",
    "file",
    "start_line",
    "end_line",
    "code",
    "run_dir",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def project_metadata():
    path = ROOT / "autoql_data" / "project_info.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["cve_id"]: row for row in csv.DictReader(stream)}


def selected_run_dirs():
    # The user explicitly selected this CVE-2022-25842 run.
    dirs = [ROOT / "autoql_runs" / "CVE-2022-25842-20261103-182319"]
    dirs.extend(sorted(BATCH_RUNS.iterdir()))
    return dirs


def collect():
    projects = project_metadata()
    accepted_runs = []
    raw_rows = []

    for run_dir in selected_run_dirs():
        manifest = read_json(run_dir / "manifest.json")
        result = read_json(run_dir / "result.json")
        cve = manifest["cve_id"]
        if result.get("final_status") != "analysis_completed" or cve in SEMANTIC_FAILURES:
            continue

        spec_path = run_dir / "vuln_spec.json"
        if not spec_path.exists():
            continue
        spec = read_json(spec_path)
        metadata = projects[cve]
        accepted_runs.append(
            {
                "cve_id": cve,
                "cwe_id": metadata["cwe_id"],
                "cwe_name": metadata["cwe_name"],
                "project_slug": metadata["project_slug"],
                "run_dir": str(run_dir.relative_to(ROOT)),
                "evidence_count": len(spec.get("evidence", [])),
            }
        )

        for evidence in spec.get("evidence", []):
            revision = evidence["revision"]
            if revision == "buggy":
                commit = manifest["buggy_commit"]
            elif revision in {"fix", "fixed"}:
                commit = manifest["fix_commit"]
            else:
                commit = ""
            raw_rows.append(
                {
                    "project_slug": metadata["project_slug"],
                    "cve_id": cve,
                    "github_username": metadata["github_username"],
                    "github_repository_name": metadata["github_repository_name"],
                    "commit": commit,
                    "evidence_id": evidence["id"],
                    "revision": revision,
                    "file": evidence["file"],
                    "start_line": evidence["start_line"],
                    "end_line": evidence["end_line"],
                    "code": evidence["code"],
                    "run_dir": str(run_dir.relative_to(ROOT)),
                }
            )

    return accepted_runs, raw_rows


def style_sheet(ws, widths):
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for index, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(index)].width = width


def create_workbook(accepted_runs, raw_rows):
    workbook = Workbook()
    workbook.remove(workbook.active)

    compatible = workbook.create_sheet("evidence_compatible")
    compatible.append(COMPATIBLE_COLUMNS)
    for row in raw_rows:
        # vuln_spec has no class/method/signature boundaries. Keep those fields
        # empty instead of inventing them. Evidence locations are mapped to the
        # only compatible line-range columns, method_start/method_end.
        compatible.append(
            [
                row["project_slug"],
                row["cve_id"],
                row["github_username"],
                row["github_repository_name"],
                row["commit"],
                row["file"],
                "",
                "",
                "",
                "",
                row["start_line"],
                row["end_line"],
                "",
                "",
            ]
        )
    style_sheet(
        compatible,
        [34, 19, 22, 28, 43, 75, 20, 14, 14, 24, 14, 14, 36, 14],
    )

    raw = workbook.create_sheet("vuln_spec_evidence")
    raw.append(RAW_COLUMNS)
    for row in raw_rows:
        raw.append([row[column] for column in RAW_COLUMNS])
    style_sheet(raw, [34, 19, 22, 28, 43, 14, 12, 75, 14, 14, 110, 58])

    summary = workbook.create_sheet("说明")
    summary.append(["项目", "值"])
    summary.append(["成功 CVE 数", len(accepted_runs)])
    summary.append(["Evidence 数", len(raw_rows)])
    summary.append(
        [
            "成功口径",
            "result.json.final_status 为 analysis_completed，且未被上一轮人工审查认定为语义失败。",
        ]
    )
    summary.append(
        [
            "运行选择",
            "CVE-2022-25842 固定使用 autoql_runs/CVE-2022-25842-20261103-182319；其余使用 batch-20261104-042207/runs。",
        ]
    )
    summary.append(
        [
            "兼容表映射",
            "method_start/method_end 存放 evidence.start_line/end_line；vuln_spec 不提供 class、method、signature 和 class_length，因此对应列留空。",
        ]
    )
    summary.append(
        [
            "排除的语义失败",
            ", ".join(sorted(SEMANTIC_FAILURES)),
        ]
    )
    summary.append([])
    summary.append(["CVE", "CWE", "CWE 名称", "项目", "运行目录", "Evidence 数"])
    for run in accepted_runs:
        summary.append(
            [
                run["cve_id"],
                run["cwe_id"],
                run["cwe_name"],
                run["project_slug"],
                run["run_dir"],
                run["evidence_count"],
            ]
        )
    style_sheet(summary, [24, 18, 58, 38, 65, 16])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(OUTPUT)


def verify(expected_runs, expected_rows):
    workbook = load_workbook(OUTPUT, read_only=True, data_only=True)
    assert workbook.sheetnames == ["evidence_compatible", "vuln_spec_evidence", "说明"]
    assert workbook["evidence_compatible"].max_row - 1 == expected_rows
    assert workbook["vuln_spec_evidence"].max_row - 1 == expected_rows
    assert workbook["说明"]["B2"].value == expected_runs
    assert workbook["说明"]["B3"].value == expected_rows


def main():
    accepted_runs, raw_rows = collect()
    create_workbook(accepted_runs, raw_rows)
    verify(len(accepted_runs), len(raw_rows))
    print(f"wrote {OUTPUT} ({len(accepted_runs)} CVEs, {len(raw_rows)} evidence rows)")


if __name__ == "__main__":
    main()
