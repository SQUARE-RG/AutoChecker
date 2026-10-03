#!/usr/bin/env python3
"""Stage 3: generate and validate positive/negative rule test cases."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from input_processing.test_generator import generate_rule_tests  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate validated positive/negative tests from Stage-2 rules."
    )
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-rules", type=Path, required=True)
    parser.add_argument(
        "--language", required=True, choices=["c", "cpp", "python", "java"]
    )
    parser.add_argument("--negative-count", type=int, default=10)
    parser.add_argument("--positive-count", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument(
        "--workers", type=int, default=1, help="Rules processed concurrently"
    )
    parser.add_argument(
        "--llm-concurrency", type=int, default=1, help="Maximum simultaneous LLM calls"
    )
    parser.add_argument("--max-repair-attempts", type=int, default=3)
    parser.add_argument("--compiler", help="Override compiler/validator executable")
    parser.add_argument("--c-standard", default="c11")
    parser.add_argument("--cpp-standard", default="c++17")
    parser.add_argument("--validation-timeout", type=int, default=30)
    parser.add_argument("--llm-timeout", type=int, default=300)
    parser.add_argument("--llm-max-retries", type=int, default=5)
    parser.add_argument("--retry-base-delay", type=float, default=2.0)
    parser.add_argument("--retry-max-delay", type=float, default=60.0)
    parser.add_argument("--log-file", type=Path)
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    parser.add_argument("--model", help="Override MODEL_NAME/LLM_MODEL")
    parser.add_argument("--base-url", help="Override LLM_BASE_URL")
    parser.add_argument("--api-key", help="Prefer environment variables over this option")
    parser.add_argument(
        "--force", action="store_true", help="Ignore rule generation checkpoints"
    )
    args = parser.parse_args()

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if args.log_file:
        args.log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s",
        handlers=handlers,
    )

    summary = generate_rule_tests(
        args.rules,
        args.output_dir,
        args.output_rules,
        language=args.language,
        negative_count=args.negative_count,
        positive_count=args.positive_count,
        batch_size=args.batch_size,
        workers=args.workers,
        llm_concurrency=args.llm_concurrency,
        max_repair_attempts=args.max_repair_attempts,
        compiler=args.compiler,
        c_standard=args.c_standard,
        cpp_standard=args.cpp_standard,
        validation_timeout=args.validation_timeout,
        llm_timeout=args.llm_timeout,
        llm_max_retries=args.llm_max_retries,
        retry_base_delay=args.retry_base_delay,
        retry_max_delay=args.retry_max_delay,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        force=args.force,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["failed_rule_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
