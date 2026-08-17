"""LangGraph 节点实现（Phase 1）。

节点类型：
- prep 节点（prep_first_gen / prep_repair）：组装 messages（C 方案：每轮全新对话）
- agent 节点（call_model / call_tools）：受限工具循环
- 纯函数节点（extract_code / compile_query / verify_cases / archive_attempt /
  save_result / fail_rule）：确定性逻辑，复用 plateform/code_ql_uniform.py
"""

import json
import os
from datetime import datetime

from langchain_community.callbacks import get_openai_callback
from langchain_core.runnables import RunnableConfig
from loguru import logger

from codeql_language_config import PYTHON_CONFIG
from llm_interface.llm_provider import calculate_deepseek_cost
from plateform.code_ql_uniform import (
    compiler_code_ql,
    run_code_ql_with_query,
    case_path_to_database_path,
    write_qlpack,
)
from prompt.codeql_prompt.codeql_python_prompt import (
    build_first_gen_messages,
    build_repair_compile_messages,
    build_repair_verify_messages,
)
from codeql_agent.parser import find_query_code_block
from codeql_agent.state import AgentState

MAX_COMPILE_ATTEMPTS = 3
MAX_TEST_ATTEMPTS = 3
MAX_PARSE_RETRIES = 3
MAX_LLM_CALLS_PER_ATTEMPT = 16   # attempt 内 LLM 调用预算（+1 次豁免提交）
MIN_QUERY_CHARS = 200            # query 最小有效长度（防碎片）

# ── prep 节点 ──────────────────────────────────────────────

def _get_ctx(config: RunnableConfig):
    """从 graph config 取 RetrievalContext（run_agent 创建后注入）。"""
    return config["configurable"]["ctx"]


def _summaries_block(ctx) -> str:
    """构造'已检索内容摘要'注入块。"""
    sums = ctx.summaries(limit=8) if ctx is not None else []
    if not sums:
        return "(无——本轮尚未检索过任何内容)"
    lines = "\n".join(f"{i}. {s}" for i, s in enumerate(sums, 1))
    return lines


def prep_first_gen(state: AgentState, config: RunnableConfig) -> AgentState:
    """first_gen 阶段：全新对话（C 方案）+ 注入检索摘要。"""
    messages = build_first_gen_messages(
        rule_description=state["rule_description"],
        neg_case=state["neg_case_code"],
        pos_case=state["pos_case_code"],
        retrieved_summary=_summaries_block(_get_ctx(config)),
    )
    return {
        "messages": messages,
        "stage": "first",
        "step": "generate",
        "file_written": False,
        "parse_retries": state.get("parse_retries", 0),
        "llm_calls_this_attempt": 0,
        "budget_exempt": False,
    }


def prep_repair(state: AgentState, config: RunnableConfig) -> AgentState:
    """repair 阶段：按 step 组装全新对话 + 注入检索摘要。"""
    history = state.get("attempt_history", [])
    retrieved = _summaries_block(_get_ctx(config))
    if state["step"] == "repair_compile":
        messages = build_repair_compile_messages(
            rule_name=state["rule_name"],
            query_code=state["query_code"],
            compile_error=state["compile_error"],
            attempt_history=history,
            retrieved_summary=retrieved,
        )
    else:  # repair_verify
        messages = build_repair_verify_messages(
            rule_name=state["rule_name"],
            query_code=state["query_code"],
            case_results=state["case_results"],
            attempt_history=history,
            retrieved_summary=retrieved,
        )
    return {
        "messages": messages,
        "file_written": False,
        "llm_calls_this_attempt": 0,
        "budget_exempt": False,
    }


# ── agent 节点 ────────────────────────────────────────────

def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    """LLM-with-tools 调用。usage 通过 config["configurable"]["usage"] 累积。"""
    from llm_interface.llm_provider import llm_client

    tools = config["configurable"]["tools"]
    llm_with_tools = llm_client.bind_tools(tools)

    with get_openai_callback() as cb:
        response = llm_with_tools.invoke(state["messages"])

    # 计费累积
    usage_records = config["configurable"]["usage"]
    usage_records.append(calculate_deepseek_cost(cb))

    return {
        "messages": state["messages"] + [response],
        "llm_calls_this_attempt": state.get("llm_calls_this_attempt", 0) + 1,
    }


def call_tools(state: AgentState, config: RunnableConfig) -> AgentState:
    """执行最后一条 AIMessage 的 tool_calls。"""
    from langchain_core.messages import ToolMessage

    tools_by_name = {t.name: t for t in config["configurable"]["tools"]}

    messages = state["messages"]
    last = messages[-1]

    new_msgs = []
    for tc in last.tool_calls:
        name = tc["name"]
        args = tc.get("args", {})
        tool_fn = tools_by_name.get(name)
        if tool_fn is None:
            result = f"错误: 未知工具 {name}"
        else:
            try:
                result = str(tool_fn.invoke(args))
            except Exception as e:
                result = f"工具执行失败: {e}"
        new_msgs.append(ToolMessage(content=result, tool_call_id=tc["id"], name=name))

    return {"messages": messages + new_msgs}


