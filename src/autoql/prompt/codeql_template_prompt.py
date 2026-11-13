"""Single Java CodeQL generation skeleton used by the Query Agent.

The Analysis V2 contract deliberately does not select an ``analysis_kind`` or
produce a separate query model. Query synthesis always starts from this one
skeleton and derives its concrete source, sink, barrier, and flow predicates
from ``vulnerability_summary`` and the program-materialized evidence.
"""


def query_skeleton() -> str:
    """Return the sole CodeQL query skeleton supplied to query synthesis."""
    return r"""Use the skeleton below as the only starting point. Replace every
bracketed placeholder with concrete CodeQL derived from the supplied
vulnerability summary and source evidence. The skeleton is guidance, not a
compilable query and not permission to invent a taint model.

Requirements:
- Identify the untrusted value as Source and the security-sensitive operand as
  Sink using semantic API, type, argument, and data-flow constraints.
- Add Sanitizer/isBarrier only when the evidence proves a guard that blocks the
  same value; otherwise remove both definitions.
- Add isAdditionalFlowStep only for an evidenced propagation step missing from
  the standard library; otherwise remove it.
- Remove unused imports, optional classes, predicates, and branches.
- Do not preserve any bracketed placeholder in the returned query.
- If the evidence cannot support a source-to-sink model, return needs_evidence
  instead of changing to another template or inventing predicates.

```ql
/**
 * @name [Vulnerability name derived from the analysis]
 * @description [Description derived from the vulnerability mechanism]
 * @problem.severity error
 * @security-severity [Numeric security severity]
 * @precision high
 * @tags security
 * @kind path-problem
 * @id autoql/[stable-query-id]
 */
import java
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.TaintTracking

class Source extends DataFlow::Node {
  Source() {
    exists([AST node type derived from evidence] sourceNode |
      [Semantic source constraints] and
      this.asExpr() = [Source expression mapping]
    )
  }
}

class Sink extends DataFlow::Node {
  Sink() {
    exists([AST node type derived from evidence] sinkNode |
      [Semantic sink constraints] and
      this.asExpr() = [Sensitive operand mapping]
    )
  }
}

class Sanitizer extends DataFlow::Node {
  Sanitizer() {
    exists([AST node type for an evidenced sanitizer] sanitizerNode |
      [Semantic sanitizer constraints] and
      this.asExpr() = [Sanitized value mapping]
    )
  }
}

module MyPathConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    source instanceof Source
  }

  predicate isSink(DataFlow::Node sink) {
    sink instanceof Sink
  }

  predicate isBarrier(DataFlow::Node sanitizer) {
    sanitizer instanceof Sanitizer
  }

  predicate isAdditionalFlowStep(DataFlow::Node node1, DataFlow::Node node2) {
    [Evidenced additional propagation step]
  }
}

module MyPathFlow = TaintTracking::Global<MyPathConfig>;
import MyPathFlow::PathGraph

from
  MyPathFlow::PathNode source,
  MyPathFlow::PathNode sink
where
  MyPathFlow::flowPath(source, sink)
select
  sink.getNode(),
  source,
  sink,
  "[Alert message derived from the vulnerability]"
```
"""
