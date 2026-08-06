# Semgrep Source Reference Cases

This document is a shape-only reference for rule synthesis.
It is derived from Semgrep source rules and collected rule clauses, but it must not be copied verbatim into the final checker.
Use it to borrow structure, operator combinations, and constraint style.

## Case 1: Generic pattern-either with metavariable binding
- Source shape: HTML rules that match one of several equivalent tags or attribute forms.
- Structure: `pattern-either` groups multiple `pattern` clauses.
- Borrowed lesson: keep the rule compact by grouping equivalent syntactic variants under one semantic intent.
- Do not borrow: the exact tag names or rule topic.

## Case 2: Context guard around a positive pattern
- Source shape: rules that match a construct only when a nearby guard is absent or when a contextual block is present.
- Structure: `pattern` plus `pattern-not`, `pattern-inside`, or `pattern-not-inside`.
- Borrowed lesson: use context to reduce false positives instead of widening the sink itself.
- Do not borrow: any task-specific function names or literal literals.

## Case 3: Taint-style source to sink with sanitizers
- Source shape: security rules that model data flowing from an input source to a risky sink.
- Structure: `mode: taint` with explicit source, sink, sanitizer, and optional propagator families.
- Borrowed lesson: express the vulnerability as a data relationship, not as a literal string match.
- Do not borrow: exact API lists unless they are the minimum needed for the target requirement.

## Case 4: Nested metavariable-pattern refinement
- Source shape: rules that first match a broader call or statement and then refine one argument or subexpression.
- Structure: `metavariable-pattern` with inner `pattern-either` alternatives.
- Borrowed lesson: isolate the important subnode instead of enumerating many top-level cases.
- Do not borrow: full sample code blocks.

## Selection policy
- Prefer 1-2 reference cases per attempt.
- Prefer the smallest case set that can express the target invariant.
- Use the references as structural guidance only.
- Do not reuse any literal topic, API list, or file-specific example from the references.
- If the target requires deep cross-function flow, mark it unsupported instead of forcing a source-shaped rule.
