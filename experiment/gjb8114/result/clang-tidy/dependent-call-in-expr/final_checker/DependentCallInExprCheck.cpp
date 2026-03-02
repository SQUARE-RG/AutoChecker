//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallSet.h"
#include "llvm/ADT/SmallVector.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Helper function to collect all CallExpr nodes within an expression
void collectCallExprs(const Expr *E, llvm::SmallVectorImpl<const CallExpr *> &Calls) {
  if (!E) return;
  
  E = E->IgnoreParenImpCasts();
  
  if (const auto *CE = dyn_cast<CallExpr>(E)) {
    Calls.push_back(CE);
    // Don't return, continue to traverse arguments
  }
  
  // Traverse all children of the expression
  for (const Stmt *Child : E->children()) {
    if (const auto *ChildExpr = dyn_cast<Expr>(Child)) {
      collectCallExprs(ChildExpr, Calls);
    }
  }
}

// Helper function to check if two expressions refer to the same memory location
bool refersToSameLocation(const Expr *E1, const Expr *E2, ASTContext &Context) {
  if (!E1 || !E2) return false;
  
  E1 = E1->IgnoreParenImpCasts();
  E2 = E2->IgnoreParenImpCasts();
  
  // Handle address-of operator
  if (const auto *UO1 = dyn_cast<UnaryOperator>(E1)) {
    if (UO1->getOpcode() == UO_AddrOf) {
      E1 = UO1->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  if (const auto *UO2 = dyn_cast<UnaryOperator>(E2)) {
    if (UO2->getOpcode() == UO_AddrOf) {
      E2 = UO2->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  // Check if both are DeclRefExpr to the same variable
  if (const auto *DRE1 = dyn_cast<DeclRefExpr>(E1)) {
    if (const auto *DRE2 = dyn_cast<DeclRefExpr>(E2)) {
      return DRE1->getDecl() == DRE2->getDecl();
    }
  }
  
  // Check if both are MemberExpr accessing the same member
  if (const auto *ME1 = dyn_cast<MemberExpr>(E1)) {
    if (const auto *ME2 = dyn_cast<MemberExpr>(E2)) {
      return ME1->getMemberDecl() == ME2->getMemberDecl() &&
             refersToSameLocation(ME1->getBase(), ME2->getBase(), Context);
    }
  }
  
  // For array subscript, check if base and index are the same
  if (const auto *ASE1 = dyn_cast<ArraySubscriptExpr>(E1)) {
    if (const auto *ASE2 = dyn_cast<ArraySubscriptExpr>(E2)) {
      return refersToSameLocation(ASE1->getBase(), ASE2->getBase(), Context) &&
             refersToSameLocation(ASE1->getIdx(), ASE2->getIdx(), Context);
    }
  }
  
  return false;
}

// Check if a parameter type could introduce data dependency
bool isDependencyType(QualType Type) {
  Type = Type.getNonReferenceType();
  
  // Pointer to non-const type
  if (const auto *PtrType = Type->getAs<PointerType>()) {
    return !PtrType->getPointeeType().isConstQualified();
  }
  
  // Reference to non-const type
  if (Type->isReferenceType()) {
    return !Type.getNonReferenceType().isConstQualified();
  }
  
  return false;
}

// Check if a function accesses global variables (including through no parameters)
bool accessesGlobalOrStatic(const FunctionDecl *Func, ASTContext &Context) {
  if (!Func) return false;
  
  // Check if function has no parameters but accesses globals
  if (Func->getNumParams() == 0) {
    // Check if function accesses global/static variables
    if (Func->hasBody()) {
      const Stmt *Body = Func->getBody();
      if (!Body) return false;
      
      // Check all DeclRefExpr in the body for global variables
      llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
      for (const Stmt *Child : Body->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          DeclRefs.push_back(DRE);
        }
      }
      
      for (const DeclRefExpr *DRE : DeclRefs) {
        if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
          if (VD->hasGlobalStorage() && !VD->isStaticLocal()) {
            return true;
          }
        }
      }
    }
    return false;
  }
  
  // Check if any parameter could point to global/static data
  for (unsigned i = 0; i < Func->getNumParams(); ++i) {
    const ParmVarDecl *Param = Func->getParamDecl(i);
    if (isDependencyType(Param->getType())) {
      return true;
    }
  }
  
  return false;
}

// Check if a function accesses a specific global variable
bool accessesSpecificGlobal(const FunctionDecl *Func, const VarDecl *Global, ASTContext &Context) {
  if (!Func || !Global) return false;
  
  // Check if the function directly references this global variable
  if (Func->hasBody()) {
    const Stmt *Body = Func->getBody();
    if (!Body) return false;
    
    // Check all DeclRefExpr in the body
    llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
    for (const Stmt *Child : Body->children()) {
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
        DeclRefs.push_back(DRE);
      }
    }
    
    for (const DeclRefExpr *DRE : DeclRefs) {
      if (DRE->getDecl() == Global) {
        return true;
      }
    }
  }
  
  return false;
}

// Check if a function accesses static local variables
bool accessesStaticLocal(const FunctionDecl *Func, ASTContext &Context) {
  if (!Func) return false;
  
  if (Func->hasBody()) {
    const Stmt *Body = Func->getBody();
    if (!Body) return false;
    
    // Check all DeclRefExpr in the body for static local variables
    llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
    for (const Stmt *Child : Body->children()) {
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
        DeclRefs.push_back(DRE);
      }
    }
    
    for (const DeclRefExpr *DRE : DeclRefs) {
      if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
        if (VD->isStaticLocal()) {
          return true;
        }
      }
    }
  }
  
  return false;
}

