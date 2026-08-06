from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import semgrep_tool_common as guardian
from llm_client import DEFAULT_LLM_API_KEY
from llm_client import DEFAULT_LLM_BASE_URL
from llm_client import DEFAULT_LLM_MODEL
from llm_client import LLMClient
from llm_client import create_llm_client
from llm_rule_generation import RequirementRunConfig
from llm_rule_generation import run_requirement_generation
from semgrep_rule_detection import extract_rule_yaml_from_interface_report
from semgrep_rule_detection import find_semgrep_bin
from semgrep_rule_detection import run_semgrep_json
from semgrep_rule_testing import evaluate_semgrep_results
from paired_sample_suite import load_paired_sample_suite
from sample_contrast_analyzer import analyze_pairs
from sample_contrast_analyzer import classify_eval_gaps
from sample_contrast_analyzer import render_contrast_for_prompt
from semgrep_repair_mode import RepairModeConfig
from semgrep_repair_mode import evaluate_repair_acceptance
from semgrep_repair_mode import run_semgrep_repair_mode


@dataclass
class ToolConfig:
    sample_folder: Path
    requirement: str
    target_language: str
    output_dir: Path
    requirement_title: str = "custom-semgrep-rule"
    max_attempts: int = 3
    max_invalid_retries: int = 5
    repair_mode: bool = True
    pattern_ir_enabled: bool = True
    max_contrast_pairs: int = 8
    semgrep_bin: str = ""
    validate_timeout_seconds: float = guardian.DEFAULT_VALIDATE_TIMEOUT_SECONDS
    scan_timeout_seconds: float = guardian.DEFAULT_SCAN_TIMEOUT_SECONDS
    request_timeout: float = 120.0
    request_retries: int = 2
    api_key: str = DEFAULT_LLM_API_KEY
    base_url: str = DEFAULT_LLM_BASE_URL
    model: str = DEFAULT_LLM_MODEL


@dataclass
class AttemptRecord:
    attempt: int
    mode: str
    counted: bool
    rule_yaml: str = ""
    eval_report: dict[str, Any] = field(default_factory=dict)
    generation_report: dict[str, Any] = field(default_factory=dict)
    repair_report: dict[str, Any] = field(default_factory=dict)
    repair_acceptance: dict[str, Any] = field(default_factory=dict)
    invalid_reason: str = ""


def _overall_correct(report: dict[str, Any]) -> int:
    return report["bad_hit"] + report["good_total"] - report["good_hit"]


def _eval_rank_key(report: dict[str, Any]) -> tuple[Any, ...]:
    bad_hit = report["bad_hit"]
    good_hit = report["good_hit"]
    overall_correct = _overall_correct(report)
    return (bad_hit, -good_hit, overall_correct)


def _score_display(report: dict[str, Any]) -> str:
    bad_total = report["bad_total"]
    good_total = report["good_total"]
    total = bad_total + good_total
    return f"{_overall_correct(report)}/{total}"


def _has_nonzero_hit(report: dict[str, Any]) -> bool:
    return report["bad_hit"] > 0 or report["good_hit"] > 0


def _all_zero_hit(report: dict[str, Any]) -> bool:
    return report["bad_hit"] == 0 and report["good_hit"] == 0


def _fully_clean(report: dict[str, Any]) -> bool:
    return int(report.get("missed_bad_count", 0) or 0) == 0 and int(report.get("flagged_good_count", 0) or 0) == 0


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _read_rule_text(rule_yaml: str) -> str:
    return Path(rule_yaml).expanduser().read_text(encoding="utf-8", errors="replace")


def _public_config(config: ToolConfig, output_dir: Path, semgrep_bin: str) -> dict[str, Any]:
    return {
        "sample_folder": str(config.sample_folder.expanduser().resolve()),
        "requirement": config.requirement,
        "target_language": config.target_language,
        "output_dir": str(output_dir),
        "requirement_title": config.requirement_title,
        "max_attempts": config.max_attempts,
        "max_invalid_retries": config.max_invalid_retries,
        "repair_mode": config.repair_mode,
        "pattern_ir_enabled": config.pattern_ir_enabled,
        "max_contrast_pairs": config.max_contrast_pairs,
        "semgrep_bin": semgrep_bin,
        "validate_timeout_seconds": config.validate_timeout_seconds,
        "scan_timeout_seconds": config.scan_timeout_seconds,
        "request_timeout": config.request_timeout,
        "request_retries": config.request_retries,
        "base_url": config.base_url,
        "model": config.model,
        "api_key": "<redacted>" if config.api_key else "",
    }


