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
  // Match for loops with assignment initialization
  auto AssignmentInitMatcher = forStmt(
      hasLoopInit(anyOf(
          // Case 1: Binary operator assignment (e.g., i = 0)
          binaryOperator(isAssignmentOperator(),
                         hasLHS(expr(ignoringParenImpCasts(
                             declRefExpr(to(varDecl().bind("lhs_var"))))))),
          // Case 2: DeclStmt with variable declaration (e.g., int i = 0)
          declStmt(hasSingleDecl(varDecl().bind("decl_var")))))).bind("for_loop");

  Finder->addMatcher(AssignmentInitMatcher, this);
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ForLoop = Result.Nodes.getNodeAs<ForStmt>("for_loop");
  if (!ForLoop || !ForLoop->getBeginLoc().isValid()) {
    return;
  }

  // Try to get the variable from either binding
  const VarDecl *LoopVar = nullptr;
  
  if (const auto *LhsVar = Result.Nodes.getNodeAs<VarDecl>("lhs_var")) {
    if (!LhsVar->isInvalidDecl()) {
      LoopVar = LhsVar;
    }
  }
  
  if (!LoopVar) {
    if (const auto *DeclVar = Result.Nodes.getNodeAs<VarDecl>("decl_var")) {
      if (!DeclVar->isInvalidDecl()) {
        LoopVar = DeclVar;
      }
    }
  }

  if (!LoopVar) {
    return;
  }

  // Check if the variable is non-local
  // A variable is considered non-local if:
  // 1. It has global storage (static or extern linkage)
  // 2. Its declaration context is not a function or block
  bool IsNonLocal = false;
  
  // Check storage duration and linkage
  if (LoopVar->hasGlobalStorage()) {
    IsNonLocal = true;
  } else {
    // Check declaration context
    const DeclContext *DC = LoopVar->getDeclContext();
    if (!DC) {
      return;
    }
    
    // Check if context is a function or block
    bool IsInFunction = false;
    bool IsInBlock = false;
    
    while (DC) {
      if (isa<FunctionDecl>(DC)) {
        IsInFunction = true;
        break;
      }
      if (isa<BlockDecl>(DC)) {
        IsInBlock = true;
        break;
      }
      DC = DC->getParent();
    }
    
    // If not in function or block, it's non-local
    if (!IsInFunction && !IsInBlock) {
      IsNonLocal = true;
    }
  }

  if (IsNonLocal) {
    diag(ForLoop->getBeginLoc(), 
         "禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]");
  }
}

} // namespace clang::tidy::ucassaat