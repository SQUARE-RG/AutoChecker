#!/usr/bin/env python3
"""Direct LLM generation module for requirement-driven Semgrep rule synthesis.

This module is intentionally thin.  The Juliet/GJB runner already owns sample
selection, contrast analysis, iteration feedback, and full evaluation.  The
interface here should only turn one prepared requirement prompt into one
Semgrep YAML rule, validate it, and report enough detail for the outer runner to
decide whether the attempt counts.
"""

from __future__ import annotations

import traceback
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from llm_client import DEFAULT_LLM_API_KEY
from llm_client import DEFAULT_LLM_BASE_URL
from llm_client import DEFAULT_LLM_MODEL
from llm_client import LLMClient
from llm_client import create_llm_client
from pattern_ir_generation import generate_pattern_ir
import semgrep_tool_common as guardian
from semgrep_rule_yaml_utils import normalize_yaml


REFERENCE_SKILL_DOC = guardian.SEMGREP_PROMPT_ROOT / "docs/semgrep_rule_generation_skill.md"


@dataclass
class RequirementRunConfig:
    requirement_text: str
    sample_files: list[str]
    output_dir: str
    requirement_title: str = "custom-requirement"
    target_language: str = "cpp"
    validate_timeout_seconds: float = guardian.DEFAULT_VALIDATE_TIMEOUT_SECONDS
    scan_timeout_seconds: float = guardian.DEFAULT_SCAN_TIMEOUT_SECONDS
    request_timeout: float = 120.0
    request_retries: int = 2
    api_key: str = DEFAULT_LLM_API_KEY
    base_url: str = DEFAULT_LLM_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    semgrep_bin: str = ""
    pattern_ir_enabled: bool = True


def read_samples_bundle(sample_files: list[str], limit_per_file: int = 6000) -> str:
    blocks: list[str] = []
    for raw in sample_files:
        path = Path(raw).expanduser().resolve()
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            blocks.append(f"[sample_read_error] {path}: {exc}")
            continue
        blocks.append(f"[sample_file] {path}\n{guardian.shorten(content, limit=limit_per_file)}")
    if not blocks:
        return "(no sample files provided)"
    return "\n\n".join(blocks)


def build_custom_task(requirement_text: str, requirement_title: str) -> guardian.RuleTask:
    title = (requirement_title or "custom-requirement").strip()
    main_title = guardian.slugify(title)
    return guardian.RuleTask(
        group="custom",
        title=title,
        main_title=main_title,
        description=(requirement_text or "").strip(),
        category="custom",
        negative_case_amount=0,
        positive_case_amount=0,
        success_case_list=[],
        failed_case_list=[],
    )


def build_reference_bundle() -> tuple[str, list[dict[str, Any]]]:
    path = REFERENCE_SKILL_DOC
    record: dict[str, Any] = {
        "path": str(path),
        "name": path.name,
        "budget_chars": 0,
        "exists": path.exists() and path.is_file(),
    }
    if not path.exists() or not path.is_file():
        record.update({"source_chars": 0, "included_chars": 0, "truncated": False})
        return f"[missing:{path.name}]\n{path}", [record]
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as exc:
        record.update({"source_chars": 0, "included_chars": 0, "truncated": False, "error": str(exc)})
        return f"[read_error:{path.name}]\n{exc}", [record]
    record.update({"source_chars": len(text), "included_chars": len(text), "truncated": False})
    bundle = "\n".join(
        [
            "[reference_bundle_policy]",
            "Only the distilled Semgrep rule-generation skill is passed to the LLM. Raw official docs and auxiliary skill notes are source material, not prompt payload.",
            "",
            f"[{path.name}] source_chars={len(text)} included_chars={len(text)} truncated=false",
            text,
        ]
    )
    return bundle.strip(), [record]


