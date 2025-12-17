第2轮生成的checker编译失败，开始第2次重试
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to:
1. Analyze compiler error messages in relation to the provided checker code (both .cpp and .h files).
2. Identify the root causes of the compilation errors.
3. Generate new checker code based on the repair steps and related reference code snippets.
4. Ensure the generated checker code is complete and compilable.

# Inputs

## checker code 

checker_cpp:
```cpp
//===--- UseUncheckPointerAfterMallocCheck.cpp - clang-tidy ---------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "UseUncheckPointerAfterMallocCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Expr.h"
#include "clang/AST/OperationKinds.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallPtrSet.h"
#include <string>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Matcher for dynamic memory allocation functions
const auto AllocFuncMatcher = functionDecl(
    hasAnyName("::malloc", "::calloc", "::realloc", "std::malloc", 
               "std::calloc", "std::realloc"));

// Matcher for allocation calls
const auto AllocCallMatcher = callExpr(
    callee(AllocFuncMatcher),
    unless(hasAncestor(callExpr()))).bind("allocCall");

// Helper matcher to find the pointer variable from allocation
const auto PointerVarFromAllocMatcher = stmt(anyOf(
    // Direct assignment: p = malloc()
    binaryOperator(hasOperatorName("="),
        hasLHS(declRefExpr(to(varDecl().bind("ptrVar")))),
        hasRHS(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))),
    // Variable declaration with initialization: int *p = malloc()
    declStmt(hasSingleDecl(varDecl(hasInitializer(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))).bind("ptrVarDecl")))
)).bind("allocExpr");

// Matcher for pointer usage
const auto PointerUseMatcher = expr(
    anyOf(
        // Dereference: *p
        unaryOperator(hasOperatorName("*"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Array subscript: p[0]
        arraySubscriptExpr(
            hasBase(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Member access through pointer: p->field
        memberExpr(hasObjectExpression(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar")))))),
        // Function call through pointer: p()
        callExpr(has(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar"))))))
    )).bind("pointerUse");

// Matcher for null pointer checks
const auto NullCheckMatcher = stmt(
    anyOf(
        // Explicit comparisons: ptr == NULL, ptr != NULL
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))),
            hasRHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0))))),
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0)))),
            hasRHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Implicit checks: if (ptr), while (ptr)
        implicitCastExpr(hasImplicitDestinationType(booleanType()),
            hasSourceExpression(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Negated checks: if (!ptr)
        unaryOperator(hasOperatorName("!"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))))
    )).bind("nullCheck");

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Match allocation expressions and pointer uses in the same function
  Finder->addMatcher(
      traverse(TK_AsIs,
          stmt(anyOf(
              // Find allocation first
              PointerVarFromAllocMatcher,
              // Then find uses that might be unchecked
              PointerUseMatcher
          )).bind("stmtNode")),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Get the current statement node
  const Stmt *StmtNode = Result.Nodes.getNodeAs<Stmt>("stmtNode");
  if (!StmtNode || !StmtNode->getBeginLoc().isValid()) return;
  
  // Get the function containing this statement
  const DeclContext *DC = nullptr;
  auto Parents = Context->getParents(*StmtNode);
  if (!Parents.empty()) {
    DC = Parents[0].get<Decl>();
  }
  const FunctionDecl *Func = dyn_cast_or_null<FunctionDecl>(DC);
  if (!Func || !Func->hasBody()) return;
  
  const Stmt *FuncBody = Func->getBody();
  if (!FuncBody) return;
  
  // Check if this is an allocation expression
  const Stmt *AllocExpr = Result.Nodes.getNodeAs<Stmt>("allocExpr");
  const VarDecl *PtrVar = nullptr;
  const VarDecl *PtrVarDecl = Result.Nodes.getNodeAs<VarDecl>("ptrVarDecl");
  
  if (AllocExpr && AllocExpr->getBeginLoc().isValid()) {
    // Get the pointer variable from the allocation
    if (PtrVarDecl && PtrVarDecl->getLocation().isValid()) {
      PtrVar = PtrVarDecl;
    } else {
      PtrVar = Result.Nodes.getNodeAs<VarDecl>("ptrVar");
    }
    
    if (!PtrVar || !PtrVar->getLocation().isValid()) return;
    
    // Store allocation information for this variable
    // We'll track allocations and their locations
    // This is a simplified approach - in a real checker, you'd want to
    // maintain state across multiple matches
  }
  
  // Check if this is a pointer usage
  const Expr *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
  const VarDecl *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  
  if (PointerUse && PointerUse->getBeginLoc().isValid() && 
      UseVar && UseVar->getLocation().isValid()) {
    
    // Find the most recent allocation for this variable before the use
    SourceLocation LastAllocLoc;
    bool IsRealloc = false;
    
    // Traverse the function body to find allocations of this variable
    std::function<void(const Stmt *)> findAllocations = [&](const Stmt *S) {
      if (!S) return;
      
      // Check if this is an allocation of our variable
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_Assign) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) {
              const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
              // Check if RHS is a call to allocation function
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(RHS)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(RHS);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(), 
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      // Check variable declarations with initializers
      if (const auto *DS = dyn_cast<DeclStmt>(S)) {
        for (const Decl *D : DS->decls()) {
          if (const auto *VD = dyn_cast<VarDecl>(D)) {
            if (VD == UseVar && VD->hasInit()) {
              const Expr *Init = VD->getInit()->IgnoreParenImpCasts();
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(Init)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(Init);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findAllocations(Child);
      }
    };
    
    findAllocations(FuncBody);
    
    // If no allocation found before this use, it's not from dynamic allocation
    if (LastAllocLoc.isInvalid()) return;
    
    // Now check if there's a null check between the allocation and the use
    bool FoundNullCheck = false;
    
    std::function<void(const Stmt *)> findNullChecks = [&](const Stmt *S) {
      if (!S || FoundNullCheck) return;
      
      // Check binary operators for explicit null comparisons
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
          
          // Check if one side is our variable
          const DeclRefExpr *VarDRE = nullptr;
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          } else if (const auto *DRE = dyn_cast<DeclRefExpr>(RHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          }
          
          if (VarDRE) {
            // Check if the other side is a null pointer constant
            const Expr *OtherSide = (VarDRE == dyn_cast<DeclRefExpr>(LHS)) ? RHS : LHS;
            if (OtherSide->isNullPointerConstant(*Context, 
                                                 Expr::NPC_ValueDependentIsNull)) {
              // Check if this null check is between allocation and use
              if (SM.isBeforeInTranslationUnit(LastAllocLoc, BinOp->getBeginLoc()) &&
                  SM.isBeforeInTranslationUnit(BinOp->getBeginLoc(), 
                                               PointerUse->getBeginLoc())) {
                FoundNullCheck = true;
                return;
              }
            }
          }
        }
      }
      
      // Check for implicit checks (if (ptr), while (ptr))
      if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
        if (DRE->getDecl() == UseVar) {
          // Check if parent is an implicit cast to boolean
          const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("");
          if (Parent) {
            if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Parent)) {
              if (ICE->getCastKind() == CK_PointerToBoolean ||
                  ICE->getCastKind() == CK_IntegralToBoolean) {
                // Check if this is in a condition context
                const Stmt *GrandParent = Result.Nodes.getNodeAs<Stmt>("");
                if (GrandParent) {
                  if (isa<IfStmt>(GrandParent) || isa<WhileStmt>(GrandParent) ||
                      isa<DoStmt>(GrandParent) || isa<ForStmt>(GrandParent) ||
                      isa<ConditionalOperator>(GrandParent)) {
                    if (SM.isBeforeInTranslationUnit(LastAllocLoc, 
                                                     ICE->getBeginLoc()) &&
                        SM.isBeforeInTranslationUnit(ICE->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      FoundNullCheck = true;
                      return;
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      // Check for negated checks (if (!ptr))
      if (const auto *UnaryOp = dyn_cast<UnaryOperator>(S)) {
        if (UnaryOp->getOpcode() == UO_LNot) {
          const Expr *SubExpr = UnaryOp->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
            if (DRE->getDecl() == UseVar) {
              // Check if this is in a condition context
              const Stmt *Parent = Result.Nodes.getNodeAs<Stmt>("");
              if (Parent) {
                if (isa<IfStmt>(Parent) || isa<WhileStmt>(Parent) ||
                    isa<DoStmt>(Parent) || isa<ForStmt>(Parent) ||
                    isa<ConditionalOperator>(Parent)) {
                  if (SM.isBeforeInTranslationUnit(LastAllocLoc,
                                                   UnaryOp->getBeginLoc()) &&
                      SM.isBeforeInTranslationUnit(UnaryOp->getBeginLoc(),
                                                   PointerUse->getBeginLoc())) {
                    FoundNullCheck = true;
                    return;
                  }
                }
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findNullChecks(Child);
      }
    };
    
    findNullChecks(FuncBody);
    
    // If no null check found, emit diagnostic
    if (!FoundNullCheck) {
      diag(PointerUse->getBeginLoc(), 
           "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
          << PointerUse->getSourceRange();
    }
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- UseUncheckPointerAfterMallocCheck.h - clang-tidy -------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Checks that pointers obtained through dynamic memory allocation functions
/// (malloc, calloc, realloc) are checked for null before their first use.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/use-uncheck-pointer-after-malloc.html
class UseUncheckPointerAfterMallocCheck : public ClangTidyCheck {
public:
  UseUncheckPointerAfterMallocCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
```
## compiler error info
[1/7] Building CXX object tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UcasSaatTidyModule.cpp.o
[2/7] Building CXX object tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UseUncheckPointerAfterMallocCheck.cpp.o
FAILED: tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UseUncheckPointerAfterMallocCheck.cpp.o 
ccache /usr/bin/c++ -DGTEST_HAS_RTTI=0 -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS -I/root/code_check/llvm-project/build/tools/clang/tools/extra/clang-tidy/ucassaat -I/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat -I/root/code_check/llvm-project/build/tools/clang/tools/extra/clang-tidy -I/root/code_check/llvm-project/clang/include -I/root/code_check/llvm-project/build/tools/clang/include -I/root/code_check/llvm-project/build/include -I/root/code_check/llvm-project/llvm/include -fPIC -fno-semantic-interposition -fvisibility-inlines-hidden -Werror=date-time -fno-lifetime-dse -Wall -Wextra -Wno-unused-parameter -Wwrite-strings -Wcast-qual -Wno-missing-field-initializers -pedantic -Wno-long-long -Wimplicit-fallthrough -Wno-maybe-uninitialized -Wno-nonnull -Wno-class-memaccess -Wno-redundant-move -Wno-pessimizing-move -Wno-noexcept-type -Wdelete-non-virtual-dtor -Wsuggest-override -Wno-comment -Wno-misleading-indentation -Wctad-maybe-unsupported -fdiagnostics-color -ffunction-sections -fdata-sections -fno-common -Woverloaded-virtual -fno-strict-aliasing -O2 -g -DNDEBUG  -fno-exceptions -funwind-tables -fno-rtti -gsplit-dwarf -std=c++17 -MD -MT tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UseUncheckPointerAfterMallocCheck.cpp.o -MF tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UseUncheckPointerAfterMallocCheck.cpp.o.d -o tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UseUncheckPointerAfterMallocCheck.cpp.o -c /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp: In member function ‘virtual void clang::tidy::ucassaat::UseUncheckPointerAfterMallocCheck::check(const clang::ast_matchers::MatchFinder::MatchResult&)’:
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp:118:36: error: ‘class clang::ASTContext’ has no member named ‘getEnclosingDeclContext’
  118 |   const DeclContext *DC = Context->getEnclosingDeclContext(StmtNode);
      |                                    ^~~~~~~~~~~~~~~~~~~~~~~
