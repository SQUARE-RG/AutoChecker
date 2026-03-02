针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr/dependent_call_in_expr_case_9.cpp增强checker
# Instruction
You are a clang-tidy expert, proficient in LLVM/Clang AST analysis and static checker development.

Your task is to generate an enhanced checker code based on the provided rules, the current checker's source code, the passed test cases, and the failed test cases. You may refer to the reference logic steps, reference AST matchers, and reference code snippets.

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
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallSet.h"
#include "llvm/ADT/SmallVector.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Helper function to collect all CallExpr nodes within an expression
void collectCallExprs(const Expr *E, llvm::SmallVectorImpl<const CallExpr *> &Calls) {
  if (!E) return;
  
  E = E->IgnoreParenImpCasts();
  
  if (const auto *CE = dyn_cast<CallExpr>(E)) {
    Calls.push_back(CE);
    // Don't return, continue to traverse arguments
  }
  
  // Traverse all children of the expression
  for (const Stmt *Child : E->children()) {
    if (const auto *ChildExpr = dyn_cast<Expr>(Child)) {
      collectCallExprs(ChildExpr, Calls);
    }
  }
}

// Helper function to check if two expressions refer to the same memory location
bool refersToSameLocation(const Expr *E1, const Expr *E2, ASTContext &Context) {
  if (!E1 || !E2) return false;
  
  E1 = E1->IgnoreParenImpCasts();
  E2 = E2->IgnoreParenImpCasts();
  
  // Handle address-of operator
  if (const auto *UO1 = dyn_cast<UnaryOperator>(E1)) {
    if (UO1->getOpcode() == UO_AddrOf) {
      E1 = UO1->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  if (const auto *UO2 = dyn_cast<UnaryOperator>(E2)) {
    if (UO2->getOpcode() == UO_AddrOf) {
      E2 = UO2->getSubExpr()->IgnoreParenImpCasts();
    }
  }
  
  // Check if both are DeclRefExpr to the same variable
  if (const auto *DRE1 = dyn_cast<DeclRefExpr>(E1)) {
    if (const auto *DRE2 = dyn_cast<DeclRefExpr>(E2)) {
      return DRE1->getDecl() == DRE2->getDecl();
    }
  }
  
  // Check if both are MemberExpr accessing the same member
  if (const auto *ME1 = dyn_cast<MemberExpr>(E1)) {
    if (const auto *ME2 = dyn_cast<MemberExpr>(E2)) {
      return ME1->getMemberDecl() == ME2->getMemberDecl() &&
             refersToSameLocation(ME1->getBase(), ME2->getBase(), Context);
    }
  }
  
  // For array subscript, check if base and index are the same
  if (const auto *ASE1 = dyn_cast<ArraySubscriptExpr>(E1)) {
    if (const auto *ASE2 = dyn_cast<ArraySubscriptExpr>(E2)) {
      return refersToSameLocation(ASE1->getBase(), ASE2->getBase(), Context) &&
             refersToSameLocation(ASE1->getIdx(), ASE2->getIdx(), Context);
    }
  }
  
  return false;
}

// Check if a parameter type could introduce data dependency
bool isDependencyType(QualType Type) {
  Type = Type.getNonReferenceType();
  
  // Pointer to non-const type
  if (const auto *PtrType = Type->getAs<PointerType>()) {
    return !PtrType->getPointeeType().isConstQualified();
  }
  
  // Reference to non-const type
  if (Type->isReferenceType()) {
    return !Type.getNonReferenceType().isConstQualified();
  }
  
  return false;
}

// Check if a function accesses global variables (including through no parameters)
bool accessesGlobalOrStatic(const FunctionDecl *Func, ASTContext &Context) {
  if (!Func) return false;
  
  // Check if function has no parameters but accesses globals
  if (Func->getNumParams() == 0) {
    // Check if function accesses global/static variables
    if (Func->hasBody()) {
      const Stmt *Body = Func->getBody();
      if (!Body) return false;
      
      // Check all DeclRefExpr in the body for global variables
      llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
      for (const Stmt *Child : Body->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          DeclRefs.push_back(DRE);
        }
      }
      
      for (const DeclRefExpr *DRE : DeclRefs) {
        if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
          if (VD->hasGlobalStorage() && !VD->isStaticLocal()) {
            return true;
          }
        }
      }
    }
    return false;
  }
  
  // Check if any parameter could point to global/static data
  for (unsigned i = 0; i < Func->getNumParams(); ++i) {
    const ParmVarDecl *Param = Func->getParamDecl(i);
    if (isDependencyType(Param->getType())) {
      return true;
    }
  }
  
  return false;
}

