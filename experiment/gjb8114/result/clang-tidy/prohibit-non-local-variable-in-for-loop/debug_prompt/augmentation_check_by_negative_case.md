针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop/prohibit_non_local_variable_in_for_loop_case_7.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

# Inputs

## rule
**Rule Description:**
Forbidden to use non-local variables for loop control variables. The rule requires that the control variable of a for loop must be a local variable, and non-local variables (such as global variables, static global variables, or external-scope variables) must not be used as loop control variables. This rule aims to ensure that the control variable of the loop has a clear scope and lifetime, preventing unintended modifications and logical errors in code caused by the spread of variable scope. When the control variable of a for loop is a non-local variable, the variable may be unintentionally modified outside the loop, affecting the expected behavior of the loop and reducing the maintainability and readability of the code. Compliant scenarios are for loops using local variables defined within functions or block scopes as control variables; non-compliant scenarios are for loops using any non-local variables (including global variables, static variables, or external variables) as control variables. The rule checks the scope of the control variable in the initialization part of the for loop, not the use of the variable within the loop body.

## current checker code

checker_cpp:
```cpp
//===--- ProhibitNonLocalVariableInForLoopCheck.cpp - clang-tidy ----------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ProhibitNonLocalVariableInForLoopCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void ProhibitNonLocalVariableInForLoopCheck::registerMatchers(MatchFinder *Finder) {
  // Match for statements
  auto ForLoopMatcher = forStmt(
      hasLoopInit(anyOf(
          // Case 1: Binary operator assignment (e.g., i = 0, config.start = 0)
          binaryOperator(
              isAssignmentOperator(),
              hasLHS(expr(ignoringParenImpCasts(
                  anyOf(
                      declRefExpr(to(varDecl().bind("lhs_var"))),
                      memberExpr(hasDeclaration(fieldDecl()),
                                 hasObjectExpression(ignoringParenImpCasts(
                                     declRefExpr(to(varDecl().bind("lhs_member_base")))))),
                      unaryOperator(hasOperatorName("*"),
                                    hasUnaryOperand(ignoringParenImpCasts(
                                        declRefExpr(to(varDecl().bind("lhs_ptr_var"))))))
                  )))),
          // Case 2: DeclStmt with variable declaration (e.g., int i = 0)
          declStmt(hasSingleDecl(varDecl().bind("decl_var")))
      )))
      .bind("for_loop");

  Finder->addMatcher(ForLoopMatcher, this);
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ForLoop = Result.Nodes.getNodeAs<ForStmt>("for_loop");
  if (!ForLoop || !ForLoop->getBeginLoc().isValid()) {
    return;
  }

  // Try to get the variable from different bindings
  const VarDecl *LoopVar = nullptr;
  
  // Check for direct variable reference (i = 0)
  if (const auto *LhsVar = Result.Nodes.getNodeAs<VarDecl>("lhs_var")) {
    if (!LhsVar->isInvalidDecl()) {
      LoopVar = LhsVar;
    }
  }
  
  // Check for member expression base (config.start = 0)
  if (!LoopVar) {
    if (const auto *LhsMemberBase = Result.Nodes.getNodeAs<VarDecl>("lhs_member_base")) {
      if (!LhsMemberBase->isInvalidDecl()) {
        LoopVar = LhsMemberBase;
      }
    }
  }
  
  // Check for pointer dereference (*ptr = 0)
  if (!LoopVar) {
    if (const auto *LhsPtrVar = Result.Nodes.getNodeAs<VarDecl>("lhs_ptr_var")) {
      if (!LhsPtrVar->isInvalidDecl()) {
        LoopVar = LhsPtrVar;
      }
    }
  }
  
  // Check for declared variable (int i = 0)
  if (!LoopVar) {
    if (const auto *DeclVar = Result.Nodes.getNodeAs<VarDecl>("decl_var")) {
      if (!DeclVar->isInvalidDecl()) {
        LoopVar = DeclVar;
      }
    }
  }

  if (!LoopVar) {
    return;
  }

  // Check if the variable is non-local
  bool IsNonLocal = false;
  
  // Check storage duration and linkage
  if (LoopVar->hasGlobalStorage()) {
    IsNonLocal = true;
  } else {
    // Check declaration context
    const DeclContext *DC = LoopVar->getDeclContext();
    if (!DC) {
      return;
    }
    
    // Check if context is a function or block
    bool IsInFunction = false;
    bool IsInBlock = false;
    
    while (DC) {
      if (isa<FunctionDecl>(DC)) {
        IsInFunction = true;
        break;
      }
      if (isa<BlockDecl>(DC)) {
        IsInBlock = true;
        break;
      }
      DC = DC->getParent();
    }
    
    // If not in function or block, it's non-local
    if (!IsInFunction && !IsInBlock) {
      IsNonLocal = true;
    }
  }

  if (IsNonLocal) {
    diag(ForLoop->getBeginLoc(), 
         "禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]");
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- ProhibitNonLocalVariableInForLoopCheck.h - clang-tidy --*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Forbidden to use non-local variables for loop control variables.
/// The rule requires that the control variable of a for loop must be a local
/// variable, and non-local variables (such as global variables, static global
/// variables, or external-scope variables) must not be used as loop control
/// variables. This rule aims to ensure that the control variable of the loop
/// has a clear scope and lifetime, preventing unintended modifications and
/// logical errors in code caused by the spread of variable scope.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/prohibit-non-local-variable-in-for-loop.html
class ProhibitNonLocalVariableInForLoopCheck : public ClangTidyCheck {
public:
  ProhibitNonLocalVariableInForLoopCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_PROHIBITNONLOCALVARIABLEINFORLOOPCHECK_H
```