def direct_rule_generation_prompt(
    requirement_text: str,
    sample_bundle: str,
    docs_bundle: str,
    pattern_ir_contract: str,
    target_language: str = "cpp",
) -> str:
    target = (target_language or "cpp").strip()
    target_lower = target.lower()
    c_cpp_specific_policy = ""
    if target_lower in {"c", "cpp", "c++", "cxx", "cc"}:
        c_cpp_specific_policy = """C/C++ parse-safety policy:
- prefer complete consumed statements/expressions over bare subexpression triggers
- when paired evidence exposes concrete C/C++ type tokens, use them directly in a small pattern-either; do not use $TYPE or $CAST metavariables in type, cast, or sizeof(...) positions
- if a BAD signal sits inside a carrier line, match the outer carrier statement/expression; do not promote an inner arithmetic/cast/dereference fragment to the whole trigger
- bare subexpression patterns such as `$P + sizeof($T)` are unreliable when the BAD code nests that expression inside an initializer, assignment, return, condition, dereference, or call argument; match the full carrier statement/expression
- Semgrep metavariable names do not impose C/C++ types; `$INT`, `$FLOAT`, `$PTR`, and `$TYPE` are only names unless constrained by concrete type syntax, supported type operators, or local declarations
- do not use `$TYPE $VAR = ...;` as a generic C/C++ declaration matcher; if the declaration type matters, use concrete type branches, otherwise match the RHS/cast expression or surrounding carrier
- any metavariable inside `sizeof(...)`, for example `sizeof($T)` or `sizeof($TYPE)`, is treated as invalid here; use concrete types from evidence, `sizeof(*$PTR)`, or a short regex fallback around the full carrier
- do not use all-metavariable assignment/arithmetic as the whole trigger, such as `$INT $V = $EXPR;`, `$V = $EXPR;`, or `$P1 - $P2`, unless the same branch also has concrete BAD-only context
- if a pattern begins with `*` or `&`, emit it with `pattern: |` rather than a bare scalar
- avoid parser-fragile anonymous C/C++ record snippets as AST patterns, such as `struct {{ ... }};` or `union {{ ... }};`; prefer a smaller parse-safe structural trigger and use regex only if necessary
"""
    else:
        c_cpp_specific_policy = """Language parse-safety policy:
- use parseable Semgrep patterns for the target language and match complete local statements/expressions where possible
- preserve meaningful library/framework API names, operators, fields, decorators/annotations, or method names when they define the risk
- avoid C/C++-specific type, pointer, cast, `sizeof`, or declaration patterns unless the target language is C/C++
"""
    return f"""You are generating one Semgrep OSS rule for the target language: {target}.

Return STRICT JSON only with these keys:
- semgrep_rule_yaml: string containing a complete YAML file
- notes: short string

YAML requirements:
- top-level `rules:` with exactly one rule
- include `id`, `message`, `severity`, and `languages`
- `languages` must match the target language `{target}` using Semgrep language ids
- use only valid Semgrep OSS syntax
- do not use YAML anchors or aliases
- do not return alternatives, candidates, fallback rules, or sample-specific line/test-name logic

Rule-shape policy:
- classify the requirement before writing YAML: source-sink flow, sensitive sink context, structural misuse, API misuse, or lifetime/order misuse
- use taint mode when a real trust-boundary source reaches a concrete sink across statements; use search mode for local structural/API/lifetime/sensitive-context checks
- use the Pattern-IR contract as a semantic planning layer, not as sample enumeration and not as a mandatory taint-mode instruction
- if Pattern-IR recommends search mode, taint-only fields may be empty; represent the rule with search-mode structural/sensitive/API branches instead of inventing fake taint sources
- if Pattern-IR conflicts with paired BAD/GOOD evidence or Semgrep feasibility, prefer the evidence and produce the most local Semgrep-expressible rule
- concrete standard/library/framework/security API names, operators, type names, field names, source APIs, and sink APIs from the requirement or paired examples are allowed when they carry the semantic distinction
- do not anchor on user-defined helper/wrapper names just because they appear in samples; use a wrapper only when its visible body is itself the local semantic evidence
- do not over-abstract meaningful evidence into placeholders; a compact evidence-backed rule is better than a generic rule that Semgrep cannot match
- do not put independent carrier alternatives in one `patterns:` list; `patterns:` is AND, so alternative writes/calls/carriers must be rule-level `pattern-either` siblings
- before BAD recall reaches the requested floor, favor coverage branches for real missed BAD carriers/API/operator/type evidence; keep FP bounded, but do not choose a tiny zero-FP subset that misses many BAD examples
- use `pattern-regex` only as a last-resort local fallback for lexical/parser-fragile surfaces; do not use regex as the default strategy or to emulate broad dataflow/type analysis
- a sibling `pattern-not` is not an ordered absence check; it cannot prove that a reset/check/cast does not occur later
- every `pattern-not` must be a scalar pattern and must only use metavariables already bound in the same positive branch, unless it is fully concrete syntax
- do not nest `pattern-either` under `pattern-either`
- for `pattern-regex`, prefer single-quoted scalar strings for one-line regexes, or `|-` block scalars when a block is necessary
- in `pattern-regex`, use portable classes such as `[A-Za-z_][A-Za-z0-9_]*`; avoid POSIX bracket classes such as `[[:space:]]` and `[[:alnum:]]`
- in taint mode, side-effect sources/sanitizers must include the API pattern, `focus-metavariable`, and `by-side-effect: true` in the same entry
- in taint mode, propagators must include explicit `from` and `to`

{c_cpp_specific_policy}

Prepared requirement and iteration feedback:
{guardian.shorten(requirement_text, 9000)}

Pattern-IR compact contract:
{guardian.shorten(pattern_ir_contract, 5000)}

Paired sample context:
{guardian.shorten(sample_bundle, 5000)}

Semgrep syntax reference:
{docs_bundle}
"""


