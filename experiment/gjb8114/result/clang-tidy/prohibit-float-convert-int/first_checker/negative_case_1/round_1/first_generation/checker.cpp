//===--- ProhibitFloatConvertIntCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitFloatConvertIntCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitFloatConvertIntCheck::registerMatchers(MatchFinder *Finder) {
  // Match assignment operators where LHS is integer type and RHS is floating type
  auto LHSMatcher = expr(hasType(isIntegerType())).bind("lhs");
  auto RHSMatcher = expr(hasType(realFloatingPointType()),
                         unless(hasDescendant(explicitCastExpr())),
                         unless(integerConstant()),
                         unless(floatConstant())).bind("rhs");
  
  Finder->addMatcher(
      binaryOperator(
          isAssignmentOperator(),
          hasLHS(LHSMatcher),
          hasRHS(RHSMatcher)
      ).bind("assignOp"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp");
  const auto *LHS = Result.Nodes.getNodeAs<Expr>("lhs");
  const auto *RHS = Result.Nodes.getNodeAs<Expr>("rhs");
  
  if (!AssignOp || !AssignOp->isValid() || 
      !LHS || !LHS->isValid() || 
      !RHS || !RHS->isValid()) {
    return;
  }
  
  // Verify types
  if (!LHS->getType()->isIntegerType() || !RHS->getType()->isFloatingType()) {
    return;
  }
  
  // Check if RHS is a constant expression (exempt per rule)
  Expr::EvalResult EvalResult;
  if (RHS->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    return;
  }
  
  // Emit diagnostic
  diag(AssignOp->getOperatorLoc(), 
       "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
}

} // namespace clang::tidy::ucassaat