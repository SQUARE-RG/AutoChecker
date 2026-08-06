# Semgrep Taint Syntax Knowledge (Official-Docs Derived)

This note distills syntax constraints from Semgrep docs for stable C/C++ rule generation.

## 1. Mode Selection (Search vs Taint)
- Prefer `mode: taint` only when detection requires SOURCE -> DATA -> SINK across multiple statements.
- Prefer search mode (`patterns` / `pattern-either`) when one local structural pattern is enough.
- Do not force taint for every CWE. Wrong taint modeling causes parser/runtime failures and weak precision.

## 2. Required Keys in Taint Mode
- `mode: taint`
- `pattern-sources`
- `pattern-sinks`

Optional but common:
- `pattern-sanitizers`
- `pattern-propagators`
- `options`

Do not invent unsupported keys (for example `pattern-not-sinks`).

## 3. Propagator Shape (Critical)
- Use explicit `from` and `to` when writing `pattern-propagators`.
- Keep one canonical tainted metavariable chain (for example `$DATA`) through source/propagator/sink.
- Add propagators for value movement that is present in the paired evidence, such as assignment, declaration initializer, and copy-like calls. Do not invent wrapper names.

Example shape:
```yaml
pattern-propagators:
  - pattern: $DST = $SRC
    from: $SRC
    to: $DST
  - pattern: $TYPE $DST = $SRC
    from: $SRC
    to: $DST
  - pattern: strcpy($DST, $SRC)
    from: $SRC
    to: $DST
    by-side-effect: true
```

## 4. Side-Effect Sources
- For APIs that write into buffers by side effect (for example `fgets`, `read`, `recv`, `scanf` family), model the destination buffer as tainted.
- Use `by-side-effect: true` where needed so taint is attached to the mutated target.
- Add `focus-metavariable` for the mutated destination so the source binds the buffer/value, not just the whole call expression.
- For scanf-like calls, model address-taking forms (`&$DATA`) when language/API semantics require it.
- For return-value sources, the tainted value is the returned expression or the variable receiving it, not an unrelated input/name argument. Use `$DATA = source(...)`, `$TYPE $DATA = source(...)`, or the call expression itself when it flows directly to a sink.
- For argv-style evidence, model the assigned/declaration target, for example `$DATA = argv[$I];` or `$TYPE $DATA = argv[$I];`.

Example shape:
```yaml
pattern-sources:
  - patterns:
      - pattern: fgets($DATA, ...)
      - focus-metavariable: $DATA
    by-side-effect: true
  - patterns:
      - pattern: scanf(..., &$DATA, ...)
      - focus-metavariable: $DATA
    by-side-effect: true
  - pattern: $DATA = getenv(...)
  - pattern: $TYPE $DATA = getenv(...)
  - pattern: $DATA = argv[$I]
  - pattern: $TYPE $DATA = argv[$I]
```

## 5. Sink Linkage
- Sink argument must consume the same tainted metavariable linked from source/propgator.
- Avoid disconnected sink placeholders (for example source uses `$DATA` but sink uses unrelated `$X`).

## 6. Sanitizer Modeling
- Put sanitizer logic in `pattern-sanitizers`.
- Sanitizer patterns should be semantically tied to validation/allowlist behavior, not generic noise filters.
- For side-effect sanitizers that overwrite a tainted buffer/value with trusted data, bind the overwritten destination with `focus-metavariable` and `by-side-effect: true`.
- For trusted literal overwrites, prefer generic string-literal patterns such as `"..."` instead of enumerating specific safe values.
- Use `"..."` for any string literal in Semgrep patterns. Do not use quoted metavariables like `"$LIT"` to mean "any string literal".
- Do not include side-effect source patterns such as `recv(...)`, `read(...)`, `scanf(...)`, or `fread(...)` unless the written destination argument is explicitly present as a metavariable and focused.

Example shape:
```yaml
pattern-sanitizers:
  - patterns:
      - pattern: strcpy($DATA, "...")
      - focus-metavariable: $DATA
    by-side-effect: true
  - patterns:
      - pattern: $DATA = "..."
      - focus-metavariable: $DATA
    by-side-effect: true
```

