
# 编译Clang-tidy
依次执行如下命令完成编译过程：
```shell
sudo apt-get update
sudo apt-get install -y cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev
sudo apt-get install -y openssh-server python3 libreadline-dev libgmp-dev pkg-config
sudo apt-get install -y libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev
sudo apt-get install -y file source-highlight libsource-highlight-dev liblzma-dev
# 进入软件根目录
cd AutoChecker
# 克隆到软件中
git clone https://github.com/llvm/llvm-project --recursive
 
#在llvm-project目录中进行编译
cd llvm-project
git checkout release/17.0.x
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

# 