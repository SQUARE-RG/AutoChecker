针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_4.cpp生成first checker
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
    int *p = NULL;
    p = (int*) calloc(1, sizeof(int));
    p[0] = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
```

## AST
TranslationUnitDecl 0x564c3e2d91c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x564c3e3ff0b8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_4.cpp:3:1, line:9:1> line:3:6 foo 'void ()'
  `-CompoundStmt 0x564c3e3ff4e0 <line:4:1, line:9:1>
    |-DeclStmt 0x564c3e3ff210 <line:5:5, col:18>
    | `-VarDecl 0x564c3e3ff178 <col:5, /root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> /root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_4.cpp:5:10 used p 'int *' cinit
    |   `-ImplicitCastExpr 0x564c3e3ff1f8 </root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> 'int *' <NullToPointer>
    |     `-GNUNullExpr 0x564c3e3ff1e0 <col:18> 'long'
    |-BinaryOperator 0x564c3e3ff408 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_4.cpp:6:5, col:37> 'int *' lvalue '='
    | |-DeclRefExpr 0x564c3e3ff228 <col:5> 'int *' lvalue Var 0x564c3e3ff178 'p' 'int *'
    | `-CStyleCastExpr 0x564c3e3ff3e0 <col:9, col:37> 'int *' <BitCast>
    |   `-CallExpr 0x564c3e3ff380 <col:16, col:37> 'void *'
    |     |-ImplicitCastExpr 0x564c3e3ff368 <col:16> 'void *(*)(size_t, size_t) noexcept(true)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x564c3e3ff2e8 <col:16> 'void *(size_t, size_t) noexcept(true)' lvalue Function 0x564c3e3e0d40 'calloc' 'void *(size_t, size_t) noexcept(true)' (UsingShadow 0x564c3e3fdf78 'calloc')
    |     |-ImplicitCastExpr 0x564c3e3ff3b0 <col:23> 'size_t':'unsigned long' <IntegralCast>
    |     | `-IntegerLiteral 0x564c3e3ff290 <col:23> 'int' 1
    |     `-UnaryExprOrTypeTraitExpr 0x564c3e3ff2c8 <col:26, col:36> 'unsigned long' sizeof 'int'
    `-BinaryOperator 0x564c3e3ff4c0 <line:7:5, col:12> 'int' lvalue '='
      |-ArraySubscriptExpr 0x564c3e3ff480 <col:5, col:8> 'int' lvalue
      | |-ImplicitCastExpr 0x564c3e3ff468 <col:5> 'int *' <LValueToRValue>
      | | `-DeclRefExpr 0x564c3e3ff428 <col:5> 'int *' lvalue Var 0x564c3e3ff178 'p' 'int *'
      | `-IntegerLiteral 0x564c3e3ff448 <col:7> 'int' 0
      `-IntegerLiteral 0x564c3e3ff4a0 <col:12> 'int' 1


## reference logic step
**logic for registerMatchers**:
1. Define a matcher to identify function calls to dynamic memory allocation functions: malloc, calloc, realloc, and their C++ equivalents (new, new[]). Use callee(functionDecl(hasAnyName(...))) to match these calls.
2. Match variable declarations that are initialized with a call to one of these allocation functions, and bind the variable declaration as 'allocVar'.
3. Match assignment expressions where the right-hand side is a call to an allocation function and the left-hand side is a variable (possibly a global or local), bind the variable as 'allocVar' and the assignment as 'allocAssign'.
4. For each bound variable, match its subsequent uses (e.g., array subscript, member access, implicit cast) within the same scope, but before any null check is performed on that variable. Use hasAncestor or traversal matchers to limit scope.
5. Match any null-check expressions involving the bound variable: binary comparisons (==, !=) with NULL/nullptr, or unary '!' operator on the variable, or the variable used directly as a condition (implicit boolean conversion). Bind these as 'nullCheck'.
6. Combine these matchers: for each allocation, if there is a use of the variable before any nullCheck exists in the control flow, trigger a match. Use anyOf to match different forms of allocation (direct init, assignment, etc.) and bind the variable name and location.
**logic for check**:
1. Retrieve the bound variable declaration ('allocVar') and the allocation expression (call or assignment) from the match result.
2. Determine the scope (function, block, or global) where the allocation occurred and collect all uses of the variable within that scope after the allocation point.
3. Identify any null-check nodes ('nullCheck') that involve the same variable. If no nullCheck exists before the first use, proceed to emit a warning.
4. If a nullCheck exists, verify its position relative to the first use: the check must occur before the first dereference or access. If the first use occurs before the check, it is a violation.
5. For reallocation (realloc), treat the new allocation as a separate event: check that a new nullCheck occurs after the realloc call and before any subsequent use.
6. Emit a single warning per violating pointer variable, using the diagnostic message: '禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]'.
7. Ensure no duplicate warnings for the same variable by tracking already-reported variables within the current compilation unit.


## reference astMatchers
Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Type>
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

Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<QualType>
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

Finder->addMatcher(
      binaryOperator(hasAnyOperatorName("==", "!="),
                     hasOperands(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                                       integerLiteral(equals(0))),
                                 callToGet(knownSmartptr()))),
      Callback);
auto IsAlwaysFalse = expr(anyOf(cxxBoolLiteral(equals(false)), integerLiteral(equals(0)), cxxNullPtrLiteralExpr(), gnuNullExpr(), NegatedString)).bind("isAlwaysFalse");
binaryOperator(hasOperands(anyOf(cxxNullPtrLiteralExpr(), integerLiteral(equals(0))), PointerExpr))


## reference api
if (const auto *DeclRef = dyn_cast<DeclRefExpr>(PtrInputExpr->IgnoreParenImpCasts()))
  if (const auto *Var = dyn_cast<VarDecl>(DeclRef->getDecl()))
    if (const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>("parent_function"))
      if (FindAssignToVarBefore{Var, DeclRef, SM}.Visit(Func->getBody()))
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
if (checkConditionVarUsageInElse(If) != nullptr) {
  if (!WarnOnConditionVariables)
    return;
  if (IsLastInScope) {
    DiagnosticBuilder Diag = diag(ElseLoc, WarningMessage)
                             << ControlFlowInterruptor
                             << SourceRange(ElseLoc);
    if (checkInitDeclUsageInElse(If) != nullptr) {
      Diag << tooling::fixit::createReplacement(
                  SourceRange(If->getIfLoc()),
                  (tooling::fixit::getText(*If->getInit(), *Result.Context) +
                   llvm::StringRef("\n"))
                      .str())
           << tooling::fixit::createRemoval(If->getInit()->getSourceRange());
    }
    const DeclStmt *VDeclStmt = If->getConditionVariableDeclStmt();
    const VarDecl *VDecl = If->getConditionVariable();
    std::string Repl =
        (tooling::fixit::getText(*VDeclStmt, *Result.Context) +
         llvm::StringRef(";\n") +
         tooling::fixit::getText(If->getIfLoc(), *Result.Context))
            .str();
    Diag << tooling::fixit::createReplacement(SourceRange(If->getIfLoc()), Repl)
         << tooling::fixit::createReplacement(VDeclStmt->getSourceRange(),
                                              VDecl->getName());
    removeElseAndBrackets(Diag, *Result.Context, Else, ElseLoc);
  } else if (WarnOnUnfixable) {
    diag(ElseLoc, WarningMessage) << ControlFlowInterruptor;
  }
  return;
}
bool clang::BinaryOperator::isNullPointerArithmeticExtension(ASTContext & Ctx, Opcode Opc, const Expr * LHS, const Expr * RHS)
SourceLocation clang::DependentScopeDeclRefExpr::getLocation() const
unsigned int clang::ParmVarDecl::getFunctionScopeDepth() const


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
#include "clang/AST/ASTTypeTraits.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/Lex/Lexer.h"
#include "llvm/ADT/SmallPtrSet.h"
#include <algorithm>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Match VarDecl with initializer containing malloc, calloc, realloc, or aligned_alloc
  auto AllocFuncMatcher = callee(functionDecl(anyOf(
      hasName("::malloc"),
      hasName("::calloc"),
      hasName("::realloc"),
      hasName("::aligned_alloc")
  )));
  
  auto AllocExprMatcher = callExpr(AllocFuncMatcher);
  
  Finder->addMatcher(
    varDecl(
      hasInitializer(ignoringParenCasts(AllocExprMatcher)),
      unless(hasAncestor(functionDecl(isImplicit())))
    ).bind("allocated_ptr"),
    this
  );
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Var = Result.Nodes.getNodeAs<VarDecl>("allocated_ptr");
  if (!Var)
    return;
  
  ASTContext *Context = Result.Context;
  SourceManager &SM = Context->getSourceManager();
  
  // Get the allocation expression
  const Expr *InitExpr = Var->getInit();
  if (!InitExpr)
    return;
  
  // Skip if the variable is never used
  if (!Var->isReferenced())
    return;
  
  // Find the parent function or compound statement
  const auto *ParentDC = Var->getDeclContext();
  if (!ParentDC)
    return;
  
  // Use getNonClosureContext() to get the enclosing non-closure context
  const auto *NonClosureCtx = ParentDC->getNonClosureContext();
  if (!NonClosureCtx)
    return;
  
  const auto *FuncDecl = dyn_cast<FunctionDecl>(NonClosureCtx);
  if (!FuncDecl || !FuncDecl->hasBody())
    return;
  
  const Stmt *FuncBody = FuncDecl->getBody();
  if (!FuncBody)
    return;
  
  // Collect all DeclRefExpr nodes referencing this variable
  llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs;
  std::function<void(const Stmt*)> CollectDeclRefs = [&](const Stmt *S) {
    if (!S) return;
    if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
      if (DRE->getDecl() == Var) {
        AllVarRefs.insert(DRE);
      }
    }
    for (const auto *Child : S->children()) {
      CollectDeclRefs(Child);
    }
  };
  CollectDeclRefs(FuncBody);
  
  // Collect all uses of the pointer (excluding the allocation itself)
  struct UseInfo {
    const Stmt *StmtNode;
    SourceLocation Loc;
    bool IsCheck;
  };
  std::vector<UseInfo> Uses;
  
  // Traverse the parent statement to find all uses
  std::function<void(const Stmt*)> CollectUses = [&](const Stmt *S) {
    if (!S) return;
    
    if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
      if (DRE->getDecl() == Var) {
        // Check if this is a null check
        bool IsCheck = false;
        // Check for binary comparison with nullptr/NULL
        const auto Parents = Context->getParents(*S);
        if (!Parents.empty()) {
          if (const auto *BO = dyn_cast_or_null<BinaryOperator>(Parents.begin()->get<Stmt>())) {
            if (BO->isComparisonOp() && 
                (BO->getOpcode() == BO_EQ || BO->getOpcode() == BO_NE)) {
              const Expr *Other = (BO->getLHS() == S) ? BO->getRHS() : BO->getLHS();
              if (Other && Other->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull) != Expr::NPCK_NotNull) {
                IsCheck = true;
                Uses.push_back(UseInfo{BO, BO->getExprLoc(), true});
                return;
              }
            }
          }
          // Check for unary '!' operator
          if (const auto *UO = dyn_cast_or_null<UnaryOperator>(Parents.begin()->get<Stmt>())) {
            if (UO->getOpcode() == UO_LNot) {
              IsCheck = true;
              Uses.push_back(UseInfo{UO, UO->getExprLoc(), true});
              return;
            }
          }
          // Check for implicit conversion in if/while condition
          if (const auto *IfS = dyn_cast_or_null<IfStmt>(Parents.begin()->get<Stmt>())) {
            if (IfS->getCond() == S) {
              IsCheck = true;
              Uses.push_back(UseInfo{IfS, IfS->getBeginLoc(), true});
              return;
            }
          }
        }
        if (!IsCheck) {
          Uses.push_back(UseInfo{S, DRE->getLocation(), false});
        }
      }
    }
    
    // Recursively traverse children
    for (const auto *Child : S->children()) {
      CollectUses(Child);
    }
  };
  
  CollectUses(FuncBody);
  
  // Sort uses by source location
  std::sort(Uses.begin(), Uses.end(), [&](const UseInfo &A, const UseInfo &B) {
    return SM.isBeforeInTranslationUnit(A.Loc, B.Loc);
  });
  
  // Check for null check before first use
  bool FoundCheckBeforeUse = false;
  bool HasReported = false;
  const Stmt *FirstUse = nullptr;
  
  for (const auto &Use : Uses) {
    if (Use.IsCheck) {
      FoundCheckBeforeUse = true;
      break;
    }
    if (!FirstUse) {
      FirstUse = Use.StmtNode;
    }
  }
  
  // If no null check found before first use, report warning
  if (!FoundCheckBeforeUse && FirstUse && !HasReported) {
    bool HasActualUse = false;
    for (const auto &Use : Uses) {
      if (!Use.IsCheck) {
        HasActualUse = true;
        break;
      }
    }
    
    if (HasActualUse) {
      diag(FirstUse->getBeginLoc(), "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]");
      HasReported = true;
    }
  }
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
