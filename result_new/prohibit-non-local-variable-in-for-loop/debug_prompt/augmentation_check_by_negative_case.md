针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop/prohibit_non_local_variable_in_for_loop_case_6.cpp增强checker
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
  // Match for statements that:
  // 1. Have an init part that is an assignment (binaryOperator) where LHS is a DeclRefExpr or MemberExpr
  // 2. Exclude for loops where init is a declaration statement (local variable)
  // 3. Remove hasCondition/hasIncrement to avoid missing loops without them
  Finder->addMatcher(
      forStmt(
          unless(hasLoopInit(declStmt())),
          hasLoopInit(
              binaryOperator(
                  isAssignmentOperator(),
                  hasLHS(ignoringParenImpCasts(
                      anyOf(
                          declRefExpr(to(varDecl().bind("loopVar"))).bind("loopVarRef"),
                          memberExpr(member(varDecl().bind("loopVar"))).bind("loopVarRef")
                      )
                  ))
              )
          )
      ).bind("forLoop"),
      this
  );
}

void ProhibitNonLocalVariableInForLoopCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ForLoop = Result.Nodes.getNodeAs<ForStmt>("forLoop");
  const auto *LoopVarRef = Result.Nodes.getNodeAs<Expr>("loopVarRef");
  const auto *LoopVar = Result.Nodes.getNodeAs<VarDecl>("loopVar");

  if (!ForLoop || !LoopVarRef || !LoopVar)
    return;

  // Check if the variable is non-local:
  // - hasGlobalStorage() covers global variables, static global variables
  // - isFileVarDecl() covers variables with file scope (external linkage)
  // - hasExternalStorage() covers variables declared with 'extern'
  if (LoopVar->hasGlobalStorage() || LoopVar->isFileVarDecl() || LoopVar->hasExternalStorage()) {
    // Skip static local variables (they have local scope but static storage)
    if (!LoopVar->isLocalVarDecl() || LoopVar->isStaticLocal()) {
      diag(ForLoop->getForLoc(), "禁止 for 循环控制变量使用非局部变量");
    }
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

/// FIXME: Write a short description.
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

int global_i = 0;  // 全局变量

int main(void) {
    for (global_i = 0; global_i < 5; global_i++) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", global_i);
    }
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

static int static_counter = 0;  // 静态全局变量

int main(void) {
    for (static_counter = 0; static_counter < 3; static_counter++) {  // 违反：使用静态全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", static_counter);
    }
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
    for (int i = 0, j = 10; i < 5; i++, j--) {  // 符合：使用多个局部变量作为循环控制
        printf("i=%d, j=%d\n", i, j);
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
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
#include <stdio.h>

int *global_ptr = NULL;  // 全局指针变量
int array[5] = {1, 2, 3, 4, 5};

int main(void) {
    int value = 10;
    global_ptr = &value;
    
    for (*global_ptr = 0; *global_ptr < 3; (*global_ptr)++) {  // 违反：使用全局指针变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", *global_ptr);
    }
    return 0;
}
```

### ast of  failed test cases
TranslationUnitDecl 0x556df7398f08 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x556df745ebc0 <line:6:1, line:15:1> line:6:5 main 'int ()'
  `-CompoundStmt 0x556df745f1f0 <col:16, line:15:1>
    |-DeclStmt 0x556df745ed08 <line:7:5, col:19>
    | `-VarDecl 0x556df745ec80 <col:5, col:17> col:9 used value 'int' cinit
    |   `-IntegerLiteral 0x556df745ece8 <col:17> 'int' 10
    |-BinaryOperator 0x556df745eda8 <line:8:5, col:19> 'int *' lvalue '='
    | |-DeclRefExpr 0x556df745ed20 <col:5> 'int *' lvalue Var 0x556df745e760 'global_ptr' 'int *'
    | `-UnaryOperator 0x556df745ed60 <col:18, col:19> 'int *' prefix '&' cannot overflow
    |   `-DeclRefExpr 0x556df745ed40 <col:19> 'int' lvalue Var 0x556df745ec80 'value' 'int'
    |-ForStmt 0x556df745f188 <line:10:5, line:13:5>
    | |-BinaryOperator 0x556df745ee38 <line:10:10, col:24> 'int' lvalue '='
    | | |-UnaryOperator 0x556df745ee00 <col:10, col:11> 'int' lvalue prefix '*' cannot overflow
    | | | `-ImplicitCastExpr 0x556df745ede8 <col:11> 'int *' <LValueToRValue>
    | | |   `-DeclRefExpr 0x556df745edc8 <col:11> 'int *' lvalue Var 0x556df745e760 'global_ptr' 'int *'
    | | `-IntegerLiteral 0x556df745ee18 <col:24> 'int' 0
    | |-<<<NULL>>>
    | |-BinaryOperator 0x556df745eee0 <col:27, col:41> 'bool' '<'
    | | |-ImplicitCastExpr 0x556df745eec8 <col:27, col:28> 'int' <LValueToRValue>
    | | | `-UnaryOperator 0x556df745ee90 <col:27, col:28> 'int' lvalue prefix '*' cannot overflow
    | | |   `-ImplicitCastExpr 0x556df745ee78 <col:28> 'int *' <LValueToRValue>
    | | |     `-DeclRefExpr 0x556df745ee58 <col:28> 'int *' lvalue Var 0x556df745e760 'global_ptr' 'int *'
    | | `-IntegerLiteral 0x556df745eea8 <col:41> 'int' 3
    | |-UnaryOperator 0x556df745ef70 <col:44, col:57> 'int' postfix '++'
    | | `-ParenExpr 0x556df745ef50 <col:44, col:56> 'int' lvalue
    | |   `-UnaryOperator 0x556df745ef38 <col:45, col:46> 'int' lvalue prefix '*' cannot overflow
    | |     `-ImplicitCastExpr 0x556df745ef20 <col:46> 'int *' <LValueToRValue>
    | |       `-DeclRefExpr 0x556df745ef00 <col:46> 'int *' lvalue Var 0x556df745e760 'global_ptr' 'int *'
    | `-CompoundStmt 0x556df745f170 <col:61, line:13:5>
    |   `-CallExpr 0x556df745f110 <line:12:9, col:34> 'int'
    |     |-ImplicitCastExpr 0x556df745f0f8 <col:9> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x556df745f078 <col:9> 'int (const char *__restrict, ...)' lvalue Function 0x556df743b3e8 'printf' 'int (const char *__restrict, ...)'
    |     |-ImplicitCastExpr 0x556df745f140 <col:16> 'const char *' <ArrayToPointerDecay>
    |     | `-StringLiteral 0x556df745f008 <col:16> 'const char[4]' lvalue "%d "
    |     `-ImplicitCastExpr 0x556df745f158 <col:23, col:24> 'int' <LValueToRValue>
    |       `-UnaryOperator 0x556df745f060 <col:23, col:24> 'int' lvalue prefix '*' cannot overflow
    |         `-ImplicitCastExpr 0x556df745f048 <col:24> 'int *' <LValueToRValue>
    |           `-DeclRefExpr 0x556df745f028 <col:24> 'int *' lvalue Var 0x556df745e760 'global_ptr' 'int *'
    `-ReturnStmt 0x556df745f1e0 <line:14:5, col:12>
      `-IntegerLiteral 0x556df745f1c0 <col:12> 'int' 0



## reference logic step
**logic for registerMatchers**:
1. Match for statements that have an init part which is a binary assignment operator
2. Exclude for loops where the init part is a declaration statement (local variable)
3. Match the left-hand side of the assignment, ignoring parentheses and implicit casts, as either a DeclRefExpr or a MemberExpr
4. For DeclRefExpr, bind the referenced VarDecl as 'loopVar' and bind the expression as 'loopVarRef'
5. For MemberExpr, bind the member VarDecl as 'loopVar' and bind the expression as 'loopVarRef'
6. Bind the entire for statement as 'forLoop'
**logic for check**:
1. Retrieve the bound nodes: ForStmt 'forLoop', Expr 'loopVarRef', and VarDecl 'loopVar'
2. If any of these nodes is null, return early
3. Check if the variable has global storage (hasGlobalStorage()), is a file-scope variable (isFileVarDecl()), or has external storage (hasExternalStorage())
4. If the variable is a local variable declaration (isLocalVarDecl()) and is not a static local variable (isStaticLocal()), skip it (it is a valid local variable)
5. If the variable is non-local (global, file-scope, extern) or is a static local variable, emit a diagnostic at the for loop location with the message '禁止 for 循环控制变量使用非局部变量'


## reference astMatchers
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

AST Traversal Matcher: ignoringParenImpCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after implicit casts and
parentheses are stripped off.

Explicit casts are not discarded.
Given
  int arr[5];
  int a = 0;
  char b = (0);
  const int c = a;
  int *d = (arr);
  long e = ((long) 0l);
The matchers
   varDecl(hasInitializer(ignoringParenImpCasts(integerLiteral())))
   varDecl(hasInitializer(ignoringParenImpCasts(declRefExpr())))
would match the declarations for a, b, c, and d, but not e.
while
   varDecl(hasInitializer(integerLiteral()))
   varDecl(hasInitializer(declRefExpr()))
would only match the declaration for a.

AST Traversal Matcher: ignoringParenCasts
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<Expr>
 Description: Matches expressions that match InnerMatcher after parentheses and
casts are stripped off.

Implicit and non-C Style casts are also discarded.
Given
  int a = 0;
  char b = (0);
  void* c = reinterpret_cast&lt;char*&gt;(0);
  char d = char(0);
The matcher
   varDecl(hasInitializer(ignoringParenCasts(integerLiteral())))
would match the declarations for a, b, c, and d.
while
   varDecl(hasInitializer(integerLiteral()))
only match the declaration for a.

Finder->addMatcher(forStmt(hasLoopInit(declStmt(forEach(varDecl().bind("loopVar"))))), this);
cxxForRangeStmt(hasLoopVariable(
    varDecl(
        hasType(qualType(references(qualType(isConstQualified())))),
        hasInitializer(
            expr(anyOf(
                     hasDescendant(
                         cxxOperatorCallExpr().bind("operator-call")),
                     hasDescendant(unaryOperator(hasOperatorName("*"))
                                       .bind("operator-call"))))
                .bind("init")))
        .bind("faulty-var")))
bool isCatchVariable(const DeclRefExpr *DeclRefExpr) {
  auto *ValueDecl = DeclRefExpr->getDecl();
  if (auto *VarDecl = dyn_cast<clang::VarDecl>(ValueDecl))
    return VarDecl->isExceptionVariable();
  return false;
}


## reference code snippets
const auto *HandlerDecl = Result.Nodes.getNodeAs<FunctionDecl>("handler_decl");
const auto *HandlerExpr = Result.Nodes.getNodeAs<DeclRefExpr>("handler_expr");
assert(Result.Nodes.getNodeAs<CallExpr>("register_call") && HandlerDecl &&
       HandlerExpr && "All of these should exist in a match here.");
bool isExprValueStored(const Expr *E, ASTContext &C) {
  E = E->IgnoreParenCasts();
  ParentMapContext &PMap = C.getParentMapContext();
  DynTypedNodeList P = PMap.getParents(*E);
  if (P.size() != 1)
    return false;
  const Expr *ParentE;
  while ((ParentE = P[0].get<Expr>()) && ParentE->IgnoreParenCasts() == E) {
    P = PMap.getParents(P[0]);
    if (P.size() != 1)
      return false;
  }

  if (const auto *ParentVarD = P[0].get<VarDecl>())
    return ParentVarD->getInit()->IgnoreParenCasts() == E;

  if (!ParentE)
    return false;

  if (const auto *BinOp = dyn_cast<BinaryOperator>(ParentE))
    return BinOp->getOpcode() == BO_Assign &&
           BinOp->getRHS()->IgnoreParenCasts() == E;

  return isa<CallExpr, CXXConstructExpr>(ParentE);
}
if (const auto *Op = Result.Nodes.getNodeAs<BinaryOperator>("binary_op"))
  return handleBinaryOperator(*Result.Context, *Op);
if (const auto *Cast = Result.Nodes.getNodeAs<ImplicitCastExpr>("cast"))
  return handleImplicitCast(*Result.Context, *Cast);
llvm_unreachable("must be binary operator or cast expression");
const DeclStmt * clang::ForStmt::getConditionVariableDeclStmt() const
bool clang::VarDecl::hasExternalStorage() const
bool clang::VarDecl::hasLocalStorage() const

