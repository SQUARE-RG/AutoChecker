from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt

def get_prompt_for_clang_tidy(key: str):
    if key =="test_case_diversify":
        prompt = load_prompt(
            "/root/code_check/commit_to_test_cases/prompt/prompt_json/test_case_diversify.json"
        )
        return prompt