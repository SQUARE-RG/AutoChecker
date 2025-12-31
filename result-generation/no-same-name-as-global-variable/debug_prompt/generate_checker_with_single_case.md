针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable/no_same_name_as_global_variable_case_10.cpp生成first checker
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
It is prohibited to use local variables with the same name as global variables in the code. This rule aims to prevent program logic errors and issues with code readability caused by variable name conflicts. When a local variable has the same name as a global variable, it will shadow the global variable within its local scope, which may lead developers to accidentally modify the wrong variable or misunderstand the scope of the variable, thereby introducing hard-to-debug defects. This rule applies to all naming conflicts between local variables defined within a function (including function parameters, variables defined inside the function, and variables defined within code blocks) and any global variables. Compliant scenarios involve using different names for local and global variables, while non-compliant scenarios occur when local variables have exactly the same name as global variables. The rule checks for direct name conflicts and does not consider whether the variable types are the same.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int level = 0;  // 全局变量

void test_nested_shadowing(void) {
    int level = 1;  // 外层局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    
    if (level > 0) {
        int level = 2;  // 内层局部变量与外层局部变量同名（允许，但外层已违规）
        printf("Inner level: %d\n", level);
    }
    printf("Outer level: %d\n", level);
}

int main(void) {
    test_nested_shadowing();
    printf("Global level: %d\n", level);
    return 0;
}
```

## AST
TranslationUnitDecl 0x55aa747131c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55aa747d90b0 <line:16:1, line:20:1> line:16:5 main 'int ()'
  `-CompoundStmt 0x55aa747d9400 <col:16, line:20:1>
    |-CallExpr 0x55aa747d9200 <line:17:5, col:27> 'void'
    | `-ImplicitCastExpr 0x55aa747d91e8 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x55aa747d91a0 <col:5> 'void ()' lvalue Function 0x55aa747d8a68 'test_nested_shadowing' 'void ()'
    |-CallExpr 0x55aa747d9370 <line:18:5, col:39> 'int'
    | |-ImplicitCastExpr 0x55aa747d9358 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x55aa747d9338 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x55aa747b5578 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x55aa747d93a0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x55aa747d92e8 <col:12> 'const char[18]' lvalue "Global level: %d\n"
    | `-ImplicitCastExpr 0x55aa747d93b8 <col:34> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x55aa747d9318 <col:34> 'int' lvalue Var 0x55aa747d88c0 'level' 'int'
    `-ReturnStmt 0x55aa747d93f0 <line:19:5, col:12>
      `-IntegerLiteral 0x55aa747d93d0 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match all VarDecl nodes to capture both global and local variable declarations.
2. Filter global variable declarations by checking if they have file scope (i.e., their parent is a TranslationUnitDecl).
3. Filter local variable declarations by checking if they have function or block scope (i.e., their parent is a FunctionDecl or a CompoundStmt).
4. Bind global variable declarations with a name like 'globalVar' for later retrieval.
5. Bind local variable declarations with a name like 'localVar' for later retrieval.
6. Ensure the matcher captures parameters of function declarations as local variables as well.
7. Combine the matchers to find any local variable whose name matches a global variable name within the same translation unit.
**logic for check**:
1. Retrieve all bound global variable nodes ('globalVar') and local variable nodes ('localVar') from the match result.
2. For each local variable, get its name as a string.
3. For each global variable, get its name as a string.
4. Compare the name of the local variable with the name of each global variable.
5. If a match is found, emit a diagnostic message at the location of the local variable declaration, indicating the conflict with the global variable.
6. Ensure the diagnostic does not trigger for local variables that shadow other local variables (only global-local conflicts).
7. Exclude system header files from the check to avoid warnings in library code.


## reference astMatchers
Narrowing Matcher: hasLocalStorage
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches a variable declaration that has function scope and is a
non-static local variable.

