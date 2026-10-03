from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .schemas import DocumentBlock


@dataclass
class DocumentChunk:
    chunk_id: str
    pages: list[int]
    block_ids: list[str]
    text: str
    token_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "pages": self.pages,
            "block_ids": self.block_ids,
            "text": self.text,
            "token_count": self.token_count,
        }


def build_chunks(
    blocks: list[DocumentBlock],
    *,
    max_tokens: int = 12000,
    overlap_pages: int = 1,
) -> list[DocumentChunk]:
    if max_tokens < 500:
        raise ValueError("max_tokens must be at least 500")
    if overlap_pages < 0:
        raise ValueError("overlap_pages cannot be negative")
    if not blocks:
        return []

    by_page: dict[int, list[DocumentBlock]] = defaultdict(list)
    for block in blocks:
        by_page[block.page].append(block)
    page_units = []
    for page_number in sorted(by_page):
        page_blocks = sorted(by_page[page_number], key=lambda item: item.order or 0)
        text = _render_blocks(page_blocks)
        page_units.append((page_number, page_blocks, text, count_tokens(text)))

    chunks: list[DocumentChunk] = []
    start = 0
    while start < len(page_units):
        end = start
        total_tokens = 0
        selected: list[tuple[int, list[DocumentBlock], str, int]] = []
        while end < len(page_units):
            unit = page_units[end]
            if selected and total_tokens + unit[3] > max_tokens:
                break
            selected.append(unit)
            total_tokens += unit[3]
            end += 1
            if total_tokens >= max_tokens:
                break

        # A single large page stays intact so that table and rule blocks are not cut.
        page_numbers = [unit[0] for unit in selected]
        selected_blocks = [block for unit in selected for block in unit[1]]
        chunk_text = "\n\n".join(unit[2] for unit in selected)
        chunks.append(
            DocumentChunk(
                chunk_id=f"chunk-{len(chunks) + 1:04d}",
                pages=page_numbers,
                block_ids=[block.block_id for block in selected_blocks],
                text=chunk_text,
                token_count=count_tokens(chunk_text),
            )
        )

        if end >= len(page_units):
            break
        next_start = end - overlap_pages
        start = max(start + 1, next_start)
    return chunks


def count_tokens(text: str) -> int:
    try:
        import tiktoken

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except (ImportError, ValueError):
        # Conservative fallback for mixed Chinese/English text.
        return max(1, len(text) // 2)


def _render_blocks(blocks: list[DocumentBlock]) -> str:
    rendered = []
    for block in blocks:
        rendered.append(
            f"[page={block.page} block_id={block.block_id} type={block.type}]\n{block.text}"
        )
    return "\n\n".join(rendered)
