

## 部署

### **codeql** 部署：

```shell
sudo apt update
sudo apt install build-essential libncurses-dev flex bison libssl-dev libelf-dev
# 下载codeql 
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
sudo unzip codeql-linux64.zip -d /opt/
sudo chmod -R 755 /opt/codeql

# 将 CodeQL 可执行文件路径添加到当前用户的 PATH 环境变量中
echo 'export PATH="$PATH:/opt/codeql/"' >> ~/.bashrc
source ~/.bashrc

# 验证安装
codeql version

# 获取codeSDK

git clone https://github.com/github/codeql.git /path/to/codeql-repo

```


## **linux内核**：
```shell
git clone https://github.com/torvalds/linux.git

```

## **llvm**
```shell
sudo apt-get update
sudo apt-get install -y cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev
sudo apt-get install -y openssh-server python3 libreadline-dev libgmp-dev pkg-config
sudo apt-get install -y libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev
sudo apt-get install -y file source-highlight libsource-highlight-dev liblzma-dev

git clone https://github.com/llvm/llvm-project --recursive

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


可以测试codeql在linux内核仓库中是否可以使用
```shell
codeql database create ../linux-db/spi-pci1xxx-db --language=cpp --command="make drivers/spi/spi-pci1xxxx.o -j8" --source-root=.

cd /root/code_check/codeql/cpp/ql/src
mkdir MyQL
touch test.ql
## 编写ql

codeql database analyze ../linux-db/spi-pci1xxx-db/ --format=csv --output=../result.csv ../codeql/cpp/ql/src/MyQL/test.ql
```
执行结果
```txt
"查找 devm_kzalloc 调用","在驱动代码中查找所有对 devm_kzalloc 函数的调用位置。","warning","找到对 devm_kzalloc 的调用","/drivers/spi/spi-pci1xxxx.c","818","12","818","23"
"查找 devm_kzalloc 调用","在驱动代码中查找所有对 devm_kzalloc 函数的调用位置。","warning","找到对 devm_kzalloc 的调用","/drivers/spi/spi-pci1xxxx.c","829","28","829","39"
```



## 关键步骤记录

clang_tidy_collect/collect_clang_tidy_astMatchers/collect_astMatchers.py   读取到所有的astMatchers的信息，保存到clang_tidy_collect/collect_clang_tidy_astMatchers/astMatchers.json中