## 7. Pattern Syntax Hygiene
- Keep YAML parse-safe (quote scalar strings with `:`).
- Keep patterns expression-level and parser-stable; avoid declaration-heavy snippets in taint sources.
- C/C++ statement patterns should be complete statements with semicolons, for example `return $X;`.
- Declaration initializers and later assignments are different shapes: `$TYPE $X = $EXPR;` does not cover `$X = $EXPR;`.
- Match the expression shape that actually exists in BAD evidence. If the BAD arithmetic is inline in a dereference, initializer, call argument, or compound assignment, do not invent a separate `$OFF = ...;` helper statement.
- If a pattern begins with `*` or `&`, use a YAML block scalar so YAML does not parse an alias or anchor.
- Prefer compact branching; avoid giant API enumeration lists.
- Reuse metavariables consistently; this improves both matching stability and explainability.

## 7.1 Search-Mode Structural Shapes
- Use one of three outer shapes:
  - Single-branch search: `patterns` containing positive context plus optional exclusions.
  - OR search: top-level `pattern-either`, where each branch is either a simple `pattern` or a flat `patterns` list.
  - Taint: `mode: taint` with `pattern-sources` and `pattern-sinks`.
- Do not nest `pattern-either` inside another `pattern-either`. If two dimensions vary, flatten the combinations into sibling branches.
- Do not put a `patterns` object inside another `patterns` list. A `patterns` list contains operator objects such as `pattern`, `pattern-not`, `pattern-inside`, `pattern-not-inside`, `metavariable-pattern`, or one simple `pattern-either`.
- Every metavariable used in `pattern-not` must already be bound by a positive sibling pattern/context in the same branch. Fresh metavariables in exclusions often make the rule invalid or semantically meaningless.
- Use `pattern-not` only when the safe form would otherwise be matched by the positive branch. If the GOOD code is already structurally different from the BAD trigger, no exclusion is needed.
- If the safe form needs an unrelated object/name, do not express it as `pattern-not` with fresh metavariables. Add positive BAD-only context or split branches instead.
- C/C++ cast patterns with type metavariables can be parser-fragile. Prefer concrete cast tokens from evidence, or bind a wider expression metavariable, rather than generating malformed casts such as `(($T) *)`.
- A standalone cast is usually not a complete finding. Include the risky use/write/call around the cast, or use a tight line-oriented `pattern-regex` for the full operation.
- Normal AST `pattern` matching may normalize away lexical spelling such as redundant parentheses. If paired BAD/GOOD only differ by explicit parentheses around a binary expression, prefer a tightly scoped `pattern-regex` branch or mark that family partial instead of relying on AST `pattern-not`.
- `pattern-regex` should match the actual BAD signal line or expression. Do not add declaration/type/assignment prefixes unless those tokens appear on that same line. For control-flow conditions, anchor around the control keyword and operator/comparison tokens.
- `pattern-regex` is often more stable than C/C++ parser-heavy patterns for local lexical token checks such as `sizeof(...)` inside pointer arithmetic, anonymous `struct {`, assignment inside a condition, or a release call not followed by an ordered reset.
- Prefer portable classes such as `[A-Za-z_][A-Za-z0-9_]*` in generated regexes. Avoid POSIX bracket classes like `[[:alnum:]]` unless the rule has already validated with Semgrep.

Valid branch-local exclusion shape:
```yaml
pattern-either:
  - patterns:
      - pattern: $OBJ.$FIELD = $X;
      - pattern-not: $OBJ.$FIELD = 0;
  - patterns:
      - pattern: sink($DATA);
      - metavariable-pattern:
          metavariable: $DATA
          pattern-either:
            - pattern: $SECRET
            - pattern: $TOKEN
```

Invalid fresh-metavariable exclusion:
```yaml
patterns:
  - pattern: $OBJ.$FIELD = $X;
  - pattern-not: $SAFE.$FIELD = $Y;
```

## 8. Pattern-IR Contract
Pattern-IR is a semantic contract between example analysis and final rule generation. It is not a Semgrep rule template.

