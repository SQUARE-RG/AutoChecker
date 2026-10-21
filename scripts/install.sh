#!/usr/bin/env bash
set -euo pipefail

# Make the project helper scripts executable and run them in order.
# Usage: bash scripts/install.sh

ROOT_DIR="/root/code_check"
cd "$ROOT_DIR"

SCRIPTS=(
  "scripts/prepair_python_env.sh"
  "scripts/prepair_clang_tidy.sh"
  "scripts/clang_tidy_dev_flow.sh"
)

echo "Checking scripts and setting executable permission..."
for s in "${SCRIPTS[@]}"; do
  if [[ -f "$s" ]]; then
    chmod +x "$s"
    echo "chmod +x $s"
  else
    echo "Error: required script not found: $s" >&2
    exit 1
  fi
done

echo "Running prepair_python_env.sh (requires root)..."
if sudo bash scripts/prepair_python_env.sh; then
  echo "prepair_python_env.sh finished successfully"
else
  echo "prepair_python_env.sh failed" >&2
  exit 2
fi

echo "Running prepair_clang_tidy.sh (requires root)..."
if sudo bash scripts/prepair_clang_tidy.sh; then
  echo "prepair_clang_tidy.sh finished successfully"
else
  echo "prepair_clang_tidy.sh failed" >&2
  exit 3
fi

echo "Running clang_tidy_dev_flow.sh..."
if bash scripts/clang_tidy_dev_flow.sh; then
  echo "clang_tidy_dev_flow.sh finished successfully"
else
  echo "clang_tidy_dev_flow.sh failed" >&2
  exit 4
fi

echo "All install scripts completed."
exit 0
