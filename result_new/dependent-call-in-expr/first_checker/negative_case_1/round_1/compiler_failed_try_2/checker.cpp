//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/Basic/Diagnostic.h"
#include <set>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to check if two function calls have data dependency
// through pointer arguments
static bool hasDataDependency(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // Collect all pointer arguments from Call1 that point to variables
  std::set<const ValueDecl *> ModifiedVars;
  for (unsigned I = 0; I < Call1->getNumArgs(); ++I) {
    const Expr *Arg = Call1->getArg(I)->IgnoreParenImpCasts();
    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        // Check if the corresponding parameter is non-const pointer
        if (const FunctionDecl *FD = Call1->getDirectCallee()) {
          if (I < FD->getNumParams()) {
            const ParmVarDecl *Param = FD->getParamDecl(I);
            QualType ParamType = Param->getType();
            if (ParamType->isPointerType() && !ParamType.isConstQualified()) {
              ModifiedVars.insert(VD);
            }
          }
        }
      }
    }
  }

  // Check if Call2 accesses any of the modified variables
  for (unsigned I = 0; I < Call2->getNumArgs(); ++I) {
    const Expr *Arg = Call2->getArg(I)->IgnoreParenImpCasts();
    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        if (ModifiedVars.count(VD))
          return true;
      }
    }
  }

  return false;
}

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match binary operators that contain at least two CallExpr nodes
  // We bind the binary operator and use forEachDescendant to find calls
  Finder->addMatcher(
      binaryOperator(
          anyOf(hasOperatorName("+"), hasOperatorName("-"),
                hasOperatorName("*"), hasOperatorName("/"),
                hasOperatorName("%"), hasOperatorName("&"),
                hasOperatorName("|"), hasOperatorName("^"),
                hasOperatorName("&&"), hasOperatorName("||"),
                hasOperatorName("=="), hasOperatorName("!="),
                hasOperatorName("<"), hasOperatorName(">"),
                hasOperatorName("<="), hasOperatorName(">="),
                hasOperatorName("<<"), hasOperatorName(">>")),
          hasDescendant(callExpr().bind("call1")),
          hasDescendant(callExpr().bind("call2")))
          .bind("binaryOp"),
      this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *Call1 = Result.Nodes.getNodeAs<CallExpr>("call1");
  const auto *Call2 = Result.Nodes.getNodeAs<CallExpr>("call2");

  if (!BinaryOp || !Call1 || !Call2)
    return;

  // Ensure we have two distinct function calls
  if (Call1 == Call2)
    return;

  // Get the direct callee functions
  const FunctionDecl *Func1 = Call1->getDirectCallee();
  const FunctionDecl *Func2 = Call2->getDirectCallee();

  if (!Func1 || !Func2)
    return;

  // Check if the two calls have data dependency
  if (hasDataDependency(Call1, Call2) || hasDataDependency(Call2, Call1)) {
    diag(BinaryOp->getExprLoc(),
         "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
  }
}

} // namespace clang::tidy::ucassaat