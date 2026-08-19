"""StateGraph 组装与路由（Phase 1 + 强化阶段）。

Phase 1:
  START → prep_first_gen → [call_model ⇄ call_tools] → extract_code
           ├─ 无代码 → append_reminder 重试（3 次）/ fail_rule
           └─ 有代码 → archive → compile
                ├─ 编译失败 → on_compile_fail → prep_repair → agent...
                └─ 编译成功 → verify_two
                     ├─ 失败 → on_verify_fail → prep_repair → agent...
                     └─ 通过 → run_all（全量 20 用例）

强化阶段（设计稿 docs/langgraph_codeql_python_augment_design.md）:
  run_all
    ├─ 全过 → save_result(success)
    └─ 有失败 → pick_target → prep_augment → agent → archive → compile
         ├─ 编译失败 → on_compile_fail → prep_augment_repair_compile → agent...
         │            （compile_attempts ≥3 → on_augment_retry）
         └─ 编译成功 → verify_target（只跑 target）
              ├─ target 没过 → on_verify_fail → prep_augment_repair_verify → agent...
              │               （test_attempts ≥3 → on_augment_retry）
              └─ target 过 → run_all 回归
                   ├─ 全过 → save_result(success)
                   ├─ 失败集变小 → on_augment_success → pick_target（下一个）
                   └─ 失败集未变小 → on_augment_retry
                          ├─ augment_attempts <3 → prep_augment（重试同 target）
                          └─ ≥3 → on_target_skip → pick_target / save_result(部分)
"""

from langgraph.graph import END, START, StateGraph

from codeql_agent import nodes
from codeql_agent.state import AgentState

MAX_COMPILE_ATTEMPTS = nodes.MAX_COMPILE_ATTEMPTS
MAX_TEST_ATTEMPTS = nodes.MAX_TEST_ATTEMPTS
MAX_PARSE_RETRIES = nodes.MAX_PARSE_RETRIES
MAX_LLM_CALLS_PER_ATTEMPT = nodes.MAX_LLM_CALLS_PER_ATTEMPT
MAX_AUGMENT_ATTEMPTS = 3           # 单 target 的强化尝试次数
MAX_GLOBAL_AUGMENT_ROUNDS = 10     # 全局强化轮数守卫


# ── 摘要 helper（§6.5）────────────────────────────────────

def _history_line(state: AgentState, outcome: str) -> str:
    """统一摘要行: r{attempt_counter-1}: {step}({target_name}) {outcome}"""
    target = f"({state['target_case']['name']})" if state.get("target_case") else ""
    return f"r{state['attempt_counter'] - 1}: {state['step']}{target} {outcome}"


# ── 状态变更小节点 ─────────────────────────────────────────

def on_compile_fail(state: AgentState) -> AgentState:
    """编译失败：记录摘要、计数、设定下一步（stage 感知）。"""
    err_line = (state.get("compile_error", "") or "unknown").strip().splitlines()
    first_line = err_line[0][:120] if err_line else "unknown"
    history = state.get("attempt_history", []) + [
        _history_line(state, f"编译失败: {first_line}")
    ]
    next_step = "augment_repair_compile" if state.get("stage") == "augment" else "repair_compile"
    return {
        "attempt_history": history,
        "compile_attempts": state.get("compile_attempts", 0) + 1,
        "step": next_step,
        "failure_reason": f"编译修复耗尽: {first_line}",
    }


def on_verify_fail(state: AgentState) -> AgentState:
    """用例失败：记录摘要、计数、设定下一步（stage 感知）。"""
    wc_txt = ", ".join(f"{n}={wc}" for n, is_neg, wc in state["case_results"])
    history = state.get("attempt_history", []) + [
        _history_line(state, f"用例失败: {wc_txt}")
    ]
    next_step = "augment_repair_verify" if state.get("stage") == "augment" else "repair_verify"
    return {
        "attempt_history": history,
        "test_attempts": state.get("test_attempts", 0) + 1,
        "step": next_step,
        "failure_reason": f"用例修复耗尽: {wc_txt}",
    }


def on_augment_retry(state: AgentState) -> AgentState:
    """本次 augment 修改无效：augment_attempts + 1，全局轮数 + 1。"""
    return {
        "augment_attempts": state.get("augment_attempts", 0) + 1,
        "global_augment_rounds": state.get("global_augment_rounds", 0) + 1,
    }


def on_augment_success(state: AgentState) -> AgentState:
    """target 修复成功：记录摘要，全局轮数 + 1。"""
    old = state.get("failed_count_before", 0)
    new = len(state.get("failed_cases", []))
    history = state.get("attempt_history", []) + [
        _history_line(state, f"成功: 失败集 {old}→{new}")
    ]
    return {
        "attempt_history": history,
        "global_augment_rounds": state.get("global_augment_rounds", 0) + 1,
    }


