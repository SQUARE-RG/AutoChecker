
You are a Clang ASTMatcher expert. Please extract the ASTMatcher DSL rules based on the source code of the following Clang-Tidy checker.

Checker source code:
```cpp
{{checker_code}}
```

Please analyze the content related to astMatcher in the check code and decompose the astMatcher-related content into atomic operations. For each atomic operation, provide:
    1. "meta_op": A clear description of the operatitchero. Summarize the core purpose of the matching operation.
    2. "meta_impl": The corresponding astMatcher code snippet,ensuring it is a valid code snippet that can be directly used in a Clang-tidy checker.


some requirements about meta_impl:
    - It should be a valid code snippet that can be directly used in a Clang-tidy checker.
    - If a custom matching function is used in addMatcher, please place the custom matching function and its usage in the code in the meta_impl field.
    - Decompose the implementation code into several atomic operations, but retain the implementation logic of each atomic operation.



**Output Format Requirements:**
    - Return ONLY a JSON array containing objects with the exact keys: "meta_op" and "meta_impl"
    - Do NOT include any explanations, preambles, suffixes, or code block markups
    - Do NOT add any additional keys or fields
    - Ensure the output is valid JSON that can be parsed directly
    
    
    
    **Example Output Format:**
    [
        {{{{
            "meta_op": "Match namespace alias declarations that are expanded in the main file",
            "meta_impl": "Finder->addMatcher(namespaceAliasDecl(isExpansionInMainFile()).bind(\"alias\"),this)"
        }}}},
        {{{{
            "meta_op": "Match C++ method declarations that are static",
            "meta_impl": "AST_MATCHER(CXXMethodDecl, isStatic) {{{{ return Node.isStatic(); }}}}\nFinder->addMatcher(cxxMethodDecl(isStatic()).bind(\"staticMethod\"), this)"
        }}}},
        {{{{
            "meta_op": "Match function declarations that are definitions",
            "meta_impl": "Finder->addMatcher(functionDecl(isDefinition()).bind(\"func\"), this)"
        }}}},
        {{{{
            "meta_op": "Match function declarations that have a body ",
            "meta_impl": "Finder->addMatcher(functionDecl(hasBody(stmt()).bind(\"function\"),this));"
        }}}},
        {{{{
            "meta_op": "Match a CXXMethodDecl that is an overloaded operator",
            "meta_impl": "AST_MATCHER(CXXMethodDecl, isOverloadedOperator) {{{{ return Node.isOverloadedOperator(); }}}}\n Finder->addMatcher(cxxMethodDecl(isOverloadedOperator()).bind(\"opMethod\"), this)"
        }}}}
    ]

First, you need to analyze the astMatcher-related content in the checker code, summarize the matching rules of the astMatcher DSL, and then output it in the specified format.








You are a **Clang ASTMatcher expert**. Your task is to extract and decompose all ASTMatcher DSL logic from the following Clang-Tidy checker source code.

# **Input**

**Checker source code:**

```cpp
{checker_code}
```
---

# **Your Task**

Analyze the checker’s implementation and extract **the ASTMatcher-related logic**, including:

* Matchers inside `registerMatchers`
* ASTMatcher-related helper functions
* Any matcher expressions embedded in `check` (if applicable)

Then **decompose** this logic into **atomic operations**, where each atomic operation represents a single conceptual matching task.

For each atomic operation, output:

## **1. `"meta_op"`**

* A clear description of the operation.

## **2. `"meta_impl"`**

* A **valid ASTMatcher code snippet** that can be directly used in a Clang-Tidy checker.
* Must reflect the atomic operation exactly.
* Preserve the implementation logic within each atomic unit.
* If a custom matching function is used in addMatcher, please place the custom matching function and its usage in the code in the meta_impl field.

---

## **Constraints for meta_impl**

* Must be valid C++ matcher code used by Clang-Tidy.
* If multiple atomic matchers exist in one combined matcher, break them apart but preserve the logic of each atomic unit.
* Do not omit any matcher-related logic from the source code.
* Do not rewrite or invent matchers that are not present.

---

