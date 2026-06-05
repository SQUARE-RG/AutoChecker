//===--- DeclareAnonymousStructCheck.cpp - clang-tidy ---------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DeclareAnonymousStructCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void DeclareAnonymousStructCheck::registerMatchers(MatchFinder *Finder) {
  Finder->addMatcher(
      recordDecl(
          ast_matchers::isAnonymousStructOrUnion(),
          hasAncestor(recordDecl(isStruct(), isDefinition()))
      ).bind("anonymousRecord"),
      this);
}

void DeclareAnonymousStructCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *MatchedRecord = Result.Nodes.getNodeAs<RecordDecl>("anonymousRecord");
  if (!MatchedRecord)
    return;

  diag(MatchedRecord->getLocation(), "禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]");
}

} // namespace clang::tidy::ucassaat