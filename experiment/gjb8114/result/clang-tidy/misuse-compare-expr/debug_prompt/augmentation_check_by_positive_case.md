针对正例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_17.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

# Inputs

## rule
**Rule Description:**
In all comparison expressions involving multiple operators that may cause ambiguity due to operator precedence (especially when bitwise operators, arithmetic operators, and comparison operators are mixed), parentheses must​ be used to explicitly define the order of operations and prevent incorrect logical evaluations. This rule specifically targets error-prone combinations, such as mixing bitwise operators (&, |, ^, <<, >>) with comparison operators (==, !=, <, >, <=, >=), or arithmetic operators (+, -, *, /, %) with comparison operators.
A compliant scenario​ occurs when parentheses are used to clearly group operands (e.g., (x & y) == z), thereby eliminating ambiguity. A non-compliant scenario​ arises when parentheses are omitted (e.g., x & y == z). In the latter case, due to the higher precedence of ==over &, the expression is parsed as x & (y == z), which may deviate from the programmer’s intent (e.g., (x & y) == z) and introduce potential logical errors.

## current checker code

checker_cpp:
```cpp
//===--- MisuseCompareExprCheck.cpp - clang-tidy --------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "MisuseCompareExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to check if an expression is already wrapped in parentheses
static bool isWrappedInParens(const Expr *E, const MatchFinder::MatchResult &Result) {
  if (!E || !E->getBeginLoc().isValid() || !E->getEndLoc().isValid())
    return false;
  
  SourceRange ExprRange = E->getSourceRange();
  // Get the character range of the expression
  CharSourceRange CharRange = Lexer::getAsCharRange(
      CharSourceRange::getTokenRange(ExprRange),
      *Result.SourceManager, Result.Context->getLangOpts());
  
  if (!CharRange.isValid())
    return false;
  
  // Check if the expression starts with '(' and ends with ')'
  StringRef Text = Lexer::getSourceText(CharRange, *Result.SourceManager, 
                                        Result.Context->getLangOpts());
  return Text.startswith("(") && Text.endswith(")");
}

void MisuseCompareExprCheck::registerMatchers(MatchFinder *Finder) {
  // Matcher for comparison operators with inner arithmetic/bitwise operators
  auto ComparisonWithInnerOp = binaryOperator(
    anyOf(
      hasOperatorName("=="),
      hasOperatorName("!="),
      hasOperatorName("<"),
      hasOperatorName(">"),
      hasOperatorName("<="),
      hasOperatorName(">=")
    ),
    anyOf(
      // Check left operand
      hasLHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("+"),
            hasOperatorName("-"),
            hasOperatorName("*"),
            hasOperatorName("/"),
            hasOperatorName("%"),
            hasOperatorName("&"),
            hasOperatorName("|"),
            hasOperatorName("^"),
            hasOperatorName("<<"),
            hasOperatorName(">>")
          )
        ).bind("innerOp")
      )),
      // Check right operand
      hasRHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("+"),
            hasOperatorName("-"),
            hasOperatorName("*"),
            hasOperatorName("/"),
            hasOperatorName("%"),
            hasOperatorName("&"),
            hasOperatorName("|"),
            hasOperatorName("^"),
            hasOperatorName("<<"),
            hasOperatorName(">>")
          )
        ).bind("innerOp")
      ))
    )
  ).bind("comparison");
  
  // Matcher for arithmetic/bitwise operators with inner comparison operators
  auto ArithmeticWithInnerCmp = binaryOperator(
    anyOf(
      hasOperatorName("+"),
      hasOperatorName("-"),
      hasOperatorName("*"),
      hasOperatorName("/"),
      hasOperatorName("%"),
      hasOperatorName("&"),
      hasOperatorName("|"),
      hasOperatorName("^"),
      hasOperatorName("<<"),
      hasOperatorName(">>")
    ),
    anyOf(
      // Check left operand
      hasLHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("=="),
            hasOperatorName("!="),
            hasOperatorName("<"),
            hasOperatorName(">"),
            hasOperatorName("<="),
            hasOperatorName(">=")
          )
        ).bind("innerCmp")
      )),
      // Check right operand
      hasRHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("=="),
            hasOperatorName("!="),
            hasOperatorName("<"),
            hasOperatorName(">"),
            hasOperatorName("<="),
            hasOperatorName(">=")
          )
        ).bind("innerCmp")
      ))
    )
  ).bind("outerOp");
  
  // Combine both patterns
  Finder->addMatcher(
    binaryOperator(
      anyOf(ComparisonWithInnerOp, ArithmeticWithInnerCmp)
    ),
    this
  );
}

void MisuseCompareExprCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Ctx = Result.Context;
  
  // Check for first pattern: comparison with inner arithmetic/bitwise operator
  if (const auto *InnerOp = Result.Nodes.getNodeAs<BinaryOperator>("innerOp")) {
    if (!InnerOp || !InnerOp->getOperatorLoc().isValid())
      return;
    
    // Skip if already wrapped in parentheses
    if (isWrappedInParens(InnerOp, Result))
      return;
    
    const auto *Comparison = Result.Nodes.getNodeAs<BinaryOperator>("comparison");
    if (!Comparison || !Comparison->getOperatorLoc().isValid())
      return;
    
    // Check if the inner operator is directly inside the comparison without parentheses
    // We need to verify that the inner operator is indeed a direct child of the comparison
    // after ignoring parentheses and implicit casts
    bool IsDirectChild = false;
    if (Comparison->getLHS()->IgnoreParenImpCasts() == InnerOp ||
        Comparison->getRHS()->IgnoreParenImpCasts() == InnerOp) {
      IsDirectChild = true;
    }
    
    if (!IsDirectChild)
      return;
    
    // Construct diagnostic message
    diag(InnerOp->getOperatorLoc(),
         "禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]")
        << FixItHint::CreateInsertion(InnerOp->getBeginLoc(), "(")
        << FixItHint::CreateInsertion(
             Lexer::getLocForEndOfToken(InnerOp->getEndLoc(), 0, 
                                       *Result.SourceManager, Ctx->getLangOpts()),
             ")");
    return;
  }
  
  // Check for second pattern: arithmetic/bitwise with inner comparison operator
  if (const auto *InnerCmp = Result.Nodes.getNodeAs<BinaryOperator>("innerCmp")) {
    if (!InnerCmp || !InnerCmp->getOperatorLoc().isValid())
      return;
    
    // Skip if already wrapped in parentheses
    if (isWrappedInParens(InnerCmp, Result))
      return;
    
    const auto *OuterOp = Result.Nodes.getNodeAs<BinaryOperator>("outerOp");
    if (!OuterOp || !OuterOp->getOperatorLoc().isValid())
      return;
    
    // Check if the inner comparison is directly inside the outer operator without parentheses
    // We need to verify that the inner comparison is indeed a direct child of the outer operator
    // after ignoring parentheses and implicit casts
    bool IsDirectChild = false;
    if (OuterOp->getLHS()->IgnoreParenImpCasts() == InnerCmp ||
        OuterOp->getRHS()->IgnoreParenImpCasts() == InnerCmp) {
      IsDirectChild = true;
    }
    
    if (!IsDirectChild)
      return;
    
    // Construct diagnostic message
    diag(InnerCmp->getOperatorLoc(),
         "禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]")
        << FixItHint::CreateInsertion(InnerCmp->getBeginLoc(), "(")
        << FixItHint::CreateInsertion(
             Lexer::getLocForEndOfToken(InnerCmp->getEndLoc(), 0, 
                                       *Result.SourceManager, Ctx->getLangOpts()),
             ")");
    return;
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- MisuseCompareExprCheck.h - clang-tidy ------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// In all comparison expressions involving multiple operators that may cause ambiguity
/// due to operator precedence (especially when bitwise operators, arithmetic operators,
/// and comparison operators are mixed), parentheses must be used to explicitly define
/// the order of operations and prevent incorrect logical evaluations.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/misuse-compare-expr.html
class MisuseCompareExprCheck : public ClangTidyCheck {
public:
  MisuseCompareExprCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_MISUSECOMPAREEXPRCHECK_H
```

