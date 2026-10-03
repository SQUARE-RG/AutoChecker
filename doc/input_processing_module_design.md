# AutoChecker 输入处理与测试生成模块设计

## 1. 目标

输入 PDF、Word、图片或纯文本规范文档，输出 AutoChecker 可消费的规则 JSON，并在下一阶段根据规则和原文示例生成测试用例。

```text
阶段一：文档解析
原始文档 -> manifest.json + document.md + blocks.json

阶段二：规则抽取
阶段一产物 -> 分块 -> LLM 抽取规则和示例 -> autochecker_rules.json

阶段三：测试生成
autochecker_rules.json -> 正反测试文件 -> 回填测试路径和数量
```

三个阶段分别运行并落盘。调整规则抽取或测试生成时，不重复执行耗时的 PaddleOCR。

## 2. 总体结构

```text
PDF / Word / 图片 / TXT / Markdown / HTML
                    │
            1. 输入转换与标准化
                    │
          PDF / 图片 / 结构化纯文本
                    │
          2. PaddleOCR 结构化解析
                    │
             Markdown + JSON
                    │
             3. 文档分块
                    │
       4. LLM 逐块抽取规则和示例
                    │
             5. 合并和去重
                    │
          6. 导出规则 JSON
                    │
          7. Agent 生成测试用例
```

## 3. 处理步骤

### 3.1 输入转换与标准化

按照文件类型选择处理方式：

| 输入格式 | 处理方式 |
|---|---|
| PDF | 直接交给 PaddleOCR |
| PNG/JPEG/TIFF | 直接交给 PaddleOCR |
| DOC/DOCX | 使用 LibreOffice headless 转成 PDF |
| TXT | 检测编码后直接读取 |
| Markdown | 直接读取并保留标题层级 |
| HTML | 提取正文；复杂页面可先渲染成 PDF |

转换后保存：

- 原始文件；
- 转换后的文件；
- 文件 SHA-256；
- 文件类型、页数和转换日志。

### 3.2 PaddleOCR 结构化解析

PDF 和图片使用 PaddleOCR PP-StructureV3，输出：

- 按阅读顺序排列的 Markdown；
- 按页组织的 JSON；
- 标题、正文、代码、表格、列表、页眉页脚等元素类型；
- 每个元素的页码、坐标和 OCR 置信度；
- 页面图片；
- PaddleOCR 原始响应和分批检查点。

每个结构块统一为：

```json
{
  "block_id": "page-31-block-7",
  "page": 31,
  "type": "paragraph_title",
  "text": "5.3.1.8 准则 R-1-3-8",
  "bbox": [102, 140, 712, 181],
  "confidence": 0.98
}
```

TXT、Markdown 等不经过 PaddleOCR，但需要转换成相同的 block 结构。

阶段一输出目录：

```text
result_input_processing/<document_id>/
├── source/                     # 原始文档
├── converted/                  # Word 等格式的转换结果
├── paddleocr/
│   ├── batches/                # PDF 分批解析检查点
│   └── raw_response.json       # 合并后的 PaddleOCR 原始响应
├── manifest.json               # 文档元数据、哈希、页数和产物路径
├── document.md                 # 按阅读顺序整理的文档
└── blocks.json                 # 统一结构块
```

阶段一结束后，PaddleOCR 不再参与规则抽取和测试生成。

### 3.3 文档分块

当前实现以完整页面为最小单位，按照 token 上限连续装入页面：

- chunk 保留原始页码和 block ID；
- 相邻 chunk 默认重叠 1 页，避免跨页规则或示例被截断；
- 默认上限为 12000 tokens，可通过命令行调整；
- 不从页面中间切分；单页超过上限时，该页独立成为一个 chunk；
- 每个 chunk 保存为 `chunks/chunk-xxxx.md`；
- `chunks/chunks.json` 保存 chunk、页码、block ID 和文本的对应关系。

示例：

```text
chunk-0001：第 1～12 页
chunk-0002：第 12～23 页
chunk-0003：第 23～34 页
```

