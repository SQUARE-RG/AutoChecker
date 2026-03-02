//===--- ProhibitNonLocalVariableInForLoopCheck.h - clang-tidy --*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Forbidden to use non-local variables for loop control variables.
/// The rule requires that the control variable of a for loop must be a local
/// variable, and non-local variables (such as global variables, static global
/// variables, or external-scope variables) must not be used as loop control
/// variables. This rule aims to ensure that the control variable of the loop
/// has a clear scope and lifetime, preventing unintended modifications and
/// logical errors in code caused by the spread of variable scope.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/prohibit-non-local-variable-in-for-loop.html
class ProhibitNonLocalVariableInForLoopCheck : public ClangTidyCheck {
public:
  ProhibitNonLocalVariableInForLoopCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H