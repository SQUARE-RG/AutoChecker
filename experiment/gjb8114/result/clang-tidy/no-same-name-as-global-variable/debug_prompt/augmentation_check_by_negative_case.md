针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable/no_same_name_as_global_variable_case_6.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

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
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoSameNameAsGlobalVariableCheck::registerMatchers(MatchFinder *Finder) {
  // Match global variable declarations (file scope)
  auto GlobalVarMatcher = varDecl(
      hasGlobalStorage(),
      hasDeclContext(anyOf(translationUnitDecl(), namespaceDecl())),
      unless(isExternC()),
      unless(isImplicit()))
      .bind("globalVar");

  // Match local variable declarations (function/block scope)
  auto LocalVarMatcher = varDecl(
      hasLocalStorage(),
      unless(isImplicit()))
      .bind("localVar");

  // Match function parameter declarations
  auto ParamVarMatcher = parmVarDecl(
      unless(isImplicit()))
      .bind("paramVar");

  // Register all matchers
  Finder->addMatcher(GlobalVarMatcher, this);
  Finder->addMatcher(LocalVarMatcher, this);
  Finder->addMatcher(ParamVarMatcher, this);
}

void NoSameNameAsGlobalVariableCheck::check(const MatchFinder::MatchResult &Result) {
  // Collect global variables from the translation unit
  static std::vector<const VarDecl *> GlobalVars;
  
  if (const auto *GlobalVar = Result.Nodes.getNodeAs<VarDecl>("globalVar")) {
    if (GlobalVar && !GlobalVar->isInvalidDecl()) {
      // Check if we're in a system header
      if (Result.SourceManager->isInSystemHeader(GlobalVar->getLocation())) {
        return;
      }
      GlobalVars.push_back(GlobalVar);
    }
    return;
  }

  const VarDecl *LocalOrParamVar = nullptr;
  
  if (const auto *LocalVar = Result.Nodes.getNodeAs<VarDecl>("localVar")) {
    LocalOrParamVar = LocalVar;
  } else if (const auto *ParamVar = Result.Nodes.getNodeAs<ParmVarDecl>("paramVar")) {
    LocalOrParamVar = ParamVar;
  }
  
  if (!LocalOrParamVar || LocalOrParamVar->isInvalidDecl()) {
    return;
  }

  // Check if we're in a system header
  if (Result.SourceManager->isInSystemHeader(LocalOrParamVar->getLocation())) {
    return;
  }

  // Get local/parameter variable name
  std::string LocalName = LocalOrParamVar->getNameAsString();
  if (LocalName.empty()) {
    return;
  }

  // Check against all global variables
  for (const auto *GlobalVar : GlobalVars) {
    if (!GlobalVar || GlobalVar->isInvalidDecl()) {
      continue;
    }

    std::string GlobalName = GlobalVar->getNameAsString();
    if (GlobalName.empty()) {
      continue;
    }

    // Check if names match
    if (LocalName == GlobalName) {
      // Emit diagnostic
      diag(LocalOrParamVar->getLocation(), 
           "禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]")
          << LocalOrParamVar;
      break; // Only report once per local/parameter variable
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

/// It is prohibited to use local variables with the same name as global variables in the code.
/// This rule aims to prevent program logic errors and issues with code readability caused by
/// variable name conflicts. When a local variable has the same name as a global variable,
/// it will shadow the global variable within its local scope, which may lead developers to
/// accidentally modify the wrong variable or misunderstand the scope of the variable,
/// thereby introducing hard-to-debug defects.
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
TranslationUnitDecl 0x56128cc341c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x56128ccfa198 <line:12:1, line:16:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x56128ccfa470 <col:16, line:16:1>
    |-CallExpr 0x56128ccfa2f0 <line:13:5, col:27> 'void'
    | `-ImplicitCastExpr 0x56128ccfa2d8 <col:5> 'void (*)()' <FunctionToPointerDecay>
    |   `-DeclRefExpr 0x56128ccfa288 <col:5> 'void ()' lvalue Function 0x56128ccf9cd8 'test_static_shadowing' 'void ()'
    |-CallExpr 0x56128ccfa3e0 <line:14:5, col:39> 'int'
    | |-ImplicitCastExpr 0x56128ccfa3c8 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x56128ccfa3a8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x56128ccd67e8 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x56128ccfa410 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x56128ccfa358 <col:12> 'const char[18]' lvalue "Global count: %d\n"
    | `-ImplicitCastExpr 0x56128ccfa428 <col:34> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x56128ccfa388 <col:34> 'int' lvalue Var 0x56128ccf9b30 'count' 'int'
    `-ReturnStmt 0x56128ccfa460 <line:15:5, col:12>
      `-IntegerLiteral 0x56128ccfa440 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match global variable declarations at file or namespace scope using varDecl with hasGlobalStorage
2. Exclude extern C declarations and implicit declarations from global variable matching
3. Bind matched global variables with 'globalVar' identifier
4. Match local variable declarations using varDecl with hasLocalStorage
5. Exclude implicit declarations from local variable matching
6. Bind matched local variables with 'localVar' identifier
7. Match function parameter declarations using parmVarDecl
8. Exclude implicit declarations from parameter matching
9. Bind matched parameters with 'paramVar' identifier
10. Register all three matchers with the MatchFinder to capture global, local, and parameter variables
**logic for check**:
1. Maintain a static vector to collect all valid global variable declarations across the translation unit
2. When a global variable is matched, verify it's not in a system header and not an invalid declaration
3. Add valid global variables to the global collection vector for later comparison
4. When a local or parameter variable is matched, verify it's not in a system header and not an invalid declaration
5. Retrieve the name of the local/parameter variable and skip if empty
6. Iterate through all collected global variables in the global collection
7. For each global variable, retrieve its name and skip if empty
8. Compare the local/parameter variable name with each global variable name
9. If names match exactly, emit a diagnostic at the local/parameter variable location with the rule identifier
10. Break after first match to avoid duplicate diagnostics for the same local/parameter variable


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

AST Traversal Matcher: ignoringImplicit
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after any implicit AST
nodes are stripped off.

Parentheses and explicit casts are not discarded.
Given
  class C {};
  C a = C();
  C b;
  C c = b;
The matchers
   varDecl(hasInitializer(ignoringImplicit(cxxConstructExpr())))
would match the declarations for a, b, and c.
While
   varDecl(hasInitializer(cxxConstructExpr()))
only match the declarations for b and c.

AST Traversal Matcher: ignoringImpCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after any implicit casts
are stripped off.

Parentheses and explicit casts are not discarded.
Given
  int arr[5];
  int a = 0;
  char b = 0;
  const int c = a;
  int *d = arr;
  long e = (long) 0l;
The matchers
   varDecl(hasInitializer(ignoringImpCasts(integerLiteral())))
   varDecl(hasInitializer(ignoringImpCasts(declRefExpr())))
would match the declarations for a, b, c, and d, but not e.
While
   varDecl(hasInitializer(integerLiteral()))
   varDecl(hasInitializer(declRefExpr()))
only match the declarations for a.

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

Node Matcher: parmVarDecl
 Parameters;Matcher<ParmVarDecl>...
 return type Matcher<Decl>
 Description: Matches parameter variable declarations.

Given
  void f(int x);
parmVarDecl()
  matches int x.

parmVarDecl(isParameterPack())
varDecl(isLocalVarDecl())
decl(unless(isImplicit()))
Finder->addMatcher(parmVarDecl().bind("paramVar"), this);
Finder->addMatcher(LocalVarCopiedFrom(declRefExpr(
                         to(varDecl(hasLocalStorage()).bind(OldVarDeclId)))),
                     this);
hasDeclContext(anyOf(translationUnitDecl(), namespaceDecl(), recordDecl()))
varDecl(unless(isLocalVarDecl()))
Finder->addMatcher(
      varDecl(hasGlobalStorage(), unless(hasConstantDeclaration())).bind("var"),
      this);
varDecl(isExternC())


## reference code snippets  
for (const BlockDecl::Capture &CapturedVar : EscapingBlockDecl->captures()) {
  const VarDecl *Var = CapturedVar.getVariable();
  if (Var && Var->hasAttr<NoEscapeAttr>()) {
    // ... (diagnostic logic follows)
  }
}
SourceLocation Loc = Var->getLocation();
if (!Loc.isValid())
  return;
SmallVector<const FunctionDecl *, 4> Diagnose;
for (const auto &RP : Overloads) {
  for (const auto *Overload : RP.second) {
    const auto *Match =
        std::find_if(RP.second.begin(), RP.second.end(),
                     [&Overload](const FunctionDecl *FD) {
                       if (FD == Overload)
                         return false;
                       if (FD->getDeclContext() != Overload->getDeclContext())
                         return false;
                       if (!areCorrespondingOverloads(Overload, FD))
                         return false;
                       return true;
                     });

    if (Match == RP.second.end()) {
      const auto *MD = dyn_cast<CXXMethodDecl>(Overload);
      if (!MD || !hasCorrespondingOverloadInBaseClass(MD))
        Diagnose.push_back(Overload);
    }
  }
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
diag(DeclRef->getExprLoc(), "function %0 %1; '%2' should be used instead")
    << FuncDecl << getRationaleFor(FunctionName)
    << ReplacementFunctionName.value() << DeclRef->getSourceRange();
const auto *VD = Result.Nodes.getNodeAs<VarDecl>("variable");
auto Diag = diag(VD->getLocation(), "twine variables are prone to use-after-free bugs");
TUInfo->getParentFinder().gatherAncestors(*Context);
DependencyFinderASTVisitor DependencyFinder(
    &TUInfo->getParentFinder().getStmtToParentStmtMap(),
    &TUInfo->getParentFinder().getDeclToParentStmtMap(),
    &TUInfo->getReplacedVars(), Loop);
if (DependencyFinder.dependsOnInsideVariable(ContainerExpr) ||
    Descriptor.ContainerString.empty() || Usages.empty() ||
    ConfidenceLevel.getLevel() < MinConfidence)
  return;
doConversion(Context, LoopVar, getReferencedVariable(ContainerExpr), Usages,
             Finder.getAliasDecl(), Finder.aliasUseRequired(),
             Finder.aliasFromForInit(), Loop, Descriptor);
for (unsigned I = 0, E = Function->getNumParams(); I != E; ++I) {
  const ParmVarDecl *Parm = Function->getParamDecl(I);
  if (Parm->isImplicit())
    continue;
  if (!Parm->getName().empty())
    continue;
NestedNameSpecifier * clang::NestedNameSpecifier::GlobalSpecifier(const ASTContext & Context)
bool clang::EvalResult::isGlobalLValue() const
bool clang::TargetInfo::validateGlobalRegisterVariable(StringRef RegName, unsigned int RegSize, bool & HasSizeMismatch) const
bool clang::DeclarationNameInfo::containsUnexpandedParameterPack() const
const ArrayInitLoopExpr * clang::VariableConstructionContext::getArrayInitLoop() const
const APValue & clang::UnnamedGlobalConstantDecl::getValue() const
int clang::StoredDiagnostic::fixit_begin() const
void clang::PartialDiagnostic::EmitToString(DiagnosticsEngine & Diags, SmallVectorImpl<char> & Buf) const
ArrayRef<ParmVarDecl *> clang::RequiresExpr::getLocalParameters() const



# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the current checker code above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
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


You can proceed with the analysis according to the following steps:

1.  Read the provided current checker code and analyze its implementation logic.
2.  Analyze the passed test cases code to understand how the checker successfully identifies issues in the code without generating false positives.
3.  Analyze the failed test cases code to determine why the checker fails to detect the issues present in these cases.
4.  Synthesize the findings from the above analyses. When generating the new code, follow the reference logic steps, consult the reference AST matchers, and utilize the reference code snippets to produce a complete and robust checker implementation. This new checker code should be capable of detecting all issues in the test cases while avoiding false positives.
5.  Output the final code strictly adhering to the specified output format requirements.

