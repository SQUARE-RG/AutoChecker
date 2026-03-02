FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    build-essential \
    python3 \
    python3-venv \
    sudo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Clone repository and run project installer (scripts/install.sh expects to run as root)
RUN git clone https://github.com/Carlson-JLQ/code_check.git \
 && cd code_check \
 && git checkout web-release \
 && true

# Override llvm-project inside the container with the local copy from build context
COPY llvm-project /root/code_check/llvm-project

RUN cd /root/code_check \
 && chmod +x scripts/install.sh \
 && bash scripts/install.sh

# Ensure Miniconda installed to /root/anaconda3 by the project's script.
ENV PATH=/root/anaconda3/bin:${PATH}

# Create conda env named `code_cehck` (matches attachment commands) and install modelscope
RUN /root/anaconda3/bin/conda create -y -n code_cehck python=3.10 \
 && /root/anaconda3/envs/code_cehck/bin/pip install --no-cache-dir modelscope \
 && /root/anaconda3/envs/code_cehck/bin/modelscope download --model BAAI/bge-large-en-v1.5 --local_dir /root/code_check/src/retriever/embedding_model

WORKDIR /root/code_check

CMD ["/bin/bash"]