## passed test cases code

```cpp
#include <stdio.h>

void process_range(int start, int end) {
    for (int i = start; i < end; i++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
}

int main(void) {
    process_range(0, 5);
    return 0;
}
#include <stdio.h>

int i = 0;  // 全局变量

void foo(void) {
    for (i = 0; i < 7; ++i) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", i);
    }
}

int main(void) {
    foo();
    return 0;
}
#include <stdio.h>

int file_scope_var = 0;  // 文件作用域变量

void process_data(void) {
    for (file_scope_var = 0; file_scope_var < 5; file_scope_var++) {  // 违反：使用文件作用域变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", file_scope_var);
    }
}

int main(void) {
    process_data();
    return 0;
}
#include <stdio.h>

int main(void) {
    for (int i = 0; i < 2; i++) {  // 符合：外层循环使用局部变量
        for (int j = 0; j < 3; j++) {  // 符合：内层循环使用局部变量
            printf("(%d,%d) ", i, j);
        }
        printf("\n");
    }
    return 0;
}
#include <stdio.h>

int global_index = 0;  // 全局索引变量
int data[5] = {10, 20, 30, 40, 50};

int main(void) {
    for (global_index = 0; global_index < 5; global_index++) {  // 违反：使用全局变量作为数组遍历的控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", data[global_index]);
    }
    return 0;
}
#include <stdio.h>

void foo(void) {
    for (int i = 0; i < 7; ++i) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
}

int main(void) {
    foo();
    return 0;
}
#include <stdio.h>

int global_i = 0;  // 全局变量

int main(void) {
    for (global_i = 0; global_i < 5; global_i++) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", global_i);
    }
    return 0;
}
#include <stdio.h>

int shared_counter = 0;  // 全局变量

void func1(void) {
    for (shared_counter = 0; shared_counter < 2; shared_counter++) {  // 违反：多个函数共享的全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("Func1: %d\n", shared_counter);
    }
}

int main(void) {
    func1();
    return 0;
}
#include <stdio.h>

int main(void) {
    {  // 开始一个块作用域
        for (int j = 0; j < 3; j++) {  // 符合：在块作用域内使用局部变量
            printf("%d ", j);
        }
    }
    // j 在这里不可访问，符合局部变量规则
    return 0;
}
#include <stdio.h>

void iterate_values(void) {
    int local_counter;  // 局部变量
    for (local_counter = 0; local_counter < 5; local_counter++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", local_counter);
    }
}

int main(void) {
    iterate_values();
    return 0;
}
#include <stdio.h>

int outer_var = 0;  // 全局变量

void outer_function(void) {
    for (outer_var = 0; outer_var < 3; outer_var++) {  // 违反：外层函数使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("Outer: %d\n", outer_var);
    }
}

int main(void) {
    outer_function();
    return 0;
}
#include <stdio.h>

extern int external_var;  // 外部声明变量
int external_var = 0;     // 实际定义

int main(void) {
    for (external_var = 0; external_var < 4; external_var++) {  // 违反：使用外部变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", external_var);
    }
    return 0;
}
#include <stdio.h>

static int static_counter = 0;  // 静态全局变量

int main(void) {
    for (static_counter = 0; static_counter < 3; static_counter++) {  // 违反：使用静态全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", static_counter);
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    for (int i = 0, j = 10; i < 5; i++, j--) {  // 符合：使用多个局部变量作为循环控制
        printf("i=%d, j=%d\n", i, j);
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int values[] = {1, 2, 3, 4, 5};
    int length = 5;
    
    for (int index = 0; index < length; index++) {  // 符合：使用局部变量控制数组遍历
        printf("%d ", values[index]);
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    for (int i = 0; i < 5; i++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
    return 0;
}
#include <stdio.h>

int main(void) {
    int reg_var;  // 寄存器变量（局部）
    for (reg_var = 0; reg_var < 5; reg_var++) {  // 符合：寄存器变量也是局部变量
        printf("%d ", reg_var);
    }
    return 0;
}
#include <stdio.h>

int global_data = 100;  // 全局变量，但与局部变量不同名

int main(void) {
    for (int counter = 0; counter < 5; counter++) {  // 符合：局部变量与全局变量不同名
        printf("%d (global=%d)\n", counter, global_data);
    }
    return 0;
}
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
#include <stdio.h>

struct Config {
    int start;
    int end;
};

struct Config config = {0, 5};  // 全局结构体变量

int main(void) {
    for (config.start = 0; config.start < config.end; config.start++) {  // 违反：使用全局结构体成员作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", config.start);
    }
    return 0;
}
```

