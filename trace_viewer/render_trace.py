#!/usr/bin/env python3
"""把 agent 运行 trace（attempts/ 目录）渲染成自包含 HTML 报告。

重点可视化：
- 每次 search_docs 检索的完整内容（方便调试检索质量）
- 完整对话时间线（system/human/assistant/tool 角色着色）
- 每次 tool 调用的参数与结果
- 编译错误 / 用例结果 / 每轮 query 代码

用法:
    python trace_viewer/render_trace.py \
        --attempts-dir result_generation/codeql/python/prevent-command-injection/attempts \
        --output trace_report.html
"""

import argparse
import html
import json
import os
from datetime import datetime

# ── HTML/CSS/JS 模板 ──────────────────────────────────────

_CSS = """
body { font-family: -apple-system, 'Segoe UI', 'PingFang SC', sans-serif;
       margin: 0; background: #f5f6f8; color: #24292f; }
header { position: sticky; top: 0; background: #24292f; color: #fff;
         padding: 12px 24px; z-index: 10; }
header h1 { margin: 0 0 8px; font-size: 18px; }
.filters button { margin-right: 8px; padding: 4px 12px; border: 1px solid #57606a;
                  background: transparent; color: #fff; border-radius: 14px; cursor: pointer; }
.filters button.active { background: #0969da; border-color: #0969da; }
.wrap { max-width: 1100px; margin: 20px auto; padding: 0 16px; }
.attempt { background: #fff; border: 1px solid #d0d7de; border-radius: 8px;
           margin-bottom: 20px; overflow: hidden; }
.attempt-header { padding: 12px 16px; border-bottom: 1px solid #d0d7de;
                  background: #f6f8fa; display: flex; align-items: center; gap: 12px; }
.attempt-num { font-weight: 700; color: #0969da; font-size: 15px; }
.step-tag { background: #ddf4ff; color: #0969da; padding: 2px 10px;
            border-radius: 12px; font-size: 12px; }
.time { color: #57606a; font-size: 12px; margin-left: auto; }
.msg { padding: 10px 16px; border-top: 1px solid #f0f2f4; }
.msg-role { display: inline-block; font-weight: 700; font-size: 12px;
            margin-bottom: 6px; padding: 2px 8px; border-radius: 10px; }
.role-system { background: #eaeef2; color: #57606a; }
.role-human { background: #ddf4ff; color: #0969da; }
.role-ai { background: #dafbe1; color: #1a7f37; }
.role-tool { background: #fff8c5; color: #9a6700; }
.toolcall { border: 1px solid #54aeff; border-radius: 6px; margin: 6px 0;
            background: #f6fbff; }
.toolcall-head { padding: 6px 10px; font-weight: 600; font-size: 13px; color: #0969da;
                 cursor: pointer; }
.toolcall-body { padding: 8px 10px; border-top: 1px dashed #54aeff; display: none; }
.toolcall.open .toolcall-body { display: block; }
.retrieved { border: 1px solid #4ac26b; border-radius: 6px; margin: 6px 0;
             background: #f0fff4; }
.retrieved-head { padding: 6px 10px; font-weight: 600; font-size: 13px;
                  color: #1a7f37; cursor: pointer; }
.retrieved-body { padding: 8px 10px; border-top: 1px dashed #4ac26b; display: none;
                  white-space: pre-wrap; font-family: monospace; font-size: 12px;
                  max-height: 420px; overflow: auto; }
.retrieved.open .retrieved-body { display: block; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px;
      padding: 10px; overflow: auto; font-size: 12px; line-height: 1.45; }
details > summary { cursor: pointer; font-size: 13px; font-weight: 600;
                    color: #57606a; padding: 4px 0; }
.error-block { background: #ffebe9; border: 1px solid #ff818266; border-radius: 6px;
               margin: 10px 16px; padding: 10px; }
.error-block pre { background: transparent; border: none; color: #cf222e; }
.content-text { white-space: pre-wrap; font-size: 13px; line-height: 1.5; }
.msg.hidden { display: none; }
"""

