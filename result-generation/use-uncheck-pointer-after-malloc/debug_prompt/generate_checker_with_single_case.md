针对负例/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_8.cpp生成first checker
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
The rule requires that any pointer obtained through dynamic memory allocation functions (such as malloc, calloc, or realloc) must be checked for non-null before its first use. This check must occur before the pointer is used; performing the check after use is considered a violation. Acceptable check methods include explicit or implicit null pointer comparisons like if (ptr != NULL), if (ptr), or if (!ptr). If a dynamically allocated pointer is never used, it does not violate this rule. If a pointer is reallocated, it must be checked again before any subsequent use. This rule applies equally to global and local variables. Only one warning should be reported per violating pointer variable.
Scenarios that should be reported include: using a dynamically allocated pointer directly without any null check, performing a null check only after the pointer has been used, using a global variable after dynamic allocation without a check, and using pointers from calloc or realloc without a prior check.
Correct scenarios include: performing a null check immediately after allocation and using the pointer only after the check passes, not using the pointer after allocation, or not using a pointer after it has been reallocated. Various forms of null pointer checks, including shorthand forms, are acceptable.

## test case code
**Test Case Code:**
```cpp
#include <stdlib.h>

int *p = NULL;
void foo(void)
{
    p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}
```

## AST
TranslationUnitDecl 0x565264daa1c8 <<invalid sloc>> <invalid sloc>
`-FunctionDecl 0x565264ed0000 </root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc/use_uncheck_pointer_after_malloc_case_8.cpp:4:1, line:9:1> line:4:6 foo 'void ()'
  `-CompoundStmt 0x565264ed02f8 <line:5:1, line:9:1>
    |-BinaryOperator 0x565264ed0248 <line:6:5, col:34> 'int *' lvalue '='
    | |-DeclRefExpr 0x565264ed00a8 <col:5> 'int *' lvalue Var 0x565264ecfe78 'p' 'int *'
    | `-CStyleCastExpr 0x565264ed0220 <col:9, col:34> 'int *' <BitCast>
    |   `-CallExpr 0x565264ed01e0 <col:16, col:34> 'void *'
    |     |-ImplicitCastExpr 0x565264ed01c8 <col:16> 'void *(*)(size_t) noexcept(true)' <FunctionToPointerDecay>
    |     | `-DeclRefExpr 0x565264ed0148 <col:16> 'void *(size_t) noexcept(true)' lvalue Function 0x565264eb17d0 'malloc' 'void *(size_t) noexcept(true)' (UsingShadow 0x565264ecf358 'malloc')
    |     `-UnaryExprOrTypeTraitExpr 0x565264ed0128 <col:23, col:33> 'unsigned long' sizeof 'int'
    `-BinaryOperator 0x565264ed02d8 <line:7:5, col:10> 'int' lvalue '='
      |-UnaryOperator 0x565264ed02a0 <col:5, col:6> 'int' lvalue prefix '*' cannot overflow
      | `-ImplicitCastExpr 0x565264ed0288 <col:6> 'int *' <LValueToRValue>
      |   `-DeclRefExpr 0x565264ed0268 <col:6> 'int *' lvalue Var 0x565264ecfe78 'p' 'int *'
      `-IntegerLiteral 0x565264ed02b8 <col:10> 'int' 1


## reference logic step
[{'logic_registerMatchers': ["1. Define a matcher for calls to dynamic memory allocation functions (malloc, calloc, realloc) and bind the CallExpr as 'allocCall' and the resulting pointer variable as 'allocatedVar'", "2. Create a matcher to capture all uses (dereferences, array subscript, member access via pointer, etc.) of a variable that holds a dynamically allocated pointer, binding the use as 'pointerUse' and the variable as 'usedVar'", '3. For each allocation, track the order of events: match the allocation statement, then find all subsequent uses of that variable before a null check', "4. Match null check patterns (if statements, ternary operators, logical AND/OR with null comparisons) on the allocated variable, binding the check as 'nullCheck' and the variable as 'checkedVar'", "5. Ensure the matcher only triggers when a 'pointerUse' occurs and there is no preceding 'nullCheck' for the same variable along any execution path from allocation to use", '6. Handle global variables by matching allocations and uses across the entire translation unit, not limited to a single function scope', '7. Handle reallocations by treating a realloc call as a new allocation that requires a fresh null check before subsequent uses'], 'logic_check': ["1. Retrieve the bound 'allocatedVar' and 'pointerUse' nodes from the match result", "2. Verify that the variable in 'allocatedVar' and 'usedVar' refers to the same pointer variable", '3. Determine the source location of the allocation and the first use after allocation', '4. Check if there exists any null check on the variable between the allocation and the first use by analyzing the AST context and control flow', '5. If no null check is found before the first use, emit a diagnostic warning at the location of the first use, indicating the pointer was used without a prior null check', '6. Ensure only one warning is emitted per variable by keeping track of already reported variables within the check callback', '7. For reallocated pointers, treat the realloc call as a new allocation point and repeat the check for uses after that point']}]

