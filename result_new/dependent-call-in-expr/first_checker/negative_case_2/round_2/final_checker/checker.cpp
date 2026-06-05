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
  // Use forEachDescendant to capture multiple calls within the same binary expression
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
          // Use forEachDescendant to find all call expressions within the binary operator
          forEachDescendant(callExpr().bind("call")))
          .bind("binaryOp"),
      this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("call");

  if (!BinaryOp || !Call)
    return;

  // We need to collect all call expressions within this binary operator
  // Since the matcher triggers for each call expression separately,
  // we need to collect all calls and check pairs
  
  // Use a static set to track processed binary operators to avoid duplicate reports
  static std::set<const BinaryOperator*> ProcessedOps;
  if (ProcessedOps.count(BinaryOp))
    return;
  
  // Collect all call expressions within this binary operator
  std::vector<const CallExpr*> Calls;
  // Traverse the binary operator's children to find all call expressions
  std::function<void(const Stmt*)> collectCalls = [&](const Stmt* S) {
    if (!S) return;
    if (const auto* CE = dyn_cast<CallExpr>(S)) {
      // Make sure this call is a direct child of the binary operator
      // (not nested inside another call)
      bool isDirectChild = false;
      for (const Stmt* Child : BinaryOp->children()) {
        if (Child == S) {
          isDirectChild = true;
          break;
        }
        // Check if the child is an implicit cast wrapping the call
        if (const auto* ICE = dyn_cast<ImplicitCastExpr>(Child)) {
          if (ICE->getSubExpr() == S) {
            isDirectChild = true;
            break;
          }
        }
      }
      if (isDirectChild) {
        Calls.push_back(CE);
      }
    }
    for (const Stmt* Child : S->children()) {
      collectCalls(Child);
    }
  };
  collectCalls(BinaryOp);
  
  // Mark this binary operator as processed
  ProcessedOps.insert(BinaryOp);
  
  // Need at least two calls to have a dependency
  if (Calls.size() < 2)
    return;
  
  // Check all pairs of calls for data dependency
  for (size_t i = 0; i < Calls.size(); ++i) {
    for (size_t j = i + 1; j < Calls.size(); ++j) {
      if (hasDataDependency(Calls[i], Calls[j]) || 
          hasDataDependency(Calls[j], Calls[i])) {
        diag(BinaryOp->getExprLoc(),
             "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
        return; // Report only once per binary operator
      }
    }
  }
}

} // namespace clang::tidy::ucassaat