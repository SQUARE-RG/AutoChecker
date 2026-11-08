# GJB 8114 规则、测试用例与 Checker 生成结果

## 输入文件

| 项目 | 数量或路径 |
| --- | --- |
| PDF | `doc/GJB-8114-2013.pdf` |
| PDF 页数 | 157 |
| 解析块数 | 1,476 |
| Markdown | `result_input_processing/gjb8114-2013/document.md` |

## 三阶段处理结果

| 阶段 | 输入 | 结果 |
| --- | --- | --- |
| 第一阶段：PDF 解析 | 157 页 PDF | 1,476 个内容块，生成 `document.md` |
| 第二阶段：规则抽取 | 7 个 Markdown 分块 | 抽取 290 个候选项，合并去重后得到 204 条规则 |
| 第三阶段：测试生成 | 204 条规则 | 191 条成功生成完整测试套件，13 条失败 |

第三阶段生成并验证的测试用例：

| 类型 | 数量 |
| --- | ---: |
| 负例 | 1,910 |
| 正例 | 1,910 |
| 合计 | 3,820 |

每条成功规则包含 10 个负例和 10 个正例，均为单文件 C++ 测试。

13 条未生成完整测试套件的规则包括：

| 原因 | 规则数 |
| --- | ---: |
| 真实负例无法通过 C++17 基础编译 | 8 |
| 依赖多文件或项目级上下文 | 4 |
| 测试用例生成未完成 | 1 |

`test_cases` 目录中实际存在 3,834 个 `.cpp` 文件，其中 3,820 个属于191条完整测试套件；其余14个是失败规则 `default-catch-after-specific-catches` 留下的10个正例和 `.staging` 中的4个临时负例，不计入有效测试集。

## Clang-Tidy 规则筛选

191 条具有完整测试套件的规则按实现能力分为：

| 分类文件 | 规则数 | 用途 |
| --- | ---: | --- |
| `clang_tidy_ast_supported_rules.json` | 141 | 进入当前 AST 驱动的 Clang-Tidy Checker 生成流程 |
| `clang_tidy_preprocessor_rules.json` | 15 | 需要 PPCallbacks、Lexer 或源码文本分析 |
| `clang_tidy_review_rules.json` | 7 | 需要进一步人工评估 |
| `dataflow_rules.json` | 28 | 需要数据流、路径状态或跨过程分析 |
| 合计 | 191 |  |

本次实际选择141条 AST 规则生成 Clang-Tidy Checker。

## Clang-Tidy Checker 生成结果

结果目录：`result_generation/clang-tidy/gjb8114_security_rules`

| 项目 | 数量 |
| --- | ---: |
| 输入规则 | 141 |
| 已处理规则 | 141 |
| 生成 Checker 源码 | 137 |
| 生成失败 | 4 |
| 成功率 | 97.16% |
| `.cpp`/`.h` 完整源码对 | 137 |

137 个已生成 Checker 的测试结果：

| 测试结果 | Checker 数量 |
| --- | ---: |
| 20/20 | 136 |
| 19/20 | 1 |
| 通过用例合计 | 2,739/2,740 |

未完全通过20个测试的规则：

| 规则 | 结果 | 未通过用例 |
| --- | --- | --- |
| `cautious-pointer-nonpointer-conversion` | 19/20 | `negative_09.cpp` |

4条生成失败的规则：

| 规则 | 失败阶段 | 原因 |
| --- | --- | --- |
| `function-decl-match-prototype` | `generate_checker` | 模型接口返回不完整响应 |
| `file-statements-max-2000` | `generate_checker` | 模型服务过载 |
| `cautious-use-of-register-variables` | `generate_checker` | 未生成有效 Checker |
| `place-const-at-outermost-except-const-pointer` | `generate_checker` | 模型接口返回不完整响应 |

## 137个成功Checker的生成与测试指标

逐规则数据见 `doc/bestPractice/GJB8114-checker-metrics.xlsx`。统计范围仅包含137条 `issuccess=True` 的Checker。

| 指标 | 合计 | 平均每个Checker |
| --- | ---: | ---: |
| LLM调用次数 | 780 | 5.693431 |
| 生成时间（秒） | 129,660.94 | 946.430219 |
| 生成时间（分钟） | 2,161.015667 | 15.773837 |
| 成本（元） | 90.614697 | 0.661421 |
| TP | 1,369 | 9.992701 |
| TN | 1,370 | 10.000000 |
| FP | 0 | 0.000000 |
| FN | 1 | 0.007299 |

测试指标定义：负例被Checker报告为TP，负例未被报告为FN，正例未被报告为TN，正例被报告为FP。

| 汇总检测指标 | 数值 |
| --- | ---: |
| Precision | 100.0000% |
| Recall | 99.9270% |
| Accuracy | 99.9635% |
| F1 | 99.9635% |

## 核对文件

- `result_input_processing/gjb8114-2013/manifest.json`
- `result_input_processing/gjb8114-2013/candidates.json`
- `result_input_processing/gjb8114-2013/autochecker_rules.json`
- `experiment/gjb8114-all/test_cases/generation_report.json`
- `experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json`
- `experiment/gjb8114-all/clang_tidy_ast_supported_rules.json`
- `result_generation/clang-tidy/gjb8114_security_rules/checker_generation_result.json`
- `doc/bestPractice/GJB8114-checker-metrics.xlsx`
