针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/realse_pointer_not_set_null/realse_pointer_not_set_null_case_4.cpp生成first checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.
Your task is to generate a complete, compilable clang-tidy checker by integrating:

* the rule description
* the test case code
* the AST information
* the reference logic steps
* the reference ASTMatchers
* the reference API usage
* and the checker template code

Your output must fully implement the new checker by modifying the provided template without altering namespaces.

# Inputs

## rule
**Rule Description:**
Prohibition of Failing to Set Pointers to Null After Release.This rule mandates that after a pointer variable is freed using free() (in C) or delete/delete[] (in C++), it must be immediately set to a null value. In C, NULL should be used, while in C++, nullptr is recommended (though NULL is acceptable). The nullification must occur within the same scope as the deallocation, without being split across conditional branches. Even if a pointer is about to go out of scope, it should be set to null first to foster good programming habits. This rule applies to all pointer types, including basic type pointers, array pointers, and structure pointers. For pointers that undergo multiple allocations and deallocations, nullification is required after each release.
Scenarios that should be reported include: failing to set a pointer to null immediately after free() or delete; separating the deallocation and nullification into different code paths (e.g., conditional branches); and incorrect handling of the original pointer after realloc() (although realloc manages memory, explicitly setting the original pointer to null is considered good practice). 
 Correct practices encompass: immediate nullification after release (e.g., free(p); p = NULL;), using nullptr in C++ (e.g., delete p; p = nullptr;), and performing deallocation and nullification only after ensuring the pointer is valid through conditional checks .

## test case code
**Test Case Code:**
```cpp
#include <stdlib.h>

struct Student {
    int id;
    char name[20];
};

void test_struct_pointer(void) {
    struct Student *stu = (struct Student*)malloc(sizeof(struct Student));
    if (stu != NULL) {
        stu->id = 1001;
        free(stu);  // 违反：结构体指针释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_struct_pointer();
    return 0;
}
```

## AST
TranslationUnitDecl 0x564193d18f68 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x564193de1f08 <line:17:1, line:20:1> line:17:5 main 'int ()'
  `-CompoundStmt 0x564193de2080 <col:16, line:20:1>
    |-CallExpr 0x564193de2030 <line:18:5, col:25> 'void'
    | `-ImplicitCastExpr 0x564193de2018 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x564193de1ff8 <col:5> 'void ()' lvalue Function 0x564193e3ea68 'test_struct_pointer' 'void ()'
    `-ReturnStmt 0x564193de2070 <line:19:5, col:12>
      `-IntegerLiteral 0x564193de2050 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for calls to memory deallocation functions: `free`, `delete`, and `delete[]`. Bind the `CallExpr` (or `CXXDeleteExpr`) as 'dealloc' and the pointer argument (or operand) as 'ptr'.
2. Define a matcher for the immediate parent statement of the deallocation (e.g., `Stmt`). Bind it as 'dealloc_stmt'.
3. Define a matcher to find subsequent assignment statements where the left-hand side is the same pointer variable (bound as 'ptr') being assigned to `NULL` or `nullptr`. Bind the assignment as 'null_assign'.
4. Create a compound matcher that finds deallocation statements where there is no following null assignment to the same pointer within the same basic block/scope (i.e., no 'null_assign' node found in the immediate sibling statements after 'dealloc_stmt').
5. Optionally, create a matcher to detect cases where deallocation and null assignment are separated into different conditional branches (e.g., `free(p)` in one branch, `p = NULL` in another). This can be done by checking if 'dealloc_stmt' and a potential 'null_assign' are not within the same compound statement (i.e., they have different immediate `CompoundStmt` parents).
6. Also, match calls to `realloc` and bind the original pointer argument to check if it is not set to null afterwards, though the rule considers this a good practice recommendation.
7. Ensure the matchers are configured to work in both C and C++ language modes, handling the appropriate function names and null constants.
**logic for check**:
1. Retrieve the bound 'dealloc' node (which could be a `CallExpr` for `free`/`realloc` or a `CXXDeleteExpr` for `delete`/`delete[]`).
2. Retrieve the bound 'ptr' node (the pointer expression being freed).
3. Determine the source location of the deallocation for reporting.
4. Check if a 'null_assign' node was also bound in the match. If not, this indicates a direct violation: deallocation without immediate null assignment.
5. If a 'null_assign' node exists, verify it is in the same immediate scope (i.e., same `CompoundStmt`) and appears after the deallocation statement. If it is in a different scope or branch, emit a violation for separated deallocation and nullification.
6. For `realloc` calls, check if the original pointer (first argument) is assigned to null after the call. If not, emit a warning (though this might be a lower severity diagnostic).
7. Ensure the check does not trigger for pointers that are about to go out of scope immediately after deallocation (though the rule requires nullification even then). This can be done by checking if the deallocation is the last statement in the block before the closing brace.
8. Emit an appropriate diagnostic message indicating the pointer variable name and the deallocation function used, referencing the rule ID.


