针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_else_branch/no_else_branch_case_5.cpp生成first checker
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
Prohibit omitting the else branch of if-else if statements. In all if-else if statement structures, the final else branch must be included, even if it does not perform any operations, and must be explicitly written. This is to ensure the logical integrity of the code and prevent undefined behavior due to omitted conditions. This rule applies to any conditional statement chain that contains one or more else if branches; the final else branch must exist to handle all uncovered condition scenarios. If the else branch is empty, it should include appropriate comments (e.g.,  Other cases not handled ). Compliant scenarios include if-else if statements that contain an else branch (whether empty or not), while non-compliant scenarios involve omitting the final else branch. The rule checks the structural integrity of conditional statements, not whether the else branch contains specific logic.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

int calculate_level(int value) {
    int level;
    if (value > 100) {
        level = 3;
    } else if (value > 50) {
        level = 2;
    } else if (value > 10) {
        level = 1;
    }
    level = 0;  // 违反：赋值语句代替else分支
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
    return level;
}

int main(void) {
    printf("%d\n", calculate_level(75));
    return 0;
}
```

## AST
TranslationUnitDecl 0x55c060d00f48 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x55c060dc6ba8 <line:17:1, line:20:1> line:17:5 main 'int ()'
  `-CompoundStmt 0x55c060dc6ef8 <col:16, line:20:1>
    |-CallExpr 0x55c060dc6e80 <line:18:5, col:39> 'int'
    | |-ImplicitCastExpr 0x55c060dc6e68 <col:5> 'int (*)(const char *__restrict, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x55c060dc6de8 <col:5> 'int (const char *__restrict, ...)' lvalue Function 0x55c060da31b8 'printf' 'int (const char *__restrict, ...)'
    | |-ImplicitCastExpr 0x55c060dc6eb0 <col:12> 'const char *' <ArrayToPointerDecay>
    | | `-StringLiteral 0x55c060dc6cd8 <col:12> 'const char[4]' lvalue "%d\n"
    | `-CallExpr 0x55c060dc6dc0 <col:20, col:38> 'int'
    |   |-ImplicitCastExpr 0x55c060dc6da8 <col:20> 'int (*)(int)' <FunctionToPointerDecay>
    |   | `-DeclRefExpr 0x55c060dc6d60 <col:20> 'int (int)' lvalue Function 0x55c060dc6598 'calculate_level' 'int (int)'
    |   `-IntegerLiteral 0x55c060dc6d40 <col:36> 'int' 75
    `-ReturnStmt 0x55c060dc6ee8 <line:19:5, col:12>
      `-IntegerLiteral 0x55c060dc6ec8 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Define a matcher for `IfStmt` nodes to capture the entire if-else if chain structure.
2. Within the `IfStmt` matcher, ensure it has an `else` branch (i.e., `hasElse(expr())`) to initially filter for compliant structures, but we will later invert the logic to find non-compliant ones.
3. To specifically target non-compliant chains (missing final `else`), create a matcher for `IfStmt` nodes that have at least one `else if` branch. This can be done by matching an `IfStmt` whose `else` branch is another `IfStmt` (i.e., `hasElse(stmt(hasDescendant(ifStmt())))`).
4. Further refine the matcher to catch chains that *lack* a final, non-`if` `else` branch. This is achieved by ensuring the final `else` branch is *not* a `NullStmt` or a compound statement that is effectively empty. However, since the rule requires *any* final `else`, we need to match chains where the final branch is another `IfStmt` (an `else if`) and there is no terminating `else` after it. This is complex; a simpler approach is to match all `IfStmt` nodes and in the `check` callback, traverse the chain to verify the presence of a final `else`.
5. Bind the top-level `IfStmt` node as 'ifChain' for inspection in the callback.
6. Optionally, bind the final `Else` part of the chain (if it exists) to examine its content, but the primary check is for its absence.
**logic for check**:
1. Retrieve the bound 'ifChain' `IfStmt` node from the match result.
2. Traverse the if-else if chain: Start from the top `IfStmt`. Check if it has an `else` branch. If the `else` branch is another `IfStmt`, continue traversing down that `IfStmt`'s `else` branches until a non-`IfStmt` `else` branch is found or no `else` branch exists.
3. If the traversal ends because an `IfStmt` node has no `else` branch, this indicates a missing final `else`. Emit a diagnostic message at the location of that final `IfStmt` (the last `else if`).
4. If the traversal finds a final `else` branch that is a `NullStmt` (a single semicolon) or an empty compound statement (`CompoundStmt` with no children), this is technically compliant but might warrant a different warning about an empty else. However, the rule states this is allowed, so no diagnostic is emitted.
5. The diagnostic should indicate that the final else branch is omitted and must be explicitly added, referencing the rule identifier.


