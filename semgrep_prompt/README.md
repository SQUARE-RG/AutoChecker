# Semgrep Prompt Workspace

This directory contains the Semgrep rule-generation workflow used by the demo
runner. The current workflow is requirement-driven, sample-pair driven, and
generic-first: it should not contain hardcoded recipes for a specific CWE, GJB
rule, benchmark file, or sample id.

## Current Entry Points

- `demo/run_semgrep_juliet_interface_test.py`
  - Main iterative runner for paired BAD/GOOD sample folders and Juliet-style
    CWE directories.
  - Generates exactly one Semgrep rule per counted attempt.
  - Invalid YAML or Semgrep validation failures are retried without consuming a
    counted attempt.
- `demo/run_semgrep_guardian.py`
  - Lower-level Guardian generation loop used by the interface runner.
  - Handles planning, YAML generation, validation, repair, test execution, and
    feedback.
- `demo/guardian_llm_generation.py`
  - Requirement interface adapter between the Juliet runner and Guardian.
- `demo/juliet_sample_suite.py`
  - Loader for curated sample folders in the required paired layout.
- `demo/sample_contrast_analyzer.py`
  - Generic BAD/GOOD contrast analysis used to feed dynamic evidence back into
    Pattern-IR and rule generation.
- `demo/juliet_rule_quality.py`
  - Generic rule normalization and semantic quality gates for Semgrep YAML.

## Sample Folder Layout

Curated sample folders use one requirement per folder:

```text
<requirement-folder>/
  bad/
    test1.cpp
    test2.cpp
  good/
    test1.cpp
    test2.cpp
```

`bad/testN.*` is paired with `good/testN.*`. If the matching GOOD file is
missing, that BAD case is still evaluated but it cannot contribute paired
contrast for that index.

## Main Command Shape

Run from `code_check` root with Python 3.10:

```bash
/home/meiosis/py310/bin/python semgrep_prompt/demo/run_semgrep_juliet_interface_test.py \
  --sample-folder semgrep_prompt/demo/curated_samples/<dataset>/<requirement> \
  --requirement "Describe the rule intent here" \
  --max-attempts 5 \
  --max-rounds 4 \
  --pattern-ir \
  --simplify \
  --iterative-no-threshold \
  --run-tag smoke_current
```

For native Juliet directories, use `--testcases-root` plus `--cwes`.

## Prompt And Knowledge Files

- `demo/juliet_global_guidance.md`
  - Short global iterative policy injected into the Juliet interface prompt.
- `docs/semgrep_compact_guide.md`
  - Compact Semgrep syntax and modeling guide.
- `docs/semgrep_taint_syntax_knowledge.md`
  - Taint-mode syntax details and common schema failures.
- `docs/checker_class_catalog.md`
  - Abstract checker-class taxonomy, not a template collection.
- `docs/semgrep_source_reference_cases.md`
  - Shape-only references; concrete APIs and literals must come from the
    current requirement or current paired examples.
- `demo/prompt_json/`
  - Legacy prompt templates used by the older autochecker path. Keep them
    generic; do not add per-CWE or per-rule recipes.

## Non-Specialization Policy

- Do not add CWE-specific prompt templates, required sink-token lists, or
  deterministic patch rules.
- Do not add benchmark-specific branches, filenames, test ids, or sample-count
  recipes.
- Concrete APIs/operators are allowed only when they come from the current
  requirement text or repeated evidence in the current BAD/GOOD pairs.
- Unsupported deep interprocedural variants should be classified as unsupported
  or partial rather than covered with broad wildcard rules.

## Output Roots

- Temporary and final run outputs are managed under `demo/demo_output/`.
- Curated samples are stored under `demo/curated_samples/`.
- Shared generated test cases for Guardian are stored under `testcase/guardian/`.

Generated outputs are diagnostic artifacts, not prompt knowledge. Do not mine
old run outputs as static recipes for future requirements.
