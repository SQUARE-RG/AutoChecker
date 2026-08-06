# Semgrep Repair Skill

Use this compact reference only when repairing one existing Semgrep OSS rule for
C/C++. The repair goal is a local behavioral change, not a fresh rewrite.

## Repair Contract

- Return strict JSON when requested.
- Put one complete YAML file in `semgrep_rule_yaml`.
- Keep top-level `rules:` with exactly one rule.
- Use valid Semgrep OSS syntax only.
- Edit the localized branch or predicate named by the repair contract.
- Do not add candidates, fallback rules, markdown, placeholders, paths,
  filenames, test IDs, line numbers, or one branch per sample.

## Acceptance Semantics

Coverage repair:

- Objective: increase BAD hits.
- A coverage repair is useful only when BAD hit count increases.
- Add one evidence-backed sibling branch or unblock one overblocking predicate.
- Keep existing branches that already hit BAD.
- GOOD FP cleanup is a later precision stage.

Precision repair:

- Objective: reduce GOOD false positives while preserving BAD hits.
- GOOD FP must decrease.
- BAD hit count must not decrease.
- Do not add new coverage branches in precision mode.
- Do not replace the whole rule when a branch-local guard, context, sanitizer,
  or exclusion can express the GOOD/BAD separator.

## Search Mode Syntax

Valid shapes:

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
- Keep `pattern-either` flat: each branch is a `pattern` item or a flat
  `patterns` list.
- Do not nest `pattern-either`.
- Do not put `patterns:` inside another `patterns:` list.
- Every `pattern-not` must be branch-local and must subtract a narrower safe
  subset that overlaps the positive branch.
- Every metavariable used in `pattern-not`, `pattern-inside`, or
  `pattern-not-inside` must be bound by a positive sibling pattern/context,
  unless the exclusion is fully concrete.
- `pattern-not` usually subtracts the same matched statement/expression.
  It is not reliable for subtracting a multi-statement declaration+assignment
  region when the finding span is only the assignment. Prefer matching the
  decisive assignment/return expression and subtracting the casted/safe
  expression on that same span.
- A sibling `pattern-not` cannot prove ordered absence. For check/use,
  release/reset, overwrite/use, or sanitizer/use relations, match a local
  ordered region with the same metavariable or keep the case partial.

## Precision Edits

Prefer one of these local edits:

- Add positive BAD-only context to the overbroad branch.
- Add `pattern-inside` for a surrounding BAD-only local region.
- Add `pattern-not-inside` for an ordered GOOD-only safe region using the same
  bound metavariable.
- Add branch-local `pattern-not` only for a narrower safe subset.
- Add `metavariable-regex`, `metavariable-comparison`, or
  `metavariable-pattern` only for an already-bound metavariable with a real
  semantic separator.
- In taint mode, add a sanitizer or scope guard for validation, allowlist, or
  trusted overwrite seen in GOOD.

Avoid these precision mistakes:

- Do not constrain ordinary identifier spelling when it is only a local sample
  name.
- Do not add global exclusions that suppress unrelated BAD branches.
- Do not remove or rewrite working BAD branches.
- Do not keep an all-metavariable call/operator/type pattern as the only
  positive evidence.

Useful repair idioms:

- Release/reset: bind the released pointer in the positive trigger, then reuse
  the same metavariable in the ordered exclusion, for example
  `pattern: free($P);` plus `pattern-not-inside: free($P); ... $P = NULL;`.
  If the release occurs inside an `if` block, the safe region may need to
  include the enclosing `if (...) { ... free($P); ... $P = NULL; ... }`.
