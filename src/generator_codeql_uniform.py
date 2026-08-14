"""语言无关的 CodeQL Checker 生成器。

核心迭代逻辑与 code_ql_generator.py 一致，但所有语言相关参数从
LanguageConfig 获取，不再硬编码 C++ 路径 / 扩展名 / 代码块标记。
"""

import os
import re
import json
from typing import List

from loguru import logger

from entity.abstractProduct import AbstractCase, AbstractChecker, AbstractRule
from entity.concreteProduct_CodeQL import Checker_CodeQL
from config import global_config as config
from llm_interface.llm_provider import llm_client, llm_invoke, calculate_deepseek_cost
from prompt.codeql_prompt.build_codeql_prompt import get_prompt_for_Codeql
from codeql_language_config import LanguageConfig
from plateform.code_ql_uniform import (
    compiler_code_ql,
    run_code_ql_with_query,
    case_path_to_database_path,
)
from retriever.retriever_codeql_uniform import (
    get_most_similar_api_doc_query_op_uniform,
    get_suggest_string_from_hint_uniform,
)

max_round = config["arguments"]["max_round"]
max_compiler_trys = config["arguments"]["max_compiler_trys"]


# ── helpers ────────────────────────────────────────────────

def _make_logic_string(logics_json) -> str:
    parts = ["**logic for query**:"]
    for step in logics_json[0]["logic_query"]:
        parts.append(step)
    return "\n".join(parts)


def _count_negative_cases(case_list: List[AbstractCase]) -> int:
    return sum(1 for c in case_list if not c.get_flag())


def _select_negative_case(cases: List[AbstractCase], skipped: List[AbstractCase]) -> AbstractCase | None:
    for case in cases:
        if not case.get_flag() and case not in skipped:
            return case
    return None


