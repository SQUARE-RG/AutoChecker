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
  // Match comparison binary operators (==, !=, <, >, <=, >=)
  // where either operand is a binary operator with lower precedence
  // (bitwise: &, |, ^, <<, >> or arithmetic: +, -, *, /, %)
  // and that inner operator is not wrapped in parentheses.
  auto InnerOpMatcher = binaryOperator(
      anyOf(
          hasAnyOperatorName("&", "|", "^", "<<", ">>"),
          hasAnyOperatorName("+", "-", "*", "/", "%")
      ),
      unless(hasParent(parenExpr()))
  );

  Finder->addMatcher(
      binaryOperator(
          isComparisonOperator(),
          anyOf(
              hasLHS(ignoringImpCasts(InnerOpMatcher.bind("innerOp"))),
              hasRHS(ignoringImpCasts(InnerOpMatcher.bind("innerOp")))
          )
      ).bind("binaryOp"),
      this
  );
}

void MisuseCompareExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *InnerOp = Result.Nodes.getNodeAs<BinaryOperator>("innerOp");

  if (!BinaryOp || !InnerOp)
    return;

  // Get the location of the comparison operator
  SourceLocation OpLoc = BinaryOp->getOperatorLoc();
  if (OpLoc.isInvalid())
    return;

  diag(OpLoc, "禁止比较表达式中的运算项未使用括号")
      << BinaryOp->getSourceRange();
}

} // namespace clang::tidy::ucassaat