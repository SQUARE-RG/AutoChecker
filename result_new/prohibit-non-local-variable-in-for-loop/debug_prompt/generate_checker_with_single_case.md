针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop/prohibit_non_local_variable_in_for_loop_case_8.cpp生成first checker
# Inputs

## rule
**Rule Description:**
Forbidden to use non-local variables for loop control variables. The rule requires that the control variable of a for loop must be a local variable, and non-local variables (such as global variables, static global variables, or external-scope variables) must not be used as loop control variables. This rule aims to ensure that the control variable of the loop has a clear scope and lifetime, preventing unintended modifications and logical errors in code caused by the spread of variable scope. When the control variable of a for loop is a non-local variable, the variable may be unintentionally modified outside the loop, affecting the expected behavior of the loop and reducing the maintainability and readability of the code. Compliant scenarios are for loops using local variables defined within functions or block scopes as control variables; non-compliant scenarios are for loops using any non-local variables (including global variables, static variables, or external variables) as control variables. The rule checks the scope of the control variable in the initialization part of the for loop, not the use of the variable within the loop body.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int i = 0;  // 全局变量

void foo(void) {
    for (i = 0; i < 7; ++i) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", i);
    }
}

int main(void) {
    foo();
    return 0;
}
```

## AST
TranslationUnitDecl 0x55f9ce922f08 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55f9ce9e8cb8 <line:12:1, line:15:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x55f9ce9e8e60 <col:16, line:15:1>
    |-CallExpr 0x55f9ce9e8e10 <line:13:5, col:9> 'void'
    | `-ImplicitCastExpr 0x55f9ce9e8df8 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x55f9ce9e8da8 <col:5> 'void ()' lvalue Function 0x55f9ce9e8838 'foo' 'void ()'
    `-ReturnStmt 0x55f9ce9e8e50 <line:14:5, col:12>
      `-IntegerLiteral 0x55f9ce9e8e30 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match for statements (forStmt) in the AST to capture the loop structure
2. Within the for statement, access the init part (forInit) and look for a binary assignment operator (binaryOperator) that assigns a value to a variable
3. In the assignment, retrieve the left-hand side (LHS) as a DeclRefExpr (declRefExpr) to get the variable being assigned
4. Bind the DeclRefExpr node as 'loopVar' to later check the variable's scope and linkage
5. Ensure the matched for loop has a condition and increment part to avoid matching incomplete for loops
6. Exclude for loops where the init part is a declaration statement (declStmt) with a local variable, as those are compliant
**logic for check**:
1. Retrieve the bound DeclRefExpr node 'loopVar' from the match result
2. Obtain the VarDecl for the variable referenced by the DeclRefExpr
3. Check the storage class of the VarDecl: if it has external linkage (isFileVarDecl()) or is a global variable (hasGlobalStorage()), it is non-local
4. If the variable is a static local variable (static storage duration but local scope), it is allowed, so only flag variables with external or global scope
5. If the variable is non-local, emit a diagnostic message: '禁止 for 循环控制变量使用非局部变量'
6. Optionally, get the source location of the for loop init to point to the exact location of the violation


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

Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Decl>
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

