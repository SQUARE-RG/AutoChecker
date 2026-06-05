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
  // Match binary assignment operators where:
  // - LHS is an integer variable
  // - RHS after stripping implicit casts and parens is a floating-point variable reference (DeclRefExpr)
  // - Explicitly exclude constant floating-point values by requiring RHS to be a DeclRefExpr
  Finder->addMatcher(
      binaryOperator(
          isAssignmentOperator(),
          hasLHS(declRefExpr(to(varDecl(hasType(isInteger()))))),
          hasRHS(ignoringParenImpCasts(
              declRefExpr(to(varDecl(hasType(realFloatingPointType()))))
                  .bind("rhs")
          ))
      ).bind("assign"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Assign = Result.Nodes.getNodeAs<BinaryOperator>("assign");
  const auto *RHS = Result.Nodes.getNodeAs<DeclRefExpr>("rhs");

  if (!Assign || !RHS)
    return;

  // Check that the RHS is a variable reference (DeclRefExpr) to a floating-point variable
  // and not a constant expression
  const ValueDecl *RHSDecl = RHS->getDecl();
  if (!RHSDecl || !isa<VarDecl>(RHSDecl))
    return;

  // Verify that the RHS variable is of floating-point type
  QualType RHSType = RHSDecl->getType();
  if (!RHSType->isRealFloatingType())
    return;

  // Check that there is no explicit cast wrapping the floating-point variable
  // The matcher already uses ignoringParenImpCasts, which strips implicit casts and parens
  // but preserves explicit casts. If the RHS matches, it means no explicit cast was present.
  // We also need to verify the parent of the RHS in the AST to ensure no explicit cast
  // is applied directly to the DeclRefExpr.
  bool HasExplicitCast = false;
  const Stmt *Parent = RHS;
  ASTContext &Context = *Result.Context;
  while (true) {
    auto Parents = Context.getParents(*Parent);
    if (Parents.empty())
      break;
    const Stmt *ParentStmt = Parents[0].get<Stmt>();
    if (!ParentStmt)
      break;
    // If we encounter an explicit cast, the assignment is compliant
    if (isa<ExplicitCastExpr>(ParentStmt)) {
      HasExplicitCast = true;
      break;
    }
    // Stop if we reach the assignment operator
    if (ParentStmt == Assign)
      break;
    Parent = ParentStmt;
  }

  if (HasExplicitCast)
    return;

  // Emit diagnostic message for violation
  diag(Assign->getBeginLoc(), "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
}

} // namespace clang::tidy::ucassaat