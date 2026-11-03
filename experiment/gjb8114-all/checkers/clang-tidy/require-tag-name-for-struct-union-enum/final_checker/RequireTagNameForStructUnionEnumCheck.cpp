//===--- RequireTagNameForStructUnionEnumCheck.cpp - clang-tidy -----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "RequireTagNameForStructUnionEnumCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/Decl.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void RequireTagNameForStructUnionEnumCheck::registerMatchers(
    MatchFinder *Finder) {
  Finder->addMatcher(
      recordDecl(isDefinition(), unless(isImplicit())).bind("record"), this);
  Finder->addMatcher(
      enumDecl(isDefinition(), unless(isImplicit())).bind("enum"), this);
}

void RequireTagNameForStructUnionEnumCheck::check(
    const MatchFinder::MatchResult &Result) {
  if (const auto *Record = Result.Nodes.getNodeAs<RecordDecl>("record")) {
    if ((Record->isStruct() || Record->isUnion()) &&
        Record->getIdentifier() == nullptr) {
      diag(Record->getLocation(),
           "struct or union definition must declare an identifier name");
    }
  }

  if (const auto *Enum = Result.Nodes.getNodeAs<EnumDecl>("enum")) {
    if (Enum->getIdentifier() == nullptr) {
      diag(Enum->getLocation(),
           "enum definition must declare an identifier name");
    }
  }
}

} // namespace clang::tidy::ucassaat