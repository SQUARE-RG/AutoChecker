针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_10.cpp增强checker
# Inputs

## rule
**Rule Description:**
This rule prohibits the direct assignment of a floating-point variable to an integer variable without using an explicit cast. It aims to prevent data precision loss and potential errors caused by implicit type conversions. When a floating-point variable (including types such as floatand double) is assigned to an integer variable (e.g., int, short, long, etc.), an explicit cast (e.g., (int)x) must be used to clearly convey the developer's intent. This avoids ambiguity and risks arising from the compiler automatically truncating the fractional part of the floating-point number.
A compliant scenario is when the assignment operation uses an explicit cast (e.g., i = (int)x;) or involves only integer variables. A violation occurs when a floating-point variable is directly assigned to an integer variable without a cast (e.g., i = x;) .
This rule specifically checks assignments between variables and does not apply to constant assignments. Furthermore, the explicit cast must correctly encompass the entire expression or variable

## current checker code

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
  // - LHS has integer type (any expression, not just DeclRefExpr)
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
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Assign = Result.Nodes.getNodeAs<BinaryOperator>("assign");
  const auto *RHS = Result.Nodes.getNodeAs<Expr>("rhs");

  if (!Assign || !RHS)
    return;

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

## passed test cases code

```cpp
#include <stdio.h>

int main(void) {
    float f1 = 1.23f;
    float f2;
    f2 = f1;  // 符合：浮点变量间赋值不违反规则
    printf("%f\n", f2);
    return 0;
}
#include <stdio.h>

int main(void) {
    double d = 12.34;
    short s;
    s = (short)(int)d;  // 符合：使用多重强制转换明确意图
    printf("%d\n", s);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f = 4.5f;
    double d = 2.5;
    int i;
    i = (int)f + (int)d;  // 符合：复杂表达式中每个浮点变量都使用强制转换
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

double global_d = 15.75;

int main(void) {
    int i;
    i = global_d;  // 违反：全局double变量直接赋给局部int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f1 = 2.5f, f2 = 3.5f;
    int i;
    i = (int)(f1 + f2);  // 符合：浮点表达式结果使用强制转换
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f = 3.14f;
    int i;
    i = f;  // 违反：float变量直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int convert_float(float f) {
    return (int)f;  // 符合：返回值中使用强制转换
}

int main(void) {
    float f = 9.99f;
    int result = convert_float(f);
    printf("%d\n", result);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f1 = 2.5f, f2 = 3.5f;
    int i;
    i = f1 + f2;  // 违反：浮点表达式结果直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

void print_int(int value) {
    printf("%d\n", value);
}

int main(void) {
    float f = 7.89f;
    print_int((int)f);  // 符合：函数参数中使用强制转换
    return 0;
}
#include <stdio.h>

#define FLOAT_TO_INT(x) ((int)(x))

int main(void) {
    float f = 6.66f;
    int i = FLOAT_TO_INT(f);  // 符合：宏定义中封装了强制转换
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    double d = 5.67;
    int i;
    i = (int)d;  // 符合：使用显式强制转换
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    double d = 5.67;
    int i;
    i = d;  // 违反：double变量直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    double d = 123.456;
    long l;
    l = d;  // 违反：double变量直接赋给long变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%ld\n", l);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f = 3.14f;
    int i;
    i = (int)f;  // 符合：使用显式强制转换
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    float f = 10.5f;
    short s;
    s = f;  // 违反：float变量直接赋给short变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", s);
    return 0;
}
#include <stdio.h>

struct Data {
    float value;
};

int main(void) {
    struct Data d = {8.88f};
    int i;
    i = d.value;  // 违反：结构体浮点成员直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    float arr[3] = {1.1f, 2.2f, 3.3f};
    int i;
    i = arr[1];  // 违反：浮点数组元素直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

float get_value(void) {
    return 7.89f;
}

int main(void) {
    int i;
    i = get_value();  // 违反：函数返回的float值直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
#include <stdio.h>

int main(void) {
    int a = 10;
    int b;
    b = a;  // 符合：整型变量间赋值不违反规则
    printf("%d\n", b);
    return 0;
}
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
#include <stdio.h>

int main(void) {
    float f = 12.34f;
    int i = f;  // 违反：初始化时float变量直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
```