def build_formal_requirement(
    requirement: str,
    target_language: str,
    sample_suite: dict[str, Any],
    prev_eval: dict[str, Any] | None = None,
    coverage_rejected_repairs: list[dict[str, Any]] | None = None,
    precision_rejected_repairs: list[dict[str, Any]] | None = None,
) -> str:
    lines = [
        f"Requirement: {requirement.strip()}",
        f"Target language: {target_language.strip()}",
        "",
        "Generate exactly one Semgrep OSS rule for this requirement.",
        "Use the paired BAD/GOOD examples as contrastive evidence, not as examples to enumerate.",
        "Allowed semantic anchors include standard/library/framework/security API names, operators, type names, fields, source APIs, and sink APIs when they define the requirement.",
        "Avoid benchmark-only helper names, file paths, test ids, line numbers, and one branch per sample.",
        "Prefer taint mode only when there is real source-to-sink dataflow; prefer search mode for local structural/API/lifetime/sensitive-context checks.",
        "Repair priority is sequential: first improve missed BAD coverage, then lower GOOD false positives without reducing BAD hits.",
        "Coverage repair and precision repair are independent goals; do not trade away BAD hits when lowering GOOD false positives.",
    ]

    pairs = sample_suite["counterexample_pairs"]
    if pairs:
        analysis = analyze_pairs(pairs, max_pairs=int(sample_suite.get("contrast_pair_limit", 8)))
        lines.extend(["", "Paired BAD/GOOD contrast summary:"])
        lines.extend(render_contrast_for_prompt(analysis))

    if prev_eval:
        lines.extend(
            [
                "",
                "Previous evaluated rule feedback:",
                "- bad_hit={}/{}".format(prev_eval.get("bad_hit"), prev_eval.get("bad_total")),
                "- good_hit={}/{}".format(prev_eval.get("good_hit"), prev_eval.get("good_total")),
                f"- bad_recall={prev_eval.get('bad_recall')}",
                f"- good_false_positive_rate={prev_eval.get('good_false_positive_rate')}",
                f"- missed_bad_count={prev_eval.get('missed_bad_count')}",
                f"- flagged_good_count={prev_eval.get('flagged_good_count')}",
            ]
        )
        gap_analysis = prev_eval.get("gap_analysis", {})
        if gap_analysis:
            lines.extend(
                [
                    "",
                    "Gap analysis from the previous rule:",
                    guardian.shorten(json.dumps(gap_analysis, ensure_ascii=False, indent=2), 4200),
                ]
            )
        anchor = _read_rule_text(str(prev_eval["rule_yaml"]))
        if anchor:
            lines.extend(
                [
                    "",
                    "Previous useful rule anchor:",
                    guardian.shorten(anchor, 2400),
                    "Preserve useful branches from this rule unless they are clearly responsible for GOOD false positives.",
                ]
            )

    for title, memory in (
        ("Failed BAD coverage repairs to avoid repeating:", coverage_rejected_repairs or []),
        ("Failed GOOD precision repairs to avoid repeating:", precision_rejected_repairs or []),
    ):
        if not memory:
            continue
        lines.extend(["", title])
        for item in memory[-4:]:
            lines.append(
                "- focus={}; action={}; reason={}".format(
                    guardian.shorten(str(item.get("focus", "")), 80),
                    guardian.shorten(str(item.get("edit_action", "")), 80),
                    guardian.shorten(str(item.get("reason", "")), 360),
                )
            )

    return "\n".join(lines).strip()


