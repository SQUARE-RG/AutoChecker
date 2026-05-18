# clang-tidy环境配置
自行配置 clang-tidy 开发环境，请确保开发设备（或虚拟机环境）性能满足以下最低要求：
操作系统：Ubuntu 20.04 及以上（可使用 WSL 或虚拟机）
CPU：4 核心及以上
内存：16 GB及以上
剩余硬盘空间：20GB 及以上（推荐使用固态硬盘）
其它条件：顺畅的网络和网速（LLVM 源代码仓库克隆需使用约 4GB 流量）

使用以下命令在AutoChecker项目根目录下克隆`llvm-project`源码仓库。
```shell
git clone https://github.com/llvm/llvm-project --recursivec
cd llvm-project
git checkout release/17.x
```
注意： 我们当前收集的知识库是基于release/17.x分支版本收集的，如果想支持其他版本的clang-tidy，请使用AutoChecker项目中的收集脚本自动化构建新的知识库。


## 编译Clang-tidy
依次执行如下命令完成编译过程：
```shell
sudo apt-get update
sudo apt-get install -y cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev
sudo apt-get install -y openssh-server python3 libreadline-dev libgmp-dev pkg-config
sudo apt-get install -y libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev
sudo apt-get install -y file source-highlight libsource-highlight-dev liblzma-dev

#在llvm-project目录中进行编译
cd llvm-project
mkdir build
cd build
cmake \
-G Ninja \
-DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
-DCMAKE_BUILD_TYPE=RelWithDebInfo \
-DLLVM_USE_SPLIT_DWARF=ON \
-DLLVM_OPTIMIZED_TABLEGEN=ON \
-DLLVM_TARGETS_TO_BUILD=X86 \
-DLLVM_ENABLE_PROJECTS='clang;clang-tools-extra' \
-DBUILD_SHARED_LIBS=ON \
-DLLVM_ENABLE_BINDINGS=OFF \
-DCLANG_ENABLE_ARCMT=OFF \
-DLLVM_INCLUDE_TESTS=OFF \
-DCLANG_INCLUDE_TESTS=OFF \
-DCMAKE_C_COMPILER_LAUNCHER=ccache \
-DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
-S ../llvm -B .
 
# 编译
cmake --build . --target FileCheck -j
cmake --build . --target clang-tidy clang clang-query -j56


```

# 准备工作环境
切换到 clang-tools-extra/clang-tidy 目录，输入以下命令创建文件夹

```shell
mkdir ucassaat
mkdir ../test/clang-tidy/checkers/ucassaat
mkdir ../docs/clang-tidy/checks/ucassaat
```
编辑 clang-tidy 目录下的 CMakeLists.txt 文件，找到以下语句并在上方插入对应语句。
```shell
add_subdirectory(ucassaat)
# 找到下一行语句（约 78 行附近），并在其上一行插入第一行语句
add_subdirectory(zircon)
```

```shell
  clangTidyUcasSaatModule
# 找到下一行语句（约 102 行附近），并在其上一行插入第一行语句
  clangTidyZirconModule
```


编辑 clang-tidy 目录下的 ClangTidyForceLinker.h 文件，找到以下语句并在上方插入对应语句。
```cpp
// This anchor is used to force the linker to link the UcasSaatModule.
extern volatile int UcasSaatModuleAnchorSource;
static int LLVM_ATTRIBUTE_UNUSED UcasSaatModuleAnchorDestination =
    UcasSaatModuleAnchorSource;

/** 找到以下（约 135~138 行附近），并在其上一行插入上方的语句 **/
// This anchor is used to force the linker to link the ZirconModule.
extern volatile int ZirconModuleAnchorSource;
static int LLVM_ATTRIBUTE_UNUSED ZirconModuleAnchorDestination =
    ZirconModuleAnchorSource;
```


切换到前面创建的 ucassaat 文件夹，新建文件 CMakeLists.txt，输入以下内容。
```shell
set(LLVM_LINK_COMPONENTS
  support
  FrontendOpenMP
  )

add_clang_library(clangTidyUcasSaatModule
  HelloWorldCheck.cpp
  UcasSaatTidyModule.cpp

  LINK_LIBS
  clangTidy
  clangTidyCppCoreGuidelinesModule
  clangTidyUtils

  DEPENDS
  omp_gen
  )

clang_target_link_libraries(clangTidyUcasSaatModule
  PRIVATE
  clangAnalysis
  clangAnalysisFlowSensitive
  clangAnalysisFlowSensitiveModels
  clangAST
  clangASTMatchers
  clangBasic
  clangLex
  clangTooling
  clangTransformer
  )
```


