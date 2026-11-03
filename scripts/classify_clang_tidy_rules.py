#!/usr/bin/env python3
"""Partition structurally valid rules by the analysis capability they require."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "experiment/gjb8114-all"

PREPROCESSOR_RULES = {
    "no-macro-alias-to-keyword-basic-type",
    "no-keyword-redefinition",
    "no-duplicate-macro-definition",
    "paired-define-undef-in-function",
    "parenthesize-function-like-macro-params-result",
    "no-absolute-path-in-include",
    "caution-macro-brace-mismatch",
    "cautious-macro-token-paste-stringize",
    "no-executable-code-before-header-include",
    "prohibit-nested-comments",
    "c-standard-comments-cautious-slash",
    "empty-branch-semicolon-and-comment",
    "switch-case-default-termination-and-shared-comment",
    "annotate-octal-literals",
    "avoid-header-files-with-h-suffix",
}

DATAFLOW_RULES = {
    "prohibit-use-or-free-unallocated-or-freed-pointer",
    "set-freed-pointer-null",
    "check-dynamic-pointer-null-before-first-use",
    "close-file-pointers-on-exit",
    "prohibit-shift-beyond-variable-width",
    "prohibit-negative-shift-count",
    "prohibit-array-out-of-bounds",
    "array-index-nonnegative-integer",
    "no-division-by-zero",
    "no-buffer-read-overflow",
    "no-buffer-write-overflow",
    "no-use-after-free",
    "free-original-malloc-pointer",
    "string-function-no-overflow",
    "release-dynamic-memory-promptly",
    "no-multiple-order-dependent-calls-in-expression",
    "no-direct-indirect-recursion",
    "check-system-function-return-status",
    "no-unreachable-statements",
    "no-unreachable-branches",
    "no-uninitialized-variable-use",
    "centralized-global-variable-initialization",
    "volatile-for-externally-writable-variables",
    "nul-terminated-string-array",
    "destructor-exception-caught-by-itself",
    "delete-new-allocated-memory",
    "use-delete-array-for-new-array",
    "delete-pointer-original-new-address",
}

REVIEW_RULES = {
    "value-returning-function-must-return",
    "static-function-must-be-used",
    "no-unused-call-parameters",
    "no-nonresource-data-return-for-external-modification",
    "const-pointer-reference-parameters-if-not-modified",
    "matched-throw-catch",
    "initialize-all-member-variables-in-constructors",
}

OUTPUT_FILENAMES = {
    "ast": "clang_tidy_ast_supported_rules.json",
    "preprocessor": "clang_tidy_preprocessor_rules.json",
    "dataflow": "dataflow_rules.json",
    "review": "clang_tidy_review_rules.json",
}


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def classify_title(main_title: str) -> str:
    if main_title in PREPROCESSOR_RULES:
        return "preprocessor"
    if main_title in DATAFLOW_RULES:
        return "dataflow"
    if main_title in REVIEW_RULES:
        return "review"
    return "ast"


def classify_rules(input_path: Path, output_dir: Path) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Rules file does not exist: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {input_path}: {exc}") from exc

    categories = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(categories, dict):
        raise ValueError("Rules JSON must contain an object field 'data'")

    partitions: dict[str, dict[str, Any]] = {
        name: {"data": {category: [] for category in categories}}
        for name in OUTPUT_FILENAMES
    }
    seen_titles: set[str] = set()
    total = 0
    for category, rules in categories.items():
        if not isinstance(rules, list):
            raise ValueError(f"Category {category!r} must contain a rule array")
        for rule in rules:
            if not isinstance(rule, dict):
                raise ValueError(f"Category {category!r} contains a non-object rule")
            main_title = str(rule.get("main_title") or "").strip()
            if not main_title:
                raise ValueError(f"Category {category!r} contains a rule without main_title")
            if main_title in seen_titles:
                raise ValueError(f"Duplicate main_title: {main_title}")
            seen_titles.add(main_title)
            capability = classify_title(main_title)
            partitions[capability]["data"][category].append(rule)
            total += 1

    configured = PREPROCESSOR_RULES | DATAFLOW_RULES | REVIEW_RULES
    missing_configured_rules = sorted(configured - seen_titles)
    if missing_configured_rules:
        raise ValueError(
            "Capability configuration contains rules absent from the input: "
            + ", ".join(missing_configured_rules)
        )

    output_paths: dict[str, str] = {}
    counts: dict[str, int] = {}
    for capability, filename in OUTPUT_FILENAMES.items():
        path = output_dir / filename
        _write_json_atomic(path, partitions[capability])
        output_paths[capability] = str(path)
        counts[capability] = sum(
            len(rules) for rules in partitions[capability]["data"].values()
        )

    if sum(counts.values()) != total:
        raise RuntimeError("Capability partitions do not cover the complete input")
    return {
        "input_rules": str(input_path),
        "total_rule_count": total,
        "counts": counts,
        "outputs": output_paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Split Clang-Tidy candidate rules into AST, preprocessor, data-flow, "
            "and manual-review groups."
        )
    )
    parser.add_argument("--rules", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    summary = classify_rules(args.rules, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