## passed test cases code

```cpp
#include <stdio.h>

int main(void) {
    int number = 7, mod = 3, expected = 1;
    if (number % mod == expected) {  // 违反：取模和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Remainder is as expected\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int x = 5, y = 3, z = 1;
    if (x & y == z) {  // 违反：位与和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int total = 100, divisor = 5, max_quotient = 25;
    if (total / divisor <= max_quotient) {  // 违反：除法和小于等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Quotient is within limit\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int a = 20, b = 10, result = 5;
    if (a - b != result) {  // 违反：减法和不等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Difference is not equal\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int value = 2, threshold = 10;
    if (value << 2 > threshold) {  // 违反：左移和大于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Value exceeds threshold\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int p = 10, q = 5, r = 15;
    if (p ^ q != r) {  // 违反：异或和不等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int a = 6, b = 2, c = 2;
    if (a | b == c) {  // 违反：位或和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int width = 5, height = 3, area_limit = 20;
    if (width * height >= area_limit) {  // 违反：乘法和大于等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Area meets or exceeds limit\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int num = 16, limit = 5;
    if (num >> 1 < limit) {  // 违反：右移和小于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Within limit\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int x = 10, y = 5, z = 3, w = 12;
    if ((x + y) > (z - w)) {  // 符合：多重算术运算使用括号明确优先级
        printf("Comparison is valid\n");
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int x = 3, y = 4, sum = 7;
    if (x + y == sum) {  // 违反：加法和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Sum is correct\n");
    }
    return 0;
}
```

