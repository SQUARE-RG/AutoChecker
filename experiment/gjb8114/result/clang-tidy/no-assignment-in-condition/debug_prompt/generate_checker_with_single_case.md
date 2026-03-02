针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition/no_assignment_in_condition_case_7.cpp生成first checker
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
TranslationUnitDecl 0x5563f2a36f58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5563f2afc8f8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition/no_assignment_in_condition_case_7.cpp:3:1, line:10:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5563f2afcf78 <col:16, line:10:1>
    |-DeclStmt 0x5563f2afcba0 <line:4:5, col:28>
    | |-VarDecl 0x5563f2afc9b8 <col:5, col:13> col:9 used a 'int' cinit
    | | `-IntegerLiteral 0x5563f2afca20 <col:13> 'int' 0
    | |-VarDecl 0x5563f2afca58 <col:5, col:20> col:16 used b 'int' cinit
    | | `-IntegerLiteral 0x5563f2afcac0 <col:20> 'int' 0
    | `-VarDecl 0x5563f2afcaf8 <col:5, col:27> col:23 used c 'int' cinit
    |   `-IntegerLiteral 0x5563f2afcb60 <col:27> 'int' 5
    |-IfStmt 0x5563f2afcf28 <line:5:5, line:8:5>
    | |-BinaryOperator 0x5563f2afccf8 <line:5:9, col:25> 'bool' '||'
    | | |-BinaryOperator 0x5563f2afcc10 <col:9, col:14> 'bool' '=='
    | | | |-ImplicitCastExpr 0x5563f2afcbf8 <col:9> 'int' <LValueToRValue>
    | | | | `-DeclRefExpr 0x5563f2afcbb8 <col:9> 'int' lvalue Var 0x5563f2afc9b8 'a' 'int'
    | | | `-IntegerLiteral 0x5563f2afcbd8 <col:14> 'int' 0
    | | `-ImplicitCastExpr 0x5563f2afcce0 <col:19, col:25> 'bool' <IntegralToBoolean>
    | |   `-ImplicitCastExpr 0x5563f2afccc8 <col:19, col:25> 'int' <LValueToRValue>
    | |     `-ParenExpr 0x5563f2afcca8 <col:19, col:25> 'int' lvalue
    | |       `-BinaryOperator 0x5563f2afcc88 <col:20, col:24> 'int' lvalue '='
    | |         |-DeclRefExpr 0x5563f2afcc30 <col:20> 'int' lvalue Var 0x5563f2afca58 'b' 'int'
    | |         `-ImplicitCastExpr 0x5563f2afcc70 <col:24> 'int' <LValueToRValue>
    | |           `-DeclRefExpr 0x5563f2afcc50 <col:24> 'int' lvalue Var 0x5563f2afcaf8 'c' 'int'
    | `-CompoundStmt 0x5563f2afcf10 <col:28, line:8:5>
    |   `-CallExpr 0x5563f2afceb0 <line:7:9, col:30> 'int'
    |     |-ImplicitCastExpr 0x5563f2afce98 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x5563f2afce18 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x5563f2ad9528 'printf' 'int (const char *__restrict, ...)'
    |     |-ImplicitCastExpr 0x5563f2afcee0 <col:16> 'const char *' <ArrayToPointerDecay>
    |     | `-StringLiteral 0x5563f2afcdd8 <col:16> 'const char[9]' lvalue "b is %d\n"
    |     `-ImplicitCastExpr 0x5563f2afcef8 <col:29> 'int' <LValueToRValue>
    |       `-DeclRefExpr 0x5563f2afcdf8 <col:29> 'int' lvalue Var 0x5563f2afca58 'b' 'int'
    `-ReturnStmt 0x5563f2afcf68 <line:9:5, col:12>
      `-IntegerLiteral 0x5563f2afcf48 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for the 'ifStmt' node to capture all if statements.
2. Define a matcher for the 'whileStmt' node to capture all while loops.
3. Define a matcher for the 'doStmt' node to capture all do-while loops.
4. Define a matcher for the 'forStmt' node to capture all for loops.
5. Define a matcher for the 'conditionalOperator' node to capture ternary operators.
6. Define a matcher for the 'binaryConditionalOperator' node (GNU extension).
7. For each control flow statement matcher, bind its condition expression as 'cond'.
8. Create a matcher for binary logical operators ('&&', '||') to capture their operands, binding the operator as 'logical_op' and each operand as 'lhs' and 'rhs'.
9. Create a matcher for the 'binaryOperator' node where the operator is an assignment ('=') and bind it as 'assign'.
10. Combine the control flow statement and logical operator matchers to find any assignment operator directly within their condition or operand expressions, using the 'hasDescendant' or 'has' relationship with the assignment operator matcher.
11. Ensure the matcher does not trigger for assignment operators that are part of a larger comparison expression (e.g., 'if ((x = y) == 5)') by excluding patterns where the assignment is an immediate child of a comparison operator matcher.
12. Bind the matched assignment statement node as 'assign_in_cond' for reporting.
**logic for check**:
1. Retrieve the bound assignment statement node ('assign_in_cond') from the match result.
2. Retrieve the parent control flow statement or logical operator context from the match result (e.g., 'ifStmt', 'whileStmt', 'logical_op').
3. Determine the exact location (source range) of the assignment within the logical expression.
4. Emit a diagnostic message at the location of the assignment operator, indicating that using assignment statements in logical expressions is prohibited.
5. Include the context (e.g., 'inside if condition', 'inside logical OR operand') in the diagnostic message to help the developer locate the issue.
6. Do not generate any fix-it hints or automatic corrections.


## reference astMatchers
Node Matcher: gotoStmt
 Parameters;Matcher<GotoStmt>...
 return type Matcher<Stmt>
 Description: Matches goto statements.

Given
  goto FOO;
  FOO: bar();
gotoStmt()
  matches 'goto FOO'

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

Node Matcher: conditionalOperator
 Parameters;Matcher<ConditionalOperator>...
 return type Matcher<Stmt>
 Description: Matches conditional operator expressions.

Example matches a ? b : c
  (a ? b : c) + 42

Node Matcher: binaryConditionalOperator
 Parameters;Matcher<BinaryConditionalOperator>...
 return type Matcher<Stmt>
 Description: Matches binary conditional operator expressions (GNU extension).

Example matches a ?: b
  (a ?: b) + 42;

Narrowing Matcher: isMoveAssignmentOperator
 Parameters;
 return type Matcher<CXXMethodDecl>
 Description: Matches if the given method declaration declares a move assignment
operator.

Given
struct A {
  A &amp;operator=(const A &amp;);
  A &amp;operator=(A &amp;&amp;);
};

cxxMethodDecl(isMoveAssignmentOperator()) matches the second method but not
the first one.

Node Matcher: forStmt
 Parameters;Matcher<ForStmt>...
 return type Matcher<Stmt>
 Description: Matches for statements.

Example matches 'for (;;) {}'
  for (;;) {}
  int i[] =  {1, 2, 3}; for (auto a : i);

Node Matcher: doStmt
 Parameters;Matcher<DoStmt>...
 return type Matcher<Stmt>
 Description: Matches do statements.

Given
  do {} while (true);
doStmt()
  matches 'do {} while(true)'

AST Traversal Matcher: hasConditionVariableStatement
 Parameters;Matcher<DeclStmt> InnerMatcher
 Return type Matcher<IfStmt>
 Description: Matches the condition variable statement in an if statement.

Given
  if (A* a = GetAPointer()) {}
hasConditionVariableStatement(...)
  matches 'A* a = GetAPointer()'.

AST Traversal Matcher: hasLHS
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches the left hand side of binary operator expressions.

Example matches a (matcher = binaryOperator(hasLHS()))
  a || b

Node Matcher: whileStmt
 Parameters;Matcher<WhileStmt>...
 return type Matcher<Stmt>
 Description: Matches while statements.

Given
  while (true) {}
whileStmt()
  matches 'while (true) {}'.

Narrowing Matcher: isAssignmentOperator
 Parameters;
 return type Matcher<CXXOperatorCallExpr>
 Description: Matches all kinds of assignment operators.

Example 1: matches a += b (matcher = binaryOperator(isAssignmentOperator()))
  if (a == b)
    a += b;

Example 2: matches s1 = s2
           (matcher = cxxOperatorCallExpr(isAssignmentOperator()))
  struct S { S&amp; operator=(const S&amp;); };
  void x() { S s1, s2; s1 = s2; }

Node Matcher: ifStmt
 Parameters;Matcher<IfStmt>...
 return type Matcher<Stmt>
 Description: Matches if statements.

Example matches 'if (x) {}'
  if (x) {}

AST_POLYMORPHIC_MATCHER_P(boolean, AST_POLYMORPHIC_SUPPORTED_TYPES(Stmt, Decl), bool, Boolean) { return Boolean; }
Finder->addMatcher(whileStmt().bind("while"), this)
binaryOperator(isComparisonOperator())
const auto DoWithFalse = doStmt(hasCondition(ignoringImpCasts(anyOf(cxxBoolLiteral(equals(false)), integerLiteral(equals(0)), cxxNullPtrLiteralExpr(), gnuNullExpr()))), equalsBoundNode("closestLoop"));
stmt().bind("stmt")
const Expr *getCondition(const BoundNodes &Nodes, const StringRef NodeId) {
  const auto *If = Nodes.getNodeAs<IfStmt>(NodeId);
  if (If != nullptr)
    return If->getCond();

  const auto *For = Nodes.getNodeAs<ForStmt>(NodeId);
  if (For != nullptr)
    return For->getCond();

  const auto *While = Nodes.getNodeAs<WhileStmt>(NodeId);
  if (While != nullptr)
    return While->getCond();

  const auto *Do = Nodes.getNodeAs<DoStmt>(NodeId);
  if (Do != nullptr)
    return Do->getCond();

  const auto *Switch = Nodes.getNodeAs<SwitchStmt>(NodeId);
  if (Switch != nullptr)
    return Switch->getCond();

  return nullptr;
}
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}
conditionalOperator()
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")
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


## reference api  
auto Diag = diag(
    IfWithDelete->getBeginLoc(),
    "'if' statement is unnecessary; deleting null pointer has no effect");
const SourceManager &SM = *Result.SourceManager;
const ASTContext *Context = Result.Context;

if (const auto *S = Result.Nodes.getNodeAs<ForStmt>("for")) {
  checkStmt(Result, S->getBody(), S->getRParenLoc());
} else if (const auto *S = Result.Nodes.getNodeAs<CXXForRangeStmt>("for-range")) {
  checkStmt(Result, S->getBody(), S->getRParenLoc());
} else if (const auto *S = Result.Nodes.getNodeAs<DoStmt>("do")) {
  checkStmt(Result, S->getBody(), S->getDoLoc(), S->getWhileLoc());
} else if (const auto *S = Result.Nodes.getNodeAs<WhileStmt>("while")) {
  SourceLocation StartLoc = findRParenLoc(S, SM, Context);
  if (StartLoc.isInvalid())
    return;
  checkStmt(Result, S->getBody(), StartLoc);
} else if (const auto *S = Result.Nodes.getNodeAs<IfStmt>("if")) {
  if (S->isConsteval())
    return;
  SourceLocation StartLoc = findRParenLoc(S, SM, Context);
  if (StartLoc.isInvalid())
    return;
  if (ForceBracesStmts.erase(S))
    ForceBracesStmts.insert(S->getThen());
  bool BracedIf = checkStmt(Result, S->getThen(), StartLoc, S->getElseLoc());
  const Stmt *Else = S->getElse();
  if (Else && BracedIf)
    ForceBracesStmts.insert(Else);
  if (Else && !isa<IfStmt>(Else)) {
    checkStmt(Result, Else, S->getElseLoc());
  }
}
CharSourceRange SourceRange = Lexer::makeFileCharRange(
    CharSourceRange::getTokenRange(ArgExpr->getSourceRange()),
    *Result.SourceManager, Result.Context->getLangOpts());
if (SourceRange.isInvalid())
  return;
diag(ASMLocation, "do not use inline assembler in safety-critical code");
const auto *Method = llvm::dyn_cast<CXXMethodDecl>(Function);
if (Param->getBeginLoc().isMacroID() || (Method && Method->isVirtual()) ||
    isReferencedOutsideOfCallExpr(*Function, *Result.Context) ||
    (Function->getTemplatedKind() != FunctionDecl::TK_NonTemplate))
  return;
const auto *Loop = Result.Nodes.getNodeAs<Stmt>("loop");
const auto *CXXLoopBound = Result.Nodes.getNodeAs<IntegerLiteral>("cxx_loop_bound");
const ASTContext *Context = Result.Context;
unsigned int clang::ConstraintInfo::getTiedOperand() const
SourceLocation clang::SourceLocExpr::getLocation() const
RetEffect clang::ento::RetEffect::MakeNoRet()
DeclContext * clang::SourceLocExpr::getParentContext()
bool clang::BinaryOperator::isAssignmentOp() const
ArrayRef<FixItHint> clang::Diagnostic::getFixItHints() const


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