# Example
checker code:
```cpp
//===--- ConvertMemberFunctionsToStatic.cpp - clang-tidy ------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "ConvertMemberFunctionsToStatic.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/DeclCXX.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang::tidy::readability {

AST_MATCHER(CXXMethodDecl, isStatic) { return Node.isStatic(); }

AST_MATCHER(CXXMethodDecl, hasTrivialBody) { return Node.hasTrivialBody(); }

AST_MATCHER(CXXMethodDecl, isOverloadedOperator) {
  return Node.isOverloadedOperator();
}

AST_MATCHER(CXXRecordDecl, hasAnyDependentBases) {
  return Node.hasAnyDependentBases();
}

AST_MATCHER(CXXMethodDecl, isTemplate) {
  return Node.getTemplatedKind() != FunctionDecl::TK_NonTemplate;
}

AST_MATCHER(CXXMethodDecl, isDependentContext) {
  return Node.isDependentContext();
}

AST_MATCHER(CXXMethodDecl, isInsideMacroDefinition) {
  const ASTContext &Ctxt = Finder->getASTContext();
  return clang::Lexer::makeFileCharRange(
             clang::CharSourceRange::getCharRange(
                 Node.getTypeSourceInfo()->getTypeLoc().getSourceRange()),
             Ctxt.getSourceManager(), Ctxt.getLangOpts())
      .isInvalid();
}

AST_MATCHER_P(CXXMethodDecl, hasCanonicalDecl,
              ast_matchers::internal::Matcher<CXXMethodDecl>, InnerMatcher) {
  return InnerMatcher.matches(*Node.getCanonicalDecl(), Finder, Builder);
}

AST_MATCHER(CXXMethodDecl, usesThis) {
  class FindUsageOfThis : public RecursiveASTVisitor<FindUsageOfThis> {
  public:
    bool Used = false;

    bool VisitCXXThisExpr(const CXXThisExpr *E) {
      Used = true;
      return false; // Stop traversal.
    }

    // If we enter a class declaration, don't traverse into it as any usages of
    // `this` will correspond to the nested class.
    bool TraverseCXXRecordDecl(CXXRecordDecl *RD) { return true; }

  } UsageOfThis;

  // TraverseStmt does not modify its argument.
  UsageOfThis.TraverseStmt(const_cast<Stmt *>(Node.getBody()));

  return UsageOfThis.Used;
}

void ConvertMemberFunctionsToStatic::registerMatchers(MatchFinder *Finder) {
  Finder->addMatcher(
      cxxMethodDecl(
          isDefinition(), isUserProvided(),
          unless(anyOf(
              isExpansionInSystemHeader(), isVirtual(), isStatic(),
              hasTrivialBody(), isOverloadedOperator(), cxxConstructorDecl(),
              cxxDestructorDecl(), cxxConversionDecl(), isTemplate(),
              isDependentContext(),
              ofClass(anyOf(
                  isLambda(),
                  hasAnyDependentBases()) // Method might become virtual
                                          // depending on template base class.
                      ),
              isInsideMacroDefinition(),
              hasCanonicalDecl(isInsideMacroDefinition()), usesThis())))
          .bind("x"),
      this);
}

/// Obtain the original source code text from a SourceRange.
static StringRef getStringFromRange(SourceManager &SourceMgr,
                                    const LangOptions &LangOpts,
                                    SourceRange Range) {
  if (SourceMgr.getFileID(Range.getBegin()) !=
      SourceMgr.getFileID(Range.getEnd()))
    return {};

  return Lexer::getSourceText(CharSourceRange(Range, true), SourceMgr,
                              LangOpts);
}

static SourceRange getLocationOfConst(const TypeSourceInfo *TSI,
                                      SourceManager &SourceMgr,
                                      const LangOptions &LangOpts) {
  assert(TSI);
  const auto FTL = TSI->getTypeLoc().IgnoreParens().getAs<FunctionTypeLoc>();
  assert(FTL);

  SourceRange Range{FTL.getRParenLoc().getLocWithOffset(1),
                    FTL.getLocalRangeEnd()};
  // Inside Range, there might be other keywords and trailing return types.
  // Find the exact position of "const".
  StringRef Text = getStringFromRange(SourceMgr, LangOpts, Range);
  size_t Offset = Text.find("const");
  if (Offset == StringRef::npos)
    return {};

  SourceLocation Start = Range.getBegin().getLocWithOffset(Offset);
  return {Start, Start.getLocWithOffset(strlen("const") - 1)};
}

void ConvertMemberFunctionsToStatic::check(
    const MatchFinder::MatchResult &Result) {
  const auto *Definition = Result.Nodes.getNodeAs<CXXMethodDecl>("x");

  // TODO: For out-of-line declarations, don't modify the source if the header
  // is excluded by the -header-filter option.
  DiagnosticBuilder Diag =
      diag(Definition->getLocation(), "method %0 can be made static")
      << Definition;

  // TODO: Would need to remove those in a fix-it.
  if (Definition->getMethodQualifiers().hasVolatile() ||
      Definition->getMethodQualifiers().hasRestrict() ||
      Definition->getRefQualifier() != RQ_None)
    return;

  const CXXMethodDecl *Declaration = Definition->getCanonicalDecl();

  if (Definition->isConst()) {
    // Make sure that we either remove 'const' on both declaration and
    // definition or emit no fix-it at all.
    SourceRange DefConst = getLocationOfConst(Definition->getTypeSourceInfo(),
                                              *Result.SourceManager,
                                              Result.Context->getLangOpts());

    if (DefConst.isInvalid())
      return;

    if (Declaration != Definition) {
      SourceRange DeclConst = getLocationOfConst(
          Declaration->getTypeSourceInfo(), *Result.SourceManager,
          Result.Context->getLangOpts());

      if (DeclConst.isInvalid())
        return;
      Diag << FixItHint::CreateRemoval(DeclConst);
    }

    // Remove existing 'const' from both declaration and definition.
    Diag << FixItHint::CreateRemoval(DefConst);
  }
  Diag << FixItHint::CreateInsertion(Declaration->getBeginLoc(), "static ");
}

} // namespace clang::tidy::readability


```

