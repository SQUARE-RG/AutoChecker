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
          hasLHS(expr(hasType(isInteger())).bind("lhs")),
          hasRHS(expr(
              hasType(realFloatingPointType()),
              // Exclude floating literals (direct constant assignments)
              unless(ignoringParenImpCasts(floatLiteral())),
              // Exclude integer literals (though they have floating type context)
              unless(ignoringParenImpCasts(integerLiteral())),
              // Exclude explicit casts to integer type
              unless(hasDescendant(explicitCastExpr(hasDestinationType(isInteger())))),
              // Exclude implicit casts that are not from floating to integer
              unless(hasParent(implicitCastExpr(hasImplicitDestinationType(isInteger()))))
          ).bind("rhs"))
      ).bind("assignOp"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp");
  const auto *LHS = Result.Nodes.getNodeAs<Expr>("lhs");
  const auto *RHS = Result.Nodes.getNodeAs<Expr>("rhs");
  
  if (!AssignOp || !AssignOp->getOperatorLoc().isValid() ||
      !LHS || !LHS->getExprLoc().isValid() ||
      !RHS || !RHS->getExprLoc().isValid()) {
    return;
  }
  
  // Verify LHS is integer type
  if (!LHS->getType()->isIntegerType()) {
    return;
  }
  
  // Verify RHS is floating type
  if (!RHS->getType()->isFloatingType()) {
    return;
  }
  
  // Check if RHS is a constant expression (exempt per rule)
  // We already excluded literals in matcher, but check for other constant expressions
  Expr::EvalResult EvalResult;
  if (RHS->isValueDependent() || RHS->isTypeDependent()) {
    return;
  }
  
  // Check if RHS evaluates to a constant (excluding literals)
  if (RHS->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    // Allow constant expressions as per rule description
    return;
  }
  
  // Check for explicit cast in the RHS expression tree
  // Look for explicit cast to integer type in the RHS
  bool HasExplicitCast = false;
  auto CheckForExplicitCast = [&](const Expr *E) {
    if (const auto *CE = dyn_cast<ExplicitCastExpr>(E)) {
      if (CE->getTypeAsWritten()->isIntegerType()) {
        HasExplicitCast = true;
      }
    }
  };
  
  // Traverse the RHS expression to check for explicit casts
  std::function<void(const Expr*)> TraverseExpr = [&](const Expr *E) {
    if (!E || HasExplicitCast) return;
    
    CheckForExplicitCast(E);
    
    // Check children
    for (const Stmt *Child : E->children()) {
      if (const Expr *ChildExpr = dyn_cast_or_null<Expr>(Child)) {
        TraverseExpr(ChildExpr);
      }
    }
  };
  
  TraverseExpr(RHS);
  
  if (HasExplicitCast) {
    return;
  }
  
  // Emit diagnostic with source ranges
  auto Diag = diag(AssignOp->getOperatorLoc(), 
                   "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
  
  // Add source ranges for LHS and RHS
  Diag << SourceRange(LHS->getBeginLoc(), LHS->getEndLoc())
       << SourceRange(RHS->getBeginLoc(), RHS->getEndLoc());
}

} // namespace clang::tidy::ucassaat