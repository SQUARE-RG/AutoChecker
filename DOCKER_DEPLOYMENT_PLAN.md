# Docker 镜像部署方案

## 一、整体架构

```
┌──────────┐     docker pull      ┌───────────────┐
│  前端     │ ◄────────────────── │  Image Registry │
│          │                      └───────────────┘
│ 创建容器  │
│  ┌────┐  │     docker run       ┌──────────────────────┐
│  │容器 │  │ ◄── stdin ────────── │ python main.py       │
│  │    │  │ ─── stdout ─────────► │   --mode sdk          │
│  │    │  │                      │                      │
│  └────┘  │                      │ clang-tidy 预编译在内 │
└──────────┘                      └──────────────────────┘
```

前端流程：
1. `docker pull` 拉取镜像（本地构建好的 clang-tidy + 项目代码）
2. `docker run` 创建容器，容器启动后立即执行 `python src/main.py --mode sdk`
3. 容器阻塞在 stdin，等待前端传入 `GeneratorInput` JSON
4. 生成过程中，容器通过 stdout 逐行返回 Log / Progress / Artifact / Status JSON
5. 生成完成后容器退出，前端读取最终状态

---

## 二、Dockerfile 需要修改的地方

### 2.1 当前问题

| 问题 | 说明 |
|------|------|
| CMD 是 `/bin/bash` | 容器启动后进入交互 shell，不会自动运行 SDK |
| `git clone` 远程仓库 | 应该用 `COPY . /root/code_check` 从构建上下文复制本地代码 |
| conda 环境名是 `code_check`，但 config.json 指向 `code_check` 的 python | 路径一致，但 Docker 内不需要 conda 的交互 shell，需要直接设置 PATH |
| llvm-project 每次都 COPY | 约 2-3GB，构建时间很长。建议分离为基础镜像 + 项目镜像 |
| 安装脚本依赖 sudo | Docker 内是 root，不需要 sudo |
| pip 用 ustc 镜像 | 如果镜像要在外网使用，可能失败。应该可配置或 fallback |

### 2.2 推荐方案：二阶段构建

**阶段一：基础镜像（clang-tidy-builder）** — 变动频率低，单独构建推送

```dockerfile
FROM ubuntu:22.04 AS clang-tidy-base
ENV DEBIAN_FRONTEND=noninteractive

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl bzip2 ca-certificates build-essential \
    python3 python3-venv cmake ninja-build zlib1g-dev \
    libxml2 libedit-dev ccache && \
    rm -rf /var/lib/apt/lists/*

# Miniconda
RUN curl -fsSL -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash /tmp/miniconda.sh -b -p /root/anaconda3 && \
    rm /tmp/miniconda.sh

ENV PATH=/root/anaconda3/bin:${PATH}

# Python 环境 + requirements
COPY requirements.txt /tmp/requirements.txt
RUN conda create -y -n code_check python=3.10 && \
    /root/anaconda3/envs/code_check/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# 下载 embedding 模型
RUN /root/anaconda3/envs/code_check/bin/pip install --no-cache-dir modelscope && \
    /root/anaconda3/envs/code_check/bin/modelscope download \
        --model BAAI/bge-large-en-v1.5 \
        --local_dir /root/code_check/src/retriever/embedding_model

# 编译 clang-tidy（这一层最耗时，约 30-60 分钟）
COPY llvm-project /root/code_check/llvm-project
WORKDIR /root/code_check/llvm-project
RUN git checkout release/17.x && \
    mkdir -p build && cd build && \
    cmake -G Ninja \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DLLVM_TARGETS_TO_BUILD=X86 \
      -DLLVM_ENABLE_PROJECTS='clang;clang-tools-extra' \
      -DBUILD_SHARED_LIBS=ON \
      -DLLVM_INCLUDE_TESTS=OFF \
      -DCLANG_INCLUDE_TESTS=OFF \
      -S ../llvm -B . && \
    cmake --build . --target FileCheck -j$(nproc) && \
    cmake --build . --target clang-tidy clang clang-query -j$(nproc)
```

**阶段二：项目镜像（AutoChecker）** — 频繁变动，基于阶段一的镜像

