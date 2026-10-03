# AutoChecker 输入处理模块设计

## 1. 目标

输入 PDF、Word、图片或纯文本规范文档，输出 AutoChecker 可消费的规则 JSON。

本模块只负责：

- 解析文档内容和结构；
- 找出文档中的全部规范；
- 生成每条规范的统一描述；
- 保留规则对应的原文和页码；
- 合并重复规则并保留来源追踪信息。

本阶段不生成测试用例和 checker。

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
       4. 大模型逐块分类并抽取规则
                    │
          5. 全局合并、去重、对账
                    │
          6. 导出 AutoChecker JSON
```

模块对外表现为一次文档上传，以上步骤由后台自动完成。

实现上拆成两个可独立运行的阶段。两个阶段通过落盘产物连接，避免每次调整提示词或重新抽取规则时重复运行耗时的 PaddleOCR：

```text
阶段一：文档解析
原始文档 -> PaddleOCR/文本解析 -> manifest.json + document.md + blocks.json

阶段二：规则抽取
阶段一目录 -> 分块 -> 大模型单次分类与抽取 -> AutoChecker JSON
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
- 标题、正文、表格、列表、页眉页脚等元素类型；
- 每个元素的页码、坐标和 OCR 置信度；
- 页面图片。

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

### 3.3 文档分块

当前实现以完整页面为最小单位，按照 token 上限连续装入页面。

分块要求：

- chunk 保留原始页码和 block ID；
- 相邻 chunk 默认重叠 1 页，避免跨页规则被截断；
- 默认上限为 12000 tokens，可通过命令行调整；
- 不从页面中间切分；单页超过上限时，该页独立成为一个 chunk；
- 表格不能从行中间切开。

示例：

```text
chunk-001：第 1～12 页
chunk-002：第 11～22 页
chunk-003：第 21～32 页
```

### 3.4 逐块分类并抽取规则

每个 chunk 独立调用大模型一次。模型在同一次响应中判断 chunk 是否包含规范，并抽取其中的规则；模型不负责跨文档去重。

`chunk_type` 取值：

- `normative`：主要内容为规范；
- `mixed`：规范与说明、示例或图表混合；
- `non_normative`：目录、封面、普通说明或无关图表，不包含规范。

抽取范围包括：

- 必须、禁止、不得等强制规则；
- 应、建议、推荐、谨慎使用等建议规则；
- 带显式规则编号的规则；
- 没有编号但包含独立约束的规则；
- 表格中的规则。

抽取原则：

- 显式规则编号是规则边界的最高优先级，一个编号输出一条规则；
- 同一编号的句子包含多个条件时不拆分，在一条 description 中完整保留；
- 没有规则编号的段落包含多个独立约束时才拆分；
- 多段共同描述一条约束时合并；
- 说明、原因和示例不能单独作为规则；
- 不补充原文没有表达的条件和例外；
- 每条规则必须引用 source block 和页码。

模型输出使用固定 JSON Schema：

```json
{
  "chunk_type": "normative",
  "reason": "包含具有明确编号和约束性用语的编程规范",
  "confidence": 0.98,
  "rules": [
    {
      "source_rule_id": "R-1-3-8",
      "main_title": "check-dynamic-allocation-before-use",
      "description": "动态分配得到的指针在使用前必须进行有效性检查。",
      "level": "required",
      "languages": ["c", "cpp"],
      "source_pages": [31, 32],
      "source_block_ids": ["page-31-block-7", "page-31-block-8"],
      "source_text": "动态分配的指针变量必须经过有效性检查后方可使用。"
    }
  ]
}
```

不包含规范时返回 `non_normative` 和空的 `rules`。分类理由和置信度写入 `chunk_extractions.json`，用于审计被跳过的内容。

### 3.5 全局合并和去重

所有 chunk 处理完成后合并候选规则。

去重优先级：

1. `source_rule_id` 相同；
2. `source_block_ids` 或来源页重叠；
3. `source_text` 相同或高度相似；
4. 语义相同且来源相邻。

只允许合并相同约束。语义相关但约束条件、强制等级或适用范围不同的规则必须保留为独立规则。

