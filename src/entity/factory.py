from abc import ABC, abstractmethod
from entity.concreteProduct_Clang_Tidy import Case_Clang_Tidy, Checker_Clang_Tidy, Rule_Clang_Tidy

from entity.concreteProduct_CodeQL import Case_CodeQL, Checker_CodeQL, Rule_CodeQL 
from typing import List

class Factory(ABC):
    @abstractmethod
    def create_case(self) :
        pass

    @abstractmethod
    def create_checker(self) :
        pass

    @abstractmethod
    def create_rule(self):
        pass
    def __str__(self):
        return f"Factory."

class Factory_Clang_Tidy(Factory):
    def create_case(self) -> Case_Clang_Tidy:
        return Case_Clang_Tidy()

    def create_checker(self) -> Checker_Clang_Tidy:
        return Checker_Clang_Tidy()

    def create_rule(self) -> Rule_Clang_Tidy:
        return Rule_Clang_Tidy()

    def __str__(self):
        return f"Factory_Clang_Tidy."
    
class Factory_CodeQL(Factory):
    def create_case(self) -> Case_CodeQL:
        return Case_CodeQL()

    def create_checker(self) -> Checker_CodeQL:
        return Checker_CodeQL()

    def create_rule(self) -> Rule_CodeQL:
        return Rule_CodeQL()
    def __str__(self):
        return f"Factory_CodeQL."