StatementMatcher makeIteratorLoopMatcher(bool IsReverse) {

  auto BeginNameMatcher = IsReverse ? hasAnyName("rbegin", "crbegin")
                                    : hasAnyName("begin", "cbegin");

  auto EndNameMatcher =
      IsReverse ? hasAnyName("rend", "crend") : hasAnyName("end", "cend");

  StatementMatcher BeginCallMatcher =
      cxxMemberCallExpr(argumentCountIs(0),
                        callee(cxxMethodDecl(BeginNameMatcher)))
          .bind(BeginCallName);

  DeclarationMatcher InitDeclMatcher =
      varDecl(hasInitializer(anyOf(ignoringParenImpCasts(BeginCallMatcher),
                                   materializeTemporaryExpr(
                                       ignoringParenImpCasts(BeginCallMatcher)),
                                   hasDescendant(BeginCallMatcher))))
          .bind(InitVarName);

  DeclarationMatcher EndDeclMatcher =
      varDecl(hasInitializer(anything())).bind(EndVarName);

  StatementMatcher EndCallMatcher = cxxMemberCallExpr(
      argumentCountIs(0), callee(cxxMethodDecl(EndNameMatcher)));

  StatementMatcher IteratorBoundMatcher =
      expr(anyOf(ignoringParenImpCasts(
                     declRefExpr(to(varDecl(equalsBoundNode(EndVarName))))),
                 ignoringParenImpCasts(expr(EndCallMatcher).bind(EndCallName)),
                 materializeTemporaryExpr(ignoringParenImpCasts(
                     expr(EndCallMatcher).bind(EndCallName)))));

  StatementMatcher IteratorComparisonMatcher = expr(ignoringParenImpCasts(
      declRefExpr(to(varDecl(equalsBoundNode(InitVarName))))));

  internal::Matcher<VarDecl> TestDerefReturnsByValue =
      hasType(hasUnqualifiedDesugaredType(
          recordType(hasDeclaration(cxxRecordDecl(hasMethod(cxxMethodDecl(
              hasOverloadedOperatorName("*"),
              anyOf(
                  returns(qualType(unless(hasCanonicalType(referenceType())))
                              .bind(DerefByValueResultName)),
                  returns(
                      qualType(unless(hasCanonicalType(rValueReferenceType())))
                          .bind(DerefByRefResultName))))))))));

  return forStmt(
             unless(isInTemplateInstantiation()),
             hasLoopInit(anyOf(declStmt(declCountIs(2),
                                        containsDeclaration(0, InitDeclMatcher),
                                        containsDeclaration(1, EndDeclMatcher)),
                               declStmt(hasSingleDecl(InitDeclMatcher)))),
             hasCondition(ignoringImplicit(binaryOperation(
                 hasOperatorName("!="), hasOperands(IteratorComparisonMatcher,
                                                    IteratorBoundMatcher)))),
             hasIncrement(anyOf(
                 unaryOperator(hasOperatorName("++"),
                               hasUnaryOperand(declRefExpr(
                                   to(varDecl(equalsBoundNode(InitVarName)))))),
                 cxxOperatorCallExpr(
                     hasOverloadedOperatorName("++"),
                     hasArgument(0, declRefExpr(to(
                                        varDecl(equalsBoundNode(InitVarName),
                                                TestDerefReturnsByValue))))))))
      .bind(IsReverse ? LoopNameReverseIterator : LoopNameIterator);
}
bool isCatchVariable(const DeclRefExpr *DeclRefExpr) {
  auto *ValueDecl = DeclRefExpr->getDecl();
  if (auto *VarDecl = dyn_cast<clang::VarDecl>(ValueDecl))
    return VarDecl->isExceptionVariable();
  return false;
}
Finder->addMatcher(compoundStmt(has(stmt(anyOf(ifStmt(), forStmt(), whileStmt())))).bind("compound"), this);


## reference api
const auto *UsageSiteExpr = Result.Nodes.getNodeAs<DeclRefExpr>("use-site");
const auto *FuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("func");
if (const auto *DeclRef = dyn_cast<DeclRefExpr>(PtrInputExpr->IgnoreParenImpCasts()))
  if (const auto *Var = dyn_cast<VarDecl>(DeclRef->getDecl()))
    if (const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>("parent_function"))
      if (FindAssignToVarBefore{Var, DeclRef, SM}.Visit(Func->getBody()))
        return;
bool isCatchVariable(const DeclRefExpr *DeclRefExpr) {
  auto *ValueDecl = DeclRefExpr->getDecl();
  if (auto *VarDecl = dyn_cast<clang::VarDecl>(ValueDecl))
    return VarDecl->isExceptionVariable();
  return false;
}
const ValueDecl * clang::DeclRefExpr::getDecl() const
void clang::TextNodeDumper::VisitDeclRefExpr(const DeclRefExpr * Node)
bool clang::VarDecl::hasExternalStorage() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitNonLocalVariableInForLoopCheck.cpp :
```cpp
//===--- ProhibitNonLocalVariableInForLoopCheck.cpp - clang-tidy ----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitNonLocalVariableInForLoopCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitNonLocalVariableInForLoopCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitNonLocalVariableInForLoopCheck.h :
```cpp
//===--- ProhibitNonLocalVariableInForLoopCheck.h - clang-tidy --*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/prohibit-non-local-variable-in-for-loop.html
class ProhibitNonLocalVariableInForLoopCheck : public ClangTidyCheck {
public:
  ProhibitNonLocalVariableInForLoopCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H

```
