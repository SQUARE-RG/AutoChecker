from entity.abstractProduct import AbstractCase
from typing import List
from help.clang_tidy_utils import get_camel_check_name,count_negative_cases,select_negative_case,get_Case_AST,get_most_similar_astMatcher_and_class_struct,parse_cpp_h_code_from_answer
from config import global_config as config
from loguru import logger
import re
import json
from prompt.clang_tidy_prompt.build_prompt import get_prompt_for_clang_tidy
from llm_interface.llm_provider import llm_client,llm_invoke

max_round = config['arguments']['max_round']
max_compiler_trys = config['arguments']['max_compiler_trys']
class Clang_tidy_CheckerGenerator(object):
    def __init__(self,rule,all_Test_Case_List: List[AbstractCase]=None,skipped_Test_Cases: List[AbstractCase]=None):

        self.all_Test_Case_List = all_Test_Case_List
        self.skipped_Test_Cases = skipped_Test_Cases
        self.RULE = rule
        self.RULER_CHECKER_CPP =config['checker']['checker_path'] + get_camel_check_name(rule.get_rule_name()) + ".cpp"
        self.RULER_CHECKER_H = config['checker']['checker_path'] + get_camel_check_name(rule.get_rule_name()) + ".h"
        self.EMBEDDED_AST_NODES = []

    def generate_checker(self):

        pass
    def run_logic_for_negative_case(self, query, testcase):
        prompt = get_prompt_for_clang_tidy("logic_for_negative_case")   
        logic_query = prompt.format(
            rule_description = query,
            negative_test_case = testcase
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer = llm_invoke(llm_client, logic_query)
            logger.debug(f"LLM logic for negative case attempt {attempt + 1}: {answer}")
            # cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(answer)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []

    def generate_checker_with_single_case(self,current_case:AbstractCase,current_case_ast_txt,case_ast_node_list):
        logics = self.run_logic_for_negative_case(self.RULE.get_rule_description(), current_case.get_case_code())
        
        astMatch_suggest_string , class_struct_suggest_string =get_most_similar_astMatcher_and_class_struct(case_ast_node_list,logics)
        ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(self.RULE.get_rule_name()) + ".cpp"
        with open(ruler_checker_cpp, 'r',encoding="utf-8") as file:
            content_cpp = file.read()
        
        ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(self.RULE.get_rule_name()) + ".h"
        with open(ruler_checker_h, 'r',encoding="utf-8") as file:
            content_h = file.read()
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            prompt = get_prompt_for_clang_tidy("generate_checker_with_single_case")   
            # generation_query = prompt.format(
            #     rule_name = self.RULE.get_rule_name(),
            #     rule_description = self.RULE.get_rule_description(),
            #     negative_test_case = current_case.get_case_code(),
            #     negative_test_case_ast = current_case_ast_txt,
            #     existing_checker_cpp = content_cpp,
            #     existing_checker_h = content_h,
            #     astMatcher_suggestions = astMatch_suggest_string,
            #     class_struct_suggestions = class_struct_suggest_string,
            #     logic_steps = logics
            # )
            # answer = llm_invoke(llm_client, generation_query)
            # logger.debug(f"LLM checker generation attempt {attempt + 1}: {answer}")
            # # 提取代码块
            # generator_cpp_code,generator_h_code = parse_cpp_h_code_from_answer(answer)
            # if generator_cpp_code and generator_h_code:
            #     return generator_cpp_code,generator_h_code,logics
            # else:
            #     logger.debug("未能从回答中提取到完整的checker代码。尝试重新生成...")
        
        return None,None,logics
    def first_checker_generation(self):
        #计算flag=0的测试用例数量，也就是负例
        total_negative_number = count_negative_cases(self.all_Test_Case_List)
        single_success = False
        for t in range(1,total_negative_number+1):
            current_case = select_negative_case(self.all_Test_Case_List, self.skipped_Test_Cases)

            # 核验选择的负例测试用例
            if current_case is None:
                logger.debug("No more negative test cases available.")
                break
            logger.info(f"当前选择的负例测试用例路径为：{current_case.get_case_path()}")

            # 获取测试用例对应的抽象语法树
            current_case_ast_txt,current_case_ast_json,case_ast_node_list = get_Case_AST(current_case.get_case_path())
           
            for ast_node in case_ast_node_list:
                if ast_node not in self.EMBEDDED_AST_NODES:
                    self.EMBEDDED_AST_NODES.append(ast_node)
            # embedding_apis(self.EMBEDDED_AST_NODES)
            round = 1
            while not single_success:
                logger.info(f"选择测试用例：{current_case.get_case_path()}\n第{round}轮生成尝试开始")
                if round > max_round:
                    logger.info(f"达到最大生成轮数{max_round}，停止当前测试用例的生成尝试")
                    self.skipped_Test_Cases.append(current_case)
                    break
                checker_cpp,checker_h  = self.generate_checker_with_single_case(current_case,current_case_ast_txt,case_ast_node_list)




    def checker_augmentation(self):
        pass


if __name__ == "__main__":
    get_Case_AST("/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/abseil/duration-conversion-cast.cpp")















