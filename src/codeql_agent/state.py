"""LangGraph AgentState 定义（Phase 1）。

设计文档: docs/langgraph_codeql_python_design.md §3
"""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    # ── 输入（run_agent 注入）──
    rule_name: str
    rule_description: str
    neg_case_name: str          # 负例文件名
    neg_case_path: str
    neg_case_code: str
    pos_case_name: str          # 正例文件名
    pos_case_path: str
    pos_case_code: str
    result_dir: str             # {result_dir}/codeql/python/{rule}/
    test_case_dir: str          # 测试用例目录

    # ── agent 对话（普通 list：prep 节点整体替换实现 C 方案的"每轮全新对话"，
    #    agent 循环内由 call_model/call_tools 手动 append）──
    messages: list

    # ── attempt 预算机制（16 次 LLM 调用，耗尽即规则级失败，无豁免）──
    llm_calls_this_attempt: int  # 本次 attempt 的 LLM 调用计数（prep 重置为 0）

    # ── query 代码（始终指向工作文件 {rule}.ql 的内容）──
    query_code: str
    parse_fail_reason: str      # 解析失败原因: A=无代码块 B=碎片 C=污染 ""=成功

    # ── 编译 ──
    compile_ok: bool
    compile_error: str
    compile_attempts: int       # 编译修复次数（≤ 3，每阶段重置）

    # ── 用例验证 ──
    verify_ok: bool
    case_results: list          # [(case_name, is_neg, warning_count)]
    verify_run_error: str       # CodeQL 运行失败详情（wc=-1 时）；空串 = 无运行错误
    env_error: str              # 环境错误（如 database 缺失）；非空 = 不进入 repair，直接失败/跳过
    test_attempts: int          # 用例修复次数（≤ 3，每阶段重置）

    # ── 上下文管理（C 方案）──
    attempt_history: list       # 每轮一行摘要

    # ── 产物管理（由 graph 递增，agent 不可见）──
    stage: str                  # "first" / "augment"
    step: str                   # "generate" / "augment" / "augment_repair_compile" /
                                # "augment_repair_verify" / "repair_compile" / "repair_verify"
    attempt_counter: int        # 归档目录序号（跨阶段全局递增）
    parse_retries: int          # 本轮输出无效（未写文件且解析失败）的重试次数（≤ 3）

    # ── 强化阶段 ──
    all_cases: list             # 全部测试用例 [{name, path, is_neg, code}]
    failed_cases: list          # 当前失败用例名列表
    skipped_cases: list         # 修不动的用例名（跳过并记录）
    passed_cases: list          # 已通过用例 [{name, path, is_neg, code}]
    target_case: dict           # 当前强化的目标用例 {name, path, is_neg, code}
    augment_attempts: int       # 当前 target 的强化尝试次数（≤3）
    global_augment_rounds: int  # 全局强化轮数守卫（≤10）
    run_all_count: int          # run_all 已执行次数（防意外循环）

    # ── 终止状态 ──
    final_status: str           # "success" / "failed"
    failure_reason: str
    final_performance: str      # "18/20"
