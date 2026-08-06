#!/usr/bin/env python3
"""Shared utilities for the formal Semgrep rule synthesis tool."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEMGREP_PROMPT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VALIDATE_TIMEOUT_SECONDS = 60.0
DEFAULT_SCAN_TIMEOUT_SECONDS = 60.0


@dataclass
class RuleTask:
    group: str
    title: str
    main_title: str
    description: str
    category: str
    negative_case_amount: int
    positive_case_amount: int
    success_case_list: list[str]
    failed_case_list: list[str]


def shorten(text: str, limit: int = 3500) -> str:
    value = (text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def slugify(text: str) -> str:
    out = re.sub(r"[^a-zA-Z0-9_-]+", "-", (text or "").strip().lower())
    out = re.sub(r"-+", "-", out).strip("-")
    return out or "rule"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_command(
    command: list[str],
    cwd: Path | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    started = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        returncode = 124
        timed_out = True

    return {
        "command": " ".join(command),
        "cwd": str(cwd) if cwd else str(Path.cwd()),
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def find_semgrep_bin(requested: str = "") -> str:
    if requested:
        return requested
    env_bin = os.environ.get("SEMGREP_BIN", "").strip()
    if env_bin:
        return env_bin
    which_bin = shutil.which("semgrep")
    if which_bin:
        return which_bin
    local_bin = Path.home() / ".local/bin/semgrep"
    if local_bin.exists():
        return str(local_bin)
    raise FileNotFoundError("Cannot find semgrep binary. Set --semgrep-bin or SEMGREP_BIN.")


def validate_rule_yaml(
    semgrep_bin: str,
    yaml_path: Path,
    timeout_seconds: float = DEFAULT_VALIDATE_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    result = run_command(
        [semgrep_bin, "--validate", "--config", str(yaml_path)],
        timeout_seconds=timeout_seconds,
    )
    result["ok"] = result["returncode"] == 0
    return result
