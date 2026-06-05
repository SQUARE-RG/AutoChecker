针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_8.cpp生成first checker
# Inputs

## rule
**Rule Description:**
This rule prohibits the direct assignment of a floating-point variable to an integer variable without using an explicit cast. It aims to prevent data precision loss and potential errors caused by implicit type conversions. When a floating-point variable (including types such as floatand double) is assigned to an integer variable (e.g., int, short, long, etc.), an explicit cast (e.g., (int)x) must be used to clearly convey the developer's intent. This avoids ambiguity and risks arising from the compiler automatically truncating the fractional part of the floating-point number.
A compliant scenario is when the assignment operation uses an explicit cast (e.g., i = (int)x;) or involves only integer variables. A violation occurs when a floating-point variable is directly assigned to an integer variable without a cast (e.g., i = x;) .
This rule specifically checks assignments between variables and does not apply to constant assignments. Furthermore, the explicit cast must correctly encompass the entire expression or variable

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

double global_d = 15.75;

int main(void) {
    int i;
    i = global_d;  // 违反：全局double变量直接赋给局部int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
```

## AST
TranslationUnitDecl 0x555e5337ff58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x555e534459f0 <line:5:1, line:11:1> line:5:5 main 'int ()'
  `-CompoundStmt 0x555e53445db0 <col:16, line:11:1>
    |-DeclStmt 0x555e53445b18 <line:6:5, col:10>
    | `-VarDecl 0x555e53445ab0 <col:5, col:9> col:9 used i 'int'
    |-BinaryOperator 0x555e53445ba0 <line:7:5, col:9> 'int' lvalue '='
    | |-DeclRefExpr 0x555e53445b30 <col:5> 'int' lvalue Var 0x555e53445ab0 'i' 'int'
    | `-ImplicitCastExpr 0x555e53445b88 <col:9> 'int' <FloatingToIntegral>
    |   `-ImplicitCastExpr 0x555e53445b70 <col:9> 'double' <LValueToRValue>
    |     `-DeclRefExpr 0x555e53445b50 <col:9> 'double' lvalue Var 0x555e53445870 'global_d' 'double'
    |-CallExpr 0x555e53445d20 <line:9:5, col:21> 'int'
    | |-ImplicitCastExpr 0x555e53445d08 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x555e53445c88 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x555e53422528 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x555e53445d50 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x555e53445c48 <col:12> 'const char[4]' lvalue "%d\n"
    | `-ImplicitCastExpr 0x555e53445d68 <col:20> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x555e53445c68 <col:20> 'int' lvalue Var 0x555e53445ab0 'i' 'int'
    `-ReturnStmt 0x555e53445da0 <line:10:5, col:12>
      `-IntegerLiteral 0x555e53445d80 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match binary assignment operators (operator=) where the LHS is a variable of integer type and the RHS is a variable of floating-point type (float, double, long double)
2. For the LHS, use hasType(isInteger()) to ensure the target is an integer type
3. For the RHS, use hasType(realFloatingPointType()) to ensure the source is a floating-point type
4. Use ignoringParenImpCasts() on the RHS to match the underlying floating-point expression, excluding any explicit casts
5. Exclude cases where the RHS is a constant (e.g., 3.14) by checking that the RHS is a DeclRefExpr (a variable reference) rather than a literal or constant expression
6. Bind the assignment expression as 'assign' and the RHS expression as 'rhs' for diagnostic reporting
**logic for check**:
1. Retrieve the bound assignment node ('assign') and the RHS node ('rhs') from the match result
2. Verify that the RHS is indeed a variable reference (DeclRefExpr) to a floating-point variable, not a constant
3. Check that the RHS does not contain an explicit cast to an integer type (e.g., (int)x) by verifying the absence of an explicit cast in the parent nodes of the RHS
4. If no explicit cast is present, emit a diagnostic message: '禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]'
5. Optionally, report the source location of the assignment for the user to identify the violation


## reference astMatchers
AST Traversal Matcher: ignoringImpCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after any implicit casts
are stripped off.

Parentheses and explicit casts are not discarded.
Given
  int arr[5];
  int a = 0;
  char b = 0;
  const int c = a;
  int *d = arr;
  long e = (long) 0l;
The matchers
   varDecl(hasInitializer(ignoringImpCasts(integerLiteral())))
   varDecl(hasInitializer(ignoringImpCasts(declRefExpr())))
would match the declarations for a, b, c, and d, but not e.
While
   varDecl(hasInitializer(integerLiteral()))
   varDecl(hasInitializer(declRefExpr()))
only match the declarations for a.

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

AST Traversal Matcher: ignoringParenCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after parentheses and
casts are stripped off.

Implicit and non-C Style casts are also discarded.
Given
  int a = 0;
  char b = (0);
  void* c = reinterpret_cast&lt;char*&gt;(0);
  char d = char(0);
The matcher
   varDecl(hasInitializer(ignoringParenCasts(integerLiteral())))
would match the declarations for a, b, c, and d.
while
   varDecl(hasInitializer(integerLiteral()))
only match the declaration for a.

Finder->addMatcher(
    callExpr(callee(functionDecl(
                 hasName("::frexp"), parameterCountIs(2),
                 HasBuiltinTyParam(0, DoubleTy),
                 hasParameter(1, parmVarDecl(hasType(pointerType(
                                     pointee(isBuiltinType(IntTy))))))))),
             HasBuiltinTyArg(0, FloatTy))
        .bind("call"),
    this);
Finder->addMatcher(
    callExpr(
        callee(functionDecl(
            hasName("::remquo"), parameterCountIs(3),
            HasBuiltinTyParam(0, DoubleTy), HasBuiltinTyParam(1, DoubleTy),
            hasParameter(2, parmVarDecl(hasType(pointerType(
                                pointee(isBuiltinType(IntTy))))))))),
        HasBuiltinTyArg(0, FloatTy), HasBuiltinTyArg(1, FloatTy))
        .bind("call"),
    this);
Finder->addMatcher(stmt(forEachDescendant(binaryOperator(allOf(isAssignmentOperator(), hasRHS(RefVarOrField), hasLHS(anyOf(declRefExpr(to(varDecl().bind("pot_tid_var"))), memberExpr(member(fieldDecl().bind("pot_tid_field")))))))), this);


## reference api
bool isCatchVariable(const DeclRefExpr *DeclRefExpr) {
  auto *ValueDecl = DeclRefExpr->getDecl();
  if (auto *VarDecl = dyn_cast<clang::VarDecl>(ValueDecl))
    return VarDecl->isExceptionVariable();
  return false;
}
const auto *BadOwnerAssignment = Nodes.getNodeAs<BinaryOperator>("bad_owner_creation_assignment");
const auto *BadOwnerInitialization = Nodes.getNodeAs<VarDecl>("bad_owner_creation_variable");
const auto *BadOwnerArgument = Nodes.getNodeAs<Expr>("bad_owner_creation_argument");
const auto *BadOwnerParameter = Nodes.getNodeAs<ParmVarDecl>("bad_owner_creation_parameter");
if (BadOwnerAssignment) {
  diag(BadOwnerAssignment->getBeginLoc(),
       "assigning newly created 'gsl::owner<>' to non-owner %0")
      << BadOwnerAssignment->getLHS()->getType()
      << BadOwnerAssignment->getSourceRange();
  return true;
}
if (BadOwnerInitialization) {
  diag(BadOwnerInitialization->getBeginLoc(),
       "initializing non-owner %0 with a newly created 'gsl::owner<>'")
      << BadOwnerInitialization->getType()
      << BadOwnerInitialization->getSourceRange();
  return true;
}
if (BadOwnerArgument) {
  assert(BadOwnerParameter && "parameter for the problematic argument not found");
  diag(BadOwnerArgument->getBeginLoc(), "initializing non-owner argument of "
                                        "type %0 with a newly created "
                                        "'gsl::owner<>'")
      << BadOwnerParameter->getType() << BadOwnerArgument->getSourceRange();
  return true;
}
return false;
bool isCastAllowedInCondition(const ImplicitCastExpr *Cast,
                              ASTContext &Context) {
  std::queue<const Stmt *> Q;
  Q.push(Cast);

  TraversalKindScope RAII(Context, TK_AsIs);

  while (!Q.empty()) {
    for (const auto &N : Context.getParents(*Q.front())) {
      const Stmt *S = N.get<Stmt>();
      if (!S)
        return false;
      if (isa<IfStmt>(S) || isa<ConditionalOperator>(S) || isa<ForStmt>(S) ||
          isa<WhileStmt>(S) || isa<BinaryConditionalOperator>(S))
        return true;
      if (isa<ParenExpr>(S) || isa<ImplicitCastExpr>(S) ||
          isUnaryLogicalNotOperator(S) ||
          (isa<BinaryOperator>(S) && cast<BinaryOperator>(S)->isLogicalOp())) {
        Q.push(S);
      } else {
        return false;
      }
    }
    Q.pop();
  }
  return false;
}
bool clang::DeclRefExpr::refersToEnclosingVariableOrCapture() const
bool clang::ImplicitCastExpr::isPartOfExplicitCast() const
bool clang::VarDecl::isUsableInConstantExpressions(const ASTContext & C) const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitFloatConvertIntCheck.cpp :
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
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *MatchedDecl = Result.Nodes.getNodeAs<FunctionDecl>("x");
  if (!MatchedDecl->getIdentifier() || MatchedDecl->getName().startswith("awesome_"))
    return;
  diag(MatchedDecl->getLocation(), "function %0 is insufficiently awesome")
      << MatchedDecl
      << FixItHint::CreateInsertion(MatchedDecl->getLocation(), "awesome_");
  diag(MatchedDecl->getLocation(), "insert 'awesome'", DiagnosticIDs::Note);
}

} // namespace clang::tidy::ucassaat

```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitFloatConvertIntCheck.h :
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
