<p align="center">
  <img src="doc/png/logo.svg" alt="AutoChecker Logo" width="360" />
</p>

<p align="center">
  <strong>From Specs and Patches to Checkers</strong>
</p>

<p align="center">
  把写在文档里的编码规范、藏在漏洞补丁里的安全经验，自动变成能扫描代码的静态代码检查器
</p>
<p align="center">
  <a href="https://autochecker.veilaxis.com/">
    <img src="https://img.shields.io/badge/🚀_在线体验-AutoChecker-2563eb?style=for-the-badge" alt="在线体验" />
  </a>
  <a href="https://github.com/SQUARE-RG/AutoChecker">
    <img src="https://img.shields.io/badge/GitHub-查看源码-24292f?style=for-the-badge&logo=github" alt="查看源码" />
  </a>
</p>
<p align="center">
  <a href="./README.md"><img src="https://img.shields.io/badge/lang-English-b0e8ff?style=flat-square&labelColor=0a0e14" alt="English"></a>
  <a href="./README-cn.md"><img src="https://img.shields.io/badge/lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-b0e8ff?style=flat-square&labelColor=0a0e14" alt="简体中文"></a>
  <a href="https://github.com/SQUARE-RG/AutoChecker/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-b0e8ff?style=flat-square&labelColor=0a0e14" alt="license"></a>
</p>

---

# AutoChecker
> **From Specs and Patches to Checkers.**

**AutoChecker 是一个基于大语言模型的智能静态代码检查器生成系统，能够将自然语言编码规范、代码测试用例以及漏洞修复补丁，自动转化为可在主流静态分析工具中执行的检查器。**

> **你只需定义“要检查什么”，AutoChecker 负责实现“如何检查”。** 从需求理解、检查器生成，到编译验证与迭代修复，让定制化静态代码检查器开发变得更加简单。

### News

