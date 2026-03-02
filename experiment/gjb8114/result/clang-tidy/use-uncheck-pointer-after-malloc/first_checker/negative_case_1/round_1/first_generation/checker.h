//===--- UseUncheckPointerAfterMallocCheck.h - clang-tidy -------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Checks that pointers obtained through dynamic memory allocation functions
/// (malloc, calloc, realloc) are checked for null before their first use.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/use-uncheck-pointer-after-malloc.html
class UseUncheckPointerAfterMallocCheck : public ClangTidyCheck {
public:
  UseUncheckPointerAfterMallocCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H