- Explicit cast false positives: prefer a focused assignment/return trigger
  such as `$I = $F;` with local cast exclusions such as `$I = (int)$F;`.
  A declaration+assignment multi-statement `pattern-not` often fails to overlap
  the assignment finding span.
  If GOOD has compound explicit casts such as `(int)a + (int)b`, a small
  line-local `pattern-not-regex` that detects an explicit integer cast on the
  same assignment line may be more reliable than many exact `pattern-not`
  variants.
  If structural cast exclusions do not change behavior, this is
  parser/span-sensitive. A small line-local `pattern-regex` is acceptable only
  when it directly matches the assignment/return signal and avoids sample names;
  otherwise keep the case partial instead of adding broad regex.
- Same-base pointer arithmetic: a bare `$N = $P1 - $P2;` trigger is shared by
  BAD and GOOD. Add local provenance context when visible, or keep this partial
  if proving same base requires alias reasoning.
- Check-before-use: the positive finding should usually be the guarded use
  statement, such as `*$P = ...;` or `$P[...] = ...;`. Put the allocation or
  producer in `pattern-inside` context. If the positive pattern spans from
  allocation through use, a GOOD guard around only the use does not overlap the
  whole finding and `pattern-not-inside` is often a no-op.
  Good guards may be written as `if ($P)`, `if ($P != NULL)`,
  `if (! $P) return;`, a boolean alias, or an explicit bool cast; preserve the
  same pointer metavariable in the guarded-use exclusion.
- Missing final control-flow branch: if a rule uses sibling branches for
  different `if/else if` chain lengths, add the corresponding final-else
  exclusion to every same-family sibling. Fixing only one chain length leaves
  GOOD examples matched by the other siblings.

## Taint Mode Syntax

Use taint only for real source-to-sink dataflow.

```yaml
rules:
  - id: example-taint
    languages: [c, cpp]
    severity: WARNING
    message: message
    mode: taint
    pattern-sources:
      - pattern: $DATA = source(...)
      - patterns:
          - pattern: read($FD, $DATA, ...)
          - focus-metavariable: $DATA
        by-side-effect: true
    pattern-propagators:
      - pattern: $DST = $SRC;
        from: $SRC
        to: $DST
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

- Supported taint keys are `mode: taint`, `pattern-sources`,
  `pattern-sinks`, `pattern-sanitizers`, `pattern-propagators`, and `options`.
- Do not invent keys such as `pattern-not-sinks`.
- Side-effect sources must use `patterns` plus `focus-metavariable` and
  `by-side-effect: true`.
- Propagators must include explicit `from` and `to`.
- Local variable names, sensitive words, assignments, casts, arithmetic, and
  formatting calls are not trust-boundary sources by themselves.

## C/C++ Pattern Stability

- Prefer structural patterns over regex.
- Statement patterns should be complete statements with semicolons.
- If a pattern starts with `*` or `&`, use a YAML block scalar.
- Model carrier shapes separately: declaration initializer, assignment, call
  argument, return expression, array subscript, pointer dereference, compound
  assignment, casted use, and side-effect call.
- Avoid bare subexpression triggers when BAD nests the expression inside a
  statement or call argument. Match the full carrier.
- Metavariable names do not impose types. `$INT`, `$FLOAT`, `$PTR`, `$TYPE`,
  `$GLOBAL`, and `$LOCAL` are only names unless constrained by concrete syntax.
- Do not rely on C/C++ type-position metavariables such as `sizeof($TYPE)` or
  `($TYPE *)$PTR` as the repaired trigger. Use concrete parseable type tokens,
  bind the value expression, or keep the branch partial.

## Regex Fallback

Use `pattern-regex` only for a local parser-fragile or lexical signal that
structural patterns cannot express robustly.

- Keep regex tied to the BAD signal line/expression.
- Do not use regex for broad dataflow, type analysis, interprocedural reasoning,
  or sample enumeration.
- Prefer single-quoted scalar strings for one-line regexes.
- Use `|-` for block regexes.
- Prefer portable classes such as `[A-Za-z_][A-Za-z0-9_]*`.
- Avoid POSIX bracket classes such as `[[:space:]]` and `[[:alnum:]]`.
