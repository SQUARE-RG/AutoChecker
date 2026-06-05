针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr/dependent_call_in_expr_case_2.cpp增强checker
# Inputs

## rule
**Rule Description:**
Multiple related functions cannot be called in the same expression.Related functions refer to functions called in the same expression that have a data dependency relationship, which will result in undefined behavior.Scenario: Reporting multiple related function calls
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            int y = inc(&x) + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then it should report "test.c:16:21: warning: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]"
    And a total of 1 warning should be reported

Scenario: Do not report multiple related function calls that are not in the same expression
    Given a source code file "test.c" with the following content:
        """
        int inc(int *x)
        {
            *x += 1;
            return *x;
        }

        int square(int *x)
        {
            *x *= *x;
            return *x;
        }

        void foo(void)
        {
            int x = 3;
            x = inc(&x);
            int y = x + square(&x);
        }
        """
    When running clang-tidy with the gjb8114 plugin to check "gjb8114-r-1-7-14" on "test.c"
    Then no warnings should be reported

## current checker code

checker_cpp:
```cpp
//===--- DependentCallInExprCheck.cpp - clang-tidy ------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DependentCallInExprCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/Basic/Diagnostic.h"
#include <set>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

// Helper function to collect all variables that are passed by non-const pointer
// or array to a function call, including struct pointer members
static void collectModifiedVars(const CallExpr *Call,
                                std::set<const ValueDecl *> &ModifiedVars) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  for (unsigned I = 0; I < Call->getNumArgs() && I < FD->getNumParams(); ++I) {
    const ParmVarDecl *Param = FD->getParamDecl(I);
    QualType ParamType = Param->getType();

    // Check if parameter is non-const pointer or array type
    bool IsNonConstPointer = false;
    if (ParamType->isPointerType()) {
      // For pointer types, check the pointee type's const qualification
      IsNonConstPointer = !ParamType->getPointeeType().isConstQualified();
    } else if (ParamType->isArrayType()) {
      // Array parameters decay to pointers, check the element type
      const ArrayType *ArrType = ParamType->getAsArrayTypeUnsafe();
      if (ArrType) {
        IsNonConstPointer = !ArrType->getElementType().isConstQualified();
      }
    }

    if (!IsNonConstPointer)
      continue;

    const Expr *Arg = Call->getArg(I)->IgnoreParenImpCasts();

    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        ModifiedVars.insert(VD);
      }
    }
  }
}

// Helper function to collect global variables modified by a function call
static void collectModifiedGlobals(const CallExpr *Call,
                                   std::set<const ValueDecl *> &ModifiedGlobals) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  // Check if the function definition is available
  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    // Traverse the body to find modifications to global variables
    std::function<void(const Stmt*)> findGlobalMods = [&](const Stmt* S) {
      if (!S) return;
      if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
        if (BO->isAssignmentOp()) {
          const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
              ModifiedGlobals.insert(VD);
            }
          }
        }
      }
      // Check for unary increment/decrement on globals
      if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
        if (UO->isIncrementDecrementOp()) {
          const Expr *Sub = UO->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(Sub)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
              ModifiedGlobals.insert(VD);
            }
          }
        }
      }
      // Check for compound assignments
      if (const auto *CAO = dyn_cast<CompoundAssignOperator>(S)) {
        const Expr *LHS = CAO->getLHS()->IgnoreParenImpCasts();
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage()) {
            ModifiedGlobals.insert(VD);
          }
        }
      }
      for (const Stmt *Child : S->children()) {
        findGlobalMods(Child);
      }
    };
    findGlobalMods(Body);
  }
}

// Helper function to check if two function calls have data dependency
// through pointer/array arguments or through global variables
static bool hasDataDependency(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // Collect all variables that are potentially modified by Call1
  std::set<const ValueDecl *> ModifiedVars;
  collectModifiedVars(Call1, ModifiedVars);

  // Also collect global variables modified by Call1
  std::set<const ValueDecl *> ModifiedGlobals;
  collectModifiedGlobals(Call1, ModifiedGlobals);

  // Check if Call2 accesses any of the modified variables (via pointer/array args)
  const FunctionDecl *FD2 = Call2->getDirectCallee();
  if (!FD2)
    return false;

  for (unsigned I = 0; I < Call2->getNumArgs(); ++I) {
    const Expr *Arg = Call2->getArg(I)->IgnoreParenImpCasts();

    // Handle array to pointer decay
    if (const auto *ICE = dyn_cast<ImplicitCastExpr>(Call2->getArg(I))) {
      if (ICE->getCastKind() == CK_ArrayToPointerDecay) {
        Arg = ICE->getSubExpr()->IgnoreParenImpCasts();
      }
    }

    if (const auto *DeclRef = dyn_cast<DeclRefExpr>(Arg)) {
      if (const auto *VD = dyn_cast<VarDecl>(DeclRef->getDecl())) {
        if (ModifiedVars.count(VD))
          return true;
      }
    }
  }

  // Check if Call2 accesses any of the modified global variables
  if (!ModifiedGlobals.empty()) {
    // Check if Call2's callee also accesses these globals
    if (FD2->hasBody()) {
      const Stmt *Body2 = FD2->getBody();
      std::function<bool(const Stmt*)> accessesGlobal = [&](const Stmt* S) -> bool {
        if (!S) return false;
        if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->hasGlobalStorage() && ModifiedGlobals.count(VD)) {
            return true;
          }
        }
        for (const Stmt *Child : S->children()) {
          if (accessesGlobal(Child)) return true;
        }
        return false;
      };
      if (accessesGlobal(Body2)) {
        return true;
      }
    }
  }

  return false;
}

// Helper function to collect static local variables modified by a function call
static void collectModifiedStaticLocals(const CallExpr *Call,
                                        std::set<const ValueDecl *> &ModifiedStaticLocals) {
  if (!Call)
    return;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return;

  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    std::function<void(const Stmt*)> findStaticMods = [&](const Stmt* S) {
      if (!S) return;
      if (const auto *BO = dyn_cast<BinaryOperator>(S)) {
        if (BO->isAssignmentOp()) {
          const Expr *LHS = BO->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
              ModifiedStaticLocals.insert(VD);
            }
          }
        }
      }
      // Check for unary increment/decrement on static locals
      if (const auto *UO = dyn_cast<UnaryOperator>(S)) {
        if (UO->isIncrementDecrementOp()) {
          const Expr *Sub = UO->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(Sub)) {
            const ValueDecl *VD = DRE->getDecl();
            if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
              ModifiedStaticLocals.insert(VD);
            }
          }
        }
      }
      // Check for compound assignments
      if (const auto *CAO = dyn_cast<CompoundAssignOperator>(S)) {
        const Expr *LHS = CAO->getLHS()->IgnoreParenImpCasts();
        if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
          const ValueDecl *VD = DRE->getDecl();
          if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal()) {
            ModifiedStaticLocals.insert(VD);
          }
        }
      }
      for (const Stmt *Child : S->children()) {
        findStaticMods(Child);
      }
    };
    findStaticMods(Body);
  }
}

// Helper function to check if a function call accesses specific static local variables
static bool accessesStaticLocals(const CallExpr *Call,
                                 const std::set<const ValueDecl *> &StaticLocals) {
  if (!Call || StaticLocals.empty())
    return false;

  const FunctionDecl *FD = Call->getDirectCallee();
  if (!FD)
    return false;

  if (FD->hasBody()) {
    const Stmt *Body = FD->getBody();
    std::function<bool(const Stmt*)> findAccess = [&](const Stmt* S) -> bool {
      if (!S) return false;
      if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
        const ValueDecl *VD = DRE->getDecl();
        if (isa<VarDecl>(VD) && cast<VarDecl>(VD)->isStaticLocal() && StaticLocals.count(VD)) {
          return true;
        }
      }
      for (const Stmt *Child : S->children()) {
        if (findAccess(Child)) return true;
      }
      return false;
    };
    return findAccess(Body);
  }
  return false;
}

// Extended data dependency check that includes static local variables
static bool hasDataDependencyEx(const CallExpr *Call1, const CallExpr *Call2) {
  if (!Call1 || !Call2)
    return false;

  // First check original data dependency
  if (hasDataDependency(Call1, Call2))
    return true;

  // Check static local variable dependency
  std::set<const ValueDecl *> ModifiedStaticLocals;
  collectModifiedStaticLocals(Call1, ModifiedStaticLocals);

  if (!ModifiedStaticLocals.empty()) {
    if (accessesStaticLocals(Call2, ModifiedStaticLocals))
      return true;
  }

  return false;
}

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match call expressions that are arguments to another call expression
  Finder->addMatcher(
      callExpr(
          forEachArgumentWithParamType(
              callExpr().bind("call"),
              qualType())
      ).bind("parentCall"),
      this);
  
  // Match binary operators that contain at least two CallExpr nodes
  Finder->addMatcher(
      binaryOperator(
          anyOf(hasOperatorName("+"), hasOperatorName("-"),
                hasOperatorName("*"), hasOperatorName("/"),
                hasOperatorName("%"), hasOperatorName("&"),
                hasOperatorName("|"), hasOperatorName("^"),
                hasOperatorName("&&"), hasOperatorName("||"),
                hasOperatorName("=="), hasOperatorName("!="),
                hasOperatorName("<"), hasOperatorName(">"),
                hasOperatorName("<="), hasOperatorName(">="),
                hasOperatorName("<<"), hasOperatorName(">>")),
          forEachDescendant(callExpr().bind("call")))
          .bind("binaryOp"),
      this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *BinaryOp = Result.Nodes.getNodeAs<BinaryOperator>("binaryOp");
  const auto *ParentCall = Result.Nodes.getNodeAs<CallExpr>("parentCall");
  const auto *Call = Result.Nodes.getNodeAs<CallExpr>("call");

  // Use a static set to track processed expressions to avoid duplicate reports
  static std::set<const Stmt*> ProcessedExprs;

  if (BinaryOp && Call) {
    if (ProcessedExprs.count(BinaryOp))
      return;

    // Collect all call expressions within this binary operator
    std::vector<const CallExpr*> Calls;
    std::function<void(const Stmt*)> collectCalls = [&](const Stmt* S) {
      if (!S) return;
      if (const auto* CE = dyn_cast<CallExpr>(S)) {
        // Make sure this call is a direct child of the binary operator
        bool isDirectChild = false;
        for (const Stmt* Child : BinaryOp->children()) {
          if (Child == S) {
            isDirectChild = true;
            break;
          }
          if (const auto* ICE = dyn_cast<ImplicitCastExpr>(Child)) {
            if (ICE->getSubExpr() == S) {
              isDirectChild = true;
              break;
            }
          }
        }
        if (isDirectChild) {
          Calls.push_back(CE);
        }
      }
      for (const Stmt* Child : S->children()) {
        collectCalls(Child);
      }
    };
    collectCalls(BinaryOp);

    ProcessedExprs.insert(BinaryOp);

    if (Calls.size() < 2)
      return;

    // Check all pairs of calls for data dependency
    for (size_t i = 0; i < Calls.size(); ++i) {
      for (size_t j = i + 1; j < Calls.size(); ++j) {
        if (hasDataDependencyEx(Calls[i], Calls[j]) ||
            hasDataDependencyEx(Calls[j], Calls[i])) {
          diag(BinaryOp->getExprLoc(),
               "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
          return;
        }
      }
    }
  }

  if (ParentCall && Call) {
    if (ProcessedExprs.count(ParentCall))
      return;

    // Collect all call expressions that are direct arguments of the parent call
    std::vector<const CallExpr*> Calls;
    for (unsigned I = 0; I < ParentCall->getNumArgs(); ++I) {
      const Expr *Arg = ParentCall->getArg(I)->IgnoreParenImpCasts();
      if (const auto *CE = dyn_cast<CallExpr>(Arg)) {
        Calls.push_back(CE);
      }
    }

    ProcessedExprs.insert(ParentCall);

    if (Calls.size() < 2)
      return;

    // Check all pairs of calls for data dependency
    for (size_t i = 0; i < Calls.size(); ++i) {
      for (size_t j = i + 1; j < Calls.size(); ++j) {
        if (hasDataDependencyEx(Calls[i], Calls[j]) ||
            hasDataDependencyEx(Calls[j], Calls[i])) {
          diag(ParentCall->getBeginLoc(),
               "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
          return;
        }
      }
    }
  }
}

} // namespace clang::tidy::ucassaat
```