output:

```
[
    {{
        "meta_op": "Detect methods that are static",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isStatic) {{ return Node.isStatic(); }}"
    }},
    {{
        "meta_op": "Detect methods that have a trivial body",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, hasTrivialBody) {{ return Node.hasTrivialBody(); }}"
    }},
    {{
        "meta_op": "Detect methods that are overloaded operators",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isOverloadedOperator) {{ return Node.isOverloadedOperator(); }}"
    }},
    {{
        "meta_op": "Detect classes that have dependent base classes",
        "meta_impl": "AST_MATCHER(CXXRecordDecl, hasAnyDependentBases) {{ return Node.hasAnyDependentBases(); }}"
    }},
    {{
        "meta_op": "Detect methods that are templates",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isTemplate) {{ return Node.getTemplatedKind() != FunctionDecl::TK_NonTemplate; }}"
    }},
    {{
        "meta_op": "Detect methods that are in a dependent context",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isDependentContext) {{ return Node.isDependentContext(); }}"
    }},
    {{
        "meta_op": "Detect methods defined inside a macro definition",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isInsideMacroDefinition) {{\n  const ASTContext &Ctxt = Finder->getASTContext();\n  return clang::Lexer::makeFileCharRange(\n             clang::CharSourceRange::getCharRange(\n                 Node.getTypeSourceInfo()->getTypeLoc().getSourceRange()),\n             Ctxt.getSourceManager(), Ctxt.getLangOpts())\n      .isInvalid();\n}}"
    }},
    {{
        "meta_op": "Match the canonical declaration of a method against an inner matcher",
        "meta_impl": "AST_MATCHER_P(CXXMethodDecl, hasCanonicalDecl,\n              ast_matchers::internal::Matcher<CXXMethodDecl>, InnerMatcher) {{\n  return InnerMatcher.matches(*Node.getCanonicalDecl(), Finder, Builder);\n}}"
    }},
    {{
        "meta_op": "Detect methods whose body uses the 'this' pointer",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, usesThis) {{\n  class FindUsageOfThis : public RecursiveASTVisitor<FindUsageOfThis> {{\n  public:\n    bool Used = false;\n    bool VisitCXXThisExpr(const CXXThisExpr *E) {{\n      Used = true;\n      return false;\n    }}\n    bool TraverseCXXRecordDecl(CXXRecordDecl *RD) {{ return true; }}\n  }} UsageOfThis;\n  UsageOfThis.TraverseStmt(const_cast<Stmt *>(Node.getBody()));\n  return UsageOfThis.Used;\n}}"
    }},
    {{
        "meta_op": "Match methods that are definitions",
        "meta_impl": "cxxMethodDecl(isDefinition())"
    }},
    {{
        "meta_op": "Match methods that are user-provided",
        "meta_impl": "cxxMethodDecl(isUserProvided())"
    }},
    {{
        "meta_op": "Exclude methods expanded in system headers",
        "meta_impl": "cxxMethodDecl(isExpansionInSystemHeader())"
    }},
    {{
        "meta_op": "Exclude virtual methods",
        "meta_impl": "cxxMethodDecl(isVirtual())"
    }},
    {{
        "meta_op": "Exclude constructors",
        "meta_impl": "cxxMethodDecl(cxxConstructorDecl())"
    }},
    {{
        "meta_op": "Exclude destructors",
        "meta_impl": "cxxMethodDecl(cxxDestructorDecl())"
    }},
    {{
        "meta_op": "Exclude conversion operators",
        "meta_impl": "cxxMethodDecl(cxxConversionDecl())"
    }},
    {{
        "meta_op": "Exclude methods whose class is a lambda",
        "meta_impl": "ofClass(isLambda())"
    }},
    {{
        "meta_op": "Exclude methods whose class has dependent bases",
        "meta_impl": "ofClass(hasAnyDependentBases())"
    }},
    {{
        "meta_op": "Exclude methods whose class is either a lambda or has dependent bases",
        "meta_impl": "ofClass(anyOf(isLambda(), hasAnyDependentBases()))"
    }},
    {{
        "meta_op": "Exclude methods whose canonical declaration is inside a macro definition",
        "meta_impl": "cxxMethodDecl(hasCanonicalDecl(isInsideMacroDefinition()))"
    }},
    {{
        "meta_op": "Exclude methods that use the 'this' pointer",
        "meta_impl": "cxxMethodDecl(usesThis())"
    }},
    {{
        "meta_op": "Match methods that satisfy all required conditions for conversion to static",
        "meta_impl": "Finder->addMatcher(\n  cxxMethodDecl(\n    isDefinition(),\n    isUserProvided(),\n    unless(anyOf(\n      isExpansionInSystemHeader(),\n      isVirtual(),\n      isStatic(),\n      hasTrivialBody(),\n      isOverloadedOperator(),\n      cxxConstructorDecl(),\n      cxxDestructorDecl(),\n      cxxConversionDecl(),\n      isTemplate(),\n      isDependentContext(),\n      ofClass(anyOf(isLambda(), hasAnyDependentBases())),\n      isInsideMacroDefinition(),\n      hasCanonicalDecl(isInsideMacroDefinition()),\n      usesThis()))\n  ).bind(\"x\"),\n  this);"
    }}
]

```