// Check if a function accesses a specific global variable
bool accessesSpecificGlobal(const FunctionDecl *Func, const VarDecl *Global, ASTContext &Context) {
  if (!Func || !Global) return false;
  
  // Check if the function directly references this global variable
  if (Func->hasBody()) {
    const Stmt *Body = Func->getBody();
    if (!Body) return false;
    
    // Check all DeclRefExpr in the body
    llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
    for (const Stmt *Child : Body->children()) {
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
        DeclRefs.push_back(DRE);
      }
    }
    
    for (const DeclRefExpr *DRE : DeclRefs) {
      if (DRE->getDecl() == Global) {
        return true;
      }
    }
  }
  
  return false;
}

// Check if a function accesses static local variables
bool accessesStaticLocal(const FunctionDecl *Func, ASTContext &Context) {
  if (!Func) return false;
  
  if (Func->hasBody()) {
    const Stmt *Body = Func->getBody();
    if (!Body) return false;
    
    // Check all DeclRefExpr in the body for static local variables
    llvm::SmallVector<const DeclRefExpr *, 8> DeclRefs;
    for (const Stmt *Child : Body->children()) {
      if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
        DeclRefs.push_back(DRE);
      }
    }
    
    for (const DeclRefExpr *DRE : DeclRefs) {
      if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
        if (VD->isStaticLocal()) {
          return true;
        }
      }
    }
  }
  
  return false;
}

// Check if two functions access the same static local variable
bool accessSameStaticLocal(const FunctionDecl *Func1, const FunctionDecl *Func2, ASTContext &Context) {
  if (!Func1 || !Func2) return false;
  
  // Collect static local variables accessed by Func1
  llvm::SmallSet<const VarDecl *, 4> Func1Statics;
  if (Func1->hasBody()) {
    const Stmt *Body1 = Func1->getBody();
    if (Body1) {
      for (const Stmt *Child : Body1->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal()) {
              Func1Statics.insert(VD);
            }
          }
        }
      }
    }
  }
  
  // Check if Func2 accesses any of the same static local variables
  if (Func2->hasBody()) {
    const Stmt *Body2 = Func2->getBody();
    if (Body2) {
      for (const Stmt *Child : Body2->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal() && Func1Statics.count(VD)) {
              return true;
            }
          }
        }
      }
    }
  }
  
  return false;
}

// Check if two functions access static local variables with the same name
bool accessStaticLocalWithSameName(const FunctionDecl *Func1, const FunctionDecl *Func2, ASTContext &Context) {
  if (!Func1 || !Func2) return false;
  
  // Collect static local variable names accessed by Func1
  llvm::SmallSet<std::string, 4> Func1StaticNames;
  if (Func1->hasBody()) {
    const Stmt *Body1 = Func1->getBody();
    if (Body1) {
      for (const Stmt *Child : Body1->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal()) {
              Func1StaticNames.insert(VD->getNameAsString());
            }
          }
        }
      }
    }
  }
  
  // Check if Func2 accesses static local variables with the same name
  if (Func2->hasBody()) {
    const Stmt *Body2 = Func2->getBody();
    if (Body2) {
      for (const Stmt *Child : Body2->children()) {
        if (const auto *DRE = dyn_cast<DeclRefExpr>(Child)) {
          if (const auto *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (VD->isStaticLocal() && Func1StaticNames.count(VD->getNameAsString())) {
              return true;
            }
          }
        }
      }
    }
  }
  
  return false;
}