checker_h:
```cpp
//===--- DependentCallInExprCheck.h - clang-tidy ----------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/dependent-call-in-expr.html
class DependentCallInExprCheck : public ClangTidyCheck {
public:
  DependentCallInExprCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DEPENDENTCALLINEXPRCHECK_H
```

## passed test cases code

```cpp
#include <stdio.h>

int modify_array(int arr[], int index) {
    arr[index] += 10;
    return arr[index];
}

int get_array_value(int arr[], int index) {
    return arr[index];
}

int main(void) {
    int numbers[3] = {1, 2, 3};
    int result = modify_array(numbers, 0) - get_array_value(numbers, 0);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
#include <stdio.h>

int shared_data = 10;

int add_to_shared(int value) {
    shared_data += value;
    return shared_data;
}

int subtract_from_shared(int value) {
    shared_data -= value;
    return shared_data;
}

int main(void) {
    int value = 5;
    value += add_to_shared(3) + subtract_from_shared(2);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return value;
}
#include <stdio.h>

int process_first(int *a) {
    *a += 1;
    return *a;
}

int process_second(int *b) {
    *b *= 2;
    return *b;
}

int main(void) {
    int data1 = 5, data2 = 10;
    int result = process_first(&data1) + process_second(&data2);  // 符合：操作不同对象
    return result;
}
#include <stdio.h>
#include <string.h>

int main(void) {
    char str1[20] = "Hello";
    char str2[20] = "World";
    int result = strlen(str1) + strlen(str2);  // 符合：操作不同字符串
    return result;
}
#include <stdio.h>

int get_file_size_a(void) {
    FILE *file = fopen("test1.txt", "r");
    if (!file) return 0;
    fseek(file, 0, SEEK_END);
    int size = ftell(file);
    fclose(file);
    return size;
}

int get_file_size_b(void) {
    FILE *file = fopen("test2.txt", "r");
    if (!file) return 0;
    fseek(file, 0, SEEK_END);
    int size = ftell(file);
    fclose(file);
    return size;
}

int main(void) {
    int result = get_file_size_a() + get_file_size_b();  // 符合：操作不同文件
    return result;
}
#include <stdio.h>

int data = 8;

int modify_data(int new_val) {
    data = new_val;
    return data;
}

int process_data(void) {
    return data * 2;
}

int main(void) {
    int result = process_data() + modify_data(15);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
#include <stdio.h>

const int READ_ONLY_DATA = 100;

int get_data_a(void) {
    return READ_ONLY_DATA;
}

int get_data_b(void) {
    return READ_ONLY_DATA * 2;
}

int main(void) {
    int result = get_data_a() + get_data_b();  // 符合：只读函数无数据修改
    return result;
}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char *buffer1 = (char *)malloc(100);
    char *buffer2 = (char *)malloc(100);
    
    strcpy(buffer1, "Test1");
    strcpy(buffer2, "Test2");
    
    int result = strlen(buffer1) + strlen(buffer2);  // 符合：操作不同内存区域
    
    free(buffer1);
    free(buffer2);
    return result;
}
#include <stdio.h>

int global_value = 3;

int modify_global(int delta) {
    global_value += delta;
    return global_value;
}

int print_global(void) {
    return global_value;
}

void process_values(int a, int b) {
    // 处理值
}

int main(void) {
    process_values(modify_global(2), print_global());  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return 0;
}
#include <stdio.h>

int calculate_area(int width, int height) {
    return width * height;
}

int calculate_perimeter(int width, int height) {
    return 2 * (width + height);
}

int main(void) {
    int w = 5, h = 10;
    int result = calculate_area(w, h) + calculate_perimeter(w, h);  // 符合：操作局部变量
    return result;
}
#include <stdio.h>
#include <time.h>

int get_current_hour(void) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    return tm_info->tm_hour;
}

int get_current_minute(void) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    return tm_info->tm_min;
}

int main(void) {
    int result = get_current_hour() * 60 + get_current_minute();  // 符合：时间函数调用
    return result;
}
#include <stdio.h>

int counter = 0;

int increment_counter(void) {
    counter++;
    return counter;
}

int get_counter_value(void) {
    return counter;
}

int compute_result(void) {
    return increment_counter() * get_counter_value();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
}
#include <stdio.h>

int value = 10;

int increment_value(void) {
    value++;
    return value;
}

int get_value(void) {
    return value;
}

int main(void) {
    int first = increment_value();  // 先调用
    int second = get_value();       // 后调用
    int result = first + second;    // 符合：调用已分离
    return result;
}
#include <stdio.h>

int global_counter = 0;

int increment_global(void) {
    global_counter++;
    return global_counter;
}

int get_global(void) {
    return global_counter;
}

int main(void) {
    int result = increment_global() + get_global();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int main(void) {
    int x = 5, y = 3;
    int result = add(x, y) + multiply(x, y);  // 符合：函数间无数据依赖
    return result;
}
#include <stdio.h>
#include <math.h>

int main(void) {
    double x = 2.0;
    double result = sin(x) + cos(x);  // 符合：标准库函数，无共享状态修改
    return (int)result;
}
```

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
#include <stdio.h>

