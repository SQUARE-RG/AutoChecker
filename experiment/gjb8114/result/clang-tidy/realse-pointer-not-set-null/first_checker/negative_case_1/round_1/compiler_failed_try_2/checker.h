//===--- RealsePointerNotSetNullCheck.h - clang-tidy ------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// Prohibition of Failing to Set Pointers to Null After Release.
/// This rule mandates that after a pointer variable is freed using free() 
/// (in C) or delete/delete[] (in C++), it must be immediately set to a null value.
/// In C, NULL should be used, while in C++, nullptr is recommended (though NULL is acceptable).
/// The nullification must occur within the same scope as the deallocation, 
/// without being split across conditional branches.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/realse-pointer-not-set-null.html
class RealsePointerNotSetNullCheck : public ClangTidyCheck {
public:
  RealsePointerNotSetNullCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;

private:
  void checkDeallocation(const Stmt *DeallocStmt, const Expr *FreedPtr,
                         const ast_matchers::MatchFinder::MatchResult &Result);
  void checkReallocation(const CallExpr *ReallocCall, const Expr *ReallocPtr,
                         const ast_matchers::MatchFinder::MatchResult &Result);
  
  bool isNullAssignmentToPtr(const Stmt *S, const ValueDecl *PtrDecl,
                             const ASTContext *Ctx);
  bool checkNullAssignmentInDifferentBranch(const IfStmt *If,
                                            const ValueDecl *PtrDecl,
                                            const Stmt *DeallocStmt,
                                            const ast_matchers::MatchFinder::MatchResult &Result);
  bool containsStmt(const Stmt *Container, const Stmt *Target);
  bool containsNullAssignmentToPtr(const Stmt *S, const ValueDecl *PtrDecl,
                                   const ASTContext *Ctx);
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_REALSEPOINTERNOTSETNULLCHECK_H