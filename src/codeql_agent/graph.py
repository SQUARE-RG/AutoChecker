"""StateGraph 组装与路由（Phase 1）。

流程（设计文档 §2 / §8.3 统一 graph 的 first 阶段部分）:

START → prep_first_gen → [call_model ⇄ call_tools] → extract_code
         ├─ 无代码 & parse_retries < 3 → append_reminder → call_model
         ├─ 无代码 & 重试耗尽 → fail_rule
         └─ 有代码 → archive_attempt → compile_query
              ├─ 编译失败 & attempts < 3 → on_compile_fail → prep_repair → call_model...
              ├─ 编译失败 & 耗尽 → fail_rule
              └─ 编译成功 → verify_cases
                   ├─ 用例失败 & attempts < 3 → on_verify_fail → prep_repair → call_model...
                   ├─ 用例失败 & 耗尽 → fail_rule
                   └─ 通过 → save_result → END
"""

from langgraph.graph import END, START, StateGraph

from codeql_agent import nodes
from codeql_agent.state import AgentState

MAX_COMPILE_ATTEMPTS = nodes.MAX_COMPILE_ATTEMPTS
MAX_TEST_ATTEMPTS = nodes.MAX_TEST_ATTEMPTS
MAX_PARSE_RETRIES = nodes.MAX_PARSE_RETRIES
MAX_LLM_CALLS_PER_ATTEMPT = nodes.MAX_LLM_CALLS_PER_ATTEMPT


# ── 状态变更小节点 ─────────────────────────────────────────

def on_compile_fail(state: AgentState) -> AgentState:
    """编译失败：记录摘要、计数、设定下一步为 repair_compile。"""
    err_line = (state.get("compile_error", "") or "unknown").strip().splitlines()
    first_line = err_line[0][:120] if err_line else "unknown"
    failed_attempt = state["attempt_counter"] - 1
    history = state.get("attempt_history", []) + [
        f"r{failed_attempt}: {state['step']} 编译失败: {first_line}"
    ]
    return {
        "attempt_history": history,
        "compile_attempts": state.get("compile_attempts", 0) + 1,
        "step": "repair_compile",
        "failure_reason": f"编译修复耗尽: {first_line}",
    }


def on_verify_fail(state: AgentState) -> AgentState:
    """用例失败：记录摘要、计数、设定下一步为 repair_verify。"""
    neg_wc = next((wc for n, is_neg, wc in state["case_results"] if is_neg), "?")
    pos_wc = next((wc for n, is_neg, wc in state["case_results"] if not is_neg), "?")
    failed_attempt = state["attempt_counter"] - 1
    history = state.get("attempt_history", []) + [
        f"r{failed_attempt}: {state['step']} 用例失败: neg={neg_wc} pos={pos_wc}"
    ]
    return {
        "attempt_history": history,
        "test_attempts": state.get("test_attempts", 0) + 1,
        "step": "repair_verify",
        "failure_reason": f"用例修复耗尽: neg={neg_wc} pos={pos_wc}",
    }


# ── 解析失败提醒（递进文案，3 次后规则级失败）──────────────

_FAIL_REASON_TEXT = {
    "A": "回复中没有找到 query_code: ```query 代码块",
    "B": "代码块内容不完整（代码太短）",
    "C": "代码块中混入了文档内容或其他非 QL 文本",
}

_FMT_EXAMPLE = """query_code:
```query
<完整的 QL 代码：QLDoc 注释 + import + 定义 + from-where-select>
```"""


def append_reminder(state: AgentState) -> AgentState:
    """解析失败重试：按失败次数递进提醒（第 3 次为最后通牒）。"""
    from langchain_core.messages import HumanMessage

    retries = state.get("parse_retries", 0)  # 本次失败之前已重试次数
    reason = _FAIL_REASON_TEXT.get(state.get("parse_fail_reason", ""), "输出格式不符合要求")

    if retries == 0:
        msg = (f"输出格式不符合要求（原因: {reason}）。请严格按以下格式重新输出：\n\n"
               f"{_FMT_EXAMPLE}")
    elif retries == 1:
        msg = (f"再次提醒（原因: {reason}）。你只能输出一个 query_code: ```query "
               f"代码块，块内是完整的 QL 源码，块外不允许有任何文字。")
    else:
        msg = (f"这是最后一次尝试（原因: {reason}）。如果本次仍未严格输出 "
               f"query_code: ```query 代码块，任务将判定失败。")

    return {
        "messages": state["messages"] + [HumanMessage(content=msg)],
        "parse_retries": retries + 1,
    }