### 3.4 逐块抽取规则和示例

每个 chunk 调用一次 LLM。LLM 判断其中是否包含有效规范：

- 包含规范：输出规则描述及其示例；
- 不包含规范：返回 `{"rules": []}`，程序直接忽略该 chunk。

不输出 `chunk_type`、分类理由或 chunk 置信度。

LLM 固定返回：

```json
{
  "rules": [
    {
      "rule_id": "R-1-1-1",
      "main_title": "do-not-redefine-keywords-with-macros",
      "description": "禁止通过宏定义改变关键字和基本类型的含义。",
      "rule_type": "required",
      "examples": [
        {
          "type": "violation",
          "code": "#define long 100\n..."
        },
        {
          "type": "compliant",
          "code": "#define LONG_NUM 100\n..."
        }
      ]
    }
  ]
}
```

`rule_type` 由 LLM 根据文档填写，只允许：

- `required`：强制性规则，原文使用“必须、禁止、不得、应当”等强制表述，或者位于强制准则章节；
- `advisory`：建议性规则，原文使用“建议、推荐、宜、可参照”等建议表述，或者位于建议准则章节。

`examples[].type` 只允许：

- `violation`：违反规则的示例；
- `compliant`：遵守规则的示例；
- `illustrative`：用于解释规则，但原文没有明确正反属性的示例。

抽取要求：

- 同一个显式规则编号只输出一条规则；
- 同一编号中的多个条件保留在一个完整 `description` 中；
- 示例、原因和背景不能单独生成规则；
- 将“违背示例”“遵循示例”关联到所属规则；
- 没有示例的规则允许 `examples` 为空；
- 目录、普通说明、评价结果和无关图表不生成规则；
- 不补充原文没有表达的约束。

LLM 可以修复示例中明显的 OCR 和排版错误，例如括号、分号、缩进以及 `retum` 等误识别，但不能改变示例的正反属性，也不能增加新的规则场景。

### 3.5 程序补充、合并和去重

LLM 不生成来源信息。程序自动为每条候选规则添加当前 chunk：

```json
"source_chunks": ["chunk-0001"]
```

合并规则：

1. `rule_id` 相同的规则合并；
2. 无编号规则根据 `main_title` 和 `description` 相似度合并；
3. 合并所有 `source_chunks`；
4. 合并所有 `examples`；
5. 示例按照 `type + 去除空白后的 code` 去重。

### 3.6 阶段二输出 JSON

阶段二最终输出 `autochecker_rules.json`：

```json
{
  "data": {
    "gjb8114": [
      {
        "rule_id": "R-1-1-1",
        "main_title": "do-not-redefine-keywords-with-macros",
        "description": "禁止通过宏定义改变关键字和基本类型的含义。",
        "rule_type": "required",
        "source_chunks": ["chunk-0001"],
        "examples": [
          {
            "type": "violation",
            "code": "#define long 100\n..."
          },
          {
            "type": "compliant",
            "code": "#define LONG_NUM 100\n..."
          }
        ],
        "rule_test_path": ""
      }
    ]
  }
}
```

字段来源：

| 字段 | 来源 |
|---|---|
| `data` 下的分类名 | 程序使用 `--category` 填充 |
| `rule_id` | LLM 从原文抽取 |
| `main_title` | LLM 生成，程序规范为唯一 kebab-case |
| `description` | LLM 根据原文整理 |
| `rule_type` | LLM 判断并填写 |
| `source_chunks` | 程序根据当前 chunk 填充并合并 |
| `examples` | LLM 提取和整理，程序去重 |
| `rule_test_path` | 程序初始化为空字符串 |

通过 `source_chunks` 打开对应的 `chunks/chunk-xxxx.md`，再根据 `chunks/chunks.json` 中的页码定位 `document.md` 原文。

## 4. 阶段三：生成测试用例

### 4.1 命令输入

