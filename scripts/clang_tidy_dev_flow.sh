#!/usr/bin/env bash
set -euo pipefail

# Script to add a custom clang-tidy module `ucassaat`, copy sources, patch build files,
# build clang-tidy and verify the new checks are listed.
# Run from any location: bash scripts/clang_tidy_dev_flow.sh

REPO_ROOT=/root/code_check/llvm-project
CLANG_TIDY_DIR="$REPO_ROOT/clang-tools-extra/clang-tidy"
MODULE_DIR="$CLANG_TIDY_DIR/ucassaat"
TEST_CHECKERS_DIR="$CLANG_TIDY_DIR/../test/clang-tidy/checkers/ucassaat"
WORKFLOW_SRC_DIR=/root/code_check/scripts/clang-tidy-work-flow
BUILD_DIR="$REPO_ROOT/build"
CMAKE_BUILD_BIN=/usr/bin/cmake

echo "Starting ucassaat clang-tidy development flow"

if [[ ! -d "$CLANG_TIDY_DIR" ]]; then
  echo "Cannot find clang-tidy dir: $CLANG_TIDY_DIR" >&2
  exit 1
fi

mkdir -p "$MODULE_DIR"
mkdir -p "$TEST_CHECKERS_DIR"

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

echo "Patching CMakeLists.txt in $CLANG_TIDY_DIR"
CMAKELISTS="$CLANG_TIDY_DIR/CMakeLists.txt"
if [[ ! -f "$CMAKELISTS" ]]; then
  echo "Missing $CMAKELISTS" >&2
  exit 1
fi

# Insert add_subdirectory(ucassaat) before add_subdirectory(zircon) if not present
if ! grep -q "add_subdirectory(ucassaat)" "$CMAKELISTS"; then
  awk '/add_subdirectory\(zircon\)/ && !x{print "add_subdirectory(ucassaat)"; x=1} {print}' "$CMAKELISTS" > "$CMAKELISTS.tmp" && mv "$CMAKELISTS.tmp" "$CMAKELISTS"
  echo "Inserted add_subdirectory(ucassaat) into CMakeLists.txt"
else
  echo "CMakeLists.txt already contains add_subdirectory(ucassaat); skipping"
fi

# Insert module registration name before clangTidyZirconModule
if ! grep -q "clangTidyUcasSaatModule" "$CMAKELISTS"; then
  awk '/clangTidyZirconModule/ && !y{print "  clangTidyUcasSaatModule"; y=1} {print}' "$CMAKELISTS" > "$CMAKELISTS.tmp" && mv "$CMAKELISTS.tmp" "$CMAKELISTS"
  echo "Inserted clangTidyUcasSaatModule into CMakeLists.txt"
else
  echo "CMakeLists.txt already contains clangTidyUcasSaatModule; skipping"
fi

echo "Patching ClangTidyForceLinker.h"
FORCE_LINKER="$CLANG_TIDY_DIR/ClangTidyForceLinker.h"
if [[ ! -f "$FORCE_LINKER" ]]; then
  echo "Missing $FORCE_LINKER" >&2
  exit 1
fi

if ! grep -q "UcasSaatModuleAnchorSource" "$FORCE_LINKER"; then
  # Insert anchor block before the Zircon anchor comment
  awk 'BEGIN{p=0} /This anchor is used to force the linker to link the ZirconModule\./ && !p{print "// This anchor is used to force the linker to link the UcasSaatModule."; print "extern volatile int UcasSaatModuleAnchorSource;"; print "static int LLVM_ATTRIBUTE_UNUSED UcasSaatModuleAnchorDestination ="; print "    UcasSaatModuleAnchorSource;"; p=1} {print}' "$FORCE_LINKER" > "$FORCE_LINKER.tmp" && mv "$FORCE_LINKER.tmp" "$FORCE_LINKER"
  echo "Inserted UcasSaat anchor into ClangTidyForceLinker.h"
else
  echo "ClangTidyForceLinker.h already contains UcasSaat anchor; skipping"
fi

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

CLANG_TIDY_BIN="$BUILD_DIR/clang-tidy"
if [[ ! -x "$CLANG_TIDY_BIN" ]]; then
  echo "clang-tidy binary not found at $CLANG_TIDY_BIN" >&2
  exit 1
fi

echo "Listing checks for ucassaat-..."
OUTPUT=$("$CLANG_TIDY_BIN" --list-checks --checks=-*,ucassaat-* 2>&1 || true)
echo "$OUTPUT"

if [[ -n "$OUTPUT" ]]; then
  echo "Development flow appears complete: some ucassaat checks were listed above." 
  exit 0
else
  echo "No ucassaat checks listed. Check build logs and CMake configuration." >&2
  exit 2
fi