## reference astMatchers
Narrowing Matcher: hasStaticStorageDuration
 Parameters;
 return type Matcher<VarDecl>
 Description: Matches a variable declaration that has static storage duration.
It includes the variable declared at namespace scope and those declared
with "static" and "extern" storage class specifiers.

void f() {
  int x;
  static int y;
  thread_local int z;
}
int a;
static int b;
extern int c;
varDecl(hasStaticStorageDuration())
  matches the function declaration y, a, b and c.

Node Matcher: nullStmt
 Parameters;Matcher<NullStmt>...
 return type Matcher<Stmt>
 Description: Matches null statements.

  foo();;
nullStmt()
  matches the second ';'

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

Narrowing Matcher: nullPointerConstant
 Parameters;
 return type Matcher<Expr>
 Description: Matches expressions that resolve to a null pointer constant, such as
GNU's __null, C++11's nullptr, or C's NULL macro.

Given:
  void *v1 = NULL;
  void *v2 = nullptr;
  void *v3 = __null; // GNU extension
  char *cp = (char *)0;
  int *ip = 0;
  int i = 0;
expr(nullPointerConstant())
  matches the initializer for v1, v2, v3, cp, and ip. Does not match the
  initializer for i.

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

Finder->addMatcher(
      binaryOperator(hasAnyOperatorName("==", "!="),
                     hasOperands(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                                       integerLiteral(equals(0))),
                                 callToGet(knownSmartptr()))),
      Callback);
anyOf(declRefExpr(to(decl().bind("deletedPointer"))), memberExpr(hasDeclaration(fieldDecl().bind("deletedMemberPointer"))))
Finder->addMatcher(unaryOperator(hasAnyOperatorName("++", "--"), hasType(pointerType())).bind("expr"), this);
const auto AllocFunc = functionDecl(hasAnyName("::malloc", "std::malloc", "::alloca", "::calloc", "std::calloc", "::realloc", "std::realloc"));
const auto AllocCall = callExpr(callee(decl(anyOf(AllocFunc, AllocFuncPtr))));
binaryOperator(hasOperatorName("="), hasLHS(expr().bind("ptr_result")), hasRHS(ignoringParenCasts(callExpr(callee(functionDecl(hasName("::realloc"), parameterCountIs(2), hasParameter(0, hasType(pointerType(pointee(voidType())))), hasParameter(1, hasType(isInteger()))).bind("realloc")), hasArgument(0, expr().bind("ptr_input")), hasAncestor(functionDecl().bind("parent_function"))).bind("call"))))
varDecl(isGlobalStatic())


## reference api  
const auto *DeleteStmt = Nodes.getNodeAs<CXXDeleteExpr>("delete_expr");
const auto *DeletedVariable = Nodes.getNodeAs<DeclRefExpr>("deleted_variable");
if (DeleteStmt) {
  diag(DeleteStmt->getBeginLoc(),
       "deleting a pointer through a type that is "
       "not marked 'gsl::owner<>'; consider using a "
       "smart pointer instead")
      << DeletedVariable->getSourceRange();
  const ValueDecl *Decl = DeletedVariable->getDecl();
  diag(Decl->getBeginLoc(), "variable declared here", DiagnosticIDs::Note)
      << Decl->getSourceRange();
  return true;
}
return false;
const SourceRange OldRParen = SourceRange(PtrArith->getLHS()->getEndLoc());
const StringRef RParen =
    Lexer::getSourceText(CharSourceRange::getTokenRange(OldRParen),
                         *Result.SourceManager, getLangOpts());