阶段三读取阶段二的规则 JSON。测试输出根目录必须由 `--output-dir` 指定，不在代码中写死：

```bash
python scripts/generate_rule_tests.py \
  --rules result_input_processing/gjb8114-2013/autochecker_rules.json \
  --output-dir experiment/gjb8114/cpp/test_cases \
  --output-rules experiment/gjb8114/cpp/gjb8114_rules_with_tests.json \
  --language cpp \
  --negative-count 10 \
  --positive-count 10 \
  --batch-size 4 \
  --max-repair-attempts 3
```

关键参数：

| 参数 | 说明 |
|---|---|
| `--rules` | 阶段二输出 JSON |
| `--output-dir` | 必填，测试用例输出根目录 |
| `--output-rules` | 回填测试信息后的新规则 JSON，不覆盖阶段二原文件 |
| `--language` | 必填，`c`、`cpp`、`python`、`java` 之一 |
| `--negative-count` | 每条规则需要的 negative case 数量 |
| `--positive-count` | 每条规则需要的 positive case 数量 |
| `--batch-size` | 每次 Agent 调用最多生成的用例总数 |
| `--max-repair-attempts` | 单个错误用例最多修复次数 |
| `--compiler` | 可选，显式指定 C/C++ 编译器或 `javac` 路径 |

一次运行只处理一种语言。不同语言分别运行并输出各自的规则 JSON，这样每条规则仍然只需要一个 `rule_test_path`。

### 4.2 输出目录

程序在指定根目录下按 `main_title` 创建子目录：

```text
<output-dir>/
└── <main_title>/
    ├── negative_01.c
    ├── negative_02.c
    ├── positive_01.c
    └── positive_02.c
```

扩展名由程序根据 `--language` 确定：

| language | 扩展名 |
|---|---|
| `c` | `.c` |
| `cpp` | `.cpp` |
| `python` | `.py` |
| `java` | `.java` |

生成中的文件先写入 `<output-dir>/.staging/<main_title>/`，通过校验后再移动到正式目录，避免不完整文件被后续 checker 使用。

### 4.3 规则可行性预判

每条规则生成测试前，先由 Agent 结合规则描述、原文示例、目标语言和语言版本进行一次可行性判断：

```json
{
  "status": "supported",
  "reason": "存在能够在单个源文件中表达且通过基础编译的真实负例"
}
```

`status` 只能是：

| 状态 | 处理方式 |
|---|---|
| `supported` | 继续生成正例和负例 |
| `requires_multiple_files` | 当前 AutoChecker 不支持多文件 case，终止本规则并继续下一条 |
| `compile_error_only` | 真实负例都会被编译器直接拒绝，终止本规则并继续下一条 |

判断顺序固定：先判断真实违背是否必须依赖多个源文件；能够单文件表达时，再判断是否至少存在一种能通过基础编译的真实负例。不得通过条件编译隐藏违背代码、只用注释描述其他文件或修掉违背点来获得可编译代码。

可行性结果写入规则 checkpoint。输入未变化时，断点续跑直接复用，不重复调用 Agent。两类不支持规则的 `rule_test_path` 保持为空，具体状态和原因写入 `generation_report.json`。

### 4.4 分批生成

不让 Agent 一次生成全部 20 个用例。程序按照 `--batch-size` 分批请求，默认每批生成 2 个 negative 和 2 个 positive：

```text
目标：10 negative + 10 positive
batch-size：4

第 1 批：negative 01～02 + positive 01～02
第 2 批：negative 03～04 + positive 03～04
……
```

这样可以控制响应长度，并且某个用例失败时不需要重新生成整条规则的所有测试。

每批 Agent 输入：

- `main_title`、`description`、`rule_type` 和 `examples`；
- 目标语言和语言版本；
- 本批需要的正反用例数量；
- 程序预先分配的文件名；Java 同时提供必须使用的类名；
- 已生成用例的简短覆盖点，避免重复。

Agent 返回结构化 JSON，程序负责命名和写文件：

