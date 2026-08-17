# Trace Viewer — Agent 运行可视化

把 `codeql_agent` 的 attempts 归档渲染成自包含 HTML 报告，用于调试：

- **检索内容完整展示**：每次 `search_docs` 返回的文档全文（折叠面板，点击展开）
- **完整对话时间线**：System / Human / Assistant / Tool 四种角色着色
- **工具调用与参数**：search_docs 的查询词、write_query_file 提交的代码
- **编译错误 / 用例结果 / 每轮 query 代码**

## 用法

```bash
cd /root/code_check

# 渲染某个规则的 attempts
python trace_viewer/render_trace.py \
  --attempts-dir result_generation/codeql/python/prevent-command-injection/attempts \
  --output trace_report.html
```

浏览器打开 `trace_report.html` 即可。

## 过滤器

- **全部**：完整时间线
- **只看检索**：只显示 search_docs 调用和返回的文档内容（调试检索质量）
- **只看错误/结果**：只显示编译错误和用例运行结果

## 目录结构

```
trace_viewer/
├── render_trace.py   # 渲染脚本（读 attempts → 输出单文件 HTML）
└── README.md
```

## 已知限制（待补）

- `meta.json` 暂无每 attempt 的 token/花费（usage 只在 run 结束汇总），
  后续可在 `nodes.call_model` 记录时带上 attempt_counter，归档时写入 meta
