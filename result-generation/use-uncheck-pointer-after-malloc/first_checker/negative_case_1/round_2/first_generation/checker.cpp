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

// Helper matcher to find the pointer variable from allocation
const auto PointerVarFromAllocMatcher = expr(
    anyOf(
        // Direct assignment: p = malloc()
        binaryOperator(hasOperatorName("="),
            hasLHS(declRefExpr(to(varDecl().bind("ptrVar")))),
            hasRHS(anyOf(
                AllocCallMatcher,
                castExpr(hasSourceExpression(AllocCallMatcher))))),
        // Variable declaration with initialization: int *p = malloc()
        varDecl(hasInitializer(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))).bind("ptrVarDecl")
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
  // Match allocation expressions and pointer uses in the same function
  Finder->addMatcher(
      traverse(TK_AsIs,
          stmt(anyOf(
              // Find allocation first
              PointerVarFromAllocMatcher,
              // Then find uses that might be unchecked
              PointerUseMatcher
          )).bind("stmtNode")),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Get the current statement node
  const Stmt *StmtNode = Result.Nodes.getNodeAs<Stmt>("stmtNode");
  if (!StmtNode || !StmtNode->getBeginLoc().isValid()) return;
  
  // Get the function containing this statement
  const DeclContext *DC = Context->getEnclosingDeclContext(StmtNode);
  const FunctionDecl *Func = dyn_cast_or_null<FunctionDecl>(DC);
  if (!Func || !Func->hasBody()) return;
  
  const Stmt *FuncBody = Func->getBody();
  if (!FuncBody) return;
  
  // Check if this is an allocation expression
  const Expr *AllocExpr = Result.Nodes.getNodeAs<Expr>("allocExpr");
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
    
    // Store allocation information for this variable
    // We'll track allocations and their locations
    // This is a simplified approach - in a real checker, you'd want to
    // maintain state across multiple matches
  }
  
  // Check if this is a pointer usage
  const Expr *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
  const VarDecl *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  
  if (PointerUse && PointerUse->getBeginLoc().isValid() && 
      UseVar && UseVar->getLocation().isValid()) {
    
    // Find the most recent allocation for this variable before the use
    SourceLocation LastAllocLoc;
    bool IsRealloc = false;
    
    // Traverse the function body to find allocations of this variable
    std::function<void(const Stmt *)> findAllocations = [&](const Stmt *S) {
      if (!S) return;
      
      // Check if this is an allocation of our variable
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_Assign) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) {
              const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
              // Check if RHS is a call to allocation function
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(RHS)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(RHS);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(), 
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      // Check variable declarations with initializers
      if (const auto *DS = dyn_cast<DeclStmt>(S)) {
        for (const Decl *D : DS->decls()) {
          if (const auto *VD = dyn_cast<VarDecl>(D)) {
            if (VD == UseVar && VD->hasInit()) {
              const Expr *Init = VD->getInit()->IgnoreParenImpCasts();
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(Init)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(Init);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findAllocations(Child);
      }
    };
    
    findAllocations(FuncBody);
    
    // If no allocation found before this use, it's not from dynamic allocation
    if (LastAllocLoc.isInvalid()) return;
    
    // Now check if there's a null check between the allocation and the use
    bool FoundNullCheck = false;
    
    std::function<void(const Stmt *)> findNullChecks = [&](const Stmt *S) {
      if (!S || FoundNullCheck) return;
      
      // Check binary operators for explicit null comparisons
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
          
          // Check if one side is our variable
          const DeclRefExpr *VarDRE = nullptr;
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          } else if (const auto *DRE = dyn_cast<DeclRefExpr>(RHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          }
          
          if (VarDRE) {
            // Check if the other side is a null pointer constant
            const Expr *OtherSide = (VarDRE == dyn_cast<DeclRefExpr>(LHS)) ? RHS : LHS;
            if (OtherSide->isNullPointerConstant(*Context, 
                                                 Expr::NPC_ValueDependentIsNull)) {
              // Check if this null check is between allocation and use
              if (SM.isBeforeInTranslationUnit(LastAllocLoc, BinOp->getBeginLoc()) &&
                  SM.isBeforeInTranslationUnit(BinOp->getBeginLoc(), 
                                               PointerUse->getBeginLoc())) {
                FoundNullCheck = true;
                return;
              }
            }
          }
        }
      }
      
      // Check for implicit checks (if (ptr), while (ptr))
      if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
        if (DRE->getDecl() == UseVar) {
          // Check if parent is an implicit cast to boolean
          const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("");
          if (Parent) {
            if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Parent)) {
              if (ICE->getCastKind() == CK_PointerToBoolean ||
                  ICE->getCastKind() == CK_IntegralToBoolean) {
                // Check if this is in a condition context
                const Stmt *GrandParent = Result.Nodes.getNodeAs<Stmt>("");
                if (GrandParent) {
                  if (isa<IfStmt>(GrandParent) || isa<WhileStmt>(GrandParent) ||
                      isa<DoStmt>(GrandParent) || isa<ForStmt>(GrandParent) ||
                      isa<ConditionalOperator>(GrandParent)) {
                    if (SM.isBeforeInTranslationUnit(LastAllocLoc, 
                                                     ICE->getBeginLoc()) &&
                        SM.isBeforeInTranslationUnit(ICE->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      FoundNullCheck = true;
                      return;
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      // Check for negated checks (if (!ptr))
      if (const auto *UnaryOp = dyn_cast<UnaryOperator>(S)) {
        if (UnaryOp->getOpcode() == UO_LNot) {
          const Expr *SubExpr = UnaryOp->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
            if (DRE->getDecl() == UseVar) {
              // Check if this is in a condition context
              const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("");
              if (Parent) {
                if (isa<IfStmt>(Parent) || isa<WhileStmt>(Parent) ||
                    isa<DoStmt>(Parent) || isa<ForStmt>(Parent) ||
                    isa<ConditionalOperator>(Parent)) {
                  if (SM.isBeforeInTranslationUnit(LastAllocLoc,
                                                   UnaryOp->getBeginLoc()) &&
                      SM.isBeforeInTranslationUnit(UnaryOp->getBeginLoc(),
                                                   PointerUse->getBeginLoc())) {
                    FoundNullCheck = true;
                    return;
                  }
                }
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findNullChecks(Child);
      }
    };
    
    findNullChecks(FuncBody);
    
    // If no null check found, emit diagnostic
    if (!FoundNullCheck) {
      diag(PointerUse->getBeginLoc(), 
           "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
          << PointerUse->getSourceRange();
    }
  }
}

} // namespace clang::tidy::ucassaat