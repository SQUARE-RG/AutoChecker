/**
 * @name Sample query
 * @description Sample CodeQL query for Python analysis.
 * @id python/sample-query
 * @kind problem
 * @tags correctness
 * @problem.severity warning
 */
import python

from Function f, Call c
where
  c.getFunc() = f and
  f.getName() = "eval"
select c, "This call to '" + f.getName() + "' may be unsafe."
