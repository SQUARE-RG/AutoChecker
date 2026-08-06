#!/usr/bin/env python3
"""Paired curated sample loading for Juliet interface runs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from semgrep_rule_testing import FunctionRegion


SAMPLE_SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".py",
    ".rs",
    ".ts",
    ".tsx",
}


def natural_sample_key(path: Path) -> tuple[int, str]:
    stem = path.stem.lower()
    match = re.search(r"(\d+)$", stem)
    if match:
        return (int(match.group(1)), stem)
    return (10**9, stem)


def sample_case_id(path: Path) -> str:
    return path.stem.strip().lower()


def collect_sample_side_files(side_dir: Path) -> dict[str, Path]:
    if not side_dir.exists() or not side_dir.is_dir():
        return {}
    out: dict[str, Path] = {}
    for path in sorted(side_dir.iterdir(), key=natural_sample_key):
        if not path.is_file() or path.suffix.lower() not in SAMPLE_SOURCE_EXTENSIONS:
            continue
        case_id = sample_case_id(path)
        if not case_id or case_id in out:
            continue
        out[case_id] = path.resolve()
    return out


def line_count(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 1
    return max(1, len(text.splitlines()))


def build_single_file_region(path: Path, label: str, case_id: str) -> FunctionRegion:
    return FunctionRegion(
        file_path=path,
        function_name=f"{label}_{case_id}",
        label=label,
        start_line=1,
        end_line=line_count(path),
    )


def load_paired_sample_suite(sample_folder: Path) -> dict[str, Any]:
    root = sample_folder.expanduser().resolve()
    bad_dir = root / "bad"
    good_dir = root / "good"
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"sample folder not found: {root}")
    if not bad_dir.exists() or not bad_dir.is_dir():
        raise FileNotFoundError(f"sample folder must contain bad/: {bad_dir}")
    if not good_dir.exists() or not good_dir.is_dir():
        raise FileNotFoundError(f"sample folder must contain good/: {good_dir}")

    bad_by_id = collect_sample_side_files(bad_dir)
    good_by_id = collect_sample_side_files(good_dir)
    if not bad_by_id:
        raise ValueError(f"sample folder has no bad/testN source files: {bad_dir}")

    eval_files: list[Path] = []
    truth_by_file: dict[str, list[FunctionRegion]] = {}
    pairs: list[dict[str, Any]] = []
    bad_total = 0
    good_total = 0

    for case_id, bad_path in sorted(bad_by_id.items(), key=lambda pair: natural_sample_key(pair[1])):
        bad_region = build_single_file_region(bad_path, "bad", case_id)
        eval_files.append(bad_path)
        truth_by_file[str(bad_path)] = [bad_region]
        bad_total += 1

        good_path = good_by_id.get(case_id)
        if good_path is None:
            continue
        good_region = build_single_file_region(good_path, "good", case_id)
        eval_files.append(good_path)
        truth_by_file[str(good_path)] = [good_region]
        good_total += 1
        pairs.append(
            {
                "trigger": "curated_pair",
                "case_id": case_id,
                "bad_example": {
                    "path": str(bad_path),
                    "function": bad_region.function_name,
                    "start_line": bad_region.start_line,
                    "end_line": bad_region.end_line,
                    "label": "bad",
                },
                "good_example": {
                    "path": str(good_path),
                    "function": good_region.function_name,
                    "start_line": good_region.start_line,
                    "end_line": good_region.end_line,
                    "label": "good",
                },
                "distinguish_requirement": "This numbered BAD/GOOD pair must be separated by vulnerability semantics.",
            }
        )

    return {
        "root": root,
        "bad_dir": bad_dir,
        "good_dir": good_dir,
        "all_files": list(eval_files),
        "eval_files": list(eval_files),
        "truth_by_file": truth_by_file,
        "bad_total": bad_total,
        "good_total": good_total,
        "counterexample_pairs": pairs,
    }
