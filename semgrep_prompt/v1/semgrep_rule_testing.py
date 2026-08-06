#!/usr/bin/env python3
"""Paired-sample Semgrep evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FunctionRegion:
    file_path: Path
    function_name: str
    label: str
    start_line: int
    end_line: int


def evaluate_semgrep_results(
    semgrep_output: dict[str, Any],
    truth_by_file: dict[str, list[FunctionRegion]],
    bad_total: int,
    good_total: int,
) -> dict[str, Any]:
    results = semgrep_output.get("results") if isinstance(semgrep_output.get("results"), list) else []

    hit_bad: set[tuple[str, str, int, int]] = set()
    hit_good: set[tuple[str, str, int, int]] = set()
    outside_findings: list[dict[str, Any]] = []

    findings_by_file: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        if not isinstance(item, dict):
            continue
        path_raw = item.get("path")
        if isinstance(path_raw, str):
            findings_by_file.setdefault(str(Path(path_raw).resolve()), []).append(item)

    for path, findings in findings_by_file.items():
        regions = truth_by_file.get(path, [])
        for finding in findings:
            start = finding.get("start") if isinstance(finding.get("start"), dict) else {}
            line = int(start.get("line", 0) or 0)
            matched = False
            for region in regions:
                if region.start_line <= line <= region.end_line:
                    key = (path, region.function_name, region.start_line, region.end_line)
                    if region.label == "bad":
                        hit_bad.add(key)
                    elif region.label == "good":
                        hit_good.add(key)
                    matched = True
                    break
            if not matched:
                outside_findings.append(
                    {
                        "path": path,
                        "line": line,
                        "check_id": finding.get("check_id", ""),
                    }
                )

    all_bad: list[tuple[str, str, int, int]] = []
    all_good: list[tuple[str, str, int, int]] = []
    for path, regions in truth_by_file.items():
        for region in regions:
            key = (path, region.function_name, region.start_line, region.end_line)
            if region.label == "bad":
                all_bad.append(key)
            elif region.label == "good":
                all_good.append(key)

    missed_bad = [item for item in all_bad if item not in hit_bad]
    flagged_good = [item for item in all_good if item in hit_good]

    bad_hit = len(hit_bad)
    good_hit = len(hit_good)
    bad_recall = bad_hit / bad_total if bad_total else 0.0
    good_fp_rate = good_hit / good_total if good_total else 0.0

    return {
        "passed": bad_total > 0 and good_total > 0 and bad_hit == bad_total and good_hit == 0,
        "bad_total": bad_total,
        "good_total": good_total,
        "bad_hit": bad_hit,
        "good_hit": good_hit,
        "bad_recall": round(bad_recall, 4),
        "good_false_positive_rate": round(good_fp_rate, 4),
        "missed_bad_count": len(missed_bad),
        "flagged_good_count": len(flagged_good),
        "outside_findings_count": len(outside_findings),
        "missed_bad_examples": [
            {
                "path": path,
                "function": fn,
                "start_line": start,
                "end_line": end,
            }
            for path, fn, start, end in missed_bad[:20]
        ],
        "flagged_good_examples": [
            {
                "path": path,
                "function": fn,
                "start_line": start,
                "end_line": end,
            }
            for path, fn, start, end in flagged_good[:20]
        ],
        "outside_findings_examples": outside_findings[:20],
        "semgrep_findings_total": len(results),
        "semgrep_runner": semgrep_output.get("_runner", {}),
        "semgrep_errors": semgrep_output.get("errors", []),
    }
