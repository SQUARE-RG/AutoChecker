针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable/no_same_name_as_global_variable_case_7.cpp生成first checker
# Inputs

## rule
**Rule Description:**
It is prohibited to use local variables with the same name as global variables in the code. This rule aims to prevent program logic errors and issues with code readability caused by variable name conflicts. When a local variable has the same name as a global variable, it will shadow the global variable within its local scope, which may lead developers to accidentally modify the wrong variable or misunderstand the scope of the variable, thereby introducing hard-to-debug defects. This rule applies to all naming conflicts between local variables defined within a function (including function parameters, variables defined inside the function, and variables defined within code blocks) and any global variables. Compliant scenarios involve using different names for local and global variables, while non-compliant scenarios occur when local variables have exactly the same name as global variables. The rule checks for direct name conflicts and does not consider whether the variable types are the same.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int* pointer = NULL;  // 全局指针变量

void test_pointer_shadowing(void) {
    int value = 5;
    int* pointer = &value;  // 违反：局部指针变量与全局指针变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local pointer value: %d\n", *pointer);
}

int main(void) {
    int x = 10;
    pointer = &x;
    test_pointer_shadowing();
    printf("Global pointer value: %d\n", *pointer);
    return 0;
}
```

## AST
TranslationUnitDecl 0x55f056bdf1c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55f056ca52c8 <line:12:1, line:18:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x55f056ca57a8 <col:16, line:18:1>
    |-DeclStmt 0x55f056ca5410 <line:13:5, col:15>
    | `-VarDecl 0x55f056ca5388 <col:5, col:13> col:9 used x 'int' cinit
    |   `-IntegerLiteral 0x55f056ca53f0 <col:13> 'int' 10
    |-BinaryOperator 0x55f056ca5480 <line:14:5, col:16> 'int *' lvalue '='
    | |-DeclRefExpr 0x55f056ca5428 <col:5> 'int *' lvalue Var 0x55f056ca4bb0 'pointer' 'int *'
    | `-UnaryOperator 0x55f056ca5468 <col:15, col:16> 'int *' prefix '&' cannot overflow
    |   `-DeclRefExpr 0x55f056ca5448 <col:16> 'int' lvalue Var 0x55f056ca5388 'x' 'int'
    |-CallExpr 0x55f056ca5550 <line:15:5, col:28> 'void'
    | `-ImplicitCastExpr 0x55f056ca5538 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x55f056ca54e8 <col:5> 'void ()' lvalue Function 0x55f056ca4d68 'test_pointer_shadowing' 'void ()'
    |-CallExpr 0x55f056ca5718 <line:16:5, col:50> 'int'
    | |-ImplicitCastExpr 0x55f056ca5700 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x55f056ca56c0 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x55f056c81838 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x55f056ca5748 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x55f056ca5638 <col:12> 'const char[26]' lvalue "Global pointer value: %d\n"
    | `-ImplicitCastExpr 0x55f056ca5760 <col:42, col:43> 'int' <LValueToRValue>
    |   `-UnaryOperator 0x55f056ca56a8 <col:42, col:43> 'int' lvalue prefix '*' cannot overflow
    |     `-ImplicitCastExpr 0x55f056ca5690 <col:43> 'int *' <LValueToRValue>
    |       `-DeclRefExpr 0x55f056ca5670 <col:43> 'int *' lvalue Var 0x55f056ca4bb0 'pointer' 'int *'
    `-ReturnStmt 0x55f056ca5798 <line:17:5, col:12>
      `-IntegerLiteral 0x55f056ca5778 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match all VarDecl nodes that are function-local variables (i.e., have a function scope or block scope), including function parameters and variables defined inside functions or code blocks
