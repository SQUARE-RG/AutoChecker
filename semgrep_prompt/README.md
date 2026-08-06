# Semgrep Prompt v1

This directory contains the formal, requirement-driven Semgrep checker
generator. The supported runtime is under `v1/`; it produces one valid
Semgrep OSS rule for one requirement and improves that rule with measured
paired-sample feedback.

The workflow is generic. It does not contain CWE-specific recipes, project
specific branches, candidate-rule generation, or one branch per validation
sample.

## Environment

Use Python 3.10 and a Semgrep installation that supports the target language:

```bash
/home/meiosis/py310/bin/python -m py_compile semgrep_prompt/v1/*.py
```

The LLM client reads `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` by default.
They can also be supplied on the command line. Do not commit credentials or
generated run output.

## Formal Entry Points

| Entry point | Purpose |
|---|---|
| `v1/semgrep_rule_tool.py` | Generate, validate, evaluate, and repair one rule for one requirement. |
| `v1/run_paired_dataset_batch.py` | Run the formal tool over the configured paired-sample tasks and write a summary. |
| `v1/collect_rule_library.py` | Collect accepted final checkers into the language-organized rule library. |

The main modules are deliberately separated by responsibility:

- `paired_sample_suite.py`: loads and pairs source files.
- `sample_contrast_analyzer.py`: summarizes BAD/GOOD differences.
- `pattern_ir_generation.py`: creates the semantic planning contract for a
  fresh generation.
- `llm_rule_generation.py`: supplies the generation skill and obtains one YAML
  rule from the LLM.
- `semgrep_rule_detection.py` and `semgrep_rule_testing.py`: validate, scan,
  and score a rule.
- `semgrep_repair_mode.py`: local coverage and precision repair using the
  current rule, Semgrep explanations, paired contrast, and failure memory.

## Paired Sample Layout

Each requirement has its own directory. The same case id must appear on both
sides when a BAD/GOOD contrast is available:

```text
<sample-root>/
  <requirement>/
    bad/
      test1.c
      test2.c
    good/
      test1.c
      test2.c
```

The loader uses the file stem as the case id, so `bad/test1.cpp` pairs with
`good/test1.cpp`. Every BAD file is evaluated. A BAD file without a matching
GOOD file remains a BAD case but does not produce a contrast pair. Both
`bad/` and `good/` directories must exist, and supported source extensions
include C/C++, Go, Java, JavaScript/TypeScript, Python, and Rust.

## Run One Requirement

Provide the sample directory, a natural-language requirement, a Semgrep
language id, and an output directory:

```bash
/home/meiosis/py310/bin/python \
  /home/meiosis/data/work/autochecker/code_check/semgrep_prompt/v1/semgrep_rule_tool.py \
  --sample-folder /path/to/samples/<requirement> \
  --requirement "Describe the security or coding property" \
  --target-language c \
  --output-dir /path/to/results/<requirement> \
  --max-attempts 5
```

`--pattern-ir` and `--repair-mode` are enabled by default. Use
`--no-pattern-ir` or `--no-repair-mode` only for a deliberate comparison.
`--max-invalid-retries` controls retries for malformed or Semgrep-invalid
responses; it is separate from the counted iteration limit.

## Run A Batch

The batch runner has the current paired task registry and can be narrowed with
`--only`:

```bash
/home/meiosis/py310/bin/python \
  /home/meiosis/data/work/autochecker/code_check/semgrep_prompt/v1/run_paired_dataset_batch.py \
  --sample-root /path/to/paired-samples \
  --output-dir /path/to/results/paired_batch \
  --max-attempts 5 \
  --only cwe15,cwe468
```

Without `--only`, the runner uses the registered Juliet and GJB paired tasks.
Each task gets its own output directory. `results.json` and
`summary_table.md` are rewritten as tasks finish.

## Runtime Flow

1. Load the paired BAD/GOOD files and create a whole-file evaluation region for
   each case.
2. Analyze paired contrast and prepare a requirement prompt.
3. On fresh generation, ask for a compact Pattern-IR semantic plan, then pass
   its contract together with the distilled generation skill to the rule
   generator.
4. Ask the LLM for exactly one YAML rule and validate it with Semgrep.
5. Scan all paired files and record BAD hits, GOOD false positives, recall,
   precision, and the overall score.
