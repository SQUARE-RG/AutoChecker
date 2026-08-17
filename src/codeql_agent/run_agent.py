"""Phase 1 LangGraph agent 单规则入口。

用法（从项目根目录运行）:
    python src/codeql_agent/run_agent.py \
        --rules experiment/openssf/python/openssf_single_rules_single.json
"""

import argparse
import glob
import json
import os
import random
import shutil
import sys
import time
from pathlib import Path

# 统一约束：必须从 /root/code_check 运行（config / embedding_db 路径依赖 CWD）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
os.chdir(str(_PROJECT_ROOT))

from loguru import logger  # noqa: E402

from config import global_config  # noqa: E402
from codeql_language_config import get_language_config  # noqa: E402
from plateform.code_ql_uniform import (  # noqa: E402
    write_qlpack,
    create_database,
)
from codeql_agent.graph import build_graph  # noqa: E402
from codeql_agent.tools import build_tools, RetrievalContext  # noqa: E402


def load_cases(rule_test_path: str, extensions: list) -> tuple:
    """加载测试用例，返回 (neg_cases, pos_cases)，每个元素 (name, path, code)。"""
    cases = []
    for ext in extensions:
        for fp in glob.glob(os.path.join(rule_test_path, f"*{ext}")):
            with open(fp, encoding="utf-8") as f:
                code = f.read()
            name = os.path.basename(fp)
            is_neg = "CHECK-MESSAGES" in code
            cases.append((name, fp, code, is_neg))
    neg = [(n, p, c) for n, p, c, neg in cases if neg]
    pos = [(n, p, c) for n, p, c, neg in cases if not neg]
    return neg, pos


def run_one_rule(rule_info: dict, lang_config, result_dir: str) -> dict:
    rule_name = rule_info["main_title"]
    rule_result_dir = os.path.join(result_dir, "codeql", lang_config.language, rule_name)
    if os.path.exists(rule_result_dir):
        shutil.rmtree(rule_result_dir)
    os.makedirs(rule_result_dir, exist_ok=True)

    # qlpack.yml（语言单一来源 + 规则级额外依赖）
    write_qlpack(rule_name, rule_result_dir, lang_config,
                 extra_dependencies=rule_info.get("extra_dependencies"))

    # 随机选正负例
    neg_cases, pos_cases = load_cases(rule_info["rule_test_path"], lang_config.source_extensions)
    if not neg_cases or not pos_cases:
        logger.error(f"规则 {rule_name} 缺负例或正例: neg={len(neg_cases)} pos={len(pos_cases)}")
        return {"issuccess": "False", "performance": "0/0", "reason": "缺用例"}

    neg_name, neg_path, neg_code = random.choice(neg_cases)
    pos_name, pos_path, pos_code = random.choice(pos_cases)
    logger.info(f"负例: {neg_name}  正例: {pos_name}")

    # 为两个用例创建 database
    create_database(neg_path, lang_config)
    create_database(pos_path, lang_config)

    # 组装 state
    initial_state = {
        "rule_name": rule_name,
        "rule_description": rule_info["description"],
        "neg_case_name": neg_name, "neg_case_path": neg_path, "neg_case_code": neg_code,
        "pos_case_name": pos_name, "pos_case_path": pos_path, "pos_case_code": pos_code,
        "result_dir": rule_result_dir,
        "test_case_dir": rule_info["rule_test_path"],
        "messages": [],
        "llm_calls_this_attempt": 0,
        "query_code": "",
        "parse_fail_reason": "",
        "compile_ok": False, "compile_error": "",
        "compile_attempts": 0,
        "verify_ok": False, "case_results": [],
        "test_attempts": 0,
        "attempt_history": [],
        "stage": "first", "step": "generate",
        "attempt_counter": 1,
        "parse_retries": 0,
        "final_status": "",
        "failure_reason": "",
    }

    # 检索上下文（run 级，每条规则独立，不跨规则共享）
    ctx = RetrievalContext()
    tools = build_tools(rule_result_dir, rule_info["rule_test_path"], rule_name, ctx)
    usage_records = []

    graph = build_graph()
    start = time.perf_counter()
    final_state = graph.invoke(
        initial_state,
        config={"configurable": {"tools": tools, "usage": usage_records, "ctx": ctx},
                "recursion_limit": 300},   # 3 attempt × ~40 步 = 120，留 2.5 倍余量
    )
    elapsed = time.perf_counter() - start

    # 汇总用量
    total_cost = sum(r["total_cost"] for r in usage_records)
    total_tokens = sum(r["total_tokens"] for r in usage_records)
    logger.info("=" * 50)
    logger.info(f"AGENT RUN: {rule_name}")
    logger.info(f"  status: {final_state['final_status']}")
    logger.info(f"  reason: {final_state.get('failure_reason', '')}")
    logger.info(f"  LLM calls: {len(usage_records)}")
    logger.info(f"  Total tokens: {total_tokens}")
    logger.info(f"  Total cost: ¥{total_cost:.6f}")
    logger.info(f"  Elapsed: {elapsed:.1f}s")
    logger.info("=" * 50)

    # 结果写入规则 JSON 结构
    rule_info["issuccess"] = "True" if final_state["final_status"] == "success" else "False"
    rule_info["performance"] = (
        "2/2" if final_state["final_status"] == "success" else "0/2")
    rule_info["usage"] = {
        "llm_calls": len(usage_records),
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "elapsed": elapsed,
        "calls": usage_records,
    }
    rule_info["attempt_history"] = final_state.get("attempt_history", [])
    rule_info["selected_cases"] = {"negative": neg_name, "positive": pos_name}
    return rule_info


def main():
    parser = argparse.ArgumentParser(description="Phase 1 LangGraph CodeQL agent")
    parser.add_argument("--rules", required=True, help="Path to rules JSON")
    parser.add_argument("--language", default="python", choices=["cpp", "python"])
    args = parser.parse_args()

    lang_config = get_language_config(args.language)
    result_dir = global_config["result"]["result_dir"]

    with open(args.rules, "r") as f:
        rule_data = json.load(f)

    for package, rule_list in rule_data.get("data", {}).items():
        for rule_info in rule_list:
            run_one_rule(rule_info, lang_config, result_dir)

    out_path = os.path.join(result_dir, "codeql", args.language,
                            "agent_checker_generation_result.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rule_data, f, indent=4, ensure_ascii=False)
    logger.info(f"结果已保存 → {out_path}")


if __name__ == "__main__":
    main()
