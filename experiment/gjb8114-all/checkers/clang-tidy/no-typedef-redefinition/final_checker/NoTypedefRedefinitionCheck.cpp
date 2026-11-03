//===--- NoTypedefRedefinitionCheck.cpp - clang-tidy ----------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoTypedefRedefinitionCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/ASTTypeTraits.h"
#include "clang/AST/Decl.h"
#include "clang/AST/DeclCXX.h"
#include "clang/AST/ParentMapContext.h"
#include "clang/AST/Type.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Basic/SourceManager.h"
#include "llvm/ADT/SmallPtrSet.h"

#include <vector>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

const TypedefDecl *resolveConflictingTypedef(const Decl *D, StringRef Name,
                                             const TypedefDecl *Current) {
  if (!D || D == Current)
    return nullptr;

  if (const auto *TD = dyn_cast<TypedefDecl>(D)) {
    if (TD != Current && TD->getName() == Name)
      return TD;
    return nullptr;
  }

  if (const auto *USD = dyn_cast<UsingShadowDecl>(D)) {
    const NamedDecl *Target = USD->getTargetDecl();
    if (const auto *TD = dyn_cast_or_null<TypedefDecl>(Target)) {
      if (TD != Current && TD->getName() == Name)
        return TD;
    }
  }

  return nullptr;
}

bool isBeforeDecl(const Decl *Existing, const Decl *Current,
                  const SourceManager &SM) {
  if (!Existing || !Current)
    return false;

  SourceLocation ExistingLoc = Existing->getLocation();
  SourceLocation CurrentLoc = Current->getLocation();
  if (ExistingLoc.isInvalid() || CurrentLoc.isInvalid())
    return false;

  return SM.isBeforeInTranslationUnit(ExistingLoc, CurrentLoc);
}

bool hasConflictingTypedefInDeclStmt(const DeclStmt *DS, StringRef Name,
                                     const TypedefDecl *Current,
                                     const SourceManager &SM) {
  if (!DS)
    return false;

  for (const auto *D : DS->decls()) {
    if (D == Current)
      continue;

    if (resolveConflictingTypedef(D, Name, Current)) {
      if (isBeforeDecl(D, Current, SM))
        return true;
    }
  }

  return false;
}

bool hasConflictingTypedefInCompoundStmt(const CompoundStmt *CS, StringRef Name,
                                         const TypedefDecl *Current,
                                         const SourceManager &SM) {
  if (!CS)
    return false;

  for (const auto *Child : CS->body()) {
    if (const auto *DS = dyn_cast<DeclStmt>(Child)) {
      if (hasConflictingTypedefInDeclStmt(DS, Name, Current, SM))
        return true;
    }
  }

  return false;
}

bool hasConflictingTypedefInForStmt(const ForStmt *FS, StringRef Name,
                                    const TypedefDecl *Current,
                                    const SourceManager &SM) {
  if (!FS)
    return false;

  return hasConflictingTypedefInDeclStmt(
      dyn_cast_or_null<DeclStmt>(FS->getInit()), Name, Current, SM);
}

bool hasConflictingTypedefInContext(const DeclContext *DC, StringRef Name,
                                    const TypedefDecl *Current,
                                    const SourceManager &SM) {
  if (!DC || !Current)
    return false;

  bool SameContext = (DC == Current->getDeclContext());

  for (const auto *D : DC->lookup(Current->getDeclName())) {
    if (D == Current)
      continue;

    if (resolveConflictingTypedef(D, Name, Current)) {
      if (SameContext && !isBeforeDecl(D, Current, SM))
        continue;
      return true;
    }
  }

  return false;
}

bool hasConflictingTypedefInBases(
    const CXXRecordDecl *RD, StringRef Name, const TypedefDecl *Current,
    llvm::SmallPtrSetImpl<const CXXRecordDecl *> &Visited) {
  if (!RD || !Visited.insert(RD).second)
    return false;

  for (const auto &Base : RD->bases()) {
    QualType BaseType = Base.getType();
    if (BaseType.isNull() || BaseType->isDependentType())
      continue;

    const CXXRecordDecl *BaseRD = nullptr;
    if (const auto *RT = BaseType->getAs<RecordType>())
      BaseRD = dyn_cast<CXXRecordDecl>(RT->getDecl());

    if (!BaseRD)
      continue;

    for (const auto *D : BaseRD->lookup(Current->getDeclName())) {
      if (resolveConflictingTypedef(D, Name, Current))
        return true;
    }

    if (hasConflictingTypedefInBases(BaseRD, Name, Current, Visited))
      return true;
  }

  return false;
}

