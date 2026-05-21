import json
import sys
from config import global_config
import glob
import os
import time
import shutil
from dotenv import load_dotenv
import loguru
from entity.factory import Factory_Clang_Tidy, Factory_CodeQL
from entity.abstractProduct import AbstractRule
from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template,setup_sdk_test_temp_dir,cleanup_sdk_temp_dir
from help.clang_tidy_utils import get_camel_check_name,adapt_sdk_input_to_entities
from entity.abstractProduct import AbstractCase
from generator import Clang_tidy_CheckerGenerator
from typing import List
from client import AutoCheckerClient
from types import GeneratorStatus, LogLevel
from llm_interface.llm_provider import get_llm_client_from_config
autoCheckerClient= AutoCheckerClient()
logger = loguru.logger
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
        # logger.info(f"最终checker已保存到: {final_checker_result_dir}")

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

    rule =get_rule_entity(factory)


    rule_name = rule_info['main_title']
    rule_description = rule_info['description']
    rule_test_path = rule_info['rule_test_path']

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
        case.case_path = test_case_file_path         
        Case_List.append(case)
    rule_info['negative_case_amount'] = negative_case_count
    rule_info['positive_case_amount'] = positive_case_count
    # print(f"负例数量： {negative_case_count}")
                
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

def main_sdk():
    """SDK 模式入口：从 stdin 读取 GeneratorInput，通过 stdout 发送进度/产物/状态。"""
    init_logger(result_name="sdk_generator")
    result_dir = global_config['result']['result_dir']

    # 1. 从 stdin 读取 SDK 输入
    autoCheckerClient.log("Waiting for GeneratorInput from stdin...", level=LogLevel.INFO)
    sdk_input = autoCheckerClient.get_input()
    autoCheckerClient.log(f"Received input for rule: {sdk_input.rule_name}", level=LogLevel.INFO)

    rule_name = sdk_input.rule_name
    rule_description = sdk_input.rule_description
    language = sdk_input.language
    framework = sdk_input.framework

    # 2. 框架检查
    if framework.value != "clang-tidy":
        autoCheckerClient.log(f"Unsupported framework: {framework.value}. Only clang-tidy is supported.", level=LogLevel.ERROR)
        autoCheckerClient.send_status(status=GeneratorStatus.FAILED, error_message=f"Unsupported framework: {framework.value}")
        sys.exit(1)

    # 3. 创建 SDK LLM client
    autoCheckerClient.report_progress(stage="Initializing LLM client")
    sdk_llm_client = get_llm_client_from_config(
        api_key=sdk_input.api_key,
        base_url=sdk_input.base_url,
        model_name=sdk_input.model_name,
    )
    autoCheckerClient.log(f"LLM client initialized: model={sdk_input.model_name}", level=LogLevel.INFO)

    # 4. 转换 SDK 输入为内部实体
    autoCheckerClient.report_progress(stage="Preparing test cases")
    temp_test_dir = setup_sdk_test_temp_dir(rule_name)
    rule, case_list = adapt_sdk_input_to_entities(
        rule_name=rule_name,
        rule_description=rule_description,
        test_cases=sdk_input.test_cases,
        temp_test_dir=temp_test_dir,
    )
    negative_count = sum(1 for c in case_list if not c.get_flag())
    positive_count = sum(1 for c in case_list if c.get_flag())
    autoCheckerClient.log(
        f"Prepared {len(case_list)} test cases ({positive_count} positive, {negative_count} negative)",
        level=LogLevel.INFO
    )

    # 5. 创建结果目录
    rule_result_dir = result_dir + rule.rule_name + "/"
    if os.path.exists(rule_result_dir):
        shutil.rmtree(rule_result_dir)
    os.makedirs(rule_result_dir, exist_ok=True)

    # 6. 预编译 clang-tidy
    autoCheckerClient.report_progress(stage="Compiling clang-tidy")
    pre_compiler_returncode = pre_compiler_clang_tidy()
    if pre_compiler_returncode != 0:
        autoCheckerClient.log("Pre-compilation of clang-tidy failed.", level=LogLevel.ERROR)
        autoCheckerClient.send_status(status=GeneratorStatus.FAILED, error_message="Pre-compilation failed")
        cleanup_sdk_temp_dir(rule_name)
        sys.exit(1)

    # 7. 生成 checker 模板
    autoCheckerClient.report_progress(stage="Generating checker template")
    pre_generate_returncode = pre_Generate_Checker_Template(checker_name=rule.get_rule_name())
    if pre_generate_returncode != 0:
        autoCheckerClient.log(f"Failed to generate checker template for rule: {rule.get_rule_name()}", level=LogLevel.ERROR)
        autoCheckerClient.send_status(status=GeneratorStatus.FAILED, error_message="Template generation failed")
        cleanup_sdk_temp_dir(rule_name)
        sys.exit(1)

    # 8. 创建生成器并运行（传入 SDK LLM client 和 SDK communication client）
    start = time.perf_counter()
    autoCheckerClient.report_progress(stage="Generating checker")
    checker_generator = Clang_tidy_CheckerGenerator(
        rule,
        all_Test_Case_List=case_list,
        skipped_Test_Cases=None,
        rule_result_dir=rule_result_dir,
        llm_client=sdk_llm_client,
        sdk_client=autoCheckerClient,
    )
    try:
        checkers_list = checker_generator.generate_checker()
    except Exception as exc:
        autoCheckerClient.log(f"Unexpected error during checker generation: {str(exc)}", level=LogLevel.ERROR)
        autoCheckerClient.send_status(
            status=GeneratorStatus.FAILED,
            error_message=f"Unexpected error: {str(exc)}"
        )
        remove_Checker_Template(checker_name=rule.get_rule_name())
        compiler_clang_tidy()
        cleanup_sdk_temp_dir(rule_name)
        sys.exit(1)

    # 9. 处理结果
    save_final_checkers(rule.get_rule_name(), rule_result_dir, "clang-tidy")
    end = time.perf_counter()
    elapsed = end - start

    if checkers_list is None:
        autoCheckerClient.log(f"Checker generation failed for rule: {rule_name}", level=LogLevel.ERROR)
        autoCheckerClient.send_status(
            status=GeneratorStatus.FAILED,
            error_message=f"Generation failed after {elapsed:.2f}s"
        )
    else:
        final_checker = checkers_list[-1]
        passed = len(final_checker.get_passed_cases())
        total = len(case_list)
        autoCheckerClient.log(
            f"Checker generated successfully: {passed}/{total} test cases passed in {elapsed:.2f}s",
            level=LogLevel.INFO
        )
        autoCheckerClient.send_status(status=GeneratorStatus.COMPLETED)

    # 10. 清理
    remove_Checker_Template(checker_name=rule.get_rule_name())
    compiler_clang_tidy()
    cleanup_sdk_temp_dir(rule_name)
    autoCheckerClient.log(f"Cleanup completed for rule: {rule_name}", level=LogLevel.INFO)