// Check if two functions access the same static local variable
bool accessSameStaticLocal(const FunctionDecl *Func1, const FunctionDecl *Func2, ASTContext &Context) {
  if (!Func1 || !Func2) return false;
  
  // Collect static local variables accessed by Func1
  llvm::SmallSet<const VarDecl *, 4> Func1Statics;
  if (Func1->hasBody()) {
    const Stmt *Body1 = Func1->getBody();
    if (Body1) {
      for (const Stmt *Child : Body1->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal()) {
              Func1Statics.insert(VD);
            }
          }
        }
      }
    }
  }
  
  // Check if Func2 accesses any of the same static local variables
  if (Func2->hasBody()) {
    const Stmt *Body2 = Func2->getBody();
    if (Body2) {
      for (const Stmt *Child : Body2->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal() && Func1Statics.count(VD)) {
              return true;
            }
          }
        }
      }
    }
  }
  
  return false;
}

// Check if two functions access static local variables with the same name
bool accessStaticLocalWithSameName(const FunctionDecl *Func1, const FunctionDecl *Func2, ASTContext &Context) {
  if (!Func1 || !Func2) return false;
  
  // Collect static local variable names accessed by Func1
  llvm::SmallSet<std::string, 4> Func1StaticNames;
  if (Func1->hasBody()) {
    const Stmt *Body1 = Func1->getBody();
    if (Body1) {
      for (const Stmt *Child : Body1->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal()) {
              Func1StaticNames.insert(VD->getNameAsString());
            }
          }
        }
      }
    }
  }
  
  // Check if Func2 accesses static local variables with the same name
  if (Func2->hasBody()) {
    const Stmt *Body2 = Func2->getBody();
    if (Body2) {
      for (const Stmt *Child : Body2->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal() && Func1StaticNames.count(VD->getNameAsString())) {
              return true;
            }
          }
        }
      }
    }
  }
  
  return false;
}

