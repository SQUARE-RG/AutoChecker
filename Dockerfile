FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ============================================================
# Layer 1: System dependencies
# ============================================================
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    cmake ninja-build gcc g++ zlib1g-dev git libxml2 libedit-dev \
    openssh-server python3 libreadline-dev libgmp-dev pkg-config \
    libdebuginfod-dev python-is-python3 libexpat-dev libmpfr-dev \
    file source-highlight libsource-highlight-dev liblzma-dev \
    ccache \
    wget curl bzip2 ca-certificates sudo \
 && rm -rf /var/lib/apt/lists/*

# ============================================================
# Layer 2: Copy project + LLVM source, then run install.sh
# install.sh does: prepair_python_env → prepair_clang_tidy → clang_tidy_dev_flow
# ============================================================
COPY . /root/code_check
COPY llvm-project /root/code_check/llvm-project
WORKDIR /root/code_check

RUN chmod +x scripts/install.sh && bash scripts/install.sh

# ============================================================
# Layer 3: Embedding model download (not covered by install.sh)
# ============================================================
RUN mkdir -p /root/code_check/src/retriever/embedding_model \
 && /root/anaconda3/envs/code_check/bin/modelscope download \
    --model BAAI/bge-large-en-v1.5 \
    --local_dir /root/code_check/src/retriever/embedding_model/bge-large-en-v1.5

# ============================================================
# Runtime
# ============================================================
WORKDIR /root/code_check
CMD ["/root/anaconda3/envs/code_check/bin/python", "src/main.py", "--mode", "sdk"]
