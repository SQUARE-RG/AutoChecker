import subprocess
import json
import os
import subprocess
from pathlib import Path
import time
#实现Checker的增删改查
config = {}
with open("/root/code_check/src/config.json", 'r') as f:
    config = json.load(f)

## 该函数用于生成Clang Tidy Checker模板
def pre_Generate_Checker_Template(checker_name=config['check']['name']):
    print("---------------------生成Checker模板-----------------------------")
    """生成Checker模板"""
    # 使用subprocess运行Python脚本
    result = subprocess.run(
        [
            config['file_paths']['python_env'],
            config['file_paths']['clang-tidy'] + 'add_new_check.py',
            config['check']['module'],
            checker_name
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("返回码:", result.returncode)
    print("标准输出:\n", result.stdout)
    print("错误输出:\n", result.stderr)
    return result.returncode  # 返回生成模板的返回码，0表示成功，其他表示失败



## 该函数用于删除Clang Tidy Checker模板
def remove_Checker_Template(checker_name=config['check']['name']):
    """删除Checker模板"""
    print("----------------------删除Checker-----------------------------")
    # 使用subprocess运行Python脚本
    result = subprocess.run(
        [
            config['file_paths']['python_env'],
            config['file_paths']['clang-tidy'] + 'remove_clang_tidy_check.py',
            config['check']['module'],
            checker_name
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("返回码:", result.returncode)
    print("标准输出:\n", result.stdout)
    print("错误输出:\n", result.stderr)

def runChecker(checker_name=config['check']['name'],testCase_path=[]):
    """运行Checker"""
    print("----------------------运行Checker-----------------------------")
    # 使用subprocess运行Python脚本
    if not testCase_path:
        print("没有指定测试用例路径")
    else:
        for testCase in testCase_path:
            print(f"正在运行测试用例: {testCase}")
            # 使用subprocess运行clang-tidy命令
            result = subprocess.run(
            [
                config['compiler']['build_bin_clang_tidy'],
                f'--checks=-*,{checker_name}',
                testCase,
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
            )
        
            print("返回码:", result.returncode)
            print("标准输出:\n", result.stdout)
            print("错误输出:\n", result.stderr)

def run_Checker_with_Check_clang_tidy(
    test_case_path: str,
    rule_name: str,
    temp_dir: str,
    std: str = "c++17",
    include_dir = None,
    log_name = None,
    script_path: str = config['test']['test_check_clang_tidy_script'],
) :
    #测试checker能否通过测试用例
    """
    在**当前工作目录**下，直接运行 test_check_clang_tidy.py，
    所有参数均用绝对路径，不调用 os.chdir。
    """
    # include_dir = include_dir or "/root/cw-base/clang-tools-extra/test/clang-tidy/checkers/abseil"
    log_name = log_name or f"{rule_name}-test.log"

    cmd = [
        "python", script_path,
        test_case_path,          # 绝对路径
        rule_name,
        temp_dir,             # 绝对路径
        f"-std={std}", "--",
        "-isystem", include_dir
    ]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    full_output = proc.stdout
    # 同时打印 & 写日志
    
    # Path(log_name).write_text(full_output, encoding="utf-8")
    # #成功就是返回码为0
    
    # print("输出日志已保存到:", log_name)
    if proc.returncode != 0:
        print(f"运行 {test_case_path} 时发生错误，返回码: {proc.returncode}")
       
        return full_output, -1
    warning_count = full_output.count("warning:")
    return full_output, warning_count
    

def modifyCheckerCode(checker_name=config['check']['name'], new_checker_code=None):
    """修改Checker代码"""
    print("----------------------修改Checker代码-----------------------------")
    if new_checker_code:
        print(f"将{checker_name}代码修改 ")
        # 假设new_checker_code是一个字符串，包含新的Checker代码
        ##TODO: 实现代码修改逻辑
        # 这里可以使用文件操作或其他方式将new_checker_code写入到相应的Checker文件中
        
    else:
        print("没有传入新的checker代码，无法修改")
def compiler_clang_tidy():
    """编译Clang Tidy"""
    print("----------------------编译Clang-tidy-----------------------------")
    # 使用subprocess运行编译命令
    result = subprocess.run(
    [
        config['compiler']['cmake_path'],
        '--build',
        config['compiler']['build_dir'],
        '--config', 'RelWithDebInfo',
        '--target', 'clang-tidy','-j','56',
        '--'
    ], 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True
    )
    
    print("返回码:", result.returncode)
    print("标准输出:\n", result.stdout)
    print("错误输出:\n", result.stderr)
    compiler_success = result.returncode == 0
    
    return result.returncode,result.stdout, result.stderr,compiler_success

if __name__ == "__main__":
    # print("main")
    # start = time.time()
    # compiler_clang_tidy()
    # pre_Generate_Checker_Template(checker_name="readability-named-parameter")
    # compiler_clang_tidy()
    # remove_Checker_Template(checker_name="readability-named-parameter")
    # compiler_clang_tidy()
    # end = time.time()
    # print(f"总共耗时: {end - start} 秒")

    run_Checker_with_Check_clang_tidy(test_case_path="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/readability/named-parameter.cpp",
    rule_name="readability-named-parameter",
    temp_dir="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/readability/tmp/tmp-readability-named-parameter",
    include_dir="/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/readability"
    )

    # remove_Checker_Template(checker_name="readability-string-compare")
    # remove_Checker_Template(checker_name="clang-tidy-metaOperation-sample")  # 如果需要删除模板，可以取消注释这一行
    #如果正确删除，返回码为0，发生错误返回码不为0
    # 注意：在实际使用中，请确保config.json中的路径和配置正确无误
    #       并且Python环境和clang-tidy脚本可用。
    #       该脚本假设Python环境和clang-tidy脚本已经正确配置在config.json中。
    #       如果需要修改路径或其他配置，请编辑config.json
    #       文件以适应您的环境。
    #       运行此脚本前，请确保已安装clang-tidy和相关依赖。
    #       该脚本将生成或删除指定的Checker模板。
    #       如果需要进一步的功能或修改，请根据实际需求调整脚本。
    # runChecker(checker_name='ucassaat-no-register-var-202428015029027',testCase_path=['/root/cw-base/cw3-tests/no-register-var-202428015029027.c'])

    #构建MetaOperation
    # BASE = "/root/cw-base/clang-tools-extra/test/clang-tidy"
    # pre_Generate_Checker_Template(checker_name="meta-operation-sample")
    # compiler_clang_tidy()
    # /root/cw-base/clang-tools-extra/test/clang-tidy/checkers/ucassaat/no-setjmp-or-longjmp-202428015029027.cpp

    # run_Checker_with_Check_clang_tidy(checker_cpp="/root/cw-base/clang-tools-extra/test/clang-tidy/checkers/ucassaat/meta-operation-sample.cpp",rule_name="ucassaat-meta-operation-sample",temp_dir="/root/cw-base/clang-tools-extra/test/clang-tidy/checkers/ucassaat/tmp/tmp-meta-operation-sample",include_dir=f"{BASE}/checkers/ucassaat")
    # run_Checker_with_Check_clang_tidy(checker_cpp="/root/cw-base/clang-tools-extra/test/clang-tidy/checkers/cppcoreguidelines/virtual-class-destructor.cpp",rule_name="ucassaat-meta-operation-sample",temp_dir="/root/cw-base/clang-tools-extra/test/clang-tidy/checkers/ucassaat/tmp/tmp-meta-operation-sample",include_dir=f"{BASE}/checkers/ucassaat")