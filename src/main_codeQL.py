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
from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template
from help.clang_tidy_utils import get_camel_check_name
from entity.abstractProduct import AbstractCase
from generator import Clang_tidy_CheckerGenerator,CodeQL_CheckerGenerator
from typing import List
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

def get_checker_generator(plateform: str,rule:AbstractRule,all_Test_Case_List: List[AbstractCase]=None,skipped_Test_Cases: List[AbstractCase]=None,rule_result_dir:str=""):
    if plateform == "clang-tidy":
        checker_generator = Clang_tidy_CheckerGenerator(rule, all_Test_Case_List, skipped_Test_Cases, rule_result_dir)
        return checker_generator
    elif plateform == "codeql":
        checker_generator = CodeQL_CheckerGenerator(rule, all_Test_Case_List, skipped_Test_Cases, rule_result_dir)
        return checker_generator
    return None

def main(plateform: str = "clang-tidy"):
    # 初始化日志
    init_logger()
    result_dir = global_config['result']['result_dir']
    # os.makedirs(result_dir, exist_ok=True)
    with open("/root/code_check/clang_tidy_sub_checker/single_rule.json", 'r') as f:
        rule_data = json.load(f)
    for rule_package,rule_list in rule_data['data'].items():
        for rule_info in rule_list:
            rule ,Case_List = process_rule_info(rule_info,plateform)

            
            if plateform == "clang-tidy":
                rule_result_dir = result_dir +"clang-tidy/"+ rule.rule_name + "/"
                if os.path.exists(rule_result_dir):
                    shutil.rmtree(rule_result_dir)
                os.makedirs(rule_result_dir, exist_ok=True)
                pre_compiler_returncode = pre_compiler_clang_tidy()
                if pre_compiler_returncode !=0:
                    logger.error("预编译clang-tidy失败，终止执行")
                    sys.exit(1)
                pre_generate_returncode = pre_Generate_Checker_Template(checker_name=rule.get_rule_name())
                if pre_generate_returncode !=0: 
                    logger.error(f"生成Checker模板失败，终止执行，规则名：{rule.get_rule_name()}")
                    sys.exit(1)
                logger.info(f"成功生成Checker模板，规则名：{rule.get_rule_name()}")
                start = time.perf_counter()
            
                checker_generator = get_checker_generator(plateform,rule,all_Test_Case_List=Case_List,skipped_Test_Cases=None,rule_result_dir= rule_result_dir)
                checkers_list = checker_generator.generate_checker()

                save_final_checkers(rule.get_rule_name(),rule_result_dir,plateform)
                if checkers_list is None:
                    logger.error(f"Checker生成失败，规则名：{rule.get_rule_name()}")
                    rule_info['issuccess'] = "False"
                    rule_info['performance']=f"0/{len(Case_List)}"
                    remove_Checker_Template(checker_name=rule.get_rule_name())
                    logger.info(f"已删除Clang仓库中的Checker，规则名：{rule.get_rule_name()}")
                else:
                    logger.info(f"生成了 {len(checkers_list)} 个Checker，规则名：{rule.get_rule_name()}")
                    final_checker = checkers_list[-1]
                    logger.info(f"最终生成的Checker通过的测试用例数量:{len(final_checker.get_passed_cases())}/{len(Case_List)}")
              
                    rule_info['issuccess'] = "True"
                    rule_info['performance']=f"{len(final_checker.get_passed_cases())}/{len(Case_List)}"
                    remove_Checker_Template(checker_name=rule.get_rule_name())
                    logger.info(f"已删除Clang仓库中的Checker，规则名：{rule.get_rule_name()}")
               
                    sucess_case_list = final_checker.get_passed_cases()
                    sucess_case_path_list = [case.get_case_path() for case in sucess_case_list]
                    rule_info['success_case_list'] = sucess_case_path_list
                    failed_case_list = [case for case in Case_List if case.get_case_path() not in sucess_case_path_list]
                    failed_case_path_list = [case.get_case_path() for case in failed_case_list]
                    rule_info['failed_case_list'] = failed_case_path_list
                logger.info("Checker生成完毕，结果已保存")
                end = time.perf_counter()
                logger.info(f"规则 {rule.get_rule_name()} 的Checker生成总共耗时: {end - start:.2f} 秒")
                compiler_clang_tidy()
            elif plateform == "codeql":
                rule_result_dir = result_dir +"codeql/"+ rule.rule_name + "/"
                if os.path.exists(rule_result_dir):
                    shutil.rmtree(rule_result_dir)
                os.makedirs(rule_result_dir, exist_ok=True)
                logger.info("开始生成CodeQL的Checker")
                start = time.perf_counter()
                checker_generator = get_checker_generator(plateform,rule,all_Test_Case_List=Case_List,skipped_Test_Cases=None,rule_result_dir= rule_result_dir)
                checkers_list = checker_generator.generate_checker()

                
    # 将结果保存到JSON文件
    result_file_path = rule_result_dir + "checker_generation_result.json"
    with open(result_file_path, 'w') as f:
        json.dump(rule_data, f, indent=4)
                    
if __name__ == "__main__":
    main()
    