def on_run_error(state: AgentState) -> AgentState:
    """CodeQL 运行失败：记录摘要、计数（计入 test_attempts）、设定修复步骤。"""
    err = state.get("verify_run_error", "unknown")
    first_line = (err.strip().splitlines() or ["unknown"])[0][:120]
    history = state.get("attempt_history", []) + [
        _history_line(state, f"运行失败: {first_line}")
    ]
    return {
        "attempt_history": history,
        "test_attempts": state.get("test_attempts", 0) + 1,
        "step": "repair_run_error",
        "failure_reason": f"运行修复耗尽: {first_line}",
    }


def on_target_skip(state: AgentState) -> AgentState:
    """target 修不动：移出 failed_cases，记入 skipped_cases。"""
    target = state["target_case"]
    history = state.get("attempt_history", []) + [
        _history_line(state, f"跳过: {state.get('augment_attempts', 3)} 次尝试未修复")
    ]
    failed = [c for c in state.get("failed_cases", []) if c["name"] != target["name"]]
    skipped = state.get("skipped_cases", []) + [target["name"]]
    return {
        "attempt_history": history,
        "failed_cases": failed,
        "skipped_cases": skipped,
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
    """agent 回答后的预算路由。"""
    last = state["messages"][-1]
    if not getattr(last, "tool_calls", None):
        return "extract_code"
    if state.get("llm_calls_this_attempt", 0) < MAX_LLM_CALLS_PER_ATTEMPT:
        return "call_tools"
    return "extract_code"


def route_after_extract(state: AgentState) -> str:
    """提取后分诊：有代码 → 归档；无代码 → 提醒重试或失败。

    parse 重试耗尽 / LLM 预算耗尽时的去向按 stage 区分：
    - augment 阶段 → on_augment_retry（target 级失败：重试或跳过，继续其他用例）
    - first 阶段 → fail_rule（首轮生成失败即规则级失败）
    """
    if state.get("query_code"):
        return "archive_attempt"
    retries = state.get("parse_retries", 0)
    calls = state.get("llm_calls_this_attempt", 0)
    if retries < MAX_PARSE_RETRIES and calls < MAX_LLM_CALLS_PER_ATTEMPT:
        return "append_reminder"
    if state.get("stage") == "augment":
        return "on_augment_retry"
    return "fail_rule"


def route_after_compile(state: AgentState) -> str:
    """编译结果路由（stage 感知）。"""
    if state["compile_ok"]:
        return "verify_target" if state.get("stage") == "augment" else "verify_cases"
    if state.get("compile_attempts", 0) < MAX_COMPILE_ATTEMPTS:
        return "on_compile_fail"
    if state.get("stage") == "augment":
        return "on_augment_retry"
    return "fail_rule"


def route_after_compile_fail(state: AgentState) -> str:
    """编译失败后的下一 prep（stage 感知）。"""
    if state.get("stage") == "augment":
        return "prep_augment_repair_compile"
    return "prep_repair"


def route_after_verify(state: AgentState) -> str:
    """Phase 1 verify_two 结果路由：通过 → run_all 全量验证。

    失败分三类：
    - 环境错误（database 缺失）→ fail_rule（agent 修不了，不浪费调用）
    - 运行失败（wc=-1）→ on_run_error（query 格式问题，专门修复）
    - 用例失败（漏报/误报）→ on_verify_fail
    """
    if state.get("env_error"):
        return "fail_rule"
    if state.get("verify_run_error"):
        return "on_run_error"
    if state["verify_ok"]:
        return "run_all"
    if state.get("test_attempts", 0) < MAX_TEST_ATTEMPTS:
        return "on_verify_fail"
    return "fail_rule"


def route_after_verify_fail(state: AgentState) -> str:
    """用例失败后的下一 prep（stage 感知）。"""
    if state.get("stage") == "augment":
        return "prep_augment_repair_verify"
    return "prep_repair"


def route_after_verify_target(state: AgentState) -> str:
    """强化阶段 target 验证结果路由。

    失败分三类：
    - 环境错误（database 缺失）→ on_target_skip（跳过该用例，不打扰 agent）
    - 运行失败（wc=-1）→ on_run_error
    - 用例失败（漏报/误报）→ on_verify_fail
    """
    if state.get("env_error"):
        return "on_target_skip"
    if state.get("verify_run_error"):
        return "on_run_error"
    if state["verify_ok"]:
        return "run_all"              # 回归验证
    if state.get("test_attempts", 0) < MAX_TEST_ATTEMPTS:
        return "on_verify_fail"
    return "on_augment_retry"


def route_after_run_all(state: AgentState) -> str:
    """全量验证结果路由。"""
    if not state.get("failed_cases"):
        return "save_result"
    if state.get("global_augment_rounds", 0) >= MAX_GLOBAL_AUGMENT_ROUNDS:
        return "save_result"          # 全局守卫：保存部分成绩
    # 强化回归 vs 首次全量
    if state.get("target_case") and "failed_count_before" in state:
        if len(state["failed_cases"]) < state["failed_count_before"]:
            return "on_augment_success"
        return "on_augment_retry"
    return "pick_target"              # 首次进入强化


def route_after_augment_retry(state: AgentState) -> str:
    """augment 修改无效后的去向。"""
    if state.get("augment_attempts", 0) >= MAX_AUGMENT_ATTEMPTS:
        return "on_target_skip"
    if state.get("global_augment_rounds", 0) >= MAX_GLOBAL_AUGMENT_ROUNDS:
        return "on_target_skip"
    return "prep_augment"


def route_after_target_skip(state: AgentState) -> str:
    """跳过 target 后的去向。"""
    if state.get("failed_cases"):
        return "pick_target"
    return "save_result"


# ── graph 组装 ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Phase 1 节点
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
    # 强化阶段节点
    g.add_node("run_all", nodes.run_all_cases)
    g.add_node("pick_target", nodes.pick_target)
    g.add_node("prep_augment", nodes.prep_augment)
    g.add_node("prep_augment_repair_compile", nodes.prep_augment_repair_compile)
    g.add_node("prep_augment_repair_verify", nodes.prep_augment_repair_verify)
    g.add_node("verify_target", nodes.verify_target)
    # 状态变更小节点
    g.add_node("on_compile_fail", on_compile_fail)
    g.add_node("on_verify_fail", on_verify_fail)
    g.add_node("on_augment_retry", on_augment_retry)
    g.add_node("on_augment_success", on_augment_success)
    g.add_node("on_target_skip", on_target_skip)
    g.add_node("on_run_error", on_run_error)
    g.add_node("append_reminder", append_reminder)
    g.add_node("prep_repair_run_error", nodes.prep_repair_run_error)

    g.add_edge(START, "prep_first_gen")

    # agent 工具循环（共享）
    g.add_edge("prep_first_gen", "call_model")
    g.add_edge("prep_repair", "call_model")
    g.add_edge("prep_augment", "call_model")
    g.add_edge("prep_augment_repair_compile", "call_model")
    g.add_edge("prep_augment_repair_verify", "call_model")
    g.add_edge("prep_repair_run_error", "call_model")
    g.add_conditional_edges("call_model", route_after_agent,
                            {"call_tools": "call_tools", "extract_code": "extract_code"})
    g.add_edge("call_tools", "call_model")

    # 输出提取与重试
    g.add_conditional_edges("extract_code", route_after_extract,
                            {"archive_attempt": "archive_attempt",
                             "append_reminder": "append_reminder",
                             "on_augment_retry": "on_augment_retry",
                             "fail_rule": "fail_rule"})
    g.add_edge("append_reminder", "call_model")

    # 编译（stage 感知路由）
    g.add_edge("archive_attempt", "compile_query")
    g.add_conditional_edges("compile_query", route_after_compile,
                            {"verify_cases": "verify_cases",
                             "verify_target": "verify_target",
                             "on_compile_fail": "on_compile_fail",
                             "on_augment_retry": "on_augment_retry",
                             "fail_rule": "fail_rule"})
    g.add_conditional_edges("on_compile_fail", route_after_compile_fail,
                            {"prep_repair": "prep_repair",
                             "prep_augment_repair_compile": "prep_augment_repair_compile"})

    # Phase 1 verify_two → run_all
    g.add_conditional_edges("verify_cases", route_after_verify,
                            {"run_all": "run_all",
                             "on_verify_fail": "on_verify_fail",
                             "on_run_error": "on_run_error",
                             "fail_rule": "fail_rule"})
    g.add_conditional_edges("on_verify_fail", route_after_verify_fail,
                            {"prep_repair": "prep_repair",
                             "prep_augment_repair_verify": "prep_augment_repair_verify"})
    g.add_edge("on_run_error", "prep_repair_run_error")

    # 强化阶段
    g.add_conditional_edges("run_all", route_after_run_all,
                            {"save_result": "save_result",
                             "pick_target": "pick_target",
                             "on_augment_success": "on_augment_success",
                             "on_augment_retry": "on_augment_retry"})
    g.add_edge("pick_target", "prep_augment")
    g.add_conditional_edges("verify_target", route_after_verify_target,
                            {"run_all": "run_all",
                             "on_verify_fail": "on_verify_fail",
                             "on_run_error": "on_run_error",
                             "on_target_skip": "on_target_skip",
                             "on_augment_retry": "on_augment_retry"})
    g.add_conditional_edges("on_augment_retry", route_after_augment_retry,
                            {"prep_augment": "prep_augment",
                             "on_target_skip": "on_target_skip"})
    g.add_edge("on_augment_success", "pick_target")
    g.add_conditional_edges("on_target_skip", route_after_target_skip,
                            {"pick_target": "pick_target",
                             "save_result": "save_result"})

    g.add_edge("save_result", END)
    g.add_edge("fail_rule", END)

    return g.compile()
