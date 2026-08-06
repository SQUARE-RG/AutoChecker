
import os
from typing import List
from entity.abstractProduct import AbstractCase
from loguru import logger
from config import global_config as config
import subprocess
from collections import OrderedDict
import re
import json
from retriever.retrieve_from_codeql_api import get_related_api
from retriever.retrieve_from_codeql_op import get_related_codeql_query_op    
from retriever.retrieve_from_codeql_doc import get_related_doc



def get_logic_string(logics_json):
    logic_string = "**logic for query**:\n"
    for step in logics_json[0]["logic_query"]:
        logic_string += step + "\n"
    return logic_string
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

def save_checker_code( query_code:str,rule_name: str):
    """将生成的检查器代码保存到指定路径。"""
    target_path = config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + rule_name + ".ql"
    with open(target_path, 'w') as f:
        f.write(query_code)
    
    return target_path

def save_middle_check(query_code:str,round_dir: str):
    """将生成的中间检查器代码保存到指定路径。"""
    query_code_path = os.path.join(round_dir, "query_code.ql")
    with open(query_code_path, 'w') as f:
        f.write(query_code)

    return ""

def get_checker_code(rule_name: str):

    """读取指定规则名称的检查器代码。"""
    target_path = config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + rule_name + ".ql"
    with open(target_path, 'r') as f:
        checker_code = f.read()
    return checker_code
 

def parse_query_code_from_answer(answer: str):
    """
    更鲁棒的解析：优先按标签匹配 `checker_cpp:` / `checker_h:` 后的 ```cpp``` 代码块；
    若未命中则退化为取回答中出现的前两个 ```cpp``` 代码块作为 cpp 和 h。
    """
    # 优先按带标签的 code fence 提取（支持 cpp 或 c++）
    query_code_pattern = r"query_code\s*:\s*```(?:query|c\+\+)\s*(.*?)\s*```"
  
    query_code_match = re.search(query_code_pattern, answer, re.IGNORECASE | re.DOTALL)
    

    query_code = query_code_match.group(1).strip() if query_code_match else None
    

    # 回退：如果没有按标签找到，尝试抓取所有 ```cpp``` code block，并用前两个作为 cpp/h
    if not query_code :
        blocks = re.findall(r"```(?:query|c\+\+)\s*(.*?)\s*```", answer, re.IGNORECASE | re.DOTALL)
        if blocks:
            if not query_code and len(blocks) >= 1:
                query_code = blocks[0].strip()
          

    return query_code
def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)
def get_logic_json(logics_json):
  
    logic_for_codeql_query = []
    for step in logics_json[0]["logic_query"]:
        logic_for_codeql_query.append(remove_number_prefix(step))
    return logic_for_codeql_query

def get_most_similar_api_doc_query_op(logics_json):
    """
    根据逻辑描述，从本地API文档和查询操作库中检索最相似的内容。
    """
    # 这里假设有一个本地的API文档和查询操作库，可以根据逻辑描述进行相似度匹配
    # 具体实现可以使用向量化检索、关键词匹配等方法
    # 目前返回占位符字符串

    api_suggest_string = '' #"最相似的API内容:\n"
    doc_suggest_string = '' #"最相似的文档内容:\n"
    query_op_suggest_string = '' #"最相似的查询操作内容:\n"

    logics_for_codeql_query = get_logic_json(logics_json)
    related_api= get_related_api(logics_for_codeql_query)
    related_doc= get_related_doc(logics_for_codeql_query)
    related_query_op= get_related_codeql_query_op(logics_for_codeql_query)
    for a in related_api:
        api_suggest_string += a + "\n"
    for d in related_doc:
        doc_suggest_string += d + "\n"
    for q in related_query_op:
        query_op_suggest_string += q + "\n"

    return api_suggest_string, doc_suggest_string, query_op_suggest_string

def get_suggest_string_from_hint(hint):
    api_suggest_string = '' #"最相似的API内容:\n"
    doc_suggest_string = '' #"最相似的文档内容:\n"
    query_op_suggest_string = '' #"最相似的查询操作内容:\n"

    related_api= get_related_api(hint)
    related_doc= get_related_doc(hint)
    related_query_op= get_related_codeql_query_op(hint)
    for a in related_api:
        api_suggest_string += a + "\n"
    for d in related_doc:
        doc_suggest_string += d + "\n"
    for q in related_query_op:
        query_op_suggest_string += q + "\n"
    return api_suggest_string, doc_suggest_string, query_op_suggest_string
