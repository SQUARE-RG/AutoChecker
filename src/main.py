import json
import sys
import argparse
from config import global_config
import glob
import os
import time
import shutil
import tempfile
from copy import deepcopy
from dotenv import load_dotenv
import loguru
from entity.factory import Factory_Clang_Tidy, Factory_CodeQL
from entity.abstractProduct import AbstractRule
from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template
from help.clang_tidy_utils import get_camel_check_name
from entity.abstractProduct import AbstractCase
from generator import Clang_tidy_CheckerGenerator
from typing import List
logger = loguru.logger

DEFAULT_RULES_PATH = (
    "/root/code_check/experiment/gjb8114-all/"
    "gjb8114_clang_tidy_supported_rules.json"
)


def save_json_atomic(file_path, payload):
    """Atomically replace a JSON result so an interrupted write stays readable."""
    parent_dir = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(parent_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(file_path)}.", suffix=".tmp", dir=parent_dir
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=4)
            stream.write("\n")
        os.replace(temp_path, file_path)
    except BaseException:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


def init_logger(log_dir: str = "./logs", result_name: str = "result"):
    """Initialize the logger settings."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    logger.add(
        f"{log_dir}/{result_name}-{time_stamp}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
    )
def load_all_cpp(root_dir: str):
    # 读取指定目录下的所有 .cpp 文件内容
    pattern = os.path.join(root_dir,  "*.cpp")
    cpp_dict = {}
    for file_path in glob.glob(pattern, recursive=True):
        with open(file_path, encoding='utf-8') as f:
            cpp_dict[file_path] = f.read()
    return cpp_dict
def get_entity(factory):
    case = factory.create_case()
    checker = factory.create_checker()
    rule = factory.create_rule()
    return case, checker, rule
def get_rule_entity(factory):
    rule = factory.create_rule()
    return rule

def get_case_entity(factory):
    case = factory.create_case()
    return case

def pre_compiler_clang_tidy():
    compiler_returncode,_,_,_ = compiler_clang_tidy()
    return compiler_returncode
def save_final_checkers(rule_name,rule_result_dir,plateform: str):
    if(plateform == "clang-tidy"):
        ruler_checker_cpp = global_config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".cpp"
        ruler_checker_h = global_config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".h"
        final_checker_result_dir = rule_result_dir + "final_checker/"
        os.makedirs(final_checker_result_dir, exist_ok=True)
        shutil.copy(ruler_checker_cpp,final_checker_result_dir)
        shutil.copy(ruler_checker_h,final_checker_result_dir)
        logger.info(f"最终checker已保存到: {final_checker_result_dir}")

def process_rule_info(rule_info,plateform: str):
    Case_List = []
    plateform_factory_map = {
        "clang-tidy": Factory_Clang_Tidy,
        "codeql": Factory_CodeQL,
    }
    factory_class = plateform_factory_map.get(plateform)
    if not factory_class:
        raise ValueError(f"Unsupported plateform: {plateform}")

    factory = factory_class()

    logger.info(f"Using factory: {factory_class.__name__}")

    rule =get_rule_entity(factory)

    logger.info(f"Using rule: {rule.__class__.__name__}")

    rule_name = rule_info['main_title']
    rule_description = rule_info['description']
    rule_test_path = rule_info['rule_test_path']

    print(rule_name)

    rule.rule_name = rule_name
    rule.rule_description = rule_description
    rule.rule_test_path = rule_test_path
    rule.rule_category = rule_info['category']

    sources = load_all_cpp(rule_test_path)
    negative_case_count =0
    positive_case_count =0
    for test_case_file_path, content in sources.items(): 
        case = get_case_entity(factory)
        case.case_code = content
        case.case_description = f"Test case for {rule_name} in {test_case_file_path}"

        if "CHECK-MESSAGES" in content:
            case.case_flag = False
            negative_case_count +=1
        else:
            case.case_flag = True
            positive_case_count +=1
            # print("负例")
        case.case_path = test_case_file_path         
        Case_List.append(case)
    rule_info['negative_case_amount'] = negative_case_count
    rule_info['positive_case_amount'] = positive_case_count
    print(f"负例数量： {negative_case_count}")
                
    return rule,Case_List
def analyze(success_case_list: List[AbstractCase], all_case_list: List[AbstractCase]):
    check_success_negative =0
    check_failed_negative =0
    for case in all_case_list:
        if case in success_case_list:
            if case.get_flag() == False:
                check_success_negative +=1
        else:
            if case.get_flag() == False:
                check_failed_negative +=1
    return check_success_negative,check_failed_negative
        
    
def get_checker_generator(plateform: str,rule:AbstractRule,all_Test_Case_List: List[AbstractCase]=None,skipped_Test_Cases: List[AbstractCase]=None,rule_result_dir:str=""):
    if plateform == "clang-tidy":
        checker_generator = Clang_tidy_CheckerGenerator(rule, all_Test_Case_List, skipped_Test_Cases, rule_result_dir)
        return checker_generator
    return None


def empty_usage(rule_name: str) -> dict:
    return {
        "rule_name": rule_name,
        "llm_calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "cost_breakdown": {"input_cost": 0.0, "output_cost": 0.0},
        "calls": [],
    }


def load_checkpoint(rule_data: dict, aggregate_result_path: str, resume: bool) -> dict:
    """Load prior per-rule results while retaining the current input ordering."""
    result = {"data": {package: [] for package in rule_data["data"]}}
    if not resume or not os.path.exists(aggregate_result_path):
        return result

    with open(aggregate_result_path, "r", encoding="utf-8") as stream:
        existing = json.load(stream)
    existing_data = existing.get("data", {})
    for package, source_rules in rule_data["data"].items():
        valid_ids = {item["rule_id"] for item in source_rules}
        result["data"][package] = [
            deepcopy(item)
            for item in existing_data.get(package, [])
            if item.get("rule_id") in valid_ids and "issuccess" in item
        ]
    return result


def upsert_completed_rule(
    completed_rule_data: dict,
    rule_data: dict,
    rule_package: str,
    completed_rule: dict,
) -> None:
    """Insert or replace one checkpoint entry and restore source rule ordering."""
    existing = {
        item["rule_id"]: item
        for item in completed_rule_data["data"].setdefault(rule_package, [])
    }
    existing[completed_rule["rule_id"]] = completed_rule
    completed_rule_data["data"][rule_package] = [
        existing[item["rule_id"]]
        for item in rule_data["data"][rule_package]
        if item["rule_id"] in existing
    ]


def checker_template_exists(rule_name: str) -> bool:
    checker_base = global_config["checker"]["checker_path"] + get_camel_check_name(rule_name)
    return os.path.exists(checker_base + ".cpp") or os.path.exists(checker_base + ".h")


def should_skip_checkpoint(entry: dict, retry_failed: bool) -> bool:
    status = str(entry.get("issuccess", "")).lower()
    if status == "true":
        return True
    if status == "false" and not retry_failed:
        return True
    return False


def main(
    plateform: str = "clang-tidy",
    rules_path: str = DEFAULT_RULES_PATH,
    resume: bool = False,
    retry_failed: bool = False,
    start_rule_id: str = None,
):
    # 初始化日志
    init_logger()
    result_dir = global_config['result']['result_dir']
    os.makedirs(result_dir, exist_ok=True)
    aggregate_result_path = os.path.join(result_dir, "checker_generation_result.json")
    with open(rules_path, 'r', encoding="utf-8") as f:
        rule_data = json.load(f)
    all_rule_ids = {
        item["rule_id"]
        for rules in rule_data["data"].values()
        for item in rules
    }
    if start_rule_id is not None and start_rule_id not in all_rule_ids:
        raise ValueError(f"起始规则不存在: {start_rule_id}")

    completed_rule_data = load_checkpoint(rule_data, aggregate_result_path, resume)
    completed_by_id = {
        item["rule_id"]: item
        for rules in completed_rule_data["data"].values()
        for item in rules
    }
    if resume:
        logger.info(
            f"断点续跑已启用，已加载{len(completed_by_id)}条规则结果: "
            f"{aggregate_result_path}"
        )

    start_reached = start_rule_id is None
    for rule_package,rule_list in rule_data['data'].items():
        for rule_info in rule_list:
            rule_id = rule_info["rule_id"]
            rule_name = rule_info["main_title"]
            if not start_reached:
                if rule_id != start_rule_id:
                    continue
                start_reached = True

            checkpoint_entry = completed_by_id.get(rule_id)
            if resume and checkpoint_entry and should_skip_checkpoint(
                checkpoint_entry, retry_failed
            ):
                logger.info(
                    f"跳过已有结果，规则ID={rule_id}，规则名={rule_name}，"
                    f"issuccess={checkpoint_entry.get('issuccess')}"
                )
                continue

            rule_result_dir = os.path.join(result_dir, rule_name) + "/"
            start = time.perf_counter()
            stage = "prepare_rule"
            rule = None
            Case_List = []
            checker_generator = None
            template_created = False
            environment_restore_failed = False
            current_result = deepcopy(rule_info)
            try:
                rule, Case_List = process_rule_info(current_result, plateform)
                if os.path.exists(rule_result_dir):
                    shutil.rmtree(rule_result_dir)
                os.makedirs(rule_result_dir, exist_ok=True)

                stage = "cleanup_stale_template"
                if checker_template_exists(rule_name):
                    logger.warning(f"发现上次中断残留的Checker模板，先清理: {rule_name}")
                    if remove_Checker_Template(checker_name=rule_name) != 0:
                        raise RuntimeError("清理上次中断残留的Checker模板失败")

                stage = "pre_compile"
                if pre_compiler_clang_tidy() != 0:
                    raise RuntimeError("预编译clang-tidy失败")

                stage = "create_template"
                if pre_Generate_Checker_Template(checker_name=rule_name) != 0:
                    raise RuntimeError("生成Checker模板失败")
                template_created = True
                logger.info(f"成功生成Checker模板，规则名：{rule_name}")

                stage = "generate_checker"
                checker_generator = get_checker_generator(
                    plateform,
                    rule,
                    all_Test_Case_List=Case_List,
                    skipped_Test_Cases=None,
                    rule_result_dir=rule_result_dir,
                )
                checkers_list = checker_generator.generate_checker()
                if not checkers_list:
                    raise RuntimeError("Checker生成流程未返回有效Checker")

                stage = "save_final_checker"
                save_final_checkers(rule_name, rule_result_dir, plateform)
                final_checker = checkers_list[-1]
                sucess_case_list = final_checker.get_passed_cases()
                sucess_case_path_list = [case.get_case_path() for case in sucess_case_list]
                failed_case_path_list = [
                    case.get_case_path()
                    for case in Case_List
                    if case.get_case_path() not in sucess_case_path_list
                ]
                check_success_negative, check_failed_negative = analyze(
                    sucess_case_list, Case_List
                )
                current_result.update({
                    "issuccess": "True",
                    "performance": f"{len(sucess_case_list)}/{len(Case_List)}",
                    "success_case_list": sucess_case_path_list,
                    "failed_case_list": failed_case_path_list,
                    "negative_case_analysis": {
                        "check_success_negative": check_success_negative,
                        "check_failed_negative": check_failed_negative,
                    },
                })
                logger.info(
                    f"最终生成的Checker通过的测试用例数量:"
                    f"{len(sucess_case_list)}/{len(Case_List)}"
                )
            except Exception as exc:
                logger.exception(
                    f"规则处理失败，记录失败后继续。规则ID={rule_id}，"
                    f"规则名={rule_name}，阶段={stage}"
                )
                current_result.update({
                    "issuccess": "False",
                    "performance": f"0/{len(Case_List)}",
                    "failure_stage": stage,
                    "failure_type": type(exc).__name__,
                    "failure_reason": str(exc),
                })
            finally:
                if template_created or checker_template_exists(rule_name):
                    if remove_Checker_Template(checker_name=rule_name) != 0:
                        logger.error(f"清理Checker模板失败，规则名：{rule_name}")
                        environment_restore_failed = True
                    else:
                        logger.info(f"已删除Clang仓库中的Checker，规则名：{rule_name}")
                # Ensure one failed rule cannot leave the shared LLVM tree in a
                # state that corrupts all subsequent rules.
                _, _, _, restored = compiler_clang_tidy()
                if not restored:
                    logger.critical(f"清理后clang-tidy编译失败，停止批处理，规则名：{rule_name}")
                    environment_restore_failed = True

            usage = (
                checker_generator.get_usage_stats()
                if checker_generator is not None
                else empty_usage(rule_name)
            )
            current_result['usage'] = usage
            end = time.perf_counter()
            current_result['time'] = f"{end - start:.2f}"
            logger.info(f"规则 {rule_name} 的Checker生成总共耗时: {end - start:.2f} 秒")
            # 输出 LLM 用量统计
            logger.info("=" * 50)
            logger.info(f"RULE USAGE: {usage['rule_name']}")
            logger.info(f"  LLM calls:        {usage['llm_calls']}")
            logger.info(f"  Prompt tokens:    {usage['prompt_tokens']}")
            logger.info(f"  Completion tokens:{usage['completion_tokens']}")
            logger.info(f"  Cached tokens:    {usage['cached_tokens']}")
            logger.info(f"  Total tokens:     {usage['total_tokens']}")
            logger.info(f"  Total cost:       ¥{usage['total_cost']:.6f}")
            logger.info(f"  Input cost:       ¥{usage['cost_breakdown']['input_cost']:.6f}")
            logger.info(f"  Output cost:      ¥{usage['cost_breakdown']['output_cost']:.6f}")
            logger.info("=" * 50)

            # 每条规则单独保存，同时增量更新已完成规则的汇总文件。
            completed_rule = deepcopy(current_result)
            per_rule_result_path = os.path.join(
                rule_result_dir, "checker_generation_result.json"
            )
            save_json_atomic(
                per_rule_result_path,
                {"data": {rule_package: [completed_rule]}},
            )
            upsert_completed_rule(
                completed_rule_data, rule_data, rule_package, completed_rule
            )
            completed_by_id[rule_id] = completed_rule
            save_json_atomic(aggregate_result_path, completed_rule_data)
            logger.info(
                f"规则结果已保存: {per_rule_result_path}; 汇总结果已更新: {aggregate_result_path}"
            )

            if environment_restore_failed:
                raise RuntimeError(
                    f"规则{rule_name}清理后clang-tidy环境未恢复，"
                    "已保存检查点，停止批处理"
                )
        
    # 保存合并后的检查点；不要用原始输入覆盖已有执行结果。
    save_json_atomic(aggregate_result_path, completed_rule_data)
    logger.info(f"全部规则结果已保存: {aggregate_result_path}")
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate clang-tidy checkers")
    parser.add_argument("--platform", default="clang-tidy")
    parser.add_argument("--rules", default=DEFAULT_RULES_PATH)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--start-rule-id")
    args = parser.parse_args()
    main(
        plateform=args.platform,
        rules_path=args.rules,
        resume=args.resume or args.retry_failed,
        retry_failed=args.retry_failed,
        start_rule_id=args.start_rule_id,
    )
    
