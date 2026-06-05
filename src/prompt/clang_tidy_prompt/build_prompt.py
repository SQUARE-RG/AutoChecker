import os

PROMPT_TXT_DIR = "/root/code_check/src/prompt/clang_tidy_prompt/prompt_txt/"

# 向后兼容：旧调用 get_prompt_for_clang_tidy 仍然可用，返回 LangChain PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt

def get_prompt_for_clang_tidy(key: str):
    """向后兼容的旧接口，返回 LangChain PromptTemplate（合并了 system+user 的完整模板）。"""
    json_path_map = {
        "logic_for_negative_case": "logic_for_negative_case.json",
        "generate_checker_with_single_case": "first_checker_for_negative_case.json",
        "analyze_compiler_error": "analyze_compiler_error.json",
        "repair_compiler_error_code": "repair_compiler_error_code.json",
        "augmentation_logic_by_negative_case": "augmentation_logic_by_negative_case.json",
        "augmentation_check_by_negative_case": "augmentation_check_by_negative_case.json",
        "augmentation_logic_by_positive_case": "augmentation_logic_by_positive_case.json",
        "augmentation_check_by_positive_case": "augmentation_check_by_positive_case.json",
    }
    json_name = json_path_map.get(key)
    if json_name:
        return load_prompt(
            "/root/code_check/src/prompt/clang_tidy_prompt/prompt_json/" + json_name
        )
    return None


def get_prompt_pair(key: str):
    """
    返回 (system_prompt: str, user_template: str)

    system_prompt: 固定指令，不含 {variable} 占位符，每次调用内容完全相同
                   → 连续调用时可命中 LLM API 的 prompt caching
    user_template: 包含 {variable} 占位符，调用方用 .format(**kwargs) 填充
    """
    system_path = os.path.join(PROMPT_TXT_DIR, key + "_system.txt")
    user_path   = os.path.join(PROMPT_TXT_DIR, key + "_user.txt")

    with open(system_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    with open(user_path, 'r', encoding='utf-8') as f:
        user_template = f.read()

    return system_prompt, user_template
