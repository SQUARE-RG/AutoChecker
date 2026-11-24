"""Single Java CodeQL generation skeleton used by the Query Agent.

The Analysis V2 contract deliberately does not select an ``analysis_kind`` or
produce a separate query model. Query synthesis always starts from this one
skeleton and derives its concrete source, sink, barrier, and flow predicates
from ``vulnerability_summary`` and the program-materialized evidence.
"""


def query_skeleton() -> str:
    """Return the sole CodeQL query skeleton supplied to query synthesis."""
    return r"""Use the skeleton below as a general starting point.

Choose the simplest CodeQL modeling strategy that matches the evidenced vulnerability mechanism. Use AST structure, API semantics, types, values, control flow, data flow, or taint tracking only when needed.

```query
/**
 * @name [Name derived from the vulnerability mechanism]
 * @description [Description of the detected vulnerable behavior]
 * @problem.severity error
 * @precision high
 * @tags security
 * @kind [problem or path-problem]
 * @id autoql/[query-id]
 */

import java

// Add only the CodeQL libraries required by the chosen analysis.
// Examples:
// import semmle.code.java.dataflow.DataFlow
// import semmle.code.java.dataflow.TaintTracking


// Define the program elements and semantic relationships that
// characterize the vulnerable behavior.
//
// These may model, for example:
// - AST or API usage
// - types, arguments, receivers, fields, annotations, or constants
// - missing or incorrect conditions
// - control-flow or state relationships
// - data-flow or taint-flow sources, sinks, and propagation
//
// Add only what the vulnerability mechanism requires.

[Relevant classes and predicates]


// Optional data-flow or taint-tracking configuration.
// Include this section only when propagation between values is
// essential to detecting the vulnerability.

[Optional DataFlow/TaintTracking configuration]


// Select the program element that represents the detected vulnerability.

from
  [Relevant query variables]
where
  [Semantic conditions defining the vulnerable behavior]
select
  [Result entity and message, or path-problem result columns]
```

For `@kind problem`, return the detected entity followed by its alert message.
For `@kind path-problem`, use an appropriate path query configuration and return the required source, sink, and message columns.

"""
