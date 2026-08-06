# Semgrep Compact Guide (Core Syntax, Taint Modeling, Principles, Limitations)

This document is a compressed, high-signal reference for LLM-driven rule generation and repair.
Its goals are:
1) avoid overfitting to validation samples,
2) enforce source-to-sink variable linkage in taint rules,
3) keep rules parseable and semantically generalizable.

---

## 1. Mental Model: Search Mode vs Taint Mode

### Search mode (default)
**Principle**  
Search mode is structural matching. It detects code shapes and local semantic structure.

**Use when**  
- The issue is mostly syntactic/structural (e.g., missing checks, unsafe construct shape).
- You can express the violation without modeling dataflow propagation.

### Taint mode (`mode: taint`)
**Principle**  
Taint mode tracks data from sources to sinks with optional sanitization/propagation.

**Use when**  
- The issue fundamentally depends on dataflow: untrusted or sensitive data reaches dangerous operations.
- You need explicit SOURCE -> DATA -> SINK semantics.

**Selection rule**
- Prefer search mode for local shape constraints (more stable, easier to validate).
- Use taint mode only when cross-statement dataflow is essential.

---

## 2. Core Search Syntax: Principles + Usage

## `pattern`
**Principle**: define one structural condition.  
**Usage**: put one parse-safe code shape.

## `patterns`
**Principle**: logical AND (all children must hold).  
**Usage**: combine trigger + context + exclusions as layered constraints.

## `pattern-either`
**Principle**: logical OR (any branch can match).  
**Usage**: represent semantic families, not sample-by-sample branches.

## `pattern-not`
**Principle**: exclude compliant or non-vulnerable forms.  
**Usage**: remove common safe patterns to reduce false positives.

## `pattern-inside` / `pattern-not-inside`
**Principle**: constrain surrounding context.  
**Usage**: enforce that a pattern appears (or does not appear) in a required structural scope.

## `metavariable-pattern`
**Principle**: second-stage structural constraint over a metavariable.  
**Usage**: refine a metavariable by requiring it to match a subpattern.

## `...` (ellipsis)
**Principle**: abstract irrelevant middle code while preserving order.  
**Usage**: model sequence-sensitive logic without enumerating variants.

### Structural best practices
- First encode the violation trigger, then encode compliant exclusions.
- Use parse-safe complete snippets (especially for C/C++).
- Do not write textual alternatives like `"A or B"` in one pattern string; split into `pattern-either` branches.
- Prefer structure over regex whenever possible.

---

## 3. Taint Syntax: Correct Schema and Variable Linking

## Supported keys (taint mode)
- `mode: taint`
- `pattern-sources`
- `pattern-sinks`
- `pattern-sanitizers` (optional)
- `pattern-propagators` (optional)
- `options` (optional; e.g., `taint_unify_mvars`)

## Do not invent unsupported keys
Examples of invalid style: custom taint keys like `pattern-not-sinks`.

## Mandatory data-linking rule
Use one canonical tainted metavariable (recommended: `$DATA`) across source, propagator, and sink.

- Source introduces taint on `$DATA`.
- Propagator moves taint from `$DATA` to another variable with explicit `from` / `to`.
- Sink consumes the same tainted data variable lineage.
- Do **not** use disconnected sink metavariables (e.g., source uses `$DATA`, sink uses unrelated `$X`).

### Minimal taint skeleton
```yaml
rules:
  - id: example-taint
    languages: [c, cpp]
    severity: WARNING
    mode: taint
    pattern-sources:
      - pattern: source_api(..., $DATA, ...)
    pattern-propagators:
      - pattern: $DST = $DATA
        from: $DATA
        to: $DST
    pattern-sinks:
      - pattern: sink_api(..., $DATA, ...)
    pattern-sanitizers:
      - pattern: is_validated($DATA)
    options:
      taint_unify_mvars: true
```

---

## 4. C/C++ Modeling Notes (High-impact for Juliet-style tasks)

1) **By-side-effect sources** (`fgets/read/recv/scanf` family)  
**Principle**: taint is on destination buffer/argument, not fake return assignment.  
**Usage**: bind the written buffer argument as tainted data.

2) **By-side-effect sanitizers** (`strcpy(dst, "...")`, assignment to literal, copy from trusted constant)  
**Principle**: taint should be cleared from the destination that is overwritten, not from the call expression.  
**Usage**: put the overwrite in `pattern-sanitizers` with `focus-metavariable` on the destination and `by-side-effect: true`. Use generic string-literal patterns (`"..."`) instead of listing safe literal values.

3) **Parser stability first**  
Use complete and parse-safe snippets; avoid fragile forms that frequently break parser validation.
Anonymous C/C++ record declarations are especially parser-fragile as AST patterns. Avoid bare patterns such as `struct { ... };` or `union { ... };`; use a tight `pattern-regex` for the declaration token surface instead.