```dockerfile
FROM clang-tidy-base:latest

# 复制项目代码（llvm-project 已在基础镜像中）
COPY . /root/code_check

# 注册 ucassaat 模块到 clang-tidy 源码树
RUN cd /root/code_check && \
    cp scripts/clang-tidy-work-flow/remove_clang_tidy_check.py \
       llvm-project/clang-tools-extra/clang-tidy/ && \
    cp scripts/clang-tidy-work-flow/test_check_clang_tidy.py \
       llvm-project/clang-tools-extra/test/clang-tidy/ && \
    cp scripts/clang-tidy-work-flow/clang-tidy/CMakeLists.txt \
       llvm-project/clang-tools-extra/clang-tidy/CMakeLists.txt && \
    cp scripts/clang-tidy-work-flow/clang-tidy/ClangTidyForceLinker.h \
       llvm-project/clang-tools-extra/clang-tidy/ClangTidyForceLinker.h && \
    mkdir -p llvm-project/clang-tools-extra/clang-tidy/ucassaat && \
    mkdir -p llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat && \
    for f in UcasSaatTidyModule.cpp CMakeLists.txt HelloWorldCheck.h HelloWorldCheck.cpp; do \
      cp scripts/clang-tidy-work-flow/$f llvm-project/clang-tools-extra/clang-tidy/ucassaat/; \
    done && \
    cmake --build llvm-project/build --target clang-tidy -j$(nproc)

# 构建 embedding 知识库缓存
RUN /root/anaconda3/envs/code_check/bin/python -c "from retriever.retrieve_from_astMatchers import embedding_ast_matchers; embedding_ast_matchers()" && \
    /root/anaconda3/envs/code_check/bin/python -c "..."  # 其他 embedding 同理

WORKDIR /root/code_check

# 关键：CMD 启动 SDK 模式
CMD ["/root/anaconda3/envs/code_check/bin/python", "src/main.py", "--mode", "sdk"]
```

### 2.3 单阶段方案（简单但不推荐）

如果不想分离基础镜像，可以将上述两步合并。缺点是每次改一行代码就要重新编译整个 LLVM（30-60 分钟）。

```dockerfile
# ... 系统依赖 + conda + pip + embedding + LLVM 编译 ...

WORKDIR /root/code_check
COPY . .

# 注册模块 + 增量编译
RUN ... && cmake --build llvm-project/build --target clang-tidy -j$(nproc)

CMD ["/root/anaconda3/envs/code_check/bin/python", "src/main.py", "--mode", "sdk"]
```

---

## 三、代码需要修改的地方

### 3.1 核心问题：stdout 污染

SDK 协议要求 **stdout 只输出 JSON 行**。但当前代码在 clang-tidy 流程中大量使用 `print()` 直接写 stdout，这会破坏协议。

**影响 clang-tidy SDK 流程的文件：**

| 文件 | print 数量 | 影响 |
|------|-----------|------|
| `src/plateform/clang_tidy.py` | 22 | **严重** — 编译、模板生成、测试运行等核心操作都 print |
| `src/help/clang_tidy_utils.py` | 3 | **中等** — `get_Case_AST()` 打印 AST 节点信息 |
| `src/entity/concreteProduct_Clang_Tidy.py` | 4 | **低** — `getInfo()` 方法，SDK 流程中不被调用 |

**修改方案：将所有 `print()` 改为 `logger.debug()`**

```python
# 修改前
print("返回码:", result.returncode)
print("标准输出:\n", result.stdout)

# 修改后
logger.debug(f"返回码: {result.returncode}")
logger.debug(f"标准输出:\n{result.stdout}")
```

这样做的好处：
- `logger.debug()` 默认输出到 **stderr**，与 stdout 的 JSON 协议互不干扰
- 本地文件模式仍然可以通过日志文件查看调试信息
- 容器模式下 stderr 可被 Docker 捕获（`docker logs`）

需修改的函数清单（`src/plateform/clang_tidy.py`）：

| 函数 | 修改点 |
|------|--------|
| `pre_Generate_Checker_Template()` | 4 处 print → logger.debug |
| `remove_Checker_Template()` | 4 处 print → logger.debug |
| `runChecker()` | 6 处 print → logger.debug |
| `run_Checker_with_Check_clang_tidy()` | 2 处 print → logger.debug |
| `modifyCheckerCode()` | 3 处 print → logger.debug |
| `compiler_clang_tidy()` | 4 处 print → logger.debug |

需修改的函数清单（`src/help/clang_tidy_utils.py`）：

| 函数 | 修改点 |
|------|--------|
| `get_Case_AST()` | 3 处 print → logger.debug |

### 3.2 次要注意项

**① `autoCheckerClient.log()` vs `logger`**

当前 `main_sdk()` 同时使用 `autoCheckerClient.log()`（stdout JSON）和 `loguru.logger`（stderr/文件）。容器模式下：
- `autoCheckerClient.log()` → stdout → 前端可见
- `logger.info()` → stderr → `docker logs` 可见

这是合理的设计，不需要修改。

**② `init_logger()` 的日志目录**

容器内 `/root/code_check/logs/` 需要可写。如使用只读 rootfs，需要挂载 volume 或改为写 `/tmp/`。

**③ `config.json` 中硬编码的路径**

```json
"python_env": "/root/anaconda3/envs/code_check/bin/python",
"clang-tidy": "/root/code_check/llvm-project/clang-tools-extra/clang-tidy/"
```

这些路径在容器中是固定的，不需要修改。但注意 `python_env` 指向的 conda python 必须在 CMD 中使用一致的解释器。

**④ embedding 知识库预热**

