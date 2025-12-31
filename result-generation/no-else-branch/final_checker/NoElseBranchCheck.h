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