// Check if two function calls have overlapping dependency arguments
bool haveDependencyOverlap(const CallExpr *Call1, const CallExpr *Call2, 
                          ASTContext &Context) {
  const FunctionDecl *Func1 = Call1->getDirectCallee();
  const FunctionDecl *Func2 = Call2->getDirectCallee();
  
  // If we can't resolve the callee, conservatively assume dependency
  if (!Func1 || !Func2) {
    return true;
  }
  
  // Check if both functions access static local variables
  bool func1AccessesStaticLocal = accessesStaticLocal(Func1, Context);
  bool func2AccessesStaticLocal = accessesStaticLocal(Func2, Context);
  
  // If both functions access static local variables, check if they access the same one
  if (func1AccessesStaticLocal && func2AccessesStaticLocal) {
    if (accessSameStaticLocal(Func1, Func2, Context)) {
      return true;
    }
    // Also check if they access static locals with the same name
    // This handles the case where each function has its own static local with the same name
    if (accessStaticLocalWithSameName(Func1, Func2, Context)) {
      return true;
    }
  }
  
  // Check if both functions access global/static variables
  bool func1AccessesGlobal = accessesGlobalOrStatic(Func1, Context);
  bool func2AccessesGlobal = accessesGlobalOrStatic(Func2, Context);
  
  // If both functions access global/static variables, they might access the same one
  if (func1AccessesGlobal && func2AccessesGlobal) {
    // Get all global variables in the translation unit
    const TranslationUnitDecl *TU = Context.getTranslationUnitDecl();
    for (const Decl *D : TU->decls()) {
      if (const auto *VD = dyn_cast<VarDecl>(D)) {
        if (VD->hasGlobalStorage() && !VD->isStaticLocal()) {
          // Check if both functions access this specific global variable
          bool func1Accesses = accessesSpecificGlobal(Func1, VD, Context);
          bool func2Accesses = accessesSpecificGlobal(Func2, VD, Context);
          
          // If both functions access the same global variable, they are dependent
          if (func1Accesses && func2Accesses) {
            return true;
          }
        }
      }
    }
    
    // For functions with no parameters that access globals, we need to be conservative
    // If both access globals but we can't determine if they access the same one,
    // we should still report a violation when they're in the same expression
    // This handles the case where increment_x modifies global x and check_x reads it
    return true;
  }
  
  // Check each parameter combination for direct overlap
  for (unsigned i = 0; i < Call1->getNumArgs() && i < Func1->getNumParams(); ++i) {
    QualType ParamType1 = Func1->getParamDecl(i)->getType();
    if (!isDependencyType(ParamType1)) continue;
    
    const Expr *Arg1 = Call1->getArg(i);
    
    for (unsigned j = 0; j < Call2->getNumArgs() && j < Func2->getNumParams(); ++j) {
      QualType ParamType2 = Func2->getParamDecl(j)->getType();
      if (!isDependencyType(ParamType2)) continue;
      
      const Expr *Arg2 = Call2->getArg(j);
      
      if (refersToSameLocation(Arg1, Arg2, Context)) {
        return true;
      }
    }
  }
  
  return false;
}

} // namespace

void DependentCallInExprCheck::registerMatchers(MatchFinder *Finder) {
  // Match all expressions to catch any expression that could contain multiple function calls
  Finder->addMatcher(expr().bind("topLevelExpr"), this);
}

void DependentCallInExprCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *TopLevel = Result.Nodes.getNodeAs<Expr>("topLevelExpr");
  if (!TopLevel || !TopLevel->getBeginLoc().isValid()) return;
  
  // Skip if this is not a top-level expression (e.g., part of a larger expression)
  // We only want to check expressions that are not subexpressions of other expressions
  // we're already checking
  if (const auto *Parent = dyn_cast_or_null<Expr>(TopLevel->IgnoreParenImpCasts())) {
    // Check if this expression is a direct child of another expression we would match
    // This prevents duplicate checking
    if (Parent != TopLevel) {
      // This is a subexpression, skip it as it will be checked when we process its parent
      return;
    }
  }
  
  // Collect all CallExprs within this top-level expression
  llvm::SmallVector<const CallExpr *, 4> Calls;
  collectCallExprs(TopLevel, Calls);
  
  // Need at least 2 calls to have a potential violation
  if (Calls.size() < 2) return;
  
  // Check each pair of calls for dependency overlap
  for (unsigned i = 0; i < Calls.size(); ++i) {
    for (unsigned j = i + 1; j < Calls.size(); ++j) {
      if (haveDependencyOverlap(Calls[i], Calls[j], *Result.Context)) {
        diag(TopLevel->getBeginLoc(), 
             "禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]");
        return; // Report only once per expression
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

/// Checks for multiple related function calls in the same expression.
/// Related functions refer to functions called in the same expression that 
/// have a data dependency relationship, which will result in undefined behavior.
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

struct Data {
    int count;
    int total;
};

int update_count(struct Data *data) {
    data->count++;
    return data->count;
}

int calculate_total(struct Data *data) {
    data->total = data->count * 10;
    return data->total;
}

int main(void) {
    struct Data my_data = {5, 0};
    int result = update_count(&my_data) + calculate_total(&my_data);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
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

## failed test cases code
This test case should report an issue, but the current checker code cannot detect this code's problem.
```cpp
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
```

### ast of  failed test cases 
TranslationUnitDecl 0x557d6a55cf48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x557d6a622d80 <line:14:1, line:17:1> line:14:5 compute_result 'int ()'
  `-CompoundStmt 0x557d6a622fc0 <col:26, line:17:1>
    `-ReturnStmt 0x557d6a622fb0 <line:15:5, col:52>
      `-BinaryOperator 0x557d6a622f90 <col:12, col:52> 'int' '*'
        |-CallExpr 0x557d6a622ed0 <col:12, col:30> 'int'
        | `-ImplicitCastExpr 0x557d6a622eb8 <col:12> 'int (*)()' <FunctionToPointerDecay>
        |   `-DeclRefExpr 0x557d6a622e70 <col:12> 'int ()' lvalue Function 0x557d6a6229f0 'increment_counter' 'int ()'
        `-CallExpr 0x557d6a622f70 <col:34, col:52> 'int'
          `-ImplicitCastExpr 0x557d6a622f58 <col:34> 'int (*)()' <FunctionToPointerDecay>
            `-DeclRefExpr 0x557d6a622f38 <col:34> 'int ()' lvalue Function 0x557d6a622bd8 'get_counter_value' 'int ()'



## reference logic step
[{'logic_registerMatchers': ['1. Match all expressions to capture any code location that could contain multiple function calls', "2. Use expr() matcher to bind the top-level expression node as 'topLevelExpr'", '3. Ensure the matcher triggers for all expression types including binary operations, conditional operators, and comma expressions', '4. The matcher must be broad enough to catch any expression context where multiple function calls could appear'], 'logic_check': ["1. Retrieve the bound top-level expression node using Result.Nodes.getNodeAs<Expr>('topLevelExpr')", '2. Validate the expression exists and has a valid source location', '3. Filter out subexpressions by checking if the current expression is a direct child of another expression we would match', '4. Collect all CallExpr nodes within the top-level expression using a recursive helper function', '5. Skip checking if fewer than 2 function calls are found in the expression', '6. For each pair of function calls in the expression, check for dependency overlap', '7. Check if both functions access static local variables and if they access the same static local or ones with the same name', '8. Check if both functions access global/static variables by examining all global variables in the translation unit', '9. For functions with no parameters that access globals, conservatively assume dependency when both access globals', '10. Check parameter combinations for direct overlap by comparing arguments that refer to the same memory location', '11. If any pair of calls shows dependency overlap, emit a diagnostic at the top-level expression location', '12. Report only once per expression even if multiple dependent pairs exist']}]

## reference astMatchers
Narrowing Matcher: equals
 Parameters;double Value
 return type Matcher<CXXBoolLiteralExpr>
 Description: 

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

Narrowing Matcher: argumentCountAtLeast
 Parameters;unsigned N
 return type Matcher<CallExpr>
 Description: Checks that a call expression or a constructor call expression has at least
the specified number of arguments (including absent default arguments).

Example matches f(0, 0) and g(0, 0, 0)
(matcher = callExpr(argumentCountAtLeast(2)))
  void f(int x, int y);
  void g(int x, int y, int z);
  f(0, 0);
  g(0, 0, 0);

Node Matcher: chooseExpr
 Parameters;Matcher<ChooseExpr>...
 return type Matcher<Stmt>
 Description: Matches GNU __builtin_choose_expr.

callExpr(unless(anyOf(argumentCountIs(0), argumentCountIs(1)))).bind("functionCall")
Finder->addMatcher(callExpr().bind("CE"), this);
Finder->addMatcher(predefinedExpr(hasAncestor(lambdaExpr())).bind("E"), this);
expr(anyOf(ComparisonUnaryOperator, ComparisonBinaryOperator))


## reference code snippets  
IdDependentBackwardBranchCheck::IdDependencyRecord *
IdDependentBackwardBranchCheck::hasIdDepVar(const Expr *Expression) {
  if (const auto *Declaration = dyn_cast<DeclRefExpr>(Expression)) {
    const auto *CheckVariable = dyn_cast<VarDecl>(Declaration->getDecl());
    auto FoundVariable = IdDepVarsMap.find(CheckVariable);
    if (FoundVariable == IdDepVarsMap.end())
      return nullptr;
    return &(FoundVariable->second);
  }
  for (const auto *Child : Expression->children())
    if (const auto *ChildExpression = dyn_cast<Expr>(Child))
      if (IdDependencyRecord *Result = hasIdDepVar(ChildExpression))
        return Result;
  return nullptr;
}
Expr *findCallExpr(const CallGraphNode *Caller, const CallGraphNode *Callee) {
  auto FoundCallee = llvm::find_if(
      Caller->callees(), [Callee](const CallGraphNode::CallRecord &Call) {
        return Call.Callee == Callee;
      });
  assert(FoundCallee != Caller->end() &&
         "Callee should be called from the caller function here.");
  return FoundCallee->CallExpr;
}
static bool haveSameNamespaceOrTranslationUnit(const CXXRecordDecl *Decl1,
                                               const CXXRecordDecl *Decl2) {
  const DeclContext *ParentDecl1 = Decl1->getLexicalParent();
  const DeclContext *ParentDecl2 = Decl2->getLexicalParent();

  if (ParentDecl1->getDeclKind() == Decl::TranslationUnit ||
      ParentDecl2->getDeclKind() == Decl::TranslationUnit) {
    return ParentDecl1 == ParentDecl2;
  }
  assert(ParentDecl1->getDeclKind() == Decl::Namespace &&
         "ParentDecl1 declaration must be a namespace");
  assert(ParentDecl2->getDeclKind() == Decl::Namespace &&
         "ParentDecl2 declaration must be a namespace");
  auto *Ns1 = NamespaceDecl::castFromDeclContext(ParentDecl1);
  auto *Ns2 = NamespaceDecl::castFromDeclContext(ParentDecl2);
  return Ns1->getOriginalNamespace() == Ns2->getOriginalNamespace();
}
assert(Range.isValid() && "Exception Source Range is invalid.");
if (IndexExpr->isValueDependent())
  return;
for (const auto *FD : Diagnose)
  diag(FD->getLocation(), "declaration of %0 has no matching declaration "
                          "of '%1' at the same scope")
      << FD << getOperatorName(getCorrespondingOverload(FD));
bool IsSamePtrExpr::check(const Expr *E1, const Expr *E2) {
  E1 = E1->IgnoreParenCasts();
  E2 = E2->IgnoreParenCasts();
  OtherE = E2;
  return Visit(const_cast<Expr *>(E1));
}
static bool isCallExprNamed(const Expr *E, StringRef Name) {
  const auto *CE = dyn_cast<CallExpr>(E->IgnoreImplicit());
  if (!CE)
    return false;
  const auto *ND = dyn_cast<NamedDecl>(CE->getCalleeDecl());
  if (!ND)
    return false;
  return ND->getQualifiedNameAsString() == Name;
}
const auto *D = Result.Nodes.getNodeAs<NamedDecl>("decl");
const auto *BD = Result.Nodes.getNodeAs<NamedDecl>("type_decl");
const auto *E = Result.Nodes.getNodeAs<Expr>("expr");
if (hasPtrOrReferenceInFunc(Func, CondVar))
  return;
const auto *OuterCall = Result.Nodes.getNodeAs<CallExpr>("outer_call");
if (Variable) {
  diag(Variable->getLocation(), "variable %0 is non-const and globally "
                              "accessible, consider making it const")
      << Variable;
}
bool clang::QualType::isAddressSpaceOverlapping(QualType T) const
bool clang::FunctionDecl::isGlobal() const
bool clang::ento::PathDiagnosticCallPiece::hasCallStackMessage()
bool clang::GenericSelectionExpr::isResultDependent() const
Expr * clang::ExpressionTraitExpr::getQueriedExpression() const
void clang::CallExpr::computeDependence()
bool clang::VarDecl::isStaticLocal() const
const_child_range clang::CallExpr::children() const
const_child_range clang::PredefinedExpr::children() const
bool clang::SourceLocation::isValid() const
bool clang::Expr::hasNonTrivialCall(const ASTContext & Ctx) const



# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the current checker code above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
    -In the check() function, all extracted nodes must be checked for non-null and isValid() to avoid direct usage

    **Example Output Format:**
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

