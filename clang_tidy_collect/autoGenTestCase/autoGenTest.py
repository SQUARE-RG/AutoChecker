'''
Docstring for clang_tidy_collect.autoGenTestCase.autoGenTest
input test_case_name: str  num of test cases to generate: int, test_case_path: str


'''

import os
import json
def auto_gen_test_case(test_case_name: str, num_cases: int, test_case_path: str):
    os.makedirs(test_case_path, exist_ok=True)
    for i in range(1,num_cases+1):
        case_file = os.path.join(test_case_path, f"{test_case_name}_case_{i}.cpp")
        with open(case_file, 'w') as f:
            pass

if __name__ == "__main__":
    # test_case_name = "dependent_call_in_expr"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)

    test_case_name = "use_uncheck_pointer_after_malloc"
    num_cases = 20
    test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc"
    auto_gen_test_case(test_case_name, num_cases, test_case_path)

    # test_case_name = "realse_pointer_not_set_null"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/realse_pointer_not_set_null"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)


    # test_case_name = "misuse_compare_expr"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/misuse_compare_expr"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)
    

    
    # test_case_name = "prohibit_float_convert_int"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)

    # test_case_name = "no_else_branch"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_else_branch"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)

    # test_case_name = "no_same_name_as_global_variable"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)

    # test_case_name = "prohibit_non_local_variable_in_for_loop"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)


    # test_case_name = "no_assignment_in_condition"
    # num_cases = 20
    # test_case_path = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition"
    # auto_gen_test_case(test_case_name, num_cases, test_case_path)
