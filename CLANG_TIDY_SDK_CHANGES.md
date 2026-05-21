# Clang-Tidy SDK 适配 — 修改前后对照文档

## 修改概览

| 文件 | 新增行 | 删除行 | 修改性质 |
|------|--------|--------|---------|
| `src/llm_interface/llm_provider.py` | +11 | 0 | 新增函数 |
| `src/help/clang_tidy_utils.py` | +51 | 0 | 新增函数 |
| `src/plateform/clang_tidy.py` | +38 | 0 | 新增函数 |
| `src/generator.py` | +105 | -28 | 增强现有类 |
| `src/main.py` | +121 | -2 | 新增入口 + 修复注释 |

---

## 一、`src/llm_interface/llm_provider.py`

### 修改前

LLM client 只能通过环境变量创建，模块加载时生成全局单例：

```python
def get_llm_client():
    model_name = os.getenv("MODEL_NAME", "deepseek")
    API_KEY = os.getenv("DEEPSEEK_API_KEY", ...)
    BASE_URL = os.getenv("DEEPSEEK_BASE_URL", ...)
    client = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, ...)
    return client

llm_client = get_llm_client()  # 全局单例，所有地方共用
```

### 修改后

新增 `get_llm_client_from_config()` 函数，支持从参数动态创建 LLM client。原有的 `get_llm_client()` 和全局 `llm_client` 保持不变，本地文件模式不受影响。

```python
# 【新增】SDK 模式：从参数创建
def get_llm_client_from_config(api_key: str, base_url: str, model_name: str = "deepseek-chat"):
    client = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=0.7)
    return client

# 【不变】本地模式：从 env 创建
def get_llm_client():
    ...

llm_client = get_llm_client()  # 全局单例，本地模式回退用
```

| 场景 | 使用函数 | API Key 来源 |
|------|---------|-------------|
| 本地文件模式 `main()` | `get_llm_client()` (模块级) | 环境变量 `.env` |
| SDK 模式 `main_sdk()` | `get_llm_client_from_config()` | 前端通过 stdin 传入 |

---

## 二、`src/help/clang_tidy_utils.py`

### 修改前

文件末尾为 `save_middle_check()` 函数，无 SDK 相关逻辑。

### 修改后

文件末尾新增两个适配器函数（原有所有函数不变）：

#### 2.1 `adapt_sdk_test_cases()`

| 项目 | 说明 |
|------|------|
| **输入** | `test_cases: list[TestCaseData]` + `temp_dir: str` |
| **输出** | `list[Case_Clang_Tidy]` |
| **职责** | ① 将 SDK 的 `TestCaseData` 转为内部实体 `Case_Clang_Tidy`；② 将 `code` 字符串写入临时 `.cpp` 文件（clang-tidy 需要物理文件路径） |

**字段映射关系：**

```
TestCaseData.file_name  ──→  Case_Clang_Tidy.case_path   (写入 temp_dir 后的路径)
TestCaseData.code       ──→  Case_Clang_Tidy.case_code
TestCaseData.compliant  ──→  Case_Clang_Tidy.case_flag   (True=正例, False=负例)
```

#### 2.2 `adapt_sdk_input_to_entities()`

| 项目 | 说明 |
|------|------|
| **输入** | `rule_name`, `rule_description`, `test_cases: list[TestCaseData]`, 可选的 `temp_test_dir` |
| **输出** | `(Rule_Clang_Tidy, list[Case_Clang_Tidy])` 元组 |
| **职责** | 一站式创建内部 rule 实体 + case 实体列表 |

SDK 的 `GeneratorInput` 中不含 `category` 字段，此函数固定使用 `"ucassaat"` 作为默认分类。

---

## 三、`src/plateform/clang_tidy.py`

### 修改前

仅提供 `run_Checker_with_Check_clang_tidy()` 函数，该函数调用 LLVM 的 `test_check_clang_tidy.py` 测试脚本，依赖测试用例中的 `CHECK-MESSAGES` 注释来验证预期 warning。

### 修改后

新增 3 个函数（原有所有函数不变）：

#### 3.1 `run_clang_tidy_directly()`

| 对比项 | `run_Checker_with_Check_clang_tidy` (原有) | `run_clang_tidy_directly` (新增) |
|--------|------------------------------------------|----------------------------------|
| 调用方式 | 通过 `test_check_clang_tidy.py` 脚本 | 直接调用 `clang-tidy` 二进制 |
| 依赖 CHECK-MESSAGES | **是**，脚本解析注释验证预期 | **否**，仅统计 warning 数量 |
| 适用场景 | 本地模式（标准 LLVM 测试用例） | SDK 模式（前端传入的纯代码） |
| 返回值 | `(full_output, warning_count)` | `(full_output, warning_count)` |

