针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_10.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

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
#include "clang/AST/Expr.h"
#include "clang/AST/Type.h"
#include "clang/AST/OperationKinds.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitFloatConvertIntCheck::registerMatchers(MatchFinder *Finder) {
  // Match assignment operators where LHS is integer type and RHS is floating type
  // Exclude cases where RHS is a constant literal or has explicit cast to integer
  Finder->addMatcher(
      binaryOperator(
          isAssignmentOperator(),
          hasLHS(expr(hasType(isInteger())).bind("lhsExpr")),
          hasRHS(expr(
              anyOf(
                  // Match floating type expressions
                  expr(hasType(realFloatingPointType())),
                  // Also match expressions that after ignoring implicit casts
                  // have floating type (to catch implicit conversions)
                  ignoringParenImpCasts(expr(hasType(realFloatingPointType())))
              )
          ).bind("rhsExpr")),
          // Exclude cases where RHS has explicit cast to integer
          unless(hasRHS(expr(anyOf(
              cStyleCastExpr(hasDestinationType(isInteger())),
              cxxStaticCastExpr(hasDestinationType(isInteger())),
              cxxFunctionalCastExpr(hasDestinationType(isInteger()))
          )))),
          // Exclude constant expressions (literals)
          unless(hasRHS(ignoringParenImpCasts(
              expr(anyOf(
                  floatLiteral(),
                  integerLiteral()
              ))
          )))
      ).bind("assignOp"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp");
  const auto *LHSExpr = Result.Nodes.getNodeAs<Expr>("lhsExpr");
  const auto *RHSExpr = Result.Nodes.getNodeAs<Expr>("rhsExpr");
  
  if (!AssignOp || !AssignOp->getOperatorLoc().isValid()) {
    return;
  }
  
  if (!LHSExpr || !LHSExpr->getExprLoc().isValid() ||
      !RHSExpr || !RHSExpr->getExprLoc().isValid()) {
    return;
  }
  
  // Verify LHS is integer type
  if (!LHSExpr->getType()->isIntegerType()) {
    return;
  }
  
  // Strip implicit casts and parentheses from RHS to get the core expression
  const Expr *StrippedRHS = RHSExpr->IgnoreParenImpCasts();
  if (!StrippedRHS) {
    return;
  }
  
  // Verify RHS is floating type (after stripping implicit casts)
  if (!StrippedRHS->getType()->isFloatingType()) {
    return;
  }
  
  // Check if RHS is value-dependent or type-dependent
  if (RHSExpr->isValueDependent() || RHSExpr->isTypeDependent()) {
    return;
  }
  
  // Check if RHS is a constant expression (exempt per rule)
  // First check if it's a literal (already excluded in matcher, but double-check)
  if (isa<FloatingLiteral>(StrippedRHS) || isa<IntegerLiteral>(StrippedRHS)) {
    return;
  }
  
  // Check if it evaluates to a constant (including const variables)
  Expr::EvalResult EvalResult;
  if (RHSExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    return;
  }
  
  // Also check the stripped version
  if (StrippedRHS->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    return;
  }
  
  // Check if RHS is a DeclRefExpr to a const variable with constant initializer
  if (const auto *DRE = dyn_cast<DeclRefExpr>(StrippedRHS)) {
    if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
      if (VD->getType().isConstQualified()) {
        if (const Expr *Init = VD->getInit()) {
          if (Init->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
            return;
          }
        }
      }
    }
  }
  
  // Check for member expressions (like d.value in the failed test case)
  if (const auto *ME = dyn_cast<MemberExpr>(StrippedRHS)) {
    // Check if the member expression refers to a const member
    if (const auto *FD = dyn_cast<FieldDecl>(ME->getMemberDecl())) {
      if (FD->getType().isConstQualified()) {
        // For const member access, we need to check if the entire expression
        // evaluates to a constant
        if (RHSExpr->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
          return;
        }
      }
    }
  }
  
  // Emit diagnostic
  auto Diag = diag(AssignOp->getOperatorLoc(), 
                   "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
  
  // Add source ranges for better context
  Diag << SourceRange(LHSExpr->getBeginLoc(), LHSExpr->getEndLoc())
       << SourceRange(RHSExpr->getBeginLoc(), RHSExpr->getEndLoc());
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

/// This rule prohibits the direct assignment of a floating-point variable to an 
/// integer variable without using an explicit cast. It aims to prevent data 
/// precision loss and potential errors caused by implicit type conversions.
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

int main(void) {
    float f1 = 2.5f, f2 = 3.5f;
    int i;
    i = f1 + f2;  // 违反：浮点表达式结果直接赋给int变量未使用强制转换
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
    double d = 5.67;
    int i;
    i = (int)d;  // 符合：使用显式强制转换
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
    float f = 10.5f;
    short s;
    s = f;  // 违反：float变量直接赋给short变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", s);
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
#include <stdio.h>

int main(void) {
    float arr[3] = {1.1f, 2.2f, 3.3f};
    int i;
    i = arr[1];  // 违反：浮点数组元素直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
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
TranslationUnitDecl 0x5596b94c8f68 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5596b958e6e8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_10.cpp:3:1, line:9:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5596b958eb20 <col:16, line:9:1>
    |-DeclStmt 0x5596b958e830 <line:4:5, col:21>
    | `-VarDecl 0x5596b958e7a8 <col:5, col:15> col:11 used f 'float' cinit
    |   `-FloatingLiteral 0x5596b958e810 <col:15> 'float' 1.234000e+01
    |-DeclStmt 0x5596b958e918 <line:5:5, col:14>
    | `-VarDecl 0x5596b958e860 <col:5, col:13> col:9 used i 'int' cinit
    |   `-ImplicitCastExpr 0x5596b958e900 <col:13> 'int' <FloatingToIntegral>
    |     `-ImplicitCastExpr 0x5596b958e8e8 <col:13> 'float' <LValueToRValue>
    |       `-DeclRefExpr 0x5596b958e8c8 <col:13> 'float' lvalue Var 0x5596b958e7a8 'f' 'float'
    |-CallExpr 0x5596b958ea90 <line:7:5, col:21> 'int'
    | |-ImplicitCastExpr 0x5596b958ea78 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x5596b958e9f8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x5596b956b318 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x5596b958eac0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x5596b958e9b8 <col:12> 'const char[4]' lvalue "%d\n"
    | `-ImplicitCastExpr 0x5596b958ead8 <col:20> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x5596b958e9d8 <col:20> 'int' lvalue Var 0x5596b958e860 'i' 'int'
    `-ReturnStmt 0x5596b958eb10 <line:8:5, col:12>
      `-IntegerLiteral 0x5596b958eaf0 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match binary operators that are assignment operators (e.g., '=', '*=', '+=').
2. Bind the entire assignment operator as 'assignOp'.
3. For the left-hand side (LHS), match an expression with an integer type and bind it as 'lhsExpr'.
4. For the right-hand side (RHS), match an expression that, after ignoring parentheses and implicit casts, has a real floating-point type. Bind this RHS expression as 'rhsExpr'.
5. Exclude cases where the RHS is an explicit cast expression (C-style cast, static_cast, functional cast) to an integer type, as these are allowed by the rule.
6. Exclude cases where the RHS, after ignoring parentheses and implicit casts, is a floating-point or integer literal, as constants are exempt.
7. Ensure the matcher does not exclude other non-literal constant expressions (e.g., const variables) at this stage; these will be handled in the check() callback.
**logic for check**:
1. Retrieve the bound nodes: 'assignOp' (BinaryOperator), 'lhsExpr' (Expr), and 'rhsExpr' (Expr).
2. Validate all retrieved nodes and their source locations are non-null and valid; return if any check fails.
3. Verify the LHS expression type is an integer type; return if not.
4. Strip implicit casts and parentheses from the RHS expression to obtain the core expression ('StrippedRHS').
5. Verify the stripped RHS expression type is a floating-point type; return if not.
6. Check if the RHS expression is value-dependent or type-dependent; return if true to avoid diagnosing template code.
7. Check if the stripped RHS is a floating-point or integer literal; return if true (should be caught by matcher, but double-check).
8. Evaluate if the RHS expression is a constant expression using EvaluateAsConstantExpr; return if true to exempt constants.
9. Also evaluate the stripped RHS expression as a constant expression; return if true.
10. If the stripped RHS is a DeclRefExpr, check if it refers to a const-qualified variable with a constant initializer; return if true.
11. If the stripped RHS is a MemberExpr, check if it refers to a const-qualified field and if the entire RHS expression evaluates to a constant; return if true.
12. If all previous checks pass (i.e., the assignment is a non-constant floating-point expression to an integer variable without an explicit cast), emit a diagnostic at the assignment operator location with the required message.
13. Attach source ranges for the LHS and RHS expressions to the diagnostic for better context.


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

AST Traversal Matcher: hasLHS
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<ArraySubscriptExpr>
 Description: Matches the left hand side of binary operator expressions.

Example matches a (matcher = binaryOperator(hasLHS()))
  a || b

Node Matcher: cStyleCastExpr
 Parameters;Matcher<CStyleCastExpr>...
 return type Matcher<Stmt>
 Description: Matches a C-style cast expression.

Example: Matches (int) 2.2f in
  int i = (int) 2.2f;

Narrowing Matcher: isAssignmentOperator
 Parameters;
 return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches all kinds of assignment operators.

Example 1: matches a += b (matcher = binaryOperator(isAssignmentOperator()))
  if (a == b)
    a += b;

Example 2: matches s1 = s2
           (matcher = cxxOperatorCallExpr(isAssignmentOperator()))
  struct S { S&amp; operator=(const S&amp;); };
  void x() { S s1, s2; s1 = s2; }

Narrowing Matcher: isCopyAssignmentOperator
 Parameters;
 return type Matcher<CXXMethodDecl>
 Description: Matches if the given method declaration declares a copy assignment
operator.

Given
struct A {
  A &amp;operator=(const A &amp;);
  A &amp;operator=(A &amp;&amp;);
};

cxxMethodDecl(isCopyAssignmentOperator()) matches the first method but not
the second one.

Node Matcher: explicitCastExpr
 Parameters;Matcher<ExplicitCastExpr>...
 return type Matcher<Stmt>
 Description: Matches explicit cast expressions.

Matches any cast expression written in user code, whether it be a
C-style cast, a functional-style cast, or a keyword cast.

Does not match implicit conversions.

Note: the name "explicitCast" is chosen to match Clang's terminology, as
Clang uses the term "cast" to apply to implicit conversions as well as to
actual cast expressions.

See also: hasDestinationType.

Example: matches all five of the casts in
  int((int)(reinterpret_cast&lt;int&gt;(static_cast&lt;int&gt;(const_cast&lt;int&gt;(42)))))
but does not match the implicit conversion in
  long ell = 42;

const auto IsGoodAssign = cxxMethodDecl(IsAssign, HasGoodReturnType);
hasLHS(expr())
unless(hasSourceExpression(integerLiteral()))
unless(declRefExpr(to(enumConstantDecl())))
expr(hasType(realFloatingPointType()))
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}


## reference code snippets  
const auto *HandlerDecl = Result.Nodes.getNodeAs<FunctionDecl>("handler_decl");
const auto *HandlerExpr = Result.Nodes.getNodeAs<DeclRefExpr>("handler_expr");
assert(Result.Nodes.getNodeAs<CallExpr>("register_call") && HandlerDecl &&
       HandlerExpr && "All of these should exist in a match here.");
static bool isUsedToInitializeAConstant(const MatchFinder::MatchResult &Result,
                                        const DynTypedNode &Node) {
  const auto *AsDecl = Node.get<DeclaratorDecl>();
  if (AsDecl) {
    if (AsDecl->getType().isConstQualified())
      return true;
    return AsDecl->isImplicit();
  }
  if (Node.get<EnumConstantDecl>())
    return true;
  return llvm::any_of(Result.Context->getParents(Node),
                      [&Result](const DynTypedNode &Parent) {
                        return isUsedToInitializeAConstant(Result, Parent);
                      });
}
const Expr *LHSFrom = ignoreNoOpCasts(LHSCast->getSubExpr());
const Expr *RHSFrom = ignoreNoOpCasts(RHSCast->getSubExpr());
const Expr *RHSE = ArraySubscriptE->getRHS()->IgnoreParenImpCasts();
if (!isa<StringLiteral>(RHSE) && !isa<DeclRefExpr>(RHSE) && !isa<MemberExpr>(RHSE))
  return;
const auto &Node = *Result.Nodes.getNodeAs<BinaryOperator>("outer");
const auto &Inner = *Result.Nodes.getNodeAs<BinaryOperator>("inner");
const StringRef LText = tooling::fixit::getText(ArraySubscriptE->getLHS()->getSourceRange(), *Result.Context);
const StringRef RText = tooling::fixit::getText(ArraySubscriptE->getRHS()->getSourceRange(), *Result.Context);
if (!IgnoreAllFloatingPointValues)
  checkBoundMatch<FloatingLiteral>(Result, "float");
bool CharExpressionDetector::isCharValuedConstant(const Expr *E) const {
  if (E->isInstantiationDependent())
    return false;
  Expr::EvalResult EvalResult;
  if (!E->EvaluateAsInt(EvalResult, Ctx, Expr::SE_AllowSideEffects))
    return false;
  return EvalResult.Val.getInt().getActiveBits() <= Ctx.getTypeSize(CharType);
};
bool isFunctionParameter(const DeclRefExpr *DeclRefExpr) {
  return isa<ParmVarDecl>(DeclRefExpr->getDecl());
}
if (IndexExpr->isValueDependent())
  return;
static APValue getConstantExprValue(const ASTContext &Ctx, const Expr &E) {
  if (auto IntegerConstant = E.getIntegerConstantExpr(Ctx))
    return APValue(*IntegerConstant);
  APValue Constant;
  if (Ctx.getLangOpts().CPlusPlus && E.isCXX11ConstantExpr(Ctx, &Constant))
    return Constant;
  return {};
}
void AssignmentInIfConditionCheck::report(const Expr *AssignmentExpr) {
  SourceLocation OpLoc =
      isa<BinaryOperator>(AssignmentExpr)
          ? cast<BinaryOperator>(AssignmentExpr)->getOperatorLoc()
          : cast<CXXOperatorCallExpr>(AssignmentExpr)->getOperatorLoc();

  diag(OpLoc, "an assignment within an 'if' condition is bug-prone")
      << AssignmentExpr->getSourceRange();
  diag(OpLoc,
       "if it should be an assignment, move it out of the 'if' condition",
       DiagnosticIDs::Note);
  diag(OpLoc, "if it is meant to be an equality check, change '=' to '=='",
       DiagnosticIDs::Note);
}
if (checkBoundMatch<IntegerLiteralCheck>(Result))
  return;
checkBoundMatch<FloatingLiteralCheck>(Result);
bool clang::VarDecl::hasConstantInitialization() const
QualType clang::Expr::findBoundMemberType(const Expr * expr)
bool clang::Expr::isTypeDependent() const
bool clang::BuiltinType::isFloatingPoint() const
bool clang::Preprocessor::parseSimpleIntegerLiteral(Token & Tok, uint64_t & Value)
bool clang::SourceLocation::isValid() const
bool clang::Expr::EvaluateAsConstantExpr(EvalResult & Result, const ASTContext & Ctx, ConstantExprKind Kind) const
PartialDiagnostic & clang::PartialDiagnostic::operator=(PartialDiagnostic && Other)
void clang::StreamingDiagnostic::AddSourceRange(const CharSourceRange & R) const
bool clang::Type::isIntegerType() const
int clang::OMPTaskReductionClause::rhs_exprs()



# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the current checker code above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
    -In the check() function, all extracted nodes must be checked for non-null and isValid() to avoid direct usage

## **Example Output Format:**

    checker_cpp:
    ```cpp
        ....(source code)....
    ```

    checker_h:
    ```cpp
        ....(source code)....
    ```


You can proceed with the analysis according to the following steps:

1.  Read the provided current checker code and analyze its implementation logic.
2.  Analyze the passed test cases code to understand how the checker successfully identifies issues in the code without generating false positives.
3.  Analyze the failed test cases code to determine why the checker fails to detect the issues present in these cases.
4.  Synthesize the findings from the above analyses. When generating the new code, follow the reference logic steps, consult the reference AST matchers, and utilize the reference code snippets to produce a complete and robust checker implementation. This new checker code should be capable of detecting all issues in the test cases while avoiding false positives.
5.  Output the final code strictly adhering to the specified output format requirements.

