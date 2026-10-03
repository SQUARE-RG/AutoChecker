# 原生 CodeQL Quick Evaluation

独立 Python 库和可选 LangChain Tool，调用 `codeql execute query-server2` 的原生范围求值。
不启动 VS Code，不修改 query，不导入或接入 AutoQL 主生成流程，不把源码片段改写成临时 select。

当前验证环境：Linux、Python 3.11、CodeQL CLI 2.23.3、`codeql/java-all` 7.7.2。
协议参考官方 vscode-codeql 1.17.8；其他版本需要重新运行集成测试。

## Python

从项目根目录使用 `PYTHONPATH=src`，建议解释器为 `code_check_autoql` 环境。

```python
from autoql.quick_eval import (
    QuickEvalSession, SessionConfig, EvaluationRequest, SymbolTarget,
    SnippetTarget, RangeTarget, SourceRange,
)

with QuickEvalSession(SessionConfig(
    codeql_binary="codeql",
    artifact_dir="/tmp/my-quick-eval-session",  # 必须是新会话目录
    allowed_roots=["/path/to/query-pack"],
    databases={"buggy": "/path/to/database"},
)) as session:
    doc = session.register_query("/path/to/query-pack/candidate.ql")
    result = session.evaluate(EvaluationRequest(
        query_id=doc.query_id,
        expected_revision=doc.revision,
        database="buggy",
        target=SymbolTarget("Config::isSource", arity=1),
        sample_limit=8,
    ))
    print(result)
```

`evaluate` 返回普通 dict，成功状态为 `ok`；只有成功才有有效的 `row_count`。
多结果集的顶层行数为 null，分别读取 `result_sets` 中的数量。外部文件/配置注册错误会抛异常；
求值过程中的可预期错误返回结构化状态。失败不等于空结果。

三种目标：

```python
SymbolTarget("isTarget", arity=1)
SnippetTarget('n.asExpr() = cc.getArgument(1)')
RangeTarget(SourceRange(53, 5, 53, 39))  # 示例坐标，需与实际文件核对
```

行列从 1 开始，列使用 Python Unicode code points，结束位置不包含。
扩展的 TS 协议声明 UTF-16，但实测 CodeQL 2.23.3 使用 code point 列号。默认 auto 模式
对 2.23.3 使用已验证的 code point 适配，其余版本按协议使用 UTF-16（尚未验证）。
可通过 SessionConfig.position_encoding 显式指定 utf16/codepoint；实际编码写入每个 probe 的请求记录。
不会在失败后尝试其他选区。文本片段必须精确、唯一；重复则返回候选范围。
符号接口只定位普通声明，不解析泛型模块实例/别名等复杂名称；不支持时使用范围接口。
成员谓词用 `Class::method`，特征谓词用 `Class::Class`；`arity` 不包含 `this`/`result`。

`locate_targets(doc.query_id, doc.revision)` 返回可定位声明。目标 ID 是标识信息，
求值时用返回的限定名或 range；文件修改后重新 register，旧 revision 不能求值。

在 `.ql` 上下文中求值导入的 `.qll`：先 register 两个文件，以 `.ql` 的 query_id 发请求，
在 target 中指定 `.qll` 的 file_id 和 expected_revision。入口上下文影响抽象类等结果。

## 计数与分页

`mode="count"` 调用原生 countOnly。CLI 2.23.3 返回 Category/Count 表，库提取
`Total tuples` 为行数，并在 `count_details` 保留各列的 distinct counts，不把表本身的行数当元组数。
原生计数不保证更快。`sample_limit` 只限制输出，不限制求值规模。

```python
result_set = result["result_sets"][0]
page = session.read_results(result["artifact_id"], result_set["next_cursor"])
```

游标为会话内不透明标识，next_cursor 为 null 表示没有下一页；first_cursor 可重新读取首页。
BQRS offset 是后端字节偏移，调用者不应自行计算。历史结果绑定原始版本，分页不重新求值。
实体列保留后端 label/url；没有 URL 时不猜位置。大整数值用带类型的十进制字符串表示。

## Agent Tools

```python
from autoql.quick_eval.tools import create_quick_eval_tools

tools = create_quick_eval_tools(session)
# 将 tools 绑定到你的 agent；本模块不执行模型调用。
```

三个工具：`codeql_locate_targets`、`codeql_quick_evaluate`、`codeql_read_probe_results`。
调用者负责登记 query，并将 query_id/revision 和数据库别名交给 agent。
工具不提供文件写入、shell 或任意 RPC。核心库不依赖 LangChain，只有 tools 模块导入它。

默认摘要最多 16 KiB；截断时 output_truncated=true，完整摘要/BQRS 留在 artifact。
样本只能作为例子，不能因为样本缺失就断言某个实体不存在。一个局部片段不会自动继承全部外部过滤条件。
建议每次探针对应一个明确诊断假设，检查关联元组而不只看数量，最后仍运行完整查询。

## 进程、期限与制品

单会话长驻 Query Server，串行求值；并发调用返回 busy。启动时先注册数据库，重启后重新注册。
不自动升级/重建数据库，不重放失败请求。`session.cancel()` 可从另一线程请求取消，
超时取消无响应时终止自有进程组。context manager/close 回收进程。

默认单请求 120 秒、会话 600 秒、12 次求值、2 线程和 4096 MiB CodeQL RAM 配置。
取消清理最多额外消耗宽限期及进程终止时间。配置可显式增大，不能依赖 quick 一词推断耗时。

会话目录包含配置、CLI/依赖解析环境、数据库 metadata 哈希、stderr、逐 probe 请求、原生响应、
BQRS、summary 和 diagnostics。没有跨请求结果缓存；历史结果读取不代表当前版本结果。
已安装依赖包和数据库在会话期间必须保持不变。受管理 QL 根目录前后哈希用于检测改动，
不能代替调用方对并发修改的控制。allowed_roots 应尽量设为具体 query pack，而非整个仓库。

会话内可显式调用 `session.delete_probe(artifact_id)` 删除单个探针，随之使其分页游标失效。
关闭后可以由调用方删除其专有 artifact 目录；库不自动清除历史证据。

## 独立命令

```bash
PYTHONPATH=src python -m autoql.quick_eval \
  --config session-config.json --query /path/to/candidate.ql --locate

PYTHONPATH=src python -m autoql.quick_eval \
  --config another-session-config.json --query /path/to/candidate.ql --request request.json
```

配置 JSON 对应 SessionConfig；request JSON 包含 database、target（带 kind）及可选 mode/sample_limit/timeout_seconds。
每次命令创建新会话，需要不同 artifact_dir。输出包含 document 信息和求值结果，失败退出码为 1。

## 测试

```bash
PYTHONPATH=src conda run -n code_check_autoql \
  python -m unittest discover -s src/autoql/tests/quick_eval -v

QUICK_EVAL_INTEGRATION=1 PYTHONPATH=src conda run -n code_check_autoql \
  python -m unittest autoql.tests.quick_eval.test_integration -v

PYTHONPATH=src conda run --no-capture-output -n code_check_autoql \
  python -m autoql.tests.quick_eval.run_historical --output /tmp/quick-eval-history
```

集成测试创建自己的小型 Java database，需要可用 CLI、Java extractor 和已安装依赖。
历史回归使用设计文档整理的两份候选和原始 buggy/fixed 数据库，绝不替换数据库。
H04 全库二元关系不进入默认回归，以免产生大规模关系枚举。所有测试不需要 LLM/API 密钥。
