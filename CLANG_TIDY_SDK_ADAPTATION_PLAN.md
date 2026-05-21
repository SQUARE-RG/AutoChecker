# Clang-Tidy 部分适配前端 SDK 修改计划

## 一、背景与目标

### 1.1 当前状态

项目已实现 clang-tidy 检查器的端到端自动生成，入口为 `src/main.py` 的 `main()` 函数：

- **输入**：从本地 JSON 文件读取规则（`clang_tidy_sub_checker/jgb8114_single_rules.json`），从磁盘加载 `.cpp` 测试用例
- **输出**：生成的 checker 代码保存到本地目录（`result-generation/`），日志写入文件
- **LLM 配置**：通过环境变量（`.env`）读取 API Key / Base URL

### 1.2 目标

对接前端提供的 SDK（`src/entity/client.py` + `src/entity/types.py`），使生成过程能**实时在网页展示**：

- **输入**：从 stdin 读取 `GeneratorInput`（包含规则描述、测试用例代码、LLM 配置）
- **输出**：通过 stdout 实时发送日志、进度、生成的代码产物、测试结果、最终状态
- **兼容性**：原有的本地文件运行模式不受影响，新增一个 SDK 模式入口

### 1.3 冗余原则

SDK 类型（`src/entity/types.py` 中的 `TestCaseData`、`CheckerFile`、`TestCaseResult` 等）仅用于 **I/O 通信层**。原有的实体类（`Case_Clang_Tidy`、`Checker_Clang_Tidy`、`Rule_Clang_Tidy`、`AbstractCase`、`AbstractChecker`、`AbstractRule`）**保持不变**，内部生成逻辑继续使用原有实体类。两者之间通过适配器/转换函数桥接。

---

## 二、需要修改的文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/main.py` | **修改** | 新增 `main_sdk()` 入口；原 `main()` 保留 |
| `src/generator.py` | **修改** | `Clang_tidy_CheckerGenerator` 增加 SDK 回调支持 |
| `src/llm_interface/llm_provider.py` | **修改** | 支持动态传入 LLM 配置（不从 env 读） |
| `src/plateform/clang_tidy.py` | **修改** | 新增测试用例临时文件写入函数 |
| `src/help/clang_tidy_utils.py` | **修改** | 新增适配器转换函数 |
| `src/entity/concreteProduct_Clang_Tidy.py` | **不改** | 保留原样 |
| `src/entity/abstractProduct.py` | **不改** | 保留原样 |
| `src/entity/factory.py` | **不改** | 保留原样 |
| `src/entity/client.py` | **不改** | SDK 文件，保留原样 |
| `src/entity/types.py` | **不改** | SDK 文件，保留原样 |
| `src/client.py` | **不改** | 保留原样（与 entity/client.py 内容相同） |
| `src/types.py` | **不改** | 保留原样（与 entity/types.py 内容相同） |
| `src/retriever/*.py` | **不改** | 检索层无需改动 |

---

## 三、详细修改设计

### 3.1 LLM 接口层 — 支持动态配置

**文件**：`src/llm_interface/llm_provider.py`

**问题**：当前 `get_llm_client()` 硬编码从 `os.getenv()` 读取配置，模块加载时就创建了全局 `llm_client`。SDK 模式下，API Key / Base URL / Model 由前端传入，各不相同。

**修改方案**：

```python
# 新增：支持参数化创建 client 的函数
def get_llm_client_from_config(api_key: str, base_url: str, model_name: str = "deepseek-chat"):
    """根据传入的配置创建 LLM client，用于 SDK 模式"""
    client = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7
    )
    return client

# 保留原有函数不变，供本地文件模式使用
def get_llm_client():
    ...  # 原有代码不动
```

**影响**：`Clang_tidy_CheckerGenerator` 和 `llm_invoke` 需要能使用动态传入的 client，而非模块级全局 `llm_client`。

**进一步修改**：在 `generator.py` 中，`Clang_tidy_CheckerGenerator.__init__` 接受一个可选的 `llm_client` 参数：

