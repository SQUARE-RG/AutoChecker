//===--- ProhibitNonLocalVariableInForLoopCheck.cpp - clang-tidy ----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitNonLocalVariableInForLoopCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitNonLocalVariableInForLoopCheck::registerMatchers(MatchFinder *Finder) {
  // Match for statements that:
  // 1. Have an init part that is an assignment (binaryOperator) where LHS is a DeclRefExpr
  // 2. Have a condition and increment part
  // 3. Exclude for loops where init is a declaration statement (local variable)
  Finder->addMatcher(
      forStmt(
          unless(hasLoopInit(declStmt())),
          hasLoopInit(
              binaryOperator(
                  isAssignmentOperator(),
                  hasLHS(ignoringParenImpCasts(
                      declRefExpr(to(varDecl().bind("loopVar"))).bind("loopVarRef")
                  ))
              )
          ),
          hasCondition(anything()),
          hasIncrement(anything())
      ).bind("forLoop"),
      this
  );
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ForLoop = Result.Nodes.getNodeAs<ForStmt>("forLoop");
  const auto *LoopVarRef = Result.Nodes.getNodeAs<DeclRefExpr>("loopVarRef");
  const auto *LoopVar = Result.Nodes.getNodeAs<VarDecl>("loopVar");

  if (!ForLoop || !LoopVarRef || !LoopVar)
    return;

  // Check if the variable is non-local:
  // - hasGlobalStorage() covers global variables, static global variables
  // - isFileVarDecl() covers variables with file scope (external linkage)
  // - hasExternalStorage() covers variables declared with 'extern'
  if (LoopVar->hasGlobalStorage() || LoopVar->isFileVarDecl() || LoopVar->hasExternalStorage()) {
    // Skip static local variables (they have local scope but static storage)
    if (!LoopVar->isLocalVarDecl() || LoopVar->isStaticLocal()) {
      diag(ForLoop->getForLoc(), "禁止 for 循环控制变量使用非局部变量");
    }
  }
}

} // namespace clang::tidy::ucassaat