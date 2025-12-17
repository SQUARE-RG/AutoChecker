针对正例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

# Inputs

## rule
**Rule Description:**
The rule requires that any pointer obtained through dynamic memory allocation functions (such as malloc, calloc, or realloc) must be checked for non-null before its first use. This check must occur before the pointer is used; performing the check after use is considered a violation. Acceptable check methods include explicit or implicit null pointer comparisons like if (ptr != NULL), if (ptr), or if (!ptr). If a dynamically allocated pointer is never used, it does not violate this rule. If a pointer is reallocated, it must be checked again before any subsequent use. This rule applies equally to global and local variables. Only one warning should be reported per violating pointer variable.
Scenarios that should be reported include: using a dynamically allocated pointer directly without any null check, performing a null check only after the pointer has been used, using a global variable after dynamic allocation without a check, and using pointers from calloc or realloc without a prior check.
Correct scenarios include: performing a null check immediately after allocation and using the pointer only after the check passes, not using the pointer after allocation, or not using a pointer after it has been reallocated. Various forms of null pointer checks, including shorthand forms, are acceptable.

## current checker code

checker_cpp:
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
#include "clang/Lex/Lexer.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Expr.h"
#include "clang/AST/OperationKinds.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallPtrSet.h"
#include <string>
#include <map>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Matcher for dynamic memory allocation functions
const auto AllocFuncMatcher = functionDecl(
    hasAnyName("::malloc", "::calloc", "::realloc", "std::malloc", 
               "std::calloc", "std::realloc"));

// Matcher for allocation calls
const auto AllocCallMatcher = callExpr(
    callee(AllocFuncMatcher),
    unless(hasAncestor(callExpr()))).bind("allocCall");

// Helper matcher to find the pointer variable from allocation
const auto PointerVarFromAllocMatcher = stmt(anyOf(
    // Direct assignment: p = malloc()
    binaryOperator(hasOperatorName("="),
        hasLHS(expr(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("ptrVar")))))),
        hasRHS(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))),
    // Variable declaration with initialization: int *p = malloc()
    declStmt(hasSingleDecl(varDecl(
        hasInitializer(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher)))),
        hasType(pointerType()))
        .bind("ptrVarDecl")))
)).bind("allocExpr");

