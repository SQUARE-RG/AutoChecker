//===--- NoAssignmentInConditionCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoAssignmentInConditionCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoAssignmentInConditionCheck::registerMatchers(MatchFinder *Finder) {
  // Match assignment operators that are used as subexpressions of conditions
  // in if, while, for, do statements, or inside logical operators (&&, ||)
  // that are part of such conditions.
  auto AssignmentOp = binaryOperator(
      isAssignmentOp(),
      hasAncestor(stmt(anyOf(
          ifStmt(hasCondition(expr().bind("cond"))),
          whileStmt(hasCondition(expr().bind("cond"))),
          forStmt(hasCondition(expr().bind("cond"))),
          doStmt(hasCondition(expr().bind("cond"))),
          binaryOperator(
              anyOf(hasOperatorName("&&"), hasOperatorName("||")),
              hasAncestor(stmt(anyOf(
                  ifStmt(hasCondition(expr().bind("cond"))),
                  whileStmt(hasCondition(expr().bind("cond"))),
                  forStmt(hasCondition(expr().bind("cond"))),
                  doStmt(hasCondition(expr().bind("cond")))))))
      ))).bind("assignment"));

  Finder->addMatcher(AssignmentOp, this);
}

void NoAssignmentInConditionCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Assignment = Result.Nodes.getNodeAs<BinaryOperator>("assignment");
  if (!Assignment)
    return;

  // Ensure the assignment is not part of a declaration initializer.
  // Check that the assignment's parent is not a DeclStmt.
  const auto *Parent = Result.Context->getParents(*Assignment).begin();
  if (Parent) {
    if (const auto *DeclStmtParent = Parent->get<DeclStmt>()) {
      (void)DeclStmtParent;
      return;
    }
  }

  diag(Assignment->getOperatorLoc(), "禁止将赋值语句作为逻辑表达式");
}

} // namespace clang::tidy::ucassaat