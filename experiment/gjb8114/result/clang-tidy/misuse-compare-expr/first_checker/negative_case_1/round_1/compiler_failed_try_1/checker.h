//===--- MisuseCompareExprCheck.h - clang-tidy ------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// In all comparison expressions involving multiple operators that may cause ambiguity
/// due to operator precedence (especially when bitwise operators, arithmetic operators,
/// and comparison operators are mixed), parentheses must be used to explicitly define
/// the order of operations and prevent incorrect logical evaluations.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/misuse-compare-expr.html
class MisuseCompareExprCheck : public ClangTidyCheck {
public:
  MisuseCompareExprCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H