## failed test cases code
This test case should not report an issue, but the current checker code reports an issue in the code, which is a false positive.
```cpp
#include <stdio.h>

int main(void) {
    int a = 20, b = 10, result = 5;
    if ((a - b) != result) {  // 符合：使用括号明确优先级
        printf("Difference is not equal\n");
    }
    return 0;
}
```

### ast of  failed test cases 
TranslationUnitDecl 0x56418a5d6fe8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x56418a69c7b8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_17.cpp:3:1, line:9:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x56418a69cdb8 <col:16, line:9:1>
    |-DeclStmt 0x56418a69ca60 <line:4:5, col:35>
    | |-VarDecl 0x56418a69c878 <col:5, col:13> col:9 used a 'int' cinit
    | | `-IntegerLiteral 0x56418a69c8e0 <col:13> 'int' 20
    | |-VarDecl 0x56418a69c918 <col:5, col:21> col:17 used b 'int' cinit
    | | `-IntegerLiteral 0x56418a69c980 <col:21> 'int' 10
    | `-VarDecl 0x56418a69c9b8 <col:5, col:34> col:25 used result 'int' cinit
    |   `-IntegerLiteral 0x56418a69ca20 <col:34> 'int' 5
    |-IfStmt 0x56418a69cd68 <line:5:5, line:7:5>
    | |-BinaryOperator 0x56418a69cb60 <line:5:9, col:20> 'bool' '!='
    | | |-ParenExpr 0x56418a69cb08 <col:9, col:15> 'int'
    | | | `-BinaryOperator 0x56418a69cae8 <col:10, col:14> 'int' '-'
    | | |   |-ImplicitCastExpr 0x56418a69cab8 <col:10> 'int' <LValueToRValue>
    | | |   | `-DeclRefExpr 0x56418a69ca78 <col:10> 'int' lvalue Var 0x56418a69c878 'a' 'int'
    | | |   `-ImplicitCastExpr 0x56418a69cad0 <col:14> 'int' <LValueToRValue>
    | | |     `-DeclRefExpr 0x56418a69ca98 <col:14> 'int' lvalue Var 0x56418a69c918 'b' 'int'
    | | `-ImplicitCastExpr 0x56418a69cb48 <col:20> 'int' <LValueToRValue>
    | |   `-DeclRefExpr 0x56418a69cb28 <col:20> 'int' lvalue Var 0x56418a69c9b8 'result' 'int'
    | `-CompoundStmt 0x56418a69cd50 <col:28, line:7:5>
    |   `-CallExpr 0x56418a69cd10 <line:6:9, col:43> 'int'
    |     |-ImplicitCastExpr 0x56418a69ccf8 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x56418a69cc78 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x56418a6793e8 'printf' 'int (const char *__restrict, ...)'
    |     `-ImplicitCastExpr 0x56418a69cd38 <col:16> 'const char *' <ArrayToPointerDecay>
    |       `-StringLiteral 0x56418a69cc48 <col:16> 'const char[25]' lvalue "Difference is not equal\n"
    `-ReturnStmt 0x56418a69cda8 <line:8:5, col:12>
      `-IntegerLiteral 0x56418a69cd88 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Define two primary matcher patterns: comparison operators containing arithmetic/bitwise operators, and arithmetic/bitwise operators containing comparison operators