## reference astMatchers
Node Matcher: nullStmt
 Parameters;Matcher<NullStmt>...
 return type Matcher<Stmt>
 Description: Matches null statements.

  foo();;
nullStmt()
  matches the second ';'

Node Matcher: cxxDeleteExpr
 Parameters;Matcher<CXXDeleteExpr>...
 return type Matcher<Stmt>
 Description: Matches delete expressions.

Given
  delete X;
cxxDeleteExpr()
  matches 'delete X'.

Narrowing Matcher: nullPointerConstant
 Parameters;
 return type Matcher<Expr>
 Description: Matches expressions that resolve to a null pointer constant, such as
GNU's __null, C++11's nullptr, or C's NULL macro.

Given:
  void *v1 = NULL;
  void *v2 = nullptr;
  void *v3 = __null; // GNU extension
  char *cp = (char *)0;
  int *ip = 0;
  int i = 0;
expr(nullPointerConstant())
  matches the initializer for v1, v2, v3, cp, and ip. Does not match the
  initializer for i.

Node Matcher: gotoStmt
 Parameters;Matcher<GotoStmt>...
 return type Matcher<Stmt>
 Description: Matches goto statements.

Given
  goto FOO;
  FOO: bar();
gotoStmt()
  matches 'goto FOO'

cxxDeleteExpr(has(declRefExpr(to(decl(equalsBoundNode("deletedPointer")))))).bind("deleteExpr")
Finder->addMatcher(
      objcMethodDecl(isInstanceMethod(), hasName("dealloc"),
                     hasDeclContext(objcCategoryImplDecl().bind("impl")))
          .bind("dealloc"),
      this);
binaryOperator(hasOperatorName("="), hasLHS(expr().bind("ptr_result")), hasRHS(ignoringParenCasts(callExpr(callee(functionDecl(hasName("::realloc"), parameterCountIs(2), hasParameter(0, hasType(pointerType(pointee(voidType())))), hasParameter(1, hasType(isInteger()))).bind("realloc")), hasArgument(0, expr().bind("ptr_input")), hasAncestor(functionDecl().bind("parent_function"))).bind("call"))))
compoundStmt(hasParent(cxxConstructorDecl()))
auto NullLiteral = implicitCastExpr(
      hasCastKind(clang::CK_NullToPointer),
      hasSourceExpression(ignoringParens(cxxNullPtrLiteralExpr())));
Finder->addMatcher(
  cxxDestructorDecl(isDefinition(), unless(ofClass(IsUnionLikeClass)))
    .bind(SpecialFunction),
  this);
Finder->addMatcher(
  cxxConstructorDecl(
    isDefinition(), unless(ofClass(IsUnionLikeClass)),
    unless(hasParent(functionTemplateDecl())),
    anyOf(
      allOf(parameterCountIs(0),
            unless(hasAnyConstructorInitializer(isWritten())),
            unless(isVariadic()), IsPublicOrOutOfLineUntilCPP20),
      allOf(isCopyConstructor(), parameterCountIs(1))))
    .bind(SpecialFunction),
  this);
