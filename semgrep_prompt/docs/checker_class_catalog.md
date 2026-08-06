# Semgrep Checker Class Catalog

This catalog is intentionally abstract. It is not a rule template collection and it does not contain sample-specific code.

## Core classes

1. `node_op`
- Use when the vulnerability can be expressed as a local AST pattern.
- Typical building blocks: `pattern`, `pattern-regex`, `metavariable-regex`, `metavariable-type`.
- Best for direct sink signatures, fixed API calls, local comparisons, and structural misuse.

2. `context_traversal`
- Use when the rule needs surrounding context or local exclusion.
- Typical building blocks: `patterns`, `pattern-either`, `pattern-not`, `pattern-inside`, `pattern-not-inside`.
- Best for source+sink conjunction, branch-specific guards, and same-base or same-context exclusions.

3. `tool_specific_taint`
- Use when the checker needs explicit source/sink/sanitizer semantics.
- Typical building blocks: `mode: taint`, `pattern-sources`, `pattern-sinks`, `pattern-sanitizers`, `pattern-propagators`, `by-side-effect`.
- Best for direct intra-procedural flows with reusable source and sink families.

4. `metavariable_linking`
- Use when one metavariable must appear consistently across multiple parts of the rule.
- Best for shared value propagation, paired source/sink modeling, and exclusion of constant-only branches.

5. `precision_guard`
- Use when a rule is too broad and needs narrow negative constraints.
- Typical building blocks: `pattern-not`, `pattern-not-inside`, literal exclusions, same-base exclusions.

## Selection policy

- Pick 1 to 2 classes per rule attempt.
- Prefer the smallest class set that still expresses the vulnerability invariant.
- If a case needs deep inter-procedural flow, mark it unsupported instead of forcing a fake bridge.
- Do not enumerate concrete Juliet file shapes or sample-specific lines.

## Semgrep capability boundary

- Reliable: intra-procedural source -> sink matching.
- Unreliable: cross-function dataflow reconstruction.
- Forbidden: bridge rules that simulate calls.

## Prompt usage

- First decide which checker classes apply.
- Then generate the rule using those classes.
- Keep the final rule compact and parser-safe.