def main(plateform: str = "clang-tidy"):
    # 初始化日志
    init_logger()
    result_dir = global_config['result']['result_dir']
   
    # os.makedirs(result_dir, exist_ok=True)
    with open("/root/code_check/clang_tidy_sub_checker/jgb8114_single_rules.json", 'r') as f:
        rule_data = json.load(f)
    for rule_package,rule_list in rule_data['data'].items():
        for rule_info in rule_list:
            autoCheckerClient.report_progress(stage=f"Processing rule: {rule_info['main_title']}")
            autoCheckerClient.log(f"Starting processing for rule: {rule_info['main_title']}", level=LogLevel.INFO)
            rule ,Case_List = process_rule_info(rule_info,plateform)

            # 创建针对这个rule的结果目录
            rule_result_dir = result_dir + rule.rule_name + "/"
            # 清理之前的结果
            if os.path.exists(rule_result_dir):
                shutil.rmtree(rule_result_dir)
            os.makedirs(rule_result_dir, exist_ok=True)
            #事先编译clang tidy
            pre_compiler_returncode = pre_compiler_clang_tidy()
            if pre_compiler_returncode !=0:
                # logger.error("预编译clang-tidy失败，终止执行")
                autoCheckerClient.log("Pre-compilation of clang-tidy failed. Terminating execution.", level=LogLevel.ERROR)
                sys.exit(1)
            pre_generate_returncode = pre_Generate_Checker_Template(checker_name=rule.get_rule_name())
            if pre_generate_returncode !=0: 
                # logger.error(f"生成Checker模板失败，终止执行，规则名：{rule.get_rule_name()}")
                autoCheckerClient.log(f"Pre-generation of Checker template failed for rule: {rule.get_rule_name()}. Terminating execution.", level=LogLevel.ERROR)
                sys.exit(1)
            # logger.info(f"成功生成Checker模板，规则名：{rule.get_rule_name()}")
            # autoCheckerClient.log(f"Successfully generated Checker template for rule: {rule.get_rule_name()}", level=LogLevel.INFO)
            # 开启生成checker的流程
            start = time.perf_counter()
            
            checker_generator = get_checker_generator(plateform,rule,all_Test_Case_List=Case_List,skipped_Test_Cases=None,rule_result_dir= rule_result_dir)
            checkers_list = checker_generator.generate_checker()

            save_final_checkers(rule.get_rule_name(),rule_result_dir,plateform)
            if checkers_list is None:
                # logger.error(f"Checker生成失败，规则名：{rule.get_rule_name()}")
                autoCheckerClient.log(f"Checker generation failed for rule: {rule.get_rule_name()}", level=LogLevel.ERROR)
                rule_info['issuccess'] = "False"
                rule_info['performance']=f"0/{len(Case_List)}"
                remove_Checker_Template(checker_name=rule.get_rule_name())
                rule_info['total_cost'] = f"{checker_generator.get_total_cost():.6f}"
                # logger.info(f"已删除Clang仓库中的Checker，规则名：{rule.get_rule_name()}")

            else:
                # logger.info(f"生成了 {len(checkers_list)} 个Checker，规则名：{rule.get_rule_name()}")
                
                final_checker = checkers_list[-1]
                # logger.info(f"最终生成的Checker通过的测试用例数量:{len(final_checker.get_passed_cases())}/{len(Case_List)}")
                autoCheckerClient.log(f"Final generated Checker passed {len(final_checker.get_passed_cases())}/{len(Case_List)} test cases for rule: {rule.get_rule_name()}", level=LogLevel.INFO)
                rule_info['issuccess'] = "True"
                rule_info['performance']=f"{len(final_checker.get_passed_cases())}/{len(Case_List)}"
                remove_Checker_Template(checker_name=rule.get_rule_name())
                # logger.info(f"已删除Clang仓库中的Checker，规则名：{rule.get_rule_name()}")
               
                sucess_case_list = final_checker.get_passed_cases()
                sucess_case_path_list = [case.get_case_path() for case in sucess_case_list]
                rule_info['success_case_list'] = sucess_case_path_list
                failed_case_list = [case for case in Case_List if case.get_case_path() not in sucess_case_path_list]
                failed_case_path_list = [case.get_case_path() for case in failed_case_list]
                rule_info['failed_case_list'] = failed_case_path_list
                rule_info['total_cost'] = f"{checker_generator.get_total_cost():.6f}"
                check_success_negative,check_failed_negative = analyze(sucess_case_list,Case_List)
                rule_info['negative_case_analysis'] = {
                    "check_success_negative": check_success_negative,
                    "check_failed_negative": check_failed_negative
                }
            # logger.info("Checker生成完毕，结果已保存")
            autoCheckerClient.log(f"Checker generation completed for rule: {rule.get_rule_name()}. Results saved.", level=LogLevel.INFO)
            autoCheckerClient.send_status(status=GeneratorStatus.COMPLETED)
            end = time.perf_counter()
            # logger.info(f"规则 {rule.get_rule_name()} 的Checker生成总共耗时: {end - start:.2f} 秒")
            autoCheckerClient.log(f"Total time taken for Checker generation for rule: {rule.get_rule_name()}: {end - start:.2f} seconds", level=LogLevel.INFO)
            rule_info['time'] = f"{end - start:.2f}"
            #再次编译clang tidy
            compiler_clang_tidy()
        
    # 将结果保存到JSON文件
    result_file_path = rule_result_dir + "checker_generation_result.json"
    with open(result_file_path, 'w') as f:
        json.dump(rule_data, f, indent=4)
                    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AutoChecker Static Analysis Generator")
    parser.add_argument("--mode", choices=["local", "sdk"], default="local",
                        help="运行模式: local=本地文件模式, sdk=SDK stdin/stdout 模式")
    args = parser.parse_args()
    if args.mode == "sdk":
        main_sdk()
    else:
        main()
    
