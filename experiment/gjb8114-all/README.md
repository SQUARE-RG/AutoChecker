# GJB 8114 规则与测试数据说明

本目录保存《GJB 8114—2013 C/C++ 语言编程安全子集》从结构化规则、测试套件到 Checker 生成输入的阶段性产物。不同 JSON 的筛选标准和用途不同，不能仅根据文件名中的 `supported` 判断其一定能由当前 AutoChecker 正确实现。

## 数据处理关系

```text
gjb8114_rules_with_tests.json
        │  结构完整性筛选
        ▼
gjb8114_clang_tidy_supported_rules.json
        │  按分析能力分类
        ├── clang_tidy_ast_supported_rules.json
        ├── clang_tidy_preprocessor_rules.json
        ├── clang_tidy_review_rules.json
        └── dataflow_rules.json
```

## JSON 文件说明

### `gjb8114_rules_with_tests.json`

第三阶段 `generate_rule_tests.py` 的完整输出，共包含 204 条规则。

- 成功规则带有 `rule_test_path`、`negative_case_amount` 和 `positive_case_amount`。
- 失败或当前测试模型不支持的规则仍保留在文件中，但 `rule_test_path` 为空。
- 该文件用于保留完整规则集合，不应直接作为 `src/main.py` 的输入。

对应测试文件位于 `test_cases/<main_title>/`，测试生成明细位于 `test_cases/generation_report.json`。

### `gjb8114_clang_tidy_supported_rules.json`

由 `scripts/filter_clang_tidy_rules.py` 生成，共包含 191 条规则。

这里的 `supported` 只表示规则满足 Checker 生成入口的结构要求：

- 测试目录存在；
- 每条规则包含 10 个负例和 10 个正例；
- 测试文件均为顶层单文件 `.cpp`；
- 必需字段和命名合法；
- 已补充 `category` 字段。

它不表示所有规则都能用 AST Matcher 完整实现。该文件是后续能力分类的输入，不建议直接批量生成全部 Checker。

结构筛选和质量告警记录在 `gjb8114_clang_tidy_filter_report.json`。

### `clang_tidy_ast_supported_rules.json`

包含 141 条适合当前 AutoChecker AST 驱动生成路径的规则，主要是：

- 声明、类型和作用域约束；
- 表达式和语句结构约束；
- 类、继承、构造函数和类型转换约束；
- 能在单个翻译单元内通过 AST 与局部语义信息判断的规则。

这是当前阶段推荐传给 `src/main.py --platform clang-tidy` 的批量输入文件。测试通过仍只代表覆盖现有测试集，生成后需要审查 Checker 的泛化能力。

### `clang_tidy_preprocessor_rules.json`

包含 15 条依赖源码文本、注释、宏或头文件信息的规则，例如宏定义、`#include`、注释内容和八进制标注。

这类规则原则上可以作为 Clang-Tidy Checker 实现，但通常需要 `PPCallbacks`、`Preprocessor`、`SourceManager` 或 `Lexer`，不能只依赖普通 AST Matcher。当前 AutoChecker 没有专门的预处理器生成模板，因此暂不与 AST 规则一起批量执行。

### `clang_tidy_review_rules.json`

包含 7 条边界规则，需要整翻译单元扫描、有限控制流、引用使用分析或更精确的语义定义。

这些规则并非确定不可由 Clang-Tidy 实现，但在批量生成前应逐条试跑并人工检查生成源码、诊断位置以及正负例覆盖情况。

### `dataflow_rules.json`

包含 28 条依赖数据流、路径状态、资源生命周期、指针别名、数值范围、调用图或项目级语义的规则，例如越界、释放后使用、资源泄漏和间接递归。

现有 AutoChecker 的 Clang-Tidy 路径主要生成 `registerMatchers()` 与 `check()`，没有完整的数据流和路径敏感分析能力。这些规则不应直接进入当前 AST Checker 批量生成，建议使用：

- Clang Static Analyzer；
- CodeQL；
- 基于 Clang CFG/Dataflow Framework 的专用 Checker；
- 人工实现的状态机或跨过程分析。

## 生成与更新命令

从第三阶段产物筛选结构完整的规则：

```bash
python scripts/filter_clang_tidy_rules.py
```

按实现能力拆分 191 条候选规则：

```bash
python scripts/classify_clang_tidy_rules.py
```

推荐首先对 AST 规则进行小规模试跑，确认环境和生成质量后再断点批量执行：

```bash
python src/main.py \
  --platform clang-tidy \
  --rules experiment/gjb8114-all/clang_tidy_ast_supported_rules.json \
  --resume
```

不要同时启动多个 `src/main.py` 进程。各规则共享同一个 LLVM 源码树和构建目录，并发添加或删除 Checker 会破坏构建状态。

## 维护约定

- 测试用例或规则发生变化后，先重新运行结构筛选，再运行能力分类。
- 能力分类依据规则的完整语义，而不是当前测试是否容易通过。
- 如果后续为 AutoChecker 增加 PPCallbacks、CFG 或数据流生成能力，应重新评估相应分组，而不是直接移动文件或复制规则。
- 四个能力文件必须互斥，且合计数量必须等于 `gjb8114_clang_tidy_supported_rules.json` 的规则数。

python src/main.py 
  --platform clang-tidy 
  --rules experiment/gjb8114-all/clang_tidy_ast_supported_rules.json 
  --resume 
  2>&1 | tee result_input_processing/gjb8114-2013/phase4.log