def _parse_query_code(answer: str, code_block_marker: str) -> str | None:
    """从 LLM 回答中解析 query 代码块（语言感知）。"""
    # 优先匹配带标签的: query_code: ```[ql|query|python|...] ```
    pattern = rf"query_code\s*:\s*```(?:ql|query|{re.escape(code_block_marker)})\s*(.*?)\s*```"
    m = re.search(pattern, answer, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    # 退而求其次：取第一个 ql/query/<marker> 代码块
    blocks = re.findall(
        rf"```(?:ql|query|{re.escape(code_block_marker)})\s*(.*?)\s*```",
        answer, re.IGNORECASE | re.DOTALL)
    return blocks[0].strip() if blocks else None


# ── 生成器主类 ─────────────────────────────────────────────

class CodeQLGeneratorUniform:
    """语言无关的 CodeQL 查询生成器。"""

    def __init__(self, rule: AbstractRule,
                 all_test_cases: List[AbstractCase],
                 skipped_test_cases: List[AbstractCase] | None,
                 rule_result_dir: str,
                 lang_config: LanguageConfig):
        self.rule = rule
        self.all_test_cases = all_test_cases
        self.skipped_test_cases = skipped_test_cases if skipped_test_cases is not None else []
        self.result_dir = rule_result_dir
        self.lang = lang_config
        self.total_cost = 0.0
        self._llm_call_count = 0
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cached_tokens = 0
        self.debug_prompt_dir = os.path.join(self.result_dir, "debug_prompt")
        os.makedirs(self.debug_prompt_dir, exist_ok=True)

    @property
    def query_path(self) -> str:
        return os.path.join(self.result_dir, f"{self.rule.get_rule_name()}.ql")

    def _save_checker_code(self, query_code: str) -> str:
        with open(self.query_path, "w") as f:
            f.write(query_code)
        return self.query_path

    def _get_checker_code(self) -> str:
        with open(self.query_path, "r") as f:
            return f.read()

    def _save_middle_check(self, query_code: str, round_dir: str):
        path = os.path.join(round_dir, "query_code.ql")
        with open(path, "w") as f:
            f.write(query_code)

    # ── LLM 调用 ─────────────────────────────────────────

    def _track_usage(self, cb):
        """累积一次 LLM 调用的 token 和花费统计。"""
        usage = calculate_deepseek_cost(cb)
        self._llm_call_count += 1
        self._total_prompt_tokens += usage["prompt_tokens"]
        self._total_completion_tokens += usage["completion_tokens"]
        self._total_cached_tokens += usage["cached_tokens"]
        self.total_cost += usage["total_cost"]

    def get_usage_stats(self) -> dict:
        """返回当前规则的全部 LLM 用量统计。"""
        return {
            "rule_name": self.rule.get_rule_name(),
            "llm_calls": self._llm_call_count,
            "prompt_tokens": self._total_prompt_tokens,
            "completion_tokens": self._total_completion_tokens,
            "cached_tokens": self._total_cached_tokens,
            "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
            "total_cost_yuan": self.total_cost,
        }

    def _llm_json(self, prompt_key: str, query: str, label: str = "") -> list:
        for attempt in range(1, config["arguments"]["max_llm_tries"] + 1):
            answer, cb = llm_invoke(llm_client, query)
            self._track_usage(cb)
            logger.debug(f"LLM {label} attempt {attempt}:\n{answer}")
            try:
                cleaned = re.sub(r"```json|```", "", answer).strip()
                return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.debug(f"JSON parse error attempt {attempt}, retry...")
        return []

    def _llm_code(self, prompt_key: str, query: str, label: str = "") -> str | None:
        for attempt in range(1, config["arguments"]["max_llm_tries"] + 1):
            answer, cb = llm_invoke(llm_client, query)
            self._track_usage(cb)
            logger.debug(f"LLM {label} attempt {attempt}:\n{answer}")
            code = _parse_query_code(answer, self.lang.code_block_marker)
            if code:
                return code
        return None

    # ── 检索 ─────────────────────────────────────────────

    def _retrieve(self, logics_json):
        return get_most_similar_api_doc_query_op_uniform(logics_json, self.lang)

    def _retrieve_from_hint(self, hint):
        return get_suggest_string_from_hint_uniform(hint, self.lang)

    # ── 入口 ─────────────────────────────────────────────

    def generate_checker(self):
        os.makedirs(self.debug_prompt_dir, exist_ok=True)
        success, init_checker = self._first_checker_generation()
        if not success:
            logger.error(f"Failed initial generation: {self.rule.get_rule_name()}")
            return None
        logger.info("Initial checker generated")
        self.rule.add_checker(init_checker)
        self.skipped_test_cases = []
        self._checker_augmentation(init_checker)
        return self.rule.get_checkers()

    # ── 第一轮生成 ───────────────────────────────────────

    def _first_checker_generation(self):
        total_neg = _count_negative_cases(self.all_test_cases)
        first_dir = os.path.join(self.result_dir, "first_checker")
        os.makedirs(first_dir, exist_ok=True)

        for t in range(1, total_neg + 1):
            case = _select_negative_case(self.all_test_cases, self.skipped_test_cases)
            if case is None:
                break
            logger.info(f"Selected negative case: {case.get_case_path()}")

            case_dir = os.path.join(first_dir, f"negative_case_{t}")
            os.makedirs(case_dir, exist_ok=True)
            rnd = 1
            ok = False

            while not ok:
                if rnd > max_round:
                    logger.info("Max rounds reached")
                    self.skipped_test_cases.append(case)
                    break

                rd = os.path.join(case_dir, f"round_{rnd}")
                os.makedirs(rd, exist_ok=True)

                # 生成
                query_code, logics = self._gen_single_case(case)
                if not query_code:
                    self.skipped_test_cases.append(case)
                    rnd += 1
                    continue

                self._save_checker_code(query_code)
                gd = os.path.join(rd, "first_generation")
                os.makedirs(gd, exist_ok=True)
                self._save_middle_check(query_code, gd)

                # 编译
                rc, stdout, stderr, compiler_ok = compiler_code_ql(self.query_path)
                try_count = 1
                while not compiler_ok:
                    if try_count > max_compiler_trys:
                        break
                    rd2 = os.path.join(rd, f"compiler_failed_try_{try_count}")
                    os.makedirs(rd2, exist_ok=True)
                    ql = self._get_checker_code()
                    steps, api_s, doc_s, op_s = self._analyze_compiler_error(
                        str(stdout + stderr), ql)
                    repair_q = get_prompt_for_Codeql("repair_compiler_error_code").format(
                        query_code=ql,
                        compiler_error_info=str(stdout + stderr),
                        repair_steps=steps,
                        api_suggest_string=api_s,
                        doc_suggest_string=doc_s,
                        query_op_suggest_string=op_s,
                    )
                    with open(os.path.join(self.debug_prompt_dir, "repair_compiler_error_code.md"), "w") as f:
                        f.write(f"Round {rnd} try {try_count}\n" + repair_q)
                    new_code = self._llm_code("repair_compiler_error_code", repair_q, "compile-repair")
                    if new_code:
                        self._save_checker_code(new_code)
                        self._save_middle_check(new_code, rd2)
                    rc, stdout, stderr, compiler_ok = compiler_code_ql(self.query_path)
                    try_count += 1

                if not compiler_ok:
                    rnd += 1
                    continue

                # 运行
                fd = os.path.join(rd, "final_checker")
                os.makedirs(fd, exist_ok=True)
                self._save_middle_check(self._get_checker_code(), fd)

                out = os.path.join(os.path.dirname(case.get_case_path()),
                                   f"{self.rule.get_rule_name()}_output.csv")
                db = case_path_to_database_path(case.get_case_path())
                _, wc = run_code_ql_with_query(self.query_path, db, out)

                if wc >= 1:
                    ok = True
                    checker = Checker_CodeQL(self._get_checker_code(), [case])
                    logger.info(f"Checker OK at round {rnd}")
                    return True, checker
                elif wc < 0:
                    logger.info("Run error, retry")
                else:
                    logger.info("No warning on negative case, retry")
                rnd += 1

        return False, None

    def _gen_single_case(self, case: AbstractCase):
        logics = self._llm_json(
            "logic_for_negative_case",
            get_prompt_for_Codeql("logic_for_negative_case").format(
                rule_description=self.rule.get_rule_description(),
                negative_test_case=case.get_case_code()),
            "logic")
        if not logics:
            logger.warning("LLM failed to generate logics after all retries")
            return None, []
        api_s, doc_s, op_s = self._retrieve(logics)
        logger.info("Context retrieval done")

        prompt = get_prompt_for_Codeql("checker_generation_for_negative_case").format(
            rule_description=self.rule.get_rule_description(),
            test_code=case.get_case_code(),
            logics=_make_logic_string(logics),
            reference_api=api_s, reference_doc=doc_s, reference_query_op=op_s,
            query_content=self._get_checker_code(),
        )
        with open(os.path.join(self.debug_prompt_dir, "generate_checker_with_single_case.md"), "w") as f:
            f.write(prompt)

        code = self._llm_code("checker_generation_for_negative_case", prompt, "gen-checker")
        return code, logics

    def _analyze_compiler_error(self, compiler_output: str, ql_content: str):
        query = get_prompt_for_Codeql("analyze_compiler_error").format(
            query_code=ql_content, compiler_error_info=compiler_output)
        data = self._llm_json("analyze_compiler_error", query, "analyze-error")
        api_s = doc_s = op_s = ""
        steps_str = ""
        if data:
            steps = data[0].get("repair_step", [])
            steps_str = "\n".join(str(s) for s in steps)
            hints = data[1].get("wait_retrieve_code_snippet", [])
            api_s, doc_s, op_s = self._retrieve_from_hint(hints)
        return steps_str, api_s, doc_s, op_s

    # ── checker 增强 ─────────────────────────────────────

    def _checker_augmentation(self, init_checker: AbstractChecker):
        s, f, all_ok = self._run_all(init_checker)
        init_checker.set_passed_cases(s)
        cur = init_checker

        while not all_ok:
            if not f:
                break
            for case in f[:]:
                logger.info(f"Augment: {case.get_case_path()}")
                rnd = 1
                case_ok = False
                while not case_ok:
                    if rnd > max_round:
                        f.remove(case)
                        self.skipped_test_cases.append(case)
                        break

                    code, _ = self._gen_case_with_checker(case, cur)
                    if not code:
                        f.remove(case)
                        self.skipped_test_cases.append(case)
                        break

                    self._save_checker_code(code)
                    _, stdout, stderr, compiler_ok = compiler_code_ql(self.query_path)
                    try_count = 1
                    while not compiler_ok:
                        if try_count > max_compiler_trys:
                            break
                        ql = self._get_checker_code()
                        steps, api_s, doc_s, op_s = self._analyze_compiler_error(
                            str(stdout + stderr), ql)
                        repair_q = get_prompt_for_Codeql("repair_compiler_error_code").format(
                            query_code=ql, compiler_error_info=str(stdout + stderr),
                            repair_steps=steps,
                            api_suggest_string=api_s, doc_suggest_string=doc_s,
                            query_op_suggest_string=op_s)
                        new_code = self._llm_code("repair_compiler_error_code", repair_q, "aug-repair")
                        if new_code:
                            self._save_checker_code(new_code)
                        _, stdout, stderr, compiler_ok = compiler_code_ql(self.query_path)
                        try_count += 1

                    if not compiler_ok:
                        rnd += 1
                        continue

                    out = os.path.join(os.path.dirname(case.get_case_path()),
                                       f"{self.rule.get_rule_name()}_output.csv")
                    db = case_path_to_database_path(case.get_case_path())
                    _, wc = run_code_ql_with_query(self.query_path, db, out)
                    case_ok = (wc == 0) if case.get_flag() else (wc > 0)
                    if case_ok:
                        f.remove(case)
                    rnd += 1

                if case_ok:
                    updated = self._get_checker_code()
                    cur.set_checker_code(updated)
                    s2, f2, _ = self._run_all(cur)
                    cur.set_passed_cases(s2)
                    self.rule.add_checker(Checker_CodeQL(updated, s2))
                    break

            cur.set_checker_code(self._get_checker_code())
            s, f, all_ok = self._run_all(cur)
            cur.set_passed_cases(s)

    def _gen_case_with_checker(self, case, checker):
        ql = self._get_checker_code()
        if not case.get_flag():
            logics = self._aug_logic_neg(ql, checker.get_passed_cases(), [case])
            api_s, doc_s, op_s = self._retrieve(logics)
            prompt = get_prompt_for_Codeql("augmentation_check_by_negative_case").format(
                rule_description=self.rule.get_rule_description(),
                logics=_make_logic_string(logics),
                query_check_code=ql,
                reference_api=api_s, reference_doc=doc_s, reference_query_op=op_s,
                passed_test_cases="\n\n".join(c.get_case_code() for c in checker.get_passed_cases()),
                failed_test_cases=case.get_case_code())
        else:
            logics = self._aug_logic_pos(ql, checker.get_passed_cases(), [case])
            api_s, doc_s, op_s = self._retrieve(logics)
            prompt = get_prompt_for_Codeql("augmentation_check_by_positive_case").format(
                rule_description=self.rule.get_rule_description(),
                logics=_make_logic_string(logics),
                query_check_code=ql,
                reference_api=api_s, reference_doc=doc_s, reference_query_op=op_s,
                passed_test_cases="\n\n".join(c.get_case_code() for c in checker.get_passed_cases()),
                failed_test_cases=case.get_case_code())

        label = "augment-neg" if not case.get_flag() else "augment-pos"
        with open(os.path.join(self.debug_prompt_dir, f"augment_{label}.md"), "w") as f:
            f.write(prompt)

        code = self._llm_code(
            "augmentation_check_by_negative_case" if not case.get_flag()
            else "augmentation_check_by_positive_case",
            prompt, label)
        return code, logics

    def _aug_logic_neg(self, ql, passed, failed):
        return self._llm_json("augmentation_logic_by_negative_case",
            get_prompt_for_Codeql("augmentation_logic_by_negative_case").format(
                query_check_code=ql,
                passed_test_cases="\n\n".join(c.get_case_code() for c in passed),
                failed_test_cases="\n\n".join(c.get_case_code() for c in failed)),
            "aug-logic-neg")

    def _aug_logic_pos(self, ql, passed, failed):
        return self._llm_json("augmentation_logic_by_positive_case",
            get_prompt_for_Codeql("augmentation_logic_by_positive_case").format(
                query_check_code=ql,
                passed_test_cases="\n\n".join(c.get_case_code() for c in passed),
                failed_test_cases="\n\n".join(c.get_case_code() for c in failed)),
            "aug-logic-pos")

    def _run_all(self, checker):
        ok_list, fail_list = [], []
        checker.clear_passed_cases()
        for case in self.all_test_cases:
            if self.skipped_test_cases and case in self.skipped_test_cases:
                continue
            db = case_path_to_database_path(case.get_case_path())
            if db is None:
                logger.warning(f"Skipping {case.get_case_path()}: database not found")
                continue
            out = os.path.join(os.path.dirname(case.get_case_path()),
                               f"{self.rule.get_rule_name()}_output.csv")
            _, wc = run_code_ql_with_query(self.query_path, db, out)
            ok = (wc == 0) if case.get_flag() else (wc > 0)
            if ok:
                ok_list.append(case)
                checker.add_passed_cases(case)
            else:
                fail_list.append(case)
        all_ok = len(fail_list) == 0
        logger.info(f"Run all: {len(ok_list)}/{len(self.all_test_cases)} passed")
        return ok_list, fail_list, all_ok
