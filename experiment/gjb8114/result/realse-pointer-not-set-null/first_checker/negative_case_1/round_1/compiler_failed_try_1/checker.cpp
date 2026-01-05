//===--- RealsePointerNotSetNullCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "RealsePointerNotSetNullCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {
AST_MATCHER_P(Stmt, isInSameScopeAs, const Stmt *, Other) {
  const Stmt *Current = &Node;
  const Stmt *Target = Other;
  
  // Use ASTContext's getParents() for parent traversal
  auto &Ctx = Finder->getASTContext();
  
  while (Current) {
    if (const auto *CS = dyn_cast<CompoundStmt>(Current)) {
      // Check if Target is within this CompoundStmt
      const Stmt *Search = Target;
      while (Search) {
        if (Search == CS) return true;
        // Get parent using ASTContext
        auto Parents = Ctx.getParents(*Search);
        if (Parents.empty()) break;
        Search = Parents[0].get<Stmt>();
      }
    }
    // Get parent using ASTContext
    auto Parents = Ctx.getParents(*Current);
    if (Parents.empty()) break;
    Current = Parents[0].get<Stmt>();
  }
  return false;
}
} // namespace

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  // Match free() calls
  auto FreeCallMatcher = callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freedPointer")),
      unless(hasAncestor(callExpr()))
  ).bind("freeCall");

  // Match delete expressions
  auto DeleteExprMatcher = cxxDeleteExpr(
      has(expr().bind("freedPointer"))
  ).bind("deleteExpr");

  // Match realloc() calls
  auto ReallocCallMatcher = callExpr(
      callee(functionDecl(hasName("realloc"))),
      hasArgument(0, expr().bind("reallocPtr")),
      unless(hasAncestor(callExpr()))
  ).bind("reallocCall");

  // Combine matchers
  Finder->addMatcher(FreeCallMatcher, this);
  Finder->addMatcher(DeleteExprMatcher, this);
  Finder->addMatcher(ReallocCallMatcher, this);
}

void RealsePointerNotSetNullCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();

  // Check for free() calls
  if (const auto *FreeCall = Result.Nodes.getNodeAs<CallExpr>("freeCall")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    if (!FreeCall || !FreedPtr || !SM->isInMainFile(FreeCall->getBeginLoc()))
      return;

    checkDeallocation(FreeCall, FreedPtr, Result);
  }

  // Check for delete expressions
  if (const auto *DeleteExpr = Result.Nodes.getNodeAs<CXXDeleteExpr>("deleteExpr")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    if (!DeleteExpr || !FreedPtr || !SM->isInMainFile(DeleteExpr->getBeginLoc()))
      return;

    checkDeallocation(DeleteExpr, FreedPtr, Result);
  }

  // Check for realloc() calls
  if (const auto *ReallocCall = Result.Nodes.getNodeAs<CallExpr>("reallocCall")) {
    const auto *ReallocPtr = Result.Nodes.getNodeAs<Expr>("reallocPtr");
    if (!ReallocCall || !ReallocPtr || !SM->isInMainFile(ReallocCall->getBeginLoc()))
      return;

    checkReallocation(ReallocCall, ReallocPtr, Result);
  }
}

void RealsePointerNotSetNullCheck::checkDeallocation(
    const Stmt *DeallocStmt, const Expr *FreedPtr, 
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();
  
  // Get the pointer variable declaration
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  // Find the parent compound statement
  const CompoundStmt *ParentCS = nullptr;
  const Stmt *Current = DeallocStmt;
  while (Current) {
    ParentCS = dyn_cast<CompoundStmt>(Current);
    if (ParentCS) break;
    // Get parent using ASTContext
    auto Parents = Ctx->getParents(*Current);
    if (Parents.empty()) break;
    Current = Parents[0].get<Stmt>();
  }

  if (!ParentCS) return;

  // Look for null assignment after deallocation
  bool FoundNullAssignment = false;
  bool InSameScope = false;
  const Stmt *NullAssignmentStmt = nullptr;

  // Traverse statements in the compound statement
  for (const auto *S : ParentCS->body()) {
    if (S == DeallocStmt) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    // Check if this statement assigns the pointer to null
    if (isNullAssignmentToPtr(S, PtrDecl, Ctx)) {
      FoundNullAssignment = true;
      NullAssignmentStmt = S;
      break;
    }

    // If we hit a control flow statement that might separate the deallocation
    // from null assignment, check if null assignment is in a different branch
    if (const auto *If = dyn_cast<IfStmt>(S)) {
      if (checkNullAssignmentInDifferentBranch(If, PtrDecl, DeallocStmt, Result)) {
        diag(DeallocStmt->getBeginLoc(), 
             "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]")
            << DeallocStmt->getSourceRange();
        return;
      }
      // After checking an if statement, we can't assume sequential execution
      break;
    }

    // Similar checks for other control flow
    if (isa<ForStmt>(S) || isa<WhileStmt>(S) || isa<DoStmt>(S) || 
        isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
      break;
    }
  }

  if (!FoundNullAssignment) {
    diag(DeallocStmt->getBeginLoc(), 
         "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]")
        << DeallocStmt->getSourceRange();
  }
}