```python
class Clang_tidy_CheckerGenerator:
    def __init__(self, rule, all_Test_Case_List=None, 
                 skipped_Test_Cases=None, rule_result_dir="",
                 llm_client=None):  # 新增参数
        ...
        self.llm_client = llm_client  # 如果为 None，则回退到全局 llm_client
```

所有调用 `llm_invoke(llm_client, ...)` 的地方改为 `llm_invoke(self.llm_client or llm_client, ...)`。

---

### 3.2 入口层 — 新增 SDK 模式入口

**文件**：`src/main.py`

**修改方案**：新增 `main_sdk()` 函数，保留原有 `main()` 不变。

```python
def main_sdk():
    """SDK 模式入口：从 stdin 读取 GeneratorInput，通过 stdout 发送进度/结果"""
    # 1. 初始化 logger（写文件 + 通过 client.log 发送到前端）
    init_logger()
    
    # 2. 通过 SDK client 读取输入
    sdk_input = autoCheckerClient.get_input()
    
    # 3. 从 SDK 输入中提取配置
    rule_name = sdk_input.rule_name
    rule_description = sdk_input.rule_description
    language = sdk_input.language
    framework = sdk_input.framework
    llm_api_key = sdk_input.api_key
    llm_base_url = sdk_input.base_url
    llm_model_name = sdk_input.model_name
    
    # 4. 创建 LLM client
    sdk_llm_client = get_llm_client_from_config(
        api_key=llm_api_key,
        base_url=llm_base_url,
        model_name=llm_model_name
    )
    
    # 5. 将 SDK 的 TestCaseData 转换为内部 Case_Clang_Tidy 实体
    rule, case_list = adapt_sdk_input_to_entities(
        rule_name, rule_description, sdk_input.test_cases
    )
    
    # 6. 后续流程与原有 main() 类似，但：
    #    - 使用 sdk_llm_client
    #    - 在每个关键阶段调用 autoCheckerClient 发送进度/产物
    #    - 测试用例已有代码内容，但需写入临时目录供 clang-tidy 运行
    
    # 7. 最终结果通过 send_artifact + send_status 发送
```

**关键差异**（SDK 模式 vs 本地文件模式）：

| 方面 | 本地文件模式 `main()` | SDK 模式 `main_sdk()` |
|------|----------------------|----------------------|
| 输入来源 | 本地 JSON 文件 | stdin → `GeneratorInput` |
| 测试用例 | 从磁盘 `.cpp` 文件读取 | `TestCaseData.code` 字符串，需写入临时文件 |
| LLM 配置 | 环境变量 | `GeneratorInput` 中的字段 |
| 输出方式 | 本地文件 + logger | stdout JSON 行协议（`client.log/report_progress/send_artifact/send_status`） |
| 规则范围 | 批量处理多条规则 | 单次处理一条规则（一个 `GeneratorInput`） |

---

### 3.3 测试用例适配器

**文件**：`src/help/clang_tidy_utils.py`（新增函数）

**问题**：SDK 的 `TestCaseData` 包含 `file_name`、`code`、`compliant` 三个字段。内部流程需要：
1. `Case_Clang_Tidy` 实体（包含 `case_code`、`case_path`、`case_flag`）
2. clang-tidy / clang 命令需要实际存在的 `.cpp` 文件路径

**新增函数**：

