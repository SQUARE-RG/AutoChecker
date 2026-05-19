# AutoChecker

**AutoChecker 是一个基于用户的规则检查需求，自动为主流静态分析工具（如 CodeQL、Clang-tidy等）生成代码检查器的工具**。

在日常开发中，我们经常需要检查代码是否符合规范（比如有没有空指针风险、资源是否正确释放、命名是否合规）。虽然静态分析工具提供了部分内置检查器，但内置检查器与用户需求常常存在不匹配的情况，如果自行开发满足需求的检查器，不仅耗时又容易出错。而AutoChecker提供了这一场景下的新方案：**用户给出需求（描述规则并给出示例），AutoChecker会自动帮你生成对应静态分析工具的代码检查器**。此外，仅需给定一条规则，AutoChecker可以生成多个分析工具的检查器供用户选用。

![Overview](Autochecker.png)

## 主要功能

- **基于规则描述和用例自动生成 checker**：用户输入规则描述和正反测试用例，工具输出该规则在选定静态分析工具中直接可用的检查器代码。
- **一次需求编写，多工具检查器生成**：对于检查需求，仅需一次性设计规则描述和测试用例作为规约，后续可生成适用于不同分析工具的 checker，方便用户高效选用。
- **支持多种主流静态检查工具**：目前支持 Clang-tidy（C/C++）、Clang Static Analyzer（C/C++）、 CodeQL（多语言）和PMD（Java），即将支持 Semgrep。

## 在线快速体验

