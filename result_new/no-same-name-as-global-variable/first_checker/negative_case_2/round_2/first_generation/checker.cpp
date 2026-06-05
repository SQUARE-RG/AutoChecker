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
  // Match global variable declarations at file scope with global storage
  auto GlobalVarMatcher = varDecl(
      hasGlobalStorage(),
      isFileScope(),
      unless(isStaticStorageClass())
  ).bind("globalVar");

  // Match function definitions and find local variables (including parameters)
  // that have the same name as any global variable
  auto LocalVarMatcher = functionDecl(
      isDefinition(),
      forEachDescendant(varDecl(
          anyOf(
              parmVarDecl(),
              varDecl(hasLocalStorage())
          )
      ).bind("localVar"))
  );

  Finder->addMatcher(GlobalVarMatcher, this);
  Finder->addMatcher(LocalVarMatcher, this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("globalVar");
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("localVar");

  // Check if both nodes are present
  if (!GlobalVar || !LocalVar)
    return;

  // Ensure both variables have identifiers
  if (!GlobalVar->getIdentifier() || !LocalVar->getIdentifier())
    return;

  // Get the names of the variables
  StringRef GlobalName = GlobalVar->getName();
  StringRef LocalName = LocalVar->getName();

  // Check if the local variable name matches the global variable name
  if (GlobalName == LocalName) {
    diag(LocalVar->getLocation(),
         "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
  }
}

} // namespace clang::tidy::ucassaat