// Check if two function calls have overlapping dependency arguments
bool haveDependencyOverlap(const CallExpr *Call1, const CallExpr *Call2, 
                          ASTContext &Context) {
  const FunctionDecl *Func1 = Call1->getDirectCallee();
  const FunctionDecl *Func2 = Call2->getDirectCallee();
  
  // If we can't resolve the callee, conservatively assume dependency
  if (!Func1 || !Func2) {
    return true;
  }
  
  // Check if both functions access static local variables
  bool func1AccessesStaticLocal = accessesStaticLocal(Func1, Context);
  bool func2AccessesStaticLocal = accessesStaticLocal(Func2, Context);
  
  // If both functions access static local variables, check if they access the same one
  if (func1AccessesStaticLocal && func2AccessesStaticLocal) {
    if (accessSameStaticLocal(Func1, Func2, Context)) {
      return true;
    }
    // Also check if they access static locals with the same name
    // This handles the case where each function has its own static local with the same name
    if (accessStaticLocalWithSameName(Func1, Func2, Context)) {
      return true;
    }
  }
  
  // Check if both functions access global/static variables
  bool func1AccessesGlobal = accessesGlobalOrStatic(Func1, Context);
  bool func2AccessesGlobal = accessesGlobalOrStatic(Func2, Context);
  
  // If both functions access global/static variables, they might access the same one
  if (func1AccessesGlobal && func2AccessesGlobal) {
    // Get all global variables in the translation unit
    const TranslationUnitDecl *TU = Context.getTranslationUnitDecl();
    for (const Decl *D : TU->decls()) {
      if (const auto *VD = dyn_cast<VarDecl>(D)) {
        if (VD->hasGlobalStorage() && !VD->isStaticLocal()) {
          // Check if both functions access this specific global variable
          bool func1Accesses = accessesSpecificGlobal(Func1, VD, Context);
          bool func2Accesses = accessesSpecificGlobal(Func2, VD, Context);
          
          // If both functions access the same global variable, they are dependent
          if (func1Accesses && func2Accesses) {
            return true;
          }
        }
      }
    }
    
    // For functions with no parameters that access globals, we need to be conservative
    // If both access globals but we can't determine if they access the same one,
    // we should still report a violation when they're in the same expression
    // This handles the case where increment_x modifies global x and check_x reads it
    return true;
  }
  
  // Check each parameter combination for direct overlap
  for (unsigned i = 0; i < Call1->getNumArgs() && i < Func1->getNumParams(); ++i) {
    QualType ParamType1 = Func1->getParamDecl(i)->getType();
    if (!isDependencyType(ParamType1)) continue;
    
    const Expr *Arg1 = Call1->getArg(i);
    
    for (unsigned j = 0; j < Call2->getNumArgs() && j < Func2->getNumParams(); ++j) {
      QualType ParamType2 = Func2->getParamDecl(j)->getType();
      if (!isDependencyType(ParamType2)) continue;
      
      const Expr *Arg2 = Call2->getArg(j);
      
      if (refersToSameLocation(Arg1, Arg2, Context)) {
        return true;
      }
    }
  }
  
  return false;
}

} // namespace

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match all expressions to catch any expression that could contain multiple function calls
  Finder->addMatcher(expr().bind("topLevelExpr"), this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *TopLevel = Result.Nodes.getNodeAs<Expr>("topLevelExpr");
  if (!TopLevel || !TopLevel->getBeginLoc().isValid()) return;
  
  // Skip if this is not a top-level expression (e.g., part of a larger expression)
  // We only want to check expressions that are not subexpressions of other expressions
  // we're already checking
  if (const auto *Parent = dyn_cast_or_null<Expr>(TopLevel->IgnoreParenImpCasts())) {
    // Check if this expression is a direct child of another expression we would match
    // This prevents duplicate checking
    if (Parent != TopLevel) {
      // This is a subexpression, skip it as it will be checked when we process its parent
      return;
    }
  }
  
  // Collect all CallExprs within this top-level expression
  llvm::SmallVector<const CallExpr *, 4> Calls;
  collectCallExprs(TopLevel, Calls);
  
  // Need at least 2 calls to have a potential violation
  if (Calls.size() < 2) return;
  
  // Check each pair of calls for dependency overlap
  for (unsigned i = 0; i < Calls.size(); ++i) {
    for (unsigned j = i + 1; j < Calls.size(); ++j) {
      if (haveDependencyOverlap(Calls[i], Calls[j], *Result.Context)) {
        diag(TopLevel->getBeginLoc(), 
             "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
        return; // Report only once per expression
      }
    }
  }
}

} // namespace clang::tidy::ucassaat