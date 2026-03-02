使用增强逻辑生成checker代码，原始回答:
checker_cpp:
```cpp
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
  // Match if statements that have at least one else-if branch
  // We need to match the entire chain starting from the first if
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
  bool FoundViolation = false;

  while (CurrentIf) {
    LastIf = CurrentIf;
    
    // Check if this if statement has an else branch
    const Stmt *ElseBranch = CurrentIf->getElse();
    if (!ElseBranch) {
      // No else branch - this is a violation
      FoundViolation = true;
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
  if (FoundViolation && LastIf && !LastIf->getElse()) {
    SourceLocation DiagLoc = LastIf->getElseLoc();
    if (!DiagLoc.isValid()) {
      DiagLoc = LastIf->getEndLoc();
    }
    diag(DiagLoc,
         "禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]");
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- NoElseBranchCheck.h - clang-tidy -----------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Prohibit omitting the else branch of if-else if statements.
/// In all if-else if statement structures, the final else branch must be
/// included, even if it does not perform any operations, and must be
/// explicitly written. This is to ensure the logical integrity of the code
/// and prevent undefined behavior due to omitted conditions.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-else-branch.html
class NoElseBranchCheck : public ClangTidyCheck {
public:
  NoElseBranchCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H
```