def extract_code(state: AgentState) -> AgentState:
    """从 agent 的最终文本输出中提取 query 代码（严格锚点解析）。

    流程:
    1. 取最新一条 AI 文本消息
    2. 严格锚点提取 query_code: ```query 块
    3. 质量校验: 碎片(<200字符) / 污染(文档标记)
    4. 通过 → 系统写工作文件；失败 → 记录原因(A/B/C) 供提醒使用
    """
    result_dir = state["result_dir"]
    rule_name = state["rule_name"]
    work_path = os.path.join(result_dir, f"{rule_name}.ql")

    # 只检查最新一条含内容的 AI 消息（避免历史坏输出干扰）
    for msg in reversed(state["messages"]):
        content = getattr(msg, "content", None)
        if not isinstance(content, str) or not content.strip():
            continue

        block = find_query_code_block(content)
        if block is None:
            return {"query_code": "", "parse_fail_reason": "A"}  # 无代码块

        code = block.strip()
        if len(code) < MIN_QUERY_CHARS:
            return {"query_code": "", "parse_fail_reason": "B"}  # 碎片

        if _is_contaminated(code):
            return {"query_code": "", "parse_fail_reason": "C"}  # 污染

        # 成功：系统写文件
        with open(work_path, "w", encoding="utf-8") as f:
            f.write(code)
        logger.info(f"extract_code: 解析成功，{len(code)} 字符 → {work_path}")
        return {"query_code": code, "parse_fail_reason": ""}

    return {"query_code": "", "parse_fail_reason": "A"}


def _is_contaminated(code: str) -> bool:
    """检测 query 代码是否混入了检索文档内容。"""
    markers = ["[doc ", "Code Example", "### 检索", "**Type**", "**Path**"]
    return any(m in code for m in markers)


# ── 纯函数节点 ────────────────────────────────────────────

def compile_query(state: AgentState) -> AgentState:
    """编译 + qlpack 前置检查。"""
    result_dir = state["result_dir"]
    rule_name = state["rule_name"]
    work_path = os.path.join(result_dir, f"{rule_name}.ql")
    qlpack_path = os.path.join(result_dir, "qlpack.yml")

    # qlpack 前置检查（§9.4 不变量）
    if not os.path.exists(qlpack_path):
        logger.warning("qlpack.yml 缺失，重新生成（防御性）")
        write_qlpack(rule_name, result_dir, PYTHON_CONFIG)

    rc, stdout, stderr, ok = compiler_code_ql(work_path)
    return {
        "compile_ok": ok,
        "compile_error": (stderr or stdout)[:4000] if not ok else "",
    }


def verify_cases(state: AgentState) -> AgentState:
    """verify_two：跑负例 + 正例。"""
    result_dir = state["result_dir"]
    rule_name = state["rule_name"]
    work_path = os.path.join(result_dir, f"{rule_name}.ql")

    results = []
    for name, path, is_neg in [
        (state["neg_case_name"], state["neg_case_path"], True),
        (state["pos_case_name"], state["pos_case_path"], False),
    ]:
        db = case_path_to_database_path(path)
        if db is None:
            results.append((name, is_neg, -1))
            continue
        out = os.path.join(os.path.dirname(path), f"{rule_name}_output.csv")
        _, wc = run_code_ql_with_query(work_path, db, out)
        results.append((name, is_neg, wc))

    neg_wc = next(wc for n, is_neg, wc in results if is_neg)
    pos_wc = next(wc for n, is_neg, wc in results if not is_neg)
    verify_ok = (neg_wc >= 1) and (pos_wc == 0)

    logger.info(f"verify_two: neg={neg_wc} pos={pos_wc} → {'PASS' if verify_ok else 'FAIL'}")
    return {"verify_ok": verify_ok, "case_results": results}


def archive_attempt(state: AgentState) -> AgentState:
    """归档本轮产物到 attempts/{NN}_{stage}_{step}/，attempt_counter += 1。"""
    result_dir = state["result_dir"]
    rule_name = state["rule_name"]
    counter = state["attempt_counter"]
    step = state["step"]
    stage = state["stage"]

    attempt_dir = os.path.join(result_dir, "attempts", f"{counter:02d}_{stage}_{step}")
    os.makedirs(attempt_dir, exist_ok=True)

    # query 快照
    work_path = os.path.join(result_dir, f"{rule_name}.ql")
    if os.path.exists(work_path):
        with open(work_path, "r", encoding="utf-8") as src, \
             open(os.path.join(attempt_dir, "query.ql"), "w", encoding="utf-8") as dst:
            dst.write(src.read())

    # messages 序列化
    msgs = []
    for m in state["messages"]:
        try:
            msgs.append(m.model_dump())
        except Exception:
            msgs.append({"type": type(m).__name__, "content": str(getattr(m, "content", ""))})
    with open(os.path.join(attempt_dir, "messages.json"), "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2, default=str)

    # 触发原因 / 结果
    if step == "repair_compile":
        with open(os.path.join(attempt_dir, "compile_error.txt"), "w", encoding="utf-8") as f:
            f.write(state.get("compile_error", ""))
    elif step == "repair_verify":
        with open(os.path.join(attempt_dir, "case_results.json"), "w", encoding="utf-8") as f:
            json.dump(state.get("case_results", []), f, ensure_ascii=False, indent=2)

    # meta
    meta = {
        "stage": stage,
        "step": step,
        "attempt": counter,
        "time": datetime.now().isoformat(),
        "query_size": len(state.get("query_code", "")),
    }
    with open(os.path.join(attempt_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logger.info(f"archived → {attempt_dir}")
    return {"attempt_counter": counter + 1}


def save_result(state: AgentState) -> AgentState:
    """Phase 1 成功收尾。"""
    state["final_status"] = "success"
    state["failure_reason"] = ""
    logger.info(f"Phase 1 SUCCESS: {state['rule_name']} verify_two 通过")
    return state


def fail_rule(state: AgentState) -> AgentState:
    """规则判失败。"""
    state["final_status"] = "failed"
    state["failure_reason"] = state.get("failure_reason", "unknown")
    logger.error(f"Phase 1 FAILED: {state['rule_name']} — {state['failure_reason']}")
    return state
