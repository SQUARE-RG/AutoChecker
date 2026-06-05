//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/Basic/Diagnostic.h"
#include <set>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to collect all variables that are passed by non-const pointer
// or array to a function call, including struct pointer members
static void collectModifiedVars(const CallExpr *Call,
                                std::set<const ValueDecl *> &ModifiedVars) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  for (unsigned I = 0; I < Call->getNumArgs() && I < FD->getNumParams(); ++I) {
    const ParmVarDecl *Param = FD->getParamDecl(I);
    QualType ParamType = Param->getType();

    // Check if parameter is non-const pointer or array type
    bool IsNonConstPointer = false;
    if (ParamType->isPointerType()) {
      // For pointer types, check the pointee type's const qualification
      IsNonConstPointer = !ParamType->getPointeeType().isConstQualified();
    } else if (ParamType->isArrayType()) {
      // Array parameters decay to pointers, check the element type
      const ArrayType *ArrType = ParamType->getAsArrayTypeUnsafe();
      if (ArrType) {
        IsNonConstPointer = !ArrType->getElementType().isConstQualified();
      }
    }

    if (!IsNonConstPointer)
      continue;

    const Expr *Arg = Call->getArg(I)->IgnoreParenImpCasts();

    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        ModifiedVars.insert(VD);
      }
    }
  }
}

// Helper function to collect global variables modified by a function call
static void collectModifiedGlobals(const CallExpr *Call,
                                   std::set<const ValueDecl *> &ModifiedGlobals) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  // Check if the function definition is available
  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    // Traverse the body to find modifications to global variables
    std::function<void(const Stmt*)> findGlobalMods = [&](const Stmt* S) {
      if (!S) return;
      if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
        if (BO->isAssignmentOp()) {
          const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
              ModifiedGlobals.insert(VD);
            }
          }
        }
      }
      // Check for unary increment/decrement on globals
      if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
        if (UO->isIncrementDecrementOp()) {
          const Expr *Sub = UO->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(Sub)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
              ModifiedGlobals.insert(VD);
            }
          }
        }
      }
      // Check for compound assignments
      if (const auto *CAO = dyn_cast<CompoundAssignOperator>(S)) {
        const Expr *LHS = CAO->getLHS()->IgnoreParenImpCasts();
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
            ModifiedGlobals.insert(VD);
          }
        }
      }
      for (const Stmt *Child : S->children()) {
        findGlobalMods(Child);
      }
    };
    findGlobalMods(Body);
  }
}

// Helper function to check if two function calls have data dependency
// through pointer/array arguments or through global variables
static bool hasDataDependency(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // Collect all variables that are potentially modified by Call1
  std::set<const ValueDecl *> ModifiedVars;
  collectModifiedVars(Call1, ModifiedVars);

  // Also collect global variables modified by Call1
  std::set<const ValueDecl *> ModifiedGlobals;
  collectModifiedGlobals(Call1, ModifiedGlobals);

  // Check if Call2 accesses any of the modified variables (via pointer/array args)
  const FunctionDecl *FD2 = Call2->getDirectCallee();
  if (!FD2)
    return false;

  for (unsigned I = 0; I < Call2->getNumArgs(); ++I) {
    const Expr *Arg = Call2->getArg(I)->IgnoreParenImpCasts();

    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call2->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        if (ModifiedVars.count(VD))
          return true;
      }
    }
  }

  // Check if Call2 accesses any of the modified global variables
  if (!ModifiedGlobals.empty()) {
    // Check if Call2's callee also accesses these globals
    if (FD2->hasBody()) {
      const Stmt *Body2 = FD2->getBody();
      std::function<bool(const Stmt*)> accessesGlobal = [&](const Stmt* S) -> bool {
        if (!S) return false;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage() && ModifiedGlobals.count(VD)) {
            return true;
          }
        }
        for (const Stmt *Child : S->children()) {
          if (accessesGlobal(Child)) return true;
        }
        return false;
      };
      if (accessesGlobal(Body2)) {
        return true;
      }
    }
  }

  return false;
}

// Helper function to collect static local variables modified by a function call
static void collectModifiedStaticLocals(const CallExpr *Call,
                                        std::set<const ValueDecl *> &ModifiedStaticLocals) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    std::function<void(const Stmt*)> findStaticMods = [&](const Stmt* S) {
      if (!S) return;
      if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
        if (BO->isAssignmentOp()) {
          const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
              ModifiedStaticLocals.insert(VD);
            }
          }
        }
      }
      // Check for unary increment/decrement on static locals
      if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
        if (UO->isIncrementDecrementOp()) {
          const Expr *Sub = UO->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(Sub)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
              ModifiedStaticLocals.insert(VD);
            }
          }
        }
      }
      // Check for compound assignments
      if (const auto *CAO = dyn_cast<CompoundAssignOperator>(S)) {
        const Expr *LHS = CAO->getLHS()->IgnoreParenImpCasts();
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
            ModifiedStaticLocals.insert(VD);
          }
        }
      }
      for (const Stmt *Child : S->children()) {
        findStaticMods(Child);
      }
    };
    findStaticMods(Body);
  }
}

