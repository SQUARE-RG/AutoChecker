//===--- ReadabilityRedundantDeclarationCheck.cpp - clang-tidy ------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ReadabilityRedundantDeclarationCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ReadabilityRedundantDeclarationCheck::registerMatchers(MatchFinder *Finder) {
  // Match all variable declarations with external linkage that are not definitions
  Finder->addMatcher(
      varDecl(hasExternalFormalLinkage(), unless(isDefinition()))
          .bind("decl"),
      this);
}

void ReadabilityRedundantDeclarationCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *MatchedDecl = Result.Nodes.getNodeAs<VarDecl>("decl");
  if (!MatchedDecl || !MatchedDecl->isValidDecl())
    return;

  // Get the declaration name
  const IdentifierInfo *NameInfo = MatchedDecl->getIdentifier();
  if (!NameInfo)
    return;

  StringRef Name = NameInfo->getName();

  // Get the declaration context
  const DeclContext *Context = MatchedDecl->getDeclContext();
  if (!Context)
    return;

  // Find all declarations with the same name in the same context
  SmallVector<const VarDecl *, 4> Declarations;
  for (const auto *Decl : Context->decls()) {
    const auto *Var = dyn_cast<VarDecl>(Decl);
    if (!Var || !Var->isValidDecl())
      continue;

    // Check if it's the same variable name
    const IdentifierInfo *OtherNameInfo = Var->getIdentifier();
    if (!OtherNameInfo || OtherNameInfo->getName() != Name)
      continue;

    // Check if it has external linkage and is not a definition
    if (!Var->hasExternalFormalLinkage() || Var->isThisDeclarationADefinition())
      continue;

    Declarations.push_back(Var);
  }

  // If there are multiple declarations, emit diagnostics for redundant ones
  if (Declarations.size() > 1) {
    // Sort by source location to identify the first declaration
    llvm::sort(Declarations, [](const VarDecl *A, const VarDecl *B) {
      return A->getLocation() < B->getLocation();
    });

    // The first declaration is the original one, others are redundant
    for (size_t i = 1; i < Declarations.size(); ++i) {
      const auto *RedundantDecl = Declarations[i];
      if (RedundantDecl == MatchedDecl) {
        diag(RedundantDecl->getLocation(),
             "redundant '%0' declaration")
            << Name;
      }
    }
  }
}

} // namespace clang::tidy::ucassaat