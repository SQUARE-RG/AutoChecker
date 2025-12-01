from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt

def get_prompt_for_clang_tidy(key: str):
    if key =="logic_for_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/logic_for_negative_case.json"
        )
        return prompt
    if key == "generate_checker_with_single_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/first_checker_for_negative_case.json"
        )
        return prompt