跨页重复规则合并时，合并所有来源页和 source block。

### 3.6 规则索引对账

如果文档包含“规则汇总”“准则索引”等表格，单独抽取索引中的规则 ID 和短描述，形成 inventory。

执行：

```text
inventory 中的规则 - 正文抽取结果 = 疑似遗漏
正文抽取结果 - inventory 中的规则 = 无编号规则或疑似误抽取
```

没有规则索引的文档跳过该步骤。

### 3.7 低置信度处理

以下情况标记为 `needs_review`：

- PaddleOCR 置信度低；
- 规则编号格式异常；
- 句子明显不完整；
- 表格列错位；
- 两条规则疑似粘连；
- 正文和规则索引不一致；
- 模型无法确定规则边界。

低置信度规则可以将对应页面截图交给多模态模型复核。正常规则不调用视觉模型。

## 4. 内部规则数据结构

模块内部保存完整来源信息：

```json
{
  "rule_uid": "gjb8114:R-1-3-8",
  "source_rule_id": "R-1-3-8",
  "main_title": "check-dynamic-allocation-before-use",
  "description": "动态分配得到的指针在使用前必须进行有效性检查。",
  "level": "required",
  "languages": ["c", "cpp"],
  "category": "gjb8114",
  "source": {
    "document_sha256": "...",
    "pages": [31, 32],
    "block_ids": ["page-31-block-7", "page-31-block-8"],
    "chunks": ["chunk-0004"],
    "original_text": "..."
  },
  "confidence": 0.94,
  "review_status": "auto_approved"
}
```

`rule_uid` 是内部稳定主键。`main_title` 首次确认后冻结，避免重复处理时名称变化。

## 5. AutoChecker 输出

通过 exporter 转换成现有格式：

```json
{
  "data": {
    "gjb8114": [
      {
        "title": "GJB 8114 R-1-3-8",
        "main_title": "check-dynamic-allocation-before-use",
        "description": "...",
        "category": "gjb8114",
        "rule_test_path": "",
        "negative_case_amount": 0,
        "positive_case_amount": 0,
        "issuccess": "",
        "performance": "",
        "rule_id": "R-1-3-8",
        "source_chunks": ["chunk-0004"],
        "source_pages": [31, 32],
        "source_block_ids": ["page-31-block-7", "page-31-block-8"],
        "review_status": "auto_approved"
      }
    ]
  }
}
```

测试尚未生成，因此 `rule_test_path` 为空，测试数量为 0。

## 6. 模块目录

```text
src/input_processing/
├── document_parser.py    # 阶段一总入口与PDF分批断点
├── converter.py          # Word等格式转换
├── paddle_parser.py      # 调用PP-StructureV3并标准化响应
├── text_parser.py        # TXT/Markdown/HTML解析
├── chunker.py            # 分块和重叠分页
├── prompts.py            # 规则抽取提示词
├── llm_client.py         # OpenAI兼容模型接口
├── rule_extractor.py     # 单次分类抽取和chunk断点
├── rule_merger.py        # 合并和去重
├── inventory_checker.py  # 规则索引对账
├── exporter.py           # AutoChecker JSON输出
├── rule_pipeline.py      # 阶段二总入口
├── io_utils.py           # 原子化文件读写
└── schemas.py            # DocumentBlock和Rule模型
```

输出目录：

```text
result_input_processing/<document_id>/
├── source/
├── converted/
├── paddleocr/
│   └── raw_response.json
├── manifest.json
├── document.md
├── blocks.json
├── chunks/
├── extractions/
├── chunk_extractions.json
├── candidates.json
├── rules.json
├── review_queue.json
├── reconciliation_report.json
└── autochecker_rules.json
```

## 7. 当前 CPU 服务器部署判断

当前服务器资源：

- Ubuntu 22.04 x86_64；
- 56 个逻辑 CPU，Intel Xeon E5-2680 v4，支持 AVX2；
- 内存 220 GiB，可用约 177 GiB；
- 可用磁盘约 2.7 TiB；
- 当前环境未检测到 NVIDIA GPU。