2. For each such local variable, check if there exists a global variable with the same name
3. Use the `hasAncestor` matcher to ensure the local variable is inside a function declaration (functionDecl) to avoid matching global variables themselves
4. Bind the local variable as 'localVar' for retrieval in the check callback
5. The matcher will trigger on every local variable declaration within any function or block
**logic for check**:
1. Retrieve the bound VarDecl node ('localVar') from the match result
2. Get the name of the local variable using getName()
3. Obtain the TranslationUnitDecl from the AST context to iterate over all declarations
4. Iterate through all global VarDecl nodes (those with no enclosing function or block scope) in the translation unit
5. For each global variable, compare its name with the local variable's name
6. If a name match is found, emit a diagnostic message indicating that the local variable shadows a global variable, using the location of the local variable declaration


## reference astMatchers
Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Stmt>
 Description: Matches if a node equals a previously bound node.

Matches a node if it equals the node previously bound to ID.

Given
  class X { int a; int b; };
cxxRecordDecl(
    has(fieldDecl(hasName("a"), hasType(type().bind("t")))),
    has(fieldDecl(hasName("b"), hasType(type(equalsBoundNode("t"))))))
  matches the class X, as a and b have the same type.

Note that when multiple matches are involved via forEach* matchers,
equalsBoundNodes acts as a filter.
For example:
compoundStmt(
    forEachDescendant(varDecl().bind("d")),
    forEachDescendant(declRefExpr(to(decl(equalsBoundNode("d"))))))
will trigger a match for each combination of variable declaration
and reference to that variable declaration within a compound statement.

Narrowing Matcher: isExternC
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches extern "C" function or variable declarations.

Given:
  extern "C" void f() {}
  extern "C" { void g() {} }
  void h() {}
  extern "C" int x = 1;
  extern "C" int y = 2;
  int z = 3;
functionDecl(isExternC())
  matches the declaration of f and g, but not the declaration of h.
varDecl(isExternC())
  matches the declaration of x and y, but not the declaration of z.

Narrowing Matcher: isExternC
 Parameters;
 return type Matcher<FunctionDecl>
 Description: Matches extern "C" function or variable declarations.

Given:
  extern "C" void f() {}
  extern "C" { void g() {} }
  void h() {}
  extern "C" int x = 1;
  extern "C" int y = 2;
  int z = 3;
functionDecl(isExternC())
  matches the declaration of f and g, but not the declaration of h.
varDecl(isExternC())
  matches the declaration of x and y, but not the declaration of z.