继续在 ucassaat 文件夹下新建文件 UcasSaatTidyModule.cpp，输入以下内容。
```cpp
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
```


继续在 ucassaat 文件夹下新建文件 HelloWorldCheck.h，输入以下内容。
```cpp
//===--- HelloWorldCheck.h - clang-tidy -------------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_HELLOWORLDCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_HELLOWORLDCHECK_H

#include "../ClangTidyCheck.h"

namespace clang::tidy::ucassaat {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// http://clang.llvm.org/extra/clang-tidy/checks/ucassaat/hello-world.html
class HelloWorldCheck : public ClangTidyCheck {
public:
  HelloWorldCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
};

} // namespace clang::tidy::ucassaat

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_UCASSAAT_HELLOWORLDCHECK_H
```

继续在 ucassaat 文件夹下新建文件 HelloWorldCheck.cpp，输入以下内容。
```cpp
//===--- HelloWorldCheck.cpp - clang-tidy ---------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "HelloWorldCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

using namespace clang::ast_matchers;

namespace clang::tidy::ucassaat {

void HelloWorldCheck::registerMatchers(MatchFinder *Finder) {
  // FIXME: Add matchers.
  Finder->addMatcher(functionDecl(unless(anyOf(isExpansionInSystemHeader(), isMain()))).bind("x"), this);
}

void HelloWorldCheck::check(const MatchFinder::MatchResult &Result) {
  // FIXME: Add callback implementation.
  const auto *MatchedDecl = Result.Nodes.getNodeAs<FunctionDecl>("x");
  if (!MatchedDecl->getIdentifier() || MatchedDecl->getName().startswith("awesome_"))
    return;
  diag(MatchedDecl->getLocation(), "function %0 is insufficiently awesome!")
      << MatchedDecl
      << FixItHint::CreateInsertion(MatchedDecl->getLocation(), "awesome_");
  diag(MatchedDecl->getLocation(), "insert 'awesome'", DiagnosticIDs::Note);
}

} // namespace clang::tidy::ucassaat
```

回到 LLVM 源码根目录，输入以下命令创建并进入编译文件夹。
```bash
# 此处改为 LLVM 源码根目录
cd ../path/to/llvm-project
mkdir build
cd build
```


在 build 目录下输入以下命令，初始化 LLVM Clang 编译配置。有关编译参数的具体解释，可以参考：https://blog.oikawa.moe/2021/06/06/clang-%e7%9a%84%e7%b7%a8%e8%ad%af-%e9%9d%a2%e5%90%91-clang-static-analyzer-%e9%96%8b%e7%99%bc%e7%9a%84%e7%b7%a8%e8%ad%af%e9%85%8d%e7%bd%ae%e6%8c%87%e5%8c%97/
```bash
cmake \
    -G Ninja \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DLLVM_USE_SPLIT_DWARF=ON \
    -DLLVM_OPTIMIZED_TABLEGEN=ON \
    -DLLVM_TARGETS_TO_BUILD=X86 \
    -DLLVM_ENABLE_PROJECTS='clang;clang-tools-extra' \
    -DBUILD_SHARED_LIBS=ON \
    -DLLVM_ENABLE_BINDINGS=OFF \
    -DCLANG_ENABLE_ARCMT=OFF \
    -DLLVM_INCLUDE_TESTS=OFF \
    -DCLANG_INCLUDE_TESTS=OFF \
    -S ../llvm -B .
```

输入以下命令开始首次编译过程，首次编译的具体耗时取决于设备性能，期间请尽量关闭其它程序。8核32G设备编译大约需要40~50分钟左右（后续增量编译时间很短）。
```shell
cmake --build . --target clang-tidy -j \
    && cmake --build . --target clang -j \
    && cmake --build . --target clang-query -j
```


    注意：若设备内存较小但 CPU 核心数较多，请考虑通过 -j 参数适当降低并行编译数。一般的推荐如下：
    8G 及以下内存：-j 2
    >8G 且 ≤16G 内存：-j 4
    >16G 且 ≤ 32G 内存：-j 8
    >32G 内存：-j 无需指定数量，保持默认设置即可


首次编译完成后，在 build 文件夹中输入以下命令，验证 clang-tidy 中是否已包含名称为 ucassaat-hello-world 的自定义检查器。
```bash
./bin/clang-tidy --list-checks --checks=-*,ucassaat-*
```
