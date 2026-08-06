from entity.abstractProduct import AbstractChecker
from entity.abstractProduct import AbstractCase
from entity.abstractProduct import AbstractRule
from typing import List, Optional
class Case_CodeQL(AbstractCase):
    def __init__(self, case_code: str = "", case_description: str ="", case_flag: bool = False,case_path: str = ""):
        """
        init a test case
        :param case_code:
        :param case_description:
        """
        self.case_code = case_code
        self.case_description = case_description
        self.case_flag = case_flag
        self.case_path = case_path
    def get_case_id(self):
        print("This is a CodeQL case, no ID needed")
        return None
    def getInfo(self):
        print("This is a CodeQL case")
    def get_case_description(self):
        return self.case_description

    def get_case_code(self):
        return self.case_code

    def get_flag(self):
        return self.case_flag
    def get_case_path(self):
        return self.case_path
    def __str__(self):
        return f"Case_CodeQL(flag={self.case_flag})"
    
class Checker_CodeQL(AbstractChecker):
    def __init__(self, checker_code: str, passed_cases: List[Case_CodeQL] = None):
        """
        init a checker
        :param checker_code:
        :param passed_cases:
        """
        self.checker_code = checker_code
        self.passed_cases = passed_cases if passed_cases is not None else []  # 避免可变默认参数问题
    def get_checker_code(self):
        return self.checker_code
    def get_passed_cases(self):
        return self.passed_cases
    def getInfo(self):
        print("This is a CodeQL checker")
    def add_passed_cases(self, case: Case_CodeQL):
        self.passed_cases.append(case)
        return True
    def set_passed_cases(self, passed_cases: List[Case_CodeQL]):
        self.passed_cases = passed_cases
    def set_checker_code(self, checker_code: str):
        self.checker_code = checker_code
        return True
    def get_passed_cases(self):
        return self.passed_cases
    def clear_passed_cases(self):
        self.passed_cases = []
        return True
    def __str__(self):
        return f"Checker_CodeQL(cases_passed={len(self.passed_cases)})"

class Rule_CodeQL(AbstractRule):
    def __init__(self, rule_name: str="", rule_description: str="", rule_test_path: str="", cases_set_xml_path: str="", cases_test_xml_path: str = "",rule_category: str=""):
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.rule_test_path = rule_test_path
        ##这两个待定，不确定要不要
        self.cases_set_xml_path = cases_set_xml_path
        self.cases_test_xml_path = cases_test_xml_path
        #
        self.checker = []
        self.rule_category=rule_category
    def getInfo(self):
        print("This is a CodeQL rule")
    def get_rule_name(self):
        return self.rule_name
    
    def get_rule_description(self):
        return self.rule_description
    
    def get_rule_test_path(self):
        return self.rule_test_path
    def get_rule_category(self):
        return self.rule_category

    def add_checker(self, checker: Checker_CodeQL):
        self.checker.append(checker)
    def get_checkers(self):
        return self.checker
    def set_rule_description(self,new_rule_description):
        self.rule_description = new_rule_description
        
    def __str__(self):
        return f"Rule_CodeQL(name={self.rule_name}, checkers_count={len(self.checker)})"
        