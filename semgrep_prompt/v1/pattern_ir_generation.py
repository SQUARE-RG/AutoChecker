#!/usr/bin/env python3
"""Lightweight Pattern-IR generation for Semgrep rule synthesis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import semgrep_tool_common as guardian
from llm_client import LLMClient


PATTERN_IR_SCHEMA_VERSION = "semgrep-pattern-ir-v1"


@dataclass
class PatternIRResult:
    payload: dict[str, Any]
    prompt: str
    contract: str
    parse_ok: bool
    error: str = ""


def pattern_ir_template(requirement_text: str, target_language: str) -> dict[str, Any]:
    return {
        "schema_version": PATTERN_IR_SCHEMA_VERSION,
        "target_language": target_language,
        "problem": {
            "kind": "source_sink_flow | sensitive_sink_context | structural_misuse | api_misuse | lifetime_or_order_misuse | unresolved",
            "goal": guardian.shorten(requirement_text, 800),
            "recommended_mode": "search | taint",
            "rationale": "",
        },
        "families": {
            "sources": [],
            "propagators": [],
            "sinks": [],
            "sanitizers": [],
            "structural_triggers": [],
            "sensitive_contexts": [],
            "good_exclusions": [],
        },
        "semantic_branches": [
            {
                "branch_id": "primary",
                "bad_evidence": [],
                "required_context": [],
                "good_exclusions": [],
                "semgrep_strategy": "search | taint",
                "notes": "",
            }
        ],
        "semgrep_notes": {
            "taint_fields_may_be_empty_for_search_mode": True,
            "unsupported_or_partial_cases": [],
        },
    }


def build_pattern_ir_prompt(
    requirement_text: str,
    sample_bundle: str,
    target_language: str,
) -> str:
    template = pattern_ir_template(requirement_text=requirement_text, target_language=target_language)
    return f"""You are producing a lightweight Pattern-IR semantic plan for one Semgrep rule.

Return STRICT JSON only. Do not return Semgrep YAML.

Purpose:
- Produce a semantic contract for the next LLM step.
- Use BAD/GOOD examples as contrastive evidence, not as cases to enumerate.
- Do not copy paths, file names, test ids, line numbers, or benchmark-only helper names.
- Concrete standard/library/framework/security API names, operators, type names, fields, source APIs, and sink APIs are allowed when they carry the requirement semantics.

Mode policy:
- Choose `source_sink_flow` and recommended_mode `taint` only when a real source reaches a concrete sink across statements.
- Choose `search` for local structural/API/lifetime/order/sensitive-context checks.
- If recommended_mode is `search`, taint-only fields may be empty: sources, propagators, sinks, sanitizers.
- Search-mode semantics must still be represented in structural_triggers, sensitive_contexts, good_exclusions, and semantic_branches.
- Do not invent fake taint sources just because source/sink fields are empty.

Branch policy:
- Each semantic branch must describe one generalized vulnerability shape.
- If BAD and GOOD share an API/operator, the branch must include distinguishing BAD context or GOOD exclusions.
- Good exclusions are semantic constraints first; only write Semgrep-like snippets when metavariables would already be bound by the branch.
- Mark Semgrep-hard distinctions as partial when they need cross-function flow, deep alias/type reasoning, or proving a later statement is absent.

Fill this JSON shape:
{guardian.shorten(json.dumps(template, ensure_ascii=False, indent=2), 3600)}

Prepared requirement and feedback:
{guardian.shorten(requirement_text, 7000)}

