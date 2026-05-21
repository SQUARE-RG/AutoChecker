import os
from typing import List
from entity.abstractProduct import AbstractCase
from loguru import logger
from config import global_config as config
import subprocess
from collections import OrderedDict
import re
import json

from retriever.retrieve_from_astMatchers import get_related_astMatchers
from retriever.retrieve_from_astMatchers_meta_op import get_related_astMatchers_meta_op
from retriever.retrieve_from_check_op import get_related_check_op
from retriever.retrieve_from_ast_api import get_related_ast_api
from entity.concreteProduct_Clang_Tidy import Case_Clang_Tidy, Rule_Clang_Tidy
# Clang tidy check name utils
#只适用于clang tidy的checker生成过程
def get_camel_name(check_name):
    return "".join(map(lambda elem: elem.capitalize(), check_name.split("-")))


def get_camel_check_name(check_name):
    return get_camel_name(check_name) + "Check"

def count_negative_cases(Case_list: List[AbstractCase]=None):
    if Case_list is None:
        return 0
    negative_cases = [case for case in Case_list if not case.get_flag()]
    return len(negative_cases)

def select_negative_case(cases: List[AbstractCase], skipped_cases: List[AbstractCase]):
        logger.info("Selecting a negative test case...")
        
        if skipped_cases is None:
            skipped_cases = []
        logger.info(f"当前skipped list 数量：{len(skipped_cases)}")
        for case in cases:
            flag = case.get_flag()
            if not flag and case not in skipped_cases:
                return case
        return None
def parse_and_deduplicate_ast_nodes(ast_content):
    """
    解析 Clang AST 文件内容，提取所有节点并去重
    
    参数:
        ast_content: AST 文件的完整文本内容
        
    返回:
        list: 去重后的节点列表，每个节点包含类型和地址
    """
    # 使用有序字典存储节点，地址作为键，类型作为值（自动去重）
    unique_nodes = OrderedDict()
    
    # 正则表达式匹配 AST 节点
    node_pattern = re.compile(
        r'^(?P<indent>[ |`-]*)'  # 缩进部分
        r'(?P<node_type>\w+)'    # 节点类型
        r'\s+(?P<address>0x[0-9a-f]+)'  # 节点地址
    )
    
    # 逐行解析 AST
    for line in ast_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 匹配节点行
        match = node_pattern.match(line)
        if match:
            node_type = match.group('node_type')
            address = match.group('address')
            
            # 使用地址作为唯一标识（自动去重）
            if address not in unique_nodes:
                unique_nodes[address] = node_type
    
    # 转换为节点列表格式
    # node_list = [{"type": node_type, "address": address} 
    #              for address, node_type in unique_nodes.items()]
    node_list = [node_type for node_type in unique_nodes.values() ]
    return node_list

def get_Case_AST(case_path):
    # case_code = case.get_case_code()
    # case_path = case.get_case_path()
    cmd = [config['compiler']['build_bin_clang'],
               '-Xclang','-ast-dump','-fsyntax-only' ,str(case_path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True)
    if result.returncode != 0:
        logger.error(f"Error generating AST for case {case_path}: {result.stderr}")
        logger.error(f"Error runing command: {' '.join(cmd)}")
        return None,None,None
    case_ast_txt = result.stdout 
    # 按行处理并提取从 "`-" 开始的节点部分
    lines = case_ast_txt.splitlines(keepends=True)
    if not lines:
        content = ""
        case_ast_json = ""
        case_ast_node_list = []
        return content, case_ast_json, case_ast_node_list
    
    found_dash_line = False
    output_lines = [lines[0]]
    for line in lines[1:]:
        if line.startswith("`-"):
            found_dash_line = True
        if found_dash_line:
            output_lines.append(line)

    # 仅保存最终清洗后的文件
    with open("./selected_case_ast_cleaned1.txt","w",encoding='utf-8') as output_file:
        output_file.writelines(output_lines)

    content = "".join(output_lines)

    case_ast_json = ''
    case_ast_node_list = parse_and_deduplicate_ast_nodes(content)
    case_ast_node_list = list(set(case_ast_node_list))  # 去重
    logger.debug("AST节点种类: " + str(case_ast_node_list))
    logger.debug("AST节点数量: " + str(len(case_ast_node_list)))
    logger.debug("AST节点示例: " + str(case_ast_node_list[:10]))  # 打印前10个节点种类

    return content,case_ast_json,case_ast_node_list
# 去除编号前缀的函数
def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)
def get_logic_json(logics_json):
    logic_for_registerMatchers=[]
    logic_for_check = []
    # import json
# logic = json.loads(response)
# print("Logic for registerMatchers:")
# for step in logic[0]["logic_registerMatchers"]:
#     print("-", step)
# print("\nLogic for check:")
# for step in logic[0]["logic_check"]:
#     print("-", step)  
    for step in logics_json[0]["logic_registerMatchers"]:
        logic_for_registerMatchers.append(remove_number_prefix(step))
    for step in logics_json[0]["logic_check"]:
        logic_for_check.append(remove_number_prefix(step))
    return logic_for_registerMatchers,logic_for_check
