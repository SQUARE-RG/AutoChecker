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
  
  SourceRange ExprRange = E->getSourceRange();
  // Get the character range of the expression
  CharSourceRange CharRange = Lexer::getAsCharRange(
      CharSourceRange::getTokenRange(ExprRange),
      *Result.SourceManager, Result.Context->getLangOpts());
  
  if (!CharRange.isValid())
    return false;
  
  // Check if the expression starts with '(' and ends with ')'
  StringRef Text = Lexer::getSourceText(CharRange, *Result.SourceManager, 
                                        Result.Context->getLangOpts());
  return Text.startswith("(") && Text.endswith(")");
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
    )
  ).bind("comparison")
   .with(anyOf(
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
   ));
  
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
    )
  ).bind("outerOp")
   .with(anyOf(
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
   ));
  
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
    
    // Construct diagnostic message
    std::string InnerOpName = std::string(InnerOp->getOpcodeStr());
    std::string OuterOpName = std::string(Comparison->getOpcodeStr());
    
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
    
    // Construct diagnostic message
    std::string InnerOpName = std::string(InnerCmp->getOpcodeStr());
    std::string OuterOpName = std::string(OuterOp->getOpcodeStr());
    
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