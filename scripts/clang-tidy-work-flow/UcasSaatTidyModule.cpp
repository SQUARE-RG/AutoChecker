//===------- UcasSaatTidyModule.cpp - clang-tidy --------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
#include "../ClangTidy.h"
#include "../ClangTidyModule.h"
#include "../ClangTidyModuleRegistry.h"
#include "HelloWorldCheck.h"
using namespace clang::ast_matchers;
namespace clang::tidy {
namespace ucassaat {
class UcasSaatModule : public ClangTidyModule {
public:
void addCheckFactories(ClangTidyCheckFactories &CheckFactories) override {
CheckFactories.registerCheck<HelloWorldCheck>(
    "ucassaat-hello-world");
}
};
// Register the UcasSaatModule using this statically initialized variable.
static ClangTidyModuleRegistry::Add<UcasSaatModule> X("ucassaat-module",
"Add ucassaat checks.");
} // namespace ucassaat
// This anchor is used to force the linker to link in the generated object file
// and thus register the UcasSaatModule.
volatile int UcasSaatModuleAnchorSource = 0;
} // namespace clang::tidy