#!/usr/bin/env bash
set -euo pipefail

# Script to add a custom clang-tidy module `ucassaat`, copy sources, patch build files,
# build clang-tidy and verify the new checks are listed.
# Run from any location: bash scripts/clang_tidy_dev_flow.sh

REPO_ROOT=/root/code_check/llvm-project
CLANG_TIDY_DIR="$REPO_ROOT/clang-tools-extra/clang-tidy"
MODULE_DIR="$CLANG_TIDY_DIR/ucassaat"
TEST_CHECKERS_DIR="$CLANG_TIDY_DIR/../test/clang-tidy/checkers/ucassaat"
DOCS_CHECKERS_DIR="$CLANG_TIDY_DIR/../../docs/clang-tidy/checks/ucassaat"
WORKFLOW_SRC_DIR=/root/code_check/scripts/clang-tidy-work-flow
WORKFLOW_CLANG_TIDY_DIR="$WORKFLOW_SRC_DIR/clang-tidy"
BUILD_DIR="$REPO_ROOT/build"
CMAKE_BUILD_BIN=/usr/bin/cmake

echo "Starting ucassaat clang-tidy development flow"

if [[ ! -d "$CLANG_TIDY_DIR" ]]; then
  echo "Cannot find clang-tidy dir: $CLANG_TIDY_DIR" >&2
  exit 1
fi

mkdir -p "$MODULE_DIR"
mkdir -p "$TEST_CHECKERS_DIR"
# add_new_check.py 的 write_docs() 假定 docs 目录已存在，需预先创建
mkdir -p "$DOCS_CHECKERS_DIR"

# Copy helper scripts from workflow dir into llvm-project locations
echo "Copying helper workflow scripts into clang-tidy tree"
if [[ -f "$WORKFLOW_SRC_DIR/remove_clang_tidy_check.py" ]]; then
  cp -v "$WORKFLOW_SRC_DIR/remove_clang_tidy_check.py" "$CLANG_TIDY_DIR/"
else
  echo "Warning: remove_clang_tidy_check.py not found in $WORKFLOW_SRC_DIR" >&2
fi

TEST_DIR_PARENT="$REPO_ROOT/clang-tools-extra/test/clang-tidy"
mkdir -p "$TEST_DIR_PARENT"
if [[ -f "$WORKFLOW_SRC_DIR/test_check_clang_tidy.py" ]]; then
  cp -v "$WORKFLOW_SRC_DIR/test_check_clang_tidy.py" "$TEST_DIR_PARENT/"
else
  echo "Warning: test_check_clang_tidy.py not found in $WORKFLOW_SRC_DIR" >&2
fi

echo "Replacing CMakeLists.txt and ClangTidyForceLinker.h with workflow versions"
SRC_CMAKELISTS="$WORKFLOW_CLANG_TIDY_DIR/CMakeLists.txt"
SRC_FORCE_LINKER="$WORKFLOW_CLANG_TIDY_DIR/ClangTidyForceLinker.h"

if [[ ! -f "$SRC_CMAKELISTS" ]]; then
  echo "Missing workflow CMakeLists at $SRC_CMAKELISTS" >&2
  exit 1
fi
if [[ ! -f "$SRC_FORCE_LINKER" ]]; then
  echo "Missing workflow ClangTidyForceLinker at $SRC_FORCE_LINKER" >&2
  exit 1
fi

cp -v "$SRC_CMAKELISTS" "$CLANG_TIDY_DIR/CMakeLists.txt"
cp -v "$SRC_FORCE_LINKER" "$CLANG_TIDY_DIR/ClangTidyForceLinker.h"

echo "Copying module source files into $MODULE_DIR"
for f in UcasSaatTidyModule.cpp CMakeLists.txt HelloWorldCheck.h HelloWorldCheck.cpp; do
  SRC="$WORKFLOW_SRC_DIR/$f"
  if [[ -f "$SRC" ]]; then
    cp -v "$SRC" "$MODULE_DIR/"
  else
    echo "Warning: source file not found: $SRC" >&2
  fi
done

echo "Files in $MODULE_DIR:"
ls -la "$MODULE_DIR" || true

echo "Now building clang-tidy target (this may take a while)..."
if [[ ! -d "$BUILD_DIR" ]]; then
  echo "Build directory $BUILD_DIR not found. Please run cmake config step first." >&2
  exit 1
fi

"$CMAKE_BUILD_BIN" --build "$BUILD_DIR" --target clang-tidy -j || { echo "Build failed" >&2; exit 1; }

CLANG_TIDY_BIN="$BUILD_DIR/bin/clang-tidy"
if [[ ! -x "$CLANG_TIDY_BIN" ]]; then
  echo "clang-tidy binary not found at $CLANG_TIDY_BIN" >&2
  exit 1
fi

echo "Listing checks for ucassaat-..."
OUTPUT=$("$CLANG_TIDY_BIN" --list-checks --checks=-*,ucassaat-* 2>&1 || true)
echo "$OUTPUT"

if [[ -n "$OUTPUT" ]]; then
  echo "Development flow appears complete: some ucassaat checks were listed above."
  # 预热 embedding 缓存，避免 main.py 首次运行时边跑边编码
  PREWARM_SCRIPT=/root/code_check/scripts/prewarm_embeddings.py
  if [[ -f "$PREWARM_SCRIPT" ]]; then
    echo "Prewarming embedding caches..."
    # 激活 conda 虚拟环境（与 prepair_python_env.sh 一致）
    CONDA_SH=/root/anaconda3/etc/profile.d/conda.sh
    if [[ -f "$CONDA_SH" ]]; then
      source "$CONDA_SH"
      conda activate code_check
      python "$PREWARM_SCRIPT" || echo "Warning: prewarm failed, main.py will compute embeddings on first run" >&2
    else
      echo "Warning: conda.sh not found at $CONDA_SH, falling back to system python" >&2
      python "$PREWARM_SCRIPT" || echo "Warning: prewarm failed, main.py will compute embeddings on first run" >&2
    fi
  else
    echo "Warning: prewarm script not found: $PREWARM_SCRIPT" >&2
  fi
  exit 0
else
  echo "No ucassaat checks listed. Check build logs and CMake configuration." >&2
  exit 2
fi