# **Output Format Requirements**

Return **ONLY** a JSON array, where each element is an object containing the **exact** keys:

* `"meta_op"`
* `"meta_impl"`

**Do NOT:**

* include explanations
* include markdown code fences
* include extra fields or comments
* wrap the JSON in any additional text

## **Example Output Format**

```
[
    {{
        "meta_op": "Match namespace alias declarations that are expanded in the main file",
        "meta_impl": "Finder->addMatcher(namespaceAliasDecl(isExpansionInMainFile()).bind(\"alias\"), this)"
    }},
    {{
        "meta_op": "Match C++ method declarations that are static",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isStatic) {{ return Node.isStatic(); }}\nFinder->addMatcher(cxxMethodDecl(isStatic()).bind(\"staticMethod\"), this)"
    }},
    {{
        "meta_op": "Match function declarations that are definitions",
        "meta_impl": "Finder->addMatcher(functionDecl(isDefinition()).bind(\"func\"), this)"
    }},
    {{
        "meta_op": "Match function declarations that have a body",
        "meta_impl": "Finder->addMatcher(functionDecl(hasBody(stmt())).bind(\"function\"), this)"
    }},
    {{
        "meta_op": "Match CXXMethodDecl that is an overloaded operator",
        "meta_impl": "AST_MATCHER(CXXMethodDecl, isOverloadedOperator) {{ return Node.isOverloadedOperator(); }}\nFinder->addMatcher(cxxMethodDecl(isOverloadedOperator()).bind(\"opMethod\"), this)"
    }}
]
```

