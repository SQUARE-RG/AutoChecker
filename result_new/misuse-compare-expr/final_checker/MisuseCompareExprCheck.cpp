//===--- MisuseCompareExprCheck.cpp - clang-tidy --------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "MisuseCompareExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void MisuseCompareExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match comparison operators that are not wrapped in parentheses
  auto InnerComparisonMatcher = binaryOperator(
      isComparisonOperator(),
      unless(hasParent(parenExpr()))
  );

  // Match when comparison operator is an operand of a non-comparison binary operator
  // (arithmetic or bitwise operators) without parentheses
  auto OuterOpMatcher = binaryOperator(
      anyOf(
          hasAnyOperatorName("&", "|", "^", "<<", ">>"),
          hasAnyOperatorName("+", "-", "*", "/", "%")
      ),
      hasEitherOperand(ignoringImpCasts(InnerComparisonMatcher))
  );

  // Match comparison operators directly inside conditional operator or return statement
  auto ConditionalOrReturnMatcher = binaryOperator(
      isComparisonOperator(),
      unless(hasParent(parenExpr())),
      anyOf(
          hasParent(conditionalOperator()),
          hasParent(returnStmt())
      )
  );

  // Match comparison operators that are arguments of function calls without parentheses
  auto CallArgMatcher = binaryOperator(
      isComparisonOperator(),
      unless(hasParent(parenExpr())),
      hasAncestor(callExpr())
  );

  // Combine all matchers to avoid duplicate bindings
  Finder->addMatcher(
      stmt(anyOf(
          OuterOpMatcher.bind("binaryOp"),
          ConditionalOrReturnMatcher,
          CallArgMatcher
      )).bind("innerOp"),
      this
  );
}

void MisuseCompareExprCheck::check(const ast_matchers::MatchFinder::MatchResult &Result) {
  const auto *InnerOp = Result.Nodes.getNodeAs<BinaryOperator>("innerOp");

  if (!InnerOp)
    return;

  SourceLocation OpLoc = InnerOp->getOperatorLoc();
  if (OpLoc.isInvalid())
    return;

  diag(OpLoc, "禁止比较表达式中的运算项未使用括号")
      << InnerOp->getSourceRange();
}

} // namespace clang::tidy::ucassaat