```json
{
  "cases": [
    {
      "polarity": "negative",
      "intent": "通过宏定义改变 long 关键字含义",
      "code": "#define long 100\n..."
    },
    {
      "polarity": "positive",
      "intent": "使用普通大写宏名称",
      "code": "#define LONG_NUM 100\n..."
    }
  ]
}
```

`intent` 只写入内部 checkpoint，用于去重和修复，不加入最终规则 JSON。

生成要求：

- Negative case 必须违反规则，未来 checker 应当报警；
- Positive case 必须遵守规则，未来 checker 不应报警；
- 每个文件只测试一个主要场景；
- 测试代码必须自包含，默认只使用语言标准库；
- 同一规则的用例应覆盖不同语法形式、类型和边界；
- 原文示例用于理解规则，不能仅修改变量名后重复生成；
- 原文没有示例时，根据 `description` 生成测试。

### 4.5 多语言校验

每个文件独立校验，命令由程序使用参数数组启动，并设置超时时间，不执行生成的程序：

| 语言 | 默认校验命令 |
|---|---|
| C | 优先 `clang -std=c11 -fsyntax-only`，不可用时使用 `gcc` |
| C++ | 优先 `clang++ -std=c++17 -fsyntax-only`，不可用时使用 `g++` |
| Python | `python -m py_compile <file.py>` |
| Java | `javac -proc:none -d <temp-classes-dir> <file.java>` |

- C/C++ 只做前端编译，不链接、不运行，也不启用 `-Werror`；
- Python 只编译字节码，不导入或执行测试代码；
- Java 每个文件独立编译，Agent 使用程序指定的类名，确保 public class 与文件名一致；
- Java class 和 Python 字节码输出到临时目录；
- 编译器路径、C/C++ 标准和超时时间允许通过配置覆盖。

Negative case 也必须通过基础语法或编译检查。Negative 表示违反待检测规则，不表示代码可以存在无关语法错误。

基础校验只能确认代码能被语言工具处理。checker 尚未生成，因此阶段三不能确定 negative 是否一定报警、positive 是否一定不报警。

### 4.6 失败用例修复

程序只把失败用例交给 Agent 修复，已经通过的文件不重新生成。修复输入包含：

```text
规则描述和 rule_type
原文 examples
用例 polarity 和 intent
当前错误代码
编译器或语法检查器的完整诊断
目标语言、语言版本和必须使用的文件名/类名
```

修复要求：

1. 只返回修正后的单个代码文件；
2. 保留原来的 `polarity` 和 `intent`；
3. 只修复校验错误，不把 negative 修成 compliant；
4. 不引入非标准第三方依赖；
5. 修复后立即使用同一个校验器重新检查。

每个失败用例最多修复 `--max-repair-attempts` 次。超过次数后，丢弃失败代码，让 Agent 根据相同 `polarity` 和 `intent` 重新生成替代用例。替代用例仍无法通过校验、导致目标数量无法补足时，将该规则记录为失败，不回填 `rule_test_path`。

### 4.7 去重和完成条件

程序检查：

- `polarity` 必须是 `negative` 或 `positive`；
- 返回数量不能超过当前批次要求；
- 代码不能为空；
- 去除注释和空白后的代码哈希不能重复；
- `intent` 不能与已有用例完全相同；
- 每个文件必须通过对应语言校验。

只有达到目标 negative/positive 数量，并且所有文件校验通过，该规则才算完成。

### 4.8 回填规则 JSON

完成后，程序将绝对路径和实际文件数量写入 `--output-rules` 指定的新文件：

```json
{
  "rule_test_path": "/root/code_check/experiment/gjb8114/cpp/test_cases/do-not-redefine-keywords-with-macros",
  "negative_case_amount": 10,
  "positive_case_amount": 10
}
```

- `rule_test_path`：程序根据 `--output-dir` 和 `main_title` 填写；
- `negative_case_amount`：程序统计通过校验的 negative 文件；
- `positive_case_amount`：程序统计通过校验的 positive 文件。

