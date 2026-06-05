针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/realse_pointer_not_set_null/realse_pointer_not_set_null_case_6.cpp生成first checker
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

void test_multiple_allocations(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 60;
        free(p);
        p = NULL;  // 第一次正确置空
        
        p = (int*)malloc(sizeof(int) * 2);  // 重新分配
        if (p != NULL) {
            p[0] = 1;
            p[1] = 2;
            free(p);  // 违反：第二次释放后未置空
            // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
        }
    }
}

int main(void) {
    test_multiple_allocations();
    return 0;
}
```

## AST
TranslationUnitDecl 0x55dd4e10cf68 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55dd4e1d5e20 <line:20:1, line:23:1> line:20:5 main 'int ()'
  `-CompoundStmt 0x55dd4e1d5f98 <col:16, line:23:1>
    |-CallExpr 0x55dd4e1d5f48 <line:21:5, col:31> 'void'
    | `-ImplicitCastExpr 0x55dd4e1d5f30 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x55dd4e1d5f10 <col:5> 'void ()' lvalue Function 0x55dd4e2324c8 'test_multiple_allocations' 'void ()'
    `-ReturnStmt 0x55dd4e1d5f88 <line:22:5, col:12>
      `-IntegerLiteral 0x55dd4e1d5f68 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match call expressions to free(), delete, or delete[] (deallocation functions) and bind them as 'dealloc_call'
2. For each deallocation call, check that it is a direct call expression (not in a macro) and the argument is a pointer expression
3. Match binary assignment operators where the left-hand side is a pointer variable and the right-hand side is NULL or nullptr, and bind the assignment expression as 'assign_null'
4. Create a matcher to find deallocation calls that are NOT followed by a null assignment in the same compound statement (block scope) by matching the deallocation call and then verifying that the next statement is not a null assignment
5. Use hasAncestor() to ensure the deallocation call is within a compound statement (block) and bind the compound statement as 'block'
6. Match deallocation calls that appear inside conditional branches (if/else) where the null assignment is in a different branch, using hasParent() to identify if the dealloc call is inside an if/else
7. Combine matchers to match: deallocation without subsequent null assignment in the same scope, deallocation and null assignment in different branches, and deallocation with no null assignment at all in the containing block
**logic for check**:
1. Retrieve the bound CallExpr ('dealloc_call') node from the match result
2. Get the argument of the deallocation call (the pointer being freed) and check it is a DeclRefExpr to a variable
3. Retrieve the bound CompoundStmt ('block') node if present, which is the containing block of the deallocation call
4. If a block is bound, iterate through the statements in the block starting from the statement after the deallocation call
5. For each subsequent statement, check if it is a binary assignment operator with the same pointer variable on the left-hand side and NULL/nullptr on the right-hand side
6. If no null assignment is found in the same block after the deallocation call, emit a diagnostic warning '禁止释放指针变量后未置空 [gjb8114-r-1-3-6]'
7. If the deallocation call is inside a conditional branch (if/else), check if the null assignment is in a different branch; if so, also emit a diagnostic
8. For the specific test case: detect that after the second free(p) in test_multiple_allocations, there is no subsequent p = NULL assignment in the same if block, and report the violation


## reference astMatchers
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

AST Traversal Matcher: hasDeclaration
 Parameters;Matcher<Decl>  InnerMatcher
 Return type Matcher<UnresolvedUsingType>
 Description: Matches a node if the declaration associated with that node
matches the given matcher.

The associated declaration is:
- for type nodes, the declaration of the underlying type
- for CallExpr, the declaration of the callee
- for MemberExpr, the declaration of the referenced member
- for CXXConstructExpr, the declaration of the constructor
- for CXXNewExpr, the declaration of the operator new
- for ObjCIvarExpr, the declaration of the ivar

For type nodes, hasDeclaration will generally match the declaration of the
sugared type. Given
  class X {};
  typedef X Y;
  Y y;
in varDecl(hasType(hasDeclaration(decl()))) the decl will match the
typedefDecl. A common use case is to match the underlying, desugared type.
This can be achieved by using the hasUnqualifiedDesugaredType matcher:
  varDecl(hasType(hasUnqualifiedDesugaredType(
      recordType(hasDeclaration(decl())))))
In this matcher, the decl will match the CXXRecordDecl of class X.

Usable as: Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1AddrLabelExpr.html">AddrLabelExpr</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1CallExpr.html">CallExpr</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1CXXConstructExpr.html">CXXConstructExpr</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1CXXNewExpr.html">CXXNewExpr</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1DeclRefExpr.html">DeclRefExpr</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1EnumType.html">EnumType</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1InjectedClassNameType.html">InjectedClassNameType</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1LabelStmt.html">LabelStmt</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1MemberExpr.html">MemberExpr</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1QualType.html">QualType</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1RecordType.html">RecordType</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1TagType.html">TagType</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1TemplateSpecializationType.html">TemplateSpecializationType</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1TemplateTypeParmType.html">TemplateTypeParmType</a>&gt;, Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1TypedefType.html">TypedefType</a>&gt;,
  Matcher&lt;<a href="https://clang.llvm.org/doxygen/classclang_1_1UnresolvedUsingType.html">UnresolvedUsingType</a>&gt;

AST Traversal Matcher: invocation
 Parameters;Matcher<*>...Matcher<*>
 Return type Matcher<*>
 Description: Matches function calls and constructor calls

Because CallExpr and CXXConstructExpr do not share a common
base class with API accessing arguments etc, AST Matchers for code
which should match both are typically duplicated. This matcher
removes the need for duplication.

Given code
struct ConstructorTakesInt
{
  ConstructorTakesInt(int i) {}
};

void callTakesInt(int i)
{
}

void doCall()
{
  callTakesInt(42);
}

void doConstruct()
{
  ConstructorTakesInt cti(42);
}

The matcher
invocation(hasArgument(0, integerLiteral(equals(42))))
matches the expression in both doCall and doConstruct

bool isReferencedOutsideOfCallExpr(const FunctionDecl &Function, ASTContext &Context) {
  auto Matches = match(declRefExpr(to(functionDecl(equalsNode(&Function))), unless(hasAncestor(callExpr()))), Context);
  return !Matches.empty();
}
const auto IsBadReturnStatement = returnStmt(unless(has(ignoringParenImpCasts(anyOf(unaryOperator(hasOperatorName("*"), hasUnaryOperand(cxxThisExpr())), cxxOperatorCallExpr(argumentCountIs(1), callee(unresolvedLookupExpr()), hasArgument(0, cxxThisExpr())), cxxOperatorCallExpr(hasOverloadedOperatorName("="), hasArgument(0, unaryOperator(hasOperatorName("*"), hasUnaryOperand(cxxThisExpr()))))))));
Finder->addMatcher(stmt(anyOf(unaryOperator(hasAnyOperatorName("++", "--")), binaryOperator(), callExpr(), returnStmt(), cxxConstructExpr())).bind("Mark"), this);


## reference api
bool isCatchVariable(const DeclRefExpr *DeclRefExpr) {
  auto *ValueDecl = DeclRefExpr->getDecl();
  if (auto *VarDecl = dyn_cast<clang::VarDecl>(ValueDecl))
    return VarDecl->isExceptionVariable();
  return false;
}
if (const auto *DRE = Result.Nodes.getNodeAs<DeclRefExpr>("used")) {
  RemoveNamedDecl(DRE->getDecl());
  return;
}
if (const auto *RetStmt = Result.Nodes.getNodeAs<ReturnStmt>("returnStmt")) {
  diag(RetStmt->getBeginLoc(), "operator=() should always return '*this'");
  return;
}
bool clang::CXXMethodDecl::isUsualDeallocationFunction(SmallVectorImpl<const FunctionDecl *> & PreventedBy) const
bool clang::FunctionDecl::isDestroyingOperatorDelete() const
QualType clang::CallExpr::getCallReturnType(const ASTContext & Ctx) const


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

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void RealsePointerNotSetNullCheck::registerMatchers(MatchFinder *Finder) {
  // Match free() calls
  Finder->addMatcher(
    callExpr(
      callee(functionDecl(hasName("free"))),
      hasArgument(0, expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );

  // Match delete expressions
  Finder->addMatcher(
    cxxDeleteExpr(
      has(expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );

  // Match delete[] expressions
  Finder->addMatcher(
    cxxDeleteExpr(
      isArray(),
      has(expr().bind("freed_pointer")),
      hasAncestor(compoundStmt().bind("parent_block"))
    ).bind("deallocation_call"),
    this
  );
}

void RealsePointerNotSetNullCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *DeallocCall = Result.Nodes.getNodeAs<Expr>("deallocation_call");
  const auto *FreedPointer = Result.Nodes.getNodeAs<Expr>("freed_pointer");
  const auto *ParentBlock = Result.Nodes.getNodeAs<CompoundStmt>("parent_block");

  if (!DeallocCall || !FreedPointer || !ParentBlock)
    return;

  // Get the source location of the deallocation call
  SourceLocation DeallocLoc = DeallocCall->getBeginLoc();
  if (DeallocLoc.isInvalid())
    return;

  // Check if the freed pointer is an lvalue (e.g., a DeclRefExpr)
  const auto *FreedDeclRef = dyn_cast<DeclRefExpr>(FreedPointer->IgnoreImpCasts());
  if (!FreedDeclRef)
    return;

  const ValueDecl *FreedVarDecl = FreedDeclRef->getDecl();
  if (!FreedVarDecl)
    return;

  // Look for a null assignment after the deallocation call in the same block
  bool FoundNullAssignment = false;

  // Iterate through statements in the block after the deallocation
  bool FoundDealloc = false;
  for (const auto *Child : ParentBlock->children()) {
    if (!FoundDealloc) {
      if (const auto *ChildStmt = dyn_cast<Stmt>(Child)) {
        if (ChildStmt == DeallocCall) {
          FoundDealloc = true;
        }
      }
      continue;
    }

    // Check if this child is a binary assignment to the freed pointer with null
    if (const auto *BinOp = dyn_cast<BinaryOperator>(Child)) {
      if (BinOp->isAssignmentOp()) {
        const Expr *LHS = BinOp->getLHS()->IgnoreImpCasts();
        if (const auto *LHSDeclRef = dyn_cast<DeclRefExpr>(LHS)) {
          if (LHSDeclRef->getDecl() == FreedVarDecl) {
            const Expr *RHS = BinOp->getRHS()->IgnoreImpCasts();
            if (RHS->isNullPointerConstant(*Result.Context, Expr::NPC_ValueDependentIsNull)) {
              FoundNullAssignment = true;
              break;
            }
          }
        }
      }
    }
  }

  if (!FoundNullAssignment) {
    diag(DeallocLoc, "禁止释放指针变量后未置空 [gjb8114-r-1-3-6]");
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

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/realse-pointer-not-set-null.html
class RealsePointerNotSetNullCheck : public ClangTidyCheck {
public:
  RealsePointerNotSetNullCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
```
