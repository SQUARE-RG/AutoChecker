# Example 1
Codeql query source code:
```query
/**
 * @name Inappropriate Intimacy
 * @description Two files share too much information about each other (accessing many operations or variables in both directions). It would be better to invert some of the dependencies to reduce the coupling between the two files.
 * @kind problem
 * @problem.severity recommendation
 * @precision medium
 * @id cpp/file-intimacy
 * @tags maintainability
 *       modularity
 *       statistical
 *       non-attributable
 */

import cpp

predicate remoteVarAccess(File source, File target, VariableAccess va) {
  va.getFile() = source and
  va.getTarget().getFile() = target and
  // Ignore variables with locations in multiple files
  strictcount(File f | f = va.getTarget().getFile()) = 1 and
  source != target
}

predicate remoteFunAccess(File source, File target, FunctionCall fc) {
  fc.getFile() = source and
  fc.getTarget().getFile() = target and
  // Ignore functions with locations in multiple files
  strictcount(File f | f = fc.getTarget().getFile()) = 1 and
  source != target
}

predicate candidateFilePair(File source, File target) {
  remoteVarAccess(source, target, _) or
  remoteFunAccess(source, target, _)
}

predicate variableDependencyCount(File source, File target, int res) {
  candidateFilePair(source, target) and
  res = count(VariableAccess va | remoteVarAccess(source, target, va))
}

predicate functionDependencyCount(File source, File target, int res) {
  candidateFilePair(source, target) and
  res = count(FunctionCall fc | remoteFunAccess(source, target, fc))
}

predicate highDependencyCount(File source, File target, int res) {
  exists(int varCount, int funCount |
    variableDependencyCount(source, target, varCount) and
    functionDependencyCount(source, target, funCount) and
    res = varCount + funCount and
    res > 20
  )
}

from File a, File b, int ca, int cb
where
  highDependencyCount(a, b, ca) and
  highDependencyCount(b, a, cb) and
  ca >= cb and
  a != b and
  not a instanceof HeaderFile and
  not b instanceof HeaderFile and
  b.getShortName().trim().length() > 0
select a,
  "File is too closely tied to $@ (" + ca.toString() + " dependencies one way and " + cb.toString() +
    " the other).", b, b.getBaseName()
```

output:

```json
[
    {{
        "meta_op": "Define cross-file variable access from a source file to a target file, excluding self-access and symbols spanning multiple files.",
        "meta_impl": "predicate remoteVarAccess(File source, File target, VariableAccess va) {\n  va.getFile() = source and\n  va.getTarget().getFile() = target and\n  strictcount(File f | f = va.getTarget().getFile()) = 1 and\n  source != target\n}"
    }},
    {{
        "meta_op": "Define cross-file function call access from a source file to a target file, excluding self-access and functions with locations in multiple files.",
        "meta_impl": "predicate remoteFunAccess(File source, File target, FunctionCall fc) {\n  fc.getFile() = source and\n  fc.getTarget().getFile() = target and\n  strictcount(File f | f = fc.getTarget().getFile()) = 1 and\n  source != target\n}"
    }},
    {{
        "meta_op": "Identify candidate file pairs that have at least one variable or function dependency from source to target.",
        "meta_impl": "predicate candidateFilePair(File source, File target) {\n  remoteVarAccess(source, target, _) or\n  remoteFunAccess(source, target, _)\n}"
    }},
    {{
        "meta_op": "Count the number of variable accesses from a source file to a target file for candidate file pairs.",
        "meta_impl": "predicate variableDependencyCount(File source, File target, int res) {\n  candidateFilePair(source, target) and\n  res = count(VariableAccess va | remoteVarAccess(source, target, va))\n}"
    }},
    {{
        "meta_op": "Count the number of function calls from a source file to a target file for candidate file pairs.",
        "meta_impl": "predicate functionDependencyCount(File source, File target, int res) {\n  candidateFilePair(source, target) and\n  res = count(FunctionCall fc | remoteFunAccess(source, target, fc))\n}"
    }},
    {{
        "meta_op": "Compute the total dependency count (variables plus functions) between two files and require it to exceed a fixed threshold.",
        "meta_impl": "predicate highDependencyCount(File source, File target, int res) {\n  exists(int varCount, int funCount |\n    variableDependencyCount(source, target, varCount) and\n    functionDependencyCount(source, target, funCount) and\n    res = varCount + funCount and\n    res > 20\n  )\n}"
    }},
    {{
        "meta_op": "Select pairs of non-header source files that exhibit high mutual dependency in both directions and enforce ordering and basic name validity.",
        "meta_impl": "from File a, File b, int ca, int cb\nwhere\n  highDependencyCount(a, b, ca) and\n  highDependencyCount(b, a, cb) and\n  ca >= cb and\n  a != b and\n  not a instanceof HeaderFile and\n  not b instanceof HeaderFile and\n  b.getShortName().trim().length() > 0"
    }},
    {{
        "meta_op": "Report the source file with an inappropriate intimacy diagnostic message that includes dependency counts and references the coupled target file.",
        "meta_impl": "select a,\n  \"File is too closely tied to $@ (\" + ca.toString() + \" dependencies one way and \" + cb.toString() +\n    \" the other).\", b, b.getBaseName()"
    }}
]

```