Finder->addMatcher(
  cxxMethodDecl(isDefinition(), isCopyAssignmentOperator(),
    unless(ofClass(IsUnionLikeClass)),
    unless(hasParent(functionTemplateDecl())),
    hasParameter(0, hasType(lValueReferenceType())),
    returns(qualType(hasCanonicalType(
      allOf(lValueReferenceType(pointee(type())),
            unless(matchers::isReferenceToConst()))))))
    .bind(SpecialFunction),
  this);


## reference api  
const auto *Smartptr = Result.Nodes.getNodeAs<Expr>("smart_pointer");
if (IsPtrToPtr && IsMemberExpr) {
  return;
}
bool VisitBinaryOperator(BinaryOperator *BO) {
  if (BO->isAssignmentOp())
    Check.report(BO);
  return true;
}
if (!isExprValueStored(NewExpr1, *Result.Context) &&
    !isExprValueStored(NewExpr2, *Result.Context))
  return;
diag(DeallocDecl->getLocation(), "category %0 should not implement -dealloc") << CID;
diag(Operator->getOperatorLoc(), "redundant repeated dereference of function pointer")
diag(Call->getBeginLoc(), "'%0' may be set to null if 'realloc' fails, which "
                      "may result in a leak of the original buffer")
    << CodeOfAssignedExpr << PtrInputExpr->getSourceRange()
    << PtrResultExpr->getSourceRange();
const CallExpr *Call = nullptr;
if ((Call = Result.Nodes.getNodeAs<CallExpr>("allocation")))
  /* handle allocation */;
else if ((Call = Result.Nodes.getNodeAs<CallExpr>("realloc")))
  /* handle realloc */;
else if ((Call = Result.Nodes.getNodeAs<CallExpr>("free")))
  /* handle free */;
assert(Call && "Unhandled binding in the Matcher");
bool clang::BinaryOperator::isNullPointerArithmeticExtension(ASTContext & Ctx, Opcode Opc, const Expr * LHS, const Expr * RHS)
void clang::TextNodeDumper::VisitCompoundAssignOperator(const CompoundAssignOperator * Node)
bool llvm::Matcher::insert(std::string Regexp, unsigned int LineNumber, std::string & REError)
DeclarationName clang::DeclarationName::getFromOpaquePtr(void * P)
void clang::SourceLocation::dump(const SourceManager & SM) const
StringRef clang::StoredDiagnostic::getMessage() const
void clang::ASTContext::DeallocateDeclListNode(DeclListNode * N)
bool clang::BlockDecl::canAvoidCopyToHeap() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.cpp :
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
  auto FreeCallMatcher = callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("freeCall");

  auto DeleteExprMatcher = cxxDeleteExpr(
      has(expr().bind("freedPointer")),
      hasParent(stmt().bind("deallocStmt"))
  ).bind("deleteExpr");

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
  
  const ValueDecl *PtrDecl = nullptr;
  if (const auto *DRE = dyn_cast<DeclRefExpr>(FreedPtr->IgnoreParenCasts())) {
    PtrDecl = DRE->getDecl();
  } else if (const auto *ME = dyn_cast<MemberExpr>(FreedPtr->IgnoreParenCasts())) {
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
    if (S == DeallocStmt) {
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
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
      ControlFlowBreak = true;
      break;
    }
  }

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
        isa<DoStmt>(S) || isa<SwitchStmt>(S) || isa<ReturnStmt>(S)) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/RealsePointerNotSetNullCheck.h :
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

# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
    -In the check() function, all extracted nodes must be checked for non-null and isValid() to avoid direct usage
    
## **Example Output Format:**

    checker_cpp:
    ```cpp
        ....(source code)....
    ```

    checker_h:
    ```cpp
        ....(source code)....
    ```