# ── 路由函数 ───────────────────────────────────────────────

def route_after_agent(state: AgentState) -> str:
    """agent 回答后的预算路由：
    - 无工具调用 → 提取代码
    - 有工具调用且预算内（<16）→ 执行工具
    - 有工具调用且预算耗尽 → 强制截断到提取（不再执行工具）
    """
    last = state["messages"][-1]
    if not getattr(last, "tool_calls", None):
        return "extract_code"
    if state.get("llm_calls_this_attempt", 0) < MAX_LLM_CALLS_PER_ATTEMPT:
        return "call_tools"
    return "extract_code"


def route_after_extract(state: AgentState) -> str:
    """提取后分诊：有代码 → 归档；无代码 → 提醒重试或规则级失败。"""
    if state.get("query_code"):
        return "archive_attempt"
    retries = state.get("parse_retries", 0)
    calls = state.get("llm_calls_this_attempt", 0)
    if retries < MAX_PARSE_RETRIES and calls < MAX_LLM_CALLS_PER_ATTEMPT:
        return "append_reminder"
    return "fail_rule"


def route_after_compile(state: AgentState) -> str:
    if state["compile_ok"]:
        return "verify_cases"
    if state.get("compile_attempts", 0) < MAX_COMPILE_ATTEMPTS:
        return "on_compile_fail"
    return "fail_rule"


def route_after_verify(state: AgentState) -> str:
    if state["verify_ok"]:
        return "save_result"
    if state.get("test_attempts", 0) < MAX_TEST_ATTEMPTS:
        return "on_verify_fail"
    return "fail_rule"


# ── graph 组装 ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    g.add_node("prep_first_gen", nodes.prep_first_gen)
    g.add_node("prep_repair", nodes.prep_repair)
    g.add_node("call_model", nodes.call_model)
    g.add_node("call_tools", nodes.call_tools)
    g.add_node("extract_code", nodes.extract_code)
    g.add_node("archive_attempt", nodes.archive_attempt)
    g.add_node("compile_query", nodes.compile_query)
    g.add_node("verify_cases", nodes.verify_cases)
    g.add_node("save_result", nodes.save_result)
    g.add_node("fail_rule", nodes.fail_rule)
    g.add_node("on_compile_fail", on_compile_fail)
    g.add_node("on_verify_fail", on_verify_fail)
    g.add_node("append_reminder", append_reminder)

    g.add_edge(START, "prep_first_gen")

    # agent 工具循环
    g.add_edge("prep_first_gen", "call_model")
    g.add_edge("prep_repair", "call_model")
    g.add_conditional_edges("call_model", route_after_agent,
                            {"call_tools": "call_tools", "extract_code": "extract_code"})
    g.add_edge("call_tools", "call_model")   # 无轮数限制：工具执行完回模型

    # 输出提取与重试
    g.add_conditional_edges("extract_code", route_after_extract,
                            {"archive_attempt": "archive_attempt",
                             "append_reminder": "append_reminder",
                             "fail_rule": "fail_rule"})
    g.add_edge("append_reminder", "call_model")

    # 编译
    g.add_edge("archive_attempt", "compile_query")
    g.add_conditional_edges("compile_query", route_after_compile,
                            {"verify_cases": "verify_cases",
                             "on_compile_fail": "on_compile_fail",
                             "fail_rule": "fail_rule"})
    g.add_edge("on_compile_fail", "prep_repair")

    # 验证
    g.add_conditional_edges("verify_cases", route_after_verify,
                            {"save_result": "save_result",
                             "on_verify_fail": "on_verify_fail",
                             "fail_rule": "fail_rule"})
    g.add_edge("on_verify_fail", "prep_repair")

    g.add_edge("save_result", END)
    g.add_edge("fail_rule", END)

    return g.compile()
