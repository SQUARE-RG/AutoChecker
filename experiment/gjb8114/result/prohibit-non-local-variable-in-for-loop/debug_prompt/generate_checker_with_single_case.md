针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop/prohibit_non_local_variable_in_for_loop_case_8.cpp生成first checker
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
TranslationUnitDecl 0x558b09e7bf08 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x558b09f41cb8 <line:12:1, line:15:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x558b09f41e60 <col:16, line:15:1>
    |-CallExpr 0x558b09f41e10 <line:13:5, col:9> 'void'
    | `-ImplicitCastExpr 0x558b09f41df8 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x558b09f41da8 <col:5> 'void ()' lvalue Function 0x558b09f41838 'foo' 'void ()'
    `-ReturnStmt 0x558b09f41e50 <line:14:5, col:12>
      `-IntegerLiteral 0x558b09f41e30 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for `ForStmt` nodes to capture all for loops.
2. Within the `ForStmt` matcher, traverse to its initialization expression using `hasLoopInit`.
3. Match initialization expressions that are binary operators of assignment form (`BinaryOperator` with `isAssignmentOp()`).
4. Alternatively, match initialization expressions that are declarations (`DeclStmt`).
5. For assignment initialization, bind the left-hand side (LHS) expression as `lhs`.
6. For declaration initialization, bind the declared variable as `decl`.
7. Ensure the bound node (`lhs` or `decl`) is a `VarDecl` to identify the loop control variable.
8. Check if the variable's declaration context is not a function or block scope (i.e., it's a global, namespace, or file scope variable).
9. Bind the matched `ForStmt` node as `forLoop` for reporting.
**logic for check**:
1. Retrieve the bound `ForStmt` node (`forLoop`) from the match result.
2. Attempt to retrieve the bound `VarDecl` node from either the `decl` or `lhs` binding, depending on the match.
3. If a `VarDecl` is found, check its storage class and linkage to determine if it's non-local (e.g., `isFileVarDecl()`, `hasGlobalStorage()`, or `getLinkageAndVisibility().getLinkage()` indicates external or internal linkage).
4. Verify the variable's declarative context is not a function or block (e.g., `getDeclContext()` is not a `FunctionDecl` or `BlockDecl`).
5. If the variable is non-local, emit a diagnostic message at the location of the `ForStmt`, indicating the use of a non-local variable as a loop control variable.
6. Include the variable's name and scope information in the diagnostic details.


## reference astMatchers
AST Traversal Matcher: hasLHS
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<ArraySubscriptExpr>
 Description: Matches the left hand side of binary operator expressions.

Example matches a (matcher = binaryOperator(hasLHS()))
  a || b

Narrowing Matcher: isExternC
 Parameters;
 return type Matcher<FunctionDecl>
 Description: Matches extern "C" function or variable declarations.

Given:
  extern "C" void f() {}
  extern "C" { void g() {} }
  void h() {}
  extern "C" int x = 1;
  extern "C" int y = 2;
  int z = 3;
functionDecl(isExternC())
  matches the declaration of f and g, but not the declaration of h.
varDecl(isExternC())
  matches the declaration of x and y, but not the declaration of z.

Node Matcher: forStmt
 Parameters;Matcher<ForStmt>...
 return type Matcher<Stmt>
 Description: Matches for statements.

Example matches 'for (;;) {}'
  for (;;) {}
  int i[] =  {1, 2, 3}; for (auto a : i);

AST Traversal Matcher: hasLoopInit
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<ForStmt>
 Description: Matches the initialization statement of a for loop.

Example:
    forStmt(hasLoopInit(declStmt()))
matches 'int x = 0' in
    for (int x = 0; x &lt; N; ++x) { }

AST Traversal Matcher: containsDeclaration
 Parameters;unsigned N, Matcher<Decl> InnerMatcher
 Return type Matcher<DeclStmt>
 Description: Matches the n'th declaration of a declaration statement.

Note that this does not work for global declarations because the AST
breaks up multiple-declaration DeclStmt's into multiple single-declaration
DeclStmt's.
Example: Given non-global declarations
  int a, b = 0;
  int c;
  int d = 2, e;
declStmt(containsDeclaration(
      0, varDecl(hasInitializer(anything()))))
  matches only 'int d = 2, e;', and
declStmt(containsDeclaration(1, varDecl()))
  matches 'int a, b = 0' as well as 'int d = 2, e;'
  but 'int c;' is not matched.

Narrowing Matcher: isConstinit
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches constinit variable declarations.

Given:
  constinit int foo = 42;
  constinit const char* bar = "bar";
  int baz = 42;
  [[clang::require_constant_initialization]] int xyz = 42;
varDecl(isConstinit())
  matches the declaration of `foo` and `bar`, but not `baz` and `xyz`.

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

varDecl(isLocalVarDecl())
hasLHS(expr())
Finder->addMatcher(cxxMethodDecl(anyOf(isOverride(), isVirtual()), hasAnyParameter(parmVarDecl(hasInitializer(expr())))).bind("Decl"), this);
declStmt(containsDeclaration(0, varDecl(hasInitializer(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasName("cast")))).bind("assign")))))
static bool possibleVarDecl(const MacroInfo *MI, const Token *Tok) {
  if (Tok == MI->tokens_end())
    return false;
  if (isVarDeclKeyword(*Tok))
    return true;
  if (!Tok->isOneOf(tok::identifier, tok::raw_identifier, tok::coloncolon))
    return false;
  while (Tok != MI->tokens_end() &&
         Tok->isOneOf(tok::identifier, tok::raw_identifier, tok::coloncolon,
                      tok::star, tok::amp, tok::ampamp, tok::less,
                      tok::greater))
    Tok++;
  return Tok == MI->tokens_end() ||
         Tok->isOneOf(tok::equal, tok::semi, tok::l_square, tok::l_paren) ||
         isVarDeclKeyword(*Tok);
}
stmt().bind("stmt")
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}
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
anyOf(initListExpr(anyOf(allOf(initCountIs(1), hasInit(0, InitBase)),
                               initCountIs(0), hasType(arrayType()))),
            InitBase)


## reference api  
const auto *const Var = Result.Nodes.getNodeAs<VarDecl>("var");
if (Variable) {
  diag(Variable->getLocation(), "variable %0 is non-const and globally "
                              "accessible, consider making it const")
      << Variable;
}
const auto *Function = dyn_cast<FunctionDecl>(Param->getDeclContext());
if (!Function)
  return;
const ForStmt *Loop;
LoopFixerKind FixerKind;
if ((Loop = Nodes.getNodeAs<ForStmt>(LoopNameArray))) {
  FixerKind = LFK_Array;
} else if ((Loop = Nodes.getNodeAs<ForStmt>(LoopNameIterator))) {
  FixerKind = LFK_Iterator;
} else if ((Loop = Nodes.getNodeAs<ForStmt>(LoopNameReverseIterator))) {
  FixerKind = LFK_ReverseIterator;
} else {
  Loop = Nodes.getNodeAs<ForStmt>(LoopNamePseudoArray);
  assert(Loop && "Bad Callback. No for statement");
  FixerKind = LFK_PseudoArray;
}
UnnamedParams.push_back(std::make_pair(Function, I));
AST_MATCHER(VarDecl, isGlobalStatic) {
  return Node.getStorageDuration() == SD_Static && !Node.isLocalVarDecl();
}
StringRef clang::DiagnosticIDs::getDescription(unsigned int DiagID) const
void clang::ForStmt::setConditionVariableDeclStmt(DeclStmt * CondVar)
Expr * clang::BindingDecl::getBinding() const
bool clang::VarDecl::hasExternalStorage() const
const Stmt * clang::CapturedStmt::getCapturedStmt() const
const Decl * clang::Decl::getNonClosureContext() const


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