functionDecl(hasBody(compoundStmt(forEachDescendant(declStmt(containsAnyDeclaration(varDecl(isLocal(), hasInitializer(anything()), unless(anyOf(hasType(isConstQualified()), hasType(references(isConstQualified())), anyOf(hasType(hasCanonicalType(templateTypeParmType())), hasType(substTemplateTypeParmType()), hasType(isDependentType()), hasType(referenceType(pointee(hasCanonicalType(templateTypeParmType())))), hasType(referenceType(pointee(substTemplateTypeParmType())))), hasInitializer(isInstantiationDependent()), varDecl(anyOf(hasType(autoType()), hasType(referenceType(pointee(autoType()))), hasType(pointerType(pointee(autoType()))))), hasType(referenceType(anyOf(rValueReferenceType(), unless(isSpelledAsLValue())))), hasType(hasCanonicalType(referenceType(pointee(functionType())))), hasType(cxxRecordDecl(isLambda())), isImplicit())).bind("local-value")), unless(has(decompositionDecl()))).bind("decl-stmt"))).bind("scope")).bind("function-decl")
returnStmt(
              has(ignoringImplicit(handleFrom(
                  IsAHandle,
                  handleFrom(IsAHandle,
                             declRefExpr(to(varDecl(
                                 hasAutomaticStorageDuration(),
                                 anyOf(hasType(arrayType()),
                                       hasType(hasUnqualifiedDesugaredType(
                                           recordType(hasDeclaration(recordDecl(
                                               unless(IsAHandle))))))))))))),
              unless(hasAncestor(lambdaExpr())))
Finder->addMatcher(LocalVarCopiedFrom(declRefExpr(
                         to(varDecl(hasLocalStorage()).bind(OldVarDeclId)))),
                     this);


## reference api
static bool isVarThatIsPossiblyChanged(const Decl *Func, const Stmt *LoopStmt,
                                     const Stmt *Cond, ASTContext *Context) {
  if (const auto *DRE = dyn_cast<DeclRefExpr>(Cond)) {
    if (const auto *Var = dyn_cast<VarDecl>(DRE->getDecl())) {
      if (!Var->isLocalVarDeclOrParm())
        return true;

      if (Var->getType().isVolatileQualified())
        return true;

      if (!Var->getType().getTypePtr()->isIntegerType())
        return true;

      return hasPtrOrReferenceInFunc(Func, Var) ||
             isChanged(LoopStmt, Var, Context);
    }
  } else if (isa<MemberExpr, CallExpr,
                 ObjCIvarRefExpr, ObjCPropertyRefExpr, ObjCMessageExpr>(Cond)) {
    return true;
  } else if (const auto *CE = dyn_cast<CastExpr>(Cond)) {
    QualType T = CE->getType();
    while (true) {
      if (T.isVolatileQualified())
        return true;

      if (!T->isAnyPointerType() && !T->isReferenceType())
        break;

      T = T->getPointeeType();
    }
  }

  return false;
}
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
const auto *LoopVar = Nodes.getNodeAs<VarDecl>(InitVarName);
const auto *EndVar = Nodes.getNodeAs<VarDecl>(EndVarName);
const auto *EndCall = Nodes.getNodeAs<CXXMemberCallExpr>(EndCallName);
const auto *BoundExpr = Nodes.getNodeAs<Expr>(ConditionBoundName);
DeclContext * clang::TranslationUnitDecl::castToDeclContext(const TranslationUnitDecl * D)
void clang::TextNodeDumper::VisitObjCIvarDecl(const ObjCIvarDecl * D)
TranslationUnitDecl * clang::TranslationUnitDecl::castFromDeclContext(const DeclContext * DC)


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoSameNameAsGlobalVariableCheck.cpp :
```cpp
//===--- NoSameNameAsGlobalVariableCheck.cpp - clang-tidy -----------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoSameNameAsGlobalVariableCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoSameNameAsGlobalVariableCheck::registerMatchers(MatchFinder *Finder) {
  // Match all global variable declarations (file/namespace scope, global storage)
  Finder->addMatcher(
      varDecl(
          hasGlobalStorage(),
          unless(anyOf(
              parmVarDecl(),
              hasAncestor(functionDecl()),
              hasAncestor(blockDecl())
          ))
      ).bind("globalVar"),
      this
  );

  // Match all local variable declarations (function parameters, variables with local storage)
  Finder->addMatcher(
      varDecl(
          anyOf(
              parmVarDecl(),
              varDecl(hasLocalStorage())
          ),
          hasAncestor(functionDecl(isDefinition()))
      ).bind("localVar"),
      this
  );
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("localVar");
  const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("globalVar");

  // Ensure both nodes are present
  if (!LocalVar || !GlobalVar)
    return;

  // Ensure both variables have identifiers
  if (!LocalVar->getIdentifier() || !GlobalVar->getIdentifier())
    return;

  // Get the names of the variables
  StringRef LocalName = LocalVar->getName();
  StringRef GlobalName = GlobalVar->getName();

  // Check if the local variable name matches the global variable name
  if (LocalName == GlobalName) {
    diag(LocalVar->getLocation(),
         "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
  }
}

} // namespace clang::tidy::ucassaat
```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoSameNameAsGlobalVariableCheck.h :
```cpp
//===--- NoSameNameAsGlobalVariableCheck.h - clang-tidy ---------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-same-name-as-global-variable.html
class NoSameNameAsGlobalVariableCheck : public ClangTidyCheck {
public:
  NoSameNameAsGlobalVariableCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOSAMENAMEASGLOBALVARIABLECHECK_H
```