def get_repair_steps_string(repair_steps):
    repair_steps_string =""
    # 每个step前加一个序号
    for i, step in enumerate(repair_steps, 1):
        repair_steps_string += f"{i}. {step}\n" 
    return repair_steps_string
def get_logic_string(logics_json):
    logic_string= '**logic for registerMatchers**:\n'
    for step in logics_json[0]["logic_registerMatchers"]:
        logic_string += step + "\n"
    logic_string += "**logic for check**:\n"
    for step in logics_json[0]["logic_check"]:
        logic_string += step + "\n"
    return logic_string
def get_most_similar_astMatcher_and_class_struct(node:list, logics_json):
    astMatch_suggest_string= '' 
    class_struct_suggest_string = ''
    logic_for_registerMatchers,logic_for_check = get_logic_json(logics_json)

    related_astMatchers= get_related_astMatchers(logic_for_registerMatchers)
    # logger.info(f"相关的AST Matchers建议:\n{related_astMatchers}")
    related_astMatchers_meta_op= get_related_astMatchers_meta_op(logic_for_registerMatchers)
    # logger.info(f"相关的AST Matchers Meta Op建议:\n{related_astMatchers_meta_op}")
    for a in related_astMatchers:
        astMatch_suggest_string += a + "\n"
    for b in related_astMatchers_meta_op:
        astMatch_suggest_string += b + "\n"


    related_check_op= get_related_check_op(logic_for_check)
    # logger.info(f"相关的Check Op建议:\n{related_check_op}")
    for c in related_check_op:
        class_struct_suggest_string += c + "\n" 
    related_ast_api= get_related_ast_api(logic_for_check)
    # logger.info(f"相关的AST API建议:\n{related_ast_api}")
    for d in related_ast_api:
        class_struct_suggest_string += d + "\n" 
    return astMatch_suggest_string,class_struct_suggest_string

def get_suggest_string_from_hint(hint):
    result = ''
    related_astMatchers= get_related_astMatchers(hint)
    # logger.info(f"相关的AST Matchers建议:\n{related_astMatchers}")
    related_astMatchers_meta_op= get_related_astMatchers_meta_op(hint)
    # logger.info(f"相关的AST Matchers Meta Op建议:\n{related_astMatchers_meta_op}")
    for a in related_astMatchers:
        result += a + "\n"
    for b in related_astMatchers_meta_op:
        result += b + "\n"


    related_check_op= get_related_check_op(hint)
    # logger.info(f"相关的Check Op建议:\n{related_check_op}")
    for c in related_check_op:
        result += c + "\n" 
    related_ast_api= get_related_ast_api(hint)
    # logger.info(f"相关的AST API建议:\n{related_ast_api}")
    for d in related_ast_api:
        result += d + "\n" 
    return result
# def tk(logic_for_registerMatchers,logic_for_check):
#     astMatch_suggest_string= '' 
#     class_struct_suggest_string = ''
#     related_astMatchers= get_related_astMatchers(logic_for_registerMatchers)
#     logger.info(f"相关的AST Matchers建议:\n{related_astMatchers}")
#     related_astMatchers_meta_op= get_related_astMatchers_meta_op(logic_for_registerMatchers)
#     logger.info(f"相关的AST Matchers Meta Op建议:\n{related_astMatchers_meta_op}")
#     for a in related_astMatchers:
#         astMatch_suggest_string += a + "\n"
#     for b in related_astMatchers_meta_op:
#         astMatch_suggest_string += b + "\n"


#     related_check_op= get_related_check_op(logic_for_check)
#     logger.info(f"相关的Check Op建议:\n{related_check_op}")
#     for c in related_check_op:
#         class_struct_suggest_string += c + "\n" 
#     related_ast_api= get_related_ast_api(logic_for_check)
#     logger.info(f"相关的AST API建议:\n{related_ast_api}")
#     for d in related_ast_api:
#         class_struct_suggest_string += d + "\n" 
#     return astMatch_suggest_string,class_struct_suggest_string


# def parse_cpp_h_code_from_answer(answer: str):
#     """返回第一个 ```cpp ... ``` 中的纯代码，若无则 None。"""
#     # 定义正则表达式模式
#     cpp_pattern = r"checker_cpp:\s*```cpp\s*(.*?)\s*```"
#     h_pattern = r"checker_h:\s*```cpp\s*(.*?)\s*```"
#     # 使用 re.DOTALL 使 . 匹配包括换行符在内的所有字符
#     cpp_match = re.search(cpp_pattern, answer, re.DOTALL)
#     h_match = re.search(h_pattern, answer, re.DOTALL)
    