int add_value(int *x) {
    *x += 5;
    return *x;
}

int multiply_value(int *x) {
    *x *= 2;
    return *x;
}

int main(void) {
    int value = 10;
    int result = add_value(&value) * multiply_value(&value);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}
```

### ast of  failed test cases
TranslationUnitDecl 0x5618bc5bff48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5618bc685ea0 <line:13:1, line:18:1> line:13:5 main 'int ()'
  `-CompoundStmt 0x5618bc686318 <col:16, line:18:1>
    |-DeclStmt 0x5618bc685fe8 <line:14:5, col:19>
    | `-VarDecl 0x5618bc685f60 <col:5, col:17> col:9 used value 'int' cinit
    |   `-IntegerLiteral 0x5618bc685fc8 <col:17> 'int' 10
    |-DeclStmt 0x5618bc6862b8 <line:15:5, col:60>
    | `-VarDecl 0x5618bc686018 <col:5, col:59> col:9 used result 'int' cinit
    |   `-BinaryOperator 0x5618bc686298 <col:18, col:59> 'int' '*'
    |     |-CallExpr 0x5618bc686190 <col:18, col:34> 'int'
    |     | |-ImplicitCastExpr 0x5618bc686178 <col:18> 'int (*)(int *)' <FunctionToPointerDecay>
    |     | | `-DeclRefExpr 0x5618bc686128 <col:18> 'int (int *)' lvalue Function 0x5618bc685980 'add_value' 'int (int *)'
    |     | `-UnaryOperator 0x5618bc6860e8 <col:28, col:29> 'int *' prefix '&' cannot overflow
    |     |   `-DeclRefExpr 0x5618bc6860c8 <col:29> 'int' lvalue Var 0x5618bc685f60 'value' 'int'
    |     `-CallExpr 0x5618bc686270 <col:38, col:59> 'int'
    |       |-ImplicitCastExpr 0x5618bc686258 <col:38> 'int (*)(int *)' <FunctionToPointerDecay>
    |       | `-DeclRefExpr 0x5618bc686238 <col:38> 'int (int *)' lvalue Function 0x5618bc685c18 'multiply_value' 'int (int *)'
    |       `-UnaryOperator 0x5618bc686220 <col:53, col:54> 'int *' prefix '&' cannot overflow
    |         `-DeclRefExpr 0x5618bc686200 <col:54> 'int' lvalue Var 0x5618bc685f60 'value' 'int'
    `-ReturnStmt 0x5618bc686308 <line:17:5, col:12>
      `-ImplicitCastExpr 0x5618bc6862f0 <col:12> 'int' <LValueToRValue>
        `-DeclRefExpr 0x5618bc6862d0 <col:12> 'int' lvalue Var 0x5618bc686018 'result' 'int'