def evaluate_rule(
    rule_yaml: Path,
    sample_suite: dict[str, Any],
    semgrep_bin: str,
    scan_timeout_seconds: float,
) -> dict[str, Any]:
    semgrep_output = run_semgrep_json(
        semgrep_bin=semgrep_bin,
        rule_yaml=rule_yaml,
        targets=[Path(path) for path in sample_suite["eval_files"]],
        timeout_seconds=float(scan_timeout_seconds),
    )
    report = evaluate_semgrep_results(
        semgrep_output=semgrep_output,
        truth_by_file=sample_suite["truth_by_file"],
        bad_total=int(sample_suite["bad_total"]),
        good_total=int(sample_suite["good_total"]),
    )
    report["rule_yaml"] = str(rule_yaml.resolve())
    report["score_display"] = _score_display(report)
    report["gap_analysis"] = classify_eval_gaps(report, _read_rule_text(str(rule_yaml)))
    return report


def run_fresh_generation(
    config: ToolConfig,
    sample_suite: dict[str, Any],
    semgrep_bin: str,
    attempt_dir: Path,
    prev_eval: dict[str, Any] | None,
    coverage_rejected_repairs: list[dict[str, Any]],
    precision_rejected_repairs: list[dict[str, Any]],
) -> tuple[dict[str, Any], Path | None]:
    requirement_text = build_formal_requirement(
        requirement=config.requirement,
        target_language=config.target_language,
        sample_suite={**sample_suite, "contrast_pair_limit": config.max_contrast_pairs},
        prev_eval=prev_eval,
        coverage_rejected_repairs=coverage_rejected_repairs,
        precision_rejected_repairs=precision_rejected_repairs,
    )
    (attempt_dir / "formal_requirement_prompt.txt").write_text(requirement_text, encoding="utf-8")
    report = run_requirement_generation(
        RequirementRunConfig(
            requirement_text=requirement_text,
            sample_files=[str(path) for path in sample_suite["eval_files"]],
            output_dir=str(attempt_dir / "generation"),
            requirement_title=config.requirement_title,
            target_language=config.target_language,
            validate_timeout_seconds=config.validate_timeout_seconds,
            scan_timeout_seconds=config.scan_timeout_seconds,
            request_timeout=config.request_timeout,
            request_retries=config.request_retries,
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            semgrep_bin=semgrep_bin,
            pattern_ir_enabled=config.pattern_ir_enabled,
        )
    )
    rule_yaml = extract_rule_yaml_from_interface_report(
        interface_report=report,
        semgrep_bin=semgrep_bin,
        validate_timeout_seconds=config.validate_timeout_seconds,
    )
    return report, rule_yaml


def run_repair_generation(
    config: ToolConfig,
    sample_suite: dict[str, Any],
    llm: LLMClient,
    semgrep_bin: str,
    attempt_dir: Path,
    base_eval: dict[str, Any],
    rejected_repairs: list[dict[str, Any]],
    forced_focus: str,
) -> dict[str, Any]:
    return run_semgrep_repair_mode(
        llm,
        RepairModeConfig(
            requirement_text=build_formal_requirement(
                requirement=config.requirement,
                target_language=config.target_language,
                sample_suite={**sample_suite, "contrast_pair_limit": config.max_contrast_pairs},
                prev_eval=base_eval,
            ),
            current_rule_yaml=Path(base_eval["rule_yaml"]).expanduser().resolve(),
            eval_files=[Path(path) for path in sample_suite["eval_files"]],
            truth_by_file=sample_suite["truth_by_file"],
            prev_eval=base_eval,
            output_dir=attempt_dir / "repair",
            semgrep_bin=semgrep_bin,
            validate_timeout_seconds=config.validate_timeout_seconds,
            scan_timeout_seconds=config.scan_timeout_seconds,
            rejected_repairs=list(rejected_repairs),
            forced_focus=forced_focus,
        ),
    )


