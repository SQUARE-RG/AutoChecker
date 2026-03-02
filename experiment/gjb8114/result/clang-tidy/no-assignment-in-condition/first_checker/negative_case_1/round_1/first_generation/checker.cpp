//===--- NoAssignmentInConditionCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoAssignmentInConditionCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoAssignmentInConditionCheck::registerMatchers(MatchFinder *Finder) {
  // Matcher for assignment operators
  auto AssignmentMatcher = binaryOperator(
      isAssignmentOperator(),
      unless(hasParent(binaryOperator(isComparisonOperator()))))
      .bind("assign_in_cond");

  // Matcher for logical operators (&&, ||) that contain assignments
  auto LogicalOpWithAssignmentMatcher = binaryOperator(
      anyOf(hasOperatorName("&&"), hasOperatorName("||")),
      anyOf(hasLHS(AssignmentMatcher), hasRHS(AssignmentMatcher)))
      .bind("logical_op");

  // Matcher for control flow statements that contain assignments in conditions
  auto ControlFlowWithAssignmentMatcher = stmt(
      anyOf(
          ifStmt(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("if"),
          whileStmt(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("while"),
          doStmt(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("do"),
          forStmt(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("for"),
          conditionalOperator(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("conditional"),
          binaryConditionalOperator(hasCondition(expr(hasDescendant(AssignmentMatcher))))
              .bind("binary_conditional")));

  // Add all matchers
  Finder->addMatcher(LogicalOpWithAssignmentMatcher, this);
  Finder->addMatcher(ControlFlowWithAssignmentMatcher, this);
}

void NoAssignmentInConditionCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Assignment = Result.Nodes.getNodeAs<BinaryOperator>("assign_in_cond");
  if (!Assignment || !Assignment->getOperatorLoc().isValid())
    return;

  // Determine the context for the diagnostic message
  llvm::StringRef ContextType;
  const Stmt *ContextStmt = nullptr;

  if (const auto *If = Result.Nodes.getNodeAs<IfStmt>("if")) {
    ContextType = "if condition";
    ContextStmt = If;
  } else if (const auto *While = Result.Nodes.getNodeAs<WhileStmt>("while")) {
    ContextType = "while condition";
    ContextStmt = While;
  } else if (const auto *Do = Result.Nodes.getNodeAs<DoStmt>("do")) {
    ContextType = "do-while condition";
    ContextStmt = Do;
  } else if (const auto *For = Result.Nodes.getNodeAs<ForStmt>("for")) {
    ContextType = "for condition";
    ContextStmt = For;
  } else if (const auto *Cond = Result.Nodes.getNodeAs<ConditionalOperator>("conditional")) {
    ContextType = "conditional operator";
    ContextStmt = Cond;
  } else if (const auto *BinCond = Result.Nodes.getNodeAs<BinaryConditionalOperator>("binary_conditional")) {
    ContextType = "binary conditional operator";
    ContextStmt = BinCond;
  } else if (const auto *LogicalOp = Result.Nodes.getNodeAs<BinaryOperator>("logical_op")) {
    ContextType = "logical expression";
    ContextStmt = LogicalOp;
  }

  if (ContextType.empty() || !ContextStmt)
    return;

  // Emit diagnostic
  diag(Assignment->getOperatorLoc(),
       "禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]")
      << Assignment->getSourceRange();
  diag(ContextStmt->getBeginLoc(),
       "assignment inside " + ContextType.str() + " is prohibited",
       DiagnosticIDs::Note);
}

} // namespace clang::tidy::ucassaat