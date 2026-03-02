//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallSet.h"
#include "llvm/ADT/SmallVector.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Helper function to collect all CallExpr nodes within an expression
void collectCallExprs(const Expr *E, llvm::SmallVectorImpl<const CallExpr *> &Calls) {
  if (!E) return;
  
  E = E->IgnoreParenImpCasts();
  
  if (const auto *CE = dyn_cast<CallExpr>(E)) {
    Calls.push_back(CE);
    return;
  }
  
  if (const auto *BO = dyn_cast<BinaryOperator>(E)) {
    collectCallExprs(BO->getLHS(), Calls);
    collectCallExprs(BO->getRHS(), Calls);
    return;
  }
  
  if (const auto *UO = dyn_cast<UnaryOperator>(E)) {
    collectCallExprs(UO->getSubExpr(), Calls);
    return;
  }
  
  if (const auto *CE = dyn_cast<ConditionalOperator>(E)) {
    collectCallExprs(CE->getCond(), Calls);
    collectCallExprs(CE->getTrueExpr(), Calls);
    collectCallExprs(CE->getFalseExpr(), Calls);
    return;
  }
  
  if (const auto *CLE = dyn_cast<CompoundLiteralExpr>(E)) {
    collectCallExprs(CLE->getInitializer(), Calls);
    return;
  }
  
  if (const auto *IE = dyn_cast<InitListExpr>(E)) {
    for (unsigned i = 0; i < IE->getNumInits(); ++i) {
      collectCallExprs(IE->getInit(i), Calls);
    }
    return;
  }
}

// Helper function to check if two expressions refer to the same memory location
bool refersToSameLocation(const Expr *E1, const Expr *E2, ASTContext &Context) {
  if (!E1 || !E2) return false;
  
  E1 = E1->IgnoreParenImpCasts();
  E2 = E2->IgnoreParenImpCasts();
  
  // Handle address-of operator
  if (const auto *UO1 = dyn_cast<UnaryOperator>(E1)) {
    if (UO1->getOpcode() == UO_AddrOf) {
      E1 = UO1->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  if (const auto *UO2 = dyn_cast<UnaryOperator>(E2)) {
    if (UO2->getOpcode() == UO_AddrOf) {
      E2 = UO2->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  // Check if both are DeclRefExpr to the same variable
  if (const auto *DRE1 = dyn_cast<DeclRefExpr>(E1)) {
    if (const auto *DRE2 = dyn_cast<DeclRefExpr>(E2)) {
      return DRE1->getDecl() == DRE2->getDecl();
    }
  }
  
  // Check if both are MemberExpr accessing the same member
  if (const auto *ME1 = dyn_cast<MemberExpr>(E1)) {
    if (const auto *ME2 = dyn_cast<MemberExpr>(E2)) {
      return ME1->getMemberDecl() == ME2->getMemberDecl() &&
             refersToSameLocation(ME1->getBase(), ME2->getBase(), Context);
    }
  }
  
  // For array subscript, check if base and index are the same
  if (const auto *ASE1 = dyn_cast<ArraySubscriptExpr>(E1)) {
    if (const auto *ASE2 = dyn_cast<ArraySubscriptExpr>(E2)) {
      return refersToSameLocation(ASE1->getBase(), ASE2->getBase(), Context) &&
             refersToSameLocation(ASE1->getIdx(), ASE2->getIdx(), Context);
    }
  }
  
  return false;
}

// Check if a parameter type could introduce data dependency
bool isDependencyType(QualType Type) {
  Type = Type.getNonReferenceType();
  
  // Pointer to non-const type
  if (const auto *PtrType = Type->getAs<PointerType>()) {
    return !PtrType->getPointeeType().isConstQualified();
  }
  
  // Reference to non-const type
  if (Type->isReferenceType()) {
    return !Type.getNonReferenceType().isConstQualified();
  }
  
  return false;
}

// Check if two function calls have overlapping dependency arguments
bool haveDependencyOverlap(const CallExpr *Call1, const CallExpr *Call2, 
                          ASTContext &Context) {
  const FunctionDecl *Func1 = Call1->getDirectCallee();
  const FunctionDecl *Func2 = Call2->getDirectCallee();
  
  if (!Func1 || !Func2) return false;
  
  // Check each parameter combination
  for (unsigned i = 0; i < Call1->getNumArgs() && i < Func1->getNumParams(); ++i) {
    QualType ParamType1 = Func1->getParamDecl(i)->getType();
    if (!isDependencyType(ParamType1)) continue;
    
    const Expr *Arg1 = Call1->getArg(i);
    
    for (unsigned j = 0; j < Call2->getNumArgs() && j < Func2->getNumParams(); ++j) {
      QualType ParamType2 = Func2->getParamDecl(j)->getType();
      if (!isDependencyType(ParamType2)) continue;
      
      const Expr *Arg2 = Call2->getArg(j);
      
      if (refersToSameLocation(Arg1, Arg2, Context)) {
        return true;
      }
    }
  }
  
  return false;
}

} // namespace

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match top-level expressions that could contain multiple function calls
  auto TopLevelExpr = expr(anyOf(
    binaryOperator(unless(hasOperatorName(","))).bind("binaryOp"),
    conditionalOperator().bind("condOp")
  )).bind("topLevelExpr");
  
  Finder->addMatcher(TopLevelExpr, this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *TopLevel = Result.Nodes.getNodeAs<Expr>("topLevelExpr");
  if (!TopLevel || TopLevel->getBeginLoc().isInvalid()) return;
  
  // Collect all CallExprs within this top-level expression
  llvm::SmallVector<const CallExpr *, 4> Calls;
  collectCallExprs(TopLevel, Calls);
  
  // Need at least 2 calls to have a potential violation
  if (Calls.size() < 2) return;
  
  // Check each pair of calls for dependency overlap
  for (unsigned i = 0; i < Calls.size(); ++i) {
    for (unsigned j = i + 1; j < Calls.size(); ++j) {
      if (haveDependencyOverlap(Calls[i], Calls[j], *Result.Context)) {
        diag(TopLevel->getBeginLoc(), 
             "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
        return; // Report only once per expression
      }
    }
  }
}

} // namespace clang::tidy::ucassaat