
CLANG_PATH = "./llvm-project/build/bin/clang"
CLANG_PLUS_PATH = "./llvm-project/build/bin/clang++"
import subprocess
import os

def validate_gen_ast(test_case_path: str):
    result = subprocess.run([CLANG_PATH,  test_case_path , '-Xclang', '-ast-dump', '-fsyntax-only'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"生成AST失败: {test_case_path}")
        print(f"错误信息: {result.stderr}")
        return False
    else:
        # print(f"生成AST成功: {test_case_path}")
        # print(f"AST内容: {result.stdout}")
        return True
def validate_compiler_clang(test_case_path: str):
    if test_case_path.endswith(".cpp"):
        result = subprocess.run([CLANG_PLUS_PATH,  test_case_path , '-o','validate_compiler'], capture_output=True, text=True)
    else:
        result = subprocess.run([CLANG_PATH,  test_case_path , '-o','validate_compiler'], capture_output=True, text=True)
    if result.returncode != 0:
     
        print(f"编译失败: {test_case_path}")
        print(f"错误信息: {result.stderr}")
        return False
    else:
        print(f"编译成功: {test_case_path}")
        return True
def get_all_test_case_path(test_case_dir: str):
    test_case_paths = []
    for root, dirs, files in os.walk(test_case_dir):
        for file in files:
            if file.endswith(".c") or file.endswith(".cpp"):
                test_case_paths.append(os.path.join(root, file))
    return test_case_paths

if __name__ == "__main__":
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/dependent_call_in_expr"
    test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/use_uncheck_pointer_after_malloc"
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/declare_anonymous_struct"
    # test_case_dir ="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/realse_pointer_not_set_null"
    # test_case_dir ="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/memset_on_stack_variable"
    # test_case_dir ="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_float_convert_int"
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_else_branch"
    
    
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_same_name_as_global_variable"
    # test_case_dir = "/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/prohibit_non_local_variable_in_for_loop"
    
    # test_case_dir="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no_assignment_in_condition"
    test_case_paths = get_all_test_case_path(test_case_dir)
    for test_case_path in test_case_paths:
        validate_compiler_clang(test_case_path)

  