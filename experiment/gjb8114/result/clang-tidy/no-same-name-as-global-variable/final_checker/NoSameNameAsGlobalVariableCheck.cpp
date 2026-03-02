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
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoSameNameAsGlobalVariableCheck::registerMatchers(MatchFinder *Finder) {
  // Match global variable declarations (file scope)
  auto GlobalVarMatcher = varDecl(
      hasGlobalStorage(),
      hasDeclContext(anyOf(translationUnitDecl(), namespaceDecl())),
      unless(isExternC()),
      unless(isImplicit()))
      .bind("globalVar");

  // Match local variable declarations (function/block scope)
  // Include static local variables by removing hasLocalStorage()
  auto LocalVarMatcher = varDecl(
      hasDeclContext(anyOf(functionDecl(), blockDecl(), recordDecl())),
      unless(hasGlobalStorage()),
      unless(isImplicit()))
      .bind("localVar");

  // Match function parameter declarations
  auto ParamVarMatcher = parmVarDecl(
      unless(isImplicit()))
      .bind("paramVar");

  // Register all matchers
  Finder->addMatcher(GlobalVarMatcher, this);
  Finder->addMatcher(LocalVarMatcher, this);
  Finder->addMatcher(ParamVarMatcher, this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  // Collect global variables from the translation unit
  static std::vector<const VarDecl *> GlobalVars;
  
  if (const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("globalVar")) {
    if (GlobalVar && !GlobalVar->isInvalidDecl()) {
      // Check if we're in a system header
      if (Result.SourceManager->isInSystemHeader(GlobalVar->getLocation())) {
        return;
      }
      GlobalVars.push_back(GlobalVar);
    }
    return;
  }

  const VarDecl *LocalOrParamVar = nullptr;
  
  if (const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("localVar")) {
    LocalOrParamVar = LocalVar;
  } else if (const auto *ParamVar = Result.Nodes.getNodeAs<ParmVarDecl>("paramVar")) {
    LocalOrParamVar = ParamVar;
  }
  
  if (!LocalOrParamVar || LocalOrParamVar->isInvalidDecl()) {
    return;
  }

  // Check if we're in a system header
  if (Result.SourceManager->isInSystemHeader(LocalOrParamVar->getLocation())) {
    return;
  }

  // Get local/parameter variable name
  std::string LocalName = LocalOrParamVar->getNameAsString();
  if (LocalName.empty()) {
    return;
  }

  // Check against all global variables
  for (const auto *GlobalVar : GlobalVars) {
    if (!GlobalVar || GlobalVar->isInvalidDecl()) {
      continue;
    }

    std::string GlobalName = GlobalVar->getNameAsString();
    if (GlobalName.empty()) {
      continue;
    }

    // Check if names match
    if (LocalName == GlobalName) {
      // Emit diagnostic
      diag(LocalOrParamVar->getLocation(), 
           "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]")
          << LocalOrParamVar;
      break; // Only report once per local/parameter variable
    }
  }
}

} // namespace clang::tidy::ucassaat