`issuccess` 和 `performance` 属于后续 checker 运行评测阶段，不在阶段二或阶段三输出。

### 4.9 断点续跑

每条规则保存 checkpoint，记录规则输入哈希、目标语言、目标数量、已完成用例、修复次数和最后一次校验结果。

- 输入哈希未变化且正式文件完整：跳过该规则；
- 部分批次完成：从缺少的编号继续生成；
- 规则描述、示例、语言或数量变化：仅使对应规则 checkpoint 失效；
- 使用 `--force`：重新生成全部规则。

## 5. 当前 CPU 服务器部署判断

当前服务器资源：

- Ubuntu 22.04 x86_64；
- 56 个逻辑 CPU，Intel Xeon E5-2680 v4，支持 AVX2；
- 内存 220 GiB，可用约 177 GiB；
- 可用磁盘约 2.7 TiB；
- 当前环境未检测到 NVIDIA GPU。

该服务器能够部署并运行 PaddleOCR PP-StructureV3 CPU 版本。没有 GPU 不影响功能，只会降低 OCR 和版面模型的处理速度。

PaddleOCR 使用独立的 Python 3.10/3.11 Conda 环境和 HTTP 服务，AutoChecker 通过 `127.0.0.1:18080` 调用。具体步骤见 [PaddleOCR 部署手册](./paddleocr_service_deployment_cn.md)。

## 6. 运行方式

### 6.1 阶段一

```bash
python scripts/parse_regulation_document.py \
  --input doc/GJB-8114-2013.pdf \
  --output-dir result_input_processing/gjb8114-2013
```

PDF 默认每 10 页调用一次 PaddleOCR。每批响应保存在 `paddleocr/batches/`，中断后重新运行会从未完成批次继续。

如果已经有 PaddleOCR HTTP 响应，可以直接导入：

```bash
python scripts/parse_regulation_document.py \
  --input doc/test.pdf \
  --response-json paddleocr_response.json \
  --output-dir result_input_processing/test
```

### 6.2 阶段二

```bash
python scripts/extract_regulation_rules.py \
  --parsed-dir result_input_processing/gjb8114-2013 \
  --category gjb8114


/root/anaconda3/envs/code_check/bin/python scripts/extract_regulation_rules.py --parsed-dir result_input_processing/gjb8114-2013 --category gjb8114 2>&1 | tee result_input_processing/gjb8114-2013/phase2.log
```

每个 chunk 完成后保存检查点。重新运行时跳过已经完成的 chunk，使用 `--force` 可重新抽取。

### 6.3 阶段三

运行：

```bash
python scripts/generate_rule_tests.py \
  --rules result_input_processing/gjb8114-2013/autochecker_rules.json \
  --output-dir experiment/gjb8114/cpp/test_cases \
  --output-rules experiment/gjb8114/cpp/gjb8114_rules_with_tests.json \
  --language cpp \
  --negative-count 10 \
  --positive-count 10 \
  --batch-size 4 \
  --max-repair-attempts 3



/root/anaconda3/envs/code_check/bin/python scripts/generate_rule_tests.py --rules result_input_processing/gjb8114-2013/autochecker_rules.json --output-dir experiment/gjb8114-all/test_cases --output-rules experiment/gjb8114-all/gjb8114_rules_with_tests.json --language cpp --negative-count 10 --positive-count 10 --batch-size 10 --workers 4 --llm-concurrency 4 --llm-timeout 600 --max-repair-attempts 3 2>&1 | tee result_input_processing/gjb8114-2013/phase3_concurrent.log
```

## 7. 阶段边界

- 阶段一只负责转换和解析文档；
- 阶段二只负责抽取规则、判断规则类型和整理原文示例；
- 阶段三只负责生成并校验测试代码；
- 后续 checker 生成阶段读取阶段三结果，生成 Clang-Tidy、CodeQL、Semgrep 等 checker，并运行测试计算准确率。
