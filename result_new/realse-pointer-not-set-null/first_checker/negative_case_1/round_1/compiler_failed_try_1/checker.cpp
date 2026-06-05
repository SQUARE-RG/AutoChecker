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

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  // Match free() calls
  Finder->addMatcher(
    callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );

  // Match delete expressions
  Finder->addMatcher(
    cxxDeleteExpr(
      has(expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );

  // Match delete[] expressions
  Finder->addMatcher(
    cxxDeleteExpr(
      isArray(),
      has(expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );
}

void RealsePointerNotSetNullCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *DeallocCall = Result.Nodes.getNodeAs<Expr>("deallocation_call");
  const auto *FreedPointer = Result.Nodes.getNodeAs<Expr>("freed_pointer");
  const auto *ParentBlock = Result.Nodes.getNodeAs<CompoundStmt>("parent_block");

  if (!DeallocCall || !FreedPointer || !ParentBlock)
    return;

  // Get the source location of the deallocation call
  SourceLocation DeallocLoc = DeallocCall->getBeginLoc();
  if (DeallocLoc.isInvalid())
    return;

  // Check if the freed pointer is an lvalue (e.g., a DeclRefExpr)
  const auto *FreedDeclRef = dyn_cast<DeclRefExpr>(FreedPointer->IgnoreImpCasts());
  if (!FreedDeclRef)
    return;

  const ValueDecl *FreedVarDecl = FreedDeclRef->getDecl();
  if (!FreedVarDecl)
    return;

  // Look for a null assignment after the deallocation call in the same block
  bool FoundNullAssignment = false;
  
  // Find the parent statement of the deallocation call within the block
  const Stmt *DeallocParent = nullptr;
  for (const auto *Child : ParentBlock->children()) {
    if (Child == DeallocCall) {
      DeallocParent = Child;
      break;
    }
    // Check if deallocation is inside a child expression
    if (const auto *ChildStmt = dyn_cast<Stmt>(Child)) {
      if (ChildStmt == DeallocCall) {
        DeallocParent = ChildStmt;
        break;
      }
    }
  }

  // Iterate through statements in the block after the deallocation
  bool FoundDealloc = false;
  for (const auto *Child : ParentBlock->children()) {
    if (!FoundDealloc) {
      if (const auto *ChildStmt = dyn_cast<Stmt>(Child)) {
        if (ChildStmt == DeallocCall) {
          FoundDealloc = true;
        }
      }
      continue;
    }

    // Check if this child is a binary assignment to the freed pointer with null
    if (const auto *BinOp = dyn_cast<BinaryOperator>(Child)) {
      if (BinOp->isAssignmentOp()) {
        const Expr *LHS = BinOp->getLHS()->IgnoreImpCasts();
        if (const auto *LHSDeclRef = dyn_cast<DeclRefExpr>(LHS)) {
          if (LHSDeclRef->getDecl() == FreedVarDecl) {
            const Expr *RHS = BinOp->getRHS()->IgnoreImpCasts();
            if (RHS->isNullPointerConstant(*Result.Context, Expr::NPC_ValueDependentIsNull)) {
              FoundNullAssignment = true;
              break;
            }
          }
        }
      }
    }
  }

  if (!FoundNullAssignment) {
    diag(DeallocLoc, "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]");
  }
}

} // namespace clang::tidy::ucassaat