### ast of  failed test cases 
TranslationUnitDecl 0x561a721ddf08 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x561a722a3d00 <line:10:1, line:16:1> line:10:5 main 'int ()'
  `-CompoundStmt 0x561a722a4200 <col:16, line:16:1>
    |-ForStmt 0x561a722a4198 <line:11:5, line:14:5>
    | |-BinaryOperator 0x561a722a3e18 <line:11:10, col:25> 'int' lvalue '='
    | | |-MemberExpr 0x561a722a3dc8 <col:10, col:17> 'int' lvalue .start 0x561a722a38d0
    | | | `-DeclRefExpr 0x561a722a3da8 <col:10> 'struct Config':'Config' lvalue Var 0x561a722a39f0 'config' 'struct Config':'Config'
    | | `-IntegerLiteral 0x561a722a3df8 <col:25> 'int' 0
    | |-<<<NULL>>>
    | |-BinaryOperator 0x561a722a3f08 <col:28, col:50> 'bool' '<'
    | | |-ImplicitCastExpr 0x561a722a3ed8 <col:28, col:35> 'int' <LValueToRValue>
    | | | `-MemberExpr 0x561a722a3e58 <col:28, col:35> 'int' lvalue .start 0x561a722a38d0
    | | |   `-DeclRefExpr 0x561a722a3e38 <col:28> 'struct Config':'Config' lvalue Var 0x561a722a39f0 'config' 'struct Config':'Config'
    | | `-ImplicitCastExpr 0x561a722a3ef0 <col:43, col:50> 'int' <LValueToRValue>
    | |   `-MemberExpr 0x561a722a3ea8 <col:43, col:50> 'int' lvalue .end 0x561a722a3938
    | |     `-DeclRefExpr 0x561a722a3e88 <col:43> 'struct Config':'Config' lvalue Var 0x561a722a39f0 'config' 'struct Config':'Config'
    | |-UnaryOperator 0x561a722a3f78 <col:55, col:67> 'int' postfix '++'
    | | `-MemberExpr 0x561a722a3f48 <col:55, col:62> 'int' lvalue .start 0x561a722a38d0
    | |   `-DeclRefExpr 0x561a722a3f28 <col:55> 'struct Config':'Config' lvalue Var 0x561a722a39f0 'config' 'struct Config':'Config'
    | `-CompoundStmt 0x561a722a4180 <col:71, line:14:5>
    |   `-CallExpr 0x561a722a4120 <line:13:9, col:35> 'int'
    |     |-ImplicitCastExpr 0x561a722a4108 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x561a722a4088 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x561a722803d8 'printf' 'int (const char *__restrict, ...)'
    |     |-ImplicitCastExpr 0x561a722a4150 <col:16> 'const char *' <ArrayToPointerDecay>
    |     | `-StringLiteral 0x561a722a4018 <col:16> 'const char[4]' lvalue "%d "
    |     `-ImplicitCastExpr 0x561a722a4168 <col:23, col:30> 'int' <LValueToRValue>
    |       `-MemberExpr 0x561a722a4058 <col:23, col:30> 'int' lvalue .start 0x561a722a38d0
    |         `-DeclRefExpr 0x561a722a4038 <col:23> 'struct Config':'Config' lvalue Var 0x561a722a39f0 'config' 'struct Config':'Config'
    `-ReturnStmt 0x561a722a41f0 <line:15:5, col:12>
      `-IntegerLiteral 0x561a722a41d0 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match for statements to capture all for loops
