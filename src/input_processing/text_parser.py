from __future__ import annotations

import re
from pathlib import Path

from .schemas import DocumentBlock


def parse_text_document(path: Path) -> tuple[list[DocumentBlock], str, int]:
    suffix = path.suffix.lower()
    text = _read_text(path)
    if suffix in {".html", ".htm"}:
        text = _html_to_markdown(text)
    blocks = _markdown_blocks(text)
    return blocks, text.rstrip() + "\n", 1


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _html_to_markdown(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("HTML parsing requires beautifulsoup4") from exc
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for level in range(1, 7):
        for heading in soup.find_all(f"h{level}"):
            heading.insert_before("#" * level + " ")
    return soup.get_text("\n")


def _markdown_blocks(text: str) -> list[DocumentBlock]:
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    blocks: list[DocumentBlock] = []
    for index, part in enumerate(parts, start=1):
        first_line = part.splitlines()[0]
        if re.match(r"^#{1,6}\s+", first_line):
            block_type = "paragraph_title"
        elif first_line.lstrip().startswith(("|", "<table")):
            block_type = "table"
        elif re.match(r"^\s*(?:[-*+] |\d+[.)]\s+)", first_line):
            block_type = "list"
        else:
            block_type = "text"
        blocks.append(
            DocumentBlock(
                block_id=f"page-1-block-{index}",
                page=1,
                type=block_type,
                text=part,
                order=index,
                confidence=1.0,
            )
        )
    return blocks