2. For comparison operators (==, !=, <, >, <=, >=), match when either left or right operand contains arithmetic/bitwise operators (+, -, *, /, %, &, |, ^, <<, >>)
3. For arithmetic/bitwise operators, match when either left or right operand contains comparison operators
4. Use ignoringParenImpCasts to skip parentheses and implicit casts when checking operands
5. Bind the inner operator as 'innerOp' for the first pattern and 'innerCmp' for the second pattern
6. Bind the outer comparison operator as 'comparison' and outer arithmetic/bitwise operator as 'outerOp'
7. Combine both patterns using anyOf to match either scenario
**logic for check**:
1. Retrieve the AST context from the match result
2. Check if the match corresponds to the first pattern by attempting to get the 'innerOp' node
3. If 'innerOp' exists, validate it has a valid operator location
4. Use the helper function isWrappedInParens to check if the inner operator is already parenthesized
5. Retrieve the outer 'comparison' node and validate it
6. Verify the inner operator is a direct child of the comparison by comparing IgnoreParenImpCasts() results
7. If all conditions are met, emit a diagnostic at the inner operator's location
8. Otherwise, check if the match corresponds to the second pattern by attempting to get the 'innerCmp' node
9. If 'innerCmp' exists, validate it has a valid operator location
10. Check if the inner comparison is already parenthesized using isWrappedInParens
11. Retrieve the outer 'outerOp' node and validate it
12. Verify the inner comparison is a direct child of the outer operator by comparing IgnoreParenImpCasts() results
13. If all conditions are met, emit a diagnostic at the inner comparison's location


## reference astMatchers
AST Traversal Matcher: hasEitherOperand
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<BinaryOperator>
 Description: Matches if either the left hand side or the right hand side of a
binary operator matches.

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

Narrowing Matcher: mapAnyOf
 Parameters;nodeMatcherFunction...
 return type unspecified
 Description: Matches any of the NodeMatchers with InnerMatchers nested within

Given
  if (true);
  for (; true; );
with the matcher
  mapAnyOf(ifStmt, forStmt).with(
    hasCondition(cxxBoolLiteralExpr(equals(true)))
    ).bind("trueCond")
matches the if and the for. It is equivalent to:
  auto trueCond = hasCondition(cxxBoolLiteralExpr(equals(true)));
  anyOf(
    ifStmt(trueCond).bind("trueCond"),
    forStmt(trueCond).bind("trueCond")
    );

The with() chain-call accepts zero or more matchers which are combined
as-if with allOf() in each of the node matchers.
Usable as: Any Matcher

Narrowing Matcher: isComparisonOperator
 Parameters;
 return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches comparison operators.

Example 1: matches a == b (matcher = binaryOperator(isComparisonOperator()))
  if (a == b)
    a += b;

Example 2: matches s1 &lt; s2
           (matcher = cxxOperatorCallExpr(isComparisonOperator()))
  struct S { bool operator&lt;(const S&amp; other); };
  void x(S s1, S s2) { bool b1 = s1 &lt; s2; }

AST Traversal Matcher: forDecomposition
 Parameters;Matcher<ValueDecl> InnerMatcher
 Return type Matcher<BindingDecl>
 Description: Matches the DecompositionDecl the binding belongs to.