Required fields to preserve:
- `problem_model.kind`: choose `source_sink_flow` only for real dataflow from a source to a sink; choose `sensitive_sink_context` when local sensitive names/parameters reach output sinks; choose `structural_misuse`, `api_misuse`, or `lifetime_misuse` for local AST misuse.
- `vulnerability_logic.source_families`: real trust-boundary operations only. Local assignments, copies, arithmetic, or identifier names are propagators/context, not sources.
- `vulnerability_logic.sensitive_context_families`: local variable/parameter/field/string context proving that a sink argument is sensitive. These entries are search-mode constraints, not taint sources.
- `vulnerability_logic.sink_families`: concrete risky operation/output/API families or structural operations to flag.
- `vulnerability_logic.structural_trigger_families`: local bad operations for search-mode rules.
- `vulnerability_logic.semantic_branches`: each branch groups one BAD semantic family with required context and GOOD exclusions. This is the main rule-generation contract.
- `vulnerability_logic.good_path_exclusions` and `sanitizer_families`: paired compliant conditions that must stay clean.
- `semgrep_mapping.primary_rule_mode`: final YAML should follow this mode unless parser correctness or precision is better served by switching to search mode.

Use Pattern-IR by translating families into compact Semgrep clauses. Do not copy placeholders unchanged, and do not create one branch per sample.

## 9. Good/Bad Contrast Rules
- If GOOD examples use the same call, operator, or output family as BAD examples, a catch-all match for that family is too broad.
- Add the distinguishing condition shown by the paired evidence instead of relying on the shared surface form.
- Treat GOOD-only feature families as safe anchors. The concrete anchor type must come from the current paired examples, not from a stored CWE-specific recipe.
- A safe anchor should become a branch-local exclusion/guard only when it overlaps the BAD core. Do not put a syntax shape into global exclusions if the same shape is BAD in another context.
- Placeholder exclusions that merely assert syntactic equality rarely prove semantic safety; prefer local context or a narrower positive branch.
- If two bad families require opposite exclusions, keep them as separate compact branches with branch-local guards.
- If a metavariable is bound by a prior initializer/assignment, match that statement separately with `patterns` or `pattern-inside`; do not constrain the variable metavariable as though it were the initializer expression.
- `pattern-not` must be linked to already-bound metavariables or concrete syntax. A fresh placeholder only in `pattern-not` is usually not a real exclusion.
- Do not use `metavariable-regex` to compare two metavariables. The regex is applied to one metavariable's text and does not expand `$OTHER`.
- If the distinguishing evidence is lexical rather than AST-semantic, such as parenthesized vs unparenthesized operator operands, use `pattern-regex` with narrow context or report partial support. Do not expect ordinary AST patterns to preserve optional parentheses.
- Regex branches should be small and line-oriented. A regex for an `if (...)` condition should not require a nearby declaration or assignment unless the vulnerable line itself contains that declaration or assignment.
- In C/C++, assignment and declaration patterns should be complete statements with semicolons; include declaration initializer and reassignment variants separately when both appear.
- For multi-argument calls, local transformations, wrappers, casts, guards, or ordered cleanup/check sequences, only model the parts that are present in the current BAD/GOOD evidence and necessary for separation.
- For declaration-heavy rules, Semgrep's C/C++ parser may reject large declaration-block metavariable patterns. Prefer smaller expression/line-oriented patterns or mark deep scope/tag reasoning partial.

## 10. Common Failure Checklist
- Missing `from`/`to` in propagators.
- No canonical metavariable linkage across source/sink.
- Side-effect API modeled as assignment when no assignment exists.
- Overusing taint where search mode is sufficient.
- Excessive sink/API enumeration causing fragile overfit rules.
- Catch-all structural operators that also match paired GOOD examples.
- Sensitive-output rules that invent taint sources from local variable names instead of using search-mode context.

## 11. Reference Pages
- https://semgrep.dev/docs/writing-rules/data-flow/taint-mode
- https://semgrep.dev/docs/writing-rules/rule-syntax
- https://semgrep.dev/docs/writing-rules/pattern-syntax