`bge_embedding.py` 中的 `embedding_ast_matchers()` 在首次调用时构建 embedding 缓存。建议在 Dockerfile 中预构建，避免容器首次启动时的延迟。

---

## 四、`main_sdk()` 流程在容器中的运行时行为

```
容器启动
    │
    ▼
python src/main.py --mode sdk
    │
    ├── init_logger()                     → stderr: loguru 初始化
    ├── autoCheckerClient.log("Waiting...") → stdout: {"type":"log","message":"Waiting..."}
    │
    ├── autoCheckerClient.get_input()     → 阻塞，等待 stdin
    │       │
    │       │ 前端通过 docker exec 或 attach 写入 GeneratorInput
    │       ▼
    ├── 解析 GeneratorInput
    ├── get_llm_client_from_config()      → 用前端传入的 api_key
    ├── adapt_sdk_input_to_entities()     → 代码写入 temp_test_dir
    │
    ├── pre_compiler_clang_tidy()         → 增量编译（如果模板没变则很快）
    │       │
    │       │ stderr: cmake 编译日志
    │
    ├── pre_Generate_Checker_Template()   → 调用 add_new_check.py
    │       │
    │       │ stderr: 脚本输出
    │
    ├── checker_generator.generate_checker()
    │       │
    │       ├── stdout: ProgressMessage("Generating initial checker")
    │       ├── stdout: LogMessage(...)
    │       ├── ... LLM 调用 + 编译 + 测试 ...
    │       ├── stdout: ArtifactMessage(checker.cpp + test_results)
    │       ├── stdout: ProgressMessage("Checker generation completed")
    │
    ├── save_final_checkers()             → 复制到 result_dir
    ├── stdout: StatusMessage(COMPLETED)
    │
    ├── remove_Checker_Template()
    ├── cleanup_sdk_temp_dir()
    │
    └── 进程退出 (exit 0)
```

---

## 五、前端交互方式

前端有两种方式与容器通信：

### 方式 A：`docker run` + attach stdin/stdout（推荐）

```bash
# 启动容器，stdin/stdout 直连
docker run -i --rm \
  --name autochecker-<rule_name> \
  autochecker:latest

# 前端通过容器的 stdin 写入 GeneratorInput
# 前端通过容器的 stdout 读取 JSON 消息
# 容器完成后自动退出并清理 (--rm)
```

### 方式 B：Docker SDK（Python/Go）

```python
import docker
client = docker.from_env()
container = client.containers.run(
    "autochecker:latest",
    stdin_open=True,
    stdout=True,
    stderr=True,
    detach=True,
)

# 写入 GeneratorInput
socket = container.attach_socket(params={'stdin': 1, 'stdout': 1, 'stream': 1})
socket.sendall(json.dumps(generator_input).encode() + b'\n')
socket.close_write()

# 读取 JSON 消息
for line in socket:
    msg = json.loads(line)
    if msg['type'] == 'artifact':
        handle_artifact(msg)
    elif msg['type'] == 'status':
        break

container.wait()
container.remove()
```

---

## 六、实施步骤建议

| 步骤 | 内容 | 预估时间 |
|------|------|---------|
| 1 | **stdout 清理**：将 `clang_tidy.py` 和 `clang_tidy_utils.py` 中所有 `print()` 改为 `logger.debug()` | 30 分钟 |
| 2 | **编写 stage-1 Dockerfile**：clang-tidy 基础镜像（OS + conda + pip + LLVM 编译 + embedding 预热） | 1 小时 |
| 3 | **编写 stage-2 Dockerfile**：项目镜像（COPY 代码 + 注册模块 + CMD） | 30 分钟 |
| 4 | **构建基础镜像并推送**（首次需 30-60 分钟编译 LLVM） | 等待 |
| 5 | **构建项目镜像并推送**（后续改动只需 2-5 分钟） | 等待 |
| 6 | **端到端测试**：`docker run` 传入一条规则，验证 stdout JSON | 1 小时 |

---

## 七、预估的镜像大小和构建时间

| 层 | 大小 | 首次构建 |
|----|------|---------|
| Ubuntu 22.04 base | ~77 MB | 1 分钟 |
| 系统依赖 (apt) | ~500 MB | 3 分钟 |
| Miniconda + pip packages | ~3 GB | 10 分钟 |
| Embedding 模型 | ~1.3 GB | 2 分钟 |
| llvm-project 源码 | ~2 GB | COPY 耗时 |
| LLVM 编译产物 (build/) | ~4 GB | **30-60 分钟** |
| 项目代码 | ~50 MB | COPY 耗时 |
| **总计** | ~11 GB | 首次 ~1 小时 |

使用二阶段构建后：
- 基础镜像（含 LLVM 编译产物）：约 10 GB，**极少变动**
- 项目镜像（仅代码层）：约 50 MB 增量，**每次改动 2-5 分钟**
