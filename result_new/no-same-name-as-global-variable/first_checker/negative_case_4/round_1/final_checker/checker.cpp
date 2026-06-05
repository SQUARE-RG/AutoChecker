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
  // Match all local variable declarations (including function parameters and
  // variables with local storage) that are inside a function definition.
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

  // Ensure the local variable node is present
  if (!LocalVar)
    return;

  // Ensure the local variable has an identifier
  if (!LocalVar->getIdentifier())
    return;

  // Get the name of the local variable
  StringRef LocalName = LocalVar->getName();

  // Obtain the translation unit declaration to iterate over all declarations
  const auto *TU = Result.Context->getTranslationUnitDecl();
  if (!TU)
    return;

  // Iterate through all declarations in the translation unit
  for (const auto *Decl : TU->decls()) {
    // Check if the declaration is a VarDecl with global storage
    const auto *GlobalVar = dyn_cast<VarDecl>(Decl);
    if (!GlobalVar)
      continue;

    // Ensure it is a global variable (not local, not parameter, not inside a function)
    if (GlobalVar->isLocalVarDeclOrParm())
      continue;

    // Ensure the global variable has an identifier
    if (!GlobalVar->getIdentifier())
      continue;

    // Check if the names match
    if (GlobalVar->getName() == LocalName) {
      diag(LocalVar->getLocation(),
           "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
      // Only report once per local variable
      break;
    }
  }
}

} // namespace clang::tidy::ucassaat