# Example 2
Codeql query source code:
```query
/**
 * @name Comparison with canceling sub-expression
 * @description If the same sub-expression is added to both sides of a
 *              comparison, and there is no possibility of overflow or
 *              rounding, then the sub-expression is redundant and could be
 *              removed.
 * @kind problem
 * @problem.severity recommendation
 * @precision medium
 * @id cpp/comparison-canceling-subexpr
 * @tags readability
 *       maintainability
 */

import cpp
import semmle.code.cpp.rangeanalysis.SimpleRangeAnalysis
import BadAdditionOverflowCheck
import PointlessSelfComparison

/**
 * Holds if `parent` is a linear expression of `child`. For example:
 *
 *     `parent = child + E`
 *     `parent = E - child`
 *     `parent = 2 * child`
 */
private predicate linearChild(Expr parent, Expr child, float multiplier) {
  child = parent.(AddExpr).getAChild() and multiplier = 1.0
  or
  child = parent.(SubExpr).getLeftOperand() and multiplier = 1.0
  or
  child = parent.(SubExpr).getRightOperand() and multiplier = -1.0
  or
  child = parent.(UnaryPlusExpr).getOperand() and multiplier = 1.0
  or
  child = parent.(UnaryMinusExpr).getOperand() and multiplier = -1.0
}

/**
 * Holds if `child` is a linear sub-expression of `cmp`, and `multiplier`
 * is its multiplication factor. For example:
 *
 *     `4*x - y < 3*z`
 *
 * In this example, `x` has multiplier 4, `y` has multiplier -1, and `z`
 * has multiplier -3 (multipliers from the right hand child are negated).
 */
private predicate cmpLinearSubExpr(ComparisonOperation cmp, Expr child, float multiplier) {
  not convertedExprMightOverflow(child) and
  (
    child = cmp.getLeftOperand() and multiplier = 1.0
    or
    child = cmp.getRightOperand() and multiplier = -1.0
    or
    exists(Expr parent, float m1, float m2 |
      cmpLinearSubExpr(cmp, parent, m1) and
      linearChild(parent, child, m2) and
      multiplier = m1 * m2
    )
  )
}

/**
 * Holds if `cmpLinearSubExpr(cmp, child, multiplier)` holds and
 * `child` is an access of variable `v`.
 */
private predicate cmpLinearSubVariable(
  ComparisonOperation cmp, Variable v, VariableAccess child, float multiplier
) {
  v = child.getTarget() and
  not exists(child.getQualifier()) and
  cmpLinearSubExpr(cmp, child, multiplier)
}

/**
 * Holds if there are two linear sub-expressions of `cmp` that
 * cancel each other. For example, `v` can be cancelled in each of
 * these examples:
 *
 *     `v < v`
 *     `v + x - v < y`
 *     `v + x + v < y + 2*v`
 */
private predicate cancelingSubExprs(ComparisonOperation cmp, VariableAccess a1, VariableAccess a2) {
  exists(Variable v |
    exists(float m | m < 0 and cmpLinearSubVariable(cmp, v, a1, m)) and
    exists(float m | m > 0 and cmpLinearSubVariable(cmp, v, a2, m))
  ) and
  not any(ClassTemplateInstantiation inst).getATemplateArgument() = cmp.getParent*()
}

from ComparisonOperation cmp, VariableAccess a1, VariableAccess a2
where
  cancelingSubExprs(cmp, a1, a2) and
  // Most practical examples found by this query are instances of
  // BadAdditionOverflowCheck or PointlessSelfComparison.
  not badAdditionOverflowCheck(cmp, _) and
  not pointlessSelfComparison(cmp)
select cmp, "Comparison can be simplified by canceling $@ with $@.", a1, a1.getTarget().getName(),
  a2, a2.getTarget().getName()
```

