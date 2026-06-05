针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_else_branch/no_else_branch_case_5.cpp生成first checker
# Inputs

## rule
**Rule Description:**
Prohibit omitting the else branch of if-else if statements. In all if-else if statement structures, the final else branch must be included, even if it does not perform any operations, and must be explicitly written. This is to ensure the logical integrity of the code and prevent undefined behavior due to omitted conditions. This rule applies to any conditional statement chain that contains one or more else if branches; the final else branch must exist to handle all uncovered condition scenarios. If the else branch is empty, it should include appropriate comments (e.g.,  Other cases not handled ). Compliant scenarios include if-else if statements that contain an else branch (whether empty or not), while non-compliant scenarios involve omitting the final else branch. The rule checks the structural integrity of conditional statements, not whether the else branch contains specific logic.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int calculate_level(int value) {
    int level;
    if (value > 100) {
        level = 3;
    } else if (value > 50) {
        level = 2;
    } else if (value > 10) {
        level = 1;
    }
    level = 0;  // 违反：赋值语句代替else分支
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
    return level;
}

int main(void) {
    printf("%d\n", calculate_level(75));
    return 0;
}
```

## AST
TranslationUnitDecl 0x562137b2bf48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x562137bf1ba8 <line:17:1, line:20:1> line:17:5 main 'int ()'
  `-CompoundStmt 0x562137bf1ef8 <col:16, line:20:1>
    |-CallExpr 0x562137bf1e80 <line:18:5, col:39> 'int'
    | |-ImplicitCastExpr 0x562137bf1e68 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x562137bf1de8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x562137bce1b8 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x562137bf1eb0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x562137bf1cd8 <col:12> 'const char[4]' lvalue "%d\n"
    | `-CallExpr 0x562137bf1dc0 <col:20, col:38> 'int'
    |   |-ImplicitCastExpr 0x562137bf1da8 <col:20> 'int (*)(int)' <FunctionToPointerDecay>
    |   | `-DeclRefExpr 0x562137bf1d60 <col:20> 'int (int)' lvalue Function 0x562137bf1598 'calculate_level' 'int (int)'
    |   `-IntegerLiteral 0x562137bf1d40 <col:36> 'int' 75
    `-ReturnStmt 0x562137bf1ee8 <line:19:5, col:12>
      `-IntegerLiteral 0x562137bf1ec8 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match IfStmt nodes that have an 'else' child which is also an IfStmt, representing an 'else if' chain.
2. For each such IfStmt, traverse down the chain of 'else if' branches to find the innermost IfStmt.
3. Check if the innermost IfStmt lacks an 'else' branch (i.e., its else() is nullptr).
4. Bind the innermost IfStmt as 'last_if' for diagnostic reporting.
5. Optionally, use hasAncestor() to ensure the match is within a function body, but this is not strictly necessary as the matcher will naturally only apply to statements in functions.
6. Use anyOf() to match chains of any length: a single else-if or multiple nested else-if constructs.
7. Ensure the matcher does not trigger on simple if-else statements (where else is not an IfStmt).
**logic for check**:
1. Retrieve the bound IfStmt node ('last_if') from the match result.
2. Check if the IfStmt has no else branch (getElse() returns nullptr).
3. If no else branch exists, emit a diagnostic message at the location of the 'if' keyword of the last else-if statement.
4. The diagnostic should clearly state that the final else branch is missing and must be included.
5. No fix-it generation should be included in this check.


## reference astMatchers
AST Traversal Matcher: hasAnyBody
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<FunctionDecl>
 Description: Matches a function declaration that has a given body present in the AST.
Note that this matcher matches all the declarations of a function whose
body is present in the AST.

Given
  void f();
  void f() {}
  void g();
functionDecl(hasAnyBody(compoundStmt()))
  matches both 'void f();'
  and 'void f() {}'
with compoundStmt()
  matching '{}'
  but does not match 'void g();'

AST Traversal Matcher: hasBody
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<FunctionDecl>
 Description: Matches a 'for', 'while', 'while' statement or a function or coroutine
definition that has a given body. Note that in case of functions or
coroutines this matcher only matches the definition itself and not the
other declarations of the same function or coroutine.

Given
  for (;;) {}
forStmt(hasBody(compoundStmt()))
  matches 'for (;;) {}'
with compoundStmt()
  matching '{}'

Given
  void f();
  void f() {}
functionDecl(hasBody(compoundStmt()))
  matches 'void f() {}'
with compoundStmt()
  matching '{}'
  but does not match 'void f();'

AST Traversal Matcher: hasAnySubstatement
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<StmtExpr>
 Description: Matches compound statements where at least one substatement matches
a given matcher. Also matches StmtExprs that have CompoundStmt as children.

Given
  { {}; 1+2; }
hasAnySubstatement(compoundStmt())
  matches '{ {}; 1+2; }'
with compoundStmt()
  matching '{}'

ifStmt(hasCondition(anyOf(declRefExpr(hasDeclaration(varDecl(anyOf(parmVarDecl(), hasLocalStorage()), hasType(isInteger()), unless(hasType(isVolatileQualified()))).bind(CondVarStr))).bind(OuterIfVar1Str), binaryOperator(hasOperatorName("&&"), hasEitherOperand(declRefExpr(hasDeclaration(varDecl(anyOf(parmVarDecl(), hasLocalStorage()), hasType(isInteger()), unless(hasType(isVolatileQualified()))).bind(OuterIfVar2Str)))))), hasThen(hasDescendant(ifStmt(hasCondition(anyOf(declRefExpr(hasDeclaration(varDecl(equalsBoundNode(CondVarStr)))).bind(InnerIfVar1Str), binaryOperator(hasAnyOperatorName("&&", "||"), hasEitherOperand(declRefExpr(hasDeclaration(varDecl(equalsBoundNode(CondVarStr)))).bind(InnerIfVar2Str)))))).bind(InnerIfStr))), forFunction(functionDecl().bind(FuncStr))).bind(OuterIfStr)
Finder->addMatcher(
  callExpr(
    callee(functionDecl(hasName("::pthread_setcanceltype"))),
    argumentCountIs(2),
    hasArgument(0, isExpandedFromMacro("PTHREAD_CANCEL_ASYNCHRONOUS")))
    .bind("setcanceltype"),
  this);
functionDecl(hasBody(stmt()))


## reference api
const auto *Method = llvm::dyn_cast<CXXMethodDecl>(Function);
if (Param->getBeginLoc().isMacroID() || (Method && Method->isVirtual()) ||
    isReferencedOutsideOfCallExpr(*Function, *Result.Context) ||
    (Function->getTemplatedKind() != FunctionDecl::TK_NonTemplate))
  return;
const auto *IfWithDelete = Result.Nodes.getNodeAs<IfStmt>("ifWithDelete");
const auto *Compound = Result.Nodes.getNodeAs<CompoundStmt>("compound");
DiagnosticBuilder
NoexceptDestructorCheck::reportMissingNoexcept(const FunctionDecl *FuncDecl) {
  return diag(FuncDecl->getLocation(), "destructors should "
                                       "be marked noexcept");
}
StringRef clang::StoredDiagnostic::getMessage() const
bool clang::ento::PathDiagnosticCallPiece::hasCallStackMessage()
bool clang::IfStmt::hasElseStorage() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoElseBranchCheck.cpp :
```cpp
//===--- NoElseBranchCheck.cpp - clang-tidy -------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoElseBranchCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoElseBranchCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void NoElseBranchCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoElseBranchCheck.h :
```cpp
//===--- NoElseBranchCheck.h - clang-tidy -----------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-else-branch.html
class NoElseBranchCheck : public ClangTidyCheck {
public:
  NoElseBranchCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H

```
