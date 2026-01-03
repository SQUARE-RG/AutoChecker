import json
from pathlib import Path
from typing import Any


def extract_json_from_text(raw: str) -> Any:
    """Parse the first JSON object embedded in a model response."""
    if raw is None:
        raise ValueError("Empty response from language model")
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("Blank response from language model")
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        parts = cleaned.split("\n", 1)
        if len(parts) == 2:
            cleaned = parts[1]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        snippet = cleaned[start : end + 1]
        return json.loads(snippet)


def dump_pretty_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
