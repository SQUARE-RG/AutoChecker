#!/usr/bin/env python3
"""Semgrep rule detection/validation helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import semgrep_tool_common as guardian


def find_semgrep_bin(requested: str = "") -> str:
    return guardian.find_semgrep_bin(requested)


def validate_rule_yaml(
    semgrep_bin: str,
    yaml_path: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    return guardian.validate_rule_yaml(semgrep_bin=semgrep_bin, yaml_path=yaml_path, timeout_seconds=timeout_seconds)


def run_semgrep_json(
    semgrep_bin: str,
    rule_yaml: Path,
    targets: list[Path],
    timeout_seconds: float,
) -> dict[str, Any]:
    cmd = [
        semgrep_bin,
        "--json",
        "--metrics=off",
        "--timeout",
        "0",
        "--config",
        str(rule_yaml),
    ]
    cmd.extend(str(path) for path in targets)

    try:
        run = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        stdout = run.stdout
        stderr = run.stderr
        returncode = run.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        returncode = 124
        timed_out = True

    try:
        payload = json.loads(stdout or "{}")
        if not isinstance(payload, dict):
            payload = {
                "results": [],
                "errors": [
                    {
                        "type": "json_shape_error",
                        "message": "Semgrep JSON stdout is not an object",
                    }
                ],
            }
    except json.JSONDecodeError:
        payload = {
            "results": [],
            "errors": [
                {
                    "type": "json_decode_error",
                    "message": "Cannot parse semgrep stdout",
                }
            ],
        }

    payload["_runner"] = {
        "command": " ".join(cmd),
        "returncode": returncode,
        "stderr": stderr,
        "timed_out": timed_out,
    }
    return payload


def extract_rule_yaml_from_interface_report(
    interface_report: dict[str, Any],
    semgrep_bin: str = "",
    validate_timeout_seconds: float = guardian.DEFAULT_VALIDATE_TIMEOUT_SECONDS,
    require_validate: bool = True,
) -> Path | None:
    summaries = interface_report.get("summaries", [])
    if not summaries:
        return None

    first = summaries[0]
    rule_dir_raw = first.get("rule_dir", "")
    if not rule_dir_raw:
        return None

    rule_dir = Path(rule_dir_raw)
    final_report = first.get("final_report", {})
    round_id = int(final_report.get("round", 1) or 1)

    semgrep_bin_raw = str(semgrep_bin or interface_report.get("semgrep_bin") or "").strip()
    if require_validate and not semgrep_bin_raw:
        semgrep_bin_raw = find_semgrep_bin("")

    candidates: list[Path] = []
    candidates.append(rule_dir / f"attempt_{round_id}" / "generated_rule.yml")
    candidates.append(rule_dir / "generated_rule.yml")
    candidates.extend(sorted(rule_dir.glob("attempt_*/generated_rule.yml")))

    seen: set[str] = set()
    for path in candidates:
        if not path.is_file():
            continue
        resolved = path.resolve()
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)

        if not require_validate:
            return resolved

        validation = validate_rule_yaml(
            semgrep_bin=semgrep_bin_raw,
            yaml_path=resolved,
            timeout_seconds=float(validate_timeout_seconds),
        )
        if bool(validation.get("ok", False)):
            return resolved
    return None
