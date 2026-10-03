#!/usr/bin/env python3
"""Stage 1: parse a regulation document and persist normalized artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from input_processing.document_parser import parse_document  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse PDF/Word/image/text into Markdown and normalized block JSON."
    )
    parser.add_argument("--input", type=Path, required=True, help="Input document path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Artifact directory (default: result_input_processing/<file-stem>)",
    )
    parser.add_argument(
        "--service-url",
        default="http://127.0.0.1:18080/layout-parsing",
        help="PaddleOCR PP-StructureV3 endpoint",
    )
    parser.add_argument(
        "--response-json",
        type=Path,
        help="Import an existing PaddleOCR response instead of invoking the service",
    )
    parser.add_argument("--timeout", type=int, default=7200, help="OCR timeout in seconds")
    parser.add_argument(
        "--pdf-batch-pages",
        type=int,
        default=10,
        help="PDF pages per resumable OCR request (1-30, default: 10)",
    )
    parser.add_argument(
        "--no-table-recognition", action="store_true", help="Disable table recognition"
    )
    parser.add_argument(
        "--no-region-detection", action="store_true", help="Disable region detection"
    )
    args = parser.parse_args()

    output_dir = args.output_dir or (
        PROJECT_ROOT / "result_input_processing" / _safe_name(args.input.stem)
    )
    manifest = parse_document(
        args.input,
        output_dir,
        service_url=args.service_url,
        response_json=args.response_json,
        timeout_seconds=args.timeout,
        use_table_recognition=not args.no_table_recognition,
        use_region_detection=not args.no_region_detection,
        pdf_batch_pages=args.pdf_batch_pages,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"parsed artifacts: {output_dir.resolve()}")


def _safe_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return normalized or "document"


if __name__ == "__main__":
    main()