```python
def adapt_sdk_test_cases(test_cases: list, temp_dir: str) -> list:
    """
    将 SDK 的 TestCaseData 列表转换为内部 Case_Clang_Tidy 列表。
    
    - 将 code 写入 temp_dir 下的临时 .cpp 文件
    - compliant=True → 正例（flag=True，不含 CHECK-MESSAGES，不应报警）
    - compliant=False → 负例（flag=False，含 CHECK-MESSAGES，应报警）
    
    返回: List[Case_Clang_Tidy]
    """
    case_list = []
    os.makedirs(temp_dir, exist_ok=True)
    for tc in test_cases:
        file_path = os.path.join(temp_dir, tc.file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tc.code)
        
        case = Case_Clang_Tidy(
            case_code=tc.code,
            case_description=f"Test case: {tc.file_name}",
            case_flag=tc.compliant,  # compliant=True 表示正例（不应报警）
            case_path=file_path
        )
        case_list.append(case)
    return case_list


def adapt_sdk_input_to_entities(rule_name: str, rule_description: str, 
                                 test_cases: list) -> tuple:
    """
    从 SDK 输入创建内部实体：Rule_Clang_Tidy + List[Case_Clang_Tidy]
    """
    rule = Rule_Clang_Tidy(
        rule_name=rule_name,
        rule_description=rule_description,
        rule_test_path="",  # SDK 模式没有固定的测试路径
        rule_category="ucassaat"
    )
    
    # 使用临时目录存放测试用例文件
    temp_test_dir = config['checker']['temp_test_dir'] + f"sdk_{rule_name}/"
    case_list = adapt_sdk_test_cases(test_cases, temp_test_dir)
    
    return rule, case_list
```

**注意事项**：
- `TestCaseData.compliant` 的语义需与内部 `case_flag` 对齐。当前逻辑是 `flag=True` 为正例（符合规则，不应报警），`flag=False` 为负例（违反规则，应报警）。SDK 的 `compliant` 应该直接映射到 `flag`。
- 临时文件在 checker 生成完成后需要清理。

---

### 3.4 生成器增强 — SDK 回调

**文件**：`src/generator.py`

**修改点**：

1. **构造函数增加参数**：

```python
class Clang_tidy_CheckerGenerator:
    def __init__(self, rule, all_Test_Case_List=None,
                 skipped_Test_Cases=None, rule_result_dir="",
                 llm_client=None,           # 新增：SDK 模式下的 LLM client
                 sdk_client=None):          # 新增：SDK 的 AutoCheckerClient 实例
        ...
        self.llm_client = llm_client
        self.sdk_client = sdk_client
```

2. **关键节点增加 `send_artifact` 调用**：

| 节点位置 | 发送内容 |
|---------|---------|
| 初始 checker 生成成功时 | `files=[CheckerFile("checker.cpp", cpp_code), CheckerFile("checker.h", h_code)]`, `test_results=初始测试结果` |
| 每次增强迭代后 | 更新后的 checker 文件 + 最新的测试结果 |
| 编译修复成功后 | 修复后的 checker 代码 |
| 最终完成时 | 最终 checker + 全部测试结果 |

3. **辅助方法**：

```python
def _build_test_results(self, success_cases, failed_cases, all_cases):
    """将内部 case 列表转换为 SDK TestCaseResult 列表"""
    results = []
    success_paths = {c.get_case_path() for c in success_cases}
    failed_paths = {c.get_case_path() for c in failed_cases}
    for case in all_cases:
        file_name = os.path.basename(case.get_case_path())
        if case in success_cases:
            status = TestCaseStatus.PASSED
        elif case in failed_cases:
            status = TestCaseStatus.FAILED
        else:
            status = TestCaseStatus.SKIPPED
        results.append(TestCaseResult(file_name=file_name, status=status))
    return results

def _send_checker_artifact(self, test_results, checker_logic="", api_knowledge=""):
    """发送当前的 checker 代码 + 测试结果到前端"""
    if self.sdk_client is None:
        return  # 非 SDK 模式，跳过
    
    cpp_code, h_code = get_checker_code(self.RULE.get_rule_name())
    files = [
        CheckerFile(file_name="checker.cpp", content=cpp_code),
        CheckerFile(file_name="checker.h", content=h_code),
    ]
    self.sdk_client.send_artifact(
        files=files,
        test_results=test_results,
        checker_logic=checker_logic,
        api_knowledge=api_knowledge,
    )
```

4. **所有 `llm_invoke(llm_client, ...)` 调用替换**为：
```python
llm_invoke(self.llm_client or llm_client, ...)
```

---

### 3.5 平台层 — 临时文件支持

**文件**：`src/plateform/clang_tidy.py`