def rejected_repair_memory_entry(
    repair_report: dict[str, Any],
    acceptance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    acceptance = acceptance or {}
    contract = repair_report.get("repair_edit_contract") if isinstance(repair_report.get("repair_edit_contract"), dict) else {}
    target = contract.get("localized_target") if isinstance(contract.get("localized_target"), dict) else {}
    return {
        "focus": str(repair_report.get("focus") or acceptance.get("repair_focus") or ""),
        "edit_action": str(repair_report.get("edit_action", "")),
        "localized_predicate": str(repair_report.get("localized_predicate", "")),
        "localized_target_summary": str(target.get("summary", "")),
        "reason": str(acceptance.get("reason") or repair_report.get("repair_skip_reason") or ""),
        "base_bad_hit": acceptance.get("base_bad_hit"),
        "candidate_bad_hit": acceptance.get("candidate_bad_hit"),
        "bad_gain": acceptance.get("bad_gain"),
        "base_good_hit": acceptance.get("base_good_hit"),
        "candidate_good_hit": acceptance.get("candidate_good_hit"),
        "good_fp_drop": acceptance.get("good_fp_drop"),
        "good_fp_increase": acceptance.get("good_fp_increase"),
        "overall_gain": acceptance.get("overall_gain"),
    }


def run_repair_step(
    config: ToolConfig,
    sample_suite: dict[str, Any],
    llm: LLMClient,
    semgrep_bin: str,
    step_dir: Path,
    base_eval: dict[str, Any],
    rejected_repairs: list[dict[str, Any]],
    forced_focus: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, Path | None, dict[str, Any]]:
    repair_report = run_repair_generation(
        config=config,
        sample_suite=sample_suite,
        llm=llm,
        semgrep_bin=semgrep_bin,
        attempt_dir=step_dir,
        base_eval=base_eval,
        rejected_repairs=rejected_repairs,
        forced_focus=forced_focus,
    )
    if bool(repair_report.get("repair_skipped", False)):
        acceptance = {
            "accepted": False,
            "reason": str(repair_report.get("repair_skip_reason") or "repair skipped"),
            "repair_focus": forced_focus,
        }
        return repair_report, None, None, acceptance

    rule_raw = str(repair_report.get("candidate_rule_yaml", "")).strip()
    rule_yaml = Path(rule_raw).expanduser().resolve() if rule_raw else None
    validation = repair_report.get("validation") if isinstance(repair_report.get("validation"), dict) else {}
    if rule_yaml is None or not rule_yaml.is_file():
        acceptance = {
            "accepted": False,
            "reason": str(validation.get("stderr") or validation.get("stdout") or "no valid repair candidate"),
            "repair_focus": forced_focus,
        }
        return repair_report, None, None, acceptance

    eval_report = evaluate_rule(
        rule_yaml=rule_yaml,
        sample_suite=sample_suite,
        semgrep_bin=semgrep_bin,
        scan_timeout_seconds=config.scan_timeout_seconds,
    )
    acceptance = evaluate_repair_acceptance(
        base_eval=base_eval,
        candidate_eval=eval_report,
        repair_focus=forced_focus,
    )
    eval_report["repair_acceptance"] = acceptance
    return repair_report, eval_report, rule_yaml, acceptance


def run_two_step_repair_attempt(
    config: ToolConfig,
    sample_suite: dict[str, Any],
    llm: LLMClient,
    semgrep_bin: str,
    attempt_dir: Path,
    base_eval: dict[str, Any],
    coverage_rejected_repairs: list[dict[str, Any]],
    precision_rejected_repairs: list[dict[str, Any]],
) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    current_eval = dict(base_eval)
    current_rule = Path(str(base_eval["rule_yaml"])).expanduser().resolve()
    steps: list[dict[str, Any]] = []
    combined_report: dict[str, Any] = {
        "mode": "two_step_repair",
        "validation_ok": True,
        "focus": "coverage_then_precision",
        "candidate_rule_yaml": str(current_rule),
        "steps": steps,
    }

    for step_name, focus, rejected_memory in (
        ("coverage", "too_narrow_coverage", coverage_rejected_repairs),
        ("precision", "too_broad_precision", precision_rejected_repairs),
    ):
        print(f"[semgrep_rule_tool] repair {step_name}: {focus}", flush=True)
        step_report, candidate_eval, candidate_rule, acceptance = run_repair_step(
            config=config,
            sample_suite=sample_suite,
            llm=llm,
            semgrep_bin=semgrep_bin,
            step_dir=attempt_dir / step_name,
            base_eval=current_eval,
            rejected_repairs=rejected_memory,
            forced_focus=focus,
        )
        step_record = {
            "step": step_name,
            "focus": focus,
            "accepted": bool(acceptance.get("accepted", False)),
            "acceptance": acceptance,
            "repair_report": step_report,
            "candidate_eval": candidate_eval or {},
            "candidate_rule_yaml": str(candidate_rule) if candidate_rule else "",
        }
        steps.append(step_record)
        if bool(acceptance.get("accepted", False)) and candidate_eval is not None and candidate_rule is not None:
            current_eval = candidate_eval
            current_rule = candidate_rule
            combined_report["candidate_rule_yaml"] = str(current_rule)
        else:
            rejected_memory.append(rejected_repair_memory_entry(step_report, acceptance))

    combined_report["validation_ok"] = True
    combined_report["final_rule_yaml"] = str(current_rule)
    combined_report["final_eval"] = current_eval
    return combined_report, current_rule, current_eval


def run_tool(config: ToolConfig) -> dict[str, Any]:
    output_dir = config.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    semgrep_bin = find_semgrep_bin(config.semgrep_bin)
    sample_suite = load_paired_sample_suite(config.sample_folder)
    llm = create_llm_client(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model,
        request_timeout=config.request_timeout,
        request_retries=config.request_retries,
    )

    guardian.write_json(
        output_dir / "tool_config.json",
        _public_config(config=config, output_dir=output_dir, semgrep_bin=semgrep_bin),
    )
    guardian.write_json(
        output_dir / "sample_suite_summary.json",
        {
            "sample_root": str(sample_suite["root"]),
            "bad_total": sample_suite["bad_total"],
            "good_total": sample_suite["good_total"],
            "eval_files": [str(path) for path in sample_suite["eval_files"]],
        },
    )

    attempts: list[AttemptRecord] = []
    counted_attempts = 0
    invalid_retries = 0
    previous_eval: dict[str, Any] | None = None
    coverage_rejected_repairs: list[dict[str, Any]] = []
    precision_rejected_repairs: list[dict[str, Any]] = []

    while counted_attempts < config.max_attempts:
        attempt_no = counted_attempts + 1
        attempt_dir = output_dir / f"attempt_{attempt_no}"
        attempt_dir.mkdir(parents=True, exist_ok=True)

        use_repair = (
            bool(config.repair_mode)
            and previous_eval is not None
            and _has_nonzero_hit(previous_eval)
            and not _fully_clean(previous_eval)
            and Path(str(previous_eval["rule_yaml"])).expanduser().is_file()
        )

        if use_repair:
            print(f"[semgrep_rule_tool] attempt {attempt_no}: two-step repair from previous valid rule", flush=True)
            repair_report, rule_yaml, eval_report = run_two_step_repair_attempt(
                config=config,
                sample_suite=sample_suite,
                llm=llm,
                semgrep_bin=semgrep_bin,
                attempt_dir=attempt_dir,
                base_eval=previous_eval,
                coverage_rejected_repairs=coverage_rejected_repairs,
                precision_rejected_repairs=precision_rejected_repairs,
            )
            generation_report = {
                "mode": "two_step_repair",
                "success": True,
                "final_report": {
                    "round_counted": True,
                    "validation": {"ok": True},
                },
            }
            mode = "repair"
        else:
            print(f"[semgrep_rule_tool] attempt {attempt_no}: fresh generation", flush=True)
            repair_report = {}
            generation_report, rule_yaml = run_fresh_generation(
                config=config,
                sample_suite=sample_suite,
                semgrep_bin=semgrep_bin,
                attempt_dir=attempt_dir,
                prev_eval=previous_eval,
                coverage_rejected_repairs=coverage_rejected_repairs,
                precision_rejected_repairs=precision_rejected_repairs,
            )
            mode = "fresh"

        final_report = generation_report.get("final_report", {})
        validation = final_report.get("validation", {})
        if rule_yaml is None or not Path(rule_yaml).is_file():
            invalid_retries += 1
            reason = str(validation.get("stderr") or validation.get("stdout") or generation_report.get("error") or "no valid rule yaml")
            print(
                "[semgrep_rule_tool] invalid YAML/rule; attempt not counted "
                f"(retry {invalid_retries}/{config.max_invalid_retries}): {guardian.shorten(reason, 700)}",
                flush=True,
            )
            attempts.append(
                AttemptRecord(
                    attempt=attempt_no,
                    mode=mode,
                    counted=False,
                    generation_report=generation_report,
                    repair_report=repair_report,
                    invalid_reason=reason,
                )
            )
            if mode == "repair":
                focus = str(repair_report.get("focus") or "")
                memory = coverage_rejected_repairs if focus == "too_narrow_coverage" else precision_rejected_repairs
                memory.append(rejected_repair_memory_entry(repair_report))
            if invalid_retries >= config.max_invalid_retries:
                break
            continue

        if not use_repair:
            eval_report = evaluate_rule(
                rule_yaml=Path(rule_yaml),
                sample_suite=sample_suite,
                semgrep_bin=semgrep_bin,
                scan_timeout_seconds=config.scan_timeout_seconds,
            )
        eval_report["attempt"] = attempt_no
        eval_report["generation_mode"] = mode

        repair_acceptance: dict[str, Any] = {}
        if mode == "repair":
            repair_acceptance = {
                "accepted": any(bool(step.get("accepted", False)) for step in repair_report.get("steps", [])),
                "repair_focus": "coverage_then_precision",
                "steps": [
                    {
                        "step": step.get("step"),
                        "focus": step.get("focus"),
                        "accepted": step.get("accepted"),
                        "reason": (step.get("acceptance") or {}).get("reason"),
                    }
                    for step in repair_report.get("steps", [])
                ],
            }
            eval_report["repair_acceptance"] = repair_acceptance

        counted_attempts += 1
        invalid_retries = 0
        previous_eval = eval_report
        guardian.write_json(attempt_dir / "eval_report.json", eval_report)
        attempts.append(
            AttemptRecord(
                attempt=attempt_no,
                mode=str(eval_report.get("generation_mode") or mode),
                counted=True,
                rule_yaml=str(rule_yaml),
                eval_report=eval_report,
                generation_report=generation_report,
                repair_report=repair_report,
                repair_acceptance=repair_acceptance,
            )
        )
        print(
            "[semgrep_rule_tool] attempt {} counted: score={} bad={}/{} good_fp={}/{}".format(
                attempt_no,
                eval_report.get("score_display"),
                eval_report.get("bad_hit"),
                eval_report.get("bad_total"),
                eval_report.get("good_hit"),
                eval_report.get("good_total"),
            ),
            flush=True,
        )

        if _fully_clean(eval_report):
            print("[semgrep_rule_tool] no missed BAD or flagged GOOD; stopping early", flush=True)
            break

        if _all_zero_hit(eval_report):
            previous_eval = None

    counted_records = [record for record in attempts if record.counted and record.eval_report]
    best_record = max(counted_records, key=lambda record: _eval_rank_key(record.eval_report)) if counted_records else None
    final_rule_path = ""
    best_eval: dict[str, Any] = {}
    if best_record is not None and best_record.rule_yaml:
        src = Path(best_record.rule_yaml).expanduser().resolve()
        final_path = output_dir / "final_rule.yml"
        _copy_file(src, final_path)
        final_rule_path = str(final_path.resolve())
        best_eval = dict(best_record.eval_report)
        best_eval["final_rule_yaml"] = final_rule_path

    rejected_repairs = coverage_rejected_repairs + precision_rejected_repairs
    report = {
        "mode": "formal_single_requirement_tool",
        "output_dir": str(output_dir),
        "semgrep_bin": semgrep_bin,
        "model": config.model,
        "requirement_title": config.requirement_title,
        "target_language": config.target_language,
        "sample_folder": str(config.sample_folder.expanduser().resolve()),
        "bad_total": sample_suite["bad_total"],
        "good_total": sample_suite["good_total"],
        "counted_attempts": counted_attempts,
        "invalid_retries_at_stop": invalid_retries,
        "final_rule_yaml": final_rule_path,
        "best_eval": best_eval,
        "attempts": [asdict(record) for record in attempts],
        "coverage_rejected_repairs": coverage_rejected_repairs,
        "precision_rejected_repairs": precision_rejected_repairs,
        "rejected_repairs": rejected_repairs,
    }
    guardian.write_json(output_dir / "run_report.json", report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and repair one Semgrep rule from paired BAD/GOOD samples.")
    parser.add_argument("--sample-folder", required=True, help="Folder containing bad/testN.* and good/testN.* paired samples.")
    parser.add_argument("--requirement", required=True, help="Natural-language rule requirement.")
    parser.add_argument("--target-language", required=True, help="Semgrep language id, for example c, cpp, python, javascript, go, java.")
    parser.add_argument("--output-dir", required=True, help="Directory for final_rule.yml, run_report.json, and attempt artifacts.")
    parser.add_argument("--requirement-title", default="custom-semgrep-rule")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--max-invalid-retries", type=int, default=5)
    parser.add_argument("--max-contrast-pairs", type=int, default=8)
    parser.add_argument("--repair-mode", dest="repair_mode", action="store_true", default=True)
    parser.add_argument("--no-repair-mode", dest="repair_mode", action="store_false")
    parser.add_argument("--pattern-ir", dest="pattern_ir_enabled", action="store_true", default=True)
    parser.add_argument("--no-pattern-ir", dest="pattern_ir_enabled", action="store_false")
    parser.add_argument("--semgrep-bin", default="")
    parser.add_argument("--validate-timeout-seconds", type=float, default=guardian.DEFAULT_VALIDATE_TIMEOUT_SECONDS)
    parser.add_argument("--scan-timeout-seconds", type=float, default=guardian.DEFAULT_SCAN_TIMEOUT_SECONDS)
    parser.add_argument("--request-timeout", type=float, default=120.0)
    parser.add_argument("--request-retries", type=int, default=2)
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY", DEFAULT_LLM_API_KEY))
    parser.add_argument("--base-url", default=os.environ.get("LLM_BASE_URL", DEFAULT_LLM_BASE_URL))
    parser.add_argument("--model", default=os.environ.get("LLM_MODEL", DEFAULT_LLM_MODEL))
    args = parser.parse_args()
    if args.max_attempts < 1:
        parser.error("--max-attempts must be >= 1")
    if args.max_invalid_retries < 1:
        parser.error("--max-invalid-retries must be >= 1")
    if args.max_contrast_pairs < 1:
        parser.error("--max-contrast-pairs must be >= 1")
    if args.validate_timeout_seconds <= 0:
        parser.error("--validate-timeout-seconds must be > 0")
    if args.scan_timeout_seconds <= 0:
        parser.error("--scan-timeout-seconds must be > 0")
    if args.request_timeout <= 0:
        parser.error("--request-timeout must be > 0")
    if args.request_retries < 0:
        parser.error("--request-retries must be >= 0")
    return args


def main() -> int:
    args = parse_args()
    config = ToolConfig(
        sample_folder=Path(args.sample_folder),
        requirement=str(args.requirement),
        target_language=str(args.target_language),
        output_dir=Path(args.output_dir),
        requirement_title=str(args.requirement_title),
        max_attempts=args.max_attempts,
        max_invalid_retries=args.max_invalid_retries,
        repair_mode=bool(args.repair_mode),
        pattern_ir_enabled=bool(args.pattern_ir_enabled),
        max_contrast_pairs=args.max_contrast_pairs,
        semgrep_bin=str(args.semgrep_bin or ""),
        validate_timeout_seconds=float(args.validate_timeout_seconds),
        scan_timeout_seconds=float(args.scan_timeout_seconds),
        request_timeout=float(args.request_timeout),
        request_retries=args.request_retries,
        api_key=str(args.api_key or ""),
        base_url=str(args.base_url or ""),
        model=str(args.model or ""),
    )
    report = run_tool(config)
    best = report["best_eval"]
    print(
        "[semgrep_rule_tool] done: final_rule={} score={} bad={}/{} good_fp={}/{}".format(
            report.get("final_rule_yaml") or "(none)",
            best.get("score_display") or "0/0",
            best.get("bad_hit", 0),
            best.get("bad_total", report["bad_total"]),
            best.get("good_hit", 0),
            best.get("good_total", report["good_total"]),
        ),
        flush=True,
    )
    return 0 if report.get("final_rule_yaml") else 1


if __name__ == "__main__":
    raise SystemExit(main())
