from typing import List
from entity.abstractProduct import AbstractCase
from loguru import logger
from config import global_config as config
import subprocess
from collections import OrderedDict
import re
import json
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

def select_negative_case(cases: list[AbstractCase], skipped_cases: list[AbstractCase]) -> AbstractCase:
        logger.info("Selecting a negative test case...")
        logger.info(f"当前skipped list 数量：{len(skipped_cases)}")
        if skipped_cases is None:
            skipped_cases = []
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
    print("AST节点种类:", case_ast_node_list)
    print("AST节点数量:", len(case_ast_node_list))
    print("AST节点示例:", case_ast_node_list[:10])  # 打印前10个节点种类

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


        


def get_most_similar_astMatcher_and_class_struct(self, node:list, logics_json):
    logic_for_registerMatchers,logic_for_check = get_logic_json(logics_json)
    for step in logic_for_registerMatchers:
        logger.info(f"Logic for registerMatchers step: {step}")
        pass
    