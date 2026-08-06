from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt

def get_prompt_for_Codeql(key: str):
    if key == "logic_for_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/logic_for_negative_case.json"
        )
        return prompt
    elif key == "checker_generation_for_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/generate_query_with_single_case.json"
        )
        return prompt
    elif key == "analyze_compiler_error":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/analyze_compiler_error.json"
        )
        return prompt
    elif key == "repair_compiler_error_code":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/repair_compiler_error_code.json"
        )
        return prompt
    elif key == "augmentation_logic_by_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/augmentation_logic_by_negative_case.json"
        )
        return prompt
    elif key == "augmentation_check_by_negative_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/augmentation_check_by_negative_case.json"
        )
        return prompt
    elif key == "augmentation_logic_by_positive_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/augmentation_logic_by_positive_case.json"
        )
        return prompt
    elif key == "augmentation_check_by_positive_case":
        prompt = load_prompt(
            "/root/code_check/src/prompt/codeql_prompt/prompt_json/augmentation_check_by_positive_case.json"
        )
        return prompt
    