
import os
from typing import List
from entity.abstractProduct import AbstractCase
from loguru import logger
from config import global_config as config
import subprocess
from collections import OrderedDict
import re
import json


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

def save_checker_code(qll_code: str, query_code:str,rule_name: str):
    """将生成的检查器代码保存到指定路径。"""
   
    return ""

def save_middle_check(qll_code: str, query_code:str,round_dir: str):
    """将生成的中间检查器代码保存到指定路径。"""
 
    return ""

def get_checker_code(rule_name: str):

    """读取指定规则名称的检查器代码。"""
  
    return "checker_code","checker_h"

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

def get_most_similer_api_doc_query_op(logics_json):
    """
    根据逻辑描述，从本地API文档和查询操作库中检索最相似的内容。
    """
    # 这里假设有一个本地的API文档和查询操作库，可以根据逻辑描述进行相似度匹配
    # 具体实现可以使用向量化检索、关键词匹配等方法
    # 目前返回占位符字符串

    api_suggest_string = "最相似的API文档内容"
    doc_suggest_string = "最相似的文档内容"
    query_op_suggest_string = "最相似的查询操作内容"

    return api_suggest_string, doc_suggest_string, query_op_suggest_string