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
  // Match all local variable declarations (including function parameters)
  // and bind them for checking against global variables.
  Finder->addMatcher(
      varDecl(unless(parmVarDecl()), unless(isStaticLocal()),
              unless(isStaticDataMember()),
              hasDeclContext(anyOf(functionDecl(), blockDecl())))
          .bind("local_var"),
      this);
  Finder->addMatcher(
      parmVarDecl().bind("local_param"),
      this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("local_var");
  const auto *LocalParam = Result.Nodes.getNodeAs<ParmVarDecl>("local_param");
  
  const VarDecl *LocalDecl = nullptr;
  if (LocalVar) {
    LocalDecl = LocalVar;
  } else if (LocalParam) {
    LocalDecl = LocalParam;
  } else {
    return;
  }

  if (!LocalDecl || !LocalDecl->getIdentifier())
    return;

  std::string LocalName = LocalDecl->getName().str();
  
  // Get the translation unit declaration context
  ASTContext &Context = *Result.Context;
  TranslationUnitDecl *TUDecl = Context.getTranslationUnitDecl();
  if (!TUDecl)
    return;

  // Traverse all declarations in the translation unit to find global variables
  for (const auto *Decl : TUDecl->decls()) {
    if (const auto *GlobalVar = dyn_cast<VarDecl>(Decl)) {
      if (!GlobalVar->isFileVarDecl() || GlobalVar->isLocalVarDeclOrParm())
        continue;
      if (!GlobalVar->getIdentifier())
        continue;
      
      if (GlobalVar->getName() == LocalName) {
        diag(LocalDecl->getLocation(), 
             "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
        return; // Report only once per local variable
      }
    }
  }
}

} // namespace clang::tidy::ucassaat