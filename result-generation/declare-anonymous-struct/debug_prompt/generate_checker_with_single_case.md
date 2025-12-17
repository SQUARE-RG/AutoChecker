针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp生成first checker
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
TranslationUnitDecl 0x560fe5b88f58 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x560fe5c4efa0 <line:12:1, line:16:1> line:12:5 main 'int ()'
  `-CompoundStmt 0x560fe5c50bd0 <col:16, line:16:1>
    |-DeclStmt 0x560fe5c50a80 <line:13:5, col:19>
    | `-VarDecl 0x560fe5c4f0a0 <col:5, col:18> col:18 used o 'struct Outer':'Outer' callinit
    |   `-CXXConstructExpr 0x560fe5c50a58 <col:18> 'struct Outer':'Outer' 'void () noexcept'
    |-BinaryOperator 0x560fe5c50b80 <line:14:5, col:20> 'int' lvalue '='
    | |-MemberExpr 0x560fe5c50b30 <col:5, col:7> 'int' lvalue .deep_value 0x560fe5c4ec50
    | | `-MemberExpr 0x560fe5c50b00 <col:5, col:7> 'Outer::(anonymous struct at /root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp:5:9)' lvalue . 0x560fe5c4ed18
    | |   `-MemberExpr 0x560fe5c50ab8 <col:5, col:7> 'Outer::(anonymous struct at /root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct/declare_anonymous_struct_case_3.cpp:4:5)' lvalue . 0x560fe5c4ee38
    | |     `-DeclRefExpr 0x560fe5c50a98 <col:5> 'struct Outer':'Outer' lvalue Var 0x560fe5c4f0a0 'o' 'struct Outer':'Outer'
    | `-IntegerLiteral 0x560fe5c50b60 <col:20> 'int' 100
    `-ReturnStmt 0x560fe5c50bc0 <line:15:5, col:12>
      `-IntegerLiteral 0x560fe5c50ba0 <col:12> 'int' 0


## reference logic step
**logic for registerMatchers**:
Define a matcher for a RecordDecl (struct/union/class) that is a definition, binding it as 'record'
Within the RecordDecl, traverse its fields using the hasDescendant matcher to find all FieldDecl nodes, binding them as 'field'
For each bound FieldDecl, check if its type is an ElaboratedType (e.g., 'struct X') or a RecordType, and retrieve the underlying RecordDecl of that type
Check if the underlying RecordDecl is an anonymous struct/union by verifying it has no name (isAnonymousStructOrUnion()) and is a direct child of the outer RecordDecl (i.e., defined inline)
Ensure the matcher only triggers for anonymous structs/unions that are direct members of another struct (not standalone)
Combine the conditions into a single matcher that matches the outer RecordDecl when it contains such an anonymous nested RecordDecl
**logic for check**:
Retrieve the bound outer RecordDecl node ('record') and the anonymous FieldDecl node ('field') from the match result
Get the source location of the anonymous struct/union for diagnostic reporting
Verify the anonymous struct/union is indeed a direct member of the outer struct (not a typedef or other construct)
Emit a diagnostic message at the source location indicating the presence of a prohibited anonymous struct within a struct definition
Include the name of the outer struct in the diagnostic message if available for better context


## reference astMatchers
Node Matcher: namedDecl
 Parameters;Matcher<NamedDecl>...
 return type Matcher<Decl>
 Description: Matches a declaration of anything that could have a name.

Example matches X, S, the anonymous union type, i, and U;
  typedef int X;
  struct S {
    union {
      int i;
    } U;
  };

Narrowing Matcher: isAnonymous
 Parameters;
 return type Matcher<NamespaceDecl>
 Description: Matches anonymous namespace declarations.

Given
  namespace n {
  namespace {} // #1
  }
namespaceDecl(isAnonymous()) will match #1 but not ::n.

Narrowing Matcher: equalsBoundNode
 Parameters;std::string ID
 return type Matcher<Decl>
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

Node Matcher: recordDecl
 Parameters;Matcher<RecordDecl>...
 return type Matcher<Decl>
 Description: Matches class, struct, and union declarations.

Example matches X, Z, U, and S
  class X;
  template&lt;class T&gt; class Z {};
  struct S {};
  union U {};

Node Matcher: recordType
 Parameters;Matcher<RecordType>...
 return type Matcher<Type>
 Description: Matches record types (e.g. structs, classes).

Given
  class C {};
  struct S {};

  C c;
  S s;

recordType() matches the type of the variable declarations of both c
and s.

const auto Record = cxxRecordDecl(unless(matchers::matchesAnyListedName(IgnoredContainers)), isSameOrDerivedFrom(namedDecl(has(cxxMethodDecl(isPublic(), hasName("data")).bind("data"))).bind("container"))).bind("record");
recordDecl(isUnion())
if (StructFieldTy->isIncompleteType()) return;
AST_MATCHER_P(CXXRecordDecl, baseOfBoundNode, std::string, ID) {
  return Builder->removeBindings(
      [&](const ast_matchers::internal::BoundNodesMap &Nodes) {
        const auto *Derived = Nodes.getNodeAs<CXXRecordDecl>(ID);
        return Derived != &Node && !Derived->isDerivedFrom(&Node);
      });
}
cxxDestructorDecl(isDefinition(), unless(ofClass(IsUnionLikeClass)))
Finder->addMatcher(cxxRecordDecl(hasBases(), isDefinition()).bind("decl"), this);


## reference api  
auto DiagBuilder = diag(Member->getMemberLoc(),
                     "accessing an element of the container does not require a call to "
                     "'data()'; did you mean to use 'operator[]'?");
const RecordDecl *RecDecl = BaseType->getAsCXXRecordDecl();
if (!RecDecl || RecDecl->getIdentifier() == nullptr)
  return;
StringRef CodeOfAssignedExpr = Lexer::getSourceText(
    CharSourceRange::getTokenRange(PtrResultExpr->getSourceRange()), SM,
    getLangOpts());
diag(D->getBeginLoc(),
     "using declarations in the global namespace in headers are prohibited");
const auto *Struct = Result.Nodes.getNodeAs<RecordDecl>("struct");
if (!Struct)
  return;
IdentifierInfo * clang::OffsetOfNode::getFieldName() const
const FileEntry * clang::Preprocessor::getHeaderToIncludeForDiagnostics(SourceLocation IncLoc, SourceLocation MLoc)
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
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl().bind("x"), this);
}

void DeclareAnonymousStructCheck::check(const MatchFinder::MatchResult &Result) {
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