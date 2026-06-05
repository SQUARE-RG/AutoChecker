针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr/dependent_call_in_expr_case_4.cpp生成first checker
# Inputs

## rule
**Rule Description:**
Multiple related functions cannot be called in the same expression.Related functions refer to functions called in the same expression that have a data dependency relationship, which will result in undefined behavior.Scenario: Reporting multiple related function calls
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            int y = inc(&x) + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then it should report "test.c:16:21: warning: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]"
    And a total of 1 warning should be reported

Scenario: Do not report multiple related function calls that are not in the same expression
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            x = inc(&x);
            int y = x + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then no warnings should be reported

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int modify_array(int arr[], int index) {
    arr[index] += 10;
    return arr[index];
}

int get_array_value(int arr[], int index) {
    return arr[index];
}

int main(void) {
    int numbers[3] = {1, 2, 3};
    int result = modify_array(numbers, 0) - get_array_value(numbers, 0);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
```

## AST
TranslationUnitDecl 0x55e72ca24f48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55e72caeae60 <line:12:1, line:17:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x55e72caeb510 <col:16, line:17:1>
    |-DeclStmt 0x55e72caeb128 <line:13:5, col:31>
    | `-VarDecl 0x55e72caeafb0 <col:5, col:30> col:9 used numbers 'int[3]' cinit
    |   `-InitListExpr 0x55e72caeb0d0 <col:22, col:30> 'int[3]'
    |     |-IntegerLiteral 0x55e72caeb018 <col:23> 'int' 1
    |     |-IntegerLiteral 0x55e72caeb038 <col:26> 'int' 2
    |     `-IntegerLiteral 0x55e72caeb058 <col:29> 'int' 3
    |-DeclStmt 0x55e72caeb4b0 <line:14:5, col:72>
    | `-VarDecl 0x55e72caeb1c0 <col:5, col:71> col:9 used result 'int' cinit
    |   `-BinaryOperator 0x55e72caeb490 <col:18, col:71> 'int' '-'
    |     |-CallExpr 0x55e72caeb340 <col:18, col:41> 'int'
    |     | |-ImplicitCastExpr 0x55e72caeb328 <col:18> 'int (*)(int *, int)' <FunctionToPointerDecay>
    |     | | `-DeclRefExpr 0x55e72caeb2b0 <col:18> 'int (int *, int)' lvalue Function 0x55e72caea880 'modify_array' 'int (int *, int)'
    |     | |-ImplicitCastExpr 0x55e72caeb370 <col:31> 'int *' <ArrayToPointerDecay>
    |     | | `-DeclRefExpr 0x55e72caeb270 <col:31> 'int[3]' lvalue Var 0x55e72caeafb0 'numbers' 'int[3]'
    |     | `-IntegerLiteral 0x55e72caeb290 <col:40> 'int' 0
    |     `-CallExpr 0x55e72caeb448 <col:45, col:71> 'int'
    |       |-ImplicitCastExpr 0x55e72caeb430 <col:45> 'int (*)(int *, int)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x55e72caeb410 <col:45> 'int (int *, int)' lvalue Function 0x55e72caeac38 'get_array_value' 'int (int *, int)'
    |       |-ImplicitCastExpr 0x55e72caeb478 <col:61> 'int *' <ArrayToPointerDecay>
    |       | `-DeclRefExpr 0x55e72caeb3d0 <col:61> 'int[3]' lvalue Var 0x55e72caeafb0 'numbers' 'int[3]'
    |       `-IntegerLiteral 0x55e72caeb3f0 <col:70> 'int' 0
    `-ReturnStmt 0x55e72caeb500 <line:16:5, col:12>
      `-ImplicitCastExpr 0x55e72caeb4e8 <col:12> 'int' <LValueToRValue>
        `-DeclRefExpr 0x55e72caeb4c8 <col:12> 'int' lvalue Var 0x55e72caeb1c0 'result' 'int'


## reference logic step
**logic for registerMatchers**:
1. Match all function call expressions in the translation unit using `callExpr()` and bind them as 'call'
2. For each call expression, also match the parent expression of the call (the expression containing the call) using `hasParent()` and bind it as 'parentExpr'
3. Create a matcher for binary operators (additive, multiplicative, assignment, etc.) that contain at least two callExpr children, using `binaryOperator(hasOperands(callExpr(), callExpr()))` and bind the binary operator as 'binaryOp'
4. Extend the binary operator matcher to also capture calls that are arguments to the binary operator, including nested calls within the same binary expression
5. Ensure the matcher only triggers when there are multiple call expressions directly or indirectly inside the same binary operator expression
**logic for check**:
1. Retrieve the bound binary operator node ('binaryOp') from the match result
2. Retrieve all call expressions that are direct or indirect children of the binary operator by traversing the AST
3. For each pair of call expressions found in the same binary expression, check if they share at least one argument that is a pointer or array type (indicating data dependency)
4. If a data dependency is found (both functions modify or read the same memory location), emit a diagnostic warning: '禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]'
5. Stop further checking for the same binary expression once a violation is reported to avoid duplicate warnings


## reference astMatchers
AST Traversal Matcher: ignoringParenImpCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after implicit casts and
parentheses are stripped off.

Explicit casts are not discarded.
Given
  int arr[5];
  int a = 0;
  char b = (0);
  const int c = a;
  int *d = (arr);
  long e = ((long) 0l);
The matchers
   varDecl(hasInitializer(ignoringParenImpCasts(integerLiteral())))
   varDecl(hasInitializer(ignoringParenImpCasts(declRefExpr())))
would match the declarations for a, b, c, and d, but not e.
while
   varDecl(hasInitializer(integerLiteral()))
   varDecl(hasInitializer(declRefExpr()))
would only match the declaration for a.

AST Traversal Matcher: hasOperands
 Parameters;Matcher<Expr> Matcher1, Matcher<Expr> Matcher2
 Return type Matcher<CXXOperatorCallExpr>
 Description: Matches if both matchers match with opposite sides of the binary operator.

Example matcher = binaryOperator(hasOperands(integerLiteral(equals(1),
                                             integerLiteral(equals(2)))
  1 + 2 // Match
  2 + 1 // Match
  1 + 1 // No match
  2 + 2 // No match

AST Traversal Matcher: hasOperands
 Parameters;Matcher<Expr> Matcher1, Matcher<Expr> Matcher2
 Return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches if both matchers match with opposite sides of the binary operator.

Example matcher = binaryOperator(hasOperands(integerLiteral(equals(1),
                                             integerLiteral(equals(2)))
  1 + 2 // Match
  2 + 1 // Match
  1 + 1 // No match
  2 + 2 // No match

Finder->addMatcher(callExpr(hasDeclaration(functionDecl(forEachTemplateArgument(templateArgument().bind("used"))))), this);
binaryOperator(hasOperatorName("*"), hasEitherOperand(ignoringImpCasts(anyOf(integerLiteral(), floatLiteral())))).bind("mult_binop")
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")


## reference api
static bool hasSingleVariadicArgumentWithValue(const CallExpr *C, uint64_t I) {
  const auto *FDecl = dyn_cast<FunctionDecl>(C->getCalleeDecl());
  if (!FDecl)
    return false;

  auto N = FDecl->getNumParams();
  if (C->getNumArgs() != N + 1)
    return false;

  const auto *IntLit =
      dyn_cast<IntegerLiteral>(C->getArg(N)->IgnoreParenImpCasts());
  if (!IntLit)
    return false;

  if (IntLit->getValue() != I)
    return false;

  return true;
}
SourceLocation Loc;

if (const auto *Op = Result.Nodes.getNodeAs<BinaryOperator>("binary_op"))
  Loc = Op->getOperatorLoc();
else if (const auto *Op = Result.Nodes.getNodeAs<UnaryOperator>("unary_op"))
  Loc = Op->getOperatorLoc();
else if (const auto *Op =
           Result.Nodes.getNodeAs<CXXOperatorCallExpr>("overloaded_op"))
  Loc = Op->getOperatorLoc();

if (Loc.isInvalid())
  return;
else if (const auto *CE = dyn_cast<CallExpr>(S)) {
  for (const auto *Arg : CE->arguments()) {
    markCanNotBeConst(Arg->IgnoreParenCasts(), true);
  }
  if (const FunctionDecl *FD = CE->getDirectCallee()) {
    unsigned ArgNr = 0U;
    for (const auto *Par : FD->parameters()) {
      if (ArgNr >= CE->getNumArgs())
        break;
      const Expr *Arg = CE->getArg(ArgNr++);
      const Type *ParType = Par->getType().getTypePtr();
      if (!ParType->isReferenceType() || Par->getType().isConstQualified())
        continue;
      markCanNotBeConst(Arg->IgnoreParenCasts(), false);
    }
  }
}
SourceLocation clang::BinaryOperator::getExprLoc() const
SourceLocation clang::BinaryOperator::getOperatorLoc() const
StringRef clang::BinaryOperator::getOpcodeStr() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DependentCallInExprCheck.cpp :
```cpp
//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/Basic/Diagnostic.h"
#include <set>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to collect all variables that are passed by non-const pointer
// or array to a function call
static void collectModifiedVars(const CallExpr *Call, 
                                std::set<const ValueDecl *> &ModifiedVars) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  for (unsigned I = 0; I < Call->getNumArgs() && I < FD->getNumParams(); ++I) {
    const ParmVarDecl *Param = FD->getParamDecl(I);
    QualType ParamType = Param->getType();
    
    // Check if parameter is non-const pointer or array type
    bool IsNonConstPointer = false;
    if (ParamType->isPointerType()) {
      // For pointer types, check the pointee type's const qualification
      IsNonConstPointer = !ParamType->getPointeeType().isConstQualified();
    } else if (ParamType->isArrayType()) {
      // Array parameters decay to pointers, check the element type
      const ArrayType *ArrType = ParamType->getAsArrayTypeUnsafe();
      if (ArrType) {
        IsNonConstPointer = !ArrType->getElementType().isConstQualified();
      }
    }

    if (!IsNonConstPointer)
      continue;

    const Expr *Arg = Call->getArg(I)->IgnoreParenImpCasts();
    
    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        ModifiedVars.insert(VD);
      }
    }
  }
}

