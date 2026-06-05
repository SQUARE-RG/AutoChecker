针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_10.cpp生成first checker
# Inputs

## rule
**Rule Description:**
In all comparison expressions involving multiple operators that may cause ambiguity due to operator precedence (especially when bitwise operators, arithmetic operators, and comparison operators are mixed), parentheses must​ be used to explicitly define the order of operations and prevent incorrect logical evaluations. This rule specifically targets error-prone combinations, such as mixing bitwise operators (&, |, ^, <<, >>) with comparison operators (==, !=, <, >, <=, >=), or arithmetic operators (+, -, *, /, %) with comparison operators.
A compliant scenario​ occurs when parentheses are used to clearly group operands (e.g., (x & y) == z), thereby eliminating ambiguity. A non-compliant scenario​ arises when parentheses are omitted (e.g., x & y == z). In the latter case, due to the higher precedence of ==over &, the expression is parsed as x & (y == z), which may deviate from the programmer’s intent (e.g., (x & y) == z) and introduce potential logical errors.

## test case code
**Test Case Code:**
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
```

## AST
TranslationUnitDecl 0x5650c2a57fe8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5650c2b1d838 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_10.cpp:3:1, line:10:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5650c2b1de18 <col:16, line:10:1>
    |-DeclStmt 0x5650c2b1dae0 <line:4:5, col:42>
    | |-VarDecl 0x5650c2b1d8f8 <col:5, col:18> col:9 used number 'int' cinit
    | | `-IntegerLiteral 0x5650c2b1d960 <col:18> 'int' 7
    | |-VarDecl 0x5650c2b1d998 <col:5, col:27> col:21 used mod 'int' cinit
    | | `-IntegerLiteral 0x5650c2b1da00 <col:27> 'int' 3
    | `-VarDecl 0x5650c2b1da38 <col:5, col:41> col:30 used expected 'int' cinit
    |   `-IntegerLiteral 0x5650c2b1daa0 <col:41> 'int' 1
    |-IfStmt 0x5650c2b1ddc8 <line:5:5, line:8:5>
    | |-BinaryOperator 0x5650c2b1dbc0 <line:5:9, col:25> 'bool' '=='
    | | |-BinaryOperator 0x5650c2b1db68 <col:9, col:18> 'int' '%'
    | | | |-ImplicitCastExpr 0x5650c2b1db38 <col:9> 'int' <LValueToRValue>
    | | | | `-DeclRefExpr 0x5650c2b1daf8 <col:9> 'int' lvalue Var 0x5650c2b1d8f8 'number' 'int'
    | | | `-ImplicitCastExpr 0x5650c2b1db50 <col:18> 'int' <LValueToRValue>
    | | |   `-DeclRefExpr 0x5650c2b1db18 <col:18> 'int' lvalue Var 0x5650c2b1d998 'mod' 'int'
    | | `-ImplicitCastExpr 0x5650c2b1dba8 <col:25> 'int' <LValueToRValue>
    | |   `-DeclRefExpr 0x5650c2b1db88 <col:25> 'int' lvalue Var 0x5650c2b1da38 'expected' 'int'
    | `-CompoundStmt 0x5650c2b1ddb0 <col:35, line:8:5>
    |   `-CallExpr 0x5650c2b1dd70 <line:7:9, col:44> 'int'
    |     |-ImplicitCastExpr 0x5650c2b1dd58 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x5650c2b1dce0 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x5650c2afa468 'printf' 'int (const char *__restrict, ...)'
    |     `-ImplicitCastExpr 0x5650c2b1dd98 <col:16> 'const char *' <ArrayToPointerDecay>
    |       `-StringLiteral 0x5650c2b1dca8 <col:16> 'const char[26]' lvalue "Remainder is as expected\n"
    `-ReturnStmt 0x5650c2b1de08 <line:9:5, col:12>
      `-IntegerLiteral 0x5650c2b1dde8 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match binary operators that are comparison operators (==, !=, <, >, <=, >=) and bind the operator as 'binaryOp'
