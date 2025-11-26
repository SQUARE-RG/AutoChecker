from abc import ABC, abstractmethod

class AbstractCase(ABC):
    @abstractmethod
    def getInfo(self):
        pass
    @abstractmethod
    def get_case_id(self):
        pass

    @abstractmethod
    def get_case_description(self):
        pass

    @abstractmethod
    def get_case_code(self):
        pass

    @abstractmethod
    def get_case_path(self):
        pass

    @abstractmethod
    def get_flag(self):
        pass
    
    def __str__(self):
        return f"AbstractCase."


class AbstractChecker(ABC):
    @abstractmethod
    def getInfo(self):
        pass
    @abstractmethod
    def get_checker_code(self):
        pass

    @abstractmethod
    def get_passed_cases(self):
        pass
    
    @abstractmethod
    def add_passed_cases(self,case: AbstractCase):
        pass
    @abstractmethod
    def set_passed_cases(self, passed_cases: list):
        pass
    @abstractmethod
    def set_checker_code(self, checker_code: str):
        pass
    @abstractmethod
    def clear_passed_cases(self):
        pass

    def __str__(self):
        return f"AbstractChecker."

class AbstractRule(ABC):
    @abstractmethod
    def getInfo(self):
        pass
    @abstractmethod
    def get_rule_name(self):
        pass
    @abstractmethod
    def get_rule_description(self):
        pass
    @abstractmethod
    def get_rule_test_path(self):
        pass
    
    @abstractmethod
    def add_checker(self):
        pass
    @abstractmethod
    def get_checkers(self):
        pass
    @abstractmethod
    def get_rule_category(self):
        pass

    @abstractmethod
    def set_rule_description(self,new_rule_description):
        pass
    
    def __str__(self):
        return f"AbstractRule."
