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
  
  auto &Ctx = Finder->getASTContext();
  
  while (Current) {
    if (const auto *CS = dyn_cast<CompoundStmt>(Current)) {
      const Stmt *Search = Target;
      while (Search) {
        if (Search == CS) return true;
        auto Parents = Ctx.getParents(*Search);
        if (Parents.empty()) break;
        Search = Parents[0].get<Stmt>();
      }
    }
    auto Parents = Ctx.getParents(*Current);
    if (Parents.empty()) break;
    Current = Parents[0].get<Stmt>();
  }
  return false;
}

AST_MATCHER_P(Expr, equalsBoundNode, std::string, ID) {
  const auto *BoundNode = Finder->getASTContext().getParents(Node);
  if (BoundNode.empty()) return false;
  const auto *DRE = dyn_cast<DeclRefExpr>(Node);
  if (!DRE) return false;
  const auto *Target = Finder->getNodeAs<DeclRefExpr>(ID);
  if (!Target) return false;
  return DRE->getDecl() == Target->getDecl();
}
} // namespace

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  auto FreeCallMatcher = callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("freeCall");

  auto DeleteExprMatcher = cxxDeleteExpr(
      has(expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("deleteExpr");

  auto ReallocCallMatcher = callExpr(
      callee(functionDecl(hasName("realloc"))),
      hasArgument(0, expr().bind("reallocPtr")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("reallocCall");

  auto NullAssignmentMatcher = binaryOperator(
      hasOperatorName("="),
      hasLHS(expr(hasDescendant(declRefExpr().bind("nullifiedPointer")))),
      hasRHS(anyOf(cxxNullPtrLiteralExpr(), integerLiteral(equals(0))))
  ).bind("nullAssign");

  Finder->addMatcher(
      traverse(TK_AsIs, FreeCallMatcher),
      this);
  Finder->addMatcher(
      traverse(TK_AsIs, DeleteExprMatcher),
      this);
  Finder->addMatcher(
      traverse(TK_AsIs, ReallocCallMatcher),
      this);
}

void RealsePointerNotSetNullCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();

  if (const auto *FreeCall = Result.Nodes.getNodeAs<CallExpr>("freeCall")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!FreeCall || !FreedPtr || !DeallocStmt || 
        !SM->isInMainFile(FreeCall->getBeginLoc()))
      return;
    checkDeallocation(FreeCall, FreedPtr, DeallocStmt, Result);
  }

  if (const auto *DeleteExpr = Result.Nodes.getNodeAs<CXXDeleteExpr>("deleteExpr")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!DeleteExpr || !FreedPtr || !DeallocStmt ||
        !SM->isInMainFile(DeleteExpr->getBeginLoc()))
      return;
    checkDeallocation(DeleteExpr, FreedPtr, DeallocStmt, Result);
  }

  if (const auto *ReallocCall = Result.Nodes.getNodeAs<CallExpr>("reallocCall")) {
    const auto *ReallocPtr = Result.Nodes.getNodeAs<Expr>("reallocPtr");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!ReallocCall || !ReallocPtr || !DeallocStmt ||
        !SM->isInMainFile(ReallocCall->getBeginLoc()))
      return;
    checkReallocation(ReallocCall, ReallocPtr, DeallocStmt, Result);
  }
}

void RealsePointerNotSetNullCheck::checkDeallocation(
    const Stmt *DeallocStmt, const Expr *FreedPtr, const Stmt *ParentStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();
  
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    auto Parents = Ctx->getParents(*ParentStmt);
    if (!Parents.empty()) {
      ParentCS = Parents[0].get<CompoundStmt>();
    }
  }
  if (!ParentCS) return;

  bool FoundNullAssignment = false;
  bool InSameScope = false;
  bool ControlFlowBreak = false;

  for (const auto *S : ParentCS->body()) {
    if (S == DeallocStmt) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
      if (BO->getOpcode() == BO_Assign) {
        const Expr *LHS = BO->getLHS()->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = BO->getRHS()->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (const auto *CE = dyn_cast<CXXOperatorCallExpr>(S)) {
      if (CE->getOperator() == OO_Equal && CE->getNumArgs() == 2) {
        const Expr *LHS = CE->getArg(0)->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = CE->getArg(1)->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

  if (!FoundNullAssignment && !ControlFlowBreak) {
    diag(DeallocStmt->getBeginLoc(), 
         "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]")
        << DeallocStmt->getSourceRange();
  }
}

void RealsePointerNotSetNullCheck::checkReallocation(
    const CallExpr *ReallocCall, const Expr *ReallocPtr, const Stmt *ParentStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();
  
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    auto Parents = Ctx->getParents(*ParentStmt);
    if (!Parents.empty()) {
      ParentCS = Parents[0].get<CompoundStmt>();
    }
  }
  if (!ParentCS) return;

  bool FoundNullAssignment = false;
  bool InSameScope = false;
  bool ControlFlowBreak = false;

  for (const auto *S : ParentCS->body()) {
    if (S == ReallocCall) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
      if (BO->getOpcode() == BO_Assign) {
        const Expr *LHS = BO->getLHS()->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = BO->getRHS()->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (const auto *CE = dyn_cast<CXXOperatorCallExpr>(S)) {
      if (CE->getOperator() == OO_Equal && CE->getNumArgs() == 2) {
        const Expr *LHS = CE->getArg(0)->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = CE->getArg(1)->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

  if (!FoundNullAssignment && !ControlFlowBreak) {
    diag(ReallocCall->getBeginLoc(),
         "realloc后原始指针应置空 [gjb8114-r-1-3-6]")
        << ReallocCall->getSourceRange();
  }
}

} // namespace clang::tidy::ucassaat