2. For the loop initialization part, handle two main cases: assignment expressions and declaration statements
3. For assignment expressions (binary operator with assignment), capture three sub-cases: direct variable reference, member expression, and pointer dereference
4. For direct variable reference, bind the referenced variable declaration
5. For member expressions, bind the base object variable declaration
6. For pointer dereferences, bind the pointer variable declaration
7. For declaration statements, bind the declared variable
8. Bind the for statement itself for location reporting
**logic for check**:
1. Retrieve the bound for statement and verify it has a valid location
2. Attempt to get the loop control variable from each binding in order: direct variable, member base, pointer variable, declared variable
3. Skip invalid variable declarations
4. If no variable is found, exit the check
5. Determine if the variable is non-local by checking its storage duration
6. Variables with global storage (static or extern) are considered non-local
7. For non-global variables, examine the declaration context hierarchy
8. Traverse parent contexts to find if the variable is declared within a function or block scope
9. If the variable is not within a function or block scope, it is non-local
10. If the variable is non-local, emit a diagnostic at the for loop location with the rule identifier


## reference astMatchers
AST Traversal Matcher: optionally
 Parameters;Matcher<*>
 Return type Matcher<*>
 Description: Matches any node regardless of the submatcher.

However, optionally will retain any bindings generated by the submatcher.
Useful when additional information which may or may not present about a main
matching node is desired.

For example, in:
  class Foo {
    int bar;
  }
The matcher:
  cxxRecordDecl(
    optionally(has(
      fieldDecl(hasName("bar")).bind("var")
  ))).bind("record")
will produce a result binding for both "record" and "var".
The matcher will produce a "record" binding for even if there is no data
member named "bar" in that class.

Usable as: Any Matcher

Narrowing Matcher: isCopyAssignmentOperator
 Parameters;
 return type Matcher<CXXMethodDecl>
 Description: Matches if the given method declaration declares a copy assignment
