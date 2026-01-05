使用增强逻辑生成checker代码，原始回答:
checker_cpp:
```cpp
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
```

checker_h:
```cpp
//===--- NoSameNameAsGlobalVariableCheck.h - clang-tidy ---------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// It is prohibited to use local variables with the same name as global variables in the code.
/// This rule aims to prevent program logic errors and issues with code readability caused by
/// variable name conflicts. When a local variable has the same name as a global variable,
/// it will shadow the global variable within its local scope, which may lead developers to
/// accidentally modify the wrong variable or misunderstand the scope of the variable,
/// thereby introducing hard-to-debug defects.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-same-name-as-global-variable.html
class NoSameNameAsGlobalVariableCheck : public ClangTidyCheck {
public:
  NoSameNameAsGlobalVariableCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H
```