6. For a valid non-zero, non-clean previous rule, run two local repair steps
   in the same iteration: coverage first, then precision. An accepted coverage
   edit becomes the input to precision. A rejected edit leaves the current
   rule unchanged.
7. Select the best counted valid rule, prioritizing BAD coverage, then fewer
   GOOD hits, then overall correctness, and copy it to `final_rule.yml`.

Coverage repair is accepted only when BAD hits increase. Precision repair is
accepted only when BAD hits do not decrease and GOOD false positives decrease.
Coverage and precision rejected-repair memories are kept in separate pools and
are passed only to the corresponding repair direction; fresh generation sees
the two pools under separate labels.

## Iteration Accounting

An iteration counts only after the generated or repaired YAML passes Semgrep
validation and can be evaluated. Empty LLM output, malformed YAML, schema
errors, and Semgrep validation failures are printed to the terminal and retried
without consuming a counted attempt, up to `--max-invalid-retries`.

The repair stage itself does not create Pattern-IR artifacts. Pattern-IR files
are written only under fresh-generation artifacts:

- `pattern_ir_prompt.txt`
- `pattern_ir_payload.json`
- `pattern_ir_contract.txt`

## Output Artifacts

Each single-run output directory normally contains:

- `tool_config.json`: resolved run configuration with the API key redacted.
- `sample_suite_summary.json`: evaluated files and case totals.
- `attempt_N/`: prompts, generated or repaired rules, validation output, and
  evaluation reports for each counted or retried attempt.
- `run_report.json`: complete attempt history, separate repair memories, and
  the selected final rule.
- `final_rule.yml`: the selected single-rule YAML when at least one valid
  counted attempt exists.

## Pattern-IR Contract

Pattern-IR is a lightweight semantic planning layer, not a rule database and
not a fixed template. Its current contract records:

- problem kind and recommended `search` or `taint` mode;
- source, sink, propagator, sanitizer, structural-trigger, sensitive-context,
  and GOOD-exclusion families;
- generalized semantic branches and Semgrep feasibility notes.

For a search-mode requirement, source/sink/propagator/sanitizer fields may be
empty. The generator must express the structural or sensitive-context meaning
in search patterns instead of inventing a taint source. If the contract
conflicts with paired evidence or Semgrep feasibility, the evidence wins.

## Knowledge Documents

Only the following distilled documents are runtime prompt payloads:

- `docs/semgrep_rule_generation_skill.md` is loaded for fresh rule generation.
- `docs/semgrep_repair_skill.md` is loaded for local repair.

The remaining files in `docs/` are reference material for maintaining those
skills: compact syntax, taint details, Pattern-IR guidance, checker classes,
official syntax pages, and source-shape references. They are not implicitly
concatenated into every LLM request. The Pattern-IR prompt is implemented in
`v1/pattern_ir_generation.py` and receives only the prepared requirement and
paired sample context.

## Rule Library and Project Scanning

Reusable accepted checkers are organized as:

```text
rules/
  <language>/
    <source>/
      <checker>.yml
```

The formal collection policy keeps accepted Juliet final rules and final rules
selected from the latest real-project scan, with provenance in rule metadata.
Intermediate generation files and repair candidates are not reusable rules.
After manual review, scan a project directly with Semgrep and one or more
language directories:

```bash
semgrep scan \
  --config semgrep_prompt/rules/python \
  --config semgrep_prompt/rules/javascript \
  /path/to/project
```

Every project finding still requires human review. A generated rule is kept
only when its semantic coverage, precision, parseability, and practical value
are acceptable; Semgrep-hard requirements may be marked partial rather than
forcing a broad rule.

## Generalization Policy

- Use paired examples as contrastive evidence, not as an enumeration list.
- Meaningful standard/library/framework/security APIs, operators, fields, and
  types may be used when they define the requirement.
- Do not memorize paths, filenames, test ids, local variable names, or sample
  counts.
- Choose taint mode only for real source-to-sink flow; use search mode for
  local structural, API, sensitive-context, lifetime, and ordering checks.
- Keep rules within Semgrep's practical local/dataflow capabilities. Do not
  fake cross-function, deep alias, or path-sensitive reasoning with wildcards.