For example, in:
void foo()
{
    int arr[3];
    auto &amp;[f, s, t] = arr;

    f = 42;
}
The matcher:
  bindingDecl(hasName("f"),
                forDecomposition(decompositionDecl())
matches 'f' in 'auto &amp;[f, s, t]'.

Narrowing Matcher: anyOf
 Parameters;Matcher<*>, ..., Matcher<*>
 return type Matcher<*>
 Description: Matches if any of the given matchers matches.

Usable as: Any Matcher

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

ignoringParenImpCasts()
binaryOperator(isComparisonOperator())
binaryOperator(hasLHS(expr(anyOf(cxxNewExpr(mayThrow()).bind("new1"), hasDescendant(cxxNewExpr(mayThrow()).bind("new1"))))), hasRHS(expr(anyOf(cxxNewExpr(mayThrow()).bind("new2"), hasDescendant(cxxNewExpr(mayThrow()).bind("new2"))))), unless(hasAnyOperatorName("&&", "||", ",")), hasAncestor(cxxTryStmt(hasHandlerFor(qualType(hasCanonicalType(anyOf(recordType(hasDeclaration(cxxRecordDecl(hasName("::std::bad_alloc")))), referenceType(pointee(recordType(hasDeclaration(cxxRecordDecl(hasName("::std::bad_alloc")))))), recordType(hasDeclaration(cxxRecordDecl(hasName("::std::exception")))), referenceType(pointee(recordType(hasDeclaration(cxxRecordDecl(hasName("::std::exception"))))))))))))
binaryOperator(hasAnyOperatorName("&&", "||"), hasEitherOperand(declRefExpr(hasDeclaration(varDecl(equalsBoundNode(CondVarStr)))).bind(InnerIfVar2Str)))
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")
expr().bind("expr")


## reference code snippets  
const auto *Inner = Result.Nodes.getNodeAs<Expr>("inner");
const auto *Outer = Result.Nodes.getNodeAs<Stmt>("outer");
if (!Inner || !Outer)
  return;
checkBoundMatch<IntegerLiteral>(Result, "integer");
const auto *LocalScope = Result.Nodes.getNodeAs<CompoundStmt>("scope");
const auto *Variable = Result.Nodes.getNodeAs<VarDecl>("local-value");
const auto *Function = Result.Nodes.getNodeAs<FunctionDecl>("function-decl");
const auto *VarDeclStmt = Result.Nodes.getNodeAs<DeclStmt>("decl-stmt");
SourceLocation ReceiverLoc = Message->getReceiverRange().getBegin();
if (ReceiverLoc.isMacroID() || ReceiverLoc.isInvalid())
  return;
const auto *LHSCast = dyn_cast<ImplicitCastExpr>(ignoreNoOpCasts(LHS));
const auto *RHSCast = dyn_cast<ImplicitCastExpr>(ignoreNoOpCasts(RHS));

if (!LHSCast || !RHSCast || !isImplicitCastCandidate(LHSCast) ||
    !isImplicitCastCandidate(RHSCast))
  continue;
bool IsUnary = false;
SourceLocation OperatorLoc;
if (const auto *UnaryOp = N.getNodeAs<UnaryOperator>("unary-signed")) {
  IsUnary = true;
  OperatorLoc = UnaryOp->getOperatorLoc();
}
TraversalKindScope RAII(*Ctx, TK_AsIs);
auto Parents = Ctx->getParents(*Lit);
if (Parents.size() == 1 && Parents[0].get<ParenExpr>() != nullptr)
  return true;
const auto *Expression = Result.Nodes.getNodeAs<Expr>("expr");
assert(Expression);
assert(isa<DeclRefExpr>(Expression) || isa<CallExpr>(Expression));
if (ConditionValue == CVK_True)
  Check.diag(Loc, "preprocessor condition is always 'true', consider "
                    "removing condition but leaving its contents");
else
  Check.diag(Loc, "preprocessor condition is always 'false', consider "
                    "removing both the condition and its contents");
const auto *OuterCall = Result.Nodes.getNodeAs<CallExpr>("outer_call");
void clang::PartialDiagnostic::Emit(const DiagnosticBuilder & DB) const
bool clang::SourceLocation::isValid() const
const Stmt * clang::ParentMap::getParentIgnoreParenCasts(const Stmt * S) const
bool llvm::omp::OMPContext::matchesISATrait(StringRef) const
bool clang::Capture::isNested() const
interp::Context & clang::ASTContext::getInterpContext()
bool clang::ObjCEncOptions::IsOutermostType() const
const ValueInfo * clang::ComparisonCategoryInfo::getEqualOrEquiv() const
bool clang::MethodVFTableLocation::operator<(const MethodVFTableLocation & other) const
bool clang::TargetOMPContext::matchesISATrait(StringRef RawString) const
bool clang::UnaryOperator::isPostfix() const



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
3.  Analyze why the current checker code is incorrectly reporting failed test cases, as the code in the failed test cases is correct and should not be reported.
4.  Synthesize the findings from the above analyses. When generating the new code, follow the reference logic steps, consult the reference AST matchers, and utilize the reference code snippets to produce a complete and robust checker implementation. This new checker code should be capable of detecting all issues in the test cases while avoiding false positives.
5.  Output the final code strictly adhering to the specified output format requirements.