const auto *LoopVar = Nodes.getNodeAs<VarDecl>(InitVarName);
const auto *EndVar = Nodes.getNodeAs<VarDecl>(EndVarName);
const auto *EndCall = Nodes.getNodeAs<CXXMemberCallExpr>(EndCallName);
const auto *BoundExpr = Nodes.getNodeAs<Expr>(ConditionBoundName);
llvm::SmallPtrSet<const DeclRefExpr *, 16> AllVarRefs =
    utils::decl_ref_expr::allDeclRefExprs(*TargetVarDecl, *LoopParent,
                                          *Context);
for (const auto *Ref : AllVarRefs) {
  if (SM.isBeforeInTranslationUnit(Ref->getLocation(),
                                   LoopStmt->getBeginLoc())) {
    return;
  }
}
else if (const auto *VD = Result.Nodes.getNodeAs<VarDecl>("Mark")) {
  const QualType T = VD->getType();
  if ((T->isPointerType() && !T->getPointeeType().isConstQualified()) ||
      T->isArrayType())
    markCanNotBeConst(VD->getInit(), true);
  else if (T->isLValueReferenceType() &&
           !T->getPointeeType().isConstQualified())
    markCanNotBeConst(VD->getInit(), false);
}
std::string CallName;
if (const auto *Call = dyn_cast<CallExpr>(AllocExpr)) {
  const NamedDecl *Func = Call->getDirectCallee();
  if (!Func) {
    Func = cast<NamedDecl>(Call->getCalleeDecl());
  }
  CallName = Func->getName().str();
} else {
  const auto *New = cast<CXXNewExpr>(AllocExpr);
  if (New->isArray()) {
    CallName = "operator new[]";
  } else {
    const auto *CtrE = New->getConstructExpr();
    if (!CtrE || !CtrE->getArg(CtrE->getNumArgs() - 1)
                       ->getType()
                       ->isIntegralOrEnumerationType())
      return;
    CallName = "operator new";
  }
}
auto EmitValueWarning = [this, &Result](const NestedNameSpecifierLoc &QualLoc,
                                      SourceLocation EndLoc) {
  SourceLocation TemplateNameEndLoc;
  if (auto TSTL = QualLoc.getTypeLoc().getAs<TemplateSpecializationTypeLoc>();
      !TSTL.isNull())
    TemplateNameEndLoc = Lexer::getLocForEndOfToken(
        TSTL.getTemplateNameLoc(), 0, *Result.SourceManager,
        Result.Context->getLangOpts());
  else
    return;

  if (EndLoc.isMacroID() || QualLoc.getEndLoc().isMacroID() ||
      TemplateNameEndLoc.isMacroID()) {
    if (IgnoreMacros)
      return;
    diag(QualLoc.getBeginLoc(), "use c++17 style variable templates");
    return;
  }
  diag(QualLoc.getBeginLoc(), "use c++17 style variable templates")
      << FixItHint::CreateInsertion(TemplateNameEndLoc, "_v")
      << FixItHint::CreateRemoval({QualLoc.getEndLoc(), EndLoc});
};
bool clang::CXXNewExpr::shouldNullCheckAllocation() const
bool clang::WhileStmt::hasVarStorage() const
void clang::SourceLocation::dump(const SourceManager & SM) const
void clang::PPChainedCallbacks::PragmaWarning(SourceLocation Loc, PragmaWarningSpecifier WarningSpec, ArrayRef<int> Ids)
bool clang::APValue::isNullPointer() const
void llvm::MallocAllocator::Deallocate(const void * Ptr, int Size, int Alignment)
DeclarationName clang::DeclarationName::getFromOpaquePtr(void * P)


## checker code template