// Helper function to check if two function calls have data dependency
// through pointer/array arguments
static bool hasDataDependency(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // Collect all variables that are potentially modified by Call1
  std::set<const ValueDecl *> ModifiedVars;
  collectModifiedVars(Call1, ModifiedVars);

  if (ModifiedVars.empty())
    return false;

  // Check if Call2 accesses any of the modified variables
  const FunctionDecl *FD2 = Call2->getDirectCallee();
  if (!FD2)
    return false;

  for (unsigned I = 0; I < Call2->getNumArgs(); ++I) {
    const Expr *Arg = Call2->getArg(I)->IgnoreParenImpCasts();
    
    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call2->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        if (ModifiedVars.count(VD))
          return true;
      }
    }
  }

  return false;
}

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match binary operators that contain at least two CallExpr nodes
  // We bind the binary operator and use forEachDescendant to find calls
  Finder->addMatcher(
      binaryOperator(
          anyOf(hasOperatorName("+"), hasOperatorName("-"),
                hasOperatorName("*"), hasOperatorName("/"),
                hasOperatorName("%"), hasOperatorName("&"),
                hasOperatorName("|"), hasOperatorName("^"),
                hasOperatorName("&&"), hasOperatorName("||"),
                hasOperatorName("=="), hasOperatorName("!="),
                hasOperatorName("<"), hasOperatorName(">"),
                hasOperatorName("<="), hasOperatorName(">="),
                hasOperatorName("<<"), hasOperatorName(">>")),
          hasDescendant(callExpr().bind("call1")),
          hasDescendant(callExpr().bind("call2")))
          .bind("binaryOp"),
      this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *Call1 = Result.Nodes.getNodeAs<CallExpr>("call1");
  const auto *Call2 = Result.Nodes.getNodeAs<CallExpr>("call2");

  if (!BinaryOp || !Call1 || !Call2)
    return;

  // Ensure we have two distinct function calls
  if (Call1 == Call2)
    return;

  // Get the direct callee functions
  const FunctionDecl *Func1 = Call1->getDirectCallee();
  const FunctionDecl *Func2 = Call2->getDirectCallee();

  if (!Func1 || !Func2)
    return;

  // Check if the two calls have data dependency
  if (hasDataDependency(Call1, Call2) || hasDataDependency(Call2, Call1)) {
    diag(BinaryOp->getExprLoc(),
         "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
  }
}

} // namespace clang::tidy::ucassaat
```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DependentCallInExprCheck.h :
```cpp
//===--- DependentCallInExprCheck.h - clang-tidy ----------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/dependent-call-in-expr.html
class DependentCallInExprCheck : public ClangTidyCheck {
public:
  DependentCallInExprCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H
```
