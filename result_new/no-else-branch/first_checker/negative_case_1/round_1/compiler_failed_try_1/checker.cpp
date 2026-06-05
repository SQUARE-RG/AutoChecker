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
  // Match if statements that have an else if branch (else is also an if statement)
  // and the innermost else if lacks an else branch.
  // We use a recursive matcher to find the last if in the else-if chain.
  Finder->addMatcher(
      ifStmt(
          hasElse(
              ifStmt().bind("elseIf")
          ),
          // Ensure we match the outermost if in the chain
          unless(hasAncestor(ifStmt(hasElse(ifStmt()))))
      ).bind("outerIf"),
      this
  );
}

void NoElseBranchCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *OuterIf = Result.Nodes.getNodeAs<IfStmt>("outerIf");
  if (!OuterIf)
    return;

  // Traverse the else-if chain to find the innermost if statement
  const IfStmt *LastIf = OuterIf;
  const Stmt *Else = OuterIf->getElse();

  while (Else) {
    if (const auto *ElseIf = dyn_cast<IfStmt>(Else)) {
      LastIf = ElseIf;
      Else = ElseIf->getElse();
    } else {
      // Found a non-if else branch, so the chain has an else (compound statement, etc.)
      // This is compliant
      return;
    }
  }

  // If we get here, LastIf is the innermost else-if and has no else branch
  if (!LastIf->getElse()) {
    diag(LastIf->getIfLoc(), "禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]");
  }
}

} // namespace clang::tidy::ucassaat