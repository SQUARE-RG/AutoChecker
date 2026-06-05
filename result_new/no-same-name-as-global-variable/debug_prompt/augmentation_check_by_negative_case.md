针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable/no_same_name_as_global_variable_case_6.cpp增强checker
# Inputs

## rule
**Rule Description:**
It is prohibited to use local variables with the same name as global variables in the code. This rule aims to prevent program logic errors and issues with code readability caused by variable name conflicts. When a local variable has the same name as a global variable, it will shadow the global variable within its local scope, which may lead developers to accidentally modify the wrong variable or misunderstand the scope of the variable, thereby introducing hard-to-debug defects. This rule applies to all naming conflicts between local variables defined within a function (including function parameters, variables defined inside the function, and variables defined within code blocks) and any global variables. Compliant scenarios involve using different names for local and global variables, while non-compliant scenarios occur when local variables have exactly the same name as global variables. The rule checks for direct name conflicts and does not consider whether the variable types are the same.

## current checker code

checker_cpp:
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
  // Match all local variable declarations (including function parameters and
  // variables with local storage) that are inside a function definition.
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

  // Ensure the local variable node is present
  if (!LocalVar)
    return;

  // Ensure the local variable has an identifier
  if (!LocalVar->getIdentifier())
    return;

  // Get the name of the local variable
  StringRef LocalName = LocalVar->getName();

  // Obtain the translation unit declaration to iterate over all declarations
  const auto *TU = Result.Context->getTranslationUnitDecl();
  if (!TU)
    return;

  // Iterate through all declarations in the translation unit
  for (const auto *Decl : TU->decls()) {
    // Check if the declaration is a VarDecl with global storage
    const auto *GlobalVar = dyn_cast<VarDecl>(Decl);
    if (!GlobalVar)
      continue;

    // Ensure it is a global variable (not local, not parameter, not inside a function)
    if (GlobalVar->isLocalVarDeclOrParm())
      continue;

    // Ensure the global variable has an identifier
    if (!GlobalVar->getIdentifier())
      continue;

    // Check if the names match
    if (GlobalVar->getName() == LocalName) {
      diag(LocalVar->getLocation(),
           "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]");
      // Only report once per local variable
      break;
    }
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
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

## passed test cases code

```cpp
#include <stdio.h>

int total_records = 0;     // 全局变量
float average_score = 0.0f; // 全局变量

void process_records(int record_count) {  // 符合：参数与全局变量不同名
    int processed = 0;  // 符合：局部变量与全局变量不同名
    for (processed = 0; processed < record_count; processed++) {
        total_records++;
    }
    printf("Processed %d records, total: %d\n", processed, total_records);
}

void calculate_average(float sum, int count) {  // 符合：参数与全局变量不同名
    if (count > 0) {
        average_score = sum / count;
    }
    printf("Average: %.2f\n", average_score);
}

int main(void) {
    process_records(5);
    calculate_average(45.5f, 5);
    return 0;
}
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
#include <stdio.h>

int total_count = 0;  // 全局变量

void add_to_count(int increment) {  // 符合：参数与全局变量不同名
    total_count += increment;
    printf("After adding %d: %d\n", increment, total_count);
}

int main(void) {
    add_to_count(5);
    add_to_count(3);
    return 0;
}
#include <stdio.h>

int max_capacity = 1000;  // 全局变量

struct Storage {
    int current_size;
    
    void resize(int new_size) {  // 符合：参数与全局变量不同名
        if (new_size > max_capacity) {
            current_size = max_capacity;
        } else {
            current_size = new_size;
        }
        printf("Resized to: %d (max: %d)\n", current_size, max_capacity);
    }
};

int main(void) {
    struct Storage s;
    s.resize(500);
    return 0;
}
#include <stdio.h>

int g_max_size = 100;  // 全局变量使用g_前缀

void calculate_size(void) {
    int local_size = 50;  // 符合：使用不同的命名约定
    if (local_size > g_max_size) {
        local_size = g_max_size;
    }
    printf("Calculated size: %d\n", local_size);
}

int main(void) {
    calculate_size();
    return 0;
}
#include <stdio.h>

int value = 100;  // 全局变量

void process_value(int value) {  // 违反：函数参数与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Parameter value: %d\n", value);
}

int main(void) {
    process_value(50);
    printf("Global value: %d\n", value);
    return 0;
}
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
#include <stdio.h>

int data = 10;
float result = 3.14f;  // 全局变量

void test_multiple_shadowing(void) {
    int data = 20;      // 违反：第一个局部变量与全局变量同名
    float result = 2.71f;  // 违反：第二个局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local data: %d, result: %.2f\n", data, result);
}

int main(void) {
    test_multiple_shadowing();
    printf("Global data: %d, result: %.2f\n", data, result);
    return 0;
}
#include <stdio.h>

int* global_ptr = NULL;  // 全局指针变量

void use_local_pointer(void) {
    int value = 42;
    int* local_ptr = &value;  // 符合：局部指针与全局指针不同名
    printf("Local pointer value: %d\n", *local_ptr);
    
    if (global_ptr != NULL) {
        printf("Global pointer value: %d\n", *global_ptr);
    }
}

int main(void) {
    int x = 100;
    global_ptr = &x;
    use_local_pointer();
    return 0;
}
#include <stdio.h>

int numbers[3] = {1, 2, 3};  // 全局数组

void test_array_shadowing(void) {
    int numbers[2] = {4, 5};  // 违反：局部数组与全局数组同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local array: %d, %d\n", numbers[0], numbers[1]);
}

int main(void) {
    test_array_shadowing();
    printf("Global array: %d, %d, %d\n", numbers[0], numbers[1], numbers[2]);
    return 0;
}
#include <stdio.h>

int global_data[5] = {1, 2, 3, 4, 5};  // 全局数组

void process_data(void) {
    int local_buffer[3] = {10, 20, 30};  // 符合：局部数组与全局数组不同名
    for (int i = 0; i < 3; i++) {
        printf("Local[%d] = %d, Global[%d] = %d\n", 
               i, local_buffer[i], i, global_data[i]);
    }
}

int main(void) {
    process_data();
    return 0;
}
#include <stdio.h>

int counter = 0;  // 全局变量

void test_basic_shadowing(void) {
    int counter = 5;  // 违反：局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local counter: %d\n", counter);
}

int main(void) {
    test_basic_shadowing();
    printf("Global counter: %d\n", counter);
    return 0;
}
#include <stdio.h>

int depth = 0;      // 全局变量
int max_depth = 10; // 全局变量

void recursive_function(int current_level) {  // 符合：参数与全局变量不同名
    if (current_level >= max_depth) {
        return;
    }
    
    int local_depth = current_level + 1;  // 符合：局部变量与全局变量不同名
    printf("Current level: %d, Local depth: %d, Global depth: %d\n", 
           current_level, local_depth, depth);
    
    if (local_depth < max_depth) {
        recursive_function(local_depth);
    }
}

int main(void) {
    depth = 0;
    recursive_function(0);
    return 0;
}
#include <stdio.h>

int index = 0;  // 全局变量

void test_block_shadowing(void) {
    for (int i = 0; i < 3; i++) {
        int index = i;  // 违反：代码块内局部变量与全局变量同名
        // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
        printf("Block index: %d\n", index);
    }
    printf("Global index: %d\n", index);
}

int main(void) {
    test_block_shadowing();
    return 0;
}
#include <stdio.h>

int the_global_var = 0;  // 全局变量

void foo(void) {
    int local_var = 0;  // 符合：局部变量与全局变量不同名
    local_var = 5;
    the_global_var = 10;
    printf("Local: %d, Global: %d\n", local_var, the_global_var);
}

int main(void) {
    foo();
    return 0;
}
#include <stdio.h>

int global_counter = 0;  // 全局变量

void test_proper_naming(void) {
    int local_counter = 5;  // 符合：局部变量与全局变量不同名
    printf("Local counter: %d\n", local_counter);
    printf("Global counter: %d\n", global_counter);
}

int main(void) {
    test_proper_naming();
    return 0;
}
#include <stdio.h>

int size = 100;  // 全局变量

struct Container {
    int capacity;
    
    void set_capacity(int new_capacity) {
        int size = new_capacity;  // 违反：成员函数内局部变量与全局变量同名
        // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
        capacity = size;
    }
};

int main(void) {
    struct Container c;
    c.set_capacity(200);
    printf("Global size: %d\n", size);
    return 0;
}
#include <stdio.h>

int the_global_var = 0;  // 全局变量

void foo(void) {
    int the_global_var = 0;  // 违反：局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    the_global_var = 5;
    printf("Local: %d\n", the_global_var);
}

int main(void) {
    foo();
    printf("Global: %d\n", the_global_var);
    return 0;
}
#include <stdio.h>

int index_global = 0;  // 全局变量

void test_block_proper(void) {
    for (int i = 0; i < 3; i++) {  // 符合：循环变量与全局变量不同名
        int item_index = i;  // 符合：块内变量与全局变量不同名
        printf("Item %d at index %d\n", i, item_index);
    }
    printf("Global index: %d\n", index_global);
}

int main(void) {
    test_block_proper();
    return 0;
}
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
#include <stdio.h>

int count = 0;  // 全局变量

void test_static_shadowing(void) {
    static int count = 0;  // 违反：静态局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    count++;
    printf("Static count: %d\n", count);
}

int main(void) {
    test_static_shadowing();
    printf("Global count: %d\n", count);
    return 0;
}
```

### ast of  failed test cases
TranslationUnitDecl 0x560bcde5b1c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x560bcdf21198 <line:12:1, line:16:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x560bcdf21470 <col:16, line:16:1>
    |-CallExpr 0x560bcdf212f0 <line:13:5, col:27> 'void'
    | `-ImplicitCastExpr 0x560bcdf212d8 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x560bcdf21288 <col:5> 'void ()' lvalue Function 0x560bcdf20cd8 'test_static_shadowing' 'void ()'
    |-CallExpr 0x560bcdf213e0 <line:14:5, col:39> 'int'
    | |-ImplicitCastExpr 0x560bcdf213c8 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x560bcdf213a8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x560bcdefd7e8 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x560bcdf21410 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x560bcdf21358 <col:12> 'const char[18]' lvalue "Global count: %d\n"
    | `-ImplicitCastExpr 0x560bcdf21428 <col:34> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x560bcdf21388 <col:34> 'int' lvalue Var 0x560bcdf20b30 'count' 'int'
    `-ReturnStmt 0x560bcdf21460 <line:15:5, col:12>
      `-IntegerLiteral 0x560bcdf21440 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match all local variable declarations (including function parameters and variables with local storage) that are inside a function definition
2. Use anyOf(parmVarDecl(), varDecl(hasLocalStorage())) to capture both parameter variables and local variables
3. Use hasAncestor(functionDecl(isDefinition())) to ensure the variable is inside a function definition
4. Bind the matched local variable declaration as 'localVar'
**logic for check**:
1. Get the matched local variable node from the result using 'localVar' binding
2. If the local variable node is null, return immediately
3. If the local variable does not have an identifier, return immediately
4. Get the name of the local variable as a string
5. Get the translation unit declaration from the AST context
6. If the translation unit is null, return immediately
7. Iterate through all declarations in the translation unit
8. For each declaration, check if it is a VarDecl
9. If it is not a VarDecl, skip to the next declaration
10. If the VarDecl is a local variable or parameter (isLocalVarDeclOrParm()), skip it
11. If the VarDecl does not have an identifier, skip it
12. Compare the global variable's name with the local variable's name
13. If the names match, emit a diagnostic at the local variable's location with the appropriate error message
14. After reporting, break out of the loop to avoid duplicate reports for the same local variable


## reference astMatchers
Narrowing Matcher: isStaticStorageClass
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches variable/function declarations that have "static" storage
class specifier ("static" keyword) written in the source.

Given:
  static void f() {}
  static int i = 0;
  extern int j;
  int k;
functionDecl(isStaticStorageClass())
  matches the function declaration f.
varDecl(isStaticStorageClass())
  matches the variable declaration i.

Narrowing Matcher: isStaticStorageClass
 Parameters;
 return type Matcher<FunctionDecl>
 Description: Matches variable/function declarations that have "static" storage
class specifier ("static" keyword) written in the source.

Given:
  static void f() {}
  static int i = 0;
  extern int j;
  int k;
functionDecl(isStaticStorageClass())
  matches the function declaration f.
varDecl(isStaticStorageClass())
  matches the variable declaration i.

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

functionDecl(hasBody(compoundStmt(forEachDescendant(declStmt(containsAnyDeclaration(varDecl(isLocal(), hasInitializer(anything()), unless(anyOf(hasType(isConstQualified()), hasType(references(isConstQualified())), anyOf(hasType(hasCanonicalType(templateTypeParmType())), hasType(substTemplateTypeParmType()), hasType(isDependentType()), hasType(referenceType(pointee(hasCanonicalType(templateTypeParmType())))), hasType(referenceType(pointee(substTemplateTypeParmType())))), hasInitializer(isInstantiationDependent()), varDecl(anyOf(hasType(autoType()), hasType(referenceType(pointee(autoType()))), hasType(pointerType(pointee(autoType()))))), hasType(referenceType(anyOf(rValueReferenceType(), unless(isSpelledAsLValue())))), hasType(hasCanonicalType(referenceType(pointee(functionType())))), hasType(cxxRecordDecl(isLambda())), isImplicit())).bind("local-value")), unless(has(decompositionDecl()))).bind("decl-stmt"))).bind("scope")).bind("function-decl")
anyOf(functionDecl(isDefinition(), unless(isDeleted())),
      varDecl(isDefinition()))
namedDecl(anyOf(functionDecl(isDefinition(), isStaticStorageClass()), varDecl(isDefinition(), isStaticStorageClass())))


## reference code snippets
const auto *OuterIf = Result.Nodes.getNodeAs<IfStmt>(OuterIfStr);
const auto *InnerIf = Result.Nodes.getNodeAs<IfStmt>(InnerIfStr);
const auto *CondVar = Result.Nodes.getNodeAs<VarDecl>(CondVarStr);
const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>(FuncStr);

const DeclRefExpr *OuterIfVar, *InnerIfVar;
if (const auto *Inner = Result.Nodes.getNodeAs<DeclRefExpr>(InnerIfVar1Str))
  InnerIfVar = Inner;
else
  InnerIfVar = Result.Nodes.getNodeAs<DeclRefExpr>(InnerIfVar2Str);
if (const auto *Outer = Result.Nodes.getNodeAs<DeclRefExpr>(OuterIfVar1Str))
  OuterIfVar = Outer;
else
  OuterIfVar = Result.Nodes.getNodeAs<DeclRefExpr>(OuterIfVar2Str);
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
if (const auto *DeclRef = dyn_cast<DeclRefExpr>(PtrInputExpr->IgnoreParenImpCasts()))
  if (const auto *Var = dyn_cast<VarDecl>(DeclRef->getDecl()))
    if (const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>("parent_function"))
      if (FindAssignToVarBefore{Var, DeclRef, SM}.Visit(Func->getBody()))
        return;
DeclContext * clang::TranslationUnitDecl::castToDeclContext(const TranslationUnitDecl * D)
const TranslationUnitDecl * clang::Decl::getTranslationUnitDecl() const
const DeclRefExpr * clang::OMPCanonicalLoop::getLoopVarRef() const

