针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp生成first checker
# Inputs

## rule
**Rule Description:**
This rule prohibits the inclusion of anonymous structs (i.e., nested struct types without a variable name) within struct definitions. An anonymous struct refers to a type that is directly embedded inside an outer struct but lacks an explicit variable name identifier. If a nested struct is assigned a specific variable name, it complies with the rule. This rule applies to all levels of struct nesting, including multi-level scenarios, and covers direct members of structs regardless of their scope (global or local).
Scenarios that should be reported include: structs containing directly defined anonymous structs (without a variable name), anonymous unions within structs, multi-level nested structs with anonymous structs at any level, and anonymous structs appearing as members of other structs.
Correct scenarios include: nested structs having explicit variable names, structs defined and used normally without any nested anonymous structs, named structs appearing as members within an outer struct, and struct types defined via typedef.
Note: The term "anonymous struct" specifically denotes a nested struct that is defined inline without a named identifier, distinguishing it from standalone unnamed structs which are not covered by this rule.

## test case code
**Test Case Code:**
```cpp
#include <stdio.h>

struct Outer {
    struct {
        struct {
            int deep_value;
        };  // 违反：多层匿名结构体嵌套
        // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
    };
};

int main(void) {
    struct Outer o;
    o.deep_value = 100;
    return 0;
}
```

## AST
TranslationUnitDecl 0x558924839f58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x5589248fffa0 <line:12:1, line:16:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x558924901bd0 <col:16, line:16:1>
    |-DeclStmt 0x558924901a80 <line:13:5, col:19>
    | `-VarDecl 0x5589249000a0 <col:5, col:18> col:18 used o 'struct Outer':'Outer' callinit
    |   `-CXXConstructExpr 0x558924901a58 <col:18> 'struct Outer':'Outer' 'void () noexcept'
    |-BinaryOperator 0x558924901b80 <line:14:5, col:20> 'int' lvalue '='
    | |-MemberExpr 0x558924901b30 <col:5, col:7> 'int' lvalue .deep_value 0x5589248ffc50
    | | `-MemberExpr 0x558924901b00 <col:5, col:7> 'Outer::(anonymous struct at /root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp:5:9)' lvalue . 0x5589248ffd18
    | |   `-MemberExpr 0x558924901ab8 <col:5, col:7> 'Outer::(anonymous struct at /root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp:4:5)' lvalue . 0x5589248ffe38
    | |     `-DeclRefExpr 0x558924901a98 <col:5> 'struct Outer':'Outer' lvalue Var 0x5589249000a0 'o' 'struct Outer':'Outer'
    | `-IntegerLiteral 0x558924901b60 <col:20> 'int' 100
    `-ReturnStmt 0x558924901bc0 <line:15:5, col:12>
      `-IntegerLiteral 0x558924901ba0 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
1. Match record declarations (struct/union) that are directly defined inside another struct/union without a name, using `recordDecl(isAnonymousStructOrUnion())`
2. Ensure the anonymous record is nested within a struct/union by matching `recordDecl(isAnonymousStructOrUnion(), hasAncestor(recordDecl(isStruct())))`
3. Bind the anonymous record declaration as 'anonymousRecord' for diagnostic reporting
4. Optionally match all levels of nesting by allowing the matcher to trigger for anonymous records at any depth within the outer struct
**logic for check**:
1. Retrieve the bound anonymous RecordDecl node via `Result.Nodes.getNodeAs<RecordDecl>("anonymousRecord")`
2. Check that the matched record is indeed anonymous (i.e., has no name) and is a struct/union type
3. Verify that the anonymous record is a direct or indirect member of an outer struct (not a standalone anonymous type)
4. Emit a diagnostic message indicating that anonymous structs/unions are prohibited inside struct definitions


## reference astMatchers
AST Traversal Matcher: eachOf
 Parameters;Matcher<*>, ..., Matcher<*>
 Return type Matcher<*>
 Description: Matches if any of the given matchers matches.

Unlike anyOf, eachOf will generate a match result for each
matching submatcher.

For example, in:
  class A { int a; int b; };
The matcher:
  cxxRecordDecl(eachOf(has(fieldDecl(hasName("a")).bind("v")),
                       has(fieldDecl(hasName("b")).bind("v"))))
