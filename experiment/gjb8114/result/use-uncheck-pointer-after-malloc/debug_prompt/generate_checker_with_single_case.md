针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp生成first checker
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
The rule requires that any pointer obtained through dynamic memory allocation functions (such as malloc, calloc, or realloc) must be checked for non-null before its first use. This check must occur before the pointer is used; performing the check after use is considered a violation. Acceptable check methods include explicit or implicit null pointer comparisons like if (ptr != NULL), if (ptr), or if (!ptr). If a dynamically allocated pointer is never used, it does not violate this rule. If a pointer is reallocated, it must be checked again before any subsequent use. This rule applies equally to global and local variables. Only one warning should be reported per violating pointer variable.
Scenarios that should be reported include: using a dynamically allocated pointer directly without any null check, performing a null check only after the pointer has been used, using a global variable after dynamic allocation without a check, and using pointers from calloc or realloc without a prior check.
Correct scenarios include: performing a null check immediately after allocation and using the pointer only after the check passes, not using the pointer after allocation, or not using a pointer after it has been reallocated. Various forms of null pointer checks, including shorthand forms, are acceptable.

## test case code
**Test Case Code:**
```cpp
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    if (p == nullptr)
    {
        return;
    }
}
```

## AST
TranslationUnitDecl 0x55c120c441c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55c120d69ef8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp:3:1, line:12:1> line:3:6 foo 'void ()'
  `-CompoundStmt 0x55c120d6a318 <line:4:1, line:12:1>
    |-DeclStmt 0x55c120d6a1a8 <line:5:5, col:40>
    | `-VarDecl 0x55c120d69fb8 <col:5, col:39> col:10 used p 'int *' cinit
    |   `-CStyleCastExpr 0x55c120d6a180 <col:14, col:39> 'int *' <BitCast>
    |     `-CallExpr 0x55c120d6a140 <col:21, col:39> 'void *'
    |       |-ImplicitCastExpr 0x55c120d6a128 <col:21> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x55c120d6a0a0 <col:21> 'void *(size_t) noexcept(true)' lvalue Function 0x55c120d4b7d0 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x55c120d69358 'malloc')
    |       `-UnaryExprOrTypeTraitExpr 0x55c120d6a080 <col:28, col:38> 'unsigned long' sizeof 'int'
    |-BinaryOperator 0x55c120d6a230 <line:6:5, col:10> 'int' lvalue '='
    | |-UnaryOperator 0x55c120d6a1f8 <col:5, col:6> 'int' lvalue prefix '*' cannot overflow
    | | `-ImplicitCastExpr 0x55c120d6a1e0 <col:6> 'int *' <LValueToRValue>
    | |   `-DeclRefExpr 0x55c120d6a1c0 <col:6> 'int *' lvalue Var 0x55c120d69fb8 'p' 'int *'
    | `-IntegerLiteral 0x55c120d6a210 <col:10> 'int' 1
    `-IfStmt 0x55c120d6a2f8 <line:8:5, line:11:5>
      |-BinaryOperator 0x55c120d6a2b0 <line:8:9, col:14> 'bool' '=='
      | |-ImplicitCastExpr 0x55c120d6a280 <col:9> 'int *' <LValueToRValue>
      | | `-DeclRefExpr 0x55c120d6a250 <col:9> 'int *' lvalue Var 0x55c120d69fb8 'p' 'int *'
      | `-ImplicitCastExpr 0x55c120d6a298 <col:14> 'int *' <NullToPointer>
      |   `-CXXNullPtrLiteralExpr 0x55c120d6a270 <col:14> 'std::nullptr_t'
      `-CompoundStmt 0x55c120d6a2e0 <line:9:5, line:11:5>
        `-ReturnStmt 0x55c120d6a2d0 <line:10:9>


