使用增强逻辑生成checker代码，原始回答:
checker_cpp:
```cpp
//===--- ProhibitFloatConvertIntCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitFloatConvertIntCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitFloatConvertIntCheck::registerMatchers(MatchFinder *Finder) {
  // Match binary assignment operators where:
  // - LHS has integer type
  // - RHS after stripping parens and implicit casts is a floating-point type expression
  // - The floating-point expression is not a constant literal (unless it's a variable reference)
  // - Exclude cases where RHS is a floating-point literal directly (constant assignment)
  Finder->addMatcher(
      binaryOperator(
          isAssignmentOperator(),
          hasLHS(expr(hasType(isInteger()))),
          hasRHS(ignoringParenImpCasts(
              expr(hasType(realFloatingPointType()),
                   unless(floatLiteral()))
                  .bind("rhs")
          ))
      ).bind("assign"),
      this);
  
  // Match VarDecl declarations with initializers where:
  // - The declared variable has integer type
  // - The initializer after stripping parens and implicit casts is a floating-point type expression
  // - The floating-point expression is not a constant literal
  Finder->addMatcher(
      varDecl(
          hasType(isInteger()),
          hasInitializer(ignoringParenImpCasts(
              expr(hasType(realFloatingPointType()),
                   unless(floatLiteral()))
                  .bind("rhs")
          ))
      ).bind("vardecl"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Assign = Result.Nodes.getNodeAs<BinaryOperator>("assign");
  const auto *VD = Result.Nodes.getNodeAs<VarDecl>("vardecl");
  const auto *RHS = Result.Nodes.getNodeAs<Expr>("rhs");

  if (!RHS)
    return;

  // Handle binary assignment operators
  if (Assign) {
    // Verify that LHS is of integer type
    QualType LHSType = Assign->getLHS()->getType().getCanonicalType();
    if (!LHSType->isIntegerType())
      return;

    // Verify that RHS is of real floating-point type
    QualType RHSType = RHS->getType().getCanonicalType();
    if (!RHSType->isRealFloatingType())
      return;

    // Check for explicit cast on the RHS by walking up the AST parents
    // until we reach the assignment operator
    bool HasExplicitCast = false;
    const Stmt *Current = RHS;
    ASTContext &Context = *Result.Context;
    while (true) {
      auto Parents = Context.getParents(*Current);
      if (Parents.empty())
        break;
      const Stmt *ParentStmt = Parents[0].get<Stmt>();
      if (!ParentStmt)
        break;
      // If we encounter an explicit cast, the assignment is compliant
      if (isa<ExplicitCastExpr>(ParentStmt)) {
        HasExplicitCast = true;
        break;
      }
      // Stop if we reach the assignment operator
      if (ParentStmt == Assign)
        break;
      Current = ParentStmt;
    }

    if (HasExplicitCast)
      return;

    // Emit diagnostic message for violation
    diag(Assign->getBeginLoc(), "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
    return;
  }

  // Handle variable declarations with initializers
  if (VD) {
    // Verify that the declared variable is of integer type
    QualType VarType = VD->getType().getCanonicalType();
    if (!VarType->isIntegerType())
      return;

    // Verify that RHS is of real floating-point type
    QualType RHSType = RHS->getType().getCanonicalType();
    if (!RHSType->isRealFloatingType())
      return;

    // Check for explicit cast on the RHS by walking up the AST parents
    // until we reach the VarDecl
    bool HasExplicitCast = false;
    const Stmt *Current = RHS;
    ASTContext &Context = *Result.Context;
    while (true) {
      auto Parents = Context.getParents(*Current);
      if (Parents.empty())
        break;
      const Stmt *ParentStmt = Parents[0].get<Stmt>();
      if (!ParentStmt)
        break;
      // If we encounter an explicit cast, the declaration is compliant
      if (isa<ExplicitCastExpr>(ParentStmt)) {
        HasExplicitCast = true;
        break;
      }
      // Stop if we reach the VarDecl (the declaration itself is not a Stmt, 
      // but its parent should be a DeclStmt which is a Stmt)
      if (isa<DeclStmt>(ParentStmt))
        break;
      Current = ParentStmt;
    }

    if (HasExplicitCast)
      return;

    // Emit diagnostic message for violation
    diag(VD->getBeginLoc(), "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- ProhibitFloatConvertIntCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITFLOATCONVERTINTCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITFLOATCONVERTINTCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/prohibit-float-convert-int.html
class ProhibitFloatConvertIntCheck : public ClangTidyCheck {
public:
  ProhibitFloatConvertIntCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITFLOATCONVERTINTCHECK_H
```