def direct_yaml_repair_prompt(requirement_text: str, generated_yaml: str, validation_stderr: str) -> str:
    return f"""Repair this Semgrep YAML without changing the intended detection semantics.

Return STRICT JSON only with key:
- semgrep_rule_yaml: string containing one complete YAML file

Validation error:
{guardian.shorten(validation_stderr, 2200)}

Original requirement summary:
{guardian.shorten(requirement_text, 3200)}

Current YAML:
{guardian.shorten(generated_yaml, 5000)}

Rules:
- fix only YAML, parse, or Semgrep schema problems
- keep exactly one rule under top-level `rules:`
- do not introduce candidates, alternatives, or offline fallback logic
- if the error involves `pattern-either`/`patterns`, flatten to a valid Semgrep shape
- if a `patterns:` list contains independent alternative carriers, split them into rule-level `pattern-either` sibling branches instead of preserving an accidental AND
- if `pattern-not` has fresh metavariables, bind them in the same positive branch or remove the invalid exclusion
- if a C/C++ pattern starts with `*` or `&`, use `pattern: |`
- if Semgrep rejects an anonymous `struct`/`union` declaration pattern, replace that branch with a tight `pattern-regex` instead of another declaration AST pattern
"""


def _extract_generated_yaml(payload: dict[str, Any]) -> str:
    raw = payload.get("semgrep_rule_yaml")
    if isinstance(raw, str):
        return normalize_yaml(raw)
    if isinstance(raw, dict):
        return normalize_yaml(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False))
    return normalize_yaml(str(raw or ""))


def _payload_error_reason(payload: dict[str, Any]) -> str:
    if not payload:
        return "empty_llm_payload: response did not contain a JSON object"
    if "semgrep_rule_yaml" in payload:
        return ""
    object_type = str(payload.get("object") or "").strip()
    choices = payload.get("choices")
    if object_type.startswith("chat.completion") and isinstance(choices, list) and not choices:
        return "empty_llm_payload: chat completion returned choices=[] and no semgrep_rule_yaml"
    return "invalid_llm_payload: missing semgrep_rule_yaml"


