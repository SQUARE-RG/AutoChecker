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
#include "clang/AST/Expr.h"
#include "clang/AST/Type.h"
#include "clang/AST/OperationKinds.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitFloatConvertIntCheck::registerMatchers(MatchFinder *Finder) {
  // Match assignment operators where LHS is integer type and RHS is floating type
  // Exclude cases where RHS is a constant literal or has explicit cast to integer
  Finder->addMatcher(
      binaryOperator(
          isAssignmentOperator(),
          hasLHS(ignoringParenImpCasts(
              declRefExpr(
                  to(varDecl(hasType(isInteger())).bind("lhsVar"))
              ).bind("lhsRef")
          )),
          hasRHS(ignoringParenImpCasts(
              declRefExpr(
                  to(varDecl(hasType(realFloatingPointType())).bind("rhsVar"))
              ).bind("rhsRef")
          )),
          // Exclude cases where RHS has explicit cast
          unless(hasRHS(expr(anyOf(
              cStyleCastExpr(hasDestinationType(isInteger())),
              cxxStaticCastExpr(hasDestinationType(isInteger())),
              cxxFunctionalCastExpr(hasDestinationType(isInteger()))
          )))),
          // Exclude constant expressions
          unless(hasRHS(ignoringParenImpCasts(
              expr(anyOf(
                  floatLiteral(),
                  integerLiteral()
              ))
          )))
      ).bind("assignOp"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp");
  const auto *LHSRef = Result.Nodes.getNodeAs<DeclRefExpr>("lhsRef");
  const auto *RHSRef = Result.Nodes.getNodeAs<DeclRefExpr>("rhsRef");
  const auto *LHSVar = Result.Nodes.getNodeAs<VarDecl>("lhsVar");
  const auto *RHSVar = Result.Nodes.getNodeAs<VarDecl>("rhsVar");
  
  if (!AssignOp || !AssignOp->getOperatorLoc().isValid()) {
    return;
  }
  
  if (!LHSRef || !LHSRef->getExprLoc().isValid() ||
      !RHSRef || !RHSRef->getExprLoc().isValid()) {
    return;
  }
  
  if (!LHSVar || !RHSVar) {
    return;
  }
  
  // Verify LHS is integer type
  if (!LHSVar->getType()->isIntegerType()) {
    return;
  }
  
  // Verify RHS is floating type
  if (!RHSVar->getType()->isFloatingType()) {
    return;
  }
  
  // Check if RHS is a constant expression (exempt per rule)
  Expr::EvalResult EvalResult;
  if (RHSRef->isValueDependent() || RHSRef->isTypeDependent()) {
    return;
  }
  
  // Check if RHS evaluates to a constant
  if (RHSRef->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    return;
  }
  
  // Emit diagnostic
  auto Diag = diag(AssignOp->getOperatorLoc(), 
                   "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
  
  // Add source ranges for better context
  Diag << SourceRange(LHSRef->getBeginLoc(), LHSRef->getEndLoc())
       << SourceRange(RHSRef->getBeginLoc(), RHSRef->getEndLoc());
}

} // namespace clang::tidy::ucassaat