operator.

Given
struct A {
  A &amp;operator=(const A &amp;);
  A &amp;operator=(A &amp;&amp;);
};

cxxMethodDecl(isCopyAssignmentOperator()) matches the first method but not
the second one.

Node Matcher: arrayInitLoopExpr
 Parameters;Matcher<ArrayInitLoopExpr>...
 return type Matcher<Stmt>
 Description: Matches a loop initializing the elements of an array in a number of contexts:
 * in the implicit copy/move constructor for a class with an array member
 * when a lambda-expression captures an array by value
 * when a decomposition declaration decomposes an array

Given
  void testLambdaCapture() {
    int a[10];
    auto Lam1 = [a]() {
      return;
    };
  }
arrayInitLoopExpr() matches the implicit loop that initializes each element of
the implicit array field inside the lambda object, that represents the array `a`
captured by value.

Node Matcher: cxxForRangeStmt
 Parameters;Matcher<CXXForRangeStmt>...
 return type Matcher<Stmt>
 Description: Matches range-based for statements.

cxxForRangeStmt() matches 'for (auto a : i)'
  int i[] =  {1, 2, 3}; for (auto a : i);
  for(int j = 0; j &lt; 5; ++j);

Node Matcher: forStmt
 Parameters;Matcher<ForStmt>...
 return type Matcher<Stmt>
 Description: Matches for statements.

Example matches 'for (;;) {}'
  for (;;) {}
  int i[] =  {1, 2, 3}; for (auto a : i);

Narrowing Matcher: memberHasSameNameAsBoundNode
 Parameters;std::string BindingID
 return type Matcher<CXXDependentScopeMemberExpr>
 Description: Matches template-dependent, but known, member names against an already-bound
node

In template declarations, dependent members are not resolved and so can
not be matched to particular named declarations.

This matcher allows to match on the name of already-bound VarDecl, FieldDecl
and CXXMethodDecl nodes.

Given
  template &lt;typename T&gt;
  struct S {
      void mem();
  };
  template &lt;typename T&gt;
  void x() {
      S&lt;T&gt; s;
      s.mem();
  }
The matcher
@code
cxxDependentScopeMemberExpr(
  hasObjectExpression(declRefExpr(hasType(templateSpecializationType(
      hasDeclaration(classTemplateDecl(has(cxxRecordDecl(has(
          cxxMethodDecl(hasName("mem")).bind("templMem")
          )))))
      )))),
  memberHasSameNameAsBoundNode("templMem")
  )
@endcode
first matches and binds the @c mem member of the @c S template, then
compares its name to the usage in @c s.mem() in the @c x function template

Finder->addMatcher(forStmt(hasLoopInit(declStmt(forEach(varDecl().bind("loopVar"))))), this);
cxxDeleteExpr(has(declRefExpr(to(decl(equalsBoundNode("deletedPointer")))))).bind("deleteExpr")
anyOf(declRefExpr(to(decl().bind("deletedPointer"))), memberExpr(hasDeclaration(fieldDecl().bind("deletedMemberPointer"))))
cxxConstructorDecl(isCopyConstructor()).bind("ctor")
anyOf(has(declStmt(containsDeclaration(0, varDecl(hasInitializer(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), callee(namedDecl(hasName("cast")))).bind("assign")))))), hasCondition(implicitCastExpr(has(callExpr(unless(isMacroID()), unless(cxxMemberCallExpr()), anyOf(callee(namedDecl(hasName("cast"))), callee(namedDecl(hasName("dyn_cast")).bind("dyn_cast")))).bind("call")))))
match(
        functionDecl(forEachDescendant(
            memberExpr(hasObjectExpression(paramRefExpr())).bind("mem-expr"))),
        *FD, FD->getASTContext());
stmt().bind("stmt")


