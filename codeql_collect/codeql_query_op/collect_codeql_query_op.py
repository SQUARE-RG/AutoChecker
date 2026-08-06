from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt
import json
import os
from langchain_openai import ChatOpenAI
import re
import pathlib as Path

# 读取codeql_collect/codeql_query_op/codeql_code_cpp.json文件下的每一个codeql query代码
# 将codeql query代码作为prompt的变量query_code
# 返回获取的结果

failed_rules = []
MAX_RETRY =3

def get_prompt_for_clang_tidy():
    prompt = load_prompt(
        "/root/code_check/codeql_collect/codeql_query_op/prompt/collect_codeql_op.json"
    )
    return prompt

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

def analyze_rule_with_llm(rule_name,query_code):
    prompt = get_prompt_for_clang_tidy().format(
        query_code=query_code
    )
    
    with open("/root/code_check/codeql_collect/codeql_query_op/debug_prompt/debug_prompt.txt","w")as f:
        f.write(prompt)
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
    all_query_code_path = "/root/code_check/codeql_collect/codeql_query_op/codeql_code_cpp.json"
    with open(all_query_code_path,'r') as file:
        data=json.load(file)

    # debug=0
    for key,value in data.items():
        print(f"Analyzing checker: {key}")
        result = analyze_rule_with_llm(key,value)
        # debug = debug+1
        # if(debug>3):
        #     break
        if result:
            for item in result:
                item['reference_path'] =f"{key}"
                analysis_results.append(item) 
    print(f"Failed rules: {failed_rules}")
    print(f"Total successful analyses: {len(analysis_results)}")
    with open("/root/code_check/codeql_collect/codeql_query_op/codeql_query_op.json","w",encoding="utf-8") as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()