#!/usr/bin/env python3
"""Compare accepted AutoQL evidence with source_sink_detect.csv annotations."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_XLSX = ROOT / "doc" / "20026-11-02" / "autoql_analysis_success_evidence.xlsx"
DATASET_CSV = ROOT / "autoql_data" / "source_sink_detect.csv"
OUTPUT_XLSX = ROOT / "doc" / "20026-11-02" / "autoql_evidence_dataset_comparison.xlsx"


def clean_path(value):
    return str(value or "").replace("\\", "/").lstrip("./")


def integer(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def overlaps(start1, end1, start2, end2):
    return max(start1, start2) <= min(end1, end2)


def load_evidence():
    workbook = load_workbook(EVIDENCE_XLSX, read_only=True, data_only=True)
    sheet = workbook["vuln_spec_evidence"]
    rows = sheet.iter_rows(values_only=True)
    headers = next(rows)
    return [dict(zip(headers, row)) for row in rows]


def load_annotations():
    with DATASET_CSV.open(encoding="utf-8-sig", newline="") as stream:
        result = []
        for row_number, row in enumerate(csv.DictReader(stream), 2):
            row["dataset_row"] = row_number
            result.append(row)
        return result


def annotation_range(annotation):
    method_start = integer(annotation["method_start"])
    method_end = integer(annotation["method_end"])
    if method_start is not None and method_end is not None:
        return method_start, method_end, "method"
    if annotation["method"]:
        # Keep the class range for display only. Matching will use the method
        # name in the canonical evidence code to avoid a broad class-level hit.
        return (
            integer(annotation["class_start"]),
            integer(annotation["class_end"]),
            "method_name_fallback",
        )
    class_start = integer(annotation["class_start"])
    class_end = integer(annotation["class_end"])
    if class_start is not None and class_end is not None:
        return class_start, class_end, "class_fallback"
    return None, None, "file_only"


def compare():
    evidence = load_evidence()
    annotations = load_annotations()
    evidence_by_cve = defaultdict(list)
    annotations_by_cve = defaultdict(list)
    for item in evidence:
        evidence_by_cve[item["cve_id"]].append(item)
    for item in annotations:
        annotations_by_cve[item["cve_id"]].append(item)

    cve_rows = []
    detail_rows = []
    comparable_evidence_count = 0
    matched_evidence_keys = set()
    matched_annotation_keys = set()

    for cve in sorted(evidence_by_cve):
        cve_evidence = evidence_by_cve[cve]
        cve_annotations = annotations_by_cve.get(cve, [])
        if cve_annotations:
            comparable_evidence_count += len(cve_evidence)

        file_match_keys = set()
        position_match_keys = set()
        cve_annotation_matches = 0
        hit_descriptions = []

        for annotation in cve_annotations:
            gt_file = clean_path(annotation["file"])
            gt_start, gt_end, range_kind = annotation_range(annotation)
            same_file = []
            matched = []
            for item in cve_evidence:
                evidence_key = (cve, item["evidence_id"])
                if clean_path(item["file"]) != gt_file:
                    continue
                same_file.append(item)
                file_match_keys.add(evidence_key)
                ev_start = integer(item["start_line"])
                ev_end = integer(item["end_line"])
                if range_kind == "method_name_fallback":
                    method_pattern = rf"\b{re.escape(annotation['method'])}\s*\("
                    is_match = re.search(method_pattern, item["code"] or "") is not None
                elif gt_start is None or gt_end is None:
                    is_match = True
                else:
                    is_match = (
                        ev_start is not None
                        and ev_end is not None
                        and overlaps(ev_start, ev_end, gt_start, gt_end)
                    )
                if is_match:
                    matched.append(item)
                    position_match_keys.add(evidence_key)
                    matched_evidence_keys.add(evidence_key)

            annotation_key = (cve, annotation["dataset_row"])
            if matched:
                matched_annotation_keys.add(annotation_key)
                cve_annotation_matches += 1
                hit_descriptions.append(
                    f"{annotation['method'] or annotation['class']} <- "
                    + ", ".join(
                        f"{item['evidence_id']}({item['revision']}:{item['start_line']}-{item['end_line']})"
                        for item in matched
                    )
                )

            detail_rows.append(
                {
                    "cve_id": cve,
                    "dataset_row": annotation["dataset_row"],
                    "dataset_commit": annotation["commit"],
                    "file": annotation["file"],
                    "class": annotation["class"],
                    "method": annotation["method"],
                    "signature": annotation["signature"],
                    "range_type": range_kind,
                    "annotation_start": gt_start,
                    "annotation_end": gt_end,
                    "matched": "是" if matched else "否",
                    "matched_evidence": "; ".join(
                        f"{item['evidence_id']}|{item['revision']}|{item['commit']}|"
                        f"{item['start_line']}-{item['end_line']}"
                        for item in matched
                    ),
                    "commit_equal": (
                        "是"
                        if any(item["commit"] == annotation["commit"] for item in matched)
                        else ("否" if matched else "")
                    ),
                    "same_file_but_no_overlap": "; ".join(
                        f"{item['evidence_id']}|{item['revision']}|{item['start_line']}-{item['end_line']}"
                        for item in same_file
                        if item not in matched
                    ),
                }
            )

        if not cve_annotations:
            status = "无数据集标注"
            reason = "source_sink_detect.csv 中没有该 CVE，不计入准确率"
        elif position_match_keys:
            status = "命中"
            reason = "至少一条 evidence 与同 CVE、同文件的标注满足位置/方法名命中规则"
        elif file_match_keys:
            status = "未命中"
            reason = "存在同文件 evidence，但与标注方法/类区间不重叠"
        else:
            status = "未命中"
            reason = "没有 evidence 命中数据集标注文件"

        first = cve_evidence[0]
        cve_rows.append(
            {
                "cve_id": cve,
                "project_slug": first["project_slug"],
                "evidence_count": len(cve_evidence),
                "annotation_count": len(cve_annotations),
                "file_matched_evidence_count": len(file_match_keys),
                "position_matched_evidence_count": len(position_match_keys),
                "matched_annotation_count": cve_annotation_matches,
                "hit_status": status,
                "included_in_accuracy": "是" if cve_annotations else "否",
                "hit_details": "；".join(hit_descriptions),
                "reason": reason,
            }
        )

    comparable = [row for row in cve_rows if row["included_in_accuracy"] == "是"]
    hit_cves = [row for row in comparable if row["hit_status"] == "命中"]
    total_annotations = sum(row["annotation_count"] for row in comparable)
    metrics = {
        "success_cves": len(cve_rows),
        "evidence_rows": len(evidence),
        "comparable_cves": len(comparable),
        "hit_cves": len(hit_cves),
        "missed_cves": len(comparable) - len(hit_cves),
        "unlabeled_cves": len(cve_rows) - len(comparable),
        "cve_accuracy": len(hit_cves) / len(comparable) if comparable else 0,
        "comparable_evidence": comparable_evidence_count,
        "matched_evidence": len(matched_evidence_keys),
        "evidence_hit_rate": (
            len(matched_evidence_keys) / comparable_evidence_count
            if comparable_evidence_count
            else 0
        ),
        "annotations": total_annotations,
        "matched_annotations": len(matched_annotation_keys),
        "annotation_coverage": (
            len(matched_annotation_keys) / total_annotations if total_annotations else 0
        ),
    }
    return cve_rows, detail_rows, metrics


def style_sheet(sheet, widths, status_column=None):
    header_fill = PatternFill("solid", fgColor="1F4E78")
    hit_fill = PatternFill("solid", fgColor="E2F0D9")
    miss_fill = PatternFill("solid", fgColor="FCE4D6")
    neutral_fill = PatternFill("solid", fgColor="E7E6E6")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        if status_column:
            status = row[status_column - 1].value
            fill = hit_fill if status in {"命中", "是"} else miss_fill if status in {"未命中", "否"} else neutral_fill
            for cell in row:
                cell.fill = fill
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width


def write_workbook(cve_rows, detail_rows, metrics):
    workbook = Workbook()
    workbook.remove(workbook.active)

    cve_sheet = workbook.create_sheet("CVE命中情况")
    cve_headers = [
        "cve_id",
        "project_slug",
        "evidence_count",
        "annotation_count",
        "file_matched_evidence_count",
        "position_matched_evidence_count",
        "matched_annotation_count",
        "hit_status",
        "included_in_accuracy",
        "hit_details",
        "reason",
    ]
    cve_sheet.append(cve_headers)
    for row in cve_rows:
        cve_sheet.append([row[column] for column in cve_headers])
    style_sheet(cve_sheet, [19, 40, 15, 17, 24, 28, 25, 18, 22, 85, 65], 8)

    detail_sheet = workbook.create_sheet("标注明细")
    detail_headers = [
        "cve_id",
        "dataset_row",
        "dataset_commit",
        "file",
        "class",
        "method",
        "signature",
        "range_type",
        "annotation_start",
        "annotation_end",
        "matched",
        "matched_evidence",
        "commit_equal",
        "same_file_but_no_overlap",
    ]
    detail_sheet.append(detail_headers)
    for row in detail_rows:
        detail_sheet.append([row[column] for column in detail_headers])
    style_sheet(
        detail_sheet,
        [19, 15, 43, 75, 24, 28, 42, 20, 18, 18, 14, 100, 16, 80],
        11,
    )

    summary = workbook.create_sheet("准确率与口径")
    summary.append(["指标", "数值", "说明"])
    rows = [
        ("成功 CVE 总数", metrics["success_cves"], "来自 success evidence Excel"),
        ("Evidence 总数", metrics["evidence_rows"], "成功 CVE 的全部 evidence"),
        ("可比较 CVE 数", metrics["comparable_cves"], "source_sink_detect.csv 中存在标注"),
        ("命中 CVE 数", metrics["hit_cves"], "至少一条 evidence 位置命中"),
        ("未命中 CVE 数", metrics["missed_cves"], "有标注但没有位置命中"),
        ("无标注 CVE 数", metrics["unlabeled_cves"], "不计入准确率"),
        ("CVE 级准确率", metrics["cve_accuracy"], "命中 CVE / 可比较 CVE"),
        ("可比较 Evidence 数", metrics["comparable_evidence"], "仅统计有数据集标注的 CVE"),
        ("命中 Evidence 数", metrics["matched_evidence"], "同 CVE、同文件且满足位置/方法名规则"),
        ("Evidence 命中率", metrics["evidence_hit_rate"], "命中 Evidence / 可比较 Evidence"),
        ("数据集标注数", metrics["annotations"], "可比较 CVE 的标注行数"),
        ("已覆盖标注数", metrics["matched_annotations"], "至少被一条 evidence 命中"),
        ("标注覆盖率", metrics["annotation_coverage"], "已覆盖标注 / 数据集标注"),
        (
            "位置命中规则",
            "CVE 与 file 必须一致；有 method_start/end 时按方法区间重叠；缺方法行号但有方法名时，要求 evidence.code 中出现该方法名；方法名也缺失时才回退 class_start/end；仍无位置时同文件即命中。",
            "区间端点按闭区间处理",
        ),
        (
            "Commit 规则",
            "commit 是否相同仅记录，不作为命中前提。",
            "evidence 同时包含 buggy/fix revision，而数据集通常只记录一个 commit",
        ),
    ]
    for row in rows:
        summary.append(row)
    for cell in (summary[7][1], summary[10][1], summary[13][1]):
        cell.number_format = "0.00%"
    style_sheet(summary, [30, 75, 95])

    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(OUTPUT_XLSX)


def verify(metrics):
    workbook = load_workbook(OUTPUT_XLSX, read_only=True, data_only=True)
    assert workbook.sheetnames == ["CVE命中情况", "标注明细", "准确率与口径"]
    assert workbook["CVE命中情况"].max_row - 1 == metrics["success_cves"]
    assert workbook["标注明细"].max_row - 1 == metrics["annotations"]


def main():
    cve_rows, detail_rows, metrics = compare()
    write_workbook(cve_rows, detail_rows, metrics)
    verify(metrics)
    print(
        f"wrote {OUTPUT_XLSX}; CVE accuracy="
        f"{metrics['hit_cves']}/{metrics['comparable_cves']}="
        f"{metrics['cve_accuracy']:.2%}"
    )


if __name__ == "__main__":
    main()
