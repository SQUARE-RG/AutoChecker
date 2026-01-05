针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr/dependent_call_in_expr_case_3.cpp生成first checker
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
Multiple related functions cannot be called in the same expression.Related functions refer to functions called in the same expression that have a data dependency relationship, which will result in undefined behavior.Scenario: Reporting multiple related function calls
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            int y = inc(&x) + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then it should report "test.c:16:21: warning: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]"
    And a total of 1 warning should be reported

Scenario: Do not report multiple related function calls that are not in the same expression
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            x = inc(&x);
            int y = x + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then no warnings should be reported

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

struct Data {
    int count;
    int total;
};

int update_count(struct Data *data) {
    data->count++;
    return data->count;
}

int calculate_total(struct Data *data) {
    data->total = data->count * 10;
    return data->total;
}

int main(void) {
    struct Data my_data = {5, 0};
    int result = update_count(&my_data) + calculate_total(&my_data);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
```

## AST
TranslationUnitDecl 0x55dbd4fdaf48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55dbd50a1328 <line:18:1, line:23:1> line:18:5 main 'int ()'
  `-CompoundStmt 0x55dbd50a19b8 <col:16, line:23:1>
    |-DeclStmt 0x55dbd50a1550 <line:19:5, col:33>
    | `-VarDecl 0x55dbd50a13f0 <col:5, col:32> col:17 used my_data 'struct Data':'Data' cinit
    |   `-InitListExpr 0x55dbd50a1500 <col:27, col:32> 'struct Data':'Data'
    |     |-IntegerLiteral 0x55dbd50a1458 <col:28> 'int' 5
    |     `-IntegerLiteral 0x55dbd50a1490 <col:31> 'int' 0
    |-DeclStmt 0x55dbd50a1958 <line:20:5, col:68>
    | `-VarDecl 0x55dbd50a1580 <col:5, col:67> col:9 used result 'int' cinit
    |   `-BinaryOperator 0x55dbd50a1938 <col:18, col:67> 'int' '+'
    |     |-CallExpr 0x55dbd50a1760 <col:18, col:39> 'int'
    |     | |-ImplicitCastExpr 0x55dbd50a1748 <col:18> 'int (*)(struct Data *)' <FunctionToPointerDecay>
    |     | | `-DeclRefExpr 0x55dbd50a16c8 <col:18> 'int (struct Data *)' lvalue Function 0x55dbd50a0d40 'update_count' 'int (struct Data *)'
    |     | `-UnaryOperator 0x55dbd50a1650 <col:31, col:32> 'struct Data *' prefix '&' cannot overflow
    |     |   `-DeclRefExpr 0x55dbd50a1630 <col:32> 'struct Data':'Data' lvalue Var 0x55dbd50a13f0 'my_data' 'struct Data':'Data'
    |     `-CallExpr 0x55dbd50a1910 <col:43, col:67> 'int'
    |       |-ImplicitCastExpr 0x55dbd50a18f8 <col:43> 'int (*)(struct Data *)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x55dbd50a18d8 <col:43> 'int (struct Data *)' lvalue Function 0x55dbd50a0fe0 'calculate_total' 'int (struct Data *)'
    |       `-UnaryOperator 0x55dbd50a18c0 <col:59, col:60> 'struct Data *' prefix '&' cannot overflow
    |         `-DeclRefExpr 0x55dbd50a18a0 <col:60> 'struct Data':'Data' lvalue Var 0x55dbd50a13f0 'my_data' 'struct Data':'Data'
    `-ReturnStmt 0x55dbd50a19a8 <line:22:5, col:12>
      `-ImplicitCastExpr 0x55dbd50a1990 <col:12> 'int' <LValueToRValue>
        `-DeclRefExpr 0x55dbd50a1970 <col:12> 'int' lvalue Var 0x55dbd50a1580 'result' 'int'


## reference logic step
[{'logic_registerMatchers': ["1. Define a matcher for function calls (callExpr) and bind them as 'call'", "2. Define a matcher for binary operators (binaryOperator) that represent expressions where multiple calls could appear (e.g., '+', '-', '*', '/', '&&', '||', etc.) and bind them as 'binaryOp'", "3. Define a matcher for conditional operators (conditionalOperator) and bind them as 'condOp'", "4. Define a matcher for comma operators (binaryOperator with opcode ',') and bind them as 'commaOp'", "5. Combine these expression matchers (binaryOperator, conditionalOperator) into a single 'topLevelExpr' matcher using anyOf", '6. Within the topLevelExpr matcher, traverse its subexpressions to find all callExpr nodes and collect them', "7. For each callExpr, retrieve its callee function declaration (functionDecl) and bind it as 'func'", '8. For each function declaration, analyze its parameters to identify pointer/reference parameters that could introduce data dependencies', '9. Create a mechanism to compare parameters of different function calls within the same topLevelExpr to detect overlapping pointer/reference arguments', "10. When overlapping pointer/reference arguments are found between multiple calls in the same expression, bind the entire topLevelExpr as 'violationExpr'"], 'logic_check': ["1. Retrieve the bound 'violationExpr' node from the match result", '2. Extract all callExpr nodes within the violationExpr using AST traversal', '3. For each callExpr, get its function declaration and parameter list', '4. Identify which parameters are pointers or references that could modify data', '5. Compare the arguments passed to these parameters across different function calls', '6. Determine if there are overlapping memory addresses (same variable passed via pointer/reference) between calls', '7. If overlapping memory addresses are found and the functions could have data dependencies (both potentially modifying or reading the same data), emit a diagnostic warning', '8. The diagnostic message should indicate that multiple related function calls appear in the same expression', '9. Include source location information from the violationExpr in the diagnostic']}]

## reference astMatchers
Node Matcher: callExpr
 Parameters;Matcher<CallExpr>...
 return type Matcher<Stmt>
 Description: Matches call expressions.

Example matches x.y() and y()
  X x;
  x.y();
  y();

Narrowing Matcher: parameterCountIs
 Parameters;unsigned N
 return type Matcher<FunctionDecl>
 Description: Matches FunctionDecls and FunctionProtoTypes that have a
specific parameter count.

Given
  void f(int i) {}
  void g(int i, int j) {}
  void h(int i, int j);
  void j(int i);
  void k(int x, int y, int z, ...);
functionDecl(parameterCountIs(2))
  matches g and h
functionProtoType(parameterCountIs(2))
  matches g and h
functionProtoType(parameterCountIs(3))
  matches k

Narrowing Matcher: hasOperatorName
 Parameters;std::string Name
 return type Matcher<CXXRewrittenBinaryOperator>
 Description: Matches the operator Name of operator expressions (binary or
unary).

Example matches a || b (matcher = binaryOperator(hasOperatorName("||")))
  !(a || b)

AST Traversal Matcher: onImplicitObjectArgument
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<CXXMemberCallExpr>
 Description: Matches on the implicit object argument of a member call expression. Unlike
`on`, matches the argument directly without stripping away anything.

Given
  class Y { public: void m(); };
  Y g();
  class X : public Y { void g(); };
  void z(Y y, X x) { y.m(); x.m(); x.g(); (g()).m(); }
cxxMemberCallExpr(onImplicitObjectArgument(hasType(
    cxxRecordDecl(hasName("Y")))))
  matches `y.m()`, `x.m()` and (g()).m(), but not `x.g()`.
cxxMemberCallExpr(on(callExpr()))
  does not match `(g()).m()`, because the parens are not ignored.

FIXME: Overload to allow directly matching types?

AST Traversal Matcher: forEachArgumentWithParamType
 Parameters;Matcher<Expr> ArgMatcher, Matcher<QualType> ParamMatcher
 Return type Matcher<CallExpr>
 Description: Matches all arguments and their respective types for a CallExpr or
CXXConstructExpr. It is very similar to forEachArgumentWithParam but
it works on calls through function pointers as well.

The difference is, that function pointers do not provide access to a
ParmVarDecl, but only the QualType for each argument.

Given
  void f(int i);
  int y;
  f(y);
  void (*f_ptr)(int) = f;
  f_ptr(y);
callExpr(
  forEachArgumentWithParamType(
    declRefExpr(to(varDecl(hasName("y")))),
    qualType(isInteger()).bind("type)
))
  matches f(y) and f_ptr(y)
with declRefExpr(...)
  matching int y
and qualType(...)
  matching int

AST Traversal Matcher: callee
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<CallExpr>
 Description: Matches if the call expression's callee expression matches.

Given
  class Y { void x() { this-&gt;x(); x(); Y y; y.x(); } };
  void f() { f(); }
callExpr(callee(expr()))
  matches this-&gt;x(), x(), y.x(), f()
with callee(...)
  matching this-&gt;x, x, y.x, f respectively

Note: Callee cannot take the more general internal::Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1Expr.html">Expr</a>&gt;
because this introduces ambiguous overloads with calls to Callee taking a
internal::Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1Decl.html">Decl</a>&gt;, as the matcher hierarchy is purely
implemented in terms of implicit casts.

Node Matcher: conditionalOperator
 Parameters;Matcher<ConditionalOperator>...
 return type Matcher<Stmt>
 Description: Matches conditional operator expressions.

Example matches a ? b : c
  (a ? b : c) + 42

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

Narrowing Matcher: hasAnyOperatorName
 Parameters;StringRef, ..., StringRef
 return type Matcher<BinaryOperator>
 Description: Matches operator expressions (binary or unary) that have any of the
specified names.

   hasAnyOperatorName("+", "-")
 Is equivalent to
   anyOf(hasOperatorName("+"), hasOperatorName("-"))

AST_MATCHER(CXXOperatorCallExpr, nestedParametersAreEquivalent) {
  return markDuplicateOperands(&Node, Builder, Finder->getASTContext());
}
else if (const auto *VD = Result.Nodes.getNodeAs<VarDecl>("Mark")) {
  const QualType T = VD->getType();
  if ((T->isPointerType() && !T->getPointeeType().isConstQualified()) || T->isArrayType())
    markCanNotBeConst(VD->getInit(), true);
  else if (T->isLValueReferenceType() && !T->getPointeeType().isConstQualified())
    markCanNotBeConst(VD->getInit(), false);
}
callExpr(...)
Finder->addMatcher(callExpr().bind("CE"), this);
callExpr(hasAnyArgument(ignoringParenImpCasts(anyOf(declRefExpr(to(equalsNode(D))), memberExpr(hasDeclaration(equalsNode(D)))))))
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}
conditionalOperator()
expr(anyOf(ComparisonUnaryOperator, ComparisonBinaryOperator))
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")
callExpr(callee(namedDecl(hasAnyName("::boost::bind", "::std::bind"))))


## reference api  
SourceLocation ReportLoc = FunctorLoc.getLocation();
if (ReportLoc.isInvalid())
  return;
diag(ReportLoc, Message) << FuncClass->getName()
                         << FixItHint::CreateRemoval(
                                FunctorTypeLoc.getArgLoc(0).getSourceRange());
StringRef WaitName = MatchedWait->getDirectCallee()->getName();
Expr *findCallExpr(const CallGraphNode *Caller, const CallGraphNode *Callee) {
  auto FoundCallee = llvm::find_if(
      Caller->callees(), [Callee](const CallGraphNode::CallRecord &Call) {
        return Call.Callee == Callee;
      });
  assert(FoundCallee != Caller->end() &&
         "Callee should be called from the caller function here.");
  return FoundCallee->CallExpr;
}
VariableCategory VC = VariableCategory::Value;
if (Variable->getType()->isReferenceType())
  VC = VariableCategory::Reference;
if (Variable->getType()->isPointerType())
  VC = VariableCategory::Pointer;
if (Variable->getType()->isArrayType()) {
  if (const auto *ArrayT = dyn_cast<ArrayType>(Variable->getType())) {
    if (ArrayT->getElementType()->isPointerType())
      VC = VariableCategory::Pointer;
  }
}
bool IsSamePtrExpr::check(const Expr *E1, const Expr *E2) {
  E1 = E1->IgnoreParenCasts();
  E2 = E2->IgnoreParenCasts();
  OtherE = E2;
  return Visit(const_cast<Expr *>(E1));
}
diag(Operator->getOperatorLoc(), "redundant repeated dereference of function pointer")
const auto *Var = Result.Nodes.getNodeAs<VarDecl>("vardecl");
const auto *CtorCall = Result.Nodes.getNodeAs<Expr>("ctor_call");
if (!Var || !CtorCall)
  return;
for (unsigned I = 1, E = Call->getNumArgs(); I < E; ++I) {
  const Expr *LHS = Call->getArg(I - 1);
  const Expr *RHS = Call->getArg(I);

  if (UsedArgs.count(RHS))
    continue;
bool clang::QualType::isAddressSpaceOverlapping(QualType T) const
QualType clang::Expr::findBoundMemberType(const Expr * expr)
bool clang::ento::PathDiagnosticCallPiece::hasCallStackMessage()
bool clang::MemberPointerType::isMemberDataPointer() const
const Expr *const * clang::CallExpr::getArgs() const
ArrayRef<Stmt *> clang::CallExpr::getRawSubExprs()
void clang::CFGCallback::compareBitwiseEquality(const BinaryOperator * B, bool isAlwaysTrue)
SourceLocation clang::ento::PathDiagnosticLocation::getValidSourceLocation(const Stmt * S, LocationOrAnalysisDeclContext LAC, bool UseEndOfStatement)


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DependentCallInExprCheck.cpp :
```cpp
//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DependentCallInExprCheck.h :
```cpp
//===--- DependentCallInExprCheck.h - clang-tidy ----------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/dependent-call-in-expr.html
class DependentCallInExprCheck : public ClangTidyCheck {
public:
  DependentCallInExprCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H

```

# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
    -In the check() function, all extracted nodes must be checked for non-null and isValid() to avoid direct usage
    **Example Output Format:**
    checker_cpp:
    ```cpp
        ....(source code)....
    ```

    checker_h:
    ```cpp
        ....(source code)....
    ```