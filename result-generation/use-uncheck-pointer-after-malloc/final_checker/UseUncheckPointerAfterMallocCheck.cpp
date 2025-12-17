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
#include "clang/Lex/Lexer.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Expr.h"
#include "clang/AST/OperationKinds.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallPtrSet.h"
#include <string>
#include <map>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Helper function to check if a statement is a descendant of another statement
static bool isDescendant(const Stmt *Descendant, const Stmt *Ancestor,
                         ASTContext *Context) {
  if (!Descendant || !Ancestor || Descendant == Ancestor) {
    return false;
  }
  
  auto Parents = Context->getParents(*Descendant);
  while (!Parents.empty()) {
    if (const Stmt *Parent = Parents[0].get<Stmt>()) {
      if (Parent == Ancestor) {
        return true;
      }
      Parents = Context->getParents(*Parent);
    } else {
      break;
    }
  }
  return false;
}

// Matcher for dynamic memory allocation functions
const auto AllocFuncMatcher = functionDecl(
    hasAnyName("::malloc", "::calloc", "::realloc", "std::malloc", 
               "std::calloc", "std::realloc"));

// Matcher for allocation calls
const auto AllocCallMatcher = callExpr(
    callee(AllocFuncMatcher),
    unless(hasAncestor(callExpr()))).bind("allocCall");

// Helper matcher to find the pointer variable from allocation
const auto PointerVarFromAllocMatcher = stmt(anyOf(
    // Direct assignment: p = malloc()
    binaryOperator(hasOperatorName("="),
        hasLHS(expr(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("ptrVar")))))),
        hasRHS(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))),
    // Variable declaration with initialization: int *p = malloc()
    declStmt(hasSingleDecl(varDecl(
        hasInitializer(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher)))),
        hasType(pointerType()))
        .bind("ptrVarDecl")))
)).bind("allocExpr");

// Matcher for pointer usage
const auto PointerUseMatcher = expr(
    anyOf(
        // Dereference: *p
        unaryOperator(hasOperatorName("*"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Array subscript: p[0]
        arraySubscriptExpr(
            hasBase(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Member access through pointer: p->field
        memberExpr(hasObjectExpression(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar")))))),
        // Function call through pointer: p()
        callExpr(has(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar"))))))
    )).bind("pointerUse");

// Matcher for null pointer checks
const auto NullCheckMatcher = stmt(
    anyOf(
        // Explicit comparisons: ptr == NULL, ptr != NULL
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))),
            hasRHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0))))),
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0)))),
            hasRHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Implicit checks: if (ptr), while (ptr)
        implicitCastExpr(hasImplicitDestinationType(booleanType()),
            hasSourceExpression(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Negated checks: if (!ptr)
        unaryOperator(hasOperatorName("!"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))))
    )).bind("nullCheck");

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Register matchers for allocation, pointer use, and null checks
  Finder->addMatcher(
      traverse(TK_AsIs, PointerVarFromAllocMatcher),
      this);
  
  Finder->addMatcher(
      traverse(TK_AsIs, PointerUseMatcher),
      this);
  
  Finder->addMatcher(
      traverse(TK_AsIs, NullCheckMatcher),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Track allocations, uses, and checks per variable
  static std::map<const VarDecl*, std::vector<SourceLocation>> Allocations;
  static std::map<const VarDecl*, std::vector<SourceLocation>> Uses;
  static std::map<const VarDecl*, std::vector<SourceLocation>> Checks;
  static llvm::SmallPtrSet<const VarDecl*, 16> ReportedVars;
  
  // Check if this is an allocation expression
  const Stmt *AllocExpr = Result.Nodes.getNodeAs<Stmt>("allocExpr");
  const VarDecl *PtrVar = nullptr;
  const VarDecl *PtrVarDecl = Result.Nodes.getNodeAs<VarDecl>("ptrVarDecl");
  
  if (AllocExpr && AllocExpr->getBeginLoc().isValid()) {
    // Get the pointer variable from the allocation
    if (PtrVarDecl && PtrVarDecl->getLocation().isValid()) {
      PtrVar = PtrVarDecl;
    } else {
      PtrVar = Result.Nodes.getNodeAs<VarDecl>("ptrVar");
    }
    
    if (!PtrVar || !PtrVar->getLocation().isValid()) return;
    
    // Store allocation location for this variable
    Allocations[PtrVar].push_back(AllocExpr->getBeginLoc());
  }
  
  // Check if this is a pointer usage
  const Expr *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
  const VarDecl *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  
  if (PointerUse && PointerUse->getBeginLoc().isValid() && 
      UseVar && UseVar->getLocation().isValid()) {
    // Store use location for this variable
    Uses[UseVar].push_back(PointerUse->getBeginLoc());
  }
  
  // Check if this is a null check
  const Stmt *NullCheck = Result.Nodes.getNodeAs<Stmt>("nullCheck");
  const VarDecl *CheckVar = Result.Nodes.getNodeAs<VarDecl>("checkVar");
  
  if (NullCheck && NullCheck->getBeginLoc().isValid() &&
      CheckVar && CheckVar->getLocation().isValid()) {
    // Store check location for this variable
    Checks[CheckVar].push_back(NullCheck->getBeginLoc());
  }
  
  // Process all variables that have both allocations and uses
  for (auto &VarUsePair : Uses) {
    const VarDecl *Var = VarUsePair.first;
    if (ReportedVars.count(Var)) continue; // Already reported
    
    auto AllocIt = Allocations.find(Var);
    if (AllocIt == Allocations.end()) continue; // No allocation for this variable
    
    // For each use, check if there's a null check after the most recent allocation
    for (SourceLocation UseLoc : VarUsePair.second) {
      // Find the most recent allocation before this use
      SourceLocation LastAllocLoc;
      for (SourceLocation AllocLoc : AllocIt->second) {
        if (SM.isBeforeInTranslationUnit(AllocLoc, UseLoc)) {
          if (LastAllocLoc.isInvalid() || 
              SM.isBeforeInTranslationUnit(LastAllocLoc, AllocLoc)) {
            LastAllocLoc = AllocLoc;
          }
        }
      }
      
      if (LastAllocLoc.isInvalid()) continue; // No allocation before this use
      
      // Check if there's a null check between the allocation and use
      bool FoundNullCheck = false;
      auto CheckIt = Checks.find(Var);
      if (CheckIt != Checks.end()) {
        for (SourceLocation CheckLoc : CheckIt->second) {
          if (SM.isBeforeInTranslationUnit(LastAllocLoc, CheckLoc) &&
              SM.isBeforeInTranslationUnit(CheckLoc, UseLoc)) {
            FoundNullCheck = true;
            break;
          }
        }
      }
      
      // Also check for null checks in the same statement (e.g., if (ptr && ptr->field))
      if (!FoundNullCheck) {
        // Get the parent statement of the use
        auto Parents = Context->getParents(*PointerUse);
        while (!Parents.empty()) {
          if (const Stmt *Parent = Parents[0].get<Stmt>()) {
            // Check if parent is an IfStmt and the use is in the then branch
            if (const auto *If = dyn_cast<IfStmt>(Parent)) {
              const Stmt *Then = If->getThen();
              if (Then && isDescendant(PointerUse, Then, Context)) {
                // Check if the condition contains a null check for our variable
                const Expr *Cond = If->getCond()->IgnoreParenImpCasts();
                
                std::function<bool(const Expr*)> containsNullCheck = [&](const Expr *E) -> bool {
                  if (!E) return false;
                  
                  // Check for explicit comparison
                  if (const auto *BinOp = dyn_cast<BinaryOperator>(E)) {
                    if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
                      const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
                      const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
                      
                      const DeclRefExpr *VarDRE = nullptr;
                      if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
                        if (DRE->getDecl() == Var) VarDRE = DRE;
                      } else if (const auto *DRE = dyn_cast<DeclRefExpr>(RHS)) {
                        if (DRE->getDecl() == Var) VarDRE = DRE;
                      }
                      
                      if (VarDRE) {
                        const Expr *OtherSide = (VarDRE == dyn_cast<DeclRefExpr>(LHS)) ? 
                                                 RHS : LHS;
                        if (OtherSide->isNullPointerConstant(*Context, 
                                                             Expr::NPC_ValueDependentIsNull)) {
                          return true;
                        }
                      }
                    }
                  }
                  
                  // Check for implicit check
                  if (const auto *DRE = dyn_cast<DeclRefExpr>(E)) {
                    if (DRE->getDecl() == Var) {
                      // Check if it's in a cast to boolean context
                      auto DREParents = Context->getParents(*DRE);
                      while (!DREParents.empty()) {
                        if (const auto *ICE = DREParents[0].get<ImplicitCastExpr>()) {
                          if (ICE->getCastKind() == CK_PointerToBoolean ||
                              ICE->getCastKind() == CK_IntegralToBoolean) {
                            return true;
                          }
                        }
                        DREParents = Context->getParents(DREParents[0]);
                      }
                    }
                  }
                  
                  // Check for negated check
                  if (const auto *UnaryOp = dyn_cast<UnaryOperator>(E)) {
                    if (UnaryOp->getOpcode() == UO_LNot) {
                      return containsNullCheck(UnaryOp->getSubExpr()->IgnoreParenImpCasts());
                    }
                  }
                  
                  // Check for logical AND/OR
                  if (const auto *BinOp = dyn_cast<BinaryOperator>(E)) {
                    if (BinOp->getOpcode() == BO_LAnd || BinOp->getOpcode() == BO_LOr) {
                      return containsNullCheck(BinOp->getLHS()->IgnoreParenImpCasts()) ||
                             containsNullCheck(BinOp->getRHS()->IgnoreParenImpCasts());
                    }
                  }
                  
                  // Recursively check children
                  for (const Stmt *Child : E->children()) {
                    if (const Expr *ChildExpr = dyn_cast_or_null<Expr>(Child)) {
                      if (containsNullCheck(ChildExpr)) return true;
                    }
                  }
                  
                  return false;
                };
                
                if (containsNullCheck(Cond)) {
                  FoundNullCheck = true;
                  break;
                }
              }
            }
          }
          Parents = Context->getParents(Parents[0]);
        }
      }
      
      // If no null check found, emit diagnostic
      if (!FoundNullCheck) {
        // Get the pointer use expression for the diagnostic
        const Expr *UseExpr = nullptr;
        for (auto &VarUsePair2 : Uses) {
          if (VarUsePair2.first == Var) {
            // Find the use at this location
            for (SourceLocation Loc : VarUsePair2.second) {
              if (Loc == UseLoc) {
                // We need to find the actual expression - for simplicity, use the first one
                UseExpr = PointerUse;
                break;
              }
            }
            if (UseExpr) break;
          }
        }
        
        if (UseExpr && UseExpr->getBeginLoc().isValid()) {
          diag(UseExpr->getBeginLoc(), 
               "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
              << UseExpr->getSourceRange();
          ReportedVars.insert(Var);
          break; // Only report once per variable
        }
      }
    }
  }
}

} // namespace clang::tidy::ucassaat