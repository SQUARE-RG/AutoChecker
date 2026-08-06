import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from config import global_config as config


def code_check_root() -> Path:
    return Path(__file__).resolve().parents[2]


def python_executable() -> str:
    configured = str(config.get("file_paths", {}).get("python_env", "")).strip()
    if configured and configured != "python3" and Path(configured).exists():
        return configured
    return sys.executable


def resolve_semgrep_bin(semgrep_bin: str = "") -> str:
    candidate = str(semgrep_bin or config.get("file_paths", {}).get("semgrep", "")).strip()
    if not candidate:
        candidate = shutil.which("semgrep") or str(Path.home() / ".local/bin/semgrep")
    return candidate


def run_semgrep_rule_tool(
    sample_folder: str,
    requirement: str,
    target_language: str,
    output_dir: str,
    requirement_title: str = "",
    max_attempts: int | None = None,
    semgrep_bin: str = "",
    pattern_ir: bool = True,
    repair_mode: bool = True,
    request_timeout: float | None = None,
) -> tuple[int, str, str]:
    root = code_check_root()
    tool_path = root / "semgrep_prompt" / "v1" / "semgrep_rule_tool.py"
    if not tool_path.is_file():
        return 1, "", f"Semgrep rule tool not found: {tool_path}"

    attempts = max_attempts if max_attempts is not None else int(config.get("arguments", {}).get("max_round", 3) or 3)
    timeout = request_timeout if request_timeout is not None else float(config.get("arguments", {}).get("semgrep_request_timeout", 120) or 120)

    cmd = [
        python_executable(),
        str(tool_path),
        "--sample-folder",
        sample_folder,
        "--requirement",
        requirement,
        "--target-language",
        target_language,
        "--output-dir",
        output_dir,
        "--requirement-title",
        requirement_title or "semgrep-rule",
        "--max-attempts",
        str(attempts),
        "--request-timeout",
        str(timeout),
    ]

    resolved_semgrep = resolve_semgrep_bin(semgrep_bin)
    if resolved_semgrep:
        cmd.extend(["--semgrep-bin", resolved_semgrep])
    if not pattern_ir:
        cmd.append("--no-pattern-ir")
    if not repair_mode:
        cmd.append("--no-repair-mode")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(tool_path.parent) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(cmd, cwd=str(root), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def load_run_report(output_dir: str) -> dict[str, Any]:
    report_path = Path(output_dir) / "run_report.json"
    if not report_path.is_file():
        return {}
    with report_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def validate_semgrep_rule(rule_yaml_path: str, semgrep_bin: str = "") -> tuple[int, str, str, bool]:
    binary = resolve_semgrep_bin(semgrep_bin)
    proc = subprocess.run(
        [binary, "--validate", "--config", rule_yaml_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr, proc.returncode == 0
