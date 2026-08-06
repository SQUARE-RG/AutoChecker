import os
import time
from entity.abstractProduct import AbstractCase, AbstractChecker,AbstractRule
from entity.concreteProduct_CodeQL import Checker_CodeQL
from typing import List

from config import global_config as config
from loguru import logger
import re
import json
from llm_interface.llm_provider import llm_client,llm_invoke,calculate_deepseek_cost
from help.code_ql_utils import count_negative_cases,select_negative_case,save_checker_code,save_middle_check,get_checker_code,get_most_similar_api_doc_query_op,get_logic_string,parse_query_code_from_answer,get_suggest_string_from_hint
from prompt.codeql_prompt.build_codeql_prompt import get_prompt_for_Codeql
from plateform.code_ql import run_code_ql_with_query,compiler_code_ql,run_code_ql,pre_Generate_Query_Template,case_path_to_database_path

max_round = config['arguments']['max_round']
max_compiler_trys = config['arguments']['max_compiler_trys']


class CodeQL_CheckerGenerator(object):
    def __init__(self,rule:AbstractRule,all_Test_Case_List: List[AbstractCase]=None,skipped_Test_Cases: List[AbstractCase]=None,rule_result_dir:str=""):

        self.all_Test_Case_List = all_Test_Case_List
        self.skipped_Test_Cases = skipped_Test_Cases if skipped_Test_Cases is not None else []
        self.RULE = rule
        self.result_dir = rule_result_dir
        self.total_cost =0.0
        # self.test_case_database_path_list = test_case_database_path_list if test_case_database_path_list is not None else []
        self.debug_prompt_dir = self.result_dir + "debug_prompt/"

    def get_total_cost(self):
        return self.total_cost
    def generate_checker(self):
        os.makedirs(self.debug_prompt_dir, exist_ok=True)
        success, init_checker = self.first_checker_generation()
        if not success:
            print(f"Failed to generate initial checker for rule: {self.RULE.get_rule_name()}")
            return None
        print("初始checker生成成功")

        self.RULE.add_checker(init_checker)
        # 初始checker生成成功后，重新洗牌
        self.skipped_Test_Cases = []
        self.checker_augmentation(init_checker)
        return self.RULE.get_checkers()
    def run_logic_for_negative_case(self,rule_description:str,case_code:str):
        prompt = get_prompt_for_Codeql("logic_for_negative_case")
        logic_query = prompt.format(rule_description=rule_description,negative_test_case=case_code)
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer,cb = llm_invoke(llm_client,logic_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            logger.debug(f"LLM logic for negative case attempt {attempt}:\n {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    def generate_checker_with_query(self,generation_query:str):
        query_check_code=""
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer,cb = llm_invoke(llm_client,generation_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            with open(self.debug_prompt_dir + "generate_checker_with_query.md", 'w',encoding="utf-8") as f:
                f.write(f"使用增强逻辑生成checker代码，原始回答:\n"+answer)
            

            # 提取代码块
            query_check_code=parse_query_code_from_answer(answer)
            if query_check_code:
                return query_check_code
            else:
                logger.debug("未能从回答中提取到有效的checker代码，尝试重新生成...")
        return query_check_code
    def generate_checker_with_single_case(self,current_case:AbstractCase):
        logics = self.run_logic_for_negative_case(self.RULE.get_rule_description(),current_case.get_case_code())
        api_suggest_string,doc_suggest_string,query_op_suggest_string = get_most_similar_api_doc_query_op(logics)
        logger.info("相关上下文检索完成")

        query_content=''
        query_checker_path = config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + self.RULE.get_rule_name() + ".ql"
        with open(query_checker_path, 'r') as f:
            query_content = f.read()
       
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            prompt = get_prompt_for_Codeql("checker_generation_for_negative_case")
            generation_query = prompt.format(
                rule_description=self.RULE.get_rule_description(),
                test_code=current_case.get_case_code(),
                logics = get_logic_string(logics),
                reference_api=api_suggest_string,
                reference_doc=doc_suggest_string,
                reference_query_op=query_op_suggest_string,
                query_content=query_content
            )
            with open(self.debug_prompt_dir + "generate_checker_with_single_case.md", 'w',encoding="utf-8") as f:
                f.write(generation_query)
            answer,cb = llm_invoke(llm_client,generation_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            logger.debug(f"LLM generate checker attempt {attempt}:\n {answer}")
            # 提取代码块
            query_check_code=parse_query_code_from_answer(answer)
            if query_check_code:
                return query_check_code, logics
            else:
                logger.debug("未能从回答中提取到有效的checker代码，尝试重新生成...")
        return None, logics

    def analyze_compiler_error(self, compiler_output: str, ql_content: str) :
        analyze_prompt = get_prompt_for_Codeql("analyze_compiler_error")
        analyze_query = analyze_prompt.format(
            query_code=ql_content,
            compiler_error_info=compiler_output
        )
      

        api_suggest_string = '' #"最相似的API内容:\n"
        doc_suggest_string = '' #"最相似的文档内容:\n"
        query_op_suggest_string = '' #"最相似的查询操作内容:\n"
        data=None
        repair_steps = []
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer,cb = llm_invoke(llm_client,analyze_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            logger.debug(f"LLM analyze compiler error attempt {attempt}:\n {answer}")
            try:
                cleaned = re.sub(r'```json|```', '', answer).strip()
                data = json.loads(cleaned)
                break
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        if data:
            logger.info("成功解析编译错误分析结果")
            repair_steps = data[0].get('repair_step', []) # 使用 get 方法提供默认值
            repair_steps_string=""
            for step in repair_steps:
                repair_steps_string+= str(step) + "\n"

            wait_retrieve_code_snippet = data[1].get('wait_retrieve_code_snippet', [])
            api_suggest_string, doc_suggest_string, query_op_suggest_string = get_suggest_string_from_hint(wait_retrieve_code_snippet)
        return repair_steps_string, api_suggest_string, doc_suggest_string, query_op_suggest_string
         
    def augmentation_logic_by_negative_case(self,query_check_code,passed_test_cases,failed_test_cases):
        prompt = get_prompt_for_Codeql("augmentation_logic_by_negative_case")
        augmentation_query = prompt.format(
            query_check_code=query_check_code,
            passed_test_cases="\n\n".join([case.get_case_code() for case in passed_test_cases]),
            failed_test_cases="\n\n".join([case.get_case_code() for case in failed_test_cases])
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer,cb = llm_invoke(llm_client,augmentation_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            logger.debug(f"LLM augmentation logic by negative case attempt {attempt}:\n {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    def augmentation_logic_by_positive_case(self,query_check_code,passed_test_cases,failed_test_cases):
        prompt = get_prompt_for_Codeql("augmentation_logic_by_positive_case")
        augmentation_query = prompt.format(
            query_check_code=query_check_code,
            passed_test_cases="\n\n".join([case.get_case_code() for case in passed_test_cases]),
            failed_test_cases="\n\n".join([case.get_case_code() for case in failed_test_cases])
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer,cb = llm_invoke(llm_client,augmentation_query)
            cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
            self.total_cost += cost['total_cost']
            logger.debug(f"LLM augmentation logic by positive case attempt {attempt}:\n {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    def generate_checker_with_single_case_and_checker(self,current_case:AbstractCase,current_checker:AbstractChecker): 
        query_checker_code = get_checker_code(self.RULE.get_rule_name())
        if current_case.get_flag() == False:
            #负例  要报告
            logics = self.augmentation_logic_by_negative_case(query_checker_code,current_checker.get_passed_cases(),[current_case])
            api_suggest_string,doc_suggest_string,query_op_suggest_string = get_most_similar_api_doc_query_op(logics)
            logger.info("相关上下文检索完成")
            repair_negative_case_prompt = get_prompt_for_Codeql("augmentation_check_by_negative_case").format(
                rule_description=self.RULE.get_rule_description(),
                logics = get_logic_string(logics),
                query_check_code=query_checker_code,
                reference_api=api_suggest_string,
                reference_doc=doc_suggest_string,
                reference_query_op=query_op_suggest_string,
                passed_test_cases="\n\n".join([case.get_case_code() for case in current_checker.get_passed_cases()]),
                failed_test_cases=current_case.get_case_code()
            )
            with open(self.debug_prompt_dir + "augmentation_check_by_negative_case.md", 'w',encoding="utf-8") as f:
                f.write(f"针对负例{current_case.get_case_path()}增强checker\n"+repair_negative_case_prompt)
            logger.info(f"针对负例{current_case.get_case_path()}开始使用增强逻辑生成checker代码")
            query_check_code = self.generate_checker_with_query(repair_negative_case_prompt)
            return query_check_code, logics
        elif current_case.get_flag() == True:
            #正例  不应该报告
            logics = self.augmentation_logic_by_positive_case(query_checker_code,current_checker.get_passed_cases(),[current_case])
            api_suggest_string,doc_suggest_string,query_op_suggest_string = get_most_similar_api_doc_query_op(logics)
            logger.info("相关上下文检索完成")
            repair_positive_case_prompt = get_prompt_for_Codeql("augmentation_check_by_positive_case").format(
                rule_description=self.RULE.get_rule_description(),
                logics = get_logic_string(logics),
                query_check_code=query_checker_code,
                reference_api=api_suggest_string,
                reference_doc=doc_suggest_string,
                reference_query_op=query_op_suggest_string,
                passed_test_cases="\n\n".join([case.get_case_code() for case in current_checker.get_passed_cases()]),
                failed_test_cases=current_case.get_case_code()
            )
            with open(self.debug_prompt_dir + "augmentation_check_by_positive_case.md", 'w',encoding="utf-8") as f:
                f.write(f"针对正例{current_case.get_case_path()}增强checker\n"+repair_positive_case_prompt)
            logger.info(f"针对正例\n{current_case.get_case_path()}\n开始使用增强逻辑生成checker代码")

            query_check_code = self.generate_checker_with_query(repair_positive_case_prompt)
            return query_check_code, logics
                                               
    def first_checker_generation(self):
        # 计算flag=0 的测试用例数量
        total_negative_number = count_negative_cases(self.all_Test_Case_List)
        single_success = False
        # 创建result_dir/first_checker目录保存初始checker代码
        first_checker_dir = self.result_dir + "first_checker/"
        os.makedirs(first_checker_dir, exist_ok=True)

        query_checker_path =config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + self.RULE.get_rule_name() + ".ql"
        for t in range(1,total_negative_number+1):
            current_case = select_negative_case(self.all_Test_Case_List, self.skipped_Test_Cases)
            # 创建first_checker_dir/negative_case_{t}目录保存当前负例测试用例相关内容
            negative_case_dir = os.path.join(first_checker_dir, f"negative_case_{t}")
            os.makedirs(negative_case_dir, exist_ok=True)

            # 核验选择的负例测试用例
            if current_case is None:
                logger.debug("No more negative test cases available.")
                break
            logger.info(f"当前选择的负例测试用例路径为：  \n {current_case.get_case_path()}")
            
            round =1
            while not single_success:
                logger.info(f"选择测试用例：\n {current_case.get_case_path()}\n第{round}轮生成尝试开始")
                if round > max_round:
                    logger.info(f"达到最大生成轮数{max_round}，停止当前测试用例的生成尝试")
                    self.skipped_Test_Cases.append(current_case)
                    break
                #创建negative_case_dir/round_{round}目录保存当前轮次相关内容
                round_dir = os.path.join(negative_case_dir, f"round_{round}")
                os.makedirs(round_dir, exist_ok=True)

                query_code,logics = self.generate_checker_with_single_case(current_case)
                if  query_code:
                    logger.info(f"第{round}轮生成的checker代码成功获取")
                else:
                    logger.info("未能生成有效的checker代码，跳过当前测试用例")
                    self.skipped_Test_Cases.append(current_case)
                    round += 1
                    continue

                # if qll_code is None or query_code is None:
                #     logger.info("未能生成有效的checker代码，跳过当前测试用例")
                #     self.skipped_Test_Cases.append(current_case)
                #     round += 1
                #     continue
                query_checker_path =save_checker_code(query_code,self.RULE.get_rule_name())
                 
                round_dir_first_generation = os.path.join(round_dir, "first_generation")
                os.makedirs(round_dir_first_generation, exist_ok=True)
                save_middle_check(query_code,round_dir_first_generation)

                logger.info("开始编译")
                current_try_compiler_count = 1


                compiler_return_code,compiler_return_stdout,compiler_return_stderr,compiler_success =compiler_code_ql(query_checker_path)
                logger.debug(f"编译返回码: {compiler_return_code}\n编译标准输出: {compiler_return_stdout}\n编译错误输出: {compiler_return_stderr}")
                while not compiler_success:
                    logger.info(f"第{round}轮生成的checker编译失败，使用编译修复功能，开始第{current_try_compiler_count}次重试")

                    repair_compiler_failed_dir = os.path.join(round_dir, f"compiler_failed_try_{current_try_compiler_count}")
                    os.makedirs(repair_compiler_failed_dir, exist_ok=True)

                    single_success = False
                    if current_try_compiler_count > config['arguments']['max_compiler_trys']:
                        logger.info(f"达到最大编译修复尝试次数{config['arguments']['max_compiler_trys']}，停止当前测试用例的生成尝试")
                        single_success =False
                        compiler_success = False
                        break 

                    ql_temp = get_checker_code(self.RULE.get_rule_name())
                    repair_steps, api_suggest_string, doc_suggest_string, query_op_suggest_string = self.analyze_compiler_error(str(compiler_return_stdout+compiler_return_stderr),ql_temp)
                    logger.info(f"编译错误分析完成")

                    repair_query = get_prompt_for_Codeql("repair_compiler_error_code").format(
                        query_code=query_code,
                        compiler_error_info=str(compiler_return_stdout+compiler_return_stderr),
                        repair_steps=repair_steps,
                        api_suggest_string=api_suggest_string,
                        doc_suggest_string=doc_suggest_string,
                        query_op_suggest_string=query_op_suggest_string
                    )

                    with open(self.debug_prompt_dir + "repair_compiler_error_code.md", 'w',encoding="utf-8") as f:
                        f.write(f"第{round}轮生成的checker编译失败，开始第{current_try_compiler_count}次重试\n"+repair_query)
                    wait_compiler_checker_ql = self.generate_checker_with_query(repair_query)

                    current_try_compiler_count += 1
                    save_checker_code(wait_compiler_checker_ql, self.RULE.get_rule_name())
                    save_middle_check(wait_compiler_checker_ql,repair_compiler_failed_dir)

                    compiler_return_code,compiler_return_stdout,compiler_return_stderr,compiler_success = compiler_code_ql(query_checker_path)
                    logger.debug(f"编译返回码: {compiler_return_code}\n编译标准输出: {compiler_return_stdout}\n编译错误输出: {compiler_return_stderr}")
                
                if compiler_success:
                    logger.info(f"第{round}轮生成的checker编译成功，下面运行测试用例进行验证")

                    # output_path和测试用例在同一个目录下面
                    output_path = os.path.join(os.path.dirname(current_case.get_case_path()), f"{self.RULE.get_rule_name()}_output.csv")

                    full_output, warning_count = run_code_ql_with_query(query_checker_path,case_path_to_database_path(current_case.get_case_path()),output_path)
                    logger.info(f"测试用例运行完成,warning数量为:{warning_count}")

                    round_final_checker_dir = os.path.join(round_dir, "final_checker")
                    os.makedirs(round_final_checker_dir, exist_ok=True)
                    a = get_checker_code(self.RULE.get_rule_name())
                    save_middle_check(a,round_final_checker_dir)

                    if warning_count >=1:
                        single_success = True
                        passed_cases = [current_case]
                        query_check_code= get_checker_code(self.RULE.get_rule_name())
                       
                        init_checker = Checker_CodeQL(query_check_code,passed_cases)
                        logger.info(f"规则{self.RULE.get_rule_name()}的query在第{round}轮生成成功")
                        return single_success,init_checker
                    elif warning_count < 0:
                        logger.info(f"运行测试用例{current_case.get_case_path()}发生错误，重新尝试")
                    else:
                        logger.info(f"生成的checker未能通过测试用例验证，进行下一轮生成尝试")
                round += 1
        return False,None
    def runAllTestCases(self,init_checker: AbstractChecker):
        failed_case_list =[]
        success_case_list = []
        all_success = False
        init_checker.clear_passed_cases()
        for test_case in self.all_Test_Case_List:
            if self.skipped_Test_Cases and test_case in self.skipped_Test_Cases:
                continue
            query_checker_path = config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + self.RULE.get_rule_name() + ".ql"
            output_path = os.path.join(os.path.dirname(test_case.get_case_path()), f"{self.RULE.get_rule_name()}_output.csv")
            database_path = case_path_to_database_path(test_case.get_case_path())
            full_output, warning_count = run_code_ql_with_query(query_checker_path,database_path,output_path)
            if test_case.get_flag():
                # 这是一个正例，应该通过测试,CHECK-MESSAGES不在代码注释中,符合规则
                if warning_count ==0:
                    success_case_list.append(test_case)
                    init_checker.add_passed_cases(test_case)
                elif warning_count > 0:
                    # 这是一个正例，但是没有通过测试，说明checker不够完善，需要继续迭代
                    failed_case_list.append(test_case)
            else:
                # 这是一个负例，应该不通过测试,CHECK-MESSAGES在代码注释中,不符合规则
                if warning_count > 0:
                    success_case_list.append(test_case)
                    init_checker.add_passed_cases(test_case)
                elif warning_count == 0:
                    failed_case_list.append(test_case)
        if len(failed_case_list) == 0:   
            all_success = True 
        logger.info(f"运行所有测试用例完成，成功通过的测试用例数量:{len(success_case_list)}/{len(self.all_Test_Case_List)}")
        return  success_case_list, failed_case_list,all_success
    
    def checker_augmentation(self,init_checker: AbstractChecker):
        failed_case_list = []
        success_case_list = []
        all_success = False
        success_case_list, failed_case_list,all_success = self.runAllTestCases(init_checker)
        init_checker.set_passed_cases(success_case_list)
        current_checker = init_checker

        while not all_success:
            if len(failed_case_list) == 0:
                all_success = True
                break
            round = 1
            for failed_case in failed_case_list:
                logger.info(f"增强阶段，当前选择的失败测试用例路径为：{failed_case.get_case_path()}")
                round =1
                current_case_success =False
                while not current_case_success:
                    if round > config['arguments']['max_round']:
                        logger.info(f"增强阶段，达到最大生成轮数{max_round}，停止当前测试用例的生成尝试")
                        failed_case_list.remove(failed_case)
                        self.skipped_Test_Cases.append(failed_case)
                        break
                    query_check_code,logics  = self.generate_checker_with_single_case_and_checker(failed_case,current_checker)
                    if query_check_code:
                        logger.info(f"增强阶段，第{round}轮生成的checker代码成功获取")
                    else:
                        logger.info("增强阶段LLM多次未能生成有效的checker代码，跳过当前测试用例")
                        failed_case_list.remove(failed_case)
                        self.skipped_Test_Cases.append(failed_case)
                       
                        break
                    query_checker_path = save_checker_code(query_check_code,self.RULE.get_rule_name())
                    logger.info("增强阶段，开始编译")
                    current_try_compiler_count = 1
                    compiler_return_code,compiler_return_stdout,compiler_return_stderr,compiler_success =compiler_code_ql(query_checker_path)
                    while not compiler_success:
                        logger.info(f"增强阶段，第{round}轮生成的checker编译失败，使用编译修复功能，开始第{current_try_compiler_count}次重试")
                        if current_try_compiler_count > config['arguments']['max_compiler_trys']:
                            logger.info(f"增强阶段，达到最大编译修复尝试次数{config['arguments']['max_compiler_trys']}，停止当前测试用例的生成尝试")
                            current_case_success =False
                            compiler_success = False
                           
                            break
                        query_check_code = get_checker_code(self.RULE.get_rule_name())
                        repair_steps, api_suggest_string, doc_suggest_string, query_op_suggest_string = self.analyze_compiler_error(str(compiler_return_stdout+compiler_return_stderr),query_check_code)
                        logger.info(f"增强阶段，编译错误分析完成")
                        repair_query = get_prompt_for_Codeql("repair_compiler_error_code").format(
                            query_code=query_check_code,
                            compiler_error_info=str(compiler_return_stdout+compiler_return_stderr),
                            repair_steps=repair_steps,
                            api_suggest_string=api_suggest_string,
                            doc_suggest_string=doc_suggest_string,
                            query_op_suggest_string=query_op_suggest_string
                        )
                        wait_compiler_checker_cpp,wait_compiler_checker_h = self.generate_checker_with_query(repair_query)
                        current_try_compiler_count += 1
                        save_checker_code(wait_compiler_checker_cpp, wait_compiler_checker_h,self.RULE.get_rule_name())
                        _,_,_ ,compiler_success = compiler_code_ql(query_checker_path)
                    if compiler_success:
                        logger.info(f"增强阶段，第{round}轮生成的checker编译成功，下面运行测试用例进行验证")
                        output_path = os.path.join(os.path.dirname(failed_case.get_case_path()), f"{self.RULE.get_rule_name()}_output.csv")

                        full_output, warning_count = run_code_ql_with_query(query_checker_path,case_path_to_database_path(failed_case.get_case_path()),output_path)
                        logger.info(f"增强阶段，测试用例运行完成,warning数量为:{warning_count}")
                        if failed_case.get_flag():
                            # 这是一个正例，应该通过测试,CHECK-MESSAGES不在代码注释中,符合规则
                            if warning_count ==0:
                                current_case_success = True
                               
                                failed_case_list.remove(failed_case)
                            elif warning_count > 0:
                                # 这是一个正例，但是没有通过测试，说明checker不够完善，需要继续迭代
                                current_case_success = False
                        else:
                            # 这是一个负例，应该不通过测试,CHECK-MESSAGES在代码注释中,不符合规则
                            if warning_count > 0:
                                current_case_success = True
                                
                                failed_case_list.remove(failed_case)
                            elif warning_count == 0:
                                current_case_success = False
                    round += 1
                if current_case_success:
                    temp_query_code = get_checker_code(self.RULE.get_rule_name())
                    current_checker.set_checker_code(temp_query_code)
                    current_checker_success_case_list, current_checker_failed_case_list,_= self.runAllTestCases(current_checker)

                    current_checker.set_passed_cases(current_checker_success_case_list)
                    tmp_query = get_checker_code(self.RULE.get_rule_name())
                    new_checker = Checker_CodeQL(tmp_query,current_checker_success_case_list)
                    self.RULE.add_checker(new_checker)
                    break
            tmp_ql = get_checker_code(self.RULE.get_rule_name())
            current_checker.set_checker_code(tmp_ql)
            success_case_list, failed_case_list,all_success = self.runAllTestCases(current_checker)
            current_checker.set_passed_cases(success_case_list) 
        return ""





                    






                

