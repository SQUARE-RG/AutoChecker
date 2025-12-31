针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_9.cpp增强checker
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
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Decl.h"
#include "clang/AST/Expr.h"
#include "clang/AST/OperationKinds.h"
#include "clang/AST/Type.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Basic/SourceManager.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/ADT/DenseSet.h"
#include <algorithm>
#include <vector>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {
// Helper to check if an expression is a null pointer constant
bool isNullPointerConstant(const Expr *E, ASTContext &Context) {
  return E->isNullPointerConstant(Context, Expr::NPC_ValueDependentIsNotNull);
}

// Helper to check if a binary operator is a null check
bool isNullCheckBinary(const BinaryOperator *BO, const ValueDecl *Decl,
                       ASTContext &Context) {
  if (BO->getOpcode() != BO_EQ && BO->getOpcode() != BO_NE)
    return false;

  const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
  const Expr *RHS = BO->getRHS()->IgnoreParenImpCasts();

  // Check if one side is a reference to our variable
  const DeclRefExpr *VarRef = nullptr;
  const Expr *Other = nullptr;

  if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
    if (DRE->getDecl() == Decl) {
      VarRef = DRE;
      Other = RHS;
    }
  }
  if (!VarRef && (VarRef = dyn_cast<DeclRefExpr>(RHS))) {
    if (VarRef->getDecl() == Decl) {
      Other = LHS;
    } else {
      VarRef = nullptr;
    }
  }

  if (!VarRef)
    return false;

  // Check if the other side is a null pointer constant
  return isNullPointerConstant(Other, Context);
}

// Helper to check if a unary operator is a null check (like !ptr)
bool isNullCheckUnary(const UnaryOperator *UO, const ValueDecl *Decl) {
  if (UO->getOpcode() != UO_LNot)
    return false;

  const Expr *SubExpr = UO->getSubExpr()->IgnoreParenImpCasts();
  if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
    return DRE->getDecl() == Decl;
  }
  return false;
}

// Helper to check if an implicit cast to bool is a null check (like if(ptr))
bool isImplicitBoolCast(const ImplicitCastExpr *ICE, const ValueDecl *Decl) {
  if (ICE->getCastKind() != CK_PointerToBoolean)
    return false;

  const Expr *SubExpr = ICE->getSubExpr()->IgnoreParenImpCasts();
  if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
    return DRE->getDecl() == Decl;
  }
  return false;
}

// Check if a statement is a null check for the given variable
bool isNullCheck(const Stmt *S, const ValueDecl *Decl, ASTContext &Context) {
  if (!S)
    return false;

  // Handle binary operator (ptr == NULL, ptr != NULL)
  if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
    return isNullCheckBinary(BO, Decl, Context);
  }

  // Handle unary operator (!ptr)
  if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
    return isNullCheckUnary(UO, Decl);
  }

  // Handle implicit cast to bool (if(ptr))
  if (const auto *ICE = dyn_cast<ImplicitCastExpr>(S)) {
    return isImplicitBoolCast(ICE, Decl);
  }

  // For conditional operators, check the condition
  if (const auto *Cond = dyn_cast<ConditionalOperator>(S)) {
    return isNullCheck(Cond->getCond(), Decl, Context);
  }

  // For IfStmt, WhileStmt, DoStmt, ForStmt - check their condition
  if (const auto *If = dyn_cast<IfStmt>(S)) {
    return isNullCheck(If->getCond(), Decl, Context);
  }
  if (const auto *While = dyn_cast<WhileStmt>(S)) {
    return isNullCheck(While->getCond(), Decl, Context);
  }
  if (const auto *Do = dyn_cast<DoStmt>(S)) {
    return isNullCheck(Do->getCond(), Decl, Context);
  }
  if (const auto *For = dyn_cast<ForStmt>(S)) {
    return isNullCheck(For->getCond(), Decl, Context);
  }

  return false;
}