Example matches x (matcher = varDecl(hasLocalStorage())
void f() {
  int x;
  static int y;
}
int z;

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

Narrowing Matcher: hasGlobalStorage
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches a variable declaration that does not have local storage.

Example matches y and z (matcher = varDecl(hasGlobalStorage())
void f() {
  int x;
  static int y;
}
int z;

Node Matcher: varDecl
 Parameters;Matcher<VarDecl>...
 return type Matcher<Decl>
 Description: Matches variable declarations.

Note: this does not match declarations of member variables, which are
"field" declarations in Clang parlance.

Example matches a
  int a;

functionDecl(hasBody(compoundStmt(forEachDescendant(declStmt(containsAnyDeclaration(varDecl(isLocal(), hasInitializer(anything()), unless(anyOf(hasType(isConstQualified()), hasType(references(isConstQualified())), anyOf(hasType(hasCanonicalType(templateTypeParmType())), hasType(substTemplateTypeParmType()), hasType(isDependentType()), hasType(referenceType(pointee(hasCanonicalType(templateTypeParmType())))), hasType(referenceType(pointee(substTemplateTypeParmType())))), hasInitializer(isInstantiationDependent()), varDecl(anyOf(hasType(autoType()), hasType(referenceType(pointee(autoType()))), hasType(pointerType(pointee(autoType()))))), hasType(referenceType(anyOf(rValueReferenceType(), unless(isSpelledAsLValue())))), hasType(hasCanonicalType(referenceType(pointee(functionType())))), hasType(cxxRecordDecl(isLambda())), isImplicit())).bind("local-value")), unless(has(decompositionDecl()))).bind("decl-stmt"))).bind("scope")).bind("function-decl")
varDecl(isLocalVarDecl())
functionDecl(...).bind("function_decl")
Finder->addMatcher(LocalVarCopiedFrom(anyOf(isConstRefReturningFunctionCall(),
                                              isConstRefReturningMethodCall(
                                                  ExcludedContainerTypes))),
                     this);
Finder->addMatcher(LocalVarCopiedFrom(declRefExpr(
                         to(varDecl(hasLocalStorage()).bind(OldVarDeclId)))),
                     this);
varDecl(hasGlobalStorage(), hasDeclContext(anyOf(translationUnitDecl(), namespaceDecl(), recordDecl())), unless(isConstexpr()))
AST_MATCHER(VarDecl, isGlobalStatic) {
  return Node.getStorageDuration() == SD_Static && !Node.isLocalVarDecl();
}


## reference api  
const auto *const ReferenceeDef = Referencee->getDefinition();
if (ReferenceeDef != nullptr &&
    Result.SourceManager->isBeforeInTranslationUnit(
        ReferenceeDef->getLocation(), Var->getLocation())) {
  return;
}
llvm::StringRef VarName = Lexer::getSourceText(
    CharSourceRange::getTokenRange(
        AppendCall->getImplicitObjectArgument()->getSourceRange()),
    SM, Context->getLangOpts());
const auto *Var = Result.Nodes.getNodeAs<VarDecl>("vardecl");
const auto *CtorCall = Result.Nodes.getNodeAs<Expr>("ctor_call");
if (!Var || !CtorCall)
  return;
if (Variable) {
  diag(Variable->getLocation(), "variable %0 is non-const and globally "
                              "accessible, consider making it const")
      << Variable;
}
if (isSystem(Result.Context->getSourceManager().getFileCharacteristic(
          T->getBeginLoc())))
  return;
bool clang::VarDecl::isLocalVarDecl() const
std::string clang::DeclarationName::getAsString() const
void clang::UnnamedGlobalConstantDecl::printName(llvm::raw_ostream & OS, const PrintingPolicy & Policy) const
void clang::PartialDiagnostic::EmitToString(DiagnosticsEngine & Diags, SmallVectorImpl<char> & Buf) const
bool clang::HeaderSearch::isFileMultipleIncludeGuarded(const FileEntry * File) const
bool clang::DiagnosticMapping::hasNoWarningAsError() const
ValueDecl * clang::LambdaCapture::getCapturedVar() const


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
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *MatchedDecl = Result.Nodes.getNodeAs<FunctionDecl>("x");
  if (!MatchedDecl->getIdentifier() || MatchedDecl->getName().startswith("awesome_"))
    return;
  diag(MatchedDecl->getLocation(), "function %0 is insufficiently awesome")
      << MatchedDecl
      << FixItHint::CreateInsertion(MatchedDecl->getLocation(), "awesome_");
  diag(MatchedDecl->getLocation(), "insert 'awesome'", DiagnosticIDs::Note);
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