**为什么需要这个函数：** SDK 模式中，前端传入的测试用例是纯 C++ 代码字符串，不含 `CHECK-MESSAGES` 注释。若使用原有的 `run_Checker_with_Check_clang_tidy`，脚本会因找不到预期注释而返回非零退出码，从而误报为错误。

#### 3.2 `setup_sdk_test_temp_dir()` / `cleanup_sdk_temp_dir()`

SDK 模式测试用例临时目录的生命周期管理：

```
setup_sdk_test_temp_dir("my-rule")   →  /root/code_check/temp_test_dir/sdk_my-rule/
cleanup_sdk_temp_dir("my-rule")      →  删除上述目录
```

---

## 四、`src/generator.py`（变更最多的文件）

### 4.1 导入变更

```diff
-from plateform.clang_tidy import compiler_clang_tidy,run_Checker_with_Check_clang_tidy
+from plateform.clang_tidy import compiler_clang_tidy,run_Checker_with_Check_clang_tidy,run_clang_tidy_directly

-from types import LogLevel
+from types import LogLevel, CheckerFile, TestCaseResult, TestCaseStatus
```

### 4.2 构造函数新增参数

```diff
-def __init__(self, rule, all_Test_Case_List=None, skipped_Test_Cases=None, rule_result_dir=""):
+def __init__(self, rule, all_Test_Case_List=None, skipped_Test_Cases=None, rule_result_dir="",
+             llm_client=None, sdk_client=None):
```

| 新参数 | 类型 | 默认值 | 作用 |
|--------|------|--------|------|
| `llm_client` | `ChatOpenAI \| None` | `None` | SDK 模式下前端传入的 LLM client；`None` 则回退到模块级全局 `llm_client` |
| `sdk_client` | `AutoCheckerClient \| None` | `None` | SDK 通信 client；`None` 则仅写本地日志，不推送前端 |

**向后兼容：** 原有调用 `Clang_tidy_CheckerGenerator(rule, cases, skipped, dir)` 无需任何修改。

### 4.3 新增 `_llm_client` property

```python
@property
def _llm_client(self):
    return self.llm_client or llm_client  # 实例级优先，回退到模块级
```

所有 LLM 调用统一通过 `self._llm_client`，自动适配 SDK/本地模式：

```diff
- answer,cb = llm_invoke(llm_client, logic_query)
+ answer,cb = llm_invoke(self._llm_client, logic_query)
```

影响 6 处调用位置：
- `run_logic_for_negative_case()`
- `augmentation_logic_by_negative_case()`
- `augmentation_logic_by_positive_case()`
- `generate_checker_with_single_case()`
- `generate_checker_with_query()`
- `analyze_compiler_error()`

### 4.4 新增 `_validate_test_case()` 方法

统一测试验证入口，根据模式自动分发：

```
                    ┌── sdk_client 不为 None?
                    │
    _validate_test_case()
                    │
          ┌─────────┴─────────┐
          │ YES               │ NO (本地模式)
          ▼                   ▼
  run_clang_tidy_directly   run_Checker_with_Check_clang_tidy
  (不依赖 CHECK-MESSAGES)    (通过 test_check_clang_tidy.py)
```

替换了 3 处原有的硬编码调用：
- `first_checker_generation()` — 初始 checker 编译后验证
- `runAllTestCase()` — 全量测试用例验证
- `checker_augmentation()` — 增强阶段验证

### 4.5 新增 `_build_test_results()` 方法

将内部 `Case_Clang_Tidy` 列表转换为 SDK 的 `TestCaseResult` 列表：

```python
Case_Clang_Tidy  ──→  TestCaseResult
  case_path              file_name = os.path.basename(case_path)
  in success_cases?      status = PASSED | FAILED | SKIPPED
```

### 4.6 新增 `_send_checker_artifact()` 方法

SDK 模式下向前端推送当前 checker 代码和测试结果：

- **SDK 模式** (`sdk_client is not None`)：构造 `ArtifactMessage`，通过 stdout 发送
- **本地模式** (`sdk_client is None`)：直接 return，不执行任何操作

在 3 个关键节点触发：

| 触发位置 | 时机 | 内容 |
|---------|------|------|
| `first_checker_generation()` | 初始 checker 通过第一个负例验证后 | checker.cpp + checker.h + 单用例测试结果 |
| `checker_augmentation()` | 每个失败用例增强成功后 | checker.cpp + checker.h + 全量测试结果 |
| `checker_augmentation()` | 全部用例通过后（`all_success=True`） | 最终 checker + 全量测试结果 |

---

## 五、`src/main.py`

### 5.1 导入变更

```diff
-from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template
+from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template,setup_sdk_test_temp_dir,cleanup_sdk_temp_dir

-from help.clang_tidy_utils import get_camel_check_name
+from help.clang_tidy_utils import get_camel_check_name,adapt_sdk_input_to_entities

+from llm_interface.llm_provider import get_llm_client_from_config
```

