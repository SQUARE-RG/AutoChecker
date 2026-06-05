针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition/no_assignment_in_condition_case_7.cpp生成first checker
# Inputs

## rule
**Rule Description:**
Prohibited is the direct use of assignment statements in logical expressions (such as conditional statements like if, while, for), aimed at preventing logical errors caused by mistakenly using the assignment operator (=) instead of the comparison operator (==). When an assignment statement is used in a logical expression, the assignment operation itself returns a value, which is implicitly converted to a boolean value for conditional evaluation. This may cause the conditional evaluation to deviate from the expected logic (such as non-zero values being converted to true, and zero values to false), potentially leading to hard-to-detect program errors. This rule requires that assignment operations must be separated from conditional evaluations, meaning that assignment should be performed first, followed by conditional evaluation using a comparison operator. Compliant scenarios include using only comparison operators (such as ==, !=) in conditions, assigning first and then comparing, or using boolean variables to store the result; non-compliant scenarios involve directly using the assignment operator in conditions (such as if (x = y)), regardless of whether the assignment is combined with a comparison operation.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int main(void) {
    int a = 0, b = 0, c = 5;
    if (a == 0 || (b = c)) {  // 违反：在逻辑或表达式中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("b is %d\n", b);
    }
    return 0;
}
```

## AST
TranslationUnitDecl 0x5654fbbd3f58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5654fbc998f8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition/no_assignment_in_condition_case_7.cpp:3:1, line:10:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5654fbc99f78 <col:16, line:10:1>
    |-DeclStmt 0x5654fbc99ba0 <line:4:5, col:28>
    | |-VarDecl 0x5654fbc999b8 <col:5, col:13> col:9 used a 'int' cinit
    | | `-IntegerLiteral 0x5654fbc99a20 <col:13> 'int' 0
    | |-VarDecl 0x5654fbc99a58 <col:5, col:20> col:16 used b 'int' cinit
    | | `-IntegerLiteral 0x5654fbc99ac0 <col:20> 'int' 0
    | `-VarDecl 0x5654fbc99af8 <col:5, col:27> col:23 used c 'int' cinit
    |   `-IntegerLiteral 0x5654fbc99b60 <col:27> 'int' 5
    |-IfStmt 0x5654fbc99f28 <line:5:5, line:8:5>
    | |-BinaryOperator 0x5654fbc99cf8 <line:5:9, col:25> 'bool' '||'
    | | |-BinaryOperator 0x5654fbc99c10 <col:9, col:14> 'bool' '=='
    | | | |-ImplicitCastExpr 0x5654fbc99bf8 <col:9> 'int' <LValueToRValue>
    | | | | `-DeclRefExpr 0x5654fbc99bb8 <col:9> 'int' lvalue Var 0x5654fbc999b8 'a' 'int'
    | | | `-IntegerLiteral 0x5654fbc99bd8 <col:14> 'int' 0
    | | `-ImplicitCastExpr 0x5654fbc99ce0 <col:19, col:25> 'bool' <IntegralToBoolean>
    | |   `-ImplicitCastExpr 0x5654fbc99cc8 <col:19, col:25> 'int' <LValueToRValue>
    | |     `-ParenExpr 0x5654fbc99ca8 <col:19, col:25> 'int' lvalue
    | |       `-BinaryOperator 0x5654fbc99c88 <col:20, col:24> 'int' lvalue '='
    | |         |-DeclRefExpr 0x5654fbc99c30 <col:20> 'int' lvalue Var 0x5654fbc99a58 'b' 'int'
    | |         `-ImplicitCastExpr 0x5654fbc99c70 <col:24> 'int' <LValueToRValue>
    | |           `-DeclRefExpr 0x5654fbc99c50 <col:24> 'int' lvalue Var 0x5654fbc99af8 'c' 'int'
    | `-CompoundStmt 0x5654fbc99f10 <col:28, line:8:5>
    |   `-CallExpr 0x5654fbc99eb0 <line:7:9, col:30> 'int'
    |     |-ImplicitCastExpr 0x5654fbc99e98 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x5654fbc99e18 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x5654fbc76528 'printf' 'int (const char *__restrict, ...)'
    |     |-ImplicitCastExpr 0x5654fbc99ee0 <col:16> 'const char *' <ArrayToPointerDecay>
    |     | `-StringLiteral 0x5654fbc99dd8 <col:16> 'const char[9]' lvalue "b is %d\n"
    |     `-ImplicitCastExpr 0x5654fbc99ef8 <col:29> 'int' <LValueToRValue>
    |       `-DeclRefExpr 0x5654fbc99df8 <col:29> 'int' lvalue Var 0x5654fbc99a58 'b' 'int'
    `-ReturnStmt 0x5654fbc99f68 <line:9:5, col:12>
      `-IntegerLiteral 0x5654fbc99f48 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match binary operators that are assignment operators (e.g., =, +=, -=, etc.) inside conditional contexts such as if/while/for/do statements
