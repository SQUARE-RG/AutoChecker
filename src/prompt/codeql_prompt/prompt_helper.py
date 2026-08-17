def query_skeleton() -> str:
    """Return the standard CodeQL query template skeleton."""
    return """```ql
/**
 * @name [Vulnerability Name based on analysis]
 * @description [Description derived from the vulnerability pattern]
 * @problem.severity error
 * @security-severity [score based on severity]
 * @precision high
 * @tags security
 * @kind path-problem
 * @id [unique-id]
 */
import java
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.TaintTracking


class Source extends DataFlow::Node {
  Source() {
    exists([AST node type from analysis] |
      /* Fill based on AST patterns for sources identified in Phase 1 & 2 */
      and this.asExpr() = [appropriate mapping]
    )
  }
}

class Sink extends DataFlow::Node {
  Sink() {
    exists([AST node type] |
      /* Fill based on AST patterns for sinks */
      and this.asExpr() = [appropriate mapping]
    ) or
    exists([Alternative AST pattern] |
      /* Additional sink patterns from analysis */
      and [appropriate condition]
    )
  }
}

class Sanitizer extends DataFlow::Node {
  Sanitizer() {
    exists([AST node type for sanitizers] |
      /* Fill based on sanitizer patterns from Phase 1 & 2 */
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

  predicate isAdditionalFlowStep(DataFlow::Node n1, DataFlow::Node n2) {
    /* Fill based on additional taint steps from analysis */
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
  "[Alert message based on vulnerability]",
  source.getNode(),
  "[source description]"
```"""