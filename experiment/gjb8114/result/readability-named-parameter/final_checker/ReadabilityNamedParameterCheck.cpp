//===--- ReadabilityNamedParameterCheck.cpp - clang-tidy ------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ReadabilityNamedParameterCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ReadabilityNamedParameterCheck::registerMatchers(MatchFinder *Finder) {
  // Match function declarations that are definitions (have a body)
  // Exclude template instantiations and functions with Naked attribute
  Finder->addMatcher(
      functionDecl(isDefinition(),
                   unless(hasAttr(attr::Kind::Naked)),
                   unless(ast_matchers::isTemplateInstantiation()))
          .bind("funcDecl"),
      this);
}

void ReadabilityNamedParameterCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *FuncDecl = Result.Nodes.getNodeAs<FunctionDecl>("funcDecl");
  if (!FuncDecl)
    return;

  // Skip lambda expressions
  if (const auto *Method = dyn_cast<CXXMethodDecl>(FuncDecl)) {
    if (Method->getParent()->isLambda())
      return;
  }

  // Skip implicitly generated functions (constructors, destructors, operators, etc.)
  if (FuncDecl->isImplicit())
    return;

  // Skip function template specializations (but not primary templates)
  if (FuncDecl->getDescribedFunctionTemplate()) {
    // This is a primary template declaration, check its parameters
  } else if (FuncDecl->isTemplateInstantiation()) {
    // This is a template instantiation, skip it to avoid duplicate diagnostics
    return;
  }

  // Skip defaulted special member functions (constructors, destructors, assignment operators)
  if (const auto *Method = dyn_cast<CXXMethodDecl>(FuncDecl)) {
    if (Method->isDefaulted())
      return;
  }

  // Skip deleted functions
  if (FuncDecl->isDeleted())
    return;

  // Check each parameter for a name
  for (unsigned I = 0, E = FuncDecl->getNumParams(); I != E; ++I) {
    const auto *Param = FuncDecl->getParamDecl(I);
    
    // Skip parameters with invalid source locations
    if (!Param->getLocation().isValid())
      continue;
      
    // Check if the parameter has a name in the source code
    if (Param->getDeclName().isEmpty()) {
      SourceLocation Loc = Param->getLocation();
      SourceManager &SM = *Result.SourceManager;
      const LangOptions &LangOpts = Result.Context->getLangOpts();
      
      // Get the source text for the parameter
      bool HasNamedParameter = false;
      
      if (Loc.isValid() && SM.isWrittenInMainFile(Loc)) {
        // Check if the location is from a macro expansion
        if (Loc.isMacroID()) {
          // Get the expansion location to see if it's from a macro
          SourceLocation ExpansionLoc = SM.getExpansionLoc(Loc);
          if (ExpansionLoc.isValid()) {
            // Check if the expansion location is different from the spelling location
            // This indicates the parameter came from a macro expansion
            SourceLocation SpellingLoc = SM.getSpellingLoc(Loc);
            if (ExpansionLoc != SpellingLoc) {
              // Parameter came from a macro, skip it
              continue;
            }
          }
        }
        
        // Get the source text starting from the parameter location
        StringRef SourceText = Lexer::getSourceText(
            CharSourceRange::getTokenRange(Loc, Loc), SM, LangOpts);
        
        if (!SourceText.empty()) {
          // Check if the source text starts with an identifier character
          // This handles both named parameters and parameters with comments
          char FirstChar = SourceText[0];
          if (isalpha(FirstChar) || FirstChar == '_' || FirstChar == '/') {
            HasNamedParameter = true;
          }
        }
        
        // Also check if there's a comment at the parameter location
        // by looking at the immediate source context
        if (!HasNamedParameter) {
          // Get a larger range to check for comments
          SourceRange ParamRange = Param->getSourceRange();
          if (ParamRange.isValid()) {
            StringRef LargerText = Lexer::getSourceText(
                CharSourceRange::getTokenRange(ParamRange), SM, LangOpts);
            
            // Check if the text contains comment markers
            if (LargerText.contains("/*") || LargerText.contains("//")) {
              HasNamedParameter = true;
            }
          }
        }
        
        // Check if the parameter type is a typedef/alias that might indicate
        // it's intentionally unnamed (like testing::Unused)
        if (!HasNamedParameter) {
          QualType ParamType = Param->getType();
          
          // Handle nullptr_t specially - it's a built-in type that looks like a typedef
          if (ParamType->isNullPtrType()) {
            HasNamedParameter = true;
            continue;
          }
          
          if (const auto *TD = ParamType->getAs<TypedefType>()) {
            StringRef TypeName = TD->getDecl()->getName();
            if (TypeName == "Unused" || TypeName == "unused_t" || 
                TypeName == "ignore_t" || TypeName == "Ignore") {
              HasNamedParameter = true;
            }
          } else if (const auto *ET = ParamType->getAs<ElaboratedType>()) {
            if (const auto *TD = ET->getNamedType()->getAs<TypedefType>()) {
              StringRef TypeName = TD->getDecl()->getName();
              if (TypeName == "Unused" || TypeName == "unused_t" || 
                  TypeName == "ignore_t" || TypeName == "Ignore") {
                HasNamedParameter = true;
              }
            }
          }
        }
        
        // Check if the parameter is part of a function that came from a macro expansion
        // This handles cases like #define M void MethodM(int) {}
        if (!HasNamedParameter) {
          SourceLocation FuncLoc = FuncDecl->getLocation();
          if (FuncLoc.isMacroID()) {
            SourceLocation FuncExpansionLoc = SM.getExpansionLoc(FuncLoc);
            SourceLocation FuncSpellingLoc = SM.getSpellingLoc(FuncLoc);
            if (FuncExpansionLoc != FuncSpellingLoc) {
              // The entire function came from a macro expansion, skip it
              continue;
            }
          }
        }
      }
      
      // Only emit diagnostic if there's truly no parameter name (not even a comment)
      if (!HasNamedParameter) {
        diag(Param->getLocation(),
             "all parameters should be named in a function");
      }
    }
  }
}

} // namespace clang::tidy::ucassaat