2. Exclude cases where the assignment is part of a declaration (e.g., int x = y;) by ensuring the assignment is an expression statement not a declaration
3. Use hasAncestor() to match assignment operators that are ancestors of control statement conditions (ifStmt, whileStmt, forStmt, doStmt) or logical binary operators (&&, ||) that are part of such conditions
4. Bind the assignment operator node as 'assignment' and the enclosing control statement or logical expression node for diagnostics
**logic for check**:
1. Retrieve the bound assignment operator node (BinaryOperator) from the match result
2. Verify that the assignment is indeed used as a subexpression of a condition in if/while/for/do or logical operator (&&/||)
3. Check that the assignment is not part of a compound assignment with comparison (e.g., x == y) — only plain assignment or compound assignment operators (=, +=, etc.)
4. Emit a diagnostic message at the location of the assignment operator indicating that assignment statements are prohibited in logical expressions
5. Optionally, provide the source range of the assignment for clearer error reporting


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

stmt(anyOf(ifStmt(anyOf(has(declStmt(containsDeclaration(0, varDecl(hasInitializer(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasName("cast")))).bind("assign")))))), hasCondition(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), anyOf(callee(namedDecl(hasName("cast"))), callee(namedDecl(hasName("dyn_cast")).bind("dyn_cast")))).bind("call")))))), whileStmt(anyOf(has(declStmt(containsDeclaration(0, varDecl(hasInitializer(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasName("cast")))).bind("assign")))))), hasCondition(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), anyOf(callee(namedDecl(hasName("cast"))), callee(namedDecl(hasName("dyn_cast")).bind("dyn_cast")))).bind("call")))))), doStmt(hasCondition(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), anyOf(callee(namedDecl(hasName("cast"))), callee(namedDecl(hasName("dyn_cast")).bind("dyn_cast")))).bind("call"))))), binaryOperator(unless(isExpansionInFileMatching("llvm/include/llvm/Support/Casting.h")), hasOperatorName("&&"), hasLHS(implicitCastExpr().bind("lhs")), hasRHS(anyOf(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasAnyName("isa", "cast", "cast_or_null", "dyn_cast", "dyn_cast_or_null")).bind("func")), hasArgument(0, mapAnyOf(declRefExpr, cxxMemberCallExpr).bind("arg"))).bind("rhs"))), callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasAnyName("isa", "cast", "cast_or_null", "dyn_cast", "dyn_cast_or_null")).bind("func")), hasArgument(0, mapAnyOf(declRefExpr, cxxMemberCallExpr).bind("arg"))).bind("rhs")))).bind("and"))))
stmt(anyOf(mapAnyOf(ifStmt, whileStmt, doStmt, forStmt).with(hasCondition(StringCompareCallExpr)), binaryOperator(hasAnyOperatorName("&&", "||"), hasEitherOperand(StringCompareCallExpr)))).bind("missing-comparison")
static bool isConstructorAssignment(const MatchFinder::MatchResult &Result, const Expr *Node) {
  return selectFirst<const Expr>(
             "e",
             match(expr(anyOf(
                       callExpr(hasParent(materializeTemporaryExpr(hasParent(
                                    cxxConstructExpr(hasParent(exprWithCleanups(
                                        hasParent(varDecl()))))))))
                           .bind("e"),
                       callExpr(hasParent(varDecl())).bind("e"))),
                   *Node, *Result.Context)) != nullptr;
}


## reference api
const auto *BinOp = Result.Nodes.getNodeAs<BinaryOperator>("binop");
std::string InverseName =
    Result.Nodes.getNodeAs<FunctionDecl>("func_decl")->getNameAsString();
if (const auto *RetStmt = Result.Nodes.getNodeAs<ReturnStmt>("returnStmt")) {
  diag(RetStmt->getBeginLoc(), "operator=() should always return '*this'");
  return;
}
else if (const auto *B = dyn_cast<BinaryOperator>(S)) {
  if (B->isAssignmentOp())
    markCanNotBeConst(B, false);
}
bool clang::BinaryOperator::isEqualityOp() const
SourceLocation clang::BinaryOperator::getExprLoc() const
SourceLocation clang::BinaryOperator::getOperatorLoc() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoAssignmentInConditionCheck.cpp :
```cpp
//===--- NoAssignmentInConditionCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoAssignmentInConditionCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoAssignmentInConditionCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void NoAssignmentInConditionCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoAssignmentInConditionCheck.h :
```cpp
//===--- NoAssignmentInConditionCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-assignment-in-condition.html
class NoAssignmentInConditionCheck : public ClangTidyCheck {
public:
  NoAssignmentInConditionCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOASSIGNMENTINCONDITIONCHECK_H

```
