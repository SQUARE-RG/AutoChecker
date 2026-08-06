/**
 * @name Empty if statement block
 * @description Detects if statements that have an empty then branch and no else branch, which are usually redundant.
 * @id cpp/redundant-if-stmt
 * @kind problem
 * @tags correctness
 * @problem.severity warning
 */
import cpp  // Import C++ standard library

from IfStmt ifstmt, BlockStmt block
where
  ifstmt.getThen() = block and      // The block is the then branch of the if statement
  block.getNumStmt() = 0 and        // The then branch is empty
  not ifstmt.hasElse()              // Exclude cases with an else branch to reduce false positives[6](@ref)
select ifstmt, "This 'if' statement is redundant as it has an empty then branch and no else."