4) **Regex scalar hygiene**  
For `pattern-regex`, prefer single-quoted scalar strings for one-line regexes. If a block scalar is needed, use `|-` so the regex does not accidentally include a trailing newline.

5) **Avoid sample brute-force enumeration**  
Model source/sink families and invariants, not file-specific/API-by-API over-expansion.

---

## 5. Pattern-IR to Semgrep Mapping

Pattern-IR should describe the rule's semantic contract before YAML is generated.

- `problem_model.kind` controls the rule mode. Use `source_sink_flow` for real source-to-sink problems; use `sensitive_sink_context` for sensitive local values reaching output sinks; use search mode for local structural/API/lifetime misuse.
- `source_families` should contain concrete trust-boundary operations only. Do not treat local variable names, assignments, arithmetic, or member access as taint sources.
- `sensitive_context_families` should contain sensitive variable/parameter/field/string context. Translate it to search-mode metavariable constraints, not taint sources.
- `sink_families` and `structural_trigger_families` should be translated into compact Semgrep branches. Each branch must still encode the vulnerability invariant.
- `good_path_exclusions` and `sanitizer_families` are first-class requirements, not optional cleanup. They should become `pattern-not`, `pattern-not-inside`, `pattern-sanitizers`, or branch-local metavariable constraints.
- `semantic_branches` are the highest-priority contract. Generate from these branches first, then use family lists as support.
- `semgrep_mapping.primary_rule_mode` is a strong default, but parseability and precision can justify switching to search mode.
- `pattern-not` clauses should share metavariables already bound by the same positive branch, or use concrete syntax. Fresh metavariables in an exclusion often erase valid matches or make the branch empty.
- Do not use `metavariable-regex` as a metavariable-to-metavariable comparison. Regex text does not expand `$OTHER` metavariables.
- For C/C++ statement patterns, include semicolons. Model declaration initializers (`$TYPE $V = ...;`) separately from reassignments (`$V = ...;`).

The final rule should not expose Pattern-IR placeholders such as generic `$SINK(...)`, bare `$DATA`, or invented function names.

---

## 6. Good/Bad Separation Rules

- If compliant examples contain the same operator/API family as violating examples, do not use a catch-all operator/API branch.
- Add the missing distinction: source provenance, sink argument sensitivity, sanitizer/constant overwrite, same-base versus different-base relationship, unsafe scaling/cast, or required surrounding context.
- If the requirement has multiple semantic families with different safe-path exclusions, represent them as separate compact branches rather than one wildcard branch.
- For output/exposure checks, search-mode context is often more precise than fake taint when the only evidence is a sensitive variable/parameter name.
- Wrapper functions should be modeled only when the wrapper body is visible to local Semgrep matching.
- For pointer/base problems, a bare subtraction/addition operator is not a complete vulnerability trigger when GOOD contains the same operator.
- If the unsafe operand is a variable initialized earlier (for example `p = lookup(base, ...)`), bind the initializer and later operation as separate ordered/contextual patterns. Do not use `metavariable-pattern` to make the variable text equal the initializer expression.
- Distinguishing context must connect to the expression operands. Generic function-scope declarations are not enough to prove BAD-only context.
- For layout/reinterpretation problems, consider union alternate member writes and byte/half-word views in addition to cast-plus-offset patterns.

---

## 7. Anti-overfitting Checklist (Generation + Repair)

- Do not encode case IDs, filenames, or benchmark-specific artifacts.
- Do not create one branch per example variant.
- Do not enumerate branch-count variants (e.g., else-if length 2/3/4) as separate semantics.
- Use shared metavariables and structural invariants.
- Remove redundant near-duplicate branches before adding new ones.

---

## 8. Practical Limits of Semgrep (Must be explicit)

- Deep interprocedural/path-sensitive reasoning is limited in many practical OSS workflows.
- Some language constructs/macros/declaration patterns are parser-sensitive.
- Taint is not full program proof; precision requires careful source/sink/sanitizer/context design.

**Policy**
- Prefer robustly expressible constraints.
- If a variant fundamentally needs unsupported deep analysis, do not force brittle overmatching.

---

## 9. Output Quality Contract for LLM

When generating or repairing rules:
1) Parseability and schema correctness first.
2) Preserve abstract vulnerability property; do not mirror sample text.
3) Keep rules compact and non-redundant.
4) Every final rule must include top-level `rules:` and the required Semgrep rule keys: `id`, `message`, `severity`, and `languages`.
5) Explicitly explain:
   - semantic property,
   - why it generalizes,
   - how source/sink/sanitizer relations are enforced.