_JS = """
function toggle(el) {
  var body = el.parentElement.querySelector('.toolcall-body, .retrieved-body');
  if (body) {
    var open = body.style.display === 'block';
    body.style.display = open ? 'none' : 'block';
    el.parentElement.classList.toggle('open', !open);
  }
}
function setFilter(mode) {
  document.querySelectorAll('.filters button').forEach(function(b) {
    b.classList.toggle('active', b.dataset.mode === mode);
  });
  document.querySelectorAll('.attempt').forEach(function(a) {
    if (mode === 'all') { a.style.display = ''; return; }
    var has = a.querySelector(mode === 'retrieval' ? '.retrieved' : '.error-block') !== null;
    a.style.display = has ? '' : 'none';
  });
  document.querySelectorAll('.msg').forEach(function(m) {
    m.classList.remove('hidden');
    if (mode === 'retrieval') {
      if (!m.classList.contains('msg-retrieval')) m.classList.add('hidden');
    } else if (mode === 'errors') {
      if (!m.classList.contains('msg-error') && !m.querySelector('.error-block')) m.classList.add('hidden');
    }
  });
}
"""


def _escape(text: str) -> str:
    return html.escape(str(text))


def _render_content(text: str) -> str:
    """消息正文：保留换行。"""
    if not text:
        return ""
    return f'<div class="content-text">{_escape(text)}</div>'


def _render_tool_result(msg: dict) -> str:
    """ToolMessage 结果。search_docs 特殊处理：完整展示检索内容。"""
    name = msg.get("name", "tool")
    content = msg.get("content", "")

    if name == "search_docs":
        return (
            '<div class="msg-retrieval">'
            f'<div class="retrieved"><div class="retrieved-head" onclick="toggle(this)">'
            f'🔍 检索结果（{name}）— 点击展开完整内容</div>'
            f'<div class="retrieved-body">{_escape(content)}</div></div>'
            '</div>'
        )
    if name == "write_query_file":
        return (
            f'<div class="toolcall"><div class="toolcall-head" onclick="toggle(this)">'
            f'📄 提交 query 文件 — 点击查看代码</div>'
            f'<div class="toolcall-body"><pre>{_escape(content)}</pre></div></div>'
        )
    return (
        f'<div class="toolcall"><div class="toolcall-head" onclick="toggle(this)">'
        f'🔧 工具结果（{name}）</div>'
        f'<div class="toolcall-body"><div class="content-text">{_escape(content)}</div></div></div>'
    )


def _render_ai_msg(msg: dict) -> str:
    """AIMessage：正文 + tool_calls。"""
    parts = []
    content = msg.get("content", "")
    if isinstance(content, str) and content.strip():
        parts.append(_render_content(content))

    for tc in msg.get("tool_calls", []) or []:
        tname = tc.get("name", "tool")
        args = tc.get("args", {})
        args_str = json.dumps(args, ensure_ascii=False, indent=2)
        # 大参数（如 query 代码）折叠展示
        if len(args_str) > 3000:
            args_view = (
                f'<details><summary>参数（{len(args_str)} 字符）点击展开</summary>'
                f'<pre>{_escape(args_str)}</pre></details>')
        else:
            args_view = f'<pre>{_escape(args_str)}</pre>'
        icon = {"search_docs": "🔍", "read_file": "📖", "write_query_file": "📄"}.get(tname, "🔧")
        parts.append(
            f'<div class="toolcall"><div class="toolcall-head" onclick="toggle(this)">'
            f'{icon} 调用工具: {tname}</div>'
            f'<div class="toolcall-body">{args_view}</div></div>')

    return "".join(parts)


def _render_messages(messages: list) -> str:
    out = []
    for msg in messages:
        mtype = msg.get("type", "")
        role = mtype
        role_cn = {"system": "System", "human": "Human",
                   "ai": "Assistant", "tool": "Tool"}.get(mtype, mtype)
        body = ""
        if mtype == "ai":
            body = _render_ai_msg(msg)
        elif mtype == "tool":
            body = _render_tool_result(msg)
        else:
            body = _render_content(msg.get("content", ""))

        extra_class = ""
        if mtype == "tool" and msg.get("name") == "search_docs":
            extra_class = " msg-retrieval"
        out.append(
            f'<div class="msg{extra_class}">'
            f'<span class="msg-role role-{role}">{role_cn}</span>'
            f'{body}</div>')
    return "".join(out)


