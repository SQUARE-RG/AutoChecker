# Semgrep Rule Generation Skill

Use this reference when generating or repairing one Semgrep OSS rule for C/C++ from a requirement plus paired BAD/GOOD examples.

## Mission

Return one valid, compact Semgrep YAML rule that captures the requirement's semantic invariant. Generalize from paired BAD/GOOD contrast, but do not memorize paths, filenames, test IDs, line numbers, sample counts, or one-off literals.

Relaxed generalization means using meaningful semantic anchors. It does not mean brute-force enumeration.

## Required Output

- Return strict JSON when the caller asks for JSON.
- Put one complete YAML file in `semgrep_rule_yaml`.
- YAML must have top-level `rules:` and exactly one rule.
- The rule must include `id`, `message`, `severity`, and `languages`.
- Use `languages: [c, cpp]` unless the task explicitly narrows the language.
- Use Semgrep OSS syntax only. Do not emit alternatives, candidates, fallback rules, markdown, or placeholders.

## Decision Process

1. Classify the problem model.
2. Choose search mode or taint mode from the evidence.
3. Identify the BAD trigger and the paired GOOD separator.
4. Build compact semantic branches rather than one branch per sample.
5. Audit YAML shape, metavariable binding, and C/C++ parser stability.

## Problem Models

`source_sink_flow`: A real trust-boundary source reaches a concrete risky sink. Examples include environment, argv, network/file/stdin reads, or API return values flowing into system/configuration/security-sensitive APIs.

`sensitive_sink_context`: A locally sensitive value is written to an output/log/error sink. Sensitive variable, parameter, field, or format-string names are context constraints, not taint sources by themselves.

`structural_misuse`, `api_misuse`, `lifetime_misuse`: Local syntax, API, pointer, memory-layout, ordering, lifetime, or coding-standard issues.

## Mode Selection

- Use taint mode when a real trust-boundary source reaches a concrete sink across statements.
- Use search mode for local structural checks, API misuse, lifetime/order checks, sensitive sink context, and coding-standard rules.
- Do not force taint mode for structural problems.
- Do not avoid taint mode when the evidence is genuinely source-to-sink dataflow.
- If a branch needs cross-function summaries, cross-scope symbol resolution, deep alias/type reasoning, or proof that a later statement is absent, keep that branch partial instead of broadening into GOOD.

## Semantic Anchors

- Concrete standard/library/framework/security API names, operators, type tokens, fields, source APIs, and sink APIs from the requirement/examples may be used when they express the semantic family.
- Do not anchor on user-defined helper or benchmark wrapper names just because they appear in samples.
- Use a wrapper name only when its visible body is itself the local semantic evidence and the requirement is truly about that wrapper family.
- Do not replace meaningful concrete APIs/operators/types with placeholders such as `$SINK(...)`, `$FUNC(...)`, `copy_like`, `format_like`, or `validated_value`.
- If paired GOOD uses the same API/operator as BAD, the shared surface is not enough. Add BAD-only argument context, provenance, operand relation, unsafe token, missing guard, source/sink relation, or a branch-local safe exclusion.

## Search Mode

Valid outer shapes:

```yaml
rules:
  - id: example
    languages: [c, cpp]
    severity: WARNING
    message: message
    patterns:
      - pattern: bad($X);
      - pattern-not: bad("...");
```

```yaml
rules:
  - id: example
    languages: [c, cpp]
    severity: WARNING
    message: message
    pattern-either:
      - pattern: bad1(...);
      - patterns:
          - pattern: bad2($X);
          - pattern-not: bad2("...");
```

Rules:

- `patterns` is AND.
- `pattern-either` is OR.
- Top-level `pattern-either` branches should be simple `pattern` items or flat `patterns` lists.
- Do not nest `pattern-either`.
- Do not put a `patterns:` object inside another `patterns:` list.
- `pattern-not` must be scalar and branch-local.
- Every metavariable in `pattern-not` must already be bound by a positive sibling pattern/context, unless the exclusion is fully concrete.
- `pattern-not` must subtract a narrower safe subset that the positive branch would otherwise match. A broader negative pattern cancels the branch.
- A sibling `pattern-not` is not an order/dominance operator. For release/reset, check/use, or cast/use safety, match a local ordered region with the same metavariable or keep the case partial.

## Taint Mode

Use taint only for real source-to-sink flow:

```yaml
rules:
  - id: example-taint
    languages: [c, cpp]
    severity: WARNING
    message: message
    mode: taint
    pattern-sources:
      - pattern: $DATA = getenv(...)
      - pattern: $TYPE $DATA = getenv(...)
      - pattern: $DATA = argv[$I]
      - pattern: $TYPE $DATA = argv[$I]
      - patterns:
          - pattern: fgets($DATA, ...)
          - focus-metavariable: $DATA
        by-side-effect: true
    pattern-propagators:
      - pattern: $DST = $SRC;
        from: $SRC
        to: $DST
      - pattern: $TYPE $DST = $SRC;
        from: $SRC
        to: $DST
      - pattern: strcpy($DST, $SRC);
        from: $SRC
        to: $DST
        by-side-effect: true
    pattern-sanitizers:
      - patterns:
          - pattern: $DATA = "...";
          - focus-metavariable: $DATA
        by-side-effect: true
    pattern-sinks:
      - pattern: sink($DATA)
    options:
      taint_unify_mvars: true
```

