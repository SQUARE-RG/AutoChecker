#!/usr/bin/env python3
"""Stage 2: extract and reconcile rules from persisted parsing artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from input_processing.rule_pipeline import extract_rules  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract regulation rules from Stage-1 Markdown/block JSON artifacts."
    )
    parser.add_argument("--parsed-dir", type=Path, required=True)
    parser.add_argument("--category", required=True, help="AutoChecker category key")
    parser.add_argument("--model", help="Override MODEL_NAME/LLM_MODEL")
    parser.add_argument("--base-url", help="Override LLM_BASE_URL")
    parser.add_argument("--api-key", help="Prefer environment variables over this option")
    parser.add_argument("--max-chunk-tokens", type=int, default=12000)
    parser.add_argument("--overlap-pages", type=int, default=1)
    parser.add_argument(
        "--force", action="store_true", help="Ignore completed chunk checkpoints"
    )
    args = parser.parse_args()

    summary = extract_rules(
        args.parsed_dir,
        category=args.category,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        max_chunk_tokens=args.max_chunk_tokens,
        overlap_pages=args.overlap_pages,
        force=args.force,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
