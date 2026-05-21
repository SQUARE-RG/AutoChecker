<p align="center">
  <img src="doc/png/logo.svg" alt="AutoChecker Logo" width="360" />
</p>

<p align="center">
  <strong>Write Your Own Checker</strong>
</p>

<p align="center">
  面向主流静态分析工具的自动检查器生成框架
</p>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README-cn.md">简体中文</a> |
  <a href="https://github.com/oraios/serena/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-b0e8ff?style=flat-square&labelColor=0a0e14" alt="license"></a>
</p>

---

# AutoChecker

**AutoChecker 是一个根据用户给出的规则需求，自动为主流静态分析工具生成代码检查器的工具。**

在日常开发中，我们经常需要检查代码是否符合规范，例如是否存在空指针风险、资源是否正确释放、命名是否符合约定等。虽然静态分析工具提供了部分内置检查器，但这些检查器往往无法完全覆盖真实场景中的个性化需求；如果手动开发新的检查器，不仅成本高，而且容易出错。

AutoChecker 为这一场景提供了新的解决方案：**用户只需给出规则描述和示例，AutoChecker 就能自动生成对应静态分析工具可用的检查器**。对于同一条规则，AutoChecker 还可以生成面向多个分析工具的检查器，方便用户按需选用。

![Overview](AutoChecker.png)

## 核心能力

- **根据规则描述和测试用例自动生成检查器**：用户输入规则描述以及正反测试用例，工具即可输出在目标静态分析工具中可直接使用的检查器代码。
- **一次编写规约，多工具复用**：同一份规则描述和测试用例可复用于不同分析工具，减少重复工作，提高规则迁移效率。
- **面向多类静态分析工具扩展**：当前文档覆盖 `PMD`、`clang-tidy` 和 `CodeQL`，并将继续扩展更多工具支持。

## 在线体验

现在可以直接在浏览器中体验 AutoChecker：

[AutoChecker.platform](https://autochecker.veilaxis.com/)

## 安装指南

AutoChecker 目前提供两种安装方式：

- **手动安装**：手动安装依赖、配置环境变量并编译运行，可用于生成 `PMD`、`clang-tidy`、`CodeQL` 等工具的检查器。
- **Docker 部署**：通过 Docker 一键完成环境配置和工具链准备，目前支持生成 `clang-tidy` 和 `CodeQL` 检查器。

### 手动安装

#### 环境要求

| 项目 | 要求 |
| --- | --- |
| 磁盘空间 | 至少 64 GB |
| 内存 | 至少 16 GB |
| 处理器 | 至少 4 核 |
| 操作系统 | Ubuntu 22.04（推荐） |
| LLM API 密钥 | 需要一个大语言模型的 API Key，例如 DeepSeek、OpenAI 等 |

#### 步骤 1：准备环境

克隆仓库：

```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
```

创建虚拟环境并安装依赖：

```shell
# 创建虚拟环境
conda create -n autochecker python=3.10
conda activate autochecker

# 进入项目根目录
cd AutoChecker
pip install -r requirements.txt
```

#### 步骤 2：安装静态分析引擎

可根据实际需求选择安装对应的静态分析引擎：

1. [部署 PMD](/doc/pmd_install_cn.md)
2. [部署 clang-tidy](/doc/clang_tidy_install_cn.md)
3. [部署 CodeQL](/doc/codeql_deploy_cn.md)

#### 步骤 3：配置大模型

在项目根目录下创建 `.env` 文件，并填写你的大模型 API 信息：

```env
API_KEY=你的API密钥
MODEL=模型名称（如 deepseek、gpt-4 等）
BASE_URL=API接口地址（如 https://api.deepseek.com）
```

完成配置后，即可开始准备规则和测试用例。

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

---

### Docker 部署

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

## 当前支持的静态分析工具

| 工具 | 支持语言 |
| --- | --- |
| PMD | Java |
| Clang-tidy | C/C++ |
| CodeQL | 多语言 |

计划支持：

- Semgrep
- Clang Static Analyzer

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

1. Jun Liu*, Yuanyuan Xie*, Jiwei Yan#, Jinhao Huang, Jun Yan, Jian Zhang. Write Your Own CodeChecker: An Automated Test-Driven Checker Development Approach with LLMs. ICSE 2026. [paper](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/43/Write-Your-Own-Code-Checker-An-Automated-Test-Driven-Checker-Development-Approach-wi)

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

- Jun Liu
- Yuanyuan Xie
- [Liqiang Ji](https://carlson-jlq.github.io/liqiang-ji.github.io/) ([@carlson-jlq](https://github.com/Carlson-JLQ))
- Jinhao Huang ([@jinhao-huang](https://github.com/jinhao-huang))
- Yuyang Xie ([@sisifuCha](https://github.com/sisifuCha))
- Xianglong Qi ([@Meiosis-Poor](https://github.com/Meiosis-Poor))
- [Jiwei Yan](https://hanada31.github.io/)

## 参与贡献

AutoChecker 是一个开源项目，欢迎社区贡献。
更多细节请参考 [开发者指南](/doc/Developer_Guide.md)。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SQUARE-RG/AutoChecker&type=Date)](https://star-history.com/#SQUARE-RG/AutoChecker&Date)