// Matcher for pointer usage
const auto PointerUseMatcher = expr(
    anyOf(
        // Dereference: *p
        unaryOperator(hasOperatorName("*"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Array subscript: p[0]
        arraySubscriptExpr(
            hasBase(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Member access through pointer: p->field
        memberExpr(hasObjectExpression(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar")))))),
        // Function call through pointer: p()
        callExpr(has(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar"))))))
    )).bind("pointerUse");

// Matcher for null pointer checks
const auto NullCheckMatcher = stmt(
    anyOf(
        // Explicit comparisons: ptr == NULL, ptr != NULL
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))),
            hasRHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0))))),
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0)))),
            hasRHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Implicit checks: if (ptr), while (ptr)
        implicitCastExpr(hasImplicitDestinationType(booleanType()),
            hasSourceExpression(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Negated checks: if (!ptr)
        unaryOperator(hasOperatorName("!"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))))
    )).bind("nullCheck");

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Register matchers for allocation, pointer use, and null checks
  Finder->addMatcher(
      traverse(TK_AsIs, PointerVarFromAllocMatcher),
      this);
  
  Finder->addMatcher(
      traverse(TK_AsIs, PointerUseMatcher),
      this);
  
  Finder->addMatcher(
      traverse(TK_AsIs, NullCheckMatcher),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Track allocations, uses, and checks per variable
  static std::map<const VarDecl*, std::vector<SourceLocation>> Allocations;
  static std::map<const VarDecl*, std::vector<SourceLocation>> Uses;
  static std::map<const VarDecl*, std::vector<SourceLocation>> Checks;
  static llvm::SmallPtrSet<const VarDecl*, 16> ReportedVars;
  
  // Check if this is an allocation expression
  const Stmt *AllocExpr = Result.Nodes.getNodeAs<Stmt>("allocExpr");
  const VarDecl *PtrVar = nullptr;
  const VarDecl *PtrVarDecl = Result.Nodes.getNodeAs<VarDecl>("ptrVarDecl");
  
  if (AllocExpr && AllocExpr->getBeginLoc().isValid()) {
    // Get the pointer variable from the allocation
    if (PtrVarDecl && PtrVarDecl->getLocation().isValid()) {
      PtrVar = PtrVarDecl;
    } else {
      PtrVar = Result.Nodes.getNodeAs<VarDecl>("ptrVar");
    }
    
    if (!PtrVar || !PtrVar->getLocation().isValid()) return;
    
    // Store allocation location for this variable
    Allocations[PtrVar].push_back(AllocExpr->getBeginLoc());
  }
  
  // Check if this is a pointer usage
  const Expr *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
  const VarDecl *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  
  if (PointerUse && PointerUse->getBeginLoc().isValid() && 
      UseVar && UseVar->getLocation().isValid()) {
    // Store use location for this variable
    Uses[UseVar].push_back(PointerUse->getBeginLoc());
  }
  
  // Check if this is a null check
  const Stmt *NullCheck = Result.Nodes.getNodeAs<Stmt>("nullCheck");
  const VarDecl *CheckVar = Result.Nodes.getNodeAs<VarDecl>("checkVar");
  
  if (NullCheck && NullCheck->getBeginLoc().isValid() &&
      CheckVar && CheckVar->getLocation().isValid()) {
    // Store check location for this variable
    Checks[CheckVar].push_back(NullCheck->getBeginLoc());
  }
  
  // Process all variables that have both allocations and uses
  for (auto &VarUsePair : Uses) {
    const VarDecl *Var = VarUsePair.first;
    if (ReportedVars.count(Var)) continue; // Already reported
    
    auto AllocIt = Allocations.find(Var);
    if (AllocIt == Allocations.end()) continue; // No allocation for this variable
    
    // For each use, check if there's a null check after the most recent allocation
    for (SourceLocation UseLoc : VarUsePair.second) {
      // Find the most recent allocation before this use
      SourceLocation LastAllocLoc;
      for (SourceLocation AllocLoc : AllocIt->second) {
        if (SM.isBeforeInTranslationUnit(AllocLoc, UseLoc)) {
          if (LastAllocLoc.isInvalid() || 
              SM.isBeforeInTranslationUnit(LastAllocLoc, AllocLoc)) {
            LastAllocLoc = AllocLoc;
          }
        }
      }
      
      if (LastAllocLoc.isInvalid()) continue; // No allocation before this use
      
      // Check if there's a null check between the allocation and use
      bool FoundNullCheck = false;
      auto CheckIt = Checks.find(Var);
      if (CheckIt != Checks.end()) {
        for (SourceLocation CheckLoc : CheckIt->second) {
          if (SM.isBeforeInTranslationUnit(LastAllocLoc, CheckLoc) &&
              SM.isBeforeInTranslationUnit(CheckLoc, UseLoc)) {
            FoundNullCheck = true;
            break;
          }
        }
      }
      
      // Also check for null checks in the same statement (e.g., if (ptr && ptr->field))
      if (!FoundNullCheck) {
        // Get the parent statement of the use
        auto Parents = Context->getParents(*PointerUse);
        while (!Parents.empty()) {
          if (const Stmt *Parent = Parents[0].get<Stmt>()) {
            // Check if parent is a binary operator with logical AND/OR
            if (const auto *BinOp = dyn_cast<BinaryOperator>(Parent)) {
              if (BinOp->getOpcode() == BO_LAnd || BinOp->getOpcode() == BO_LOr) {
                // Check if the other operand contains a null check
                const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
                const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
                
                // Check if LHS contains a null check of our variable
                std::function<bool(const Expr*)> containsNullCheck = [&](const Expr *E) -> bool {
                  if (!E) return false;
                  
                  // Check for explicit comparison
                  if (const auto *InnerBinOp = dyn_cast<BinaryOperator>(E)) {
                    if (InnerBinOp->getOpcode() == BO_EQ || InnerBinOp->getOpcode() == BO_NE) {
                      const Expr *InnerLHS = InnerBinOp->getLHS()->IgnoreParenImpCasts();
                      const Expr *InnerRHS = InnerBinOp->getRHS()->IgnoreParenImpCasts();
                      
                      const DeclRefExpr *VarDRE = nullptr;
                      if (const auto *DRE = dyn_cast<DeclRefExpr>(InnerLHS)) {
                        if (DRE->getDecl() == Var) VarDRE = DRE;
                      } else if (const auto *DRE = dyn_cast<DeclRefExpr>(InnerRHS)) {
                        if (DRE->getDecl() == Var) VarDRE = DRE;
                      }
                      
                      if (VarDRE) {
                        const Expr *OtherSide = (VarDRE == dyn_cast<DeclRefExpr>(InnerLHS)) ? 
                                                 InnerRHS : InnerLHS;
                        if (OtherSide->isNullPointerConstant(*Context, 
                                                             Expr::NPC_ValueDependentIsNull)) {
                          return true;
                        }
                      }
                    }
                  }
                  
                  // Check for implicit check
                  if (const auto *DRE = dyn_cast<DeclRefExpr>(E)) {
                    if (DRE->getDecl() == Var) {
                      // Check if it's in a cast to boolean context
                      auto DREParents = Context->getParents(*DRE);
                      while (!DREParents.empty()) {
                        if (const auto *ICE = DREParents[0].get<ImplicitCastExpr>()) {
                          if (ICE->getCastKind() == CK_PointerToBoolean ||
                              ICE->getCastKind() == CK_IntegralToBoolean) {
                            return true;
                          }
                        }
                        DREParents = Context->getParents(DREParents[0]);
                      }
                    }
                  }
                  
                  // Check for negated check
                  if (const auto *UnaryOp = dyn_cast<UnaryOperator>(E)) {
                    if (UnaryOp->getOpcode() == UO_LNot) {
                      return containsNullCheck(UnaryOp->getSubExpr()->IgnoreParenImpCasts());
                    }
                  }
                  
                  // Recursively check children
                  for (const Stmt *Child : E->children()) {
                    if (const Expr *ChildExpr = dyn_cast_or_null<Expr>(Child)) {
                      if (containsNullCheck(ChildExpr)) return true;
                    }
                  }
                  
                  return false;
                };
                
                if (containsNullCheck(LHS) || containsNullCheck(RHS)) {
                  FoundNullCheck = true;
                  break;
                }
              }
            }
          }
          Parents = Context->getParents(Parents[0]);
        }
      }
      
      // If no null check found, emit diagnostic
      if (!FoundNullCheck) {
        // Get the pointer use expression for the diagnostic
        const Expr *UseExpr = nullptr;
        for (auto &VarUsePair2 : Uses) {
          if (VarUsePair2.first == Var) {
            // Find the use at this location
            for (SourceLocation Loc : VarUsePair2.second) {
              if (Loc == UseLoc) {
                // We need to find the actual expression - for simplicity, use the first one
                UseExpr = PointerUse;
                break;
              }
            }
            if (UseExpr) break;
          }
        }
        
        if (UseExpr && UseExpr->getBeginLoc().isValid()) {
          diag(UseExpr->getBeginLoc(), 
               "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
              << UseExpr->getSourceRange();
          ReportedVars.insert(Var);
          break; // Only report once per variable
        }
      }
    }
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
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

/// Checks that pointers obtained through dynamic memory allocation functions
/// (malloc, calloc, realloc) are checked for null before their first use.
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

## passed test cases code

```cpp
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
}
#include <stdlib.h>

void foo(void)
{
    int *p = NULL;
    p = (int*) calloc(1, sizeof(int));
    if (p == NULL)
        return;
    p[0] = 1;
    p = (int*) realloc(p, sizeof(int) * 2);
    p[1] = 2;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>
#include <stdbool.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (!p)
        return;
    p[0] = 1;
}

void bar(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (p) {
        p[0] = 1;
    }
}

void func(void)
{
    int *p = (int*) malloc(sizeof(int));
    bool good = p;
    if (good) p[0] = 1;
}

void explict_cast_func(void)
{
    int *p = (int*) malloc(sizeof(int));
    if ((bool)p) p[0] = 1;
}

void double_negative_func(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (!!p) p[0] = 1;
}
#include <stdlib.h>

int *p = NULL;
void foo(void)
{
    p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    *p = 1;// 违反：指针未检查即使用
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>
void foo(void)
{
    int *pa = NULL;
    pa = (int*) malloc(sizeof(int) * 2);
    int *pb = (int*) malloc(sizeof(int) * 2);
    pa[0] = 1;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pa[1] = 2;
    pb[0] = 3;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pb[1] = 4;
}
#include <stdlib.h>

void foo(void)
{
    int *p = NULL;
    p = (int*) calloc(1, sizeof(int));
    p[0] = 1;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>

void foo()
{
    int *p = (int*) malloc(sizeof(int));
    if (!p)
        return;
    p[0] = 1;
}

void bar()
{
    int *p = (int*) malloc(sizeof(int));
    if (p) p[0] = 1;
}

void func()
{
    int *p = (int*) malloc(sizeof(int));
    bool failed = !p;
    if (!failed) p[0] = 1;
}

void explict_cast_func()
{
    int *p = (int*) malloc(sizeof(int));
    if (static_cast<bool>(p)) p[0] = 1;
}
#include <stdlib.h>
void foo(void)
{
    int *p = NULL;
    p = (int*) malloc(sizeof(int));
    p = (int*) malloc(sizeof(int));
}
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    if (p == nullptr)
    {
        return;
    }
}
```

## failed test cases code
This test case should not report an issue, but the current checker code reports an issue in the code, which is a false positive.
```cpp
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (p != NULL)
    {
        *p = 1;
    }
}
```

### ast of  failed test cases 
TranslationUnitDecl 0x55d4185ad1c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55d4186d3058 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp:3:1, line:10:1> line:3:6 foo 'void ()'
  `-CompoundStmt 0x55d4186d3470 <line:4:1, line:10:1>
    |-DeclStmt 0x55d4186d3308 <line:5:5, col:40>
    | `-VarDecl 0x55d4186d3118 <col:5, col:39> col:10 used p 'int *' cinit
    |   `-CStyleCastExpr 0x55d4186d32e0 <col:14, col:39> 'int *' <BitCast>
    |     `-CallExpr 0x55d4186d32a0 <col:21, col:39> 'void *'
    |       |-ImplicitCastExpr 0x55d4186d3288 <col:21> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x55d4186d3200 <col:21> 'void *(size_t) noexcept(true)' lvalue Function 0x55d4186b4930 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x55d4186d24b8 'malloc')
    |       `-UnaryExprOrTypeTraitExpr 0x55d4186d31e0 <col:28, col:38> 'unsigned long' sizeof 'int'
    `-IfStmt 0x55d4186d3450 <line:6:5, line:9:5>
      |-BinaryOperator 0x55d4186d3388 <line:6:9, /root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> 'bool' '!='
      | |-ImplicitCastExpr 0x55d4186d3358 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp:6:9> 'int *' <LValueToRValue>
      | | `-DeclRefExpr 0x55d4186d3320 <col:9> 'int *' lvalue Var 0x55d4186d3118 'p' 'int *'
      | `-ImplicitCastExpr 0x55d4186d3370 </root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> 'int *' <NullToPointer>
      |   `-GNUNullExpr 0x55d4186d3340 <col:18> 'long'
      `-CompoundStmt 0x55d4186d3438 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_2.cpp:7:5, line:9:5>
        `-BinaryOperator 0x55d4186d3418 <line:8:9, col:14> 'int' lvalue '='
          |-UnaryOperator 0x55d4186d33e0 <col:9, col:10> 'int' lvalue prefix '*' cannot overflow
          | `-ImplicitCastExpr 0x55d4186d33c8 <col:10> 'int *' <LValueToRValue>
          |   `-DeclRefExpr 0x55d4186d33a8 <col:10> 'int *' lvalue Var 0x55d4186d3118 'p' 'int *'
          `-IntegerLiteral 0x55d4186d33f8 <col:14> 'int' 1



## reference logic step
[{'logic_registerMatchers': ['1. Define a matcher for dynamic memory allocation functions (malloc, calloc, realloc).', "2. Create a matcher to capture allocation call expressions, binding them as 'allocCall'.", "3. Create a matcher to identify the pointer variable receiving the allocation result. This matcher must handle both direct assignments (e.g., p = malloc()) and variable declarations with initializers (e.g., int *p = malloc()). Bind the variable declaration as 'ptrVar'.", "4. Create a matcher to capture uses of a pointer variable. This includes dereference (*p), array subscript (p[0]), member access (p->field), and calls through a pointer (p()). Bind the use expression as 'pointerUse' and the referenced variable as 'useVar'.", "5. Create a matcher to identify null pointer checks on a variable. This includes explicit comparisons (==, !=) with NULL/0, implicit checks in boolean contexts (if(ptr)), and negated checks (!ptr). Bind the check statement as 'nullCheck' and the checked variable as 'checkVar'.", '6. Register all three matchers (allocation variable finder, pointer use, null check) with the MatchFinder, using traverse(TK_AsIs) to ensure they match across the entire AST.'], 'logic_check': ['1. Retrieve the ASTContext and SourceManager from the MatchResult.', '2. Maintain static maps to track allocation locations, use locations, and null check locations per variable across the translation unit. Also maintain a set of already reported variables to avoid duplicate diagnostics.', "3. If the current match is for an allocation expression ('allocExpr'), extract the pointer variable ('ptrVar'). Store the allocation's source location in the Allocations map for that variable.", "4. If the current match is for a pointer use ('pointerUse'), extract the used variable ('useVar'). Store the use's source location in the Uses map for that variable.", "5. If the current match is for a null check ('nullCheck'), extract the checked variable ('checkVar'). Store the check's source location in the Checks map for that variable.", '6. After processing the current match, iterate through all variables in the Uses map that have not been reported.', '7. For each such variable, check if it exists in the Allocations map. If not, skip (the pointer was not allocated via the tracked functions).', '8. For each use location of the variable, find the most recent allocation location that precedes this use in the source code.', '9. If a preceding allocation is found, search for a null check on the same variable that occurs between that allocation and the use. Check both the stored check locations and analyze the immediate context of the use (e.g., if the use is part of a logical AND/OR expression where the other operand contains a null check).', '10. If no qualifying null check is found between the allocation and the use, emit a diagnostic at the use location. Add the variable to the reported set to prevent further reports for the same variable.', '11. The diagnostic logic must not include any fix-it generation or code modification suggestions.']}]

## reference astMatchers
Narrowing Matcher: hasLocalStorage
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches a variable declaration that has function scope and is a
non-static local variable.

Example matches x (matcher = varDecl(hasLocalStorage())
void f() {
  int x;
  static int y;
}
int z;

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

Narrowing Matcher: hasThreadStorageDuration
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches a variable declaration that has thread storage duration.

Example matches z, but not x, z, or a.
(matcher = varDecl(hasThreadStorageDuration())
void f() {
  int x;
  static int y;
  thread_local int z;
}
int a;

AST Traversal Matcher: traverse
 Parameters;TraversalKind TK, Matcher<*>  InnerMatcher
 Return type Matcher<*>
 Description: Causes all nested matchers to be matched with the specified traversal kind.

Given
  void foo()
  {
      int i = 3.0;
  }
The matcher
  traverse(TK_IgnoreUnlessSpelledInSource,
    varDecl(hasInitializer(floatLiteral().bind("init")))
  )
matches the variable declaration with "init" bound to the "3.0".

AST Traversal Matcher: throughUsingDecl
 Parameters;Matcher<UsingShadowDecl> Inner
 Return type Matcher<DeclRefExpr>
 Description: Matches if a node refers to a declaration through a specific
using shadow declaration.

Examples:
  namespace a { int f(); }
  using a::f;
  int x = f();
declRefExpr(throughUsingDecl(anything()))
  matches f

  namespace a { class X{}; }
  using a::X;
  X x;
typeLoc(loc(usingType(throughUsingDecl(anything()))))
  matches X

Usable as: Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1DeclRefExpr.html">DeclRefExpr</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1UsingType.html">UsingType</a>&gt;

anyOf(declRefExpr(to(decl().bind("deletedPointer"))), memberExpr(hasDeclaration(fieldDecl().bind("deletedMemberPointer"))))
binaryOperator(hasOperands(anyOf(cxxNullPtrLiteralExpr(), integerLiteral(equals(0))), PointerExpr))
const auto AllocFunc = functionDecl(hasAnyName("::malloc", "std::malloc", "::alloca", "::calloc", "std::calloc", "::realloc", "std::realloc"));
const auto AllocCall = callExpr(callee(decl(anyOf(AllocFunc, AllocFuncPtr))));
Finder->addMatcher(binaryOperator(AdditiveOperator, hasLHS(anyOf(AllocCall, castExpr(hasSourceExpression(AllocCall)))), hasRHS(IntExpr)).bind("PtrArith"), this);
void LoopConvertCheck::registerMatchers(MatchFinder *Finder) {
  Finder->addMatcher(traverse(TK_AsIs, makeArrayLoopMatcher()), this);
  Finder->addMatcher(traverse(TK_AsIs, makeIteratorLoopMatcher(false)), this);
  Finder->addMatcher(traverse(TK_AsIs, makePseudoArrayLoopMatcher()), this);
  if (UseReverseRanges)
    Finder->addMatcher(traverse(TK_AsIs, makeIteratorLoopMatcher(true)), this);
}


## reference code snippets  
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
const Expr *AllocExpr = PtrArith->getLHS()->IgnoreParenCasts();
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
static const DeclRefExpr *findUsage(const Stmt *Node, int64_t DeclIdentifier) {
  if (!Node)
    return nullptr;
  if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Node)) {
    if (DeclRef->getDecl()->getID() == DeclIdentifier)
      return DeclRef;
  } else {
    for (const Stmt *ChildNode : Node->children()) {
      if (const DeclRefExpr *Result = findUsage(ChildNode, DeclIdentifier))
        return Result;
    }
  }
  return nullptr;
}
std::string FixItInitList;
bool HasRelevantBaseInit = false;
bool ShouldNotDoFixit = false;
bool HasWrittenInitializer = false;
SmallVector<FixItHint, 2> SafeFixIts;
const auto *Method = llvm::dyn_cast<CXXMethodDecl>(Function);
if (Param->getBeginLoc().isMacroID() || (Method && Method->isVirtual()) ||
    isReferencedOutsideOfCallExpr(*Function, *Result.Context) ||
    (Function->getTemplatedKind() != FunctionDecl::TK_NonTemplate))
  return;
const ASTContext &Ctx = *Result.Context;
const auto *CE = Result.Nodes.getNodeAs<CallExpr>("call");
else if (const auto *ASM = Result.Nodes.getNodeAs<VarDecl>("asm-var"))
  ASMLocation = ASM->getLocation();
for (unsigned I = 0, E = Function->getNumParams(); I != E; ++I) {
  const auto *Param = Function->getParamDecl(I);
  if (Param->isUsed() || Param->isReferenced() || !Param->getDeclName() ||
      Param->hasAttr<UnusedAttr>())
    continue;

  // ... (further parameter checks follow)
}
bool clang::CXXNewExpr::shouldNullCheckAllocation() const
bool clang::Capture::capturesVariable() const
SourceLocation clang::SourceLocation::getLocWithOffset(IntTy Offset) const
Expr * clang::OMPAllocatorClause::getAllocator() const
bool clang::WhileStmt::hasVarStorage() const
const SourceManager & clang::ASTContext::getSourceManager() const
unsigned int clang::DiagnosticMapping::serialize() const
SourceLocation clang::SourceLocation::getFromPtrEncoding(const void * Encoding)
SourceLocation clang::OMPUseClause::getVarLoc() const
void clang::DiagnosticMapping::setNoErrorAsFatal(bool Value)



# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the current checker code above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
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


You can proceed with the analysis according to the following steps:

1.  Read the provided current checker code and analyze its implementation logic.
2.  Analyze the passed test cases code to understand how the checker successfully identifies issues in the code without generating false positives.
3.  Analyze why the current checker code is incorrectly reporting failed test cases, as the code in the failed test cases is correct and should not be reported.
4.  Synthesize the findings from the above analyses. When generating the new code, follow the reference logic steps, consult the reference AST matchers, and utilize the reference code snippets to produce a complete and robust checker implementation. This new checker code should be capable of detecting all issues in the test cases while avoiding false positives.
5.  Output the final code strictly adhering to the specified output format requirements.

