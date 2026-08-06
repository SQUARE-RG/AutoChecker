import json
import os
import subprocess
from unittest import result


config = {}
with open("/root/code_check/src/config.json", 'r') as f:
    config = json.load(f)
def compiler_code_ql(query_path):
    print("----------------------编译CodeQL-----------------------------")
    result = subprocess.run([
        'codeql',
        "query",
        'compile',
        query_path
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    if result.returncode == 0:
        print("CodeQL编译成功")
        compiler_success= True
    else:
        print("CodeQL编译失败")
        compiler_success= False
    return result.returncode, result.stdout, result.stderr, compiler_success
    
def run_code_ql(query_path, database_path, output_path):
    print("----------------------运行CodeQL-----------------------------")
    result = subprocess.run([
        'codeql',
        "database",
        'analyze',
        database_path,
        '--format=csv',
        '--output=' + output_path,
        query_path,
        '--rerun'
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    if result.returncode == 0:
        print("CodeQL运行成功")
        run_success= True
    else:
        print("CodeQL运行失败")
        run_success= False
    return result.returncode, result.stdout, result.stderr, run_success

def run_code_ql_with_query(query_path, database_path, output_path):
    print("----------------------运行CodeQL-----------------------------")
    cmd =[
        'codeql',
        "database",
        'analyze',
        database_path,
        '--format=csv',
        '--output=' + output_path,
        query_path,
        '--rerun'
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    full_output = proc.stdout
    if proc.returncode != 0:
        print(f"运行 {database_path} 时发生错误，返回码: {proc.returncode}")
        return  full_output, -1
    with open(output_path, 'r') as f:
        output_content = f.read()
    print(f"CodeQL运行成功，输出内容:\n{output_content}")
    # 统计输出内容中的行数，作为告警数量
    warning_count = len(output_content.strip().split('\n')) 

    return full_output, warning_count

def pre_Generate_Query_Template(checker_name):
    # 在config['file_paths']['codeql']+"/cpp/ql/src/MyQL"路径下创建一个ql文件，命名为checker_name+".ql"
   # 模板内容复制/root/code_check/src/prompt/codeql_prompt/prompt_txt/standard.ql
    template_path = "/root/code_check/src/prompt/codeql_prompt/prompt_txt/standard.ql"
    target_path = config['file_paths']['codeql']+"/cpp/ql/src/MyQL/" + checker_name + ".ql"
    with open(template_path, 'r') as src_file:
        template_content = src_file.read()
    with open(target_path, 'w') as target_file:
        target_file.write(template_content)
    print(f"已生成CodeQL查询模板: {target_path}")
    return target_path


def create_databases_for_test_cases(test_case_list):

    """
    假如某个测试用例路径是/root/code_check/test_cases/case1.cpp，
    那么对应的database路径就是/root/code_check/test_cases/case1_db
    这个函数会为每个测试用例创建一个CodeQL database，并返回所有database的路径列表
    """
    database_path_list = []
    for test_case in test_case_list:
        case_path = test_case.get_case_path()
        case_dir, case_file = os.path.split(case_path)
        case_name, _ = os.path.splitext(case_file)
        database_path = os.path.join(case_dir, case_name + "_db")
        if os.path.exists(database_path):
            print(f"Database already exists, skipping creation: {database_path}")
            database_path_list.append(database_path)
            continue
        build_command = f"gcc -c {case_path}"
        # 创建CodeQL database
        cmd = [
            "codeql",
            "database",
            "create",
            database_path,
            "--language=cpp",
            "--command=" + build_command,  # 使用=连接参数名和值
            "--source-root=" + case_dir
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"成功创建CodeQL database: {database_path}")
            database_path_list.append(database_path)
        else:
            print(f"创建CodeQL database失败: {database_path}")
            print(f"错误信息: {result.stderr}")
    return database_path_list

def create_database(test_case_path):
    case_dir, case_file = os.path.split(test_case_path)
    case_name, _ = os.path.splitext(case_file)
    database_path = os.path.join(case_dir, case_name + "_db")
    build_command = f"gcc -c {test_case_path}"
    # 创建CodeQL database
    cmd = [
        "codeql",
        "database",
        "create",
        database_path,
        "--language=cpp",
        "--command=" + build_command,  # 使用=连接参数名和值
        "--source-root=" + case_dir
    ]
    print(f"正在创建CodeQL database，命令为: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"成功创建CodeQL database: {database_path}")
        return database_path
    else:
        print(f"创建CodeQL database失败: {database_path}")
        print(f"错误信息: {result.stderr}")
        return None 
    
def case_path_to_database_path(test_case_path):
    # 假如某个测试用例路径是/root/code_check/test_cases/case1.cpp，
    #那么对应的database路径就是/root/code_check/test_cases/case1_db
    # 返回database路径
    case_dir, case_file = os.path.split(test_case_path)
    case_name, _ = os.path.splitext(case_file)
    database_path = os.path.join(case_dir, case_name + "_db")  
    # 验证database是否存在，如果不存在则报告错误
    if not os.path.exists(database_path):
        print(f"未找到对应的database文件，测试用例路径: {test_case_path}")
        return None
     
    return database_path

def database_path_to_case_path(database_path):
    # 假如某个database路径是/root/code_check/test_cases/case1_db，
    # 那么对应的测试用例路径就是/root/code_check/test_cases/case1.c或者cpp
    # 请验证测试用例文件是否存在，返回测试用例路径
    case_dir, database_file = os.path.split(database_path)
    database_name, _ = os.path.splitext(database_file)
    case_name = database_name.replace("_db", "")
    possible_extensions = ['.c', '.cpp']
    for ext in possible_extensions:
        case_path = os.path.join(case_dir, case_name + ext)
        if os.path.exists(case_path):
            return case_path
    print(f"未找到对应的测试用例文件，数据库路径: {database_path}")
    return None 

   
if __name__ == "__main__":
    # pre_Generate_Query_Template("test_query")
    compiler_code_ql("/root/code_check/codeql/cpp/ql/src/MyQL/test_query.ql")
    database_path = create_database("/root/code_check/temp_validate/test_unused_parameter.cpp")
    print(f"生成的database路径为: {database_path}")
    # print(case_path_to_database_path("/root/code_check/temp_validate/drivers__spi__spi-pci1xxxx.c_bug.c"))
    # run_code_ql("/root/code_check/codeql/cpp/ql/src/MyQL/test.ql","/root/code_check/linux-db/spi-pci1xxx-db","/root/code_check/result.csv")
    full_output,wraning_count = run_code_ql_with_query("/root/code_check/codeql/cpp/ql/src/MyQL/test_query.ql",database_path,"/root/code_check/temp_validate/result.csv")
    print("输出\n"+full_output)
    print(wraning_count)