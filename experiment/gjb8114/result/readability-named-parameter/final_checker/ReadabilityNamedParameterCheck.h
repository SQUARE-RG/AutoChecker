//===--- ReadabilityNamedParameterCheck.h - clang-tidy ----------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYNAMEDPARAMETERCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYNAMEDPARAMETERCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Find functions with unnamed arguments.
/// All parameters should be named, with identical names in the declaration and
/// implementation.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/readability-named-parameter.html
class ReadabilityNamedParameterCheck : public ClangTidyCheck {
public:
  ReadabilityNamedParameterCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYNAMEDPARAMETERCHECK_H