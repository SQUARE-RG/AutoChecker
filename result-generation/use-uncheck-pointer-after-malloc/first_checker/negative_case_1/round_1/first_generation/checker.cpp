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

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Matcher for dynamic memory allocation functions
const auto AllocFuncMatcher = functionDecl(
    hasAnyName("::malloc", "::calloc", "::realloc", "std::malloc", 
               "std::calloc", "std::realloc"));

// Matcher for allocation calls
const auto AllocCallMatcher = callExpr(
    callee(AllocFuncMatcher),
    unless(hasAncestor(callExpr()))).bind("allocCall");

// Matcher for pointer variable declaration or assignment from allocation
const auto AllocVarMatcher = varDecl(
    hasInitializer(anyOf(
        AllocCallMatcher,
        castExpr(hasSourceExpression(AllocCallMatcher)),
        binaryOperator(hasOperatorName("="),
                       hasRHS(anyOf(
                           AllocCallMatcher,
                           castExpr(hasSourceExpression(AllocCallMatcher))))))))
    .bind("allocVar");

// Matcher for assignment of allocation result to existing pointer
const auto AllocAssignMatcher = binaryOperator(
    hasOperatorName("="),
    hasLHS(declRefExpr(to(varDecl().bind("assignVar")))),
    hasRHS(anyOf(
        AllocCallMatcher,
        castExpr(hasSourceExpression(AllocCallMatcher)))))
    .bind("allocAssign");

// Matcher for pointer usage (dereference, array subscript, etc.)
const auto PointerUseMatcher = expr(
    anyOf(
        unaryOperator(hasOperatorName("*"), 
                      hasUnaryOperand(ignoringParenImpCasts(
                          declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))),
        arraySubscriptExpr(
            hasBase(ignoringParenImpCasts(
                declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))),
        memberExpr(hasObjectExpression(ignoringParenImpCasts(
            declRefExpr(to(varDecl(equalsBoundNode("allocVar")))))))))
    .bind("pointerUse");

// Matcher for null pointer checks
const auto NullCheckMatcher = stmt(
    anyOf(
        // Explicit comparisons: ptr == NULL, ptr != NULL
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl(equalsBoundNode("allocVar")))))),
            hasRHS(nullPointerConstant())),
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(nullPointerConstant()),
            hasRHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))),
        // Implicit checks: if (ptr), if (!ptr)
        implicitCastExpr(hasImplicitDestinationType(booleanType()),
            hasSourceExpression(ignoringParenImpCasts(
                declRefExpr(to(varDecl(equalsBoundNode("allocVar"))))))),
        unaryOperator(hasOperatorName("!"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl(equalsBoundNode("allocVar")))))))))
    .bind("nullCheck");

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Match allocation to variable declaration
  Finder->addMatcher(
      traverse(TK_AsIs,
          declStmt(
              hasSingleDecl(AllocVarMatcher),
              forEachDescendant(PointerUseMatcher))),
      this);
  
  // Match assignment of allocation result
  Finder->addMatcher(
      traverse(TK_AsIs,
          AllocAssignMatcher),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Handle allocation in variable declaration
  if (const auto *AllocVar = Result.Nodes.getNodeAs<VarDecl>("allocVar")) {
    if (!AllocVar || !AllocVar->getLocation().isValid()) return;
    
    const auto *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
    if (!PointerUse || !PointerUse->getBeginLoc().isValid()) return;
    
    // Check if there's a null check before this usage
    bool foundCheck = false;
    
    // Traverse from allocation to usage to find null checks
    const Stmt *Body = nullptr;
    if (const DeclContext *DC = AllocVar->getDeclContext()) {
      if (const FunctionDecl *FD = dyn_cast<FunctionDecl>(DC)) {
        Body = FD->getBody();
      }
    }
    
    if (Body) {
      // Simple traversal to find null checks between allocation and usage
      std::function<void(const Stmt *)> traverse = [&](const Stmt *S) {
        if (!S) return;
        
        // Check if this is a null check involving our variable
        if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
          if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
            // Check if it involves our variable and a null constant
            const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
            const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
            
            const DeclRefExpr *DRE = nullptr;
            if (const auto *D = dyn_cast<DeclRefExpr>(LHS)) {
              DRE = D;
            } else if (const auto *D = dyn_cast<DeclRefExpr>(RHS)) {
              DRE = D;
            }
            
            if (DRE && DRE->getDecl() == AllocVar) {
              // Check if other side is null
              if (RHS->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull) ||
                  LHS->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull)) {
                if (SM.isBeforeInTranslationUnit(BinOp->getBeginLoc(), 
                                                 PointerUse->getBeginLoc())) {
                  foundCheck = true;
                }
              }
            }
          }
        }
        // Also check for implicit checks: if (ptr), if (!ptr)
        else if (const auto *UnaryOp = dyn_cast<UnaryOperator>(S)) {
          if (UnaryOp->getOpcode() == UO_LNot) {
            const Expr *SubExpr = UnaryOp->getSubExpr()->IgnoreParenImpCasts();
            if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
              if (DRE->getDecl() == AllocVar) {
                if (SM.isBeforeInTranslationUnit(UnaryOp->getBeginLoc(),
                                                 PointerUse->getBeginLoc())) {
                  foundCheck = true;
                }
              }
            }
          }
        }
        else if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
          // Check for implicit conversion to bool in if/while conditions
          if (DRE->getDecl() == AllocVar) {
            // Check if parent is an implicit cast to bool
            if (const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("")) {
              if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Parent)) {
                if (ICE->getCastKind() == CK_PointerToBoolean) {
                  if (SM.isBeforeInTranslationUnit(ICE->getBeginLoc(),
                                                   PointerUse->getBeginLoc())) {
                    foundCheck = true;
                  }
                }
              }
            }
          }
        }
        
        // Recurse
        for (const Stmt *Child : S->children()) {
          traverse(Child);
        }
      };
      
      traverse(Body);
    }
    
    if (!foundCheck) {
      // Emit warning for unchecked usage
      diag(PointerUse->getBeginLoc(), 
           "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
          << FixItHint::CreateInsertion(PointerUse->getBeginLoc(), 
                                        "// Check pointer before use");
    }
  }
  
  // Handle assignment case (realloc, etc.)
  if (const auto *AssignVar = Result.Nodes.getNodeAs<VarDecl>("assignVar")) {
    if (!AssignVar || !AssignVar->getLocation().isValid()) return;
    
    const auto *AllocAssign = Result.Nodes.getNodeAs<BinaryOperator>("allocAssign");
    if (!AllocAssign || !AllocAssign->getBeginLoc().isValid()) return;
    
    // Find the next usage of this variable after assignment
    const Stmt *Body = nullptr;
    if (const DeclContext *DC = AssignVar->getDeclContext()) {
      if (const FunctionDecl *FD = dyn_cast<FunctionDecl>(DC)) {
        Body = FD->getBody();
      }
    }
    
    if (Body) {
      const Expr *FirstUseAfterAssign = nullptr;
      
      std::function<void(const Stmt *)> findUsage = [&](const Stmt *S) {
        if (!S) return;
        
        // Check if this is a usage of our variable
        if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
          if (DRE->getDecl() == AssignVar) {
            // Check if it's a usage (not the assignment itself)
            if (SM.isBeforeInTranslationUnit(AllocAssign->getEndLoc(),
                                             DRE->getBeginLoc())) {
              // Check parent to see if it's a real usage
              if (const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("")) {
                if (isa<UnaryOperator>(Parent) || 
                    isa<ArraySubscriptExpr>(Parent) ||
                    isa<MemberExpr>(Parent) ||
                    isa<CallExpr>(Parent)) {
                  if (!FirstUseAfterAssign || 
                      SM.isBeforeInTranslationUnit(DRE->getBeginLoc(),
                                                   FirstUseAfterAssign->getBeginLoc())) {
                    FirstUseAfterAssign = DRE;
                  }
                }
              }
            }
          }
        }
        
        for (const Stmt *Child : S->children()) {
          findUsage(Child);
        }
      };
      
      findUsage(Body);
      
      if (FirstUseAfterAssign) {
        // Check for null check between assignment and usage
        bool foundCheck = false;
        
        std::function<void(const Stmt *)> checkForNull = [&](const Stmt *S) {
          if (!S) return;
          
          if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
            if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
              const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
              const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
              
              const DeclRefExpr *DRE = nullptr;
              if (const auto *D = dyn_cast<DeclRefExpr>(LHS)) {
                DRE = D;
              } else if (const auto *D = dyn_cast<DeclRefExpr>(RHS)) {
                DRE = D;
              }
              
              if (DRE && DRE->getDecl() == AssignVar) {
                if (RHS->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull) ||
                    LHS->isNullPointerConstant(*Context, Expr::NPC_ValueDependentIsNotNull)) {
                  if (SM.isBeforeInTranslationUnit(AllocAssign->getEndLoc(),
                                                   BinOp->getBeginLoc()) &&
                      SM.isBeforeInTranslationUnit(BinOp->getBeginLoc(),
                                                   FirstUseAfterAssign->getBeginLoc())) {
                    foundCheck = true;
                  }
                }
              }
            }
          }
          
          for (const Stmt *Child : S->children()) {
            checkForNull(Child);
          }
        };
        
        checkForNull(Body);
        
        if (!foundCheck) {
          diag(FirstUseAfterAssign->getBeginLoc(),
               "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
              << FixItHint::CreateInsertion(FirstUseAfterAssign->getBeginLoc(),
                                            "// Check pointer before use");
        }
      }
    }
  }
}

} // namespace clang::tidy::ucassaat