### 5.2 错位注释修复

```diff
-            # print("负例")        # 此注释在正例分支中，属于错位
```

### 5.3 新增 `main_sdk()` 函数（核心变更）

SDK 模式的完整入口函数，与原有 `main()` 并行存在。流程对比如下：

| 阶段 | 本地模式 `main()` | SDK 模式 `main_sdk()` |
|------|------------------|----------------------|
| **输入** | 读取本地 JSON 文件（`clang_tidy_sub_checker/jgb8114_single_rules.json`） | stdin → `autoCheckerClient.get_input()` → `GeneratorInput` |
| **批量/单次** | 批量处理多条规则 | 单次处理一条规则 |
| **LLM 配置** | 环境变量 `.env` | `GeneratorInput.api_key / base_url / model_name` |
| **测试用例** | 从磁盘 `.cpp` 文件加载 | `GeneratorInput.test_cases` → 写入临时文件 |
| **进度上报** | 有限（仅 `log` + `report_progress`） | 全程：`log` + `report_progress` + `send_artifact` + `send_status` |
| **失败处理** | 记录日志后继续下一条规则 | `send_status(FAILED)` + `sys.exit(1)` |
| **清理** | `remove_Checker_Template` + 重新编译 | 上述 + `cleanup_sdk_temp_dir` |

`main_sdk()` 的 10 步骤：

```
① stdin 读取 GeneratorInput
② 框架检查（仅支持 clang-tidy）
③ 创建 SDK LLM client（get_llm_client_from_config）
④ 转换测试用例（adapt_sdk_input_to_entities → 写入临时文件）
⑤ 创建结果目录
⑥ 预编译 clang-tidy
⑦ 生成 Checker 模板
⑧ 创建 Clang_tidy_CheckerGenerator(llm_client=..., sdk_client=...)
    → generate_checker() → 内部自动推送 send_artifact
⑨ 处理结果：COMPLETED 或 FAILED
⑩ 清理模板 + 临时文件 + 重新编译
```

### 5.4 入口切换

```diff
 if __name__ == "__main__":
-    main()
+    import argparse
+    parser = argparse.ArgumentParser(...)
+    parser.add_argument("--mode", choices=["local", "sdk"], default="local")
+    args = parser.parse_args()
+    if args.mode == "sdk":
+        main_sdk()
+    else:
+        main()
```

**使用方式：**

```bash
# 本地文件模式（默认，行为不变）
python src/main.py
python src/main.py --mode local

# SDK 模式（从 stdin 读取，向 stdout 输出 JSON 行协议）
python src/main.py --mode sdk < input.json
```

---

## 六、未修改的文件

以下文件完全保持不变，与 SDK 无耦合：

| 文件 | 原因 |
|------|------|
| `src/entity/abstractProduct.py` | 抽象基类保持不变 |
| `src/entity/concreteProduct_Clang_Tidy.py` | 内部实体类保持不变，SDK 类型通过适配器转换 |
| `src/entity/factory.py` | 工厂类保持不变 |
| `src/entity/client.py` | SDK 文件，不修改 |
| `src/entity/types.py` | SDK 文件，不修改 |
| `src/entity/__init__.py` | 空文件，无需修改 |
| `src/retriever/*.py` | 检索层与 SDK 无关 |
| `src/prompt/clang_tidy_prompt/*` | Prompt 模板与 SDK 无关 |
| `src/config.py` / `src/global_config.py` | 配置层与 SDK 无关 |

---

## 七、数据流对比

### 修改前（仅本地文件模式）

```
┌─────────────────┐
│ JSON 规则文件    │──→ main()
│ .cpp 测试用例    │     │
│ .env LLM 配置   │     ↓
└─────────────────┘   generator.py ──→ 本地 result-generation/
                          │
                      logger ──→ 日志文件
```

### 修改后（两种模式共存）

```
本地模式 (--mode local)：
    JSON + .cpp + .env ──→ main() ──→ generator.py ──→ 本地文件（不变）

SDK 模式 (--mode sdk)：
    stdin ──→ GeneratorInput ──→ main_sdk()
                │                    │
                │  rule_name         ├── get_llm_client_from_config()
                │  rule_description  ├── adapt_sdk_input_to_entities()
                │  test_cases        ├── Clang_tidy_CheckerGenerator
                │  api_key           │    ├── llm_client (SDK)
                │  base_url          │    └── sdk_client (SDK)
                │  model_name        │         │
                └────────────────────┘         ↓
                                     stdout JSON 行协议
                                     ├── LogMessage
                                     ├── ProgressMessage
                                     ├── ArtifactMessage (checker + 测试结果)
                                     └── StatusMessage (completed/failed)
```