will generate two results binding "v", the first of which binds
the field declaration of a, the second the field declaration of
b.

Usable as: Any Matcher

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

Narrowing Matcher: isInAnonymousNamespace
 Parameters;
 return type Matcher<Decl>
 Description: Matches declarations in an anonymous namespace.

Given
  class vector {};
  namespace foo {
    class vector {};
    namespace {
      class vector {}; // #1
    }
  }
  namespace {
    class vector {}; // #2
    namespace foo {
      class vector{}; // #3
    }
  }
cxxRecordDecl(hasName("vector"), isInAnonymousNamespace()) will match
#1, #2 and #3.

Finder->addMatcher(namedDecl(anyOf(functionDecl(isDefinition(), isStaticStorageClass()), varDecl(isDefinition(), isStaticStorageClass())), isInAnonymousNamespace()).bind("static-def"), this);
AST_MATCHER_P2(Expr, hasSizeOfDescendant, int, Depth,
               ast_matchers::internal::Matcher<Expr>, InnerMatcher) {
  if (Depth < 0)
    return false;

  const Expr *E = Node.IgnoreParenImpCasts();
  if (InnerMatcher.matches(*E, Finder, Builder))
    return true;

  if (const auto *CE = dyn_cast<CastExpr>(E)) {
    const auto M = hasSizeOfDescendant(Depth - 1, InnerMatcher);
    return M.matches(*CE->getSubExpr(), Finder, Builder);
  }
  if (const auto *UE = dyn_cast<UnaryOperator>(E)) {
    const auto M = hasSizeOfDescendant(Depth - 1, InnerMatcher);
    return M.matches(*UE->getSubExpr(), Finder, Builder);
  }
  if (const auto *BE = dyn_cast<BinaryOperator>(E)) {
    const auto LHS = hasSizeOfDescendant(Depth - 1, InnerMatcher);
    const auto RHS = hasSizeOfDescendant(Depth - 1, InnerMatcher);
    return LHS.matches(*BE->getLHS(), Finder, Builder) ||
           RHS.matches(*BE->getRHS(), Finder, Builder);
  }

  return false;
}
auto ShouldIgnoreRecord = allOf(boolean(IgnoreClassesWithAllMemberVariablesBeingPublic), unless(hasNonPublicMemberVariable()));


## reference api
const auto *Literal = Result.Nodes.getNodeAs<StringLiteral>("literal");
const auto *FindFunc = Result.Nodes.getNodeAs<FunctionDecl>("func");
const auto *Struct = Result.Nodes.getNodeAs<RecordDecl>("struct");
if (!Struct)
  return;
const auto *RecordDecl = Result.Nodes.getNodeAs<CXXRecordDecl>("record_decl");
if (!RecordDecl)
  return;
void clang::RecordDecl::setAnonymousStructOrUnion(bool Anon)
bool clang::RecordDecl::isAnonymousStructOrUnion() const
bool clang::FieldDecl::isAnonymousStructOrUnion() const


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DeclareAnonymousStructCheck.cpp :
```cpp
//===--- DeclareAnonymousStructCheck.cpp - clang-tidy ---------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "DeclareAnonymousStructCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void DeclareAnonymousStructCheck::registerMatchers(MatchFinder *Finder) {
  Finder->addMatcher(
      fieldDecl(
          hasType(recordDecl(isAnonymousStructOrUnion())),
          hasParent(recordDecl(isDefinition()))
      ).bind("anonymous_field"),
      this);
}

void DeclareAnonymousStructCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *MatchedField = Result.Nodes.getNodeAs<FieldDecl>("anonymous_field");
  if (!MatchedField)
    return;

  diag(MatchedField->getLocation(), "禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]");
}

} // namespace clang::tidy::ucassaat
```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/DeclareAnonymousStructCheck.h :
```cpp
//===--- DeclareAnonymousStructCheck.h - clang-tidy -------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DECLAREANONYMOUSSTRUCTCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DECLAREANONYMOUSSTRUCTCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/declare-anonymous-struct.html
class DeclareAnonymousStructCheck : public ClangTidyCheck {
public:
  DeclareAnonymousStructCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_DECLAREANONYMOUSSTRUCTCHECK_H
```