bool hasConflictFromDeclContexts(
    const TypedefDecl *TD, StringRef Name, const SourceManager &SM,
    llvm::SmallPtrSetImpl<const CXXRecordDecl *> &VisitedBases) {
  const DeclContext *DC = TD->getDeclContext();

  while (DC) {
    if (const auto *CXXRD = dyn_cast<CXXRecordDecl>(DC)) {
      if (hasConflictingTypedefInContext(CXXRD, Name, TD, SM) ||
          hasConflictingTypedefInBases(CXXRD, Name, TD, VisitedBases))
        return true;
    } else if (const auto *RD = dyn_cast<RecordDecl>(DC)) {
      if (hasConflictingTypedefInContext(RD, Name, TD, SM))
        return true;
    } else if (const auto *NS = dyn_cast<NamespaceDecl>(DC)) {
      if (hasConflictingTypedefInContext(NS, Name, TD, SM))
        return true;
    } else if (const auto *TU = dyn_cast<TranslationUnitDecl>(DC)) {
      if (hasConflictingTypedefInContext(TU, Name, TD, SM))
        return true;
    }

    if (DC->isTranslationUnit())
      break;

    DC = DC->getParent();
  }

  return false;
}

bool hasConflictFromLexicalParents(
    const TypedefDecl *TD, StringRef Name, ASTContext *Context,
    const SourceManager &SM,
    llvm::SmallPtrSetImpl<const CXXRecordDecl *> &VisitedBases) {
  if (!TD || !Context)
    return false;

  llvm::SmallPtrSet<const Decl *, 32> VisitedDecls;
  llvm::SmallPtrSet<const Stmt *, 32> VisitedStmts;

  std::vector<DynTypedNode> Worklist;
  for (const auto &Parent : Context->getParents(DynTypedNode::create(*TD)))
    Worklist.push_back(Parent);

  while (!Worklist.empty()) {
    DynTypedNode Node = Worklist.back();
    Worklist.pop_back();

    if (const auto *D = Node.get<Decl>()) {
      if (!VisitedDecls.insert(D).second)
        continue;

      if (const auto *CXXRD = dyn_cast<CXXRecordDecl>(D)) {
        if (hasConflictingTypedefInContext(CXXRD, Name, TD, SM) ||
            hasConflictingTypedefInBases(CXXRD, Name, TD, VisitedBases))
          return true;
      } else if (const auto *RD = dyn_cast<RecordDecl>(D)) {
        if (hasConflictingTypedefInContext(RD, Name, TD, SM))
          return true;
      } else if (const auto *NS = dyn_cast<NamespaceDecl>(D)) {
        if (hasConflictingTypedefInContext(NS, Name, TD, SM))
          return true;
      } else if (const auto *TU = dyn_cast<TranslationUnitDecl>(D)) {
        if (hasConflictingTypedefInContext(TU, Name, TD, SM))
          return true;
      }

      for (const auto &Parent : Context->getParents(Node))
        Worklist.push_back(Parent);
      continue;
    }

    if (const auto *S = Node.get<Stmt>()) {
      if (!VisitedStmts.insert(S).second)
        continue;

      if (const auto *CS = dyn_cast<CompoundStmt>(S)) {
        if (hasConflictingTypedefInCompoundStmt(CS, Name, TD, SM))
          return true;
      } else if (const auto *FS = dyn_cast<ForStmt>(S)) {
        if (hasConflictingTypedefInForStmt(FS, Name, TD, SM))
          return true;
      }

      for (const auto &Parent : Context->getParents(Node))
        Worklist.push_back(Parent);
      continue;
    }

    for (const auto &Parent : Context->getParents(Node))
      Worklist.push_back(Parent);
  }

  return false;
}

} // namespace

void NoTypedefRedefinitionCheck::registerMatchers(MatchFinder *Finder) {
  Finder->addMatcher(
      typedefDecl(isExpansionInMainFile(), unless(isExpansionInSystemHeader()))
          .bind("typedef_decl"),
      this);
}

void NoTypedefRedefinitionCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *TD = Result.Nodes.getNodeAs<TypedefDecl>("typedef_decl");
  if (!TD || !Result.Context || !Result.SourceManager)
    return;

  StringRef Name = TD->getName();
  if (Name.empty())
    return;

  // A direct redeclaration in the redeclaration chain is a real redefinition.
  for (const Decl *Prev = TD->getPreviousDecl(); Prev;
       Prev = Prev->getPreviousDecl()) {
    if (const auto *PrevTD = dyn_cast<TypedefDecl>(Prev)) {
      if (PrevTD != TD && PrevTD->getName() == Name) {
        diag(TD->getLocation(),
             "typedef %0 is a redefinition or shadows an existing typedef type")
            << TD;
        return;
      }
    }
  }

  llvm::SmallPtrSet<const CXXRecordDecl *, 16> VisitedBases;

  if (hasConflictFromLexicalParents(TD, Name, Result.Context,
                                    *Result.SourceManager, VisitedBases)) {
    diag(TD->getLocation(),
         "typedef %0 is a redefinition or shadows an existing typedef type")
        << TD;
    return;
  }

  if (hasConflictFromDeclContexts(TD, Name, *Result.SourceManager,
                                  VisitedBases)) {
    diag(TD->getLocation(),
         "typedef %0 is a redefinition or shadows an existing typedef type")
        << TD;
  }
}

} // namespace clang::tidy::ucassaat