## reference logic step
**logic for registerMatchers**:
1. Match call expressions that are arguments to another call expression using forEachArgumentWithParamType to bind the inner call as 'call' and the outer call as 'parentCall'
2. Match binary operators with common arithmetic, comparison, bitwise, and logical operators that have at least two call expressions as descendants, binding the binary operator as 'binaryOp' and each descendant call as 'call'
3. Ensure the matcher does not miss nested call expressions or calls within complex expressions like ternary operators or comma operators
4. For the binary operator matcher, use forEachDescendant to capture all call expressions within the binary operator's subtree
**logic for check**:
1. Retrieve the bound nodes from the match result: the binary operator, parent call, and the matched call expression
2. Use a static set to track processed expressions to avoid duplicate reports for the same expression
3. For binary operator matches: collect all direct child call expressions of the binary operator by iterating its children, including handling implicit casts; if there are at least two such calls, check all pairs for data dependency using hasDataDependencyEx
4. For parent call matches: collect all call expressions that are direct arguments of the parent call after ignoring parentheses and implicit casts; if there are at least two such calls, check all pairs for data dependency using hasDataDependencyEx
5. In hasDataDependencyEx: first check original data dependency via hasDataDependency, which collects variables modified through non-const pointer/array parameters of Call1 and checks if Call2 accesses them, and also checks global variable modifications; then additionally check static local variable modifications of Call1 and whether Call2 accesses those static locals
6. If any pair of calls has a data dependency in either direction, emit a diagnostic at the appropriate location (binary operator location or parent call location) with the message '禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]' and return immediately to avoid multiple reports for the same expression
7. For the ternary operator or other compound expressions that contain multiple call expressions with data dependencies, the matcher must be extended to also match ternary conditional operators (?) and possibly other expression types that can contain multiple calls, and apply the same dependency checking logic


