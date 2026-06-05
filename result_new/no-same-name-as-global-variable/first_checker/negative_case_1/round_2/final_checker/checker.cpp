//===--- NoSameNameAsGlobalVariableCheck.cpp - clang-tidy -----------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoSameNameAsGlobalVariableCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoSameNameAsGlobalVariableCheck::registerMatchers(MatchFinder *Finder) {
  // Match global variable declarations (file-scope variables)
  Finder->addMatcher(
      varDecl(hasGlobalStorage(), unless(hasAncestor(functionDecl())),
              unless(hasAncestor(blockDecl())))
          .bind("global_var"),
      this);
  
  // Match local variable declarations (including function parameters and block-scope variables)
  Finder->addMatcher(
      varDecl(anyOf(parmVarDecl(), varDecl(hasLocalStorage())))
          .bind("local_var"),
      this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("global_var");
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("local_var");

  if (!GlobalVar || !LocalVar)
    return;

  if (!GlobalVar->getIdentifier() || !LocalVar->getIdentifier())
    return;

  // Get the names of the global and local variables
  StringRef GlobalName = GlobalVar->getName();
  StringRef LocalName = LocalVar->getName();

  // Check if the local variable name matches the global variable name
  if (GlobalName == LocalName) {
    diag(LocalVar->getLocation(),
         "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
  }
}

} // namespace clang::tidy::ucassaat