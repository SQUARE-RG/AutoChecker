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
          hasLHS(expr(hasType(isInteger())).bind("lhsExpr")),
          hasRHS(expr(
              anyOf(
                  // Match floating type expressions
                  expr(hasType(realFloatingPointType())),
                  // Also match expressions that after ignoring implicit casts
                  // have floating type (to catch implicit conversions)
                  ignoringParenImpCasts(expr(hasType(realFloatingPointType())))
              )
          ).bind("rhsExpr")),
          // Exclude cases where RHS has explicit cast to integer
          unless(hasRHS(expr(anyOf(
              cStyleCastExpr(hasDestinationType(isInteger())),
              cxxStaticCastExpr(hasDestinationType(isInteger())),
              cxxFunctionalCastExpr(hasDestinationType(isInteger()))
          )))),
          // Exclude constant expressions (literals)
          unless(hasRHS(ignoringParenImpCasts(
              expr(anyOf(
                  floatLiteral(),
                  integerLiteral()
              ))
          )))
      ).bind("assignOp"),
      this);

  // Match variable declarations with initializers where the variable is integer type
  // and the initializer is floating type (to catch initialization cases)
  Finder->addMatcher(
      varDecl(
          hasType(isInteger()),
          hasInitializer(expr(
              anyOf(
                  expr(hasType(realFloatingPointType())).bind("initExpr"),
                  ignoringParenImpCasts(expr(hasType(realFloatingPointType())).bind("initExpr"))
              )
          )),
          // Exclude cases where initializer has explicit cast to integer
          unless(hasInitializer(expr(anyOf(
              cStyleCastExpr(hasDestinationType(isInteger())),
              cxxStaticCastExpr(hasDestinationType(isInteger())),
              cxxFunctionalCastExpr(hasDestinationType(isInteger()))
          )))),
          // Exclude constant expressions (literals)
          unless(hasInitializer(ignoringParenImpCasts(
              expr(anyOf(
                  floatLiteral(),
                  integerLiteral()
              ))
          )))
      ).bind("varDecl"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  // Handle assignment operator cases
  if (const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp")) {
    const auto *LHSExpr = Result.Nodes.getNodeAs<Expr>("lhsExpr");
    const auto *RHSExpr = Result.Nodes.getNodeAs<Expr>("rhsExpr");
    
    if (!AssignOp || !AssignOp->getOperatorLoc().isValid()) {
      return;
    }
    
    if (!LHSExpr || !LHSExpr->getExprLoc().isValid() ||
        !RHSExpr || !RHSExpr->getExprLoc().isValid()) {
      return;
    }
    
    // Verify LHS is integer type
    if (!LHSExpr->getType()->isIntegerType()) {
      return;
    }
    
    // Strip implicit casts and parentheses from RHS to get the core expression
    const Expr *StrippedRHS = RHSExpr->IgnoreParenImpCasts();
    if (!StrippedRHS) {
      return;
    }
    
    // Verify RHS is floating type (after stripping implicit casts)
    if (!StrippedRHS->getType()->isFloatingType()) {
      return;
    }
    
    // Check if RHS is value-dependent or type-dependent
    if (RHSExpr->isValueDependent() || RHSExpr->isTypeDependent()) {
      return;
    }
    
    // Check if RHS is a constant expression (exempt per rule)
    // First check if it's a literal (already excluded in matcher, but double-check)
    if (isa<FloatingLiteral>(StrippedRHS) || isa<IntegerLiteral>(StrippedRHS)) {
      return;
    }
    
    // Check if it evaluates to a constant (including const variables)
    Expr::EvalResult EvalResult;
    if (RHSExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
      return;
    }
    
    // Also check the stripped version
    if (StrippedRHS->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
      return;
    }
    
    // Check if RHS is a DeclRefExpr to a const variable with constant initializer
    if (const auto *DRE = dyn_cast<DeclRefExpr>(StrippedRHS)) {
      if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
        if (VD->getType().isConstQualified()) {
          if (const Expr *Init = VD->getInit()) {
            if (Init->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
              return;
            }
          }
        }
      }
    }
    
    // Check for member expressions (like d.value in the failed test case)
    if (const auto *ME = dyn_cast<MemberExpr>(StrippedRHS)) {
      // Check if the member expression refers to a const member
      if (const auto *FD = dyn_cast<FieldDecl>(ME->getMemberDecl())) {
        if (FD->getType().isConstQualified()) {
          // For const member access, we need to check if the entire expression
          // evaluates to a constant
          if (RHSExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
            return;
          }
        }
      }
    }
    
    // Emit diagnostic
    auto Diag = diag(AssignOp->getOperatorLoc(), 
                     "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
    
    // Add source ranges for better context
    Diag << SourceRange(LHSExpr->getBeginLoc(), LHSExpr->getEndLoc())
         << SourceRange(RHSExpr->getBeginLoc(), RHSExpr->getEndLoc());
  }
  
  // Handle variable declaration with initializer cases
  if (const auto *VarD = Result.Nodes.getNodeAs<VarDecl>("varDecl")) {
    const auto *InitExpr = Result.Nodes.getNodeAs<Expr>("initExpr");
    
    if (!VarD || !VarD->getLocation().isValid()) {
      return;
    }
    
    if (!InitExpr || !InitExpr->getExprLoc().isValid()) {
      return;
    }
    
    // Verify variable is integer type
    if (!VarD->getType()->isIntegerType()) {
      return;
    }
    
    // Strip implicit casts and parentheses from initializer to get the core expression
    const Expr *StrippedInit = InitExpr->IgnoreParenImpCasts();
    if (!StrippedInit) {
      return;
    }
    
    // Verify initializer is floating type (after stripping implicit casts)
    if (!StrippedInit->getType()->isFloatingType()) {
      return;
    }
    
    // Check if initializer is value-dependent or type-dependent
    if (InitExpr->isValueDependent() || InitExpr->isTypeDependent()) {
      return;
    }
    
    // Check if initializer is a literal (already excluded in matcher, but double-check)
    if (isa<FloatingLiteral>(StrippedInit) || isa<IntegerLiteral>(StrippedInit)) {
      return;
    }
    
    // Check if it evaluates to a constant (including const variables)
    Expr::EvalResult EvalResult;
    if (InitExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
      return;
    }
    
    // Also check the stripped version
    if (StrippedInit->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
      return;
    }
    
    // Check if initializer is a DeclRefExpr to a const variable with constant initializer
    if (const auto *DRE = dyn_cast<DeclRefExpr>(StrippedInit)) {
      if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
        if (VD->getType().isConstQualified()) {
          if (const Expr *Init = VD->getInit()) {
            if (Init->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
              return;
            }
          }
        }
      }
    }
    
    // Check for member expressions
    if (const auto *ME = dyn_cast<MemberExpr>(StrippedInit)) {
      // Check if the member expression refers to a const member
      if (const auto *FD = dyn_cast<FieldDecl>(ME->getMemberDecl())) {
        if (FD->getType().isConstQualified()) {
          // For const member access, we need to check if the entire expression
          // evaluates to a constant
          if (InitExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
            return;
          }
        }
      }
    }
    
    // Emit diagnostic at the variable declaration location
    auto Diag = diag(VarD->getLocation(), 
                     "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
    
    // Add source ranges for better context
    Diag << SourceRange(VarD->getBeginLoc(), VarD->getEndLoc())
         << SourceRange(InitExpr->getBeginLoc(), InitExpr->getEndLoc());
  }
}

} // namespace clang::tidy::ucassaat