### ast of  failed test cases
TranslationUnitDecl 0x5558cc249f68 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5558cc30f6e8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_10.cpp:3:1, line:9:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5558cc30fb20 <col:16, line:9:1>
    |-DeclStmt 0x5558cc30f830 <line:4:5, col:21>
    | `-VarDecl 0x5558cc30f7a8 <col:5, col:15> col:11 used f 'float' cinit
    |   `-FloatingLiteral 0x5558cc30f810 <col:15> 'float' 1.234000e+01
    |-DeclStmt 0x5558cc30f918 <line:5:5, col:14>
    | `-VarDecl 0x5558cc30f860 <col:5, col:13> col:9 used i 'int' cinit
    |   `-ImplicitCastExpr 0x5558cc30f900 <col:13> 'int' <FloatingToIntegral>
    |     `-ImplicitCastExpr 0x5558cc30f8e8 <col:13> 'float' <LValueToRValue>
    |       `-DeclRefExpr 0x5558cc30f8c8 <col:13> 'float' lvalue Var 0x5558cc30f7a8 'f' 'float'
    |-CallExpr 0x5558cc30fa90 <line:7:5, col:21> 'int'
    | |-ImplicitCastExpr 0x5558cc30fa78 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x5558cc30f9f8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x5558cc2ec318 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x5558cc30fac0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x5558cc30f9b8 <col:12> 'const char[4]' lvalue "%d\n"
    | `-ImplicitCastExpr 0x5558cc30fad8 <col:20> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x5558cc30f9d8 <col:20> 'int' lvalue Var 0x5558cc30f860 'i' 'int'
    `-ReturnStmt 0x5558cc30fb10 <line:8:5, col:12>
      `-IntegerLiteral 0x5558cc30faf0 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match binary assignment operators (including compound assignments like +=, -=, *=, /=) where LHS has integer type
2. For the RHS, use ignoringParenImpCasts to strip parentheses and implicit casts, then match an expression that has real floating-point type
3. Exclude the case where the stripped RHS is a floatLiteral (i.e., a constant floating-point literal) to allow direct constant assignments
4. Additionally, exclude the case where the stripped RHS is a floating-point variable reference (DeclRefExpr) to allow direct variable assignments, since the rule only prohibits implicit conversions from expressions, not direct assignments of variables
5. Bind the RHS expression node with 'rhs' for further checking in the callback
**logic for check**:
1. Retrieve the bound nodes: the assignment operator ('assign') and the RHS expression ('rhs')
2. Verify that the LHS type is indeed an integer type using getCanonicalType and isIntegerType
3. Verify that the RHS type (after stripping) is indeed a real floating-point type using getCanonicalType and isRealFloatingType
4. Check if there is an explicit cast on the RHS by walking up the AST parents from the RHS expression until the assignment operator is reached; if an ExplicitCastExpr is encountered, the assignment is compliant and no diagnostic should be emitted
5. If no explicit cast is found, emit a diagnostic at the location of the assignment operator indicating the violation


## reference astMatchers
Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Stmt>
 Description: Matches if a node equals a previously bound node.

Matches a node if it equals the node previously bound to ID.

Given
  class X { int a; int b; };
cxxRecordDecl(
    has(fieldDecl(hasName("a"), hasType(type().bind("t")))),
    has(fieldDecl(hasName("b"), hasType(type(equalsBoundNode("t"))))))
  matches the class X, as a and b have the same type.

Note that when multiple matches are involved via forEach* matchers,
equalsBoundNodes acts as a filter.
For example:
compoundStmt(
    forEachDescendant(varDecl().bind("d")),
    forEachDescendant(declRefExpr(to(decl(equalsBoundNode("d"))))))
will trigger a match for each combination of variable declaration
and reference to that variable declaration within a compound statement.

Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Type>
 Description: Matches if a node equals a previously bound node.

Matches a node if it equals the node previously bound to ID.

Given
  class X { int a; int b; };
cxxRecordDecl(
    has(fieldDecl(hasName("a"), hasType(type().bind("t")))),
    has(fieldDecl(hasName("b"), hasType(type(equalsBoundNode("t"))))))
  matches the class X, as a and b have the same type.

Note that when multiple matches are involved via forEach* matchers,
equalsBoundNodes acts as a filter.
For example:
compoundStmt(
    forEachDescendant(varDecl().bind("d")),
    forEachDescendant(declRefExpr(to(decl(equalsBoundNode("d"))))))
will trigger a match for each combination of variable declaration
and reference to that variable declaration within a compound statement.

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

stmt(eachOf(integerLiteral().bind(IntegerLiteralCheck::Name), floatLiteral().bind(FloatingLiteralCheck::Name)), unless(anyOf(hasParent(userDefinedLiteral()), hasAncestor(substNonTypeTemplateParmExpr()))))
Finder->addMatcher(stmt(forEachDescendant(binaryOperator(allOf(isAssignmentOperator(), hasRHS(RefVarOrField), hasLHS(anyOf(declRefExpr(to(varDecl().bind("pot_tid_var"))), memberExpr(member(fieldDecl().bind("pot_tid_field")))))))), this);
Finder->addMatcher(
  callExpr(
    callee(functionDecl(hasName("::pthread_setcanceltype"))),
    argumentCountIs(2),
    hasArgument(0, isExpandedFromMacro("PTHREAD_CANCEL_ASYNCHRONOUS")))
    .bind("setcanceltype"),
  this);


## reference code snippets
const auto *LoopVar = Nodes.getNodeAs<VarDecl>(InitVarName);
const auto *EndVar = Nodes.getNodeAs<VarDecl>(EndVarName);
const auto *EndCall = Nodes.getNodeAs<CXXMemberCallExpr>(EndCallName);
const auto *BoundExpr = Nodes.getNodeAs<Expr>(ConditionBoundName);
if (const auto *RetStmt = Result.Nodes.getNodeAs<ReturnStmt>("returnStmt")) {
  diag(RetStmt->getBeginLoc(), "operator=() should always return '*this'");
  return;
}
const auto *LHSCast = dyn_cast<ImplicitCastExpr>(ignoreNoOpCasts(LHS));
const auto *RHSCast = dyn_cast<ImplicitCastExpr>(ignoreNoOpCasts(RHS));

if (!LHSCast || !RHSCast || !isImplicitCastCandidate(LHSCast) ||
    !isImplicitCastCandidate(RHSCast))
  continue;
bool clang::ImplicitCastExpr::isPartOfExplicitCast() const
bool clang::ImplicitCastExpr::classof(const Stmt * T)
bool clang::CXXRewrittenBinaryOperator::isAssignmentOp() const