## reference astMatchers
AST Traversal Matcher: hasElse
 Parameters;Matcher<Stmt> InnerMatcher
 Return type Matcher<IfStmt>
 Description: Matches the else-statement of an if statement.

Examples matches the if statement
  (matcher = ifStmt(hasElse(cxxBoolLiteral(equals(true)))))
  if (false) false; else true;

AST Traversal Matcher: hasTrueExpression
 Parameters;Matcher<Expr> InnerMatcher
 Return type Matcher<AbstractConditionalOperator>
 Description: Matches the true branch expression of a conditional operator.

Example 1 (conditional ternary operator): matches a
  condition ? a : b

Example 2 (conditional binary operator): matches opaqueValueExpr(condition)
  condition ?: b

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

Node Matcher: ifStmt
 Parameters;Matcher<IfStmt>...
 return type Matcher<Stmt>
 Description: Matches if statements.

Example matches 'if (x) {}'
  if (x) {}

AST_POLYMORPHIC_MATCHER_P(boolean, AST_POLYMORPHIC_SUPPORTED_TYPES(Stmt, Decl), bool, Boolean) { return Boolean; }
ifStmt(hasElse(stmt()))
static const DeclRefExpr *checkConditionVarUsageInElse(const IfStmt *If) {
  if (const VarDecl *CondVar = If->getConditionVariable())
    return findUsage(If->getElse(), CondVar->getID());
  return nullptr;
}
hasElse(stmt())
expr().bind("expr")


## reference api  
const auto *IfWithDelete = Result.Nodes.getNodeAs<IfStmt>("ifWithDelete");
const auto *Compound = Result.Nodes.getNodeAs<CompoundStmt>("compound");
bool TraverseIfStmt(IfStmt *Node, bool InElseIf = false) {
  if (!Node)
    return Base::TraverseIfStmt(Node);

  {
    CognitiveComplexity::Criteria Reasons;
    Reasons = CognitiveComplexity::Criteria::None;
    Reasons |= CognitiveComplexity::Criteria::Increment;
    Reasons |= CognitiveComplexity::Criteria::IncrementNesting;

    if (!InElseIf) {
      Reasons |= CognitiveComplexity::Criteria::PenalizeNesting;
    }

    CC.account(Node->getIfLoc(), CurrentNestingLevel, Reasons);
  }

  if (!InElseIf) {
    if (!TraverseStmt(Node->getInit()))
      return false;

    if (!TraverseStmt(Node->getCond()))
      return false;
  } else {
    if (!traverseStmtWithIncreasedNestingLevel(Node->getInit()))
      return false;

    if (!traverseStmtWithIncreasedNestingLevel(Node->getCond()))
      return false;
  }

  if (!traverseStmtWithIncreasedNestingLevel(Node->getThen()))
    return false;

  if (!Node->getElse())
    return true;

  if (auto *E = dyn_cast<IfStmt>(Node->getElse()))
    return TraverseIfStmt(E, true);

  {
    CognitiveComplexity::Criteria Reasons;
    Reasons = CognitiveComplexity::Criteria::Increment;
    Reasons |= CognitiveComplexity::Criteria::IncrementNesting;
    CC.account(Node->getElseLoc(), CurrentNestingLevel, Reasons);
  }

  return traverseStmtWithIncreasedNestingLevel(Node->getElse());
}
DiagnosticBuilder Diag = diag(ElseLoc, WarningMessage)
                       << ControlFlowInterruptor << SourceRange(ElseLoc);
removeElseAndBrackets(Diag, *Result.Context, Else, ElseLoc);
bool clang::CompoundStmt::body_empty() const
void clang::DiagnosticsEngine::setLastDiagnosticIgnored(bool Ignored)
const Stmt * clang::CapturedStmt::getCapturedStmt() const
const Stmt * clang::IfStmt::getElse() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoElseBranchCheck.cpp :
```cpp
//===--- NoElseBranchCheck.cpp - clang-tidy -------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "NoElseBranchCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void NoElseBranchCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void NoElseBranchCheck::check(const MatchFinder::MatchResult &Result) {
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
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/NoElseBranchCheck.h :
```cpp
//===--- NoElseBranchCheck.h - clang-tidy -----------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/no-else-branch.html
class NoElseBranchCheck : public ClangTidyCheck {
public:
  NoElseBranchCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_NOELSEBRANCHCHECK_H

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