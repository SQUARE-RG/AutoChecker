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