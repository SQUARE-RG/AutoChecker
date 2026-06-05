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
  if (Var->isReferenced() == false && Var->getDeclUse() == 0)
    return;
  
  // Find the parent function or compound statement
  const Stmt *ParentStmt = Var->getParentFunctionOrMethod();
  if (!ParentStmt)
    return;
  
  // Get all references to this variable within the parent scope
  llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs;
  for (const auto *Ref : Var->references()) {
    if (const auto *DRE = dyn_cast<DeclRefExpr>(Ref)) {
      AllVarRefs.insert(DRE);
    }
  }
  
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
        const Stmt *Parent = S;
        // Check for binary comparison with nullptr/NULL
        if (const auto *BO = dyn_cast_or_null<BinaryOperator>(S->getParent())) {
          if (BO->isComparisonOp() && 
              (BO->getOpcode() == BO_EQ || BO->getOpcode() == BO_NE)) {
            const Expr *Other = (BO->getLHS() == S) ? BO->getRHS() : BO->getLHS();
            if (Other && (Other->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull) != Expr::NPC_NeverIsNull)) {
              IsCheck = true;
              Uses.push_back({BO, BO->getExprLoc(), true});
              return;
            }
          }
        }
        // Check for unary '!' operator
        if (const auto *UO = dyn_cast_or_null<UnaryOperator>(S->getParent())) {
          if (UO->getOpcode() == UO_LNot) {
            IsCheck = true;
            Uses.push_back({UO, UO->getExprLoc(), true});
            return;
          }
        }
        // Check for implicit conversion in if/while condition
        if (const auto *IfS = dyn_cast_or_null<IfStmt>(S->getParent())) {
          if (IfS->getCond() == S) {
            IsCheck = true;
            Uses.push_back({IfS, IfS->getBeginLoc(), true});
            return;
          }
        }
        if (!IsCheck) {
          Uses.push_back({S, DRE->getLocation(), false});
        }
      }
    }
    
    // Recursively traverse children
    for (const auto *Child : S->children()) {
      CollectUses(Child);
    }
  };
  
  CollectUses(ParentStmt);
  
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
    // Check if the variable is used at all (excluding the check itself)
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