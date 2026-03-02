//===--- NoElseBranchCheck.cpp - clang-tidy -------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoElseBranchCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoElseBranchCheck::registerMatchers(MatchFinder *Finder) {
  // Match all if statements that have at least one else-if branch
  Finder->addMatcher(
      ifStmt(hasElse(stmt(hasDescendant(ifStmt())))).bind("ifChain"),
      this);
}

void NoElseBranchCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *IfChain = Result.Nodes.getNodeAs<IfStmt>("ifChain");
  if (!IfChain || !IfChain->getBeginLoc().isValid()) {
    return;
  }

  // Traverse the if-else if chain to find the last if statement
  const IfStmt *CurrentIf = IfChain;
  const IfStmt *LastIf = nullptr;

  while (CurrentIf) {
    LastIf = CurrentIf;
    
    // Check if this if statement has an else branch
    const Stmt *ElseBranch = CurrentIf->getElse();
    if (!ElseBranch) {
      // No else branch - this is a violation
      break;
    }
    
    // Check if the else branch is another if statement (else-if)
    if (const auto *ElseIf = dyn_cast<IfStmt>(ElseBranch)) {
      // Continue traversing down the else-if chain
      CurrentIf = ElseIf;
    } else {
      // Found a non-if else branch (could be NullStmt, CompoundStmt, etc.)
      // This is compliant, so return without diagnostic
      return;
    }
  }

  // If we exited the loop because we found an if without an else branch,
  // emit a diagnostic
  if (LastIf && !LastIf->getElse()) {
    diag(LastIf->getElseLoc().isValid() ? LastIf->getElseLoc() 
                                         : LastIf->getEndLoc(),
         "禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]");
  }
}

} // namespace clang::tidy::ucassaat