//===--- ReadabilityRedundantDeclarationCheck.h - clang-tidy ----*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYREDUNDANTDECLARATIONCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYREDUNDANTDECLARATIONCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Finds redundant variable and function declarations.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/readability-redundant-declaration.html
class ReadabilityRedundantDeclarationCheck : public ClangTidyCheck {
public:
  ReadabilityRedundantDeclarationCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;

private:
  void checkVarDecl(const clang::VarDecl *MatchedDecl,
                    const ast_matchers::MatchFinder::MatchResult &Result);
  void checkFuncDecl(const clang::FunctionDecl *MatchedDecl,
                     const ast_matchers::MatchFinder::MatchResult &Result);
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_READABILITYREDUNDANTDECLARATIONCHECK_H