// Check if a statement is a use of the variable (dereference or subscript)
bool isPointerUse(const Stmt *S, const ValueDecl *Decl) {
  if (!S)
    return false;

  // Dereference operator (*ptr)
  if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
    if (UO->getOpcode() == UO_Deref) {
      const Expr *SubExpr = UO->getSubExpr()->IgnoreParenImpCasts();
      if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
        return DRE->getDecl() == Decl;
      }
    }
    return false;
  }

  // Array subscript (ptr[...])
  if (const auto *ASE = dyn_cast<ArraySubscriptExpr>(S)) {
    const Expr *Base = ASE->getBase()->IgnoreParenImpCasts();
    if (const auto *DRE = dyn_cast<DeclRefExpr>(Base)) {
      return DRE->getDecl() == Decl;
    }
    return false;
  }

  // Member access through pointer (ptr->field)
  if (const auto *ME = dyn_cast<MemberExpr>(S)) {
    if (ME->isArrow()) {
      const Expr *Base = ME->getBase()->IgnoreParenImpCasts();
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Base)) {
        return DRE->getDecl() == Decl;
      }
    }
    return false;
  }

  return false;
}

// Get all statements related to a variable in a function body
void collectVarStatements(const ValueDecl *Decl, const Stmt *FunctionBody,
                          ASTContext &Context,
                          llvm::SmallVectorImpl<const Stmt *> &AllocStmts,
                          llvm::SmallVectorImpl<const Stmt *> &UseStmts,
                          llvm::SmallVectorImpl<const Stmt *> &CheckStmts) {
  struct Collector : public RecursiveASTVisitor<Collector> {
    const ValueDecl *Decl;
    ASTContext &Context;
    llvm::SmallVectorImpl<const Stmt *> &AllocStmts;
    llvm::SmallVectorImpl<const Stmt *> &UseStmts;
    llvm::SmallVectorImpl<const Stmt *> &CheckStmts;

    Collector(const ValueDecl *Decl, ASTContext &Context,
              llvm::SmallVectorImpl<const Stmt *> &AllocStmts,
              llvm::SmallVectorImpl<const Stmt *> &UseStmts,
              llvm::SmallVectorImpl<const Stmt *> &CheckStmts)
        : Decl(Decl), Context(Context), AllocStmts(AllocStmts),
          UseStmts(UseStmts), CheckStmts(CheckStmts) {}

    bool VisitCallExpr(CallExpr *CE) {
      // Check if this is an allocation call that initializes our variable
      // This is simplified - a full implementation would track assignments
      return true;
    }

    bool VisitStmt(Stmt *S) {
      if (isPointerUse(S, Decl)) {
        UseStmts.push_back(S);
      } else if (isNullCheck(S, Decl, Context)) {
        CheckStmts.push_back(S);
      }
      return true;
    }
  };

  Collector collector(Decl, Context, AllocStmts, UseStmts, CheckStmts);
  collector.TraverseStmt(const_cast<Stmt *>(FunctionBody));
}

