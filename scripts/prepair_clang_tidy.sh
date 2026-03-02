#!/usr/bin/env bash
set -euo pipefail

# Prepare system and build clang/clang-tidy from llvm-project (release/17.0.x)
# Usage: sudo bash scripts/prepair_clang_tidy.sh

REPO_DIR_CANDIDATE1=/root/code_check
REPO_DIR_CANDIDATE2=/root/code_cehck
LLVM_DIR=llvm-project
LLVM_BRANCH=release/17.0.x
MAKE_JOBS=${MAKE_JOBS:-56}

echo "Starting clang/clang-tidy preparation script"

if [[ $EUID -ne 0 ]]; then
	echo "This script requires root privileges. Run with sudo or as root." >&2
	exit 1
fi

if [[ -d "$REPO_DIR_CANDIDATE1" ]]; then
	REPO_DIR="$REPO_DIR_CANDIDATE1"
elif [[ -d "$REPO_DIR_CANDIDATE2" ]]; then
	REPO_DIR="$REPO_DIR_CANDIDATE2"
else
	echo "Neither $REPO_DIR_CANDIDATE1 nor $REPO_DIR_CANDIDATE2 exists. Please ensure project directory is present." >&2
	exit 1
fi

cd "$REPO_DIR"

echo "Running apt-get update and installing required packages..."
apt-get update
apt-get install -y cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev
apt-get install -y openssh-server python3 libreadline-dev libgmp-dev pkg-config
apt-get install -y libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev
apt-get install -y file source-highlight libsource-highlight-dev liblzma-dev

# if [[ ! -d "$LLVM_DIR" ]]; then
# 	echo "Cloning llvm-project repository (this may take a long time)..."
# 	git clone https://github.com/llvm/llvm-project --recursive "$LLVM_DIR"
# else
# 	echo "Directory $LLVM_DIR already exists; updating..."
# 	pushd "$LLVM_DIR" >/dev/null
# 	git fetch --all
# 	git submodule sync --recursive
# 	git submodule update --init --recursive
# 	popd >/dev/null
# fi

cd "$LLVM_DIR"
echo "Checking out branch $LLVM_BRANCH"
git checkout "$LLVM_BRANCH"

echo "Creating build directory..."
mkdir -p build
cd build

echo "Configuring CMake (Ninja generator)..."
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

echo "Building FileCheck (parallel: nproc)..."
cmake --build . --target FileCheck -j"$(nproc)"

echo "Building clang-tidy, clang and clang-query (parallel: $MAKE_JOBS)..."
cmake --build . --target clang-tidy clang clang-query -j"$MAKE_JOBS"

echo "clang/clang-tidy build steps completed. Built artifacts are in: $(pwd)"

exit 0

