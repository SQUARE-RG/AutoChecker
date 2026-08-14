"""CodeQL 多语言代码生成 — 统一入口。

用法:
    python main_codeql_uniform.py --language cpp
    python main_codeql_uniform.py --language python
"""

import argparse
import glob
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import List

# Ensure project root is in sys.path and os.getcwd() for config loading
# Works regardless of whether script is invoked from /root/code_check/ or /root/code_check/src/
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))
os.chdir(str(_project_root))

from loguru import logger

from entity.factory import Factory_CodeQL
from entity.abstractProduct import AbstractCase, AbstractRule
from config import global_config
from codeql_language_config import get_language_config, LanguageConfig
from plateform.code_ql_uniform import (
    write_qlpack,
    create_databases_for_test_cases,
    pre_generate_query_template,
)
from generator_codeql_uniform import CodeQLGeneratorUniform


def init_logger(log_dir: str = "./logs", result_name: str = "result"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    logger.add(
        f"{log_dir}/{result_name}-{time_stamp}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
    )


def load_sources(root_dir: str, extensions: List[str]) -> dict:
    """按扩展名加载测试用例，返回 {file_path: content}。"""
    sources = {}
    for ext in extensions:
        pattern = os.path.join(root_dir, f"*{ext}")
        for file_path in glob.glob(pattern):
            with open(file_path, encoding="utf-8") as f:
                sources[file_path] = f.read()
    return sources


def process_rule_info(rule_info: dict, lang_config: LanguageConfig):
    """解析规则信息，返回 (rule, case_list)。"""
    factory = Factory_CodeQL()
    rule: AbstractRule = factory.create_rule()
    rule.rule_name = rule_info["main_title"]
    rule.rule_description = rule_info["description"]
    rule.rule_test_path = rule_info["rule_test_path"]
    rule.rule_category = rule_info.get("category", "")

    sources = load_sources(rule.rule_test_path, lang_config.source_extensions)
    cases = []
    neg = pos = 0
    for path, content in sources.items():
        case: AbstractCase = factory.create_case()
        case.case_code = content
        case.case_description = f"Test case for {rule.rule_name} in {path}"
        case.case_path = path
        if "CHECK-MESSAGES" in content:
            case.case_flag = False
            neg += 1
        else:
            case.case_flag = True
            pos += 1
        cases.append(case)

    rule_info["negative_case_amount"] = neg
    rule_info["positive_case_amount"] = pos
    logger.info(f"  neg={neg}, pos={pos}")
    return rule, cases


def save_results(rule_data: dict, output_dir: str):
    path = os.path.join(output_dir, "checker_generation_result.json")
    with open(path, "w") as f:
        json.dump(rule_data, f, indent=4)


def main(language: str = "cpp", rules_path: str = None):
    init_logger()
    lang_config = get_language_config(language)
    result_dir = global_config["result"]["result_dir"]

    if rules_path is None:
        rules_path = "/root/code_check/experiment/gjb8114/rule_codeql/jgb8114_single_rules.json"

    with open(rules_path, "r") as f:
        rule_data = json.load(f)

    for rule_package, rule_list in rule_data.get("data", {}).items():
        for rule_info in rule_list:
            rule, cases = process_rule_info(rule_info, lang_config)

            # 1. 创建输出目录
            rule_result_dir = os.path.join(result_dir, "codeql", language, rule.rule_name)
            if os.path.exists(rule_result_dir):
                shutil.rmtree(rule_result_dir)
            os.makedirs(rule_result_dir, exist_ok=True)

            # 2. 生成 qlpack.yml
            write_qlpack(rule.rule_name, rule_result_dir, language)

            # 3. 为测试用例创建 database
            create_databases_for_test_cases(cases, lang_config)

            # 4. 生成 .ql 查询模板
            pre_generate_query_template(rule.rule_name, rule_result_dir, lang_config)
            logger.info(f"Query template → {rule_result_dir}/{rule.rule_name}.ql")

            # 5. 运行生成器
            logger.info(f"Starting generator for: {rule.rule_name}")
            start = time.perf_counter()
            generator = CodeQLGeneratorUniform(
                rule=rule,
                all_test_cases=cases,
                skipped_test_cases=None,
                rule_result_dir=rule_result_dir,
                lang_config=lang_config,
            )
            checkers = generator.generate_checker()

            if checkers is None:
                logger.error(f"Checker generation failed: {rule.rule_name}")
                rule_info["issuccess"] = "False"
                rule_info["performance"] = f"0/{len(cases)}"
            else:
                logger.info(f"Generated {len(checkers)} checker(s): {rule.rule_name}")
                final = checkers[-1]
                passed = len(final.get_passed_cases())
                logger.info(f"Passed: {passed}/{len(cases)}")
                rule_info["issuccess"] = "True"
                rule_info["performance"] = f"{passed}/{len(cases)}"
                rule_info["success_case_list"] = [c.get_case_path() for c in final.get_passed_cases()]
                failed = [c for c in cases if c.get_case_path() not in
                          [p.get_case_path() for p in final.get_passed_cases()]]
                rule_info["failed_case_list"] = [c.get_case_path() for c in failed]

            elapsed = time.perf_counter() - start

            # 6. 输出本规则用量统计
            usage = generator.get_usage_stats()
            logger.info("=" * 50)
            logger.info(f"RULE USAGE: {usage['rule_name']}")
            logger.info(f"  LLM calls:        {usage['llm_calls']}")
            logger.info(f"  Prompt tokens:    {usage['prompt_tokens']}")
            logger.info(f"  Completion tokens:{usage['completion_tokens']}")
            logger.info(f"  Cached tokens:    {usage['cached_tokens']}")
            logger.info(f"  Total tokens:     {usage['total_tokens']}")
            logger.info(f"  Total cost:       ¥{usage['total_cost_yuan']:.6f}")
            logger.info(f"  Elapsed:          {elapsed:.1f}s")
            logger.info("=" * 50)

            # 清理测试用例目录下残留的 _output.csv 文件
            for csv_file in glob.glob(os.path.join(rule.rule_test_path, "**/*_output.csv"), recursive=True):
                os.unlink(csv_file)

            # 写入 rule_info
            rule_info["usage"] = usage

    # 保存结果
    save_results(rule_data, os.path.join(result_dir, "codeql", language))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodeQL multi-language checker generator")
    parser.add_argument("--language", default="cpp", choices=["cpp", "python"],
                        help="Target language (default: cpp)")
    parser.add_argument("--rules", default=None,
                        help="Path to rules JSON")
    args = parser.parse_args()
    main(language=args.language, rules_path=args.rules)