// Helper function to check if a function call accesses specific static local variables
static bool accessesStaticLocals(const CallExpr *Call,
                                 const std::set<const ValueDecl *> &StaticLocals) {
  if (!Call || StaticLocals.empty())
    return false;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return false;

  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    std::function<bool(const Stmt*)> findAccess = [&](const Stmt* S) -> bool {
      if (!S) return false;
      if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
        const ValueDecl *VD = DRE->getDecl();
        if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal() && StaticLocals.count(VD)) {
          return true;
        }
      }
      for (const Stmt *Child : S->children()) {
        if (findAccess(Child)) return true;
      }
      return false;
    };
    return findAccess(Body);
  }
  return false;
}

// Extended data dependency check that includes static local variables
static bool hasDataDependencyEx(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // First check original data dependency
  if (hasDataDependency(Call1, Call2))
    return true;

  // Check static local variable dependency
  std::set<const ValueDecl *> ModifiedStaticLocals;
  collectModifiedStaticLocals(Call1, ModifiedStaticLocals);

  if (!ModifiedStaticLocals.empty()) {
    if (accessesStaticLocals(Call2, ModifiedStaticLocals))
      return true;
  }

  return false;
}

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match call expressions that are arguments to another call expression
  Finder->addMatcher(
      callExpr(
          forEachArgumentWithParamType(
              callExpr().bind("call"),
              qualType())
      ).bind("parentCall"),
      this);
  
  // Match binary operators that contain at least two CallExpr nodes
  Finder->addMatcher(
      binaryOperator(
          anyOf(hasOperatorName("+"), hasOperatorName("-"),
                hasOperatorName("*"), hasOperatorName("/"),
                hasOperatorName("%"), hasOperatorName("&"),
                hasOperatorName("|"), hasOperatorName("^"),
                hasOperatorName("&&"), hasOperatorName("||"),
                hasOperatorName("=="), hasOperatorName("!="),
                hasOperatorName("<"), hasOperatorName(">"),
                hasOperatorName("<="), hasOperatorName(">="),
                hasOperatorName("<<"), hasOperatorName(">>")),
          forEachDescendant(callExpr().bind("call")))
          .bind("binaryOp"),
      this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *ParentCall = Result.Nodes.getNodeAs<CallExpr>("parentCall");
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("call");

  // Use a static set to track processed expressions to avoid duplicate reports
  static std::set<const Stmt*> ProcessedExprs;

  if (BinaryOp && Call) {
    if (ProcessedExprs.count(BinaryOp))
      return;

    // Collect all call expressions within this binary operator
    std::vector<const CallExpr*> Calls;
    std::function<void(const Stmt*)> collectCalls = [&](const Stmt* S) {
      if (!S) return;
      if (const auto* CE = dyn_cast<CallExpr>(S)) {
        // Make sure this call is a direct child of the binary operator
        bool isDirectChild = false;
        for (const Stmt* Child : BinaryOp->children()) {
          if (Child == S) {
            isDirectChild = true;
            break;
          }
          if (const auto* ICE = dyn_cast<ImplicitCastExpr>(Child)) {
            if (ICE->getSubExpr() == S) {
              isDirectChild = true;
              break;
            }
          }
        }
        if (isDirectChild) {
          Calls.push_back(CE);
        }
      }
      for (const Stmt* Child : S->children()) {
        collectCalls(Child);
      }
    };
    collectCalls(BinaryOp);

    ProcessedExprs.insert(BinaryOp);

    if (Calls.size() < 2)
      return;

    // Check all pairs of calls for data dependency
    for (size_t i = 0; i < Calls.size(); ++i) {
      for (size_t j = i + 1; j < Calls.size(); ++j) {
        if (hasDataDependencyEx(Calls[i], Calls[j]) ||
            hasDataDependencyEx(Calls[j], Calls[i])) {
          diag(BinaryOp->getExprLoc(),
               "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
          return;
        }
      }
    }
  }

  if (ParentCall && Call) {
    if (ProcessedExprs.count(ParentCall))
      return;

    // Collect all call expressions that are direct arguments of the parent call
    std::vector<const CallExpr*> Calls;
    for (unsigned I = 0; I < ParentCall->getNumArgs(); ++I) {
      const Expr *Arg = ParentCall->getArg(I)->IgnoreParenImpCasts();
      if (const auto *CE = dyn_cast<CallExpr>(Arg)) {
        Calls.push_back(CE);
      }
    }

    ProcessedExprs.insert(ParentCall);

    if (Calls.size() < 2)
      return;

    // Check all pairs of calls for data dependency
    for (size_t i = 0; i < Calls.size(); ++i) {
      for (size_t j = i + 1; j < Calls.size(); ++j) {
        if (hasDataDependencyEx(Calls[i], Calls[j]) ||
            hasDataDependencyEx(Calls[j], Calls[i])) {
          diag(ParentCall->getBeginLoc(),
               "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
          return;
        }
      }
    }
  }
}

} // namespace clang::tidy::ucassaat