Paired sample context:
{guardian.shorten(sample_bundle, 5000)}
"""


def unresolved_pattern_ir(requirement_text: str, target_language: str, error: str = "") -> dict[str, Any]:
    payload = pattern_ir_template(requirement_text=requirement_text, target_language=target_language)
    payload["problem"]["kind"] = "unresolved"
    payload["problem"]["recommended_mode"] = "search"
    payload["problem"]["rationale"] = "Pattern-IR generation failed; use requirement text and paired examples directly."
    payload["semantic_branches"] = []
    if error:
        payload["error"] = error
    return payload


def merge_pattern_ir(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = merge_pattern_ir(merged[key], value)
        else:
            merged[key] = value
    return merged


def _string_items(raw: Any, limit: int = 8) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            text = str(item.get("pattern") or item.get("summary") or item.get("intent") or item.get("name") or "").strip()
        else:
            text = str(item or "").strip()
        if text:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def _family_lines(families: dict[str, Any], recommended_mode: str) -> list[str]:
    lines: list[str] = []
    labels = [
        ("sources", "source families"),
        ("propagators", "propagators"),
        ("sinks", "sink/operation families"),
        ("sanitizers", "sanitizers"),
        ("structural_triggers", "structural triggers"),
        ("sensitive_contexts", "sensitive contexts"),
        ("good_exclusions", "good exclusions"),
    ]
    for key, label in labels:
        items = _string_items(families.get(key), limit=10)
        if items:
            lines.append(f"- {label}: " + "; ".join(items))

    if recommended_mode == "search":
        lines.append("- search-mode note: taint fields may be empty; do not invent fake sources/sinks.")
    return lines


def compact_pattern_ir_contract(payload: dict[str, Any]) -> str:
    problem = payload.get("problem") if isinstance(payload.get("problem"), dict) else {}
    families = payload.get("families") if isinstance(payload.get("families"), dict) else {}
    branches = payload.get("semantic_branches") if isinstance(payload.get("semantic_branches"), list) else []

    kind = str(problem.get("kind") or "unresolved").strip()
    recommended_mode = str(problem.get("recommended_mode") or "search").strip().lower()
    if recommended_mode not in {"search", "taint"}:
        recommended_mode = "search"

    lines = [
        "Pattern-IR compact contract:",
        f"- problem_kind={kind}; recommended_mode={recommended_mode}; rationale={guardian.shorten(str(problem.get('rationale') or ''), 360)}",
        "- Treat this as semantic planning, not as sample enumeration or mandatory YAML.",
        "- If this contract conflicts with paired BAD/GOOD evidence or Semgrep feasibility, prefer the evidence and explain the local choice in notes.",
    ]
    lines.extend(_family_lines(families, recommended_mode))

    branch_lines: list[str] = []
    for branch in branches[:6]:
        if not isinstance(branch, dict):
            continue
        branch_id = str(branch.get("branch_id") or "branch").strip()
        strategy = str(branch.get("semgrep_strategy") or recommended_mode).strip()
        bad = "; ".join(_string_items(branch.get("bad_evidence"), limit=4))
        context = "; ".join(_string_items(branch.get("required_context"), limit=4))
        exclusions = "; ".join(_string_items(branch.get("good_exclusions"), limit=3))
        notes = guardian.shorten(str(branch.get("notes") or ""), 220)
        branch_lines.append(
            f"{branch_id}: strategy={strategy}; bad={bad or '(describe BAD core)'}; context={context or '(none)'}; good_exclusions={exclusions or '(none)'}; notes={notes}"
        )
    if branch_lines:
        lines.append("- semantic branches: " + " || ".join(branch_lines))
    elif kind == "unresolved":
        lines.append("- semantic branches: unresolved; infer from requirement and paired BAD/GOOD evidence.")

    return "\n".join(lines).strip()


def generate_pattern_ir(
    llm: LLMClient,
    requirement_text: str,
    sample_bundle: str,
    target_language: str,
    output_dir: Path,
    enabled: bool = True,
) -> PatternIRResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    if not enabled:
        payload = unresolved_pattern_ir(requirement_text, target_language, error="pattern_ir_disabled")
        contract = compact_pattern_ir_contract(payload)
        guardian.write_json(output_dir / "pattern_ir_payload.json", payload)
        (output_dir / "pattern_ir_contract.txt").write_text(contract, encoding="utf-8")
        return PatternIRResult(payload=payload, prompt="", contract=contract, parse_ok=False, error="pattern_ir_disabled")

    prompt = build_pattern_ir_prompt(
        requirement_text=requirement_text,
        sample_bundle=sample_bundle,
        target_language=target_language,
    )
    (output_dir / "pattern_ir_prompt.txt").write_text(prompt, encoding="utf-8")

    error = ""
    try:
        payload = merge_pattern_ir(
            pattern_ir_template(requirement_text=requirement_text, target_language=target_language),
            llm.ask_json(prompt, retries=1),
        )
        parse_ok = True
    except Exception as exc:
        error = f"pattern_ir_generation_error: {exc}"
        payload = unresolved_pattern_ir(requirement_text, target_language, error=error)
        parse_ok = False

    if not isinstance(payload, dict):
        error = "pattern_ir_generation_error: response was not a JSON object"
        payload = unresolved_pattern_ir(requirement_text, target_language, error=error)
        parse_ok = False

    payload.setdefault("schema_version", PATTERN_IR_SCHEMA_VERSION)
    contract = compact_pattern_ir_contract(payload)
    guardian.write_json(output_dir / "pattern_ir_payload.json", payload)
    (output_dir / "pattern_ir_contract.txt").write_text(contract, encoding="utf-8")

    return PatternIRResult(payload=payload, prompt=prompt, contract=contract, parse_ok=parse_ok, error=error)
