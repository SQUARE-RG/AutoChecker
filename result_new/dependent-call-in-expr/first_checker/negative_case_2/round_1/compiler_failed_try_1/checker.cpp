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

// Helper function to collect all variables that are passed by non-const pointer
// or array to a function call
static void collectModifiedVars(const CallExpr *Call, 
                                std::set<const ValueDecl *> &ModifiedVars) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  for (unsigned I = 0; I < Call->getNumArgs() && I < FD->getNumParams(); ++I) {
    const ParmVarDecl *Param = FD->getParamDecl(I);
    QualType ParamType = Param->getType();
    
    // Check if parameter is non-const pointer or array type
    bool IsNonConstPointer = false;
    if (ParamType->isPointerType()) {
      // For pointer types, check the pointee type's const qualification
      IsNonConstPointer = !ParamType->getPointeeType().isConstQualified();
    } else if (ParamType->isArrayType()) {
      // Array parameters decay to pointers, check the element type
      const ArrayType *ArrType = ParamType->getAsArrayTypeUnsafe();
      if (ArrType) {
        IsNonConstPointer = !ArrType->getElementType().isConstQualified();
      }
    }

    if (!IsNonConstPointer)
      continue;

    const Expr *Arg = Call->getArg(I)->IgnoreParenImpCasts();
    
    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        ModifiedVars.insert(VD);
      }
    }
  }
}

// Helper function to check if two function calls have data dependency
// through pointer/array arguments
static bool hasDataDependency(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // Collect all variables that are potentially modified by Call1
  std::set<const ValueDecl *> ModifiedVars;
  collectModifiedVars(Call1, ModifiedVars);

  if (ModifiedVars.empty())
    return false;

  // Check if Call2 accesses any of the modified variables
  const FunctionDecl *FD2 = Call2->getDirectCallee();
  if (!FD2)
    return false;

  for (unsigned I = 0; I < Call2->getNumArgs(); ++I) {
    const Expr *Arg = Call2->getArg(I)->IgnoreParenImpCasts();
    
    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call2->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

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