**新增函数**：

```python
def setup_sdk_test_temp_dir(rule_name: str) -> str:
    """为 SDK 模式创建测试用例临时目录"""
    temp_dir = config['checker']['temp_test_dir'] + f"sdk_{rule_name}/"
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def cleanup_sdk_temp_dir(rule_name: str):
    """清理 SDK 模式的临时目录"""
    temp_dir = config['checker']['temp_test_dir'] + f"sdk_{rule_name}/"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
```

---

### 3.6 入口切换

**文件**：`src/main.py`

在文件末尾修改 `__main__` 块：

```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["local", "sdk"], default="local",
                        help="运行模式: local=本地文件模式, sdk=SDK stdin/stdout 模式")
    args = parser.parse_args()
    
    if args.mode == "sdk":
        main_sdk()
    else:
        main()
```

---

## 四、数据流对比

### 4.1 修改前（本地文件模式）

```
本地 JSON 规则文件 ──→ main() ──→ 磁盘 .cpp 文件
                         │
                    env var LLM 配置
                         │
                         ↓
                    generator.py ──→ 本地 result-generation/
                         │
                    logger → 日志文件
```

### 4.2 修改后（SDK 模式 / 本地文件模式共存）

```
SDK 模式:
stdin → AutoCheckerClient.get_input() → main_sdk() → generator.py
           ↑                              │               │
           │  GeneratorInput                │               ↓
           │  (rule, test_cases,            │         stdout JSON lines
           │   llm_config)                  │         → client.log()
           │                                │         → client.report_progress()
           └────────────────────────────────┘         → client.send_artifact()
                                                      → client.send_status()

本地文件模式 (保持不变):
JSON 文件 → main() → generator.py → 本地文件输出
```

---

## 五、实施步骤

建议按以下顺序实施，每步完成后可独立测试：

| 步骤 | 内容 | 涉及文件 | 预估工作量 |
|------|------|---------|-----------|
| 1 | LLM 接口层：新增 `get_llm_client_from_config()`，支持动态配置 | `llm_provider.py` | 小 |
| 2 | 实体适配器：新增 `adapt_sdk_test_cases()` 等转换函数 | `clang_tidy_utils.py` | 小 |
| 3 | 平台层：新增临时文件目录管理函数 | `clang_tidy.py` | 小 |
| 4 | 生成器增强：增加 `llm_client`/`sdk_client` 参数，增加 `send_artifact` 回调 | `generator.py` | 中 |
| 5 | 新增 SDK 入口 `main_sdk()` | `main.py` | 中 |
| 6 | 入口切换：`--mode` 参数 | `main.py` | 小 |
| 7 | 端到端集成测试 | 全部 | 中 |

---

## 六、风险与注意事项

1. **`TestCaseData.compliant` 语义对齐**：需与前端确认 `compliant=True` 的准确含义（是"该用例符合规则"=正例=不应报警，还是"该用例是合规的测试"）。当前假设 `compliant=True` = 正例（不应产生 warning）。

2. **规则分类（category）**：SDK 的 `GeneratorInput` 中没有 `category` 字段。当前 checker 模板生成依赖此字段确定 include 路径。SDK 模式下可默认使用 `"ucassaat"`。

3. **临时文件清理**：SDK 模式下测试用例写入临时目录，生成完成后需清理，避免磁盘堆积。

4. **编译依赖**：SDK 模式仍需依赖本地 LLVM/Clang 编译环境（CMake、clang-tidy 源码）。这不适合无编译环境的轻量部署。

5. **`send_artifact` 的 `checker_logic` / `api_knowledge` 字段**：这两个可选字段用于向前端展示 checker 的检测逻辑和使用的 API 知识。需要在生成流程中采集并传入。

6. **文件格式**：`src/entity/client.py` 和 `src/entity/types.py` 目前与 `src/` 下的同名文件内容完全相同。实施时需确认以哪个位置为准（建议以 `src/entity/` 为准，`src/client.py` 和 `src/types.py` 后续可删除或保留作向后兼容）。
