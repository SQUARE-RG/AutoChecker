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
  // Global variables are declared at translation unit scope or namespace scope
  // and have global storage.
  auto GlobalVarMatcher = varDecl(
      hasGlobalStorage(),
      unless(hasAncestor(functionDecl())),
      unless(hasAncestor(blockDecl()))
  ).bind("global_var");

  // Match function definitions (to scope the local variable search)
  // For each function definition, match local variables (including parameters,
  // local variables, and block-scope variables) that have the same name as any
  // global variable.
  auto LocalVarMatcher = functionDecl(
      isDefinition(),
      forEachDescendant(varDecl(
          anyOf(
              parmVarDecl(),
              varDecl(hasLocalStorage())
          ),
          unless(parmVarDecl(hasAncestor(functionDecl(unless(isDefinition())))))
      ).bind("local_var"))
  );

  // We need to match global variables separately and then in check() we compare names
  Finder->addMatcher(GlobalVarMatcher, this);
  Finder->addMatcher(LocalVarMatcher, this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("global_var");
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("local_var");

  // We need both a global and a local variable to compare
  if (!GlobalVar || !LocalVar)
    return;

  // Ensure both variables have identifiers (names)
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