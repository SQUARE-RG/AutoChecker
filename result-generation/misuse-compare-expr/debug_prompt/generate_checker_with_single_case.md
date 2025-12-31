针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_10.cpp生成first checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.
Your task is to generate a complete, compilable clang-tidy checker by integrating:

* the rule description
* the test case code
* the AST information
* the reference logic steps
* the reference ASTMatchers
* the reference API usage
* and the checker template code

Your output must fully implement the new checker by modifying the provided template without altering namespaces.

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
TranslationUnitDecl 0x560997dfbfe8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x560997ec1838 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr/misuse_compare_expr_case_10.cpp:3:1, line:10:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x560997ec1e18 <col:16, line:10:1>
    |-DeclStmt 0x560997ec1ae0 <line:4:5, col:42>
    | |-VarDecl 0x560997ec18f8 <col:5, col:18> col:9 used number 'int' cinit
    | | `-IntegerLiteral 0x560997ec1960 <col:18> 'int' 7
    | |-VarDecl 0x560997ec1998 <col:5, col:27> col:21 used mod 'int' cinit
    | | `-IntegerLiteral 0x560997ec1a00 <col:27> 'int' 3
    | `-VarDecl 0x560997ec1a38 <col:5, col:41> col:30 used expected 'int' cinit
    |   `-IntegerLiteral 0x560997ec1aa0 <col:41> 'int' 1
    |-IfStmt 0x560997ec1dc8 <line:5:5, line:8:5>
    | |-BinaryOperator 0x560997ec1bc0 <line:5:9, col:25> 'bool' '=='
    | | |-BinaryOperator 0x560997ec1b68 <col:9, col:18> 'int' '%'
    | | | |-ImplicitCastExpr 0x560997ec1b38 <col:9> 'int' <LValueToRValue>
    | | | | `-DeclRefExpr 0x560997ec1af8 <col:9> 'int' lvalue Var 0x560997ec18f8 'number' 'int'
    | | | `-ImplicitCastExpr 0x560997ec1b50 <col:18> 'int' <LValueToRValue>
    | | |   `-DeclRefExpr 0x560997ec1b18 <col:18> 'int' lvalue Var 0x560997ec1998 'mod' 'int'
    | | `-ImplicitCastExpr 0x560997ec1ba8 <col:25> 'int' <LValueToRValue>
    | |   `-DeclRefExpr 0x560997ec1b88 <col:25> 'int' lvalue Var 0x560997ec1a38 'expected' 'int'
    | `-CompoundStmt 0x560997ec1db0 <col:35, line:8:5>
    |   `-CallExpr 0x560997ec1d70 <line:7:9, col:44> 'int'
    |     |-ImplicitCastExpr 0x560997ec1d58 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x560997ec1ce0 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x560997e9e468 'printf' 'int (const char *__restrict, ...)'
    |     `-ImplicitCastExpr 0x560997ec1d98 <col:16> 'const char *' <ArrayToPointerDecay>
    |       `-StringLiteral 0x560997ec1ca8 <col:16> 'const char[26]' lvalue "Remainder is as expected\n"
    `-ReturnStmt 0x560997ec1e08 <line:9:5, col:12>
      `-IntegerLiteral 0x560997ec1de8 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for binary operators that are comparison operators (==, !=, <, >, <=, >=) and bind them as 'comparison'
2. Within the comparison operator matcher, traverse the AST to find any direct child binary operators that are arithmetic (+, -, *, /, %) or bitwise (&, |, ^, <<, >>) operators, binding them as 'innerOp'
3. Ensure the 'innerOp' is not already wrapped in parentheses by checking its source range against its parent's source range, binding the problematic 'innerOp' node
4. Create an alternative matcher for binary operators that are arithmetic or bitwise operators, binding them as 'outerOp'
5. Within the 'outerOp' matcher, traverse the AST to find any direct child binary operators that are comparison operators, binding them as 'innerCmp'
6. Ensure the 'innerCmp' is not already wrapped in parentheses by checking its source range against its parent's source range, binding the problematic 'innerCmp' node
7. Combine both matcher patterns (comparison-with-inner-arithmetic/bitwise and arithmetic/bitwise-with-inner-comparison) into a single top-level matcher using `anyOf`
**logic for check**:
1. Retrieve the bound 'innerOp' or 'innerCmp' node from the match result, depending on which pattern matched
2. Determine the type of the inner operator (arithmetic or bitwise) and the outer operator (comparison or arithmetic/bitwise) from the matched nodes
3. Construct a diagnostic message describing the ambiguous operator precedence between the inner and outer operators
4. Emit a diagnostic at the location of the inner operator, indicating that parentheses are required to clarify the intended order of operations


## reference astMatchers
AST Traversal Matcher: hasEitherOperand
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches if either the left hand side or the right hand side of a
binary operator matches.

AST Traversal Matcher: hasAnyUsingShadowDecl
 Parameters;Matcher<UsingShadowDecl> InnerMatcher
 Return type Matcher<BaseUsingDecl>
 Description: Matches any using shadow declaration.

Given
  namespace X { void b(); }
  using X::b;
usingDecl(hasAnyUsingShadowDecl(hasName("b"))))
  matches using X::b

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

Narrowing Matcher: memberHasSameNameAsBoundNode
 Parameters;std::string BindingID
 return type Matcher<CXXDependentScopeMemberExpr>
 Description: Matches template-dependent, but known, member names against an already-bound
node

In template declarations, dependent members are not resolved and so can
not be matched to particular named declarations.

This matcher allows to match on the name of already-bound VarDecl, FieldDecl
and CXXMethodDecl nodes.

Given
  template &lt;typename T&gt;
  struct S {
      void mem();
  };
  template &lt;typename T&gt;
  void x() {
      S&lt;T&gt; s;
      s.mem();
  }
The matcher
@code
cxxDependentScopeMemberExpr(
  hasObjectExpression(declRefExpr(hasType(templateSpecializationType(
      hasDeclaration(classTemplateDecl(has(cxxRecordDecl(has(
          cxxMethodDecl(hasName("mem")).bind("templMem")
          )))))
      )))),
  memberHasSameNameAsBoundNode("templMem")
  )
@endcode
first matches and binds the @c mem member of the @c S template, then
compares its name to the usage in @c s.mem() in the @c x function template

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

hasEitherOperand(...)
static bool insideMacroDefinition(const MatchFinder::MatchResult &Result, SourceRange Range) {
  return !clang::Lexer::makeFileCharRange(
              clang::CharSourceRange::getCharRange(Range),
              *Result.SourceManager, Result.Context->getLangOpts())
              .isValid();
}
binaryOperator(isComparisonOperator())
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")


## reference api  
auto Diag = diag(ArraySubscriptE->getBeginLoc(), "confusing array subscript expression, usually the index is inside the []");
if (const auto *BinOp = Result.Nodes.getNodeAs<BinaryOperator>("binary")) {
  if (areSidesBinaryConstExpressions(BinOp, Result.Context)) {
    const Expr *LhsConst = nullptr, *RhsConst = nullptr;
    BinaryOperatorKind MainOpcode, SideOpcode;
    if (!retrieveConstExprFromBothSides(BinOp, MainOpcode, SideOpcode, LhsConst, RhsConst, Result.Context))
      return;
    if (areExprsFromDifferentMacros(LhsConst, RhsConst, Result.Context) ||
        areExprsMacroAndNonMacro(LhsConst, RhsConst))
      return;
  }
  diag(BinOp->getOperatorLoc(), "both sides of operator are equivalent");
}
const auto *Inner = Result.Nodes.getNodeAs<Expr>("inner");
const auto *Outer = Result.Nodes.getNodeAs<Stmt>("outer");
if (!Inner || !Outer)
  return;
diag(Alloc->getBeginLoc(),
     "addition operator is applied to the argument of %0 instead of its "
     "result")
    << StrLen->getDirectCallee()->getName() << Hint;
bool clang::BinaryOperator::isBitwiseOp() const
OptionalDiagnostic & clang::OptionalDiagnostic::operator<<(const llvm::APFixedPoint & FX)
const CapturedStmt * clang::OMPChildren::getInnermostCapturedStmt(int CaptureRegions) const


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

# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
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