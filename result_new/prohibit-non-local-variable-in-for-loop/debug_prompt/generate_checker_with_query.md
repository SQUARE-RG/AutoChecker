使用增强逻辑生成checker代码，原始回答:
checker_cpp:
```cpp
//===--- ProhibitNonLocalVariableInForLoopCheck.cpp - clang-tidy ----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitNonLocalVariableInForLoopCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitNonLocalVariableInForLoopCheck::registerMatchers(MatchFinder *Finder) {
  // Match for statements that:
  // 1. Have an init part that is a binary assignment operator
  // 2. Exclude for loops where init is a declaration statement (local variable)
  // 3. Match the LHS expression, ignoring parentheses and implicit casts
  // 4. For DeclRefExpr, bind the referenced VarDecl as 'loopVar' and the expression as 'loopVarRef'
  // 5. For MemberExpr, bind the member VarDecl as 'loopVar' and the expression as 'loopVarRef'
  // 6. Additionally, handle cases where the LHS is a unary operator (e.g., *ptr = ...) by
  //    matching the DeclRefExpr inside the unary operator's sub-expression
  Finder->addMatcher(
      forStmt(
          unless(hasLoopInit(declStmt())),
          hasLoopInit(
              binaryOperator(
                  isAssignmentOperator(),
                  hasLHS(ignoringParenImpCasts(
                      anyOf(
                          declRefExpr(to(varDecl().bind("loopVar"))).bind("loopVarRef"),
                          memberExpr(member(varDecl().bind("loopVar"))).bind("loopVarRef"),
                          // Handle cases like *global_ptr = ... where the LHS is a unary operator
                          unaryOperator(
                              hasOperatorName("*"),
                              hasUnaryOperand(ignoringParenImpCasts(
                                  anyOf(
                                      declRefExpr(to(varDecl().bind("loopVar"))).bind("loopVarRef"),
                                      memberExpr(member(varDecl().bind("loopVar"))).bind("loopVarRef")
                                  )
                              ))
                          )
                      )
                  ))
              )
          )
      ).bind("forLoop"),
      this
  );
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ForLoop = Result.Nodes.getNodeAs<ForStmt>("forLoop");
  const auto *LoopVarRef = Result.Nodes.getNodeAs<Expr>("loopVarRef");
  const auto *LoopVar = Result.Nodes.getNodeAs<VarDecl>("loopVar");

  if (!ForLoop || !LoopVarRef || !LoopVar)
    return;

  // Check if the variable is non-local:
  // - hasGlobalStorage() covers global variables, static global variables
  // - isFileVarDecl() covers variables with file scope (external linkage)
  // - hasExternalStorage() covers variables declared with 'extern'
  if (LoopVar->hasGlobalStorage() || LoopVar->isFileVarDecl() || LoopVar->hasExternalStorage()) {
    // Skip static local variables (they have local scope but static storage)
    if (!LoopVar->isLocalVarDecl() || LoopVar->isStaticLocal()) {
      diag(ForLoop->getForLoc(), "禁止 for 循环控制变量使用非局部变量");
    }
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
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

/// FIXME: Write a short description.
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
```