def _render_attempt(attempt_dir: str) -> str:
    meta = {}
    meta_path = os.path.join(attempt_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

    name = os.path.basename(attempt_dir)
    step = meta.get("step", "?")
    stage = meta.get("stage", "?")
    t = meta.get("time", "")

    parts = [f'<div class="attempt" data-step="{step}">']
    parts.append(
        '<div class="attempt-header">'
        f'<span class="attempt-num">{name}</span>'
        f'<span class="step-tag">{stage} / {step}</span>'
        f'<span class="time">{t}</span>'
        '</div>')

    # 对话时间线
    msgs_path = os.path.join(attempt_dir, "messages.json")
    if os.path.exists(msgs_path):
        with open(msgs_path, encoding="utf-8") as f:
            messages = json.load(f)
        parts.append(_render_messages(messages))
    else:
        parts.append('<div class="msg">(无 messages.json)</div>')

    # 编译错误
    err_path = os.path.join(attempt_dir, "compile_error.txt")
    if os.path.exists(err_path):
        with open(err_path, encoding="utf-8") as f:
            err = f.read()
        parts.append(
            f'<div class="error-block"><strong>❌ 编译错误</strong>'
            f'<pre>{_escape(err)}</pre></div>')

    # 用例结果
    res_path = os.path.join(attempt_dir, "case_results.json")
    if os.path.exists(res_path):
        with open(res_path, encoding="utf-8") as f:
            results = json.load(f)
        parts.append(
            f'<div class="error-block"><strong>🧪 用例结果</strong>'
            f'<pre>{_escape(json.dumps(results, ensure_ascii=False, indent=2))}</pre></div>')

    # 本轮 query
    ql_path = os.path.join(attempt_dir, "query.ql")
    if os.path.exists(ql_path):
        with open(ql_path, encoding="utf-8") as f:
            ql = f.read()
        parts.append(
            f'<details><summary>📄 本轮 query 代码（{len(ql)} 字符）</summary>'
            f'<pre>{_escape(ql)}</pre></details>')

    parts.append("</div>")
    return "".join(parts)


def render(attempts_dir: str, output: str) -> None:
    attempt_dirs = sorted(
        (os.path.join(attempts_dir, d) for d in os.listdir(attempts_dir)
         if os.path.isdir(os.path.join(attempts_dir, d)))
    )
    if not attempt_dirs:
        print(f"⚠ {attempts_dir} 下没有 attempt 目录")
        return

    body = "".join(_render_attempt(d) for d in attempt_dirs)

    page = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>Agent Trace Report — {os.path.basename(attempts_dir)}</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>CodeQL Agent Trace — {_escape(os.path.basename(attempts_dir))}</h1>
  <div class="filters">
    <button data-mode="all" class="active" onclick="setFilter('all')">全部</button>
    <button data-mode="retrieval" onclick="setFilter('retrieval')">只看检索</button>
    <button data-mode="errors" onclick="setFilter('errors')">只看错误/结果</button>
  </div>
</header>
<div class="wrap">{body}</div>
<script>{_JS}</script>
</body>
</html>"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✅ 报告已生成: {output}（{len(attempt_dirs)} 个 attempt）")


def main():
    parser = argparse.ArgumentParser(description="渲染 agent trace 为 HTML 报告")
    parser.add_argument("--attempts-dir", required=True,
                        help="attempts 目录路径（如 result_generation/codeql/python/<rule>/attempts）")
    parser.add_argument("--output", default="trace_report.html",
                        help="输出 HTML 文件路径")
    args = parser.parse_args()
    render(args.attempts_dir, args.output)


if __name__ == "__main__":
    main()