[New!] 可点击链接快速在浏览器中体验工具效果：[autochecker.party](https://autochecker.veilaxis.com/en)

## 安装指南

AutoChecker有两种安装方式：
- 1. 手动安装依赖，配置环境变量，编译运行。
- 2. 通过 Docker 一键部署，自动配置好所有依赖环境和工具链，无需手动折腾编译环境。

第一种方式可以支持PMD,clang-tidy，codeql等工具的检查器生成。
第二种方式目前只支持clang-tidy，codeql的检查器生成。
### 手动安装
#### 前置要求
磁盘空间：至少64GB
内存：至少16GB
处理器：至少4核
操作系统：Ubuntu 22.04（推荐）
LLM API 密钥：需要一个大语言模型的 API Key（如 DeepSeek、OpenAI 等）

#### Step1 环境准备
克隆仓库：
```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
```
创建虚拟环境：
```shell
# 创建虚拟环境
conda create -n autochecker python=3.10
conda activate autochecker 
# 进入软件根目录
cd AutoChecker
pip install -r requirements.txt
```
#### Step2 安装静态分析引擎

PMD:
![deploy pmd](/doc/pmd_install_cn.md)
![deploy clang-tidy](/doc/clang_tidy_install_cn.md)
![deploy codeql](/doc/codeql_deploy_cn.md)

#### Step3 配置 LLM 大模型

在容器内的软件根目录下创建 `.env` 文件，填入你的大模型 API 信息：

```
API_KEY=你的API密钥
MODEL=模型名称（如 deepseek、gpt-4 等）
BASE_URL=API接口地址（如 https://api.deepseek.com）
```

配置完成后，安装就结束了。接下来只需准备规则和测试用例，就能开始生成 checker 了。

#### Step4 准备规则和测试套件

在项目根目录新建rule.json
```json
{
    "data": {
        "ucassaat": [
            {
                "main_title": "use-uncheck-pointer-after-malloc",
                "description": "The rule requires that any pointer obtained through dynamic memory allocation functions (such as malloc, calloc, or realloc) must be checked for non-null before its first use. This check must occur before the pointer is used; performing the check after use is considered a violation. Acceptable check methods include explicit or implicit null pointer comparisons like if (ptr != NULL), if (ptr), or if (!ptr). If a dynamically allocated pointer is never used, it does not violate this rule. If a pointer is reallocated, it must be checked again before any subsequent use. This rule applies equally to global and local variables. Only one warning should be reported per violating pointer variable.",
                "category": "ucassaat",
                "rule_test_path": "/root/code_check/experiment/gjb8114/codeql_test_case/use_uncheck_pointer_after_malloc"
            }
        ]
    }
}

```
注意：
- 如果您希望生成clang-tidy的checker，category字段值请和![deploy clang-tidy](/doc/clang_tidy_install_cn.md)中一致。
- rule_test_path请使用绝对路径，指向测试套件的位置。
- 测试套件里面违反规则的测试用例，请在代码中用"CHECK-MESSAGES"进行注释。

#### Step5 运行
```
python src/main.py --rule_file rule.json --language cpp  --analyzer clang-tidy
```
最终生成的结果会默认保存到result-generation目录中。



### Docker
#### 前置要求

| 依赖 | 说明 |
| ---- | ---- |
| **Docker** | 建议 28.1.1 或以上版本 |
| **操作系统** | Ubuntu 22.04（推荐），其他 Linux 发行版也可运行 |
| **LLM API 密钥** | 需要一个大语言模型的 API Key（如 DeepSeek、OpenAI 等） |

#### Step1克隆项目

```bash
git clone https://github.com/SQUARE-RG/AutoChecker.git
cd AutoChecker
```

#### Step2 构建 Docker 镜像

镜像构建过程会自动完成以下工作：安装 Python 运行环境、配置 conda 虚拟环境、下载嵌入模型、编译各静态分析工具的工具链，整个过程约需 10 分钟。

```bash
docker build -t autochecker:1.0 .
```

> 构建过程中会执行各项依赖的安装和编译，请耐心等待。看到 `Successfully tagged autochecker:1.0` 即表示构建成功。

#### Step3 创建并启动容器

```bash
docker run -it --name autochecker-container autochecker:1.0 /bin/bash
```

执行后会自动进入容器的交互终端，默认位于 AutoChecker 的根目录下。

#### Step4 配置 LLM 大模型

在容器内的软件根目录下创建 `.env` 文件，填入你的大模型 API 信息：

```
API_KEY=你的API密钥
MODEL=模型名称（如 deepseek、gpt-4 等）
BASE_URL=API接口地址（如 https://api.deepseek.com）
```

配置完成后，安装就结束了。接下来只需准备规则和测试用例，就能开始生成 checker 了。



#### Step5 准备规则文件

在软件根目录下创建 `rule.json`，填写你的检测规则和测试用例路径：

```json
{
    "main_title": "你的规则名称",
    "title": "规则简述（可选）",
    "description": "详细描述这条规则要检查什么问题，适用于什么场景。",
    "rule_test_path": "/绝对路径/测试用例目录/",
    "category": "规则分类（可选）"
}
```

测试用例要求：以 `.cpp`、`.c` 或 `.java` 等对应语言后缀结尾的代码文件，每个文件需能独立编译。

#### Step6 启动生成

```bash
python src/main.py --input rule.json
```

程序运行过程中会实时输出处理进度。生成完毕后，结果默认保存在 `result-generation/` 目录下，包含：
- **final_checker/**：最终生成的检查器代码（.h 头文件和 .cpp 实现文件）
- **checker_generation_result.json**：检查器在测试用例上的表现报告（准确率、耗时、费用等）

#### Step7 将生成的 checker 集成到你的工具中

生成的 checker 代码可直接放入对应静态分析工具的 checker 目录中，编译后即可使用。

## 支持的静态分析工具

| 工具 | 支持语言 |
| ---- | ---- |
| PMD | Java |
| Clang-tidy | C/C++ |
| Clang Static Analyzer | C/C++ |
| CodeQL | 多语言 |

**即将支持：**
- Semgrep

## 配置说明

根目录下的 `config.json` 可按需调整以下参数：

| 参数 | 说明 | 默认值 |
| ---- | ---- | ---- |
| `max_round` | 每个测试用例的最大迭代轮次 | 2 |
| `max_compiler_trys` | 修复编译失败的最大尝试次数 | 5 |
| `top_key` | 检索最相关代码片段的数量 | 2 |
| `result_dir` | 结果输出目录 | result-generation/ |

## 论文和引用
+ 论文pdf
  
+ 正式参考文献格式

+ bib 信息