结论：该服务器能够部署并运行 PaddleOCR PP-StructureV3 CPU 版本，CPU、内存和磁盘都满足批量规范文档解析需求。没有 GPU 不影响功能，只会降低 OCR 和版面模型的处理速度；本模块属于离线文档处理场景，可以先使用 CPU 版本。

部署时应使用独立 Python 3.10 或 3.11 环境，不使用当前默认的 Python 3.14，也不把 PaddleOCR 依赖直接安装到 AutoChecker 主环境中。建议将 PaddleOCR 封装为独立进程或 HTTP 服务，AutoChecker 通过文件路径或接口调用。

具体安装和服务化步骤见 [PaddleOCR PP-StructureV3 CPU 服务部署手册](./paddleocr_service_deployment_cn.md)。

首期采用单实例、有限并发运行。实际并发数在上线前通过典型 PDF 压测确定，避免多个版面模型进程同时占用过多内存。

## 8. 第一版实现范围

第一版只实现：

1. PDF、DOCX、图片、TXT 输入；
2. DOCX 转 PDF；
3. PaddleOCR 输出 Markdown 和 JSON；
4. 按 token 上限和重叠页面分块；
5. 大模型逐块单次分类与抽取；
6. 全局合并去重；
7. 有规则索引时进行对账；
8. 导出 AutoChecker JSON。

第一版不实现测试生成、向量数据库、复杂检索系统和分布式部署。

## 9. 当前实现和运行方式

### 9.1 阶段一：解析文档

确保 PaddleOCR 服务已经监听 `127.0.0.1:18080`，然后运行：

在 AutoChecker 的 `code_check` 环境安装 PDF 分批依赖：

```bash
/root/anaconda3/envs/code_check/bin/python -m pip install pypdf
```

```bash
cd /root/code_check
/root/anaconda3/envs/code_check/bin/python scripts/parse_regulation_document.py \
  --input "regulations/GJB 8114-2013 C C++语言编程安全子集.pdf" \
  --output-dir result_input_processing/gjb8114
```

PDF 默认每 10 页调用一次 PaddleOCR，以低于服务端 30 页限制。每批响应立即保存在 `paddleocr/batches/`；OCR 中断后重跑同一命令会从未完成批次继续。

如果已经有 PaddleOCR HTTP 响应，可以直接导入，不再次执行 OCR：

```bash
/root/anaconda3/envs/code_check/bin/python scripts/parse_regulation_document.py \
  --input doc/test.pdf \
  --response-json paddleocr_response.json \
  --output-dir result_input_processing/test
```

阶段一主要输出：

```text
result_input_processing/<document_id>/
├── manifest.json
├── document.md
├── blocks.json
├── source/
└── paddleocr/raw_response.json
```

### 9.2 阶段二：抽取规则

大模型配置继续使用项目 `.env` 中的 `MODEL_NAME`、`DEEPSEEK_API_KEY` 和 `DEEPSEEK_BASE_URL`，也兼容 `LLM_API_KEY`、`LLM_BASE_URL`：

```bash
/root/anaconda3/envs/code_check/bin/python scripts/extract_regulation_rules.py \
  --parsed-dir result_input_processing/gjb8114 \
  --category gjb8114 \
  --title-prefix "GJB 8114" \
  --languages c,cpp
```

如果规则汇总表位于第 8～10 页，可增加：

```bash
--inventory-pages 8-10
```

每个 chunk 完成后都会在 `extractions/` 中写入检查点。命令中断后重新运行会跳过已经完成的 chunk；只有使用 `--force` 才会重新调用大模型。

默认每个 chunk 最大 12000 tokens、相邻 chunk 重叠 1 页。可以通过 `--max-chunk-tokens` 和 `--overlap-pages` 调整。每个 chunk 只进行一次分类与规则抽取；接口失败或返回非法 JSON 时仍会进行技术性重试。

阶段二主要输出：

```text
result_input_processing/<document_id>/
├── chunks/
├── extractions/
├── chunk_extractions.json
├── candidates.json
├── rules.json
├── review_queue.json
├── reconciliation_report.json
└── autochecker_rules.json
```
