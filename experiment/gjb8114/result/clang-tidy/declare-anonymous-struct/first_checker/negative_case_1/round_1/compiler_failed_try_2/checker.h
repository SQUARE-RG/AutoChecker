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

/// 禁止在结构体定义中包含匿名结构体。
///
/// 此规则禁止在结构体定义中包含匿名结构体（即没有变量名的嵌套结构体类型）。
/// 匿名结构体指的是直接嵌入在外层结构体中但没有显式变量名标识符的类型。
/// 如果嵌套结构体有明确的变量名，则符合规则。
/// 此规则适用于所有级别的结构体嵌套，包括多级场景，并覆盖结构体的直接成员（无论其作用域是全局还是局部）。
///
/// 对于用户文档，请参阅：
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