#     # 提取代码内容
#     checker_cpp_code = cpp_match.group(1).strip() if cpp_match else None
#     checker_h_code = h_match.group(1).strip() if h_match else None
#     return checker_cpp_code,checker_h_code


# ...existing code...
def parse_cpp_h_code_from_answer(answer: str):
    """
    更鲁棒的解析：优先按标签匹配 `checker_cpp:` / `checker_h:` 后的 ```cpp``` 代码块；
    若未命中则退化为取回答中出现的前两个 ```cpp``` 代码块作为 cpp 和 h。
    """
    # 优先按带标签的 code fence 提取（支持 cpp 或 c++）
    cpp_pattern = r"checker_cpp\s*:\s*```(?:cpp|c\+\+)\s*(.*?)\s*```"
    h_pattern = r"checker_h\s*:\s*```(?:cpp|c\+\+)\s*(.*?)\s*```"
    cpp_match = re.search(cpp_pattern, answer, re.IGNORECASE | re.DOTALL)
    h_match = re.search(h_pattern, answer, re.IGNORECASE | re.DOTALL)

    checker_cpp_code = cpp_match.group(1).strip() if cpp_match else None
    checker_h_code = h_match.group(1).strip() if h_match else None

    # 回退：如果没有按标签找到，尝试抓取所有 ```cpp``` code block，并用前两个作为 cpp/h
    if not checker_cpp_code or not checker_h_code:
        blocks = re.findall(r"```(?:cpp|c\+\+)\s*(.*?)\s*```", answer, re.IGNORECASE | re.DOTALL)
        if blocks:
            if not checker_cpp_code and len(blocks) >= 1:
                checker_cpp_code = blocks[0].strip()
            if not checker_h_code and len(blocks) >= 2:
                checker_h_code = blocks[1].strip()

    return checker_cpp_code, checker_h_code
# ...existing code...

def save_checker_code(checker_cpp: str, checker_h:str,rule_name: str):
    """将生成的检查器代码保存到指定路径。"""
    ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".cpp"
    with open(ruler_checker_cpp, 'w', encoding='utf-8') as file:
        file.write(checker_cpp)
    ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".h"
    with open(ruler_checker_h, 'w', encoding='utf-8') as file:
        file.write(checker_h)
    return ""

def get_checker_code(rule_name: str):

    """读取指定规则名称的检查器代码。"""
    ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".cpp"    
    with open(ruler_checker_cpp, 'r', encoding='utf-8') as file:
        checker_code = file.read()
    ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".h"
    with open(ruler_checker_h, 'r', encoding='utf-8') as file:
        checker_h = file.read()
    return checker_code,checker_h

def save_middle_check(checker_cpp: str, checker_h:str,round_dir: str):
    """将生成的中间检查器代码保存到指定路径。"""
    ruler_checker_cpp = os.path.join(round_dir, "checker.cpp")
    with open(ruler_checker_cpp, 'w', encoding='utf-8') as file:
        file.write(checker_cpp)
    ruler_checker_h = os.path.join(round_dir, "checker.h")
    with open(ruler_checker_h, 'w', encoding='utf-8') as file:
        file.write(checker_h)
    return ""


# ============================================================
# SDK 适配器：将 SDK 类型转换为内部实体类
# ============================================================

def adapt_sdk_test_cases(test_cases: list, temp_dir: str) -> list:
    """
    将 SDK 的 TestCaseData 列表转换为内部 Case_Clang_Tidy 列表。

    TestCaseData.compliant=True  → 正例（合规代码，checker 不应报警）
    TestCaseData.compliant=False → 负例（违规代码，checker 应报警）

    同时将 code 写入 temp_dir 下的 .cpp 文件，因为 clang-tidy 需要实际文件路径。
    """
    case_list = []
    os.makedirs(temp_dir, exist_ok=True)
    for tc in test_cases:
        file_path = os.path.join(temp_dir, tc.file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(tc.code)
        case = Case_Clang_Tidy(
            case_code=tc.code,
            case_description=f"SDK test case: {tc.file_name}",
            case_flag=tc.compliant,
            case_path=file_path
        )
        case_list.append(case)
    return case_list


def adapt_sdk_input_to_entities(rule_name: str, rule_description: str,
                                 test_cases: list, temp_test_dir: str = None):
    """
    从 SDK 输入创建内部实体：Rule_Clang_Tidy + List[Case_Clang_Tidy]。
    返回 (rule, case_list) 元组。
    """
    if temp_test_dir is None:
        temp_test_dir = config['checker']['temp_test_dir'] + f"sdk_{rule_name}/"
    rule = Rule_Clang_Tidy(
        rule_name=rule_name,
        rule_description=rule_description,
        rule_test_path=temp_test_dir,
        rule_category="ucassaat"
    )
    case_list = adapt_sdk_test_cases(test_cases, temp_test_dir)
    return rule, case_list