In file included from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchers.h:72,
                 from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchFinder.h:43,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/../ClangTidyCheck.h:14,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.h:12,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp:9:
/root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchersInternal.h: In instantiation of ‘std::vector<clang::ast_matchers::internal::DynTypedMatcher> clang::ast_matchers::internal::VariadicOperatorMatcher<Ps>::getMatchers(std::index_sequence<Idx ...>) const & [with T = clang::Expr; long unsigned int ...Is = {0, 1}; Ps = {clang::ast_matchers::internal::BindableMatcher<clang::Stmt>, clang::ast_matchers::internal::Matcher<clang::Decl>}; std::index_sequence<Idx ...> = std::integer_sequence<long unsigned int, 0, 1>]’:
/root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchersInternal.h:1364:30:   required from ‘clang::ast_matchers::internal::VariadicOperatorMatcher<Ps>::operator clang::ast_matchers::internal::Matcher<From>() && [with T = clang::Expr; Ps = {clang::ast_matchers::internal::BindableMatcher<clang::Stmt>, clang::ast_matchers::internal::Matcher<clang::Decl>}]’
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp:37:45:   required from here
/root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchersInternal.h:1372:13: error: ‘clang::ast_matchers::internal::Matcher< <template-parameter-1-1> >::Matcher(const clang::ast_matchers::internal::DynTypedMatcher&) [with T = clang::Expr]’ is private within this context
 1372 |     return {Matcher<T>(std::get<Is>(Params))...};
      |             ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchersInternal.h:667:12: note: declared private here
  667 |   explicit Matcher(const DynTypedMatcher &Implementation)
      |            ^~~~~~~
