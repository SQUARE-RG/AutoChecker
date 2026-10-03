from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from .chunker import DocumentChunk
from .io_utils import read_json, write_json
from .prompts import (
    RULE_EXTRACTION_SYSTEM_PROMPT,
    build_extraction_prompt,
)
from .schemas import ChunkExtractionResult, RuleCandidate, RuleExample


InvokeFunction = Callable[[str, str], str]


def extract_chunk_rules(
    chunk: DocumentChunk,
    checkpoint_dir: Path,
    invoke: InvokeFunction,
    *,
    retries: int = 3,
    force: bool = False,
) -> ChunkExtractionResult:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    completed_path = checkpoint_dir / f"{chunk.chunk_id}.completed.json"
    if completed_path.exists() and not force:
        saved = read_json(completed_path)
        if saved.get("schema_version") == 3:
            return ChunkExtractionResult.from_dict(saved)

    prompt = build_extraction_prompt(chunk.text)
    payload, raw_response = _invoke_json(invoke, prompt, retries)
    result = normalize_chunk_result(payload, chunk)
    completed = result.to_dict()
    completed["schema_version"] = 3
    completed["raw_response"] = raw_response
    write_json(
        completed_path,
        completed,
    )
    return result


def normalize_chunk_result(
    payload: dict[str, Any], chunk: DocumentChunk
) -> ChunkExtractionResult:
    return ChunkExtractionResult(
        chunk_id=chunk.chunk_id,
        rules=normalize_rules(payload, chunk),
    )


def normalize_rules(payload: dict[str, Any], chunk: DocumentChunk) -> list[RuleCandidate]:
    values = payload.get("rules", [])
    if not isinstance(values, list):
        raise ValueError("LLM response field 'rules' must be an array")
    normalized: list[RuleCandidate] = []
    for value in values:
        if not isinstance(value, dict):
            continue
        description = _clean_string(value.get("description"))
        if not description:
            continue
        rule_id = _clean_string(value.get("rule_id") or value.get("source_rule_id")) or None
        rule_type = _normalize_rule_type(value.get("rule_type"))
        main_title = _slugify(_clean_string(value.get("main_title")))
        if not main_title:
            seed = rule_id or description
            main_title = "rule-" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
        normalized.append(
            RuleCandidate(
                rule_id=rule_id,
                main_title=main_title,
                description=description,
                rule_type=rule_type,
                examples=_normalize_examples(value.get("examples")),
                source_chunks=[chunk.chunk_id],
            )
        )
    return normalized


def parse_json_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
    stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("LLM response must be a JSON object")
    return value


def _invoke_json(
    invoke: InvokeFunction, prompt: str, retries: int
) -> tuple[dict[str, Any], str]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        raw = invoke(prompt, RULE_EXTRACTION_SYSTEM_PROMPT)
        try:
            return parse_json_response(raw), raw
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(attempt * 2, 5))
    raise RuntimeError(f"LLM did not return valid rule JSON after {retries} attempts") from last_error


def _clean_string(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slugify(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def _normalize_rule_type(value: Any) -> str:
    normalized = _clean_string(value).lower()
    if normalized in {"advisory", "recommended", "recommendation", "建议", "建议性"}:
        return "advisory"
    return "required"


def _normalize_examples(value: Any) -> list[RuleExample]:
    if not isinstance(value, list):
        return []
    examples: list[RuleExample] = []
    seen: set[tuple[str, str]] = set()
    allowed_types = {"violation", "compliant", "illustrative"}
    for item in value:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "").strip()
        if not code:
            continue
        example_type = _clean_string(item.get("type")).lower()
        if example_type not in allowed_types:
            example_type = "illustrative"
        key = (example_type, re.sub(r"\s+", "", code))
        if key in seen:
            continue
        seen.add(key)
        examples.append(RuleExample(type=example_type, code=code))
    return examples
