from __future__ import annotations

import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .converter import prepare_input
from .io_utils import read_json, sha256_file, write_json, write_text
from .paddle_parser import call_paddleocr, normalize_paddleocr_response
from .text_parser import parse_text_document


def parse_document(
    input_path: Path,
    output_dir: Path,
    *,
    service_url: str = "http://127.0.0.1:18080/layout-parsing",
    response_json: Path | None = None,
    timeout_seconds: int = 7200,
    use_table_recognition: bool = True,
    use_region_detection: bool = True,
    pdf_batch_pages: int = 10,
) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    source_dir = output_dir / "source"
    converted_dir = output_dir / "converted"
    paddle_dir = output_dir / "paddleocr"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_copy = source_dir / input_path.name
    if source_copy != input_path:
        shutil.copy2(input_path, source_copy)

    prepared_path, parser_type = prepare_input(input_path, converted_dir)
    if parser_type == "paddleocr":
        if response_json:
            response = read_json(response_json)
            blocks, markdown, page_count = normalize_paddleocr_response(response)
            write_json(paddle_dir / "raw_response.json", response)
            backend = "paddleocr-import"
        elif prepared_path.suffix.lower() == ".pdf":
            blocks, markdown, page_count = _parse_pdf_in_batches(
                prepared_path,
                paddle_dir,
                source_sha256=sha256_file(input_path),
                service_url=service_url,
                timeout_seconds=timeout_seconds,
                use_table_recognition=use_table_recognition,
                use_region_detection=use_region_detection,
                batch_pages=pdf_batch_pages,
            )
            backend = "paddleocr-http-batched"
        else:
            response = call_paddleocr(
                prepared_path,
                service_url=service_url,
                timeout_seconds=timeout_seconds,
                use_table_recognition=use_table_recognition,
                use_region_detection=use_region_detection,
            )
            blocks, markdown, page_count = normalize_paddleocr_response(response)
            write_json(paddle_dir / "raw_response.json", response)
            backend = "paddleocr-http"
    else:
        if response_json is not None:
            raise ValueError("--response-json can only be used with PDF, Word, or image input")
        blocks, markdown, page_count = parse_text_document(prepared_path)
        backend = "native-text"

    write_text(output_dir / "document.md", markdown)
    write_json(output_dir / "blocks.json", {"blocks": [block.to_dict() for block in blocks]})
    manifest = {
        "schema_version": 1,
        "document_id": output_dir.name,
        "source_file": input_path.name,
        "source_path": str(input_path),
        "source_sha256": sha256_file(input_path),
        "source_type": input_path.suffix.lower().lstrip("."),
        "prepared_path": str(prepared_path),
        "parser_backend": backend,
        "page_count": page_count,
        "block_count": len(blocks),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "markdown": "document.md",
            "blocks": "blocks.json",
            "raw_response": "paddleocr/raw_response.json" if parser_type == "paddleocr" else None,
        },
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _parse_pdf_in_batches(
    pdf_path: Path,
    paddle_dir: Path,
    *,
    source_sha256: str,
    service_url: str,
    timeout_seconds: int,
    use_table_recognition: bool,
    use_region_detection: bool,
    batch_pages: int,
):
    if batch_pages < 1 or batch_pages > 30:
        raise ValueError("pdf_batch_pages must be between 1 and 30")
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "Batched PDF parsing requires pypdf; install it in the code_check environment"
        ) from exc

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    batches_dir = paddle_dir / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)
    progress_path = batches_dir / "progress.json"
    request_options = {
        "batch_pages": batch_pages,
        "use_table_recognition": use_table_recognition,
        "use_region_detection": use_region_detection,
    }
    if progress_path.exists():
        progress = read_json(progress_path)
        if progress.get("source_sha256") != source_sha256:
            raise RuntimeError(
                f"Existing OCR checkpoints in {batches_dir} belong to another document; "
                "use a different output directory"
            )
        if progress.get("request_options") != request_options:
            raise RuntimeError(
                f"Existing OCR checkpoints in {batches_dir} use different parsing options; "
                "use a different output directory"
            )
    else:
        write_json(
            progress_path,
            {
                "source_sha256": source_sha256,
                "page_count": page_count,
                "request_options": request_options,
            },
        )

    all_blocks = []
    markdown_parts = []
    batch_records = []
    for start in range(0, page_count, batch_pages):
        end = min(start + batch_pages, page_count)
        checkpoint = batches_dir / f"pages-{start + 1:04d}-{end:04d}.json"
        if checkpoint.exists():
            record = read_json(checkpoint)
            response = record["response"]
            print(f"reusing OCR batch pages {start + 1}-{end}")
        else:
            print(f"parsing PDF pages {start + 1}-{end}/{page_count}")
            writer = PdfWriter()
            for page_index in range(start, end):
                writer.add_page(reader.pages[page_index])
            with tempfile.NamedTemporaryFile(suffix=".pdf") as temporary_pdf:
                writer.write(temporary_pdf)
                temporary_pdf.flush()
                response = call_paddleocr(
                    Path(temporary_pdf.name),
                    service_url=service_url,
                    timeout_seconds=timeout_seconds,
                    use_table_recognition=use_table_recognition,
                    use_region_detection=use_region_detection,
                )
            record = {
                "start_page": start + 1,
                "end_page": end,
                "response": response,
            }
            write_json(checkpoint, record)
        blocks, markdown, parsed_count = normalize_paddleocr_response(
            response, page_offset=start
        )
        if parsed_count != end - start:
            raise RuntimeError(
                f"PaddleOCR returned {parsed_count} pages for requested pages "
                f"{start + 1}-{end}; refusing to produce an incomplete document"
            )
        all_blocks.extend(blocks)
        markdown_parts.append(markdown.rstrip())
        batch_records.append(
            {
                "start_page": start + 1,
                "end_page": end,
                "checkpoint": str(checkpoint.relative_to(paddle_dir)),
            }
        )
    write_json(
        paddle_dir / "raw_response.json",
        {"source_sha256": source_sha256, "page_count": page_count, "batches": batch_records},
    )
    return all_blocks, "\n\n---\n\n".join(markdown_parts).rstrip() + "\n", page_count