// Helper to find the function body containing a statement
const FunctionDecl *findContainingFunction(const Stmt *S, ASTContext &Context) {
  const Stmt *Current = S;
  while (Current) {
    auto Parents = Context.getParents(*Current);
    if (Parents.empty())
      break;
    
    if (const auto *FuncDecl = Parents[0].get<FunctionDecl>()) {
      return FuncDecl;
    }
    
    Current = Parents[0].get<Stmt>();
    if (!Current) {
      if (const auto *ParentDecl = Parents[0].get<Decl>()) {
        if (const auto *FuncDecl = dyn_cast<FunctionDecl>(ParentDecl)) {
          return FuncDecl;
        }
      }
    }
  }
  return nullptr;
}

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Matcher for dynamic memory allocation functions
  const auto AllocFunc = functionDecl(
      hasAnyName("::malloc", "malloc", "::calloc", "calloc", "::realloc", "realloc"),
      unless(hasAttr(attr::NoThrow)) // Standard allocation functions don't throw
  );

  // Matcher for calls to allocation functions
  const auto AllocCall = callExpr(callee(AllocFunc)).bind("allocCall");

  // Matcher for variable declarations initialized with allocation result
  const auto AllocVarDecl = varDecl(
      hasType(pointerType()),
      hasInitializer(anyOf(
          castExpr(has(AllocCall)),
          AllocCall
      ))
  ).bind("allocVar");

  // Matcher for assignments to pointer variables from allocation calls
  const auto AllocAssign = binaryOperator(
      hasOperatorName("="),
      hasLHS(declRefExpr(to(varDecl(hasType(pointerType())).bind("assignVar")))),
      hasRHS(anyOf(
          castExpr(has(AllocCall)),
          AllocCall
      ))
  ).bind("allocAssign");

  // Matcher for pointer uses (dereference, array subscript, or member access)
  const auto PointerUse = stmt(anyOf(
      unaryOperator(hasOperatorName("*"),
          has(ignoringParenImpCasts(declRefExpr(to(varDecl(hasType(pointerType())).bind("useVar")))))
      ).bind("derefUse"),
      arraySubscriptExpr(
          hasBase(ignoringParenImpCasts(declRefExpr(to(varDecl(hasType(pointerType())).bind("useVar")))))
      ).bind("subscriptUse"),
      memberExpr(isArrow(),
          has(ignoringParenImpCasts(declRefExpr(to(varDecl(hasType(pointerType())).bind("useVar")))))
      ).bind("memberUse")
  )).bind("firstBadUse");

  // Combine: find allocation (declaration or assignment) and a use
  Finder->addMatcher(
      traverse(TK_AsIs,
          stmt(anyOf(
              hasDescendant(AllocVarDecl),
              hasDescendant(AllocAssign)
          ), hasDescendant(PointerUse))
      ),
      this
  );
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AllocVar = Result.Nodes.getNodeAs<VarDecl>("allocVar");
  const auto *AssignVar = Result.Nodes.getNodeAs<VarDecl>("assignVar");
  const auto *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  const auto *FirstBadUse = Result.Nodes.getNodeAs<Stmt>("firstBadUse");
  const auto *AllocCall = Result.Nodes.getNodeAs<CallExpr>("allocCall");
  const auto *AllocAssign = Result.Nodes.getNodeAs<BinaryOperator>("allocAssign");

  if (!FirstBadUse || !AllocCall)
    return;

  // Determine which variable we're checking
  const ValueDecl *TargetDecl = nullptr;
  if (UseVar) {
    TargetDecl = UseVar;
  } else if (AllocVar) {
    TargetDecl = AllocVar;
  } else if (AssignVar) {
    TargetDecl = AssignVar;
  }

  if (!TargetDecl)
    return;

  // Get the function body containing the variable
  const FunctionDecl *Func = nullptr;
  const Stmt *Body = nullptr;
  
  // First try to get the function from the target declaration's context
  const DeclContext *DC = TargetDecl->getDeclContext();
  Func = dyn_cast<FunctionDecl>(DC);
  
  if (Func && Func->hasBody()) {
    Body = Func->getBody();
  } else {
    // For global variables or if we couldn't find the function from the declaration,
    // find the function containing the allocation call
    Func = findContainingFunction(AllocCall, *Result.Context);
    if (Func && Func->hasBody()) {
      Body = Func->getBody();
    }
  }

  if (!Body)
    return;

  SourceManager &SM = *Result.SourceManager;
  ASTContext &Context = *Result.Context;

  // Collect all statements related to this variable
  llvm::SmallVector<const Stmt *, 8> AllocStmts;
  llvm::SmallVector<const Stmt *, 16> UseStmts;
  llvm::SmallVector<const Stmt *, 8> CheckStmts;

  collectVarStatements(TargetDecl, Body, Context, AllocStmts, UseStmts, CheckStmts);

  // If no uses, no violation
  if (UseStmts.empty())
    return;

  // Sort all statements by source location
  auto compareSourceLoc = [&SM](const Stmt *A, const Stmt *B) {
    return SM.isBeforeInTranslationUnit(A->getBeginLoc(), B->getBeginLoc());
  };

  std::sort(UseStmts.begin(), UseStmts.end(), compareSourceLoc);
  std::sort(CheckStmts.begin(), CheckStmts.end(), compareSourceLoc);

  // Find the allocation statement
  const Stmt *AllocStmt = nullptr;
  if (AllocAssign) {
    AllocStmt = AllocAssign;
  } else if (AllocCall) {
    AllocStmt = AllocCall;
  }

  if (!AllocStmt)
    return;

  // Check each use to see if there's a null check before it
  for (const Stmt *Use : UseStmts) {
    // Skip if use is before allocation (shouldn't happen for this variable)
    if (SM.isBeforeInTranslationUnit(Use->getBeginLoc(), AllocStmt->getBeginLoc()))
      continue;

    bool hasCheckBeforeUse = false;
    
    // Check if any null check occurs before this use
    for (const Stmt *Check : CheckStmts) {
      if (SM.isBeforeInTranslationUnit(Check->getBeginLoc(), Use->getBeginLoc())) {
        hasCheckBeforeUse = true;
        break;
      }
    }

    if (!hasCheckBeforeUse) {
      // Found a violation - emit diagnostic at the first violating use
      diag(Use->getBeginLoc(),
           "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
          << TargetDecl;
      return; // Only report one warning per variable
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
    int *p = (int*) malloc(sizeof(int));
    if (p != NULL)
    {
        *p = 1;
    }
}
// File: positive_realloc_checked.c
#include <stdlib.h>
void test_safe_realloc(void) {
    int *p = (int*)malloc(sizeof(int));
    if (!p) return;
    int *new_p = (int*)realloc(p, sizeof(int) * 2);
    if (new_p != NULL) {
        new_p[1] = 2;
        p = new_p;
    } else {
        free(p);
    }
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
}

// File: negative_basic_malloc.c
#include <stdlib.h>
void test_basic(void) {
    int *p = (int*)malloc(sizeof(int));
    *p = 10; 
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
// File: positive_c_shorthand.c
#include <stdlib.h>
void test_c_shorthand(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p) {
        *p = 1;
    }
}
#include <stdlib.h>

int *p = NULL;
void foo(void)
{
    p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
// File: positive_used_in_condition.c
#include <stdlib.h>
#include <stdbool.h>
void test_in_condition(void) {
    int *p = (int*)malloc(sizeof(int));
    bool isValid = (p != NULL);
    if (isValid) {
        *p = 1;
    }
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
void foo(void)
{
    int *p = NULL;
    p = (int*) malloc(sizeof(int));
    p = (int*) malloc(sizeof(int));
}
// File: positive_unused.c
#include <stdlib.h>
void test_unused(void) {
    int *p = (int*)malloc(sizeof(int));
    // 指针 p 未被使用
}
// File: positive_free_no_use.c
#include <stdlib.h>
void test_free(void) {
    int *p = (int*)malloc(sizeof(int));
    free(p); // 释放前未使用
}
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
// File: negative_one_of_two.c
#include <stdlib.h>
void test_two_pointers(void) {
    int *p1 = (int*)malloc(sizeof(int));
    int *p2 = (int*)malloc(sizeof(int));
    if (p1 != NULL) { *p1 = 1; } // p1 被正确检查
    *p2 = 2; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
```

### ast of  failed test cases 
TranslationUnitDecl 0x5562ce59c1c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5562ce6c2138 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_9.cpp:3:1, line:9:1> line:3:6 test_two_pointers 'void ()'
  `-CompoundStmt 0x5562ce6c27a0 <col:30, line:9:1>
    |-DeclStmt 0x5562ce6c23e8 <line:4:5, col:40>
    | `-VarDecl 0x5562ce6c21f8 <col:5, col:39> col:10 used p1 'int *' cinit
    |   `-CStyleCastExpr 0x5562ce6c23c0 <col:15, col:39> 'int *' <BitCast>
    |     `-CallExpr 0x5562ce6c2380 <col:21, col:39> 'void *'
    |       |-ImplicitCastExpr 0x5562ce6c2368 <col:21> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x5562ce6c22e0 <col:21> 'void *(size_t) noexcept(true)' lvalue Function 0x5562ce6a3a10 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x5562ce6c1598 'malloc')
    |       `-UnaryExprOrTypeTraitExpr 0x5562ce6c22c0 <col:28, col:38> 'unsigned long' sizeof 'int'
    |-DeclStmt 0x5562ce6c25a8 <line:5:5, col:40>
    | `-VarDecl 0x5562ce6c2418 <col:5, col:39> col:10 used p2 'int *' cinit
    |   `-CStyleCastExpr 0x5562ce6c2580 <col:15, col:39> 'int *' <BitCast>
    |     `-CallExpr 0x5562ce6c2540 <col:21, col:39> 'void *'
    |       |-ImplicitCastExpr 0x5562ce6c2528 <col:21> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x5562ce6c2500 <col:21> 'void *(size_t) noexcept(true)' lvalue Function 0x5562ce6a3a10 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x5562ce6c1598 'malloc')
    |       `-UnaryExprOrTypeTraitExpr 0x5562ce6c24e0 <col:28, col:38> 'unsigned long' sizeof 'int'
    |-IfStmt 0x5562ce6c26f0 <line:6:5, col:32>
    | |-BinaryOperator 0x5562ce6c2628 <col:9, /root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> 'bool' '!='
    | | |-ImplicitCastExpr 0x5562ce6c25f8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_9.cpp:6:9> 'int *' <LValueToRValue>
    | | | `-DeclRefExpr 0x5562ce6c25c0 <col:9> 'int *' lvalue Var 0x5562ce6c21f8 'p1' 'int *'
    | | `-ImplicitCastExpr 0x5562ce6c2610 </root/code_check/llvm-project/build/lib/clang/17/include/stddef.h:84:18> 'int *' <NullToPointer>
    | |   `-GNUNullExpr 0x5562ce6c25e0 <col:18> 'long'
    | `-CompoundStmt 0x5562ce6c26d8 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_9.cpp:6:21, col:32>
    |   `-BinaryOperator 0x5562ce6c26b8 <col:23, col:29> 'int' lvalue '='
    |     |-UnaryOperator 0x5562ce6c2680 <col:23, col:24> 'int' lvalue prefix '*' cannot overflow
    |     | `-ImplicitCastExpr 0x5562ce6c2668 <col:24> 'int *' <LValueToRValue>
    |     |   `-DeclRefExpr 0x5562ce6c2648 <col:24> 'int *' lvalue Var 0x5562ce6c21f8 'p1' 'int *'
    |     `-IntegerLiteral 0x5562ce6c2698 <col:29> 'int' 1
    `-BinaryOperator 0x5562ce6c2780 <line:7:5, col:11> 'int' lvalue '='
      |-UnaryOperator 0x5562ce6c2748 <col:5, col:6> 'int' lvalue prefix '*' cannot overflow
      | `-ImplicitCastExpr 0x5562ce6c2730 <col:6> 'int *' <LValueToRValue>
      |   `-DeclRefExpr 0x5562ce6c2710 <col:6> 'int *' lvalue Var 0x5562ce6c2418 'p2' 'int *'
      `-IntegerLiteral 0x5562ce6c2760 <col:11> 'int' 2



## reference logic step
**logic for registerMatchers**:
1. Match calls to dynamic memory allocation functions (malloc, calloc, realloc) using functionDecl matcher with appropriate names
2. Match variable declarations with pointer type that are initialized with allocation results using varDecl matcher with hasInitializer containing allocation calls
3. Match assignment expressions where pointer variables receive allocation results using binaryOperator matcher with operator '=' and RHS containing allocation calls
4. Match pointer usage patterns including dereference (*ptr), array subscript (ptr[...]), and member access through pointer (ptr->field)
5. Combine allocation patterns with usage patterns using hasDescendant relationships to find cases where allocated pointers are used
6. Bind allocation call, allocation variable, assignment variable, usage variable, and first bad use statement for retrieval in check()
**logic for check**:
1. Retrieve bound nodes: allocation call, allocation variable, assignment variable, usage variable, and first bad use statement
2. Determine the target variable declaration from available bound nodes (useVar, allocVar, or assignVar)
3. Find the containing function body for the target variable by checking declaration context or traversing AST parents
4. Collect all statements related to the target variable within the function body using RecursiveASTVisitor
5. Identify allocation statements, pointer usage statements, and null check statements for the target variable
6. Sort usage statements and check statements by source location for chronological analysis
7. For each pointer usage after allocation, verify if any null check occurs before that usage
8. If a usage lacks preceding null check, emit diagnostic at that usage location with appropriate message
9. Only report one violation per variable to avoid duplicate warnings


## reference astMatchers
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

AST Traversal Matcher: hasInitializer
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<VarDecl>
 Description: Matches a variable declaration that has an initializer expression
that matches the given matcher.

Example matches x (matcher = varDecl(hasInitializer(callExpr())))
  bool y() { return true; }
  bool x = y();

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

Node Matcher: memberPointerType
 Parameters;Matcher<MemberPointerType>...
 return type Matcher<Type>
 Description: Matches member pointer types.
Given
  struct A { int i; }
  A::* ptr = A::i;
memberPointerType()
  matches "A::* ptr"

anyOf(declRefExpr(to(decl().bind("deletedPointer"))), memberExpr(hasDeclaration(fieldDecl().bind("deletedMemberPointer"))))
Finder->addMatcher(stmt(forEachDescendant(varDecl(hasInitializer(RefVarOrField)).bind("pot_tid_var"))), this);
const auto AllocFunc = functionDecl(hasAnyName("malloc","::malloc", "std::malloc","alloca", "::alloca", "calloc","::calloc", "std::calloc", "::realloc", "realloc","std::realloc"));
const auto AllocCall = callExpr(callee(decl(anyOf(AllocFunc, AllocFuncPtr))));
Finder->addMatcher(binaryOperator(AdditiveOperator, hasLHS(anyOf(AllocCall, castExpr(hasSourceExpression(AllocCall)))), hasRHS(IntExpr)).bind("PtrArith"), this);


## reference code snippets  
for (Stmt *CodeBlock : CodeBlocks) {
  UseAfterMoveFinder Finder(Result.Context);
  UseAfterMove Use;
  if (Finder.find(CodeBlock, MovingCall, Arg->getDecl(), &Use))
    emitDiagnostic(MovingCall, Arg, Use, this, Result.Context);
}
else if (const auto *VD = Result.Nodes.getNodeAs<VarDecl>("Mark")) {
  const QualType T = VD->getType();
  if ((T->isPointerType() && !T->getPointeeType().isConstQualified()) ||
      T->isArrayType())
    markCanNotBeConst(VD->getInit(), true);
  else if (T->isLValueReferenceType() &&
           !T->getPointeeType().isConstQualified())
    markCanNotBeConst(VD->getInit(), false);
}
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
markRedeclarationsAsVisited(OriginalDeclaration);
diag(Matched->getBeginLoc(),
     "the value returned by this function should be used")
    << Matched->getSourceRange();
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
AST_MATCHER(VarDecl, isLocalVarDecl) { return Node.isLocalVarDecl(); }
const auto *LoopVar = Nodes.getNodeAs<VarDecl>(InitVarName);
const auto *EndVar = Nodes.getNodeAs<VarDecl>(EndVarName);
const auto *EndCall = Nodes.getNodeAs<CXXMemberCallExpr>(EndCallName);
const auto *BoundExpr = Nodes.getNodeAs<Expr>(ConditionBoundName);
SourceLocation clang::OMPDestroyClause::getVarLoc() const
StringRef clang::DiagnosticIDs::getWarningOptionForGroup(diag::Group)
bool clang::APValue::isNullPointer() const
uint64_t clang::TargetInfo::getNullPointerValue(LangAS AddrSpace) const
Stmt * clang::LambdaExpr::getBody() const
const Stmt * clang::ento::PathDiagnosticLocation::getStmtOrNull() const
CallGraphNode * clang::CallGraph::getOrInsertNode(Decl *)
SourceLocation clang::SourceLocExpr::getLocation() const
ArrayRef<CleanupObject> clang::ExprWithCleanups::getObjects() const



# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the current checker code above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
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


You can proceed with the analysis according to the following steps:

1.  Read the provided current checker code and analyze its implementation logic.
2.  Analyze the passed test cases code to understand how the checker successfully identifies issues in the code without generating false positives.
3.  Analyze the failed test cases code to determine why the checker fails to detect the issues present in these cases.
4.  Synthesize the findings from the above analyses. When generating the new code, follow the reference logic steps, consult the reference AST matchers, and utilize the reference code snippets to produce a complete and robust checker implementation. This new checker code should be capable of detecting all issues in the test cases while avoiding false positives.
5.  Output the final code strictly adhering to the specified output format requirements.

