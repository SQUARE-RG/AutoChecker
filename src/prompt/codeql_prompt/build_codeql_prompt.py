from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt

def get_prompt_for_Codeql(key: str):
    if key == "logic_for_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/logic_for_negative_case.json"
        )
        return prompt
    