## reference logic step
**logic for registerMatchers**:
1. Define a list of dynamic memory allocation functions (malloc, calloc, realloc) using known names and user-configurable options.
2. Create a matcher for calls to these allocation functions and bind the CallExpr as 'allocCall'.
3. Create a matcher for VarDecl nodes that are initialized with the result of such a call (or have their value later assigned from such a call) and bind the VarDecl as 'allocVar'.
4. Create a matcher for DeclRefExpr nodes that reference the 'allocVar' to track all uses of the pointer.
5. Create a matcher for UnaryOperator nodes of dereference type (*) or ArraySubscriptExpr nodes where the base is a DeclRefExpr referencing 'allocVar', to identify pointer uses.
6. Create a matcher for BinaryOperator nodes that represent comparisons (==, !=) between a DeclRefExpr of 'allocVar' and a null pointer constant, to identify null checks.
7. Create a matcher for IfStmt, WhileStmt, DoStmt, ForStmt, or ConditionalOperator nodes whose condition contains an implicit or explicit null check on 'allocVar' (e.g., if(ptr), if(!ptr), if(ptr != NULL)).
8. Combine the above matchers to find sequences where a 'use' of 'allocVar' occurs before any 'nullCheck' on that same variable within the same function scope.
9. Ensure the matcher binds the first violating 'use' node as 'firstBadUse' and the associated 'allocVar'.
**logic for check**:
1. Retrieve the bound VarDecl node 'allocVar' and the Stmt node 'firstBadUse' from the match result.
2. Traverse the AST subtree of the function containing 'allocVar' to collect all Stmts related to this variable: its allocation, all its uses (dereferences, subscript, passing as argument requiring non-null), and all its null checks.
3. Order these collected Stmts by their source location (source order).
4. Determine the location of the allocation statement for this variable.
5. Iterate through the ordered list. For each 'use' statement, check if a null check statement for this variable exists before it in the order. If not, this is a violation.
6. If a violation is found, emit a diagnostic at the location of 'firstBadUse' (or the first violating use) pointing to the variable name and the rule.
7. Ensure that for each variable, only one warning is emitted (for its first violating use).
8. Handle special cases: if the variable is never used, no warning; if reallocated, treat the new allocation as a new allocation point and restart checking for subsequent uses.
9. Consider control flow: a null check must dominate the use in the CFG. For simplicity, initial implementation may assume linear order, but note that advanced implementation would require CFG analysis.


## reference astMatchers
Narrowing Matcher: argumentCountAtLeast
 Parameters;unsigned N
 return type Matcher<CallExpr>
 Description: Checks that a call expression or a constructor call expression has at least
the specified number of arguments (including absent default arguments).

Example matches f(0, 0) and g(0, 0, 0)
(matcher = callExpr(argumentCountAtLeast(2)))
  void f(int x, int y);
  void g(int x, int y, int z);
  f(0, 0);
  g(0, 0, 0);

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

Node Matcher: declRefExpr
 Parameters;Matcher<DeclRefExpr>...
 return type Matcher<Stmt>
 Description: Matches expressions that refer to declarations.

Example matches x in if (x)
  bool x;
  if (x) {}

Narrowing Matcher: nullPointerConstant
 Parameters;
 return type Matcher<Expr>
 Description: Matches expressions that resolve to a null pointer constant, such as
GNU's __null, C++11's nullptr, or C's NULL macro.

Given:
  void *v1 = NULL;
  void *v2 = nullptr;
  void *v3 = __null; // GNU extension
  char *cp = (char *)0;
  int *ip = 0;
  int i = 0;
expr(nullPointerConstant())
  matches the initializer for v1, v2, v3, cp, and ip. Does not match the
  initializer for i.

Narrowing Matcher: hasDynamicExceptionSpec
 Parameters;
 return type Matcher<FunctionDecl>
 Description: Matches functions that have a dynamic exception specification.

Given:
  void f();
  void g() noexcept;
  void h() noexcept(true);
  void i() noexcept(false);
  void j() throw();
  void k() throw(int);
  void l() throw(...);
functionDecl(hasDynamicExceptionSpec()) and
  functionProtoType(hasDynamicExceptionSpec())
  match the declarations of j, k, and l, but not f, g, h, or i.

Node Matcher: unaryOperator
 Parameters;Matcher<UnaryOperator>...
 return type Matcher<Stmt>
 Description: Matches unary operator expressions.

Example matches !a
  !a || b

Node Matcher: varDecl
 Parameters;Matcher<VarDecl>...
 return type Matcher<Decl>
 Description: Matches variable declarations.

Note: this does not match declarations of member variables, which are
"field" declarations in Clang parlance.

Example matches a
  int a;

