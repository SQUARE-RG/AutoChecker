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
              // Check if the parent of the ICE is an IfStmt condition
              if (!GrandParents.empty()) {
                if (const auto *GrandIf = dyn_cast_or_null<IfStmt>(GrandParents.begin()->get<Stmt>())) {
                  if (GrandIf->getCond() == ICE) {
                    IsCheck = true;
                    Uses.push_back(UseInfo{GrandIf, GrandIf->getBeginLoc(), true, false, false});
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