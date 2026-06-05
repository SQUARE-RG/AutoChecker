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
  // Match all global variable declarations (file/namespace scope, global storage)
  Finder->addMatcher(
      varDecl(
          hasGlobalStorage(),
          unless(anyOf(
              parmVarDecl(),
              hasAncestor(functionDecl()),
              hasAncestor(blockDecl())
          ))
      ).bind("globalVar"),
      this
  );

  // Match all local variable declarations (function parameters, variables with local storage)
  Finder->addMatcher(
      varDecl(
          anyOf(
              parmVarDecl(),
              varDecl(hasLocalStorage())
          ),
          hasAncestor(functionDecl(isDefinition()))
      ).bind("localVar"),
      this
  );
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("localVar");
  const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("globalVar");

  // Ensure both nodes are present
  if (!LocalVar || !GlobalVar)
    return;

  // Ensure both variables have identifiers
  if (!LocalVar->getIdentifier() || !GlobalVar->getIdentifier())
    return;

  // Get the names of the variables
  StringRef LocalName = LocalVar->getName();
  StringRef GlobalName = GlobalVar->getName();

  // Check if the local variable name matches the global variable name
  if (LocalName == GlobalName) {
    diag(LocalVar->getLocation(),
         "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
  }
}

} // namespace clang::tidy::ucassaat