The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.cpp :
```cpp
//===--- UseUncheckPointerAfterMallocCheck.cpp - clang-tidy ---------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "UseUncheckPointerAfterMallocCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Lex/Lexer.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/Expr.h"
#include "clang/AST/OperationKinds.h"
#include "clang/AST/Type.h"
#include "llvm/ADT/SmallPtrSet.h"
#include <string>

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

namespace {

// Matcher for dynamic memory allocation functions
const auto AllocFuncMatcher = functionDecl(
    hasAnyName("::malloc", "::calloc", "::realloc", "std::malloc", 
               "std::calloc", "std::realloc"));

// Matcher for allocation calls
const auto AllocCallMatcher = callExpr(
    callee(AllocFuncMatcher),
    unless(hasAncestor(callExpr()))).bind("allocCall");

// Helper matcher to find the pointer variable from allocation - fixed version
const auto PointerVarFromAllocMatcher = stmt(anyOf(
    // Direct assignment: p = malloc()
    binaryOperator(hasOperatorName("="),
        hasLHS(declRefExpr(to(varDecl().bind("ptrVar")))),
        hasRHS(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))),
    // Variable declaration with initialization: int *p = malloc()
    declStmt(hasSingleDecl(varDecl(
        hasInitializer(anyOf(
            AllocCallMatcher,
            castExpr(hasSourceExpression(AllocCallMatcher))))
        .bind("ptrVarDecl"))))
)).bind("allocExpr");

// Matcher for pointer usage
const auto PointerUseMatcher = expr(
    anyOf(
        // Dereference: *p
        unaryOperator(hasOperatorName("*"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Array subscript: p[0]
        arraySubscriptExpr(
            hasBase(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("useVar")))))),
        // Member access through pointer: p->field
        memberExpr(hasObjectExpression(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar")))))),
        // Function call through pointer: p()
        callExpr(has(ignoringParenImpCasts(
            declRefExpr(to(varDecl().bind("useVar"))))))
    )).bind("pointerUse");

// Matcher for null pointer checks
const auto NullCheckMatcher = stmt(
    anyOf(
        // Explicit comparisons: ptr == NULL, ptr != NULL
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))),
            hasRHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0))))),
        binaryOperator(anyOf(hasOperatorName("=="), hasOperatorName("!=")),
            hasLHS(anyOf(cxxNullPtrLiteralExpr(), gnuNullExpr(),
                         integerLiteral(equals(0)))),
            hasRHS(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Implicit checks: if (ptr), while (ptr)
        implicitCastExpr(hasImplicitDestinationType(booleanType()),
            hasSourceExpression(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar")))))),
        // Negated checks: if (!ptr)
        unaryOperator(hasOperatorName("!"),
            hasUnaryOperand(ignoringParenImpCasts(
                declRefExpr(to(varDecl().bind("checkVar"))))))
    )).bind("nullCheck");

} // namespace

void UseUncheckPointerAfterMallocCheck::registerMatchers(MatchFinder *Finder) {
  // Register separate matchers for allocation and pointer use
  Finder->addMatcher(
      traverse(TK_AsIs, PointerVarFromAllocMatcher),
      this);
  
  Finder->addMatcher(
      traverse(TK_AsIs, PointerUseMatcher),
      this);
}

void UseUncheckPointerAfterMallocCheck::check(const MatchFinder::MatchResult &Result) {
  ASTContext *Context = Result.Context;
  const SourceManager &SM = *Result.SourceManager;
  
  // Check if this is an allocation expression
  const Stmt *AllocExpr = Result.Nodes.getNodeAs<Stmt>("allocExpr");
  const VarDecl *PtrVar = nullptr;
  const VarDecl *PtrVarDecl = Result.Nodes.getNodeAs<VarDecl>("ptrVarDecl");
  
  if (AllocExpr && AllocExpr->getBeginLoc().isValid()) {
    // Get the pointer variable from the allocation
    if (PtrVarDecl && PtrVarDecl->getLocation().isValid()) {
      PtrVar = PtrVarDecl;
    } else {
      PtrVar = Result.Nodes.getNodeAs<VarDecl>("ptrVar");
    }
    
    if (!PtrVar || !PtrVar->getLocation().isValid()) return;
    
    // Store allocation information for this variable
    // We'll track allocations and their locations
    // This is a simplified approach - in a real checker, you'd want to
    // maintain state across multiple matches
  }
  
  // Check if this is a pointer usage
  const Expr *PointerUse = Result.Nodes.getNodeAs<Expr>("pointerUse");
  const VarDecl *UseVar = Result.Nodes.getNodeAs<VarDecl>("useVar");
  
  if (PointerUse && PointerUse->getBeginLoc().isValid() && 
      UseVar && UseVar->getLocation().isValid()) {
    
    // Get the function containing this statement
    const FunctionDecl *Func = nullptr;
    auto Parents = Context->getParents(*PointerUse);
    while (!Parents.empty()) {
      if (const auto *FD = Parents[0].get<FunctionDecl>()) {
        Func = FD;
        break;
      }
      Parents = Context->getParents(Parents[0]);
    }
    
    if (!Func || !Func->hasBody()) return;
    
    const Stmt *FuncBody = Func->getBody();
    if (!FuncBody) return;
    
    // Find the most recent allocation for this variable before the use
    SourceLocation LastAllocLoc;
    bool IsRealloc = false;
    
    // Traverse the function body to find allocations of this variable
    std::function<void(const Stmt *)> findAllocations = [&](const Stmt *S) {
      if (!S) return;
      
      // Check if this is an allocation of our variable
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_Assign) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) {
              const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
              // Check if RHS is a call to allocation function
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(RHS)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(RHS);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(), 
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      // Check variable declarations with initializers
      if (const auto *DS = dyn_cast<DeclStmt>(S)) {
        for (const Decl *D : DS->decls()) {
          if (const auto *VD = dyn_cast<VarDecl>(D)) {
            if (VD == UseVar && VD->hasInit()) {
              const Expr *Init = VD->getInit()->IgnoreParenImpCasts();
              const CallExpr *CE = nullptr;
              if (const auto *Cast = dyn_cast<CastExpr>(Init)) {
                CE = dyn_cast<CallExpr>(Cast->getSubExpr()->IgnoreParenImpCasts());
              } else {
                CE = dyn_cast<CallExpr>(Init);
              }
              
              if (CE) {
                const FunctionDecl *FD = CE->getDirectCallee();
                if (FD) {
                  StringRef Name = FD->getName();
                  if (Name == "malloc" || Name == "calloc" || Name == "realloc" ||
                      Name == "std::malloc" || Name == "std::calloc" || Name == "std::realloc") {
                    if (SM.isBeforeInTranslationUnit(CE->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      LastAllocLoc = CE->getBeginLoc();
                      IsRealloc = (Name == "realloc" || Name == "std::realloc");
                    }
                  }
                }
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findAllocations(Child);
      }
    };
    
    findAllocations(FuncBody);
    
    // If no allocation found before this use, it's not from dynamic allocation
    if (LastAllocLoc.isInvalid()) return;
    
    // Now check if there's a null check between the allocation and the use
    bool FoundNullCheck = false;
    
    std::function<void(const Stmt *)> findNullChecks = [&](const Stmt *S) {
      if (!S || FoundNullCheck) return;
      
      // Check binary operators for explicit null comparisons
      if (const auto *BinOp = dyn_cast<BinaryOperator>(S)) {
        if (BinOp->getOpcode() == BO_EQ || BinOp->getOpcode() == BO_NE) {
          const Expr *LHS = BinOp->getLHS()->IgnoreParenImpCasts();
          const Expr *RHS = BinOp->getRHS()->IgnoreParenImpCasts();
          
          // Check if one side is our variable
          const DeclRefExpr *VarDRE = nullptr;
          if (const auto *DRE = dyn_cast<DeclRefExpr>(LHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          } else if (const auto *DRE = dyn_cast<DeclRefExpr>(RHS)) {
            if (DRE->getDecl() == UseVar) VarDRE = DRE;
          }
          
          if (VarDRE) {
            // Check if the other side is a null pointer constant
            const Expr *OtherSide = (VarDRE == dyn_cast<DeclRefExpr>(LHS)) ? RHS : LHS;
            if (OtherSide->isNullPointerConstant(*Context, 
                                                 Expr::NPC_ValueDependentIsNull)) {
              // Check if this null check is between allocation and use
              if (SM.isBeforeInTranslationUnit(LastAllocLoc, BinOp->getBeginLoc()) &&
                  SM.isBeforeInTranslationUnit(BinOp->getBeginLoc(), 
                                               PointerUse->getBeginLoc())) {
                FoundNullCheck = true;
                return;
              }
            }
          }
        }
      }
      
      // Check for implicit checks (if (ptr), while (ptr))
      if (const auto *DRE = dyn_cast<DeclRefExpr>(S)) {
        if (DRE->getDecl() == UseVar) {
          // Check parent nodes to see if this is in a condition context
          auto DREParents = Context->getParents(*DRE);
          while (!DREParents.empty()) {
            if (const auto *ICE = DREParents[0].get<ImplicitCastExpr>()) {
              if (ICE->getCastKind() == CK_PointerToBoolean ||
                  ICE->getCastKind() == CK_IntegralToBoolean) {
                // Check if this is in a condition context
                auto ICEParents = Context->getParents(*ICE);
                while (!ICEParents.empty()) {
                  const Stmt *ParentStmt = ICEParents[0].get<Stmt>();
                  if (ParentStmt) {
                    if (isa<IfStmt>(ParentStmt) || isa<WhileStmt>(ParentStmt) ||
                        isa<DoStmt>(ParentStmt) || isa<ForStmt>(ParentStmt) ||
                        isa<ConditionalOperator>(ParentStmt)) {
                      if (SM.isBeforeInTranslationUnit(LastAllocLoc, 
                                                       ICE->getBeginLoc()) &&
                          SM.isBeforeInTranslationUnit(ICE->getBeginLoc(),
                                                       PointerUse->getBeginLoc())) {
                        FoundNullCheck = true;
                        return;
                      }
                    }
                  }
                  ICEParents = Context->getParents(ICEParents[0]);
                }
              }
            }
            DREParents = Context->getParents(DREParents[0]);
          }
        }
      }
      
      // Check for negated checks (if (!ptr))
      if (const auto *UnaryOp = dyn_cast<UnaryOperator>(S)) {
        if (UnaryOp->getOpcode() == UO_LNot) {
          const Expr *SubExpr = UnaryOp->getSubExpr()->IgnoreParenImpCasts();
          if (const auto *DRE = dyn_cast<DeclRefExpr>(SubExpr)) {
            if (DRE->getDecl() == UseVar) {
              // Check if this is in a condition context
              auto UnaryParents = Context->getParents(*UnaryOp);
              while (!UnaryParents.empty()) {
                const Stmt *ParentStmt = UnaryParents[0].get<Stmt>();
                if (ParentStmt) {
                  if (isa<IfStmt>(ParentStmt) || isa<WhileStmt>(ParentStmt) ||
                      isa<DoStmt>(ParentStmt) || isa<ForStmt>(ParentStmt) ||
                      isa<ConditionalOperator>(ParentStmt)) {
                    if (SM.isBeforeInTranslationUnit(LastAllocLoc,
                                                     UnaryOp->getBeginLoc()) &&
                        SM.isBeforeInTranslationUnit(UnaryOp->getBeginLoc(),
                                                     PointerUse->getBeginLoc())) {
                      FoundNullCheck = true;
                      return;
                    }
                  }
                }
                UnaryParents = Context->getParents(UnaryParents[0]);
              }
            }
          }
        }
      }
      
      for (const Stmt *Child : S->children()) {
        findNullChecks(Child);
      }
    };
    
    findNullChecks(FuncBody);
    
    // If no null check found, emit diagnostic
    if (!FoundNullCheck) {
      diag(PointerUse->getBeginLoc(), 
           "禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]")
          << PointerUse->getSourceRange();
    }
  }
}

} // namespace clang::tidy::ucassaat
```
The content of /root/code_check/llvm-project/clang-tools-extra/clang-tidy/ucassaat/UseUncheckPointerAfterMallocCheck.h :
```cpp
//===--- UseUncheckPointerAfterMallocCheck.h - clang-tidy -------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Checks that pointers obtained through dynamic memory allocation functions
/// (malloc, calloc, realloc) are checked for null before their first use.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/use-uncheck-pointer-after-malloc.html
class UseUncheckPointerAfterMallocCheck : public ClangTidyCheck {
public:
  UseUncheckPointerAfterMallocCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_USEUNCHECKPOINTERAFTERMALLOCCHECK_H
```

# Output Formatting Requirements

**Output Format Requirements:**
    -Strictly output according to the format below, do not add any additional explanations or text, code blocks are marked with ```cpp and include the complete source code.
    -Ensure that the source code is complete and compilable.
    -Please modify based on the checker code template above.Namespace content such as "namespace clang::tidy::ucassaat", please do not modify to prevent prevent compilation error.
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