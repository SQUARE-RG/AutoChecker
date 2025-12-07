import os
from entity.factory import Factory_Clang_Tidy, Factory_CodeQL
import glob
from plateform.clang_tidy import compiler_clang_tidy,pre_Generate_Checker_Template,remove_Checker_Template
from help.clang_tidy_utils import get_camel_check_name
from plateform.clang_tidy import compiler_clang_tidy,run_Checker_with_Check_clang_tidy
from config import global_config as config
def get_entity(factory):
    case = factory.create_case()
    checker = factory.create_checker()
    rule = factory.create_rule()
    return case, checker, rule
def get_rule_entity(factory):
    case = factory.create_case()
    return case

def get_case_entity(factory):
    case = factory.create_case()
    return case
def load_all_cpp(root_dir: str):
    # 读取指定目录下的所有 .cpp 文件内容
    pattern = os.path.join(root_dir,  "*.cpp")
    cpp_dict = {}
    for file_path in glob.glob(pattern, recursive=True):
        with open(file_path, encoding='utf-8') as f:
            cpp_dict[file_path] = f.read()
    return cpp_dict
# 验证官方的checker是否都能通过测试用例

def validate_official_checker(plateform: str,rule_test_path,rule_name: str):
    Case_List = []
    plateform_factory_map = {
        "clang-tidy": Factory_Clang_Tidy,
        "codeql": Factory_CodeQL,
    }
    factory_class = plateform_factory_map.get(plateform)
    if not factory_class:
        raise ValueError(f"Unsupported plateform: {plateform}")

    factory = factory_class()

    sources = load_all_cpp(rule_test_path)
    negative_case_count =0
    positive_case_count =0
    for test_case_file_path, content in sources.items(): 
        case = get_case_entity(factory)
        case.case_code = content
        case.case_description = f"Test case for {rule_name} in {test_case_file_path}"

        if "CHECK-MESSAGES" in content:
            case.case_flag = False
            negative_case_count +=1
        else:
            case.case_flag = True
            positive_case_count +=1
            
        case.case_path = test_case_file_path         
        Case_List.append(case)
    
    print(f"负例数量： {negative_case_count}")
    for case in Case_List:
        print(f"运行测试用例: {case.get_case_path()},这是一个 {'负例' if case.case_flag==False else '正例'}")
        BASE = config['test']['base']
        full_output,warning_count  = run_Checker_with_Check_clang_tidy(
            test_case_path=case.get_case_path(),
            rule_name = rule_name,
            temp_dir=f"{config['checker']['temp_test_dir']}tmp_{rule_name}",
            include_dir=f"{BASE}/checkers/readability"
        )
        print(f"警告数量: {warning_count}")
        if warning_count >0 and case.case_flag == True:
            print(f"官方checker {rule_name} 未通过测试用例: {case.get_case_path()}, 预期无警告，实际有 {warning_count} 个警告")
        elif warning_count ==0 and case.case_flag == False:
            print(f"官方checker {rule_name} 未通过测试用例: {case.get_case_path()}, 预期有警告，实际无警告")
 
if __name__ == "__main__":
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/readability/named-parameter"

    test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/readability/redundant-declaration"
    validate_official_checker(
        plateform="clang-tidy",
        rule_test_path=test_case_dir,
        rule_name="readability-redundant-declaration"
    )