void RealsePointerNotSetNullCheck::checkReallocation(
    const CallExpr *ReallocCall, const Expr *ReallocPtr,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();
  
  // Get the pointer variable declaration
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  // Find the parent compound statement
  const CompoundStmt *ParentCS = nullptr;
  const Stmt *Current = ReallocCall;
  while (Current) {
    ParentCS = dyn_cast<CompoundStmt>(Current);
    if (ParentCS) break;
    // Get parent using ASTContext
    auto Parents = Ctx->getParents(*Current);
    if (Parents.empty()) break;
    Current = Parents[0].get<Stmt>();
  }

  if (!ParentCS) return;

  // Look for null assignment of original pointer after realloc
  bool FoundNullAssignment = false;
  bool InSameScope = false;

  for (const auto *S : ParentCS->body()) {
    if (S == ReallocCall) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    // Check if this statement assigns the ORIGINAL pointer to null
    if (isNullAssignmentToPtr(S, PtrDecl, Ctx)) {
      FoundNullAssignment = true;
      break;
    }

    // Stop at control flow boundaries
    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
      break;
    }
  }

  if (!FoundNullAssignment) {
    diag(ReallocCall->getBeginLoc(),
         "realloc后原始指针应置空 [gjb8114-r-1-3-6]")
        << ReallocCall->getSourceRange();
  }
}

bool RealsePointerNotSetNullCheck::isNullAssignmentToPtr(
    const Stmt *S, const ValueDecl *PtrDecl, const ASTContext *Ctx) {
  
  // Check for binary operator assignment: ptr = NULL/nullptr/0
  if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
    if (BO->getOpcode() == BO_Assign) {
      const Expr *LHS = BO->getLHS()->IgnoreParenCasts();
      const Expr *RHS = BO->getRHS()->IgnoreParenCasts();
      
      // Check if LHS refers to our pointer
      const ValueDecl *LHSDecl = nullptr;
      if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
        LHSDecl = DRE->getDecl();
      } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
        LHSDecl = ME->getMemberDecl();
      }
      
      if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
        // Check if RHS is a null pointer constant
        // Remove const qualifier to match isNullPointerConstant signature
        ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
        if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
          return true;
        }
      }
    }
  }
  
  // Check for C++11 nullptr assignment: ptr = nullptr
  if (const auto *CE = dyn_cast<CXXOperatorCallExpr>(S)) {
    if (CE->getOperator() == OO_Equal) {
      if (CE->getNumArgs() == 2) {
        const Expr *LHS = CE->getArg(0)->IgnoreParenCasts();
        const Expr *RHS = CE->getArg(1)->IgnoreParenCasts();
        
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          // Remove const qualifier to match isNullPointerConstant signature
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            return true;
          }
        }
      }
    }
  }
  
  return false;
}

bool RealsePointerNotSetNullCheck::checkNullAssignmentInDifferentBranch(
    const IfStmt *If, const ValueDecl *PtrDecl, const Stmt *DeallocStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  
  // Check if deallocation is in the if branch
  const Stmt *Then = If->getThen();
  const Stmt *Else = If->getElse();
  
  bool DeallocInThen = false;
  bool DeallocInElse = false;
  
  // Check if deallocation is in then branch
  if (Then && Then->getStmtClass() == DeallocStmt->getStmtClass()) {
    if (Then == DeallocStmt) DeallocInThen = true;
  } else if (Then) {
    // Recursively check compound statements
    DeallocInThen = containsStmt(Then, DeallocStmt);
  }
  
  // Check if deallocation is in else branch
  if (Else && Else->getStmtClass() == DeallocStmt->getStmtClass()) {
    if (Else == DeallocStmt) DeallocInElse = true;
  } else if (Else) {
    DeallocInElse = containsStmt(Else, DeallocStmt);
  }
  
  // If deallocation is in one branch, check if null assignment is in the other
  if (DeallocInThen && Else) {
    return containsNullAssignmentToPtr(Else, PtrDecl, Ctx);
  }
  
  if (DeallocInElse && Then) {
    return containsNullAssignmentToPtr(Then, PtrDecl, Ctx);
  }
  
  return false;
}

bool RealsePointerNotSetNullCheck::containsStmt(
    const Stmt *Container, const Stmt *Target) {
  
  if (Container == Target) return true;
  
  for (const auto *Child : Container->children()) {
    if (!Child) continue;
    if (containsStmt(Child, Target)) return true;
  }
  
  return false;
}

bool RealsePointerNotSetNullCheck::containsNullAssignmentToPtr(
    const Stmt *S, const ValueDecl *PtrDecl, const ASTContext *Ctx) {
  
  if (isNullAssignmentToPtr(S, PtrDecl, Ctx)) return true;
  
  for (const auto *Child : S->children()) {
    if (!Child) continue;
    if (containsNullAssignmentToPtr(Child, PtrDecl, Ctx)) return true;
  }
  
  return false;
}

} // namespace clang::tidy::ucassaat