Rules:

- Supported taint keys are `mode: taint`, `pattern-sources`, `pattern-sinks`, `pattern-sanitizers`, `pattern-propagators`, and `options`.
- Do not invent keys such as `pattern-not-sinks`.
- Side-effect sources such as `fgets`, `read`, `recv`, and `scanf` taint the mutated destination argument. Use `patterns` plus `focus-metavariable`, then set `by-side-effect: true` on that entry.
- Return-value sources taint the returned/assigned value. Do not focus an unrelated input/name argument.
- Assignments, declaration initializers, formatting, and copy calls are propagators or local context, not trust-boundary sources.
- Propagators must include explicit `from` and `to`.
- Local sensitive names are not taint sources.

## C/C++ Pattern Stability

- Prefer parse-safe structural Semgrep patterns over regex.
- Statement patterns should be complete statements with semicolons.
- If a pattern starts with `*` or `&`, use a YAML block scalar.
- Model common carrier shapes separately when evidence shows them: declaration initializer, reassignment, direct call argument, return expression, array subscript, pointer dereference, compound assignment, and casted expression.
- Avoid bare subexpression triggers such as `$P + sizeof($T)` or `$P1 - $P2` when BAD nests that expression inside an initializer, assignment, condition, dereference, return, or call argument.
- Do not invent helper statements such as `$OFF = sizeof($T);` when the BAD code has the arithmetic inline.
- Metavariable names do not impose C/C++ types. `$INT`, `$FLOAT`, `$DOUBLE`, `$PTR`, and `$TYPE` are only names unless constrained by concrete type syntax or supported Semgrep type operators.
- Do not put a metavariable in C/C++ type position and then constrain it with `metavariable-regex` or `metavariable-pattern`; Semgrep may not bind type-position metavariables reliably. Prefer concrete parseable type alternatives such as `int $X = ...;`, `long $X = ...;`, `double $X = ...;`, or bind the value expression instead.
- Do not use all-metavariable assignment, arithmetic, member-write, or dereference patterns as complete triggers. Add concrete BAD-only API/operator/type/cast/source/sink/context in the same branch.
- Do not make a standalone cast the finding. Include the risky use, write, call, or arithmetic around it.
- Anonymous C/C++ record declarations and some cast type metavariables are parser-fragile. Prefer smaller structural statement/expression patterns.

## Regex Fallback

Regex is a last-resort local fallback, not the default strategy.

Use `pattern-regex` only when the BAD/GOOD distinction is local but parser-fragile or lexical in a way structural AST patterns cannot express robustly. Keep it tied to the actual BAD signal line/expression. Do not use regex to emulate broad dataflow, type analysis, interprocedural reasoning, or sample enumeration.

Regex rules:

- Prefer structural patterns first.
- Match the actual BAD signal line or expression.
- Do not add declaration/type/setup prefixes unless they appear on the same signal line.
- Prefer single-quoted scalar strings for one-line regexes.
- Use `|-` for block regexes to avoid an unintended trailing newline.
- Prefer portable character classes such as `[A-Za-z_][A-Za-z0-9_]*`.
- Avoid POSIX bracket classes such as `[[:alnum:]]` and `[[:space:]]`.

## Pattern-IR Use

Pattern-IR is a semantic hint layer, not a Semgrep template.

- Implement semantic branches first.
- Use family lists as support material, not catch-all permission.
- `source_families` must contain real trust-boundary operations only.
- `sensitive_context_families` become search-mode constraints.
- `sink_families` and `structural_trigger_families` become compact positive branches.
- `good_path_exclusions` and `sanitizer_families` are precision evidence.
- If Pattern-IR conflicts with paired BAD/GOOD evidence, trust the paired evidence.

## Final Checklist

- YAML has top-level `rules:` and exactly one rule.
- No alternatives, candidates, fallback rules, placeholders, or markdown.
- No sample paths, filenames, test IDs, line numbers, or one-off benchmark literals.
- No user-defined helper/wrapper anchoring unless the visible wrapper body is semantic evidence.
- No unsupported Semgrep keys.
- No nested `pattern-either` or nested `patterns`.
- No fresh metavariables in `pattern-not`.
- No `pattern-not` that subsumes the positive pattern.
- No fake taint source from local variable names.
- No disconnected source/sink metavariables in taint mode.
- No side-effect source without `focus-metavariable` and `by-side-effect`.
- No broad catch-all shared API/operator branch that also matches paired GOOD.
