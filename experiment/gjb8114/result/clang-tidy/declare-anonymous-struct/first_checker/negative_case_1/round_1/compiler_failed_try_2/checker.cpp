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
#include "clang/ASTMatchers/ASTMatchers.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void DeclareAnonymousStructCheck::registerMatchers(MatchFinder *Finder) {
  // Match struct/union/class definitions that contain fields with record type
  Finder->addMatcher(
      recordDecl(isDefinition(),
                 has(fieldDecl(hasType(recordType()))
                         .bind("field")))
          .bind("record"),
      this);
}

void DeclareAnonymousStructCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *Record = Result.Nodes.getNodeAs<RecordDecl>("record");
  const auto *Field = Result.Nodes.getNodeAs<FieldDecl>("field");

  if (!Record || !Field || !Record->getLocation().isValid() ||
      !Field->getLocation().isValid())
    return;

  // Get the type of the field
  const Type *FieldType = Field->getType().getTypePtrOrNull();
  if (!FieldType)
    return;

  // Check if it's an elaborated type (e.g., 'struct X')
  if (const auto *Elaborated = dyn_cast<ElaboratedType>(FieldType)) {
    FieldType = Elaborated->getNamedType().getTypePtrOrNull();
    if (!FieldType)
      return;
  }

  // Get the record declaration from the field type
  const RecordType *RecordTy = dyn_cast<RecordType>(FieldType);
  if (!RecordTy)
    return;

  const RecordDecl *InnerRecord = RecordTy->getDecl();
  if (!InnerRecord || !InnerRecord->isAnonymousStructOrUnion())
    return;

  // Emit diagnostic
  diag(Field->getLocation(),
       "禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]")
      << Field->getSourceRange();

  // Add note pointing to the outer struct definition
  if (Record->getIdentifier()) {
    diag(Record->getLocation(), "外层结构体 '%0' 定义在此",
         DiagnosticIDs::Note)
        << Record->getName() << Record->getSourceRange();
  } else {
    diag(Record->getLocation(), "外层结构体定义在此", DiagnosticIDs::Note)
        << Record->getSourceRange();
  }
}

} // namespace clang::tidy::ucassaat