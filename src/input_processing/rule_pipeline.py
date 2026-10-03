from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .chunker import build_chunks
from .exporter import build_autochecker_rules
from .io_utils import read_json, write_json, write_text
from .llm_client import create_llm_client, invoke_text
from .rule_extractor import extract_chunk_rules
from .rule_merger import merge_rules
from .schemas import DocumentBlock


def extract_rules(
    parsed_dir: Path,
    *,
    category: str,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    max_chunk_tokens: int = 12000,
    overlap_pages: int = 1,
    force: bool = False,
    invoke: Callable[[str, str], str] | None = None,
) -> dict[str, Any]:
    parsed_dir = parsed_dir.resolve()
    block_payload = read_json(parsed_dir / "blocks.json")
    blocks = [DocumentBlock.from_dict(item) for item in block_payload.get("blocks", [])]
    if not blocks:
        raise RuntimeError(f"No document blocks found in {parsed_dir / 'blocks.json'}")

    chunks = build_chunks(
        blocks, max_tokens=max_chunk_tokens, overlap_pages=overlap_pages
    )
    chunks_dir = parsed_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    write_json(chunks_dir / "chunks.json", {"chunks": [chunk.to_dict() for chunk in chunks]})
    for chunk in chunks:
        write_text(chunks_dir / f"{chunk.chunk_id}.md", chunk.text.rstrip() + "\n")

    if invoke is None:
        client = create_llm_client(model=model, api_key=api_key, base_url=base_url)
        invoke = lambda prompt, system: invoke_text(client, prompt, system)

    all_candidates = []
    non_empty_chunks = 0
    checkpoint_dir = parsed_dir / "extractions"
    for index, chunk in enumerate(chunks, start=1):
        print(
            f"[{index}/{len(chunks)}] extracting {chunk.chunk_id}, "
            f"pages={chunk.pages[0]}-{chunk.pages[-1]}, tokens={chunk.token_count}"
        )
        result = extract_chunk_rules(
            chunk,
            checkpoint_dir,
            invoke,
            force=force,
        )
        if not result.rules:
            continue
        non_empty_chunks += 1
        all_candidates.extend(result.rules)

    write_json(
        parsed_dir / "candidates.json",
        {"rules": [candidate.to_dict() for candidate in all_candidates]},
    )
    rules = merge_rules(all_candidates)
    output_path = parsed_dir / "autochecker_rules.json"
    write_json(output_path, build_autochecker_rules(rules, category=category))
    return {
        "chunk_count": len(chunks),
        "non_empty_chunk_count": non_empty_chunks,
        "candidate_count": len(all_candidates),
        "rule_count": len(rules),
        "output": str(output_path),
    }