output:

```json
[
    {{
        "meta_op": "Define when one expression is a direct linear child of another expression and compute the corresponding multiplier.",
        "meta_impl": "private predicate linearChild(Expr parent, Expr child, float multiplier) {\n  child = parent.(AddExpr).getAChild() and multiplier = 1.0\n  or\n  child = parent.(SubExpr).getLeftOperand() and multiplier = 1.0\n  or\n  child = parent.(SubExpr).getRightOperand() and multiplier = -1.0\n  or\n  child = parent.(UnaryPlusExpr).getOperand() and multiplier = 1.0\n  or\n  child = parent.(UnaryMinusExpr).getOperand() and multiplier = -1.0\n}"
    }},
    {{
        "meta_op": "Recursively derive all linear sub-expressions of a comparison and accumulate their multipliers while excluding sub-expressions that may overflow due to conversions.",
        "meta_impl": "private predicate cmpLinearSubExpr(ComparisonOperation cmp, Expr child, float multiplier) {\n  not convertedExprMightOverflow(child) and\n  (\n    child = cmp.getLeftOperand() and multiplier = 1.0\n    or\n    child = cmp.getRightOperand() and multiplier = -1.0\n    or\n    exists(Expr parent, float m1, float m2 |\n      cmpLinearSubExpr(cmp, parent, m1) and\n      linearChild(parent, child, m2) and\n      multiplier = m1 * m2\n    )\n  )\n}"
    }},
    {{
        "meta_op": "Restrict linear sub-expressions to unqualified variable accesses and associate each with its variable and computed multiplier.",
        "meta_impl": "private predicate cmpLinearSubVariable(\n  ComparisonOperation cmp, Variable v, VariableAccess child, float multiplier\n) {\n  v = child.getTarget() and\n  not exists(child.getQualifier()) and\n  cmpLinearSubExpr(cmp, child, multiplier)\n}"
    }},
    {{
        "meta_op": "Detect pairs of variable accesses in a comparison whose linear multipliers have opposite signs, indicating canceling sub-expressions, while excluding template argument contexts.",
        "meta_impl": "private predicate cancelingSubExprs(ComparisonOperation cmp, VariableAccess a1, VariableAccess a2) {\n  exists(Variable v |\n    exists(float m | m < 0 and cmpLinearSubVariable(cmp, v, a1, m)) and\n    exists(float m | m > 0 and cmpLinearSubVariable(cmp, v, a2, m))\n  ) and\n  not any(ClassTemplateInstantiation inst).getATemplateArgument() = cmp.getParent*()\n}"
    }},
    {{
        "meta_op": "Select comparison operations that contain canceling sub-expressions and filter out cases already covered by bad addition overflow checks or pointless self-comparisons.",
        "meta_impl": "from ComparisonOperation cmp, VariableAccess a1, VariableAccess a2\nwhere\n  cancelingSubExprs(cmp, a1, a2) and\n  not badAdditionOverflowCheck(cmp, _) and\n  not pointlessSelfComparison(cmp)"
    }},
    {{
        "meta_op": "Report the comparison along with both canceling variable accesses, emitting a diagnostic that suggests simplification by canceling the redundant sub-expressions.",
        "meta_impl": "select cmp, \"Comparison can be simplified by canceling $@ with $@.\", a1, a1.getTarget().getName(),\n  a2, a2.getTarget().getName()"
    }}
]
```