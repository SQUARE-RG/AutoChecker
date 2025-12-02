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
    if key == "analyze_compiler_error":
        prompt = load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/analyze_compiler_error.json"
        )
        return prompt
    if key =="repair_compiler_error_code":
        prompt = load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/repair_compiler_error_code.json"
        )
        return prompt
    if key =="augmentation_logic_by_negative_case":
        prompt =load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/augmentation_logic_by_negative_case.json"
        )
        return prompt
    if key =="augmentation_check_by_negative_case":
        prompt =load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/augmentation_check_by_negative_case.json"
        )
        return prompt

    if key =="augmentation_logic_by_positive_case":
        prompt =load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/augmentation_logic_by_positive_case.json"
        )
        return prompt
    if key =="augmentation_check_by_positive_case":
        prompt =load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/augmentation_check_by_positive_case.json"
        )
        return prompt