//===--- MisuseCompareExprCheck.cpp - clang-tidy --------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "MisuseCompareExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to check if an expression is already wrapped in parentheses
static bool isWrappedInParens(const Expr *E, const MatchFinder::MatchResult &Result) {
  if (!E || !E->getBeginLoc().isValid() || !E->getEndLoc().isValid())
    return false;
  
  // Get the immediate parent expression
  auto Parents = Result.Context->getParents(*E);
  if (Parents.size() == 1) {
    if (const auto *Paren = Parents[0].get<ParenExpr>()) {
      // Check if the parentheses directly wrap this expression
      if (Paren->getSubExpr()->IgnoreParenImpCasts() == E->IgnoreParenImpCasts()) {
        return true;
      }
    }
  }
  
  return false;
}

void MisuseCompareExprCheck::registerMatchers(MatchFinder *Finder) {
  // Matcher for comparison operators with inner arithmetic/bitwise operators
  auto ComparisonWithInnerOp = binaryOperator(
    anyOf(
      hasOperatorName("=="),
      hasOperatorName("!="),
      hasOperatorName("<"),
      hasOperatorName(">"),
      hasOperatorName("<="),
      hasOperatorName(">=")
    ),
    anyOf(
      // Check left operand
      hasLHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("+"),
            hasOperatorName("-"),
            hasOperatorName("*"),
            hasOperatorName("/"),
            hasOperatorName("%"),
            hasOperatorName("&"),
            hasOperatorName("|"),
            hasOperatorName("^"),
            hasOperatorName("<<"),
            hasOperatorName(">>")
          )
        ).bind("innerOp")
      )),
      // Check right operand
      hasRHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("+"),
            hasOperatorName("-"),
            hasOperatorName("*"),
            hasOperatorName("/"),
            hasOperatorName("%"),
            hasOperatorName("&"),
            hasOperatorName("|"),
            hasOperatorName("^"),
            hasOperatorName("<<"),
            hasOperatorName(">>")
          )
        ).bind("innerOp")
      ))
    )
  ).bind("comparison");
  
  // Matcher for arithmetic/bitwise operators with inner comparison operators
  auto ArithmeticWithInnerCmp = binaryOperator(
    anyOf(
      hasOperatorName("+"),
      hasOperatorName("-"),
      hasOperatorName("*"),
      hasOperatorName("/"),
      hasOperatorName("%"),
      hasOperatorName("&"),
      hasOperatorName("|"),
      hasOperatorName("^"),
      hasOperatorName("<<"),
      hasOperatorName(">>")
    ),
    anyOf(
      // Check left operand
      hasLHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("=="),
            hasOperatorName("!="),
            hasOperatorName("<"),
            hasOperatorName(">"),
            hasOperatorName("<="),
            hasOperatorName(">=")
          )
        ).bind("innerCmp")
      )),
      // Check right operand
      hasRHS(ignoringParenImpCasts(
        binaryOperator(
          anyOf(
            hasOperatorName("=="),
            hasOperatorName("!="),
            hasOperatorName("<"),
            hasOperatorName(">"),
            hasOperatorName("<="),
            hasOperatorName(">=")
          )
        ).bind("innerCmp")
      ))
    )
  ).bind("outerOp");
  
  // Combine both patterns
  Finder->addMatcher(
    binaryOperator(
      anyOf(ComparisonWithInnerOp, ArithmeticWithInnerCmp)
    ),
    this
  );
}

void MisuseCompareExprCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Ctx = Result.Context;
  
  // Check for first pattern: comparison with inner arithmetic/bitwise operator
  if (const auto *InnerOp = Result.Nodes.getNodeAs<BinaryOperator>("innerOp")) {
    if (!InnerOp || !InnerOp->getOperatorLoc().isValid())
      return;
    
    // Skip if already wrapped in parentheses
    if (isWrappedInParens(InnerOp, Result))
      return;
    
    const auto *Comparison = Result.Nodes.getNodeAs<BinaryOperator>("comparison");
    if (!Comparison || !Comparison->getOperatorLoc().isValid())
      return;
    
    // Check if the inner operator is directly inside the comparison without parentheses
    // We need to verify that the inner operator is indeed a direct child of the comparison
    // after ignoring parentheses and implicit casts
    bool IsDirectChild = false;
    if (Comparison->getLHS()->IgnoreParenImpCasts() == InnerOp ||
        Comparison->getRHS()->IgnoreParenImpCasts() == InnerOp) {
      IsDirectChild = true;
    }
    
    if (!IsDirectChild)
      return;
    
    // Construct diagnostic message
    diag(InnerOp->getOperatorLoc(),
         "禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]")
        << FixItHint::CreateInsertion(InnerOp->getBeginLoc(), "(")
        << FixItHint::CreateInsertion(
             Lexer::getLocForEndOfToken(InnerOp->getEndLoc(), 0, 
                                       *Result.SourceManager, Ctx->getLangOpts()),
             ")");
    return;
  }
  
  // Check for second pattern: arithmetic/bitwise with inner comparison operator
  if (const auto *InnerCmp = Result.Nodes.getNodeAs<BinaryOperator>("innerCmp")) {
    if (!InnerCmp || !InnerCmp->getOperatorLoc().isValid())
      return;
    
    // Skip if already wrapped in parentheses
    if (isWrappedInParens(InnerCmp, Result))
      return;
    
    const auto *OuterOp = Result.Nodes.getNodeAs<BinaryOperator>("outerOp");
    if (!OuterOp || !OuterOp->getOperatorLoc().isValid())
      return;
    
    // Check if the inner comparison is directly inside the outer operator without parentheses
    // We need to verify that the inner comparison is indeed a direct child of the outer operator
    // after ignoring parentheses and implicit casts
    bool IsDirectChild = false;
    if (OuterOp->getLHS()->IgnoreParenImpCasts() == InnerCmp ||
        OuterOp->getRHS()->IgnoreParenImpCasts() == InnerCmp) {
      IsDirectChild = true;
    }
    
    if (!IsDirectChild)
      return;
    
    // Construct diagnostic message
    diag(InnerCmp->getOperatorLoc(),
         "禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]")
        << FixItHint::CreateInsertion(InnerCmp->getBeginLoc(), "(")
        << FixItHint::CreateInsertion(
             Lexer::getLocForEndOfToken(InnerCmp->getEndLoc(), 0, 
                                       *Result.SourceManager, Ctx->getLangOpts()),
             ")");
    return;
  }
}

} // namespace clang::tidy::ucassaat