- 🎉 **AutoChecker 生成的检查器发现的两项真实漏洞已获得 CVE 编号： [CVE-2026-103754](https://www.cve.org/CVERecord?id=CVE-2026-103754) 和 [CVE-2026-71364](https://www.cve.org/CVERecord?id=CVE-2026-71364)。**
- 🔍 **AutoChecker 生成的检查器已在 13 个开源代码仓库中发现并报告 16 项漏洞，全部获得项目开发者确认。**


<h3 align="center">真实开源项目验证</h3>

<p align="center">
  AutoChecker 已在多个真实开源项目中发现并报告安全缺陷。
</p>

<table align="center">
  <tr>
    <td align="center" width="180">
      <h2>16</h2>
      <p>项真实代码缺陷</p>
    </td>
    <td align="center" width="180">
      <h2>13</h2>
      <p>个开源仓库</p>
    </td>
    <td align="center" width="180">
      <h2>2</h2>
      <p>项 CVE 编号</p>
    </td>
  </tr>
</table>


### 为什么需要 AutoChecker？

CodeQL、Clang-Tidy、PMD 等静态分析工具提供了丰富的内置检查规则，但这些规则难以覆盖企业内部编码规范、项目特定约束以及不断出现的新型漏洞模式。

当现有规则无法满足需求时，开发者通常需要手动编写检查器，不仅要理解抽象语法树、控制流和数据流等程序分析技术，还需要熟悉不同静态分析框架的 API 与实现机制。**即使只是增加一条检测规则，也可能需要投入大量开发与调试工作。**

**AutoChecker 让开发者不再需要从零实现每一条检查规则。** 无论是希望将一条编码规范转化为自动化检查，还是从一次漏洞修复中提取可复用的检测逻辑，AutoChecker 都能够自动生成相应的检查器，并通过真实工具链进行验证和迭代优化。

### AutoChecker 能做什么？

AutoChecker 提供两种互补的检查器生成方式，满足软件质量与安全检测的不同需求。

| 生成方式 | 你需要提供 | AutoChecker 为你完成 |
| --- | --- | --- |
| **从规范生成检查器** | 自然语言规则描述、合规与违规代码示例 | 自动生成适用于 Clang-Tidy、CodeQL、PMD、Semgrep 等静态分析工具的检查器，让编码规范真正落地 |
| **从漏洞生成检查器** | CVE 或漏洞信息、修复补丁及相关代码仓库 | 分析漏洞根因，自动生成 CodeQL 安全检查器，将历史漏洞转化为可复用的同类缺陷检测能力 |

两种方式均采用**自动生成、真实验证、反馈修复**的工作流程。AutoChecker 不只是生成检查器代码，还会实际调用静态分析工具进行编译与测试，并根据编译错误、漏报和误报反馈迭代修复，最终输出经过验证的检查器及其测试结果。

### 典型应用场景

- **编码规范自动化落地**：将国家及行业标准、开源安全编码指南等自然语言规则转化为自动化检查器，让编码规范从文档走向实际执行。
- **企业与项目定制检查**：针对企业内部框架、专用 API、业务安全约束和团队编码约定，快速生成现有静态分析工具尚未覆盖的定制化检查器。
- **漏洞变体与同类缺陷检测**：从 CVE 及修复补丁中分析漏洞机制，生成可复用的安全检查器，帮助开发者在其他代码仓库中发现潜在的同类漏洞。
- **持续代码质量与安全保障**：将生成的检查器集成到代码审查、CI/CD 和安全扫描流程中，让定制化检查能力持续服务于软件研发过程。

### AutoChecker 如何工作？

AutoChecker 将传统上依赖静态分析专家完成的检查器开发过程，转化为由 AI 驱动的自动化工作流。

对于**规范与测试用例驱动**的生成方式，AutoChecker 首先理解自然语言规则及合规、违规代码示例，提取关键检测条件；随后检索目标静态分析框架的 API 和实现知识，生成候选检查器，并通过编译和测试验证其检测行为。如果出现编译失败、漏报或误报，系统会根据反馈自动修复，直至满足验证条件或达到预设迭代上限。

![Overview](AutoChecker.png)

对于**漏洞与补丁驱动**的生成方式，AutoChecker 从漏洞信息及修复补丁出发，自动探索相关源码，分析漏洞触发条件、根本原因与修复机制，将分析结果转化为结构化漏洞规格，并据此生成 CodeQL 检查器。系统通过漏洞版本与修复版本的差分验证，结合关键谓词的匹配反馈，持续定位和修复检查器中的检测逻辑问题。

最终，AutoChecker 输出可供目标静态分析工具使用的检查器代码，将**编码规范和历史漏洞知识转化为可持续复用的自动化检测能力**。

### 核心优势

- **无需从零编写检查器**：以自然语言、代码示例或历史漏洞为输入，自动完成检测逻辑分析、检查器生成与验证，降低定制化静态分析规则的开发门槛。
- **知识增强的智能生成**：结合检测逻辑引导的知识检索（LGKR）与 Agentic RAG，按需获取静态分析框架的 API、分析操作及实现示例，提高检查器生成的可靠性。
- **真实工具链验证与自动修复**：在实际静态分析环境中编译和运行候选检查器，利用测试反馈与差分谓词探测（DPP）定位问题，指导针对性修复。
- **多语言、多分析引擎支持**：支持面向 Clang-Tidy、Clang Static Analyzer、CodeQL、Semgrep 等分析引擎生成检查器，覆盖 C/C++、Java、Python、JavaScript、TypeScript、Rust 等语言，并提供 PMD 检查器生成能力。
- **让检测能力持续复用**：既能将相同规范应用于不同静态分析工具，也能将历史漏洞的修复经验转化为可复用的安全检查器，减少重复开发成本。


## 安装指南

AutoChecker 包含两条相互独立的检查器生成路线。请根据输入类型选择对应的安装与运行流程：

- **规范与测试用例驱动**：输入自然语言规则以及合规、违规代码示例，生成面向多种静态分析工具的检查器。
- **漏洞与补丁驱动**：输入漏洞信息、修复补丁以及修复前后的源码，生成用于检测同类缺陷的安全检查器。

### 路线一：规范与测试用例驱动的检查器生成

该路线目前仅保留手动安装说明。Docker 部署流程仍在调整，暂不建议使用。

#### 环境要求

| 项目 | 要求 |
| --- | --- |
| 磁盘空间 | 至少 64 GB |
| 内存 | 至少 16 GB |
| 处理器 | 至少 4 核 |
| 操作系统 | Ubuntu 22.04（推荐） |
| LLM API 密钥 | 需要一个大语言模型的 API Key，例如 DeepSeek、OpenAI 等 |

#### 步骤 1：准备 Python 环境

克隆仓库并进入项目根目录：

```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
cd AutoChecker
```

创建虚拟环境并安装依赖：

```shell
# 创建虚拟环境
conda create -n autochecker python=3.10
conda activate autochecker
pip install -r requirements.txt
```

#### 步骤 2：安装静态分析引擎

可根据实际需求选择安装对应的静态分析引擎：

1. [部署 PMD](/doc/pmd_install_cn.md)
2. [部署 clang-tidy](/doc/clang_tidy_install_cn.md)
3. [部署 CodeQL](/doc/codeql_deploy_cn.md)
4. [部署 Semgrep](/doc/semgrep_deploy_cn.md)

#### 步骤 3：配置模型与工具路径

复制项目提供的环境变量模板：

```bash
cp .env.example .env
```

然后编辑 `.env`，至少填写所使用模型对应的模型名称、API Key 和 API 地址；如果使用 CodeQL，还需要根据实际安装位置更新 `CODEQL_HOME` 及相应的 QL pack 路径。请勿将包含密钥的 `.env` 提交到版本控制系统。

#### 步骤 4：准备规则与测试套件

在项目根目录下新建 `rule.json`：

```json
{
    "data": {
        "ucassaat": [
            {
                "main_title": "use-uncheck-pointer-after-malloc",
                "description": "The rule requires that any pointer obtained through dynamic memory allocation functions (such as malloc, calloc, or realloc) must be checked for non-null before its first use. This check must occur before the pointer is used; performing the check after use is considered a violation. Acceptable check methods include explicit or implicit null pointer comparisons like if (ptr != NULL), if (ptr), or if (!ptr). If a dynamically allocated pointer is never used, it does not violate this rule. If a pointer is reallocated, it must be checked again before any subsequent use. This rule applies equally to global and local variables. Only one warning should be reported per violating pointer variable.",
                "rule_test_path": "/root/code_check/experiment/gjb8114/codeql_test_case/use_uncheck_pointer_after_malloc"
            }
        ]
    }
}
```

注意事项：

- `rule_test_path` 请使用绝对路径，并指向测试套件所在目录。
- 对于违反规则的测试用例，请在代码中使用 `CHECK-MESSAGES` 注释标记预期结果。

#### 步骤 5：运行

```shell
python src/main.py --rule_file rule.json --language cpp --analyzer clang-tidy
```

生成结果默认保存在 `result-generation` 目录中。

<!--
### 路线一的 Docker 部署（暂不开放）

#### 环境要求

| 依赖 | 说明 |
| --- | --- |
| Docker | 建议使用 28.1.1 或以上版本 |
| 操作系统 | Ubuntu 22.04（推荐），其他 Linux 发行版通常也可运行 |
| LLM API 密钥 | 需要一个大语言模型的 API Key，例如 DeepSeek、OpenAI 等 |

#### 步骤 1：克隆项目

```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
cd AutoChecker
git clone https://github.com/llvm/llvm-project.git --branch release/17.x --depth 1
```

#### 步骤 2：构建 Docker 镜像

构建过程会自动完成以下工作：安装 Python 运行环境、配置 `conda` 虚拟环境、下载嵌入模型，并编译相关静态分析工具链。整个过程大约需要 10 分钟。

```bash
docker build -t autochecker:1.0 .
```

> 构建过程中会执行依赖安装和编译，请耐心等待。看到 `Successfully tagged autochecker:1.0` 即表示构建成功。

#### 步骤 3：创建并启动容器

```bash
docker run -it --name autochecker-container autochecker:1.0 /bin/bash
```

执行后会自动进入容器交互终端，默认位于 AutoChecker 根目录。

#### 步骤 4：配置大模型

在容器内的项目根目录下创建 `.env` 文件，并填写你的大模型 API 信息：

```env
API_KEY=你的API密钥
MODEL=模型名称（如 deepseek、gpt-4 等）
BASE_URL=API接口地址（如 https://api.deepseek.com）
```

完成配置后，即可开始准备规则和测试用例。

#### 步骤 5：准备规则文件

在项目根目录下创建 `rule.json`，填写你的检测规则和测试用例路径：

```json
{
    "main_title": "你的规则名称",
    "title": "规则简述（可选）",
    "description": "详细描述这条规则需要检查的问题，以及它适用的场景。",
    "rule_test_path": "/绝对路径/测试用例目录/",
    "category": "规则分类（可选）"
}
```

测试用例要求：

- 使用与目标语言对应的文件后缀，例如 `.cpp`、`.c`、`.java`。
- 每个测试文件应能够独立编译。

#### 步骤 6：启动生成

```bash
python src/main.py --rule_file rule.json --language cpp --analyzer clang-tidy
```

程序运行时会实时输出处理进度。生成完成后，结果默认保存在 `result-generation/` 目录下，主要包括：

- `final_checker/`：最终生成的检查器代码，例如头文件和实现文件。
- `checker_generation_result.json`：检查器在测试用例上的表现报告，例如准确率、耗时和费用等信息。

#### 步骤 7：集成生成的检查器

生成的检查器代码可直接放入对应静态分析工具的检查器目录中，重新编译后即可使用。
-->

---

### 路线二：漏洞与补丁驱动的检查器生成

> **当前支持范围：该路线暂时只支持为 Java 漏洞生成 CodeQL 安全查询。** 输入的漏洞必须记录在 `autoql_data/project_info.csv` 中，运行时需要提供完整的 40 位修复提交 SHA。

#### 环境要求

| 项目 | 要求 |
| --- | --- |
| 磁盘空间 | 至少 64 GB |
| 内存 | 至少 16 GB |
| 处理器 | 至少 4 核 |
| 操作系统 | Ubuntu 22.04（推荐） |
| Python | 3.11 |
| CodeQL | CodeQL CLI 及 Java QL packs |
| LLM API 密钥 | 当前使用项目 `.env.example` 中定义的模型配置 |

#### 步骤 1：准备项目与 Python 环境

```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
cd AutoChecker

conda create -n autochecker-autoql python=3.11
conda activate autochecker-autoql
python -m pip install -r requirements.txt -r src/autoql/requirements.txt
```

漏洞与补丁驱动路线依赖 Python 3.11，建议使用独立环境，不要直接升级路线一使用的 Python 3.10 环境。

#### 步骤 2：安装 CodeQL

以下流程参考了 [QLCoder 的 Linux 安装说明](https://github.com/neuralprogram/qlcoder#native-linux)，并按 AutoChecker 的目录结构和脚本进行了调整。从 [CodeQL Action Releases](https://github.com/github/codeql-action/releases) 下载适用于 Linux 的 `codeql-bundle-linux64.tar.gz`。项目的 `.env.example` 以 CodeQL bundle 2.23.3 为示例；也可以使用其他版本，但必须同步修改 QL pack 路径。

以下示例将 CodeQL 解压到项目内的 `codeql-bundle-2.23.3` 目录：

```bash
mkdir -p codeql-bundle-2.23.3
tar -xzf /path/to/codeql-bundle-linux64.tar.gz \
  -C codeql-bundle-2.23.3 --strip-components=1

export PATH="$PWD/codeql-bundle-2.23.3:$PATH"
codeql version
```

如需在新终端中继续使用 CodeQL，请将其可执行文件目录永久加入 `PATH`，或在运行前重新执行上面的 `export` 命令。

#### 步骤 3：配置环境变量

项目已经提供 `.env.example`，无需从其他项目复制配置文件：

```bash
cp .env.example .env
```

编辑 `.env`，填写模型配置，并将 `CODEQL_HOME` 改为 CodeQL 的绝对路径，例如：

```env
MODEL_NAME=你的模型名称
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_BASE_URL=你的API地址

CODEQL_HOME=/absolute/path/to/AutoChecker/codeql-bundle-2.23.3
```

不同 CodeQL bundle 中 QL pack 的版本目录可能不同。先查看实际版本：

```bash
set -a
source .env
set +a

ls "$CODEQL_HOME/qlpacks/codeql/java-queries/"
ls "$CODEQL_HOME/qlpacks/codeql/java-all/"
```

然后在 `.env` 中更新 Java QL pack 路径：

```env
JAVA_SECURITY_QLPACK_PATH=/absolute/path/to/codeql-bundle/qlpacks/codeql/java-queries/<version>/Security/CWE
JAVA_LIBRARY_QLPACK_PATH=/absolute/path/to/codeql-bundle/qlpacks/codeql/java-all/<version>/semmle/code/java
```

`.env.example` 还包含 C/C++ 和 Python QL pack 的配置项，保留并按所安装 bundle 的实际版本更新即可。请勿将包含密钥的 `.env` 提交到版本控制系统。

#### 步骤 4：准备漏洞仓库与补丁

确认目标漏洞已经记录在 `autoql_data/project_info.csv` 中，然后使用本项目 `autoql_scripts` 目录下的脚本拉取仓库并生成修复差异：

```bash
CVE_ID="CVE-YYYY-NNNN"
python3 autoql_scripts/get_cve_repos.py --cve "$CVE_ID"
```

该脚本也支持批量处理：

```bash
# 多个 CVE
python3 autoql_scripts/get_cve_repos.py --cves "CVE-YYYY-NNNN,CVE-YYYY-MMMM"

# 处理 autoql_data/project_info.csv 中的全部 CVE
python3 autoql_scripts/get_cve_repos.py --all
```

#### 步骤 5：创建漏洞版本与修复版本的 CodeQL 数据库

```bash
# 为指定 CVE 创建数据库
python3 autoql_scripts/build_codeql_dbs.py --cve-id "$CVE_ID"

# 或为已准备的全部 CVE 创建数据库
python3 autoql_scripts/build_codeql_dbs.py
```

数据库使用 `--build-mode=none` 创建，无需运行目标 Java 项目的构建工具。对于指定 CVE，脚本会在 `cves/<CVE-ID>/` 下生成 `<CVE-ID>-vul` 和 `<CVE-ID>-fix` 两个数据库。

#### 步骤 6：构建 CodeQL 文档知识库

```bash
python3 autoql_scripts/codeql_docs_fetcher.py
```

本项目不需要执行 QLCoder 中的以下两个命令：

```text
python3 scripts/cwe_fetcher.py
python3 scripts/cves_fetcher.py
```

#### 步骤 7：生成并验证 CodeQL 检查器

将目标漏洞的完整修复提交 SHA 传给 AutoQL：

```bash
FIX_COMMIT_SHA="填写40位修复提交SHA"
PYTHONPATH=src python -m autoql.run_patch --commit "$FIX_COMMIT_SHA"
```

默认输出目录为 `autoql_runs/`。运行结果包含漏洞规格、生成及修复过程、CodeQL 编译与执行日志、评估结果，以及验证成功后的 `final.ql`。如需先检查输入、仓库版本和 CodeQL 数据库是否正确，而不调用大模型，可以运行：

```bash
PYTHONPATH=src python -m autoql.run_patch \
  --commit "$FIX_COMMIT_SHA" --preflight-only
```

## 当前支持的静态分析工具

AutoChecker 的两条检查器生成路线面向不同输入和检测目标，因此具有不同的静态分析工具与语言支持范围。

### 规范与测试用例驱动的检查器生成

该路线以自然语言规则描述及合规、违规测试用例为输入，面向编码规范、项目约束和定制化质量检查需求生成检查器。目前支持情况如下：

| 静态分析工具 | 支持语言 | 生成结果 | 当前状态 |
| --- | --- | --- | --- |
| PMD | Java | Java 检查器 | 已支持，参见 [PMD 部署说明](doc/pmd_install_cn.md) |
| Clang-Tidy | C/C++ | C++ 检查器源码 | 已支持，参见 [Clang-Tidy 部署说明](doc/clang_tidy_install_cn.md) |
| CodeQL | C/C++、Python | CodeQL 查询 | 已支持，参见 [CodeQL 部署说明](doc/codeql_deploy_cn.md) |
| Semgrep | C/C++、Java、Python、JavaScript、TypeScript、Rust | Semgrep YAML 规则 | 已支持，参见 [Semgrep 部署说明](doc/semgrep_deploy_cn.md) |
| Clang Static Analyzer | C/C++ | Clang Static Analyzer 检查器 | 实验性支持，安装和统一运行入口仍在完善 |

### 漏洞与补丁驱动的检查器生成

该路线以漏洞信息、修复补丁及修复前后的源码为输入，通过分析漏洞触发条件、根本原因和修复机制，生成用于检测同类缺陷的安全检查器。目前支持情况如下：

| 静态分析工具 | 支持语言 | 生成结果 | 当前状态 |
| --- | --- | --- | --- |
| CodeQL | Java | CodeQL 安全查询 | 已支持，可在漏洞版本与修复版本上进行差分验证 |

其中，“已支持”表示仓库中已有相应的生成与验证实现；“实验性支持”表示已经完成原型和实验验证，但工程化接口或部署文档仍需继续完善。各后端目前并非全部通过同一个命令入口调用，运行前请先阅读对应部署文档和源码入口。若希望完善现有后端，或增加新的静态分析工具与语言支持，请参阅[开发者指南](doc/Developer_Guide.md)。

## 配置说明

根目录下的 `config.json` 支持按需调整以下参数：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `max_round` | 每个测试用例的最大迭代轮次 | 2 |
| `max_compiler_trys` | 修复编译失败的最大尝试次数 | 5 |
| `top_key` | 检索最相关代码片段的数量 | 2 |
| `result_dir` | 结果输出目录 | result-generation/ |

## 论文引用

如果你的研究或项目使用了我们的工作，欢迎引用：

1. Jun Liu, Yuanyuan Xie, Jiwei Yan, Jinhao Huang, Jun Yan, Jian Zhang. Write Your Own CodeChecker: An Automated Test-Driven Checker Development Approach with LLMs. ICSE 2026. [paper](https://hanada31.github.io/pdf/ICSE2026_AutoChecker.pdf)

```bibtex
@inproceedings{AutoChecker,
      title={Write Your Own CodeChecker: An Automated Test-Driven Checker Development Approach with LLMs},
      author={Jun Liu and Yuanyuan Xie and Jiwei Yan and Jinhao Huang and Jun Yan and Jian Zhang},
      booktitle={Proceedings of the International Conference on Software Engineering (ICSE)},
      year={2026}
}
```

## 维护者与贡献者

AutoChecker 由 [SQUARE Research Group](https://square16.org/) 的成员持续开发与维护：

- Jun Liu([@nonsense-j](https://github.com/nonsense-j))
- Yuanyuan Xie([@xyyusr](https://github.com/xyyusr))
- [Liqiang Ji](https://carlson-jlq.github.io/liqiang-ji.github.io/) ([@carlson-jlq](https://github.com/Carlson-JLQ))
- Jinhao Huang ([@jinhao-huang](https://github.com/jinhao-huang))
- Yuyang Xie ([@sisifuCha](https://github.com/sisifuCha))
- Xianglong Qi ([@Meiosis-Poor](https://github.com/Meiosis-Poor))
- [Jiwei Yan](https://hanada31.github.io/)([@hanada31](https://github.com/hanada31))

## 参与贡献

AutoChecker 是一个开源项目，欢迎社区贡献。
更多细节请参考 [开发者指南](/doc/Developer_Guide.md)。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SQUARE-RG/AutoChecker&type=Date)](https://star-history.com/#SQUARE-RG/AutoChecker&Date)
