import os
from entity.abstractProduct import AbstractCase,AbstractRule
from typing import List
from help.clang_tidy_utils import get_camel_check_name,count_negative_cases,select_negative_case,get_Case_AST,get_most_similar_astMatcher_and_class_struct,parse_cpp_h_code_from_answer,save_checker_code,get_checker_code,get_suggest_string_from_hint,save_middle_check
from config import global_config as config
from loguru import logger
import re
import json
from prompt.clang_tidy_prompt.build_prompt import get_prompt_for_clang_tidy
from llm_interface.llm_provider import llm_client,llm_invoke
from plateform.clang_tidy import compiler_clang_tidy,run_Checker_with_Check_clang_tidy
from entity.concreteProduct_Clang_Tidy import AbstractChecker, Checker_Clang_Tidy

max_round = config['arguments']['max_round']
max_compiler_trys = config['arguments']['max_compiler_trys']
class Clang_tidy_CheckerGenerator(object):
    def __init__(self,rule:AbstractRule,all_Test_Case_List: List[AbstractCase]=None,skipped_Test_Cases: List[AbstractCase]=None,rule_result_dir:str=""):

        self.all_Test_Case_List = all_Test_Case_List
        # self.skipped_Test_Cases = skipped_Test_Cases
        self.skipped_Test_Cases = skipped_Test_Cases if skipped_Test_Cases is not None else []
        self.RULE = rule
        self.RULER_CHECKER_CPP =config['checker']['checker_path'] + get_camel_check_name(rule.get_rule_name()) + ".cpp"
        self.RULER_CHECKER_H = config['checker']['checker_path'] + get_camel_check_name(rule.get_rule_name()) + ".h"
        self.EMBEDDED_AST_NODES = []
        self.result_dir = rule_result_dir

    def generate_checker(self):
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
        
    def run_logic_for_negative_case(self, query, testcase):
        prompt = get_prompt_for_clang_tidy("logic_for_negative_case")   
        logic_query = prompt.format(
            rule_description = query,
            negative_test_case = testcase
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer = llm_invoke(llm_client, logic_query)
            logger.debug(f"LLM logic for negative case attempt {attempt}:\n {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    def augmentation_logic_by_negative_case(self,check_cpp_code,check_h_code,passed_test_cases,failed_test_cases):
        prompt = get_prompt_for_clang_tidy("augmentation_logic_by_negative_case")   
        augmentation_query = prompt.format(
            check_cpp_code = check_cpp_code,
            check_h_code = check_h_code,
            passed_test_cases = passed_test_cases,
            failed_test_cases = failed_test_cases
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer = llm_invoke(llm_client, augmentation_query)
            logger.debug(f"LLM augmentation logic by negative case attempt {attempt}: {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    
    def augmentation_logic_by_positive_case(self,check_cpp_code,check_h_code,passed_test_cases,failed_test_cases):
        prompt = get_prompt_for_clang_tidy("augmentation_logic_by_positive_case")   
        augmentation_query = prompt.format(
            check_cpp_code = check_cpp_code,
            check_h_code = check_h_code,
            passed_test_cases = passed_test_cases,
            failed_test_cases = failed_test_cases
          
        )
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer = llm_invoke(llm_client, augmentation_query)
            logger.debug(f"LLM augmentation logic by positive case attempt {attempt}: {answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                json_logic = json.loads(cleaned)
                return json_logic
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        return []
    def generate_checker_with_single_case(self,current_case:AbstractCase,current_case_ast_txt,case_ast_node_list):
        logics = self.run_logic_for_negative_case(self.RULE.get_rule_description(), current_case.get_case_code())
        
        astMatch_suggest_string , class_struct_suggest_string =get_most_similar_astMatcher_and_class_struct(case_ast_node_list,logics_json=logics)
        ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(self.RULE.get_rule_name()) + ".cpp"
        with open(ruler_checker_cpp, 'r',encoding="utf-8") as file:
            content_cpp = file.read()
        
        ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(self.RULE.get_rule_name()) + ".h"
        with open(ruler_checker_h, 'r',encoding="utf-8") as file:
            content_h = file.read()
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            prompt = get_prompt_for_clang_tidy("generate_checker_with_single_case")  
            generation_query = prompt.format(
                rule_description = self.RULE.get_rule_description(),
                test_code = current_case.get_case_code(),
                ast_txt = current_case_ast_txt,
                logics = logics,
                reference_astMatchers = astMatch_suggest_string,
                renference_check_api = class_struct_suggest_string,
                ruler_checker_cpp_name = ruler_checker_cpp,
                content_of_ruler_checker_cpp = content_cpp,
                ruler_checker_h_name = ruler_checker_h,
                content_of_ruler_checker_h = content_h,
            )
            answer = llm_invoke(llm_client, generation_query)
            logger.debug(f"LLM checker generation attempt {attempt}: \n{answer}")
            # 提取代码块
            generator_cpp_code,generator_h_code = parse_cpp_h_code_from_answer(answer)
            if generator_cpp_code and generator_h_code:
                return generator_cpp_code,generator_h_code,logics
            else:
                logger.debug("未能从回答中提取到完整的checker代码。尝试重新生成...")
        
        return None,None,logics
    def generate_checker_with_single_case_and_checker(self,current_case:AbstractCase,current_case_ast_txt,case_ast_node_list,current_checker:AbstractChecker):
        checker_cpp,checker_h = get_checker_code(self.RULE.get_rule_name())
        if current_case.get_flag() == False:
            # 负例
            logics = self.augmentation_logic_by_negative_case(checker_cpp,checker_h,current_checker.get_passed_cases(),[current_case])
            astMatch_suggest_string , class_struct_suggest_string =get_most_similar_astMatcher_and_class_struct(case_ast_node_list,logics)
            repair_negative_case_prompt = get_prompt_for_clang_tidy("augmentation_check_by_negative_case").format(
                rule_description = self.RULE.get_rule_description(),
                ast_txt = current_case_ast_txt,
                logics = logics,
                reference_astMatchers = astMatch_suggest_string,
                renference_check_api = class_struct_suggest_string,
                content_of_ruler_checker_cpp = checker_cpp,
                content_of_ruler_checker_h = checker_h,
                passed_test_cases = "\n".join([case.get_case_code() for case in current_checker.get_passed_cases()]),
                failed_test_cases = current_case.get_case_code()
            )
            logger.info(f"针对负例{current_case.get_case_path()}开始使用增强逻辑生成checker代码")
            checker_cpp,checker_h = self.generate_checker_with_query(repair_negative_case_prompt)
            return checker_cpp,checker_h,logics 
        elif current_case.get_flag() == True:
            # 正例
            # logger.info(f"针对正例，当前checker检查器的输出为:\n{full_output}")
            logics = self.augmentation_logic_by_positive_case(checker_cpp,checker_h,current_checker.get_passed_cases(),[current_case])
            astMatch_suggest_string , class_struct_suggest_string =get_most_similar_astMatcher_and_class_struct(case_ast_node_list,logics)
            repair_positive_case_prompt = get_prompt_for_clang_tidy("augmentation_check_by_positive_case").format(
                rule_description = self.RULE.get_rule_description(),
                ast_txt = current_case_ast_txt,
                logics = logics,
                reference_astMatchers = astMatch_suggest_string,
                renference_check_api = class_struct_suggest_string, 
                content_of_ruler_checker_cpp = checker_cpp,
                content_of_ruler_checker_h = checker_h,
                passed_test_cases = "\n".join([case.get_case_code() for case in current_checker.get_passed_cases()]),
                failed_test_cases = current_case.get_case_code()
               
            )
            logger.info(f"针对正例\n{current_case.get_case_path()}\n开始使用增强逻辑生成checker代码")
            checker_cpp,checker_h = self.generate_checker_with_query(repair_positive_case_prompt)
            return checker_cpp,checker_h,logics 
  

    def generate_checker_with_query(self, query: str):
        checker_cpp =""
        checker_h = ""
        while(checker_cpp == "" or checker_h =="" or checker_cpp is None or checker_h is None):
            checker = llm_invoke(llm_client, query)
            checker_cpp,checker_h = parse_cpp_h_code_from_answer(checker)
        return checker_cpp,checker_h

    def analyze_compiler_error(self, compiler_output: str, cpp_temp: str, h_temp: str) :
        analyze_prompt = get_prompt_for_clang_tidy("analyze_compiler_error")
        analyze_query = analyze_prompt.format(
            check_cpp_code = cpp_temp,
            check_h_code = h_temp,
            compiler_error_info = compiler_output
        )
        data = None
        suggestions = []
        repair_steps= []
        for attempt in range(1,config['arguments']['max_llm_tries'] + 1):
            answer = llm_invoke(llm_client, analyze_query)
            logger.debug(f"LLM analyze compiler error attempt {attempt}: \n{answer}")
            cleaned = re.sub(r'```json|```', '', answer).strip()
            try:
                data = json.loads(cleaned)
                break
            except json.JSONDecodeError as e:
                logger.debug(f"JSON解析错误: {e}. 尝试重新生成...")
        
        if data is not None:
            logger.info("成功解析编译错误分析结果")
            repair_steps = data[0].get('repair_step', []) # 使用 get 方法提供默认值
            wait_retrieve_code_snippet = data[1].get('wait_retrieve_code_snippet', [])
            # 检索代码片段
            suggestions = get_suggest_string_from_hint(wait_retrieve_code_snippet)
        return repair_steps,suggestions
                             
        
    def first_checker_generation(self):
        #计算flag=0的测试用例数量，也就是负例
        total_negative_number = count_negative_cases(self.all_Test_Case_List)
        single_success = False
        # 创建result_dir/first_checker目录保存初始checker代码
        first_checker_dir = self.result_dir + "first_checker/"
        os.makedirs(first_checker_dir, exist_ok=True)

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

            # 获取测试用例对应的抽象语法树
            current_case_ast_txt,current_case_ast_json,case_ast_node_list = get_Case_AST(current_case.get_case_path())
           
            # for ast_node in case_ast_node_list:
            #     if ast_node not in self.EMBEDDED_AST_NODES:
            #         self.EMBEDDED_AST_NODES.append(ast_node)
            # embedding_apis(self.EMBEDDED_AST_NODES)
            round = 1
            while not single_success:
                logger.info(f"选择测试用例：\n {current_case.get_case_path()}\n第{round}轮生成尝试开始")
                

                if round > max_round:
                    logger.info(f"达到最大生成轮数{max_round}，停止当前测试用例的生成尝试")
                    self.skipped_Test_Cases.append(current_case)
                    break
                
                #创建negative_case_dir/round_{round}目录保存当前轮次相关内容
                round_dir = os.path.join(negative_case_dir, f"round_{round}")
                os.makedirs(round_dir, exist_ok=True)
                
                checker_cpp,checker_h,logics  = self.generate_checker_with_single_case(current_case,current_case_ast_txt,case_ast_node_list)
                if checker_cpp is None or checker_h is None:
                    logger.info("未能生成有效的checker代码，跳过当前测试用例")
                    self.skipped_Test_Cases.append(current_case)
                    round += 1
                    continue
                save_checker_code(checker_cpp,checker_h,self.RULE.get_rule_name())
                # 将第round轮生成的checker代码保存到对应目录

                round_dir_first_generation = os.path.join(round_dir, "first_generation")
                os.makedirs(round_dir_first_generation, exist_ok=True)
                save_middle_check(checker_cpp,checker_h,round_dir_first_generation)



                logger.info("开始编译")
                current_try_compiler_count = 1
                compiler_return_code,compiler_return_stdout,compiler_return_stderr,compiler_success =compiler_clang_tidy()
                # round += 1
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
                    cpp_temp,h_temp = get_checker_code(self.RULE.get_rule_name())
                    repair_steps,suggestions = self.analyze_compiler_error(str(compiler_return_stdout),cpp_temp,h_temp)
                    repair_query = get_prompt_for_clang_tidy("repair_compiler_error_code").format(
                        check_cpp_code = cpp_temp,
                        check_h_code = h_temp,
                        compiler_error_info = str(compiler_return_stdout),
                        repair_steps = repair_steps,
                        repair_suggestions = suggestions
                    )
                    wait_compiler_checker_cpp,wait_compiler_checker_h = self.generate_checker_with_query(repair_query)
                    current_try_compiler_count += 1
                    save_checker_code(wait_compiler_checker_cpp, wait_compiler_checker_h,self.RULE.get_rule_name())

                    save_middle_check(wait_compiler_checker_cpp,wait_compiler_checker_h,repair_compiler_failed_dir)

                    _,_,_ ,compiler_success=compiler_clang_tidy()
                if compiler_success:
                    logger.info(f"第{round}轮生成的checker编译成功，下面运行测试用例进行验证")
                    BASE = config['test']['base']
                    full_output, warning_count = run_Checker_with_Check_clang_tidy(
                        test_case_path=current_case.get_case_path(),
                        rule_name=f"ucassaat-{self.RULE.get_rule_name()}",
                        temp_dir=f"{config['checker']['temp_test_dir']}tmp_{self.RULE.get_rule_name()}",
                        include_dir=f"{BASE}/checkers/{self.RULE.get_rule_category()}"
                    )
                    logger.info(f"测试用例运行完成,warning数量为:{warning_count}")

                    round_final_checker_dir = os.path.join(round_dir, "final_checker")
                    os.makedirs(round_final_checker_dir, exist_ok=True)
                    a,b = get_checker_code(self.RULE.get_rule_name())
                    save_middle_check(a,b,round_final_checker_dir)
                  
                    if warning_count >=1:
                        single_success = True
                        passed_cases = [current_case]
                        tmp_checker_cpp,tmp_checker_h = get_checker_code(self.RULE.get_rule_name())
                        source_code ="check.cpp:\n"+ tmp_checker_cpp + "\n" +"check.h:\n"+ tmp_checker_h
                        init_checker = Checker_Clang_Tidy(source_code,passed_cases)
                        logger.info(f"规则{self.RULE.get_rule_name()}的Checker在第{round}轮生成成功")
                        return single_success,init_checker
                    elif warning_count < 0:
                        logger.info(f"运行测试用例{current_case.get_case_path()}发生错误，重新尝试")
                        # TODO 运行修复功能 -- 编译 -- 如果编译不通过直接跳过 -- 编译通过后运行测试用例  -- 不通过测试用例直接放弃
                round += 1
        return False, None
    def runAllTestCase(self,init_checker: AbstractChecker):    
        failed_case_list =[]
        success_case_list = []
        all_success = False
        init_checker.clear_passed_cases()
        for test_case in self.all_Test_Case_List:
            if self.skipped_Test_Cases and test_case in self.skipped_Test_Cases:
                continue
            BASE = config['test']['base']
            full_output, warning_count = run_Checker_with_Check_clang_tidy(
                test_case_path=test_case.get_case_path(),
                rule_name=f"ucassaat-{self.RULE.get_rule_name()}",
                temp_dir=f"{config['checker']['temp_test_dir']}tmp_{self.RULE.get_rule_name()}",
                include_dir=f"{BASE}/checkers/{self.RULE.get_rule_category()}"
            )
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

    def checker_augmentation(self, init_checker: AbstractChecker):

        # check_augmnetation_dir = self.result_dir + "checker_augmentation/"
        # os.makedirs(check_augmnetation_dir, exist_ok=True)

        failed_case_list = []
        success_case_list = []
        all_success = False
        success_case_list, failed_case_list,all_success = self.runAllTestCase(init_checker)
        init_checker.set_passed_cases(success_case_list)

        current_checker = init_checker
        while not all_success:
            if len(failed_case_list) ==0:
                all_success = True
                break
            round = 1
            for failed_case in failed_case_list:
                logger.info(f"增强阶段，当前选择的失败测试用例路径为：{failed_case.get_case_path()}")
                current_case_ast_txt,current_case_ast_json,case_ast_node_list = get_Case_AST(failed_case.get_case_path())
                # for ast_node in case_ast_node_list:
                #     if ast_node not in self.EMBEDDED_AST_NODES:
                #         self.EMBEDDED_AST_NODES.append(ast_node)
                round = 1
                current_case_success =False
                while not current_case_success:
                    if round > config['arguments']['max_round']:
                        logger.info(f"增强阶段，达到最大生成轮数{max_round}，停止当前测试用例的生成尝试")
                        failed_case_list.remove(failed_case)
                        self.skipped_Test_Cases.append(failed_case)
                        break
                    
                    # BASE = config['test']['base']
                    # full_output, warning_count = run_Checker_with_Check_clang_tidy(
                    #     test_case_path=failed_case.get_case_path(),
                    #     rule_name=f"ucassaat-{self.RULE.get_rule_name()}",
                    #     temp_dir=f"{config['checker']['temp_test_dir']}tmp_{self.RULE.get_rule_name()}",
                    #     include_dir=f"{BASE}/checkers/{self.RULE.get_rule_category()}"
                    # )

                    wait_compiler_checker_cpp,wait_compiler_checker_h,logics  = self.generate_checker_with_single_case_and_checker(failed_case,current_case_ast_txt,case_ast_node_list,current_checker)
                    save_checker_code(wait_compiler_checker_cpp,wait_compiler_checker_h, self.RULE.get_rule_name())
                    # round += 1
                    logger.info("增强阶段，开始编译")
                    current_try_compiler_count = 1
                    compiler_return_code,compiler_return_stdout,compiler_return_stderr,compiler_success =compiler_clang_tidy()
                    while not compiler_success:
                        logger.info(f"增强阶段，第{round}轮生成的checker编译失败，使用编译修复功能，开始第{current_try_compiler_count}次重试")
                        if current_try_compiler_count > config['arguments']['max_compiler_trys']:
                            logger.info(f"增强阶段，达到最大编译修复尝试次数{config['arguments']['max_compiler_trys']}，停止当前测试用例的生成尝试")
                            current_case_success =False
                            compiler_success = False
                           
                            break
                        cpp_temp,h_temp = get_checker_code(self.RULE.get_rule_name())
                        repair_steps,suggestions = self.analyze_compiler_error(str(compiler_return_stdout),cpp_temp,h_temp)
                        repair_query = get_prompt_for_clang_tidy("repair_compiler_error_code").format(
                            check_cpp_code = cpp_temp,
                            check_h_code = h_temp,
                            compiler_error_info = str(compiler_return_stdout),
                            repair_steps = repair_steps,
                            repair_suggestions = suggestions
                        )
                        wait_compiler_checker_cpp,wait_compiler_checker_h = self.generate_checker_with_query(repair_query)
                        current_try_compiler_count += 1
                        save_checker_code(wait_compiler_checker_cpp, wait_compiler_checker_h,self.RULE.get_rule_name())
                        _,_,_ ,compiler_success=compiler_clang_tidy()
                    if compiler_success:
                        logger.info(f"增强阶段，第{round}轮生成的checker编译成功，下面运行测试用例进行验证")
                        BASE = config['test']['base']
                        full_output, warning_count = run_Checker_with_Check_clang_tidy(
                            test_case_path=failed_case.get_case_path(),
                            rule_name=f"ucassaat-{self.RULE.get_rule_name()}",
                            temp_dir=f"{config['checker']['temp_test_dir']}tmp_{self.RULE.get_rule_name()}",
                            include_dir=f"{BASE}/checkers/{self.RULE.get_rule_category()}"
                        )
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
                # round = 1
                if current_case_success:
                    tmp_checker_cpp,tmp_checker_h = get_checker_code(self.RULE.get_rule_name())
                    source_code ="check.cpp:\n"+ tmp_checker_cpp + "\n" +"check.h:\n"+ tmp_checker_h
                    current_checker.set_checker_code(source_code)
                    current_checker_success_case_list, current_checker_failed_case_list,_= self.runAllTestCase(current_checker)
                    
                    current_checker.set_passed_cases(current_checker_success_case_list)
                    tmp_cpp,tmp_h = get_checker_code(self.RULE.get_rule_name())
                    code = "check.cpp:\n"+ tmp_cpp + "\n" +"check.h:\n"+ tmp_h
                    new_checker = Checker_Clang_Tidy(code,current_checker_success_case_list)
                    self.RULE.add_checker(new_checker)
                    break
            #重新运行所有的测试用例
            tmp_cpp,tmp_h = get_checker_code(self.RULE.get_rule_name())
            code = "check.cpp:\n"+ tmp_cpp + "\n" +"check.h:\n"+ tmp_h
            current_checker.set_checker_code(code)
            success_case_list, failed_case_list,all_success = self.runAllTestCase(current_checker)
            current_checker.set_passed_cases(success_case_list)   
        return ""
# if __name__ == "__main__":
#     get_Case_AST("/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/abseil/duration-conversion-cast.cpp")