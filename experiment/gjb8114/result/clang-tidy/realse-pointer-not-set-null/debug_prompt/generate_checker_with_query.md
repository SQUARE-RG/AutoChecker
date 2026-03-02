使用增强逻辑生成checker代码，原始回答:
checker_cpp:
```cpp
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

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  // Match free() calls
  auto FreeCallMatcher = callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("freeCall");

  // Match delete expressions
  auto DeleteExprMatcher = cxxDeleteExpr(
      has(expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("deleteExpr");

  // Match realloc() calls
  auto ReallocCallMatcher = callExpr(
      callee(functionDecl(hasName("realloc"))),
      hasArgument(0, expr().bind("reallocPtr")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("reallocCall");

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
  
  ASTContext *Ctx = Result.Context;
  
  // Extract the pointer declaration
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  // Find the enclosing compound statement
  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
    if (!Parents.empty()) {
      ParentCS = Parents[0].get<CompoundStmt>();
    }
  }
  if (!ParentCS) return;

  bool FoundNullAssignment = false;
  bool InSameScope = false;
  bool ControlFlowBreak = false;

  // Scan statements after the deallocation
  for (const auto *S : ParentCS->body()) {
    if (S == DeallocStmt) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    // Check for assignment to null
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
            // Assignment to non-null value, treat as control flow break
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    // Check for C++ operator= assignment to null
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

    // Check for control flow statements that break the sequence
    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S) ||
        isa<GotoStmt>(S) || isa<BreakStmt>(S) || isa<ContinueStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

  // Report violation if no null assignment found and no control flow break
  if (!FoundNullAssignment && !ControlFlowBreak) {
    diag(DeallocStmt->getBeginLoc(), 
         "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]")
        << DeallocStmt->getSourceRange();
  }
}

void RealsePointerNotSetNullCheck::checkReallocation(
    const CallExpr *ReallocCall, const Expr *ReallocPtr, const Stmt *ParentStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  ASTContext *Ctx = Result.Context;
  
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
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
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S) ||
        isa<GotoStmt>(S) || isa<BreakStmt>(S) || isa<ContinueStmt>(S)) {
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
```

checker_h:
```cpp
//===--- RealsePointerNotSetNullCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Prohibition of Failing to Set Pointers to Null After Release.
/// This rule mandates that after a pointer variable is freed using free() 
/// (in C) or delete/delete[] (in C++), it must be immediately set to a null value.
/// In C, NULL should be used, while in C++, nullptr is recommended (though NULL is acceptable).
/// The nullification must occur within the same scope as the deallocation, 
/// without being split across conditional branches.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/realse-pointer-not-set-null.html
class RealsePointerNotSetNullCheck : public ClangTidyCheck {
public:
  RealsePointerNotSetNullCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;

private:
  void checkDeallocation(const Stmt *DeallocStmt, const Expr *FreedPtr,
                         const Stmt *ParentStmt,
                         const ast_matchers::MatchFinder::MatchResult &Result);
  void checkReallocation(const CallExpr *ReallocCall, const Expr *ReallocPtr,
                         const Stmt *ParentStmt,
                         const ast_matchers::MatchFinder::MatchResult &Result);
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
```