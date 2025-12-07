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
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ReadabilityRedundantDeclarationCheck::registerMatchers(MatchFinder *Finder) {
  // Match all variable declarations that are not definitions
  // Only consider declarations at file or namespace scope
  Finder->addMatcher(
      varDecl(unless(isDefinition()),
              hasParent(decl(anyOf(translationUnitDecl(), namespaceDecl()))))
          .bind("varDecl"),
      this);
  
  // Match all function declarations that are not definitions
  // Exclude member functions (methods) and only consider file/namespace scope
  Finder->addMatcher(
      functionDecl(unless(isDefinition()),
                   unless(cxxMethodDecl()),
                   hasParent(decl(anyOf(translationUnitDecl(), namespaceDecl()))))
          .bind("funcDecl"),
      this);
}

void ReadabilityRedundantDeclarationCheck::check(const MatchFinder::MatchResult &Result) {
  // Handle variable declarations
  if (const auto *MatchedVarDecl = Result.Nodes.getNodeAs<VarDecl>("varDecl")) {
    if (!MatchedVarDecl || !MatchedVarDecl->getLocation().isValid())
      return;
    checkVarDecl(MatchedVarDecl, Result);
  }
  
  // Handle function declarations
  if (const auto *MatchedFuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("funcDecl")) {
    if (!MatchedFuncDecl || !MatchedFuncDecl->getLocation().isValid())
      return;
    checkFuncDecl(MatchedFuncDecl, Result);
  }
}

void ReadabilityRedundantDeclarationCheck::checkVarDecl(const VarDecl *MatchedDecl,
                                                        const MatchFinder::MatchResult &Result) {
  // Get the declaration name
  const IdentifierInfo *NameInfo = MatchedDecl->getIdentifier();
  if (!NameInfo)
    return;

  StringRef Name = NameInfo->getName();

  // Get the translation unit context to search all declarations
  const DeclContext *TUContext = MatchedDecl->getTranslationUnitDecl();
  if (!TUContext)
    return;

  // Find all declarations with the same name in the translation unit
  SmallVector<const VarDecl *, 4> Declarations;
  for (const auto *Decl : TUContext->decls()) {
    const auto *Var = dyn_cast<VarDecl>(Decl);
    if (!Var)
      continue;

    // Check if it's the same variable name
    const IdentifierInfo *OtherNameInfo = Var->getIdentifier();
    if (!OtherNameInfo || OtherNameInfo->getName() != Name)
      continue;

    // Check if it's not a definition
    if (Var->isThisDeclarationADefinition())
      continue;

    // Check if it's at file or namespace scope
    const DeclContext *VarContext = Var->getDeclContext();
    if (!isa<TranslationUnitDecl>(VarContext) && !isa<NamespaceDecl>(VarContext))
      continue;

    // Check if they have compatible storage classes
    // Both must be either static or non-static
    if (MatchedDecl->getStorageClass() != Var->getStorageClass())
      continue;

    // Check language linkage compatibility
    if (MatchedDecl->getLanguageLinkage() != Var->getLanguageLinkage())
      continue;

    // Check if they have compatible types using ASTContext::hasSameType
    if (!Result.Context->hasSameType(MatchedDecl->getType(), Var->getType()))
      continue;

    // Check if they have compatible inline specifiers
    if (MatchedDecl->isInlineSpecified() != Var->isInlineSpecified())
      continue;

    // Check if they are in the same namespace or translation unit
    const DeclContext *MatchedContext = MatchedDecl->getDeclContext();
    const DeclContext *VarDeclContext = Var->getDeclContext();
    
    // If both are in namespaces, check if they are the same namespace
    if (isa<NamespaceDecl>(MatchedContext) && isa<NamespaceDecl>(VarDeclContext)) {
      const auto *MatchedNS = cast<NamespaceDecl>(MatchedContext);
      const auto *VarNS = cast<NamespaceDecl>(VarDeclContext);
      if (MatchedNS->getOriginalNamespace() != VarNS->getOriginalNamespace())
        continue;
    } else if (MatchedContext != VarDeclContext) {
      // One is in translation unit, other is in namespace, or vice versa
      continue;
    }

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

void ReadabilityRedundantDeclarationCheck::checkFuncDecl(const FunctionDecl *MatchedDecl,
                                                         const MatchFinder::MatchResult &Result) {
  // Get the declaration name
  DeclarationName DeclName = MatchedDecl->getDeclName();
  if (!DeclName.isIdentifier())
    return;

  StringRef Name = DeclName.getAsString();

  // Get the translation unit context to search all declarations
  const DeclContext *TUContext = MatchedDecl->getTranslationUnitDecl();
  if (!TUContext)
    return;

  // Find all declarations with the same name in the translation unit
  SmallVector<const FunctionDecl *, 4> Declarations;
  for (const auto *Decl : TUContext->decls()) {
    const auto *Func = dyn_cast<FunctionDecl>(Decl);
    if (!Func)
      continue;

    // Check if it's the same function name
    if (Func->getDeclName() != DeclName)
      continue;

    // Check if it's not a definition
    if (Func->isThisDeclarationADefinition())
      continue;

    // Exclude member functions (methods)
    if (isa<CXXMethodDecl>(Func))
      continue;

    // Check if it's at file or namespace scope
    const DeclContext *FuncContext = Func->getDeclContext();
    if (!isa<TranslationUnitDecl>(FuncContext) && !isa<NamespaceDecl>(FuncContext))
      continue;

    // Check if they have compatible storage classes
    // Both must be either static or non-static
    if (MatchedDecl->getStorageClass() != Func->getStorageClass())
      continue;

    // Check language linkage compatibility
    if (MatchedDecl->getLanguageLinkage() != Func->getLanguageLinkage())
      continue;

    // Check if they have compatible types (return type and parameters)
    // using ASTContext::hasSameType
    if (!Result.Context->hasSameType(MatchedDecl->getType(), Func->getType()))
      continue;

    // Check if they have compatible inline specifiers
    // For functions, also check if they are both inline or both not inline
    if (MatchedDecl->isInlineSpecified() != Func->isInlineSpecified())
      continue;

    // Check if they are in the same namespace or translation unit
    const DeclContext *MatchedContext = MatchedDecl->getDeclContext();
    const DeclContext *FuncDeclContext = Func->getDeclContext();
    
    // If both are in namespaces, check if they are the same namespace
    if (isa<NamespaceDecl>(MatchedContext) && isa<NamespaceDecl>(FuncDeclContext)) {
      const auto *MatchedNS = cast<NamespaceDecl>(MatchedContext);
      const auto *FuncNS = cast<NamespaceDecl>(FuncDeclContext);
      if (MatchedNS->getOriginalNamespace() != FuncNS->getOriginalNamespace())
        continue;
    } else if (MatchedContext != FuncDeclContext) {
      // One is in translation unit, other is in namespace, or vice versa
      continue;
    }

    Declarations.push_back(Func);
  }

  // If there are multiple declarations, emit diagnostics for redundant ones
  if (Declarations.size() > 1) {
    // Sort by source location to identify the first declaration
    llvm::sort(Declarations, [](const FunctionDecl *A, const FunctionDecl *B) {
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