from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt
import json
import os
from langchain_openai import ChatOpenAI
import re
failed_rules = []
MAX_RETRY =3
def get_prompt_for_clang_tidy():
    prompt = load_prompt(
        "/root/code_check/clang_tidy_collect/collect_check_op/collect_check_op.json"
    )
    return prompt
def convert_rule_to_filename(rule_name):
    """
    将 Clang-Tidy 规则名称转换为对应的检查器文件名
    
    参数:
        rule_name (str): 规则名称，如 "readability-named-parameter"
        
    返回:
        str: 对应的检查器文件名，如 "NamedParameterCheck.cpp"
    """
    # 1. 分割规则名称（去掉模块前缀）
    parts = rule_name.split('-')
    
    # 2. 移除模块前缀（如 "readability", "modernize" 等）
    # 保留规则名称部分（通常从第二部分开始）
    if len(parts) > 1:
        rule_parts = parts[1:]
    else:
        rule_parts = parts
    
    # 3. 将每个部分转换为首字母大写
    capitalized_parts = [part.capitalize() for part in rule_parts]
    
    # 4. 合并为驼峰命名
    camel_case_name = ''.join(capitalized_parts)
    
    # 5. 添加 "Check" 后缀和 ".cpp" 扩展名
    return f"{camel_case_name}Check.cpp"
def get_checker_code(rule_package,rule_name):
    BASE_DIR = "/root/code_check/llvm-project/clang-tools-extra/clang-tidy"
    rule_cpp_name = convert_rule_to_filename(rule_name)
    alt_cpp_name  = rule_cpp_name.replace("Check.cpp", ".cpp")   # 去掉 Check
    #/root/cw-base/clang-tools-extra/clang-tidy/readability/NamedParameterCheck.cpp
    for name in (rule_cpp_name, alt_cpp_name):
        full_path = os.path.join(BASE_DIR, rule_package, name)
        if os.path.isfile(full_path):
            with open(full_path, encoding="utf-8") as f:
                return f.read()
def get_client():
    client  = ChatOpenAI(
            model="deepseek-ai/DeepSeek-V3",
            api_key="sk-GxYp71HLFJkG3rIjspI5LG7BZ5TVOaTXGRYUyqYE09lGNDXX",
            base_url="https://api2.aigcbest.top/v1"
        )
    return client

llm_client = get_client()
def build_messages(prompt: str):
    messages = []
    messages.append({"role": "user", "content": prompt})
    return messages
def analyze_rule_with_llm(rule_name,checker_code):
    prompt = get_prompt_for_clang_tidy().format(
        checker_code=checker_code
        )
   
    query =  build_messages(prompt)
    
    for attempt in range(1, MAX_RETRY + 1):
        response = llm_client.invoke(query).content
        cleaned = re.sub(r'```json|```', '', response).strip()
        try:
            
            return json.loads(cleaned) 
        except Exception as e:
            print(f"[{rule_name}] 第{attempt}次解析失败，重试中..." if attempt < MAX_RETRY else f"[{rule_name}] 最终解析失败")
            if attempt == MAX_RETRY:
                failed_rules.append(rule_name)
                return None
    return None

def main():
    analysis_results=[]
    with open("/root/code_check/clang_tidy_collect/collect_clang_tidy_checker/all_checker.json", "r") as f:
        all_checkers = json.load(f)
    print(f"Total rule packages: {len(all_checkers['data'])}")
    for rule_package,rule_list in all_checkers['data'].items():
        print(f"Analyzing rule package: {rule_package}")
        for rule_info in rule_list:
            rule_name = rule_info['main_title']
            rule_description = rule_info['description']
            checker_code = get_checker_code(rule_package,rule_info['main_title'])
            print(f"Analyzing rule: {rule_name}")
            result = analyze_rule_with_llm(rule_name, checker_code)
            if result:
                for item in result:
                    item['reference_path'] =f"/root/code_check/llvm-project/clang-tools-extra/clang-tidy/{rule_package}/{convert_rule_to_filename(rule_name)}"
                    analysis_results.append(item) 
    print(f"Failed rules: {failed_rules}")
    print(f"Total successful analyses: {len(analysis_results)}")
    with open("/root/code_check/clang_tidy_collect/collect_check_op/clang_tidy_check_op.json", "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