ninja: build stopped: subcommand failed.


## repair steps
['Remove the erroneous line `const DeclContext *DC = Context->getEnclosingDeclContext(StmtNode);` and replace it with proper parent traversal to get the enclosing function. Use `Context->getParents(*StmtNode)` to get the parent nodes and find the nearest `FunctionDecl`.', 'Fix the matcher definition for `PointerVarFromAllocMatcher`. The matcher currently uses `anyOf` with mismatched types (a `Matcher<Stmt>` and a `Matcher<Decl>`). Change it to only match `Stmt` nodes, or restructure to avoid mixing `Stmt` and `Decl` matchers in `anyOf`.', 'Replace the `anyOf` matcher in `PointerVarFromAllocMatcher` with a single `stmt` matcher that captures both assignment and declaration patterns. Use `hasDescendant` or `has` to combine the patterns without type mismatch.', 'Update the `registerMatchers` method to use separate matchers for allocation and pointer use, avoiding the problematic `anyOf` that mixes types. Register two separate matchers: one for `PointerVarFromAllocMatcher` and one for `PointerUseMatcher`.']

## reference code snippets
Narrowing Matcher: hasAnyOperatorName
 Parameters;StringRef, ..., StringRef
 return type Matcher<BinaryOperator>
 Description: Matches operator expressions (binary or unary) that have any of the
