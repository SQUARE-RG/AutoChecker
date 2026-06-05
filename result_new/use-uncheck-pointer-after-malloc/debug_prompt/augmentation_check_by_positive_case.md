针对正例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_17.cpp增强checker
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
  
  auto AllocAssignMatcher = binaryOperator(
      isAssignmentOperator(),
      hasRHS(ignoringParenCasts(AllocExprMatcher)),
      hasLHS(declRefExpr(to(varDecl().bind("allocVar"))))
  );
  
  Finder->addMatcher(
    AllocAssignMatcher,
    this
  );
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Var = Result.Nodes.getNodeAs<VarDecl>("allocated_ptr");
  if (!Var) {
    Var = Result.Nodes.getNodeAs<VarDecl>("allocVar");
  }
  if (!Var)
    return;
  
  ASTContext *Context = Result.Context;
  SourceManager &SM = Context->getSourceManager();
  
  if (!Var->isReferenced())
    return;
  
  const auto *ParentDC = Var->getDeclContext();
  if (!ParentDC)
    return;
  
  const auto *NonClosureAncestor = ParentDC->getNonClosureAncestor();
  if (!NonClosureAncestor)
    return;
  
  const FunctionDecl *FuncDecl = nullptr;
  const Stmt *SearchBody = nullptr;
  
  if (const auto *FD = dyn_cast<FunctionDecl>(NonClosureAncestor)) {
    if (FD->hasBody()) {
      FuncDecl = FD;
      SearchBody = FD->getBody();
    }
  } else if (const auto *TU = dyn_cast<TranslationUnitDecl>(NonClosureAncestor)) {
    SearchBody = TU->getBody();
  }
  
  if (!SearchBody)
    return;
  
  struct UseInfo {
    const Stmt *StmtNode;
    SourceLocation Loc;
    bool IsCheck;
    bool IsAllocAssign;
    bool IsFree;
  };
  std::vector<UseInfo> Uses;
  
  // Helper to check if a DeclRefExpr refers to the tracked variable
  auto RefersToVar = [&](const DeclRefExpr *DRE) -> bool {
    if (!DRE) return false;
    const ValueDecl *VD = DRE->getDecl();
    if (!VD) return false;
    if (VD == Var) return true;
    return false;
  };
  
  std::function<void(const Stmt*)> CollectUses = [&](const Stmt *S) {
    if (!S) return;
    
    // Handle MemberExpr: check if it accesses a member of a struct that was assigned the allocation
    if (const auto *ME = dyn_cast<MemberExpr>(S)) {
      if (ME->isArrow()) {
        // p->member: the base is a pointer
        const Expr *Base = ME->getBase()->IgnoreParenImpCasts();
        if (const auto *BaseDRE = dyn_cast<DeclRefExpr>(Base)) {
          if (BaseDRE->getDecl() == Var) {
            // This is a use of the pointer via member access
            bool IsCheck = false;
            bool IsAllocAssign = false;
            bool IsFree = false;
            
            const auto Parents = Context->getParents(*S);
            if (!Parents.empty()) {
              if (const auto *BO = dyn_cast_or_null<BinaryOperator>(Parents.begin()->get<Stmt>())) {
                if (BO->isAssignmentOp()) {
                  if (const auto *Call = dyn_cast<CallExpr>(BO->getRHS()->IgnoreParenCasts())) {
                    if (const auto *FD = dyn_cast<FunctionDecl>(Call->getCalleeDecl())) {
                      if (FD->getName() == "malloc" || FD->getName() == "calloc" ||
                          FD->getName() == "realloc" || FD->getName() == "aligned_alloc") {
                        IsAllocAssign = true;
                        Uses.push_back(UseInfo{BO, BO->getExprLoc(), false, true, false});
                        return;
                      }
                    }
                  }
                }
              }
            }
            if (!IsCheck && !IsAllocAssign && !IsFree) {
              Uses.push_back(UseInfo{S, ME->getExprLoc(), false, false, false});
            }
          }
        }
      } else {
        // s.member: check if the base is a struct variable that was assigned the allocation
        const Expr *Base = ME->getBase()->IgnoreParenImpCasts();
        if (const auto *BaseDRE = dyn_cast<DeclRefExpr>(Base)) {
          if (const auto *BaseVar = dyn_cast<VarDecl>(BaseDRE->getDecl())) {
            // Check if this struct variable's member was assigned via allocation
            // We need to track this in a more sophisticated way
            // For now, we skip this case as it's complex
          }
        }
      }
    }
    
    if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
      if (DRE->getDecl() == Var) {
        bool IsCheck = false;
        bool IsAllocAssign = false;
        bool IsFree = false;
        
        const auto Parents = Context->getParents(*S);
        if (!Parents.empty()) {
          // Check if this is a free() call use
          if (const auto *CE = dyn_cast_or_null<CallExpr>(Parents.begin()->get<Stmt>())) {
            if (const auto *FD = dyn_cast<FunctionDecl>(CE->getCalleeDecl())) {
              if (FD->getName() == "free") {
                IsFree = true;
                Uses.push_back(UseInfo{CE, CE->getExprLoc(), false, false, true});
                return;
              }
            }
          }
          
          if (const auto *BO = dyn_cast_or_null<BinaryOperator>(Parents.begin()->get<Stmt>())) {
            if (BO->isAssignmentOp()) {
              if (const auto *Call = dyn_cast<CallExpr>(BO->getRHS()->IgnoreParenCasts())) {
                if (const auto *FD = dyn_cast<FunctionDecl>(Call->getCalleeDecl())) {
                  if (FD->getName() == "malloc" || FD->getName() == "calloc" ||
                      FD->getName() == "realloc" || FD->getName() == "aligned_alloc") {
                    IsAllocAssign = true;
                    Uses.push_back(UseInfo{BO, BO->getExprLoc(), false, true, false});
                    return;
                  }
                }
              }
            }
            if (BO->isComparisonOp() && 
                (BO->getOpcode() == BO_EQ || BO->getOpcode() == BO_NE)) {
              const Expr *Other = (BO->getLHS() == S) ? BO->getRHS() : BO->getLHS();
              if (Other && Other->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull) != Expr::NPCK_NotNull) {
                IsCheck = true;
                Uses.push_back(UseInfo{BO, BO->getExprLoc(), true, false, false});
                return;
              }
            }
          }
          if (const auto *UO = dyn_cast_or_null<UnaryOperator>(Parents.begin()->get<Stmt>())) {
            if (UO->getOpcode() == UO_LNot) {
              IsCheck = true;
              Uses.push_back(UseInfo{UO, UO->getExprLoc(), true, false, false});
              return;
            }
          }
          if (const auto *IfS = dyn_cast_or_null<IfStmt>(Parents.begin()->get<Stmt>())) {
            if (IfS->getCond() == S) {
              IsCheck = true;
              Uses.push_back(UseInfo{IfS, IfS->getBeginLoc(), true, false, false});
              return;
            }
          }
          if (const auto *CSCE = dyn_cast_or_null<CXXStaticCastExpr>(Parents.begin()->get<Stmt>())) {
            if (CSCE->getType()->isBooleanType()) {
              IsCheck = true;
              Uses.push_back(UseInfo{CSCE, CSCE->getExprLoc(), true, false, false});
              return;
            }
          }
          // Check for implicit cast to bool (e.g., in if condition, bool variable assignment)
          if (const auto *ICE = dyn_cast_or_null<ImplicitCastExpr>(Parents.begin()->get<Stmt>())) {
            if (ICE->getCastKind() == CK_PointerToBoolean) {
              // Check if parent of ICE is a UnaryOperator with '!' (double negative)
              const auto GrandParents = Context->getParents(*ICE);
              if (!GrandParents.empty()) {
                if (const auto *GrandUO = dyn_cast_or_null<UnaryOperator>(GrandParents.begin()->get<Stmt>())) {
                  if (GrandUO->getOpcode() == UO_LNot) {
                    // This is a double negative: !!p, treat as check
                    IsCheck = true;
                    Uses.push_back(UseInfo{GrandUO, GrandUO->getExprLoc(), true, false, false});
                    return;
                  }
                }
              }
              // Otherwise, implicit cast to bool is a check
              IsCheck = true;
              Uses.push_back(UseInfo{ICE, ICE->getExprLoc(), true, false, false});
              return;
            }
          }
        }
        if (!IsCheck && !IsAllocAssign && !IsFree) {
          Uses.push_back(UseInfo{S, DRE->getLocation(), false, false, false});
        }
      }
    }
    
    for (const auto *Child : S->children()) {
      CollectUses(Child);
    }
  };
  
  CollectUses(SearchBody);
  
  // Filter out free() calls and alloc-assign uses for violation detection
  std::vector<UseInfo> FilteredUses;
  for (const auto &Use : Uses) {
    if (!Use.IsFree && !Use.IsAllocAssign) {
      FilteredUses.push_back(Use);
    }
  }
  
  if (FilteredUses.empty())
    return;
  
  // Find the first actual use and see if there is a check before it
  bool HasCheck = false;
  bool HasUse = false;
  const Stmt *FirstUse = nullptr;
  
  // Sort by source location to ensure correct order
  std::sort(FilteredUses.begin(), FilteredUses.end(),
            [&SM](const UseInfo &A, const UseInfo &B) {
              return SM.isBeforeInTranslationUnit(A.Loc, B.Loc);
            });
  
  for (const auto &Use : FilteredUses) {
    if (Use.IsCheck) {
      HasCheck = true;
      if (!HasUse) {
        break; // Check before any use is good
      }
    } else {
      if (!HasUse) {
        FirstUse = Use.StmtNode;
        HasUse = true;
      }
    }
  }
  
  if (!HasUse)
    return;
  
  // Determine if the first non-alloc-assign use is a check
  bool FirstIsCheck = false;
  if (!FilteredUses.empty()) {
    FirstIsCheck = FilteredUses.front().IsCheck;
  }
  
  if (!FirstIsCheck && FirstUse) {
    diag(FirstUse->getBeginLoc(), "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]");
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

## passed test cases code

```cpp
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
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
}
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
#include <stdlib.h>

void foo(void)
{
    int *p = NULL;
    p = (int*) calloc(1, sizeof(int));
    p[0] = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
// File: negative_basic_malloc.c
#include <stdlib.h>
void test_basic(void) {
    int *p = (int*)malloc(sizeof(int));
    *p = 10; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
// File: negative_one_of_two.c
#include <stdlib.h>
void test_two_pointers(void) {
    int *p1 = (int*)malloc(sizeof(int));
    int *p2 = (int*)malloc(sizeof(int));
    if (p1 != NULL) { *p1 = 1; } // p1 被正确检查
    *p2 = 2; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
#include <stdlib.h>
void foo(void)
{
    int *pa = NULL;
    pa = (int*) malloc(sizeof(int) * 2);
    int *pb = (int*) malloc(sizeof(int) * 2);
    pa[0] = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pa[1] = 2;
    pb[0] = 3;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pb[1] = 4;
}
#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}

// File: positive_unused.c
#include <stdlib.h>
void test_unused(void) {
    int *p = (int*)malloc(sizeof(int));
    // 指针 p 未被使用
}
#include <stdlib.h>
void foo(void)
{
    int *p = NULL;
    p = (int*) malloc(sizeof(int));
    p = (int*) malloc(sizeof(int));
}
```

## failed test cases code
This test case should not report an issue, but the current checker code reports an issue in the code, which is a false positive.
```cpp
// File: positive_c_shorthand.c
#include <stdlib.h>
void test_c_shorthand(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p) {
        *p = 1;
    }
}
```

### ast of  failed test cases
TranslationUnitDecl 0x55eb7a2591d8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55eb7a37f288 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_17.cpp:3:1, line:8:1> line:3:6 test_c_shorthand 'void ()'
  `-CompoundStmt 0x55eb7a37f668 <col:29, line:8:1>
    |-DeclStmt 0x55eb7a37f538 <line:4:5, col:39>
    | `-VarDecl 0x55eb7a37f348 <col:5, col:38> col:10 used p 'int *' cinit
    |   `-CStyleCastExpr 0x55eb7a37f510 <col:14, col:38> 'int *' <BitCast>
    |     `-CallExpr 0x55eb7a37f4d0 <col:20, col:38> 'void *'
    |       |-ImplicitCastExpr 0x55eb7a37f4b8 <col:20> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x55eb7a37f430 <col:20> 'void *(size_t) noexcept(true)' lvalue Function 0x55eb7a360870 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x55eb7a37e6e8 'malloc')
    |       `-UnaryExprOrTypeTraitExpr 0x55eb7a37f410 <col:27, col:37> 'unsigned long' sizeof 'int'
    `-IfStmt 0x55eb7a37f648 <line:5:5, line:7:5>
      |-ImplicitCastExpr 0x55eb7a37f588 <line:5:9> 'bool' <PointerToBoolean>
      | `-ImplicitCastExpr 0x55eb7a37f570 <col:9> 'int *' <LValueToRValue>
      |   `-DeclRefExpr 0x55eb7a37f550 <col:9> 'int *' lvalue Var 0x55eb7a37f348 'p' 'int *'
      `-CompoundStmt 0x55eb7a37f630 <col:12, line:7:5>
        `-BinaryOperator 0x55eb7a37f610 <line:6:9, col:14> 'int' lvalue '='
          |-UnaryOperator 0x55eb7a37f5d8 <col:9, col:10> 'int' lvalue prefix '*' cannot overflow
          | `-ImplicitCastExpr 0x55eb7a37f5c0 <col:10> 'int *' <LValueToRValue>
          |   `-DeclRefExpr 0x55eb7a37f5a0 <col:10> 'int *' lvalue Var 0x55eb7a37f348 'p' 'int *'
          `-IntegerLiteral 0x55eb7a37f5f0 <col:14> 'int' 1



## reference logic step
**logic for registerMatchers**:
1. Match variable declarations that have an initializer which is a call to one of the allocation functions (malloc, calloc, realloc, aligned_alloc), ignoring parentheses and implicit casts
2. Exclude variable declarations that are within implicit function declarations to avoid matching compiler-generated code
3. Additionally, match binary assignment operators where the right-hand side is a call to one of the allocation functions and the left-hand side is a reference to a variable, binding that variable
4. Bind the matched variable declaration as 'allocated_ptr' for the first matcher; for the second matcher, bind the variable referenced on the left-hand side as 'allocVar'
**logic for check**:
1. Retrieve the variable declaration from either the 'allocated_ptr' or 'allocVar' binding
2. Check if the variable is referenced; if not, return early
3. Determine the enclosing function or translation unit that contains the variable declaration, and obtain the body statement to search for uses
4. Traverse the body statement recursively to collect all uses of the variable, classifying each use as: a check (comparison with NULL/nullptr, logical NOT, implicit cast to bool, use in if condition, static cast to bool, or double negation), an allocation assignment (reassigning the variable with a new allocation), a free() call, or an unchecked use (any other dereference or access)
5. For each use, correctly identify the parent context to distinguish between a use that is a check, an allocation reassignment, or a free() call, avoiding misclassification
6. Filter out free() calls and allocation reassignment uses from the collected uses, keeping only checks and unchecked uses
7. Sort the filtered uses by source location in translation unit order to process them in execution order
8. Determine if there is any check occurrence before the first unchecked use; if a check appears before any unchecked use, the code is safe and no diagnostic is emitted
9. If the first use found is an unchecked use (not a check) and no prior check exists, emit a diagnostic at the location of the first unchecked use to indicate that the dynamically allocated pointer is used without a null check
10. Ensure that implicit casts to boolean (PointerToBoolean) are correctly recognized as checks, but only when they are not part of a double negation pattern (!!p), which also counts as a check


## reference astMatchers
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

declStmt(containsDeclaration(0, varDecl(hasInitializer(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasName("cast")))).bind("assign")))))
const auto Alloc0FuncPtr = varDecl(hasType(isConstQualified()), hasInitializer(ignoringParenImpCasts(declRefExpr(hasDeclaration(Alloc0Func)))));
const auto Alloc1FuncPtr = varDecl(hasType(isConstQualified()), hasInitializer(ignoringParenImpCasts(declRefExpr(hasDeclaration(Alloc1Func)))));
const auto AllocFuncPtr = varDecl(hasType(isConstQualified()), hasInitializer(ignoringParenImpCasts(declRefExpr(hasDeclaration(AllocFunc)))));


## reference code snippets
if (const auto *DeclRef = dyn_cast<DeclRefExpr>(PtrInputExpr->IgnoreParenImpCasts()))
  if (const auto *Var = dyn_cast<VarDecl>(DeclRef->getDecl()))
    if (const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>("parent_function"))
      if (FindAssignToVarBefore{Var, DeclRef, SM}.Visit(Func->getBody()))
        return;
const auto *OwnerAssignment = Nodes.getNodeAs<BinaryOperator>("owner_assignment");
const auto *OwnerInitialization = Nodes.getNodeAs<VarDecl>("owner_initialization");
const auto *OwnerInitializer = Nodes.getNodeAs<CXXCtorInitializer>("owner_member_initializer");
if (OwnerAssignment) {
  diag(OwnerAssignment->getBeginLoc(),
       "expected assignment source to be of type 'gsl::owner<>'; got %0")
      << OwnerAssignment->getRHS()->getType()
      << OwnerAssignment->getSourceRange();
  return true;
}
if (OwnerInitialization) {
  diag(OwnerInitialization->getBeginLoc(),
       "expected initialization with value of type 'gsl::owner<>'; got %0")
      << OwnerInitialization->getAnyInitializer()->getType()
      << OwnerInitialization->getSourceRange();
  return true;
}
if (OwnerInitializer) {
  diag(OwnerInitializer->getSourceLocation(),
       "expected initialization of owner member variable with value of type "
       "'gsl::owner<>'; got %0")
      << OwnerInitializer->getInit()->getType()
      << OwnerInitializer->getSourceRange();
  return true;
}
return false;
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
bool clang::DeclRefExpr::refersToEnclosingVariableOrCapture() const
bool clang::ImplicitCastExpr::isPartOfExplicitCast() const
NamespaceDecl * clang::TranslationUnitDecl::getAnonymousNamespace() const

