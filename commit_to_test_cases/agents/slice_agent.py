from dataclasses import dataclass
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from utils.json_utils import extract_json_from_text


@dataclass
class SliceResult:
    code: str
    rationale: str


class SliceAgent:
    """Generate compact before/after test cases guided by the inferred pattern."""

    def __init__(self, llm):
        buggy_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Main Agent that extracts vulnerable kernel slices."
                    "Generate a minimal, standalone C program that reproduces the buggy pattern."
                    "Instructions: \n"
                    "1. Only keep structs, helpers, and logic necessary to demonstrate the bug.\n"
                    "2. Replace Linux-only helpers with small stubs that rely on libc (malloc/calloc/etc).\n"
                    "3. Highlight the buggy statement with the exact comment '// CHECK-MESSAGES: ...'.\n"
                    "4. Remove unrelated functions, macros, and headers.\n"
                    "5. Ensure the result is self-contained C11 code with a main() entry.\n"
                    "Return strict JSON with keys 'code' and 'rationale'.",
                ),
                (
                    "human",
                    "漏洞模式: {pattern}\n关键 API: {key_apis}\n补丁 diff: {file_patch}\n"
                    "初始代码片段如下 (可根据需要精简):\n```c\n{before_code}\n```\n"
                    "如之前的编译器反馈存在报错，可优先避免相同问题: {compile_feedback}\n"
                    "请输出 JSON。",
                ),
            ]
        )
        fixed_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Main Agent for fixed slices."
                    "Produce a minimal C program that shows the corrected logic without the vulnerability."
                    "Requirements: keep the same data structures as the buggy slice, drop kernel-only details,"
                    "and ensure the program compiles as freestanding C11 code.",
                ),
                (
                    "human",
                    "漏洞模式: {pattern}\n关键 API: {key_apis}\n补丁 diff: {file_patch}\n"
                    "修复后代码片段:```c\n{after_code}\n```\n"
                    "请输出 JSON，字段同前。",
                ),
            ]
        )
        parser = StrOutputParser()
        self.buggy_chain = buggy_prompt | llm | parser
        self.fixed_chain = fixed_prompt | llm | StrOutputParser()

    def create_buggy_slice(
        self,
        pattern: str,
        before_code: str,
        key_apis: str,
        file_patch: str,
        compile_feedback: Optional[str] = None,
    ) -> SliceResult:
        response = self.buggy_chain.invoke(
            {
                "pattern": pattern,
                "before_code": before_code,
                "key_apis": key_apis,
                "file_patch": file_patch,
                "compile_feedback": compile_feedback or "无",
            }
        )
        payload = extract_json_from_text(response)
        return SliceResult(code=payload.get("code", ""), rationale=payload.get("rationale", ""))

    def create_fixed_slice(
        self,
        pattern: str,
        after_code: str,
        key_apis: str,
        file_patch: str,
    ) -> SliceResult:
        response = self.fixed_chain.invoke(
            {
                "pattern": pattern,
                "after_code": after_code,
                "key_apis": key_apis,
                "file_patch": file_patch,
            }
        )
        payload = extract_json_from_text(response)
        return SliceResult(code=payload.get("code", ""), rationale=payload.get("rationale", ""))