specified names.

   hasAnyOperatorName("+", "-")
 Is equivalent to
   anyOf(hasOperatorName("+"), hasOperatorName("-"))

Node Matcher: cxxConstructExpr
 Parameters;Matcher<CXXConstructExpr>...
 return type Matcher<Stmt>
 Description: Matches constructor call expressions (including implicit ones).

Example matches string(ptr, n) and ptr within arguments of f
    (matcher = cxxConstructExpr())
  void f(const string &amp;a, const string &amp;b);
  char *ptr;
  int n;
  f(string(ptr, n), ptr);

AST Traversal Matcher: forEachArgumentWithParamType
 Parameters;Matcher<Expr> ArgMatcher, Matcher<QualType> ParamMatcher
 Return type Matcher<CallExpr>
 Description: Matches all arguments and their respective types for a CallExpr or
CXXConstructExpr. It is very similar to forEachArgumentWithParam but
it works on calls through function pointers as well.

The difference is, that function pointers do not provide access to a
ParmVarDecl, but only the QualType for each argument.

Given
  void f(int i);
  int y;
  f(y);
  void (*f_ptr)(int) = f;
  f_ptr(y);
callExpr(
  forEachArgumentWithParamType(
    declRefExpr(to(varDecl(hasName("y")))),
    qualType(isInteger()).bind("type)
))
  matches f(y) and f_ptr(y)
with declRefExpr(...)
  matching int y
and qualType(...)
  matching int

AST Traversal Matcher: hasParent
 Parameters;Matcher<*>
 Return type Matcher<*>
 Description: Matches AST nodes that have a parent that matches the provided
matcher.

Given
void f() { for (;;) { int x = 42; if (true) { int x = 43; } } }
compoundStmt(hasParent(ifStmt())) matches "{ int x = 43; }".

Usable as: Any Matcher

hasEitherOperand(...)
Finder->addMatcher(arraySubscriptExpr(hasBase(ignoringImpCasts(anyOf(AllPointerTypes, hasType(decayedType(hasDecayedType(pointerType()))))))).bind("expr"), this);
static BasesVector getParentsByGrandParent(const CXXRecordDecl &GrandParent,
                                           const CXXRecordDecl &ThisClass,
                                           const CXXMethodDecl &MemberDecl) {
  BasesVector Result;
  for (const auto &Base : ThisClass.bases()) {
    const auto *BaseDecl = Base.getType()->getAsCXXRecordDecl();
    const CXXMethodDecl *ActualMemberDecl =
        MemberDecl.getCorrespondingMethodInClass(BaseDecl);
    if (!ActualMemberDecl)
      continue;
    const Type *TypePtr = ActualMemberDecl->getThisType().getTypePtr();
    const CXXRecordDecl *RecordDeclType = TypePtr->getPointeeCXXRecordDecl();
    assert(RecordDeclType && "TypePtr is not a pointer to CXXRecordDecl!");
    if (RecordDeclType->getCanonicalDecl()->isDerivedFrom(&GrandParent))
      Result.emplace_back(RecordDeclType);
  }

  return Result;
}
if (const auto *BinOp = Result.Nodes.getNodeAs<BinaryOperator>("binary")) {
  if (areSidesBinaryConstExpressions(BinOp, Result.Context)) {
    const Expr *LhsConst = nullptr, *RhsConst = nullptr;
    BinaryOperatorKind MainOpcode, SideOpcode;
    if (!retrieveConstExprFromBothSides(BinOp, MainOpcode, SideOpcode, LhsConst, RhsConst, Result.Context))
      return;
    if (areExprsFromDifferentMacros(LhsConst, RhsConst, Result.Context) ||
        areExprsMacroAndNonMacro(LhsConst, RhsConst))
      return;
  }
  diag(BinOp->getOperatorLoc(), "both sides of operator are equivalent");
}
auto NullLiteral = implicitCastExpr(
    hasCastKind(clang::CK_NullToPointer),
    hasSourceExpression(ignoringParens(cxxNullPtrLiteralExpr())));
auto StringLikeClass = cxxRecordDecl(hasAnyName(StringLikeClassNames));
auto StringType = hasUnqualifiedDesugaredType(recordType(hasDeclaration(StringLikeClass)));
auto CharStarType = hasUnqualifiedDesugaredType(pointerType(pointee(isAnyCharacter())));
auto CharType = hasUnqualifiedDesugaredType(isCharType());
auto StringNpos = declRefExpr(to(varDecl(hasName("npos"), hasDeclContext(StringLikeClass))));
auto StringFind = cxxMemberCallExpr(callee(cxxMethodDecl(hasName("find"), parameterCountIs(2), hasParameter(0, parmVarDecl(anyOf(hasType(StringType), hasType(CharStarType), hasType(CharType)))))), on(hasType(StringType)), hasArgument(0, expr().bind("parameter_to_find")), anyOf(hasArgument(1, integerLiteral(equals(0))), hasArgument(1, cxxDefaultArgExpr())), onImplicitObjectArgument(expr().bind("string_being_searched")));
const auto PParentStmtExpr = Result.Nodes.getNodeAs<Expr>("stexpr");
const auto ParentCompStmt = Result.Nodes.getNodeAs<CompoundStmt>("parent");
const auto *ParentCond = getCondition(Result.Nodes, "parent");
const auto *ParentReturnStmt = Result.Nodes.getNodeAs<ReturnStmt>("parent");
DynTypedNodeList clang::ParentMapContext::getParents(const DynTypedNode & Node)
bool clang::BinaryOperator::isBitwiseOp() const
Stmt & clang::Stmt::operator=(Stmt &&)
UnresolvedLookupExpr * clang::UnresolvedLookupExpr::Create(const ASTContext & Context, CXXRecordDecl * NamingClass, NestedNameSpecifierLoc QualifierLoc, SourceLocation TemplateKWLoc, const DeclarationNameInfo & NameInfo, bool RequiresADL, const TemplateArgumentListInfo * Args, UnresolvedSetIterator Begin, UnresolvedSetIterator End)


# Output Formatting Requirements
**Output Format Requirements:**
- Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
- Ensure that the source code is complete and compilable.
- Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.

## **Example Output Format:**

    checker_cpp:
    ```cpp
        ....(source code)....
    ```

    checker_h:
    ```cpp
        ....(source code)....
    ```