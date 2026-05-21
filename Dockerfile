FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ============================================================
# Layer 1: System dependencies
# 对应 prepair_clang_tidy.sh 的 apt-get 部分
# 单独分层以利用 Docker 缓存（很少变动）
# ============================================================
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev \
    openssh-server python3 libreadline-dev libgmp-dev pkg-config \
    libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev \
    file source-highlight libsource-highlight-dev liblzma-dev \
    ccache \
    wget curl bzip2 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ============================================================
# Layer 2: Miniconda + Python 环境 + Embedding 模型
# 对应 prepair_python_env.sh 的全部逻辑 + modelscope 下载
# ============================================================
RUN curl -fsSL -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
 && bash /tmp/miniconda.sh -b -p /root/anaconda3 \
 && rm /tmp/miniconda.sh

ENV PATH=/root/anaconda3/bin:${PATH}

COPY requirements.txt /tmp/requirements.txt
RUN source /root/anaconda3/etc/profile.d/conda.sh \
 && conda create -y -n code_check python=3.10 \
 && /root/anaconda3/envs/code_check/bin/pip install --no-cache-dir -r /tmp/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple \
 && /root/anaconda3/envs/code_check/bin/pip install --no-cache-dir modelscope -i https://pypi.mirrors.ustc.edu.cn/simple \
 && rm /tmp/requirements.txt

RUN mkdir -p /root/code_check/src/retriever/embedding_model \
 && /root/anaconda3/envs/code_check/bin/modelscope download \
    --model BAAI/bge-large-en-v1.5 \
    --local_dir /root/code_check/src/retriever/embedding_model/bge-large-en-v1.5

# ============================================================
# Layer 3: LLVM / Clang 编译
# 对应 prepair_clang_tidy.sh 的 cmake + build 部分
# （git clone 由 COPY 替代，跳过 git checkout）
# ============================================================
COPY llvm-project /root/code_check/llvm-project
WORKDIR /root/code_check/llvm-project

RUN git checkout release/17.x \
 && mkdir -p build && cd build \
 && cmake \
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
    -S ../llvm -B . \
 && cmake --build . --target FileCheck -j$(nproc) \
 && cmake --build . --target clang-tidy clang clang-query -j$(nproc)

# ============================================================
# Layer 4: 项目代码 + ucassaat 模块注册
# 对应 scripts/clang_tidy_dev_flow.sh（直接调用脚本）
# 这一层变动最频繁，利用 Docker 缓存只需增量编译
# ============================================================
WORKDIR /root/code_check
COPY . /root/code_check

RUN chmod +x scripts/clang_tidy_dev_flow.sh \
 && bash scripts/clang_tidy_dev_flow.sh

# ============================================================
# Runtime
# ============================================================
WORKDIR /root/code_check
CMD ["/root/anaconda3/envs/code_check/bin/python", "src/main.py", "--mode", "sdk"]
