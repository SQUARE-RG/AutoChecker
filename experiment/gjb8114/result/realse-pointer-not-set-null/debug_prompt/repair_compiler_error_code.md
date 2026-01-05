第1轮生成的checker编译失败，开始第1次重试
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
//===--- RealsePointerNotSetNullCheck.cpp - clang-tidy --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "RealsePointerNotSetNullCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  // Match free() calls
  auto FreeCallMatcher = callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("freeCall");

  // Match delete expressions
  auto DeleteExprMatcher = cxxDeleteExpr(
      has(expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("deleteExpr");

  // Match realloc() calls
  auto ReallocCallMatcher = callExpr(
      callee(functionDecl(hasName("realloc"))),
      hasArgument(0, expr().bind("reallocPtr")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("reallocCall");

  Finder->addMatcher(
      traverse(TK_AsIs, FreeCallMatcher),
      this);
  Finder->addMatcher(
      traverse(TK_AsIs, DeleteExprMatcher),
      this);
  Finder->addMatcher(
      traverse(TK_AsIs, ReallocCallMatcher),
      this);
}

void RealsePointerNotSetNullCheck::check(const MatchFinder::MatchResult &Result) {
  const ASTContext *Ctx = Result.Context;
  const SourceManager *SM = &Ctx->getSourceManager();

  if (const auto *FreeCall = Result.Nodes.getNodeAs<CallExpr>("freeCall")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!FreeCall || !FreedPtr || !DeallocStmt || 
        !SM->isInMainFile(FreeCall->getBeginLoc()))
      return;
    checkDeallocation(FreeCall, FreedPtr, DeallocStmt, Result);
  }

  if (const auto *DeleteExpr = Result.Nodes.getNodeAs<CXXDeleteExpr>("deleteExpr")) {
    const auto *FreedPtr = Result.Nodes.getNodeAs<Expr>("freedPointer");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!DeleteExpr || !FreedPtr || !DeallocStmt ||
        !SM->isInMainFile(DeleteExpr->getBeginLoc()))
      return;
    checkDeallocation(DeleteExpr, FreedPtr, DeallocStmt, Result);
  }

  if (const auto *ReallocCall = Result.Nodes.getNodeAs<CallExpr>("reallocCall")) {
    const auto *ReallocPtr = Result.Nodes.getNodeAs<Expr>("reallocPtr");
    const auto *DeallocStmt = Result.Nodes.getNodeAs<Stmt>("deallocStmt");
    if (!ReallocCall || !ReallocPtr || !DeallocStmt ||
        !SM->isInMainFile(ReallocCall->getBeginLoc()))
      return;
    checkReallocation(ReallocCall, ReallocPtr, DeallocStmt, Result);
  }
}

void RealsePointerNotSetNullCheck::checkDeallocation(
    const Stmt *DeallocStmt, const Expr *FreedPtr, const Stmt *ParentStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  
  // Extract the pointer declaration
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  // Find the enclosing compound statement
  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
    if (!Parents.empty()) {
      ParentCS = Parents[0].get<CompoundStmt>();
    }
  }
  if (!ParentCS) return;

  bool FoundNullAssignment = false;
  bool InSameScope = false;
  bool ControlFlowBreak = false;

  // Scan statements after the deallocation
  for (const auto *S : ParentCS->body()) {
    if (S == DeallocStmt) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    // Check for assignment to null
    if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
      if (BO->getOpcode() == BO_Assign) {
        const Expr *LHS = BO->getLHS()->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = BO->getRHS()->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            // Assignment to non-null value, treat as control flow break
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    // Check for C++ operator= assignment to null
    if (const auto *CE = dyn_cast<CXXOperatorCallExpr>(S)) {
      if (CE->getOperator() == OO_Equal && CE->getNumArgs() == 2) {
        const Expr *LHS = CE->getArg(0)->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = CE->getArg(1)->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    // Check for control flow statements that break the sequence
    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S) ||
        isa<GotoStmt>(S) || isa<BreakStmt>(S) || isa<ContinueStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

  // Report violation if no null assignment found and no control flow break
  if (!FoundNullAssignment && !ControlFlowBreak) {
    diag(DeallocStmt->getBeginLoc(), 
         "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]")
        << DeallocStmt->getSourceRange();
  }
}

void RealsePointerNotSetNullCheck::checkReallocation(
    const CallExpr *ReallocCall, const Expr *ReallocPtr, const Stmt *ParentStmt,
    const ast_matchers::MatchFinder::MatchResult &Result) {
  
  const ASTContext *Ctx = Result.Context;
  
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(ReallocPtr->IgnoreParenCasts())) {
    PtrDecl = ME->getMemberDecl();
  }
  
  if (!PtrDecl) return;

  const CompoundStmt *ParentCS = dyn_cast<CompoundStmt>(ParentStmt);
  if (!ParentCS) {
    DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
    if (!Parents.empty()) {
      ParentCS = Parents[0].get<CompoundStmt>();
    }
  }
  if (!ParentCS) return;

  bool FoundNullAssignment = false;
  bool InSameScope = false;
  bool ControlFlowBreak = false;

  for (const auto *S : ParentCS->body()) {
    if (S == ReallocCall) {
      InSameScope = true;
      continue;
    }

    if (!InSameScope) continue;

    if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
      if (BO->getOpcode() == BO_Assign) {
        const Expr *LHS = BO->getLHS()->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = BO->getRHS()->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (const auto *CE = dyn_cast<CXXOperatorCallExpr>(S)) {
      if (CE->getOperator() == OO_Equal && CE->getNumArgs() == 2) {
        const Expr *LHS = CE->getArg(0)->IgnoreParenCasts();
        const ValueDecl *LHSDecl = nullptr;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          LHSDecl = DRE->getDecl();
        } else if (const auto *ME = dyn_cast<MemberExpr>(LHS)) {
          LHSDecl = ME->getMemberDecl();
        }
        if (LHSDecl && LHSDecl->getCanonicalDecl() == PtrDecl->getCanonicalDecl()) {
          const Expr *RHS = CE->getArg(1)->IgnoreParenCasts();
          ASTContext &NonConstCtx = const_cast<ASTContext&>(*Ctx);
          if (RHS->isNullPointerConstant(NonConstCtx, Expr::NPC_ValueDependentIsNotNull)) {
            FoundNullAssignment = true;
            break;
          } else {
            ControlFlowBreak = true;
            break;
          }
        }
      }
    }

    if (isa<IfStmt>(S) || isa<ForStmt>(S) || isa<WhileStmt>(S) || 
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S) ||
        isa<GotoStmt>(S) || isa<BreakStmt>(S) || isa<ContinueStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

  if (!FoundNullAssignment && !ControlFlowBreak) {
    diag(ReallocCall->getBeginLoc(),
         "realloc后原始指针应置空 [gjb8114-r-1-3-6]")
        << ReallocCall->getSourceRange();
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- RealsePointerNotSetNullCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Prohibition of Failing to Set Pointers to Null After Release.
/// This rule mandates that after a pointer variable is freed using free() 
/// (in C) or delete/delete[] (in C++), it must be immediately set to a null value.
/// In C, NULL should be used, while in C++, nullptr is recommended (though NULL is acceptable).
/// The nullification must occur within the same scope as the deallocation, 
/// without being split across conditional branches.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/realse-pointer-not-set-null.html
class RealsePointerNotSetNullCheck : public ClangTidyCheck {
public:
  RealsePointerNotSetNullCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;

private:
  void checkDeallocation(const Stmt *DeallocStmt, const Expr *FreedPtr,
                         const Stmt *ParentStmt,
                         const ast_matchers::MatchFinder::MatchResult &Result);
  void checkReallocation(const CallExpr *ReallocCall, const Expr *ReallocPtr,
                         const Stmt *ParentStmt,
                         const ast_matchers::MatchFinder::MatchResult &Result);
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
```
## compiler error info
[1/7] Building CXX object tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/UcasSaatTidyModule.cpp.o
[2/7] Building CXX object tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/RealsePointerNotSetNullCheck.cpp.o
FAILED: tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/RealsePointerNotSetNullCheck.cpp.o 
ccache /usr/bin/c++ -DGTEST_HAS_RTTI=0 -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS -I/root/code_check/llvm-project/build/tools/clang/tools/extra/clang-tidy/ucassaat -I/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat -I/root/code_check/llvm-project/build/tools/clang/tools/extra/clang-tidy -I/root/code_check/llvm-project/clang/include -I/root/code_check/llvm-project/build/tools/clang/include -I/root/code_check/llvm-project/build/include -I/root/code_check/llvm-project/llvm/include -fPIC -fno-semantic-interposition -fvisibility-inlines-hidden -Werror=date-time -fno-lifetime-dse -Wall -Wextra -Wno-unused-parameter -Wwrite-strings -Wcast-qual -Wno-missing-field-initializers -pedantic -Wno-long-long -Wimplicit-fallthrough -Wno-maybe-uninitialized -Wno-nonnull -Wno-class-memaccess -Wno-redundant-move -Wno-pessimizing-move -Wno-noexcept-type -Wdelete-non-virtual-dtor -Wsuggest-override -Wno-comment -Wno-misleading-indentation -Wctad-maybe-unsupported -fdiagnostics-color -ffunction-sections -fdata-sections -fno-common -Woverloaded-virtual -fno-strict-aliasing -O2 -g -DNDEBUG  -fno-exceptions -funwind-tables -fno-rtti -gsplit-dwarf -std=c++17 -MD -MT tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/RealsePointerNotSetNullCheck.cpp.o -MF tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/RealsePointerNotSetNullCheck.cpp.o.d -o tools/clang/tools/extra/clang-tidy/ucassaat/CMakeFiles/obj.clangTidyUcasSaatModule.dir/RealsePointerNotSetNullCheck.cpp.o -c /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp: In member function ‘void clang::tidy::ucassaat::RealsePointerNotSetNullCheck::checkDeallocation(const clang::Stmt*, const clang::Expr*, const clang::Stmt*, const clang::ast_matchers::MatchFinder::MatchResult&)’:
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp:101:47: error: passing ‘const clang::ASTContext’ as ‘this’ argument discards qualifiers [-fpermissive]
  101 |     DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
      |                                ~~~~~~~~~~~~~~~^~~~~~~~~~~~~
In file included from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchers.h:63,
                 from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchFinder.h:43,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/../ClangTidyCheck.h:14,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.h:12,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp:9:
/root/code_check/llvm-project/clang/include/clang/AST/ParentMapContext.h:131:25: note:   in call to ‘clang::DynTypedNodeList clang::ASTContext::getParents(const NodeT&) [with NodeT = clang::Stmt]’
  131 | inline DynTypedNodeList ASTContext::getParents(const NodeT &Node) {
      |                         ^~~~~~~~~~
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp: In member function ‘void clang::tidy::ucassaat::RealsePointerNotSetNullCheck::checkReallocation(const clang::CallExpr*, const clang::Expr*, const clang::Stmt*, const clang::ast_matchers::MatchFinder::MatchResult&)’:
/root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp:204:47: error: passing ‘const clang::ASTContext’ as ‘this’ argument discards qualifiers [-fpermissive]
  204 |     DynTypedNodeList Parents = Ctx->getParents(*ParentStmt);
      |                                ~~~~~~~~~~~~~~~^~~~~~~~~~~~~
In file included from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchers.h:63,
                 from /root/code_check/llvm-project/clang/include/clang/ASTMatchers/ASTMatchFinder.h:43,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/../ClangTidyCheck.h:14,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.h:12,
                 from /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp:9:
/root/code_check/llvm-project/clang/include/clang/AST/ParentMapContext.h:131:25: note:   in call to ‘clang::DynTypedNodeList clang::ASTContext::getParents(const NodeT&) [with NodeT = clang::Stmt]’
  131 | inline DynTypedNodeList ASTContext::getParents(const NodeT &Node) {
      |                         ^~~~~~~~~~
ninja: build stopped: subcommand failed.


## repair steps
1. The compilation error occurs because the code calls a non-const method `getParents` on a const pointer `Ctx` (const ASTContext*). The method `ASTContext::getParents` is not marked as const, so it cannot be called on a const object.
2. To fix this, we need to obtain a non-const ASTContext reference. The `MatchResult` provides a non-const `ASTContext&` via `Result.Context` (which is actually a pointer to a non-const ASTContext). However, in the code, `Ctx` is declared as `const ASTContext*`. Change the declaration to `ASTContext*` (non-const) in both `checkDeallocation` and `checkReallocation` functions.
3. Specifically, in `checkDeallocation` and `checkReallocation`, replace `const ASTContext *Ctx = Result.Context;` with `ASTContext *Ctx = Result.Context;`. This matches the actual type of `Result.Context` (which is `ASTContext*`).
4. Alternatively, if we want to keep `Ctx` as const, we can use `Result.Context->getParents(...)` directly since `Result.Context` is non-const. But the simpler fix is to change the variable type to non-const.


## reference code snippets
AST Traversal Matcher: hasParent
 Parameters;Matcher<*>
 Return type Matcher<*>
 Description: Matches AST nodes that have a parent that matches the provided
matcher.

Given
void f() { for (;;) { int x = 42; if (true) { int x = 43; } } }
compoundStmt(hasParent(ifStmt())) matches "{ int x = 43; }".

Usable as: Any Matcher

Node Matcher: parenType
 Parameters;Matcher<ParenType>...
 return type Matcher<Type>
 Description: Matches ParenType nodes.

Given
  int (*ptr_to_array)[4];
  int *array_of_ptrs[4];

varDecl(hasType(pointsTo(parenType()))) matches ptr_to_array but not
array_of_ptrs.

AST Traversal Matcher: forEachTemplateArgument
 Parameters;clang::ast_matchers::Matcher<TemplateArgument> InnerMatcher
 Return type Matcher<ClassTemplateSpecializationDecl>
 Description: Matches classTemplateSpecialization, templateSpecializationType and
functionDecl nodes where the template argument matches the inner matcher.
This matcher may produce multiple matches.

Given
  template &lt;typename T, unsigned N, unsigned M&gt;
  struct Matrix {};

  constexpr unsigned R = 2;
  Matrix&lt;int, R * 2, R * 4&gt; M;

  template &lt;typename T, typename U&gt;
  void f(T&amp;&amp; t, U&amp;&amp; u) {}

  bool B = false;
  f(R, B);
templateSpecializationType(forEachTemplateArgument(isExpr(expr())))
  matches twice, with expr() matching 'R * 2' and 'R * 4'
functionDecl(forEachTemplateArgument(refersToType(builtinType())))
  matches the specialization f&lt;unsigned, bool&gt; twice, for 'unsigned'
  and 'bool'

traverse(TK_AsIs, arraySubscriptExpr())
AST_MATCHER_FUNCTION_P(StatementMatcher, isConstRefReturningMethodCall, std::vector<StringRef>, ExcludedContainerTypes) {
  const auto MethodDecl =
      cxxMethodDecl(returns(hasCanonicalType(matchers::isReferenceToConst())))
          .bind(MethodDeclId);
  const auto ReceiverExpr = declRefExpr(to(varDecl().bind(ObjectArgId)));
  const auto ReceiverType =
      hasCanonicalType(recordType(hasDeclaration(namedDecl(
          unless(matchers::matchesAnyListedName(ExcludedContainerTypes))))));

  return expr(anyOf(
      cxxMemberCallExpr(callee(MethodDecl), on(ReceiverExpr),
                        thisPointerType(ReceiverType)),
      cxxOperatorCallExpr(callee(MethodDecl), hasArgument(0, ReceiverExpr),
                          hasArgument(0, hasType(ReceiverType)))));
}
AST_MATCHER_P(Expr, hasParentIgnoringImpCasts, ast_matchers::internal::Matcher<Expr>, InnerMatcher) {
  const Expr *E = &Node;
  do {
    DynTypedNodeList Parents = Finder->getASTContext().getParents(*E);
    if (Parents.size() != 1)
      return false;
    E = Parents[0].get<Expr>();
    if (!E)
      return false;
  } while (isa<ImplicitCastExpr>(E));
  return InnerMatcher.matches(*E, Finder, Builder);
}
AST_POLYMORPHIC_MATCHER(isType,
                        AST_POLYMORPHIC_SUPPORTED_TYPES(ElaboratedTypeLoc,
                                                        DependentNameTypeLoc)) {
  return Node.getBeginLoc().isValid() && isNamedType(Node);
}
const ASTContext *Context = Result.Context;
const auto *DerivedRD = DerivedMD->getParent()->getDefinition();
assert(DerivedRD);
TraversalKindScope RAII(*Result.Context, TK_AsIs);
const auto *IfWithDelete = Result.Nodes.getNodeAs<IfStmt>("ifWithDelete");
const auto *Compound = Result.Nodes.getNodeAs<CompoundStmt>("compound");
const auto *InitializerList = Result.Nodes.getNodeAs<InitListExpr>("list");
const auto *ConcatenatedLiteral = Result.Nodes.getNodeAs<StringLiteral>("str");
assert(InitializerList && ConcatenatedLiteral);
unsigned int clang::GCCAsmStmt::AnalyzeAsmString(SmallVectorImpl<AsmStringPiece> & Pieces, const ASTContext & C, unsigned int & DiagOffs) const
ASTNodeKind clang::DynTypedNode::getNodeKind() const
QualType clang::ASTContext::getConstType(QualType T) const
void clang::TextNodeDumper::VisitUnresolvedLookupExpr(const UnresolvedLookupExpr * Node)


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