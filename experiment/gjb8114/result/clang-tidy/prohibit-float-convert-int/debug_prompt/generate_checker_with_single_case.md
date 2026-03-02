针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_1.cpp生成first checker
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
This rule prohibits the direct assignment of a floating-point variable to an integer variable without using an explicit cast. It aims to prevent data precision loss and potential errors caused by implicit type conversions. When a floating-point variable (including types such as floatand double) is assigned to an integer variable (e.g., int, short, long, etc.), an explicit cast (e.g., (int)x) must be used to clearly convey the developer's intent. This avoids ambiguity and risks arising from the compiler automatically truncating the fractional part of the floating-point number.
A compliant scenario is when the assignment operation uses an explicit cast (e.g., i = (int)x;) or involves only integer variables. A violation occurs when a floating-point variable is directly assigned to an integer variable without a cast (e.g., i = x;) .
This rule specifically checks assignments between variables and does not apply to constant assignments. Furthermore, the explicit cast must correctly encompass the entire expression or variable

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int main(void) {
    float f = 3.14f;
    int i;
    i = f;  // 违反：float变量直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}
```

## AST
TranslationUnitDecl 0x561a907c9f58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x561a9088f6d8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int/prohibit_float_convert_int_case_1.cpp:3:1, line:10:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x561a9088fb50 <col:16, line:10:1>
    |-DeclStmt 0x561a9088f820 <line:4:5, col:20>
    | `-VarDecl 0x561a9088f798 <col:5, col:15> col:11 used f 'float' cinit
    |   `-FloatingLiteral 0x561a9088f800 <col:15> 'float' 3.140000e+00
    |-DeclStmt 0x561a9088f8b8 <line:5:5, col:10>
    | `-VarDecl 0x561a9088f850 <col:5, col:9> col:9 used i 'int'
    |-BinaryOperator 0x561a9088f940 <line:6:5, col:9> 'int' lvalue '='
    | |-DeclRefExpr 0x561a9088f8d0 <col:5> 'int' lvalue Var 0x561a9088f850 'i' 'int'
    | `-ImplicitCastExpr 0x561a9088f928 <col:9> 'int' <FloatingToIntegral>
    |   `-ImplicitCastExpr 0x561a9088f910 <col:9> 'float' <LValueToRValue>
    |     `-DeclRefExpr 0x561a9088f8f0 <col:9> 'float' lvalue Var 0x561a9088f798 'f' 'float'
    |-CallExpr 0x561a9088fac0 <line:8:5, col:21> 'int'
    | |-ImplicitCastExpr 0x561a9088faa8 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x561a9088fa28 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x561a9086c308 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x561a9088faf0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x561a9088f9e8 <col:12> 'const char[4]' lvalue "%d\n"
    | `-ImplicitCastExpr 0x561a9088fb08 <col:20> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x561a9088fa08 <col:20> 'int' lvalue Var 0x561a9088f850 'i' 'int'
    `-ReturnStmt 0x561a9088fb40 <line:9:5, col:12>
      `-IntegerLiteral 0x561a9088fb20 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for binary operators with assignment ('=') that represent assignment statements
2. Bind the binary operator as 'assignOp' for later retrieval
3. Within the assignment matcher, match the left-hand side (LHS) as an integer variable declaration reference
4. Bind the LHS as 'lhsVar' to identify the integer variable being assigned to
5. Within the assignment matcher, match the right-hand side (RHS) as a floating-point variable declaration reference
6. Bind the RHS as 'rhsVar' to identify the floating-point variable being assigned
7. Exclude cases where the RHS is an explicit cast expression (CStyleCastExpr or CXXStaticCastExpr) to filter compliant code
8. Exclude cases where the RHS is a constant expression to focus only on variable assignments
9. Combine all conditions to create a final matcher that triggers only for direct floating-point to integer variable assignments without explicit casts
**logic for check**:
1. Retrieve the bound binary operator node ('assignOp') from the match result
2. Retrieve the bound LHS variable declaration reference ('lhsVar') to identify the integer variable
3. Retrieve the bound RHS variable declaration reference ('rhsVar') to identify the floating-point variable
4. Get the source locations of the assignment operator and both variables for diagnostic reporting
5. Extract the type information from both variables to confirm integer and floating-point types
6. Verify that the assignment is indeed between variables (not constants) by checking the declarations
7. Emit a diagnostic message at the assignment location indicating the rule violation
8. Include the variable names and types in the diagnostic message for clarity
9. Ensure the diagnostic points to the exact location of the problematic assignment in the source code


## reference astMatchers
Narrowing Matcher: isValueDependent
 Parameters;
 return type Matcher<Expr>
 Description: Matches expression that are value-dependent because they contain a
non-type template parameter.

For example, the array bound of "Chars" in the following example is
value-dependent.
  template&lt;int Size&gt; int f() { return Size; }
expr(isValueDependent()) matches return Size

AST Traversal Matcher: ignoringParenCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after parentheses and
casts are stripped off.

Implicit and non-C Style casts are also discarded.
Given
  int a = 0;
  char b = (0);
  void* c = reinterpret_cast&lt;char*&gt;(0);
  char d = char(0);
The matcher
   varDecl(hasInitializer(ignoringParenCasts(integerLiteral())))
would match the declarations for a, b, c, and d.
while
   varDecl(hasInitializer(integerLiteral()))
only match the declaration for a.

AST Traversal Matcher: hasLHS
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<ArraySubscriptExpr>
 Description: Matches the left hand side of binary operator expressions.

Example matches a (matcher = binaryOperator(hasLHS()))
  a || b

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

Narrowing Matcher: equals
 Parameters;double Value
 return type Matcher<FloatingLiteral>
 Description: 

Narrowing Matcher: isAssignmentOperator
 Parameters;
 return type Matcher<BinaryOperator>
 Description: Matches all kinds of assignment operators.

Example 1: matches a += b (matcher = binaryOperator(isAssignmentOperator()))
  if (a == b)
    a += b;

Example 2: matches s1 = s2
           (matcher = cxxOperatorCallExpr(isAssignmentOperator()))
  struct S { S&amp; operator=(const S&amp;); };
  void x() { S s1, s2; s1 = s2; }

AST Traversal Matcher: capturesVar
 Parameters;Matcher<ValueDecl> InnerMatcher
 Return type Matcher<LambdaCapture>
 Description: Matches a `LambdaCapture` that refers to the specified `VarDecl`. The
`VarDecl` can be a separate variable that is captured by value or
reference, or a synthesized variable if the capture has an initializer.

Given
  void foo() {
    int x;
    auto f = [x](){};
    auto g = [x = 1](){};
  }
In the matcher
lambdaExpr(hasAnyCapture(lambdaCapture(capturesVar(hasName("x")))),
capturesVar(hasName("x")) matches `x` and `x = 1`.

implicitCastExpr(unless(hasParent(cxxStaticCastExpr())))
Finder->addMatcher(stmt(forEachDescendant(binaryOperator(allOf(isAssignmentOperator(), hasRHS(RefVarOrField), hasLHS(anyOf(declRefExpr(to(varDecl().bind("pot_tid_var"))), memberExpr(member(fieldDecl().bind("pot_tid_field")))))))), this);
BindableMatcher<clang::Stmt> charCastExpression(bool IsSigned, const Matcher<clang::QualType> &IntegerType, const std::string &CastBindName) const {
  const auto IntTypedef = qualType(hasDeclaration(typedefDecl(hasAnyName(utils::options::parseStringList(CharTypdefsToIgnoreList)))));
  auto CharTypeExpr = expr();
  if (IsSigned) {
    CharTypeExpr = expr(hasType(qualType(isAnyCharacter(), isSignedInteger(), unless(IntTypedef))));
  } else {
    CharTypeExpr = expr(hasType(qualType(isAnyCharacter(), unless(isSignedInteger()), unless(IntTypedef))));
  }
  const auto ImplicitCastExpr = implicitCastExpr(hasSourceExpression(CharTypeExpr), hasImplicitDestinationType(IntegerType)).bind(CastBindName);
  const auto CStyleCastExpr = cStyleCastExpr(has(ImplicitCastExpr));
  const auto StaticCastExpr = cxxStaticCastExpr(has(ImplicitCastExpr));
  const auto FunctionalCastExpr = cxxFunctionalCastExpr(has(ImplicitCastExpr));
  return traverse(TK_AsIs, expr(anyOf(ImplicitCastExpr, CStyleCastExpr, StaticCastExpr, FunctionalCastExpr)));
}
StatementMatcher LoopVarConversionMatcher = traverse(TK_AsIs, implicitCastExpr(hasImplicitDestinationType(isInteger()), has(ignoringParenImpCasts(LoopVarMatcher))).bind(LoopVarCastName));
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}
Finder->addMatcher(
  cxxOperatorCallExpr(
    hasAnyOverloadedOperatorName("=", "+="),
    callee(cxxMethodDecl(ofClass(classTemplateSpecializationDecl(
      hasName("::std::basic_string"),
      hasTemplateArgument(0, refersToType(hasCanonicalType(
        qualType().bind("type")))))))),
    hasArgument(1,
      ignoringImpCasts(
        expr(hasType(isInteger()), unless(hasType(isAnyCharacter())),
          unless(callExpr(callee(functionDecl(
            hasAnyName("tolower", "std::tolower", "toupper",
                      "std::toupper"))))),
          unless(hasType(qualType(
            hasCanonicalType(equalsBoundNode("type"))))))
          .bind("expr"))),
    unless(isInTemplateInstantiation())
  ),
  this
);


## reference api  
SourceManager &SM = *Result.SourceManager;
const auto *FirstDecl = cast<CXXMethodDecl>(MatchedDecl->getFirstDecl());
const SourceLocation FirstDeclEnd = utils::lexer::findNextTerminator(
    FirstDecl->getEndLoc(), SM, getLangOpts());
const CharSourceRange SecondDeclRange = CharSourceRange::getTokenRange(
    MatchedDecl->getBeginLoc(),
    utils::lexer::findNextTerminator(MatchedDecl->getEndLoc(), SM,
                                     getLangOpts()));
if (FirstDeclEnd.isInvalid() || SecondDeclRange.isInvalid())
  return;
const auto *const Referencee = Result.Nodes.getNodeAs<VarDecl>("referencee");
if (Result.Nodes.getNodeAs<CXXMethodDecl>("cv"))
  diag(Method->getBeginLoc(),
       "operator=() should not be marked '%select{const|virtual}0'")
      << !Method->isConst();
std::optional<SourceRange>
getTypeSpecifierLocation(const VarDecl *Var,
                         const MatchFinder::MatchResult &Result) {
  SourceRange TypeSpecifier(
      Var->getTypeSpecStartLoc(),
      Var->getTypeSpecEndLoc().getLocWithOffset(Lexer::MeasureTokenLength(
          Var->getTypeSpecEndLoc(), *Result.SourceManager,
          Result.Context->getLangOpts())));

  if (TypeSpecifier.getBegin().isMacroID() ||
      TypeSpecifier.getEnd().isMacroID())
    return std::nullopt;
  return TypeSpecifier;
}
static double getValue(const IntegerLiteral *IntLit,
                     const FloatingLiteral *FloatLit) {
  if (IntLit)
    return IntLit->getValue().getLimitedValue();

  assert(FloatLit != nullptr && "Neither IntLit nor FloatLit set");
  return FloatLit->getValueAsApproximateDouble();
}
auto Diag = [&] {
  if (MatchedCallExpr->getNumArgs() == 3) {
    auto DiagL =
        diag(MatchedCallExpr->getBeginLoc(),
             "'std::random_shuffle' has been removed in C++17; use "
             "'std::shuffle' and an alternative random mechanism instead");
    DiagL << FixItHint::CreateReplacement(
        MatchedArgumentThree->getSourceRange(),
        "std::mt19937(std::random_device()())");
    return DiagL;
  }
  auto DiagL = diag(MatchedCallExpr->getBeginLoc(),
                    "'std::random_shuffle' has been removed in C++17; use "
                    "'std::shuffle' instead");
  DiagL << FixItHint::CreateInsertion(
      MatchedCallExpr->getRParenLoc(),
      ", std::mt19937(std::random_device()())");
  return DiagL;
}();
SourceLocation ReportLoc = FunctorLoc.getLocation();
if (ReportLoc.isInvalid())
  return;
diag(ReportLoc, Message) << FuncClass->getName()
                         << FixItHint::CreateRemoval(
                                FunctorTypeLoc.getArgLoc(0).getSourceRange());
diag(MatchedDecl->getLocation(), "operator=() does not handle self-assignment properly");
const auto *PtrArith = Result.Nodes.getNodeAs<BinaryOperator>("PtrArith");
if (!PtrArith)
  return;
Expr * clang::BinaryOperator::getRHS() const
bool llvm::Type::isFloatingPointTy() const
void clang::DiagnosticOptions::setFormat(TextDiagnosticFormat Value)
uintptr_t clang::DeclarationName::getAsOpaqueInteger() const
SourceLocation clang::ento::PathDiagnosticLocation::getValidSourceLocation(const Stmt * S, LocationOrAnalysisDeclContext LAC, bool UseEndOfStatement)
void clang::PartialDiagnostic::EmitToString(DiagnosticsEngine & Diags, SmallVectorImpl<char> & Buf) const
bool clang::BinaryOperator::isAssignmentOp() const
Opcode clang::BinaryOperator::getOpForCompoundAssignment(Opcode Opc)
SourceLocation clang::SourceLocExpr::getLocation() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitFloatConvertIntCheck.cpp :
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
          hasOperatorName("="),
          hasLHS(expr(hasType(isInteger())).bind("lhs")),
          hasRHS(expr(
              hasType(realFloatingPointType()),
              // Exclude floating literals (direct constant assignments)
              unless(ignoringParenImpCasts(floatLiteral())),
              // Exclude integer literals (though they have floating type context)
              unless(ignoringParenImpCasts(integerLiteral())),
              // Exclude explicit casts to integer type
              unless(hasDescendant(explicitCastExpr(hasDestinationType(isInteger())))),
              // Exclude implicit casts that are not from floating to integer
              unless(hasParent(implicitCastExpr(hasImplicitDestinationType(isInteger()))))
          ).bind("rhs"))
      ).bind("assignOp"),
      this);
}

void ProhibitFloatConvertIntCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AssignOp = Result.Nodes.getNodeAs<BinaryOperator>("assignOp");
  const auto *LHS = Result.Nodes.getNodeAs<Expr>("lhs");
  const auto *RHS = Result.Nodes.getNodeAs<Expr>("rhs");
  
  if (!AssignOp || !AssignOp->getOperatorLoc().isValid() ||
      !LHS || !LHS->getExprLoc().isValid() ||
      !RHS || !RHS->getExprLoc().isValid()) {
    return;
  }
  
  // Verify LHS is integer type
  if (!LHS->getType()->isIntegerType()) {
    return;
  }
  
  // Verify RHS is floating type
  if (!RHS->getType()->isFloatingType()) {
    return;
  }
  
  // Check if RHS is a constant expression (exempt per rule)
  // We already excluded literals in matcher, but check for other constant expressions
  Expr::EvalResult EvalResult;
  if (RHS->isValueDependent() || RHS->isTypeDependent()) {
    return;
  }
  
  // Check if RHS evaluates to a constant (excluding literals)
  if (RHS->EvaluateAsConstantExpr(EvalResult, *Result.Context)) {
    // Allow constant expressions as per rule description
    return;
  }
  
  // Check for explicit cast in the RHS expression tree
  // Look for explicit cast to integer type in the RHS
  bool HasExplicitCast = false;
  auto CheckForExplicitCast = [&](const Expr *E) {
    if (const auto *CE = dyn_cast<ExplicitCastExpr>(E)) {
      if (CE->getTypeAsWritten()->isIntegerType()) {
        HasExplicitCast = true;
      }
    }
  };
  
  // Traverse the RHS expression to check for explicit casts
  std::function<void(const Expr*)> TraverseExpr = [&](const Expr *E) {
    if (!E || HasExplicitCast) return;
    
    CheckForExplicitCast(E);
    
    // Check children
    for (const Stmt *Child : E->children()) {
      if (const Expr *ChildExpr = dyn_cast_or_null<Expr>(Child)) {
        TraverseExpr(ChildExpr);
      }
    }
  };
  
  TraverseExpr(RHS);
  
  if (HasExplicitCast) {
    return;
  }
  
  // Emit diagnostic with source ranges
  auto Diag = diag(AssignOp->getOperatorLoc(), 
                   "禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]");
  
  // Add source ranges for LHS and RHS
  Diag << SourceRange(LHS->getBeginLoc(), LHS->getEndLoc())
       << SourceRange(RHS->getBeginLoc(), RHS->getEndLoc());
}

} // namespace clang::tidy::ucassaat
```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/ProhibitFloatConvertIntCheck.h :
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