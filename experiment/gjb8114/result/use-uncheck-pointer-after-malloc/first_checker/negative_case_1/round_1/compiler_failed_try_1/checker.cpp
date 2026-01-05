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
bool isNullCheckBinary(const BinaryOperator *BO, const VarDecl *Var,
                       ASTContext &Context) {
  if (BO->getOpcode() != BO_EQ && BO->getOpcode() != BO_NE)
    return false;

  const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
  const Expr *RHS = BO->getRHS()->IgnoreParenImpCasts();

  // Check if one side is a reference to our variable
  const DeclRefExpr *VarRef = nullptr;
  const Expr *Other = nullptr;

  if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
    if (DRE->getDecl() == Var) {
      VarRef = DRE;
      Other = RHS;
    }
  }
  if (!VarRef && (VarRef = dyn_cast<DeclRefExpr>(RHS))) {
    if (VarRef->getDecl() == Var) {
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
bool isNullCheckUnary(const UnaryOperator *UO, const VarDecl *Var) {
  if (UO->getOpcode() != UO_LNot)
    return false;

  const Expr *SubExpr = UO->getSubExpr()->IgnoreParenImpCasts();
  if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
    return DRE->getDecl() == Var;
  }
  return false;
}

// Helper to check if an implicit cast to bool is a null check (like if(ptr))
bool isImplicitBoolCast(const ImplicitCastExpr *ICE, const VarDecl *Var) {
  if (ICE->getCastKind() != CK_PointerToBoolean)
    return false;

  const Expr *SubExpr = ICE->getSubExpr()->IgnoreParenImpCasts();
  if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
    return DRE->getDecl() == Var;
  }
  return false;
}

// Check if a statement is a null check for the given variable
bool isNullCheck(const Stmt *S, const VarDecl *Var, ASTContext &Context) {
  if (!S)
    return false;

  // Handle binary operator (ptr == NULL, ptr != NULL)
  if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
    return isNullCheckBinary(BO, Var, Context);
  }

  // Handle unary operator (!ptr)
  if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
    return isNullCheckUnary(UO, Var);
  }

  // Handle implicit cast to bool (if(ptr))
  if (const auto *ICE = dyn_cast<ImplicitCastExpr>(S)) {
    return isImplicitBoolCast(ICE, Var);
  }

  // For conditional operators, check the condition
  if (const auto *Cond = dyn_cast<ConditionalOperator>(S)) {
    return isNullCheck(Cond->getCond(), Var, Context);
  }

  // For IfStmt, WhileStmt, DoStmt, ForStmt - check their condition
  if (const auto *If = dyn_cast<IfStmt>(S)) {
    return isNullCheck(If->getCond(), Var, Context);
  }
  if (const auto *While = dyn_cast<WhileStmt>(S)) {
    return isNullCheck(While->getCond(), Var, Context);
  }
  if (const auto *Do = dyn_cast<DoStmt>(S)) {
    return isNullCheck(Do->getCond(), Var, Context);
  }
  if (const auto *For = dyn_cast<ForStmt>(S)) {
    return isNullCheck(For->getCond(), Var, Context);
  }

  return false;
}

// Check if a statement is a use of the variable (dereference or subscript)
[[maybe_unused]] bool isPointerUse(const Stmt *S, const VarDecl *Var) {
  if (!S)
    return false;

  // Dereference operator (*ptr)
  if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
    if (UO->getOpcode() == UO_Deref) {
      const Expr *SubExpr = UO->getSubExpr()->IgnoreParenImpCasts();
      if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
        return DRE->getDecl() == Var;
      }
    }
    return false;
  }

  // Array subscript (ptr[...])
  if (const auto *ASE = dyn_cast<ArraySubscriptExpr>(S)) {
    const Expr *Base = ASE->getBase()->IgnoreParenImpCasts();
    if (const auto *DRE = dyn_cast<DeclRefExpr>(Base)) {
      return DRE->getDecl() == Var;
    }
    return false;
  }

  // Passing as argument to a function (could be a use, but we'll be conservative)
  // For now, we only check dereference and subscript
  return false;
}