## reference code snippets  
if (Variable) {
  diag(Variable->getLocation(), "variable %0 is non-const and globally "
                              "accessible, consider making it const")
      << Variable;
}
if (F->getLocation().isInvalid() || F->isImplicit())
  return;
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
StringRef Type = llvm::isa<VarDecl>(MatchedDecl) ? "variable" : "function";
if (!Arg->getDecl()->getDeclContext()->isFunctionOrMethod())
  return;
const auto *Loop = Result.Nodes.getNodeAs<Stmt>("loop");
const auto *CXXLoopBound = Result.Nodes.getNodeAs<IntegerLiteral>("cxx_loop_bound");
const ASTContext *Context = Result.Context;
bool NeedsQualification = true;
const DeclContext *Context = UserVarDecl->getDeclContext();
while (Context) {
  if (const auto *Namespace = dyn_cast<NamespaceDecl>(Context))
    if (isa<TranslationUnitDecl>(Namespace->getDeclContext()) &&
        Namespace->getName() == "llvm")
      NeedsQualification = false;
  for (const auto *UsingDirective : Context->using_directives()) {
    const NamespaceDecl *Namespace = UsingDirective->getNominatedNamespace();
    if (isa<TranslationUnitDecl>(Namespace->getDeclContext()) &&
        Namespace->getName() == "llvm")
      NeedsQualification = false;
  }
  Context = Context->getParent();
}
if (checkConditionVarUsageInElse(If) != nullptr) {
  if (!WarnOnConditionVariables)
    return;
  if (IsLastInScope) {
    DiagnosticBuilder Diag = diag(ElseLoc, WarningMessage)
                             << ControlFlowInterruptor
                             << SourceRange(ElseLoc);
    if (checkInitDeclUsageInElse(If) != nullptr) {
      Diag << tooling::fixit::createReplacement(
                  SourceRange(If->getIfLoc()),
                  (tooling::fixit::getText(*If->getInit(), *Result.Context) +
                   llvm::StringRef("\n"))
                      .str())
           << tooling::fixit::createRemoval(If->getInit()->getSourceRange());
    }
    const DeclStmt *VDeclStmt = If->getConditionVariableDeclStmt();
    const VarDecl *VDecl = If->getConditionVariable();
    std::string Repl =
        (tooling::fixit::getText(*VDeclStmt, *Result.Context) +
         llvm::StringRef(";\n") +
         tooling::fixit::getText(If->getIfLoc(), *Result.Context))
            .str();
    Diag << tooling::fixit::createReplacement(SourceRange(If->getIfLoc()), Repl)
         << tooling::fixit::createReplacement(VDeclStmt->getSourceRange(),
                                              VDecl->getName());
    removeElseAndBrackets(Diag, *Result.Context, Else, ElseLoc);
  } else if (WarnOnUnfixable) {
    diag(ElseLoc, WarningMessage) << ControlFlowInterruptor;
  }
  return;
}
const auto *LoopVar = Nodes.getNodeAs<VarDecl>(InitVarName);
const auto *EndVar = Nodes.getNodeAs<VarDecl>(EndVarName);
const auto *EndCall = Nodes.getNodeAs<CXXMemberCallExpr>(EndCallName);
const auto *BoundExpr = Nodes.getNodeAs<Expr>(ConditionBoundName);
bool clang::VarDecl::hasGlobalStorage() const
VarDecl * clang::BindingDecl::getHoldingVar() const
bool clang::VarDecl::isLocalVarDecl() const
bool clang::SourceLocation::isValid() const
bool clang::VarDecl::hasLocalStorage() const
bool clang::VarDecl::isPreviousDeclInSameBlockScope() const
bool clang::Expr::refersToGlobalRegisterVar() const
const Expr * clang::Expr::skipRValueSubobjectAdjustments() const
void llvm::ExitOnError::operator()(Error Err) const
void clang::PartialDiagnostic::EmitToString(DiagnosticsEngine & Diags, SmallVectorImpl<char> & Buf) const



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