## reference astMatchers
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

AST Traversal Matcher: hasAnyArgument
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<CallExpr>
 Description: Matches any argument of a call expression or a constructor call
expression, or an ObjC-message-send expression.

Given
  void x(int, int, int) { int y; x(1, y, 42); }
callExpr(hasAnyArgument(declRefExpr()))
  matches x(1, y, 42)
with hasAnyArgument(...)
  matching y

For ObjectiveC, given
  @interface I - (void) f:(int) y; @end
  void foo(I *i) { [i f:12]; }
objcMessageExpr(hasAnyArgument(integerLiteral(equals(12))))
  matches [i f:12]

AST Traversal Matcher: hasOperands
 Parameters;Matcher<Expr> Matcher1, Matcher<Expr> Matcher2
 Return type Matcher<CXXOperatorCallExpr>
 Description: Matches if both matchers match with opposite sides of the binary operator.

Example matcher = binaryOperator(hasOperands(integerLiteral(equals(1),
                                             integerLiteral(equals(2)))
  1 + 2 // Match
  2 + 1 // Match
  1 + 1 // No match
  2 + 2 // No match

match(functionDecl(forEachDescendant(
              callExpr(forEachArgumentWithParam(
                           paramRefExpr(), parmVarDecl().bind("passed-to")))
                  .bind("call-expr"))),
            *FD, FD->getASTContext());
binaryOperator(hasOperatorName("*"), hasEitherOperand(ignoringImpCasts(anyOf(integerLiteral(), floatLiteral())))).bind("mult_binop")
binaryOperator(unless(anyOf(isComparisonOperator(), hasOperatorName("&&"), hasOperatorName("||"), hasOperatorName("="))), hasEitherOperand(StringCompareCallExpr)).bind("suspicious-operator")


## reference code snippets
AST_MATCHER_P2(Expr, hasSideEffect, bool, CheckFunctionCalls,
               clang::ast_matchers::internal::Matcher<NamedDecl>,
               IgnoredFunctionsMatcher) {
  const Expr *E = &Node;

  if (const auto *Op = dyn_cast<UnaryOperator>(E)) {
    UnaryOperator::Opcode OC = Op->getOpcode();
    return OC == UO_PostInc || OC == UO_PostDec || OC == UO_PreInc ||
           OC == UO_PreDec;
  }

  if (const auto *Op = dyn_cast<BinaryOperator>(E)) {
    return Op->isAssignmentOp();
  }

  if (const auto *OpCallExpr = dyn_cast<CXXOperatorCallExpr>(E)) {
    OverloadedOperatorKind OpKind = OpCallExpr->getOperator();
    return OpKind == OO_Equal || OpKind == OO_PlusEqual ||
           OpKind == OO_MinusEqual || OpKind == OO_StarEqual ||
           OpKind == OO_SlashEqual || OpKind == OO_AmpEqual ||
           OpKind == OO_PipeEqual || OpKind == OO_CaretEqual ||
           OpKind == OO_LessLessEqual || OpKind == OO_GreaterGreaterEqual ||
           OpKind == OO_PlusPlus || OpKind == OO_MinusMinus ||
           OpKind == OO_PercentEqual || OpKind == OO_New ||
           OpKind == OO_Delete || OpKind == OO_Array_New ||
           OpKind == OO_Array_Delete;
  }

  if (const auto *CExpr = dyn_cast<CallExpr>(E)) {
    bool Result = CheckFunctionCalls;
    if (const auto *FuncDecl = CExpr->getDirectCallee()) {
      if (FuncDecl->getDeclName().isIdentifier() &&
          IgnoredFunctionsMatcher.matches(*FuncDecl, Finder,
                                          Builder))
        Result = false;
      else if (const auto *MethodDecl = dyn_cast<CXXMethodDecl>(FuncDecl))
        Result &= !MethodDecl->isConst();
    }
    return Result;
  }

  return isa<CXXNewExpr>(E) || isa<CXXDeleteExpr>(E) || isa<CXXThrowExpr>(E);
}
if (const auto *DeclRef = dyn_cast<DeclRefExpr>(PtrInputExpr->IgnoreParenImpCasts()))
  if (const auto *Var = dyn_cast<VarDecl>(DeclRef->getDecl()))
    if (const auto *Func = Result.Nodes.getNodeAs<FunctionDecl>("parent_function"))
      if (FindAssignToVarBefore{Var, DeclRef, SM}.Visit(Func->getBody()))
        return;
bool isReferencedOutsideOfCallExpr(const FunctionDecl &Function,
                                 ASTContext &Context) {
  auto Matches = match(declRefExpr(to(functionDecl(equalsNode(&Function))),
                                   unless(hasAncestor(callExpr()))),
                       Context);
  return !Matches.empty();
}
child_range clang::CXXRewrittenBinaryOperator::children()
const_child_range clang::BinaryOperator::children() const
bool clang::ImplicitCastExpr::isPartOfExplicitCast() const