2. For each matched binary comparison operator, check if either the left-hand side (LHS) or right-hand side (RHS) is a binary operator with lower precedence than comparison operators, specifically bitwise operators (&, |, ^, <<, >>) or arithmetic operators (+, -, *, /, %)
3. Use the 'hasEitherOperand' matcher combined with 'binaryOperator' to match when a comparison operator has a bitwise or arithmetic operator as a direct child operand
4. Ensure the matched sub-expression (bitwise or arithmetic operator) is not wrapped in parentheses by using the 'unless(hasParent(parenExpr()))' matcher
5. Bind the problematic sub-expression (the bitwise or arithmetic operator lacking parentheses) as 'innerOp' for diagnostic reporting
6. Combine these matchers into a single 'binaryOperation' matcher that triggers when a comparison operator has an unparenthesized lower-precedence operator as an operand
**logic for check**:
1. Retrieve the bound comparison binary operator ('binaryOp') from the match result
2. Retrieve the bound inner operator ('innerOp') that lacks parentheses
3. Determine the source location of the comparison operator to report the diagnostic at the correct position
4. Emit a diagnostic message indicating that parentheses are required for the operation to avoid ambiguity in the comparison expression
5. Report the diagnostic at the location of the comparison operator with the appropriate severity level


## reference astMatchers
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

binaryOperator(unless(isExpansionInFileMatching("llvm/include/llvm/Support/Casting.h")), hasOperatorName("&&"), hasLHS(implicitCastExpr().bind("lhs")), hasRHS(anyOf(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasAnyName("isa", "cast", "cast_or_null", "dyn_cast", "dyn_cast_or_null")).bind("func")), hasArgument(0, mapAnyOf(declRefExpr, cxxMemberCallExpr).bind("arg"))).bind("rhs"))), callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasAnyName("isa", "cast", "cast_or_null", "dyn_cast", "dyn_cast_or_null")).bind("func")), hasArgument(0, mapAnyOf(declRefExpr, cxxMemberCallExpr).bind("arg"))).bind("rhs")))).bind("and")
binaryOperator(
  anyOf(isComparisonOperator(),
        hasAnyOperatorName("-", "/", "%", "|", "&", "^", "&&",
                           "||", "=")),
  operandsAreEquivalent(),
  unless(isInTemplateInstantiation()),
  unless(binaryOperatorIsInMacro()),
  unless(hasType(realFloatingPointType())),
  unless(hasEitherOperand(hasType(realFloatingPointType()))),
  unless(hasLHS(anyOf(cxxBoolLiteral(), characterLiteral(), integerLiteral()))),
  unless(hasDescendant(integerLiteral(expandedByMacro(KnownBannedMacroNames)))),
  unless(hasAncestor(expr(isRequiresExpr()))))
  .bind("binary")
binaryOperator(
  hasAnyOperatorName("|", "&", "||", "&&", "^"),
  nestedOperandsAreEquivalent(),
  unless(isInTemplateInstantiation()),
  unless(binaryOperatorIsInMacro()),
  unless(hasDescendant(integerLiteral(expandedByMacro(KnownBannedMacroNames)))),
  unless(hasAncestor(expr(isRequiresExpr()))))
  .bind("nested-duplicates")


## reference api
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
const Expr *BaseExpr = MemberExpression->getBase();
if (isa<CXXOperatorCallExpr>(BaseExpr))
  return;
Opcode clang::BinaryOperator::negateComparisonOp(Opcode Opc)
bool clang::BinaryOperator::isComparisonOp() const
Opcode clang::BinaryOperator::getOpForCompoundAssignment(Opcode Opc)


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/MisuseCompareExprCheck.cpp :
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

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void MisuseCompareExprCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void MisuseCompareExprCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/MisuseCompareExprCheck.h :
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

/// FIXME: Write a short description.
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
