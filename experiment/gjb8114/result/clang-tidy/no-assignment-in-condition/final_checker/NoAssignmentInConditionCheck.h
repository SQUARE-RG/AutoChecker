//===--- NoAssignmentInConditionCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Prohibits direct use of assignment statements in logical expressions
/// (such as conditional statements like if, while, for), aimed at preventing
/// logical errors caused by mistakenly using the assignment operator (=)
/// instead of the comparison operator (==).
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-assignment-in-condition.html
class NoAssignmentInConditionCheck : public ClangTidyCheck {
public:
  NoAssignmentInConditionCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H