def _direct_generate_once(
    llm: LLMClient,
    semgrep_bin: str,
    requirement_text: str,
    sample_bundle: str,
    docs_bundle: str,
    pattern_ir_contract: str,
    rule_dir: Path,
    validate_timeout_seconds: float,
    target_language: str = "cpp",
) -> dict[str, Any]:
    attempt_dir = rule_dir / "attempt_1"
    attempt_dir.mkdir(parents=True, exist_ok=True)

    prompt = direct_rule_generation_prompt(
        requirement_text=requirement_text,
        sample_bundle=sample_bundle,
        docs_bundle=docs_bundle,
        pattern_ir_contract=pattern_ir_contract,
        target_language=target_language,
    )
    (attempt_dir / "direct_generation_prompt.txt").write_text(prompt, encoding="utf-8")

    payload: dict[str, Any] = {}
    raw_error = ""
    try:
        payload = llm.ask_json(prompt, retries=2)
    except Exception as exc:
        raw_error = f"llm_json_generation_error: {exc}"
        payload = {}

    guardian.write_json(attempt_dir / "generated_payload.json", payload)
    payload_error = _payload_error_reason(payload)
    if payload_error:
        raw_error = f"{payload_error}; {raw_error}" if raw_error else payload_error
    yaml_text = "" if payload_error else _extract_generated_yaml(payload)
    yaml_path = attempt_dir / "generated_rule.yml"
    yaml_path.write_text(yaml_text, encoding="utf-8")

    if yaml_text.strip():
        validation = guardian.validate_rule_yaml(
            semgrep_bin=semgrep_bin,
            yaml_path=yaml_path,
            timeout_seconds=float(validate_timeout_seconds),
        )
    else:
        validation = {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": raw_error or "empty semgrep_rule_yaml",
            "timed_out": False,
        }
    repaired = False

    if (not validation.get("ok")) and yaml_text.strip():
        validation_stderr = str(validation.get("stderr") or validation.get("stdout") or "")
        print(
            "[direct_generation] invalid Semgrep YAML; attempting one syntax repair. error={}".format(
                guardian.shorten(validation_stderr.replace("\n", " "), 500)
            ),
            flush=True,
        )
        repair_prompt = direct_yaml_repair_prompt(
            requirement_text=requirement_text,
            generated_yaml=yaml_text,
            validation_stderr=validation_stderr,
        )
        (attempt_dir / "direct_repair_prompt.txt").write_text(repair_prompt, encoding="utf-8")
        try:
            repaired_payload = llm.ask_json(repair_prompt, retries=1)
            guardian.write_json(attempt_dir / "repaired_payload.json", repaired_payload)
            repaired_yaml = _extract_generated_yaml(repaired_payload)
            if repaired_yaml.strip():
                yaml_path.write_text(repaired_yaml, encoding="utf-8")
                validation = guardian.validate_rule_yaml(
                    semgrep_bin=semgrep_bin,
                    yaml_path=yaml_path,
                    timeout_seconds=float(validate_timeout_seconds),
                )
                repaired = bool(validation.get("ok"))
        except Exception as exc:
            raw_error = f"yaml_repair_error: {exc}"

    validation_stderr = str(validation.get("stderr") or validation.get("stdout") or raw_error or "")
    if not validation.get("ok"):
        print(
            "[direct_generation] invalid Semgrep YAML/rule validation; outer attempt will not be counted. error={}".format(
                guardian.shorten(validation_stderr.replace("\n", " "), 700)
            ),
            flush=True,
        )

    report = {
        "round": 1,
        "round_counted": bool(validation.get("ok")),
        "validation": validation,
        "feedback": "validate_ok: {}\n{}".format(bool(validation.get("ok")), validation_stderr),
        "passed": bool(validation.get("ok")),
        "generated_rule_yaml": str(yaml_path),
        "repaired": repaired,
    }
    if raw_error:
        report["error"] = raw_error
    guardian.write_json(attempt_dir / "attempt_report.json", report)
    return report