Node Matcher: cxxNullPtrLiteralExpr
 Parameters;Matcher<CXXNullPtrLiteralExpr>...
 return type Matcher<Stmt>
 Description: Matches nullptr literal.

Finder->addMatcher(functionDecl(isDefinition(), hasBody(stmt()), hasAnyParameter(decl()), unless(hasAttr(attr::Kind::Naked))).bind("function"), this);
AST_POLYMORPHIC_MATCHER_P(boolean, AST_POLYMORPHIC_SUPPORTED_TYPES(Stmt, Decl), bool, Boolean) { return Boolean; }
varDecl(isStaticLocal())
binaryOperator(hasOperands(anyOf(cxxNullPtrLiteralExpr(), integerLiteral(equals(0))), PointerExpr))
unaryOperator(hasOperatorName("*"), has(implicitCastExpr(hasCastKind(CK_FunctionToPointerDecay))))
Finder->addMatcher(cxxOperatorCallExpr(anyOf(AssignOperator, PlusOperator)), this);
Finder->addMatcher(declRefExpr(to(functionDecl().bind("func"))).bind("use-site"), this);
const auto AllocFunc = functionDecl(hasAnyName("malloc","::malloc", "std::malloc","alloca", "::alloca", "calloc","::calloc", "std::calloc", "::realloc", "realloc","std::realloc"));
const auto AllocCall = callExpr(callee(decl(anyOf(AllocFunc, AllocFuncPtr))));


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
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
const auto *Var = Result.Nodes.getNodeAs<VarDecl>("vardecl");
const auto *CtorCall = Result.Nodes.getNodeAs<Expr>("ctor_call");
if (!Var || !CtorCall)
  return;
static const char *UseUsingWarning = "use 'using' instead of 'typedef'";
if (MatchedDecl->getUnderlyingType()->isArrayType() || StartLoc.isMacroID()) {
  diag(StartLoc, UseUsingWarning);
  return;
}
bool FindAssignToVarBefore::isAccessForVar(const Expr *E) const {
  if (const auto *DeclRef = dyn_cast<DeclRefExpr>(E->IgnoreParenCasts()))
    return DeclRef->getDecl() &&
           DeclRef->getDecl()->getCanonicalDecl() == Var &&
           SM.isBeforeInTranslationUnit(E->getBeginLoc(),
                                        VarRef->getBeginLoc());
  return false;
}
if (std::optional<std::vector<SourceLocation>> Errors =
        analyzeFunction(*FuncDecl, *Result.Context, ModelOptions))
  for (const SourceLocation &Loc : *Errors)
    diag(Loc, "unchecked access to optional value");
const Expr *AllocExpr = PtrArith->getLHS()->IgnoreParenCasts();
if (!isExprValueStored(NewExpr1, *Result.Context) &&
    !isExprValueStored(NewExpr2, *Result.Context))
  return;
diag(S->getUsedLocation(),
     "calling a function that uses a default argument is disallowed");
SourceRange clang::StmtSequence::getSourceRange() const
SourceLocation clang::OMPDestroyClause::getVarLoc() const
bool clang::MacroInfo::isWarnIfUnused() const
StringRef clang::DiagnosticIDs::getWarningOptionForGroup(diag::Group)
ArrayRef<Expr *> clang::MSAsmStmt::getAllExprs() const
void clang::PartialDiagnostic::EmitToString(DiagnosticsEngine & Diags, SmallVectorImpl<char> & Buf) const
bool clang::TypeLoc::isNull() const
Expr * clang::OMPAllocatorClause::getAllocator() const
bool clang::StoredDeclsList::isNull() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp :
```cpp
//===--- UseUncheckPointerAfterMallocCheck.cpp - clang-tidy ---------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "UseUncheckPointerAfterMallocCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.h :
```cpp
//===--- UseUncheckPointerAfterMallocCheck.h - clang-tidy -------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/use-uncheck-pointer-after-malloc.html
class UseUncheckPointerAfterMallocCheck : public ClangTidyCheck {
public:
  UseUncheckPointerAfterMallocCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H

```

# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
    -In the check() function, all extracted nodes must be checked for non-null to avoid direct usage
    
## **Example Output Format:**

    checker_cpp:
    ```cpp
        ....(source code)....
    ```

    checker_h:
    ```cpp
        ....(source code)....
    ```