// Get all statements related to a variable in a function body
void collectVarStatements(const VarDecl *Var, const Stmt *FunctionBody,
                          ASTContext &Context,
                          llvm::SmallVectorImpl<const Stmt *> &AllocStmts,
                          llvm::SmallVectorImpl<const Stmt *> &UseStmts,
                          llvm::SmallVectorImpl<const Stmt *> &CheckStmts) {
  struct Collector : public RecursiveASTVisitor<Collector> {
    const VarDecl *Var;
    ASTContext &Context;
    llvm::SmallVectorImpl<const Stmt *> &AllocStmts;
    llvm::SmallVectorImpl<const Stmt *> &UseStmts;
    llvm::SmallVectorImpl<const Stmt *> &CheckStmts;

    Collector(const VarDecl *Var, ASTContext &Context,
              llvm::SmallVectorImpl<const Stmt *> &AllocStmts,
              llvm::SmallVectorImpl<const Stmt *> &UseStmts,
              llvm::SmallVectorImpl<const Stmt *> &CheckStmts)
        : Var(Var), Context(Context), AllocStmts(AllocStmts),
          UseStmts(UseStmts), CheckStmts(CheckStmts) {}

    bool VisitCallExpr(CallExpr *CE) {
      // Check if this is an allocation call that initializes our variable
      // This is simplified - a full implementation would track assignments
      return true;
    }

    bool VisitStmt(Stmt *S) {
      if (isPointerUse(S, Var)) {
        UseStmts.push_back(S);
      } else if (isNullCheck(S, Var, Context)) {
        CheckStmts.push_back(S);
      }
      return true;
    }
  };

  Collector collector(Var, Context, AllocStmts, UseStmts, CheckStmts);
  collector.TraverseStmt(const_cast<Stmt *>(FunctionBody));
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

  // Matcher for pointer uses (dereference or array subscript)
  const auto PointerUse = stmt(anyOf(
      unaryOperator(hasOperatorName("*"),
          has(ignoringParenImpCasts(declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))
      ).bind("derefUse"),
      arraySubscriptExpr(
          hasBase(ignoringParenImpCasts(declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))
      ).bind("subscriptUse")
  )).bind("firstBadUse");

  // Combine: find a variable from allocation, then a use of that variable
  // We'll check in the callback whether there was a null check before the use
  Finder->addMatcher(
      traverse(TK_AsIs,
          stmt(hasDescendant(AllocVarDecl), hasDescendant(PointerUse))
      ),
      this
  );
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *AllocVar = Result.Nodes.getNodeAs<VarDecl>("allocVar");
  const auto *FirstBadUse = Result.Nodes.getNodeAs<Stmt>("firstBadUse");
  const auto *AllocCall = Result.Nodes.getNodeAs<CallExpr>("allocCall");

  if (!AllocVar || !FirstBadUse || !AllocCall)
    return;

  // Get the function body containing the variable
  const DeclContext *DC = AllocVar->getDeclContext();
  const FunctionDecl *Func = dyn_cast<FunctionDecl>(DC);
  if (!Func || !Func->hasBody())
    return;

  const Stmt *Body = Func->getBody();
  if (!Body)
    return;

  SourceManager &SM = *Result.SourceManager;
  ASTContext &Context = *Result.Context;

  // Collect all statements related to this variable
  llvm::SmallVector<const Stmt *, 8> AllocStmts;
  llvm::SmallVector<const Stmt *, 16> UseStmts;
  llvm::SmallVector<const Stmt *, 8> CheckStmts;

  collectVarStatements(AllocVar, Body, Context, AllocStmts, UseStmts, CheckStmts);

  // If no uses, no violation
  if (UseStmts.empty())
    return;

  // Sort all statements by source location
  auto compareSourceLoc = [&SM](const Stmt *A, const Stmt *B) {
    return SM.isBeforeInTranslationUnit(A->getBeginLoc(), B->getBeginLoc());
  };

  std::sort(UseStmts.begin(), UseStmts.end(), compareSourceLoc);
  std::sort(CheckStmts.begin(), CheckStmts.end(), compareSourceLoc);

  // Find the allocation statement (simplified - use the actual allocation call)
  const Stmt *AllocStmt = AllocCall;
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
          << AllocVar;
      return; // Only report one warning per variable
    }
  }
}

} // namespace clang::tidy::ucassaat