def run_requirement_generation(config: RequirementRunConfig) -> dict[str, Any]:
    requirement_text = (config.requirement_text or "").strip()
    if not requirement_text:
        raise ValueError("requirement_text is required")

    output_dir = Path(config.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_bundle = read_samples_bundle(config.sample_files)
    docs_bundle_full, docs_bundle_manifest = build_reference_bundle()

    (output_dir / "docs_bundle.txt").write_text(docs_bundle_full, encoding="utf-8")
    guardian.write_json(output_dir / "docs_bundle_manifest.json", docs_bundle_manifest)
    (output_dir / "example_context_bundle.txt").write_text(sample_bundle, encoding="utf-8")

    task = build_custom_task(requirement_text=requirement_text, requirement_title=config.requirement_title)
    guardian.write_json(output_dir / "selected_rules.json", [asdict(task)])

    run_meta = {
        "mode": "direct_single_rule_generation",
        "pattern_ir_enabled": bool(config.pattern_ir_enabled),
        "requirement_title": task.title,
        "requirement_main_title": task.main_title,
        "sample_files": [str(Path(x).expanduser().resolve()) for x in config.sample_files],
    }
    guardian.write_json(output_dir / "run_mode_meta.json", run_meta)

    semgrep_bin = guardian.find_semgrep_bin(config.semgrep_bin)
    llm = create_llm_client(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model,
        request_timeout=float(config.request_timeout),
        request_retries=int(config.request_retries),
    )

    summary: dict[str, Any]
    start = time.time()
    try:
        rule_slug = guardian.slugify(task.main_title or task.title)
        rule_dir = output_dir / rule_slug
        rule_dir.mkdir(parents=True, exist_ok=True)
        pattern_ir_result = generate_pattern_ir(
            llm=llm,
            requirement_text=requirement_text,
            sample_bundle=sample_bundle,
            target_language=config.target_language,
            output_dir=rule_dir,
            enabled=bool(config.pattern_ir_enabled),
        )
        final_report = _direct_generate_once(
            llm=llm,
            semgrep_bin=semgrep_bin,
            requirement_text=requirement_text,
            sample_bundle=sample_bundle,
            docs_bundle=docs_bundle_full,
            pattern_ir_contract=pattern_ir_result.contract,
            rule_dir=rule_dir,
            validate_timeout_seconds=float(config.validate_timeout_seconds),
            target_language=config.target_language,
        )
        final_report["pattern_ir_parse_ok"] = pattern_ir_result.parse_ok
        final_report["pattern_ir_error"] = pattern_ir_result.error
        summary = {
            "rule": asdict(task),
            "rule_dir": str(rule_dir),
            "success": bool(final_report.get("passed", False)),
            "final_report": final_report,
            "pattern_ir": {
                "parse_ok": pattern_ir_result.parse_ok,
                "error": pattern_ir_result.error,
                "payload_path": str((rule_dir / "pattern_ir_payload.json").resolve()),
                "contract_path": str((rule_dir / "pattern_ir_contract.txt").resolve()),
            },
        }
        guardian.write_json(rule_dir / "rule_summary.json", summary)
    except Exception as exc:
        rule_slug = guardian.slugify(task.main_title or task.title)
        rule_dir = output_dir / rule_slug
        rule_dir.mkdir(parents=True, exist_ok=True)
        trace = traceback.format_exc()
        (rule_dir / "pipeline_exception.txt").write_text(trace, encoding="utf-8")
        summary = {
            "rule": asdict(task),
            "rule_dir": str(rule_dir),
            "success": False,
            "error": str(exc),
            "traceback": trace,
            "final_report": {},
        }
        guardian.write_json(rule_dir / "rule_summary.json", summary)

    success_count = 1 if summary.get("success") else 0
    failed_count = 1 - success_count
    report = {
        "mode": "direct_single_rule_generation",
        "output_dir": str(output_dir),
        "semgrep_bin": semgrep_bin,
        "base_url": config.base_url,
        "model": config.model,
        "pattern_ir_enabled": bool(config.pattern_ir_enabled),
        "pattern_ir": summary.get("pattern_ir", {}),
        "requirement_title": task.title,
        "requirement_main_title": task.main_title,
        "sample_files": [str(Path(x).expanduser().resolve()) for x in config.sample_files],
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": float(success_count),
        "elapsed_seconds": round(time.time() - start, 2),
        "summaries": [summary],
    }
    guardian.write_json(output_dir / "run_summary.json", report)
    return report
