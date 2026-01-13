import subprocess
from unittest import result

def compiler_code_ql(query_path):
    print("----------------------编译CodeQL-----------------------------")
    result = subprocess.run([
        'codeql',
        "query",
        'compile',
        query_path
    ])
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
    ])
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
    warning_count = full_output.count("warning:")
    return full_output, warning_count

if __name__ == "__main__":
    # compiler_code_ql("/root/code_check/codeql/cpp/ql/src/MyQL/test.ql")
    run_code_ql("/root/code_check/codeql/cpp/ql/src/MyQL/test.ql","/root/code_check/linux-db/spi-pci1xxx-db","/root/code_check/result.csv")
