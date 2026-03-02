#!/usr/bin/env bash
set -euo pipefail

# 安装并准备 Conda 环境脚本
# 功能：
#  1) 下载并静默安装 Miniconda 到 /opt/anaconda3（如系统已有 conda 则跳过）
#  2) 创建 conda 环境 `autochecker`（Python 3.10）
#  3) 激活该环境并在项目根目录安装 requirements.txt

INSTALL_DIR=/root/anaconda3
MINICONDA_SH=/tmp/Miniconda3-latest-Linux-x86_64.sh
CONDA_ENV_NAME=code_check
PYTHON_VERSION=3.10
REPO_DIR=/root/code_check
REQUIREMENTS=${REPO_DIR}/requirements.txt

echo "Starting environment preparation..."

if [[ $EUID -ne 0 ]]; then
  echo "This script requires root privileges. Run with sudo or as root." >&2
  exit 1
fi

download_installer() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$MINICONDA_SH" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$MINICONDA_SH" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  else
    echo "Neither curl nor wget is available. Install one or download Miniconda manually." >&2
    exit 1
  fi
}

if [[ -x "$INSTALL_DIR/bin/conda" ]]; then
  echo "Found conda installation at $INSTALL_DIR; using it."
elif command -v conda >/dev/null 2>&1; then
  echo "A different conda was found on PATH, but Miniconda will be installed to $INSTALL_DIR to satisfy requirement."
  download_installer
  echo "Installing Miniconda to $INSTALL_DIR (silent mode)..."
  bash "$MINICONDA_SH" -b -p "$INSTALL_DIR"
  rm -f "$MINICONDA_SH"
else
  echo "Downloading Miniconda installer..."
  download_installer
  echo "Installing Miniconda to $INSTALL_DIR (silent mode)..."
  bash "$MINICONDA_SH" -b -p "$INSTALL_DIR"
  rm -f "$MINICONDA_SH"
fi

CONDA_SH="$INSTALL_DIR/etc/profile.d/conda.sh"
if [[ -f "$CONDA_SH" ]]; then
  # shellcheck disable=SC1090
  source "$CONDA_SH"
else
  echo "Cannot find conda initialization script at $CONDA_SH" >&2
  exit 1
fi

echo "Ensuring conda base is initialized..."
conda activate base >/dev/null 2>&1 || true

if conda env list | awk '{print $1}' | grep -qx "$CONDA_ENV_NAME"; then
  echo "Conda env '$CONDA_ENV_NAME' already exists; skipping creation."
else
  echo "Creating conda env '$CONDA_ENV_NAME' with Python $PYTHON_VERSION..."
  conda create -y -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION"
fi

echo "Activating environment '$CONDA_ENV_NAME'..."
conda activate "$CONDA_ENV_NAME"

if [[ -f "$REQUIREMENTS" ]]; then
  echo "Installing Python requirements from $REQUIREMENTS..."
  pip install --upgrade pip
  echo "当前 pip 路径: $(which pip)"
  pip install -r "$REQUIREMENTS"
else
  echo "Requirements file not found at $REQUIREMENTS" >&2
  exit 1
fi

echo "Environment setup complete. To use the environment interactively run:"
echo "  source $CONDA_SH && conda activate $CONDA_ENV_NAME"
echo "Project directory: $REPO_DIR"

exit 0
