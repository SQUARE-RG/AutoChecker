import base64
from dataclasses import dataclass
from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


@dataclass
class GeneratedCase:
    name: str
    code: str
    rationale: str


class GeneratedCaseModel(BaseModel):
    name: str = Field(..., description="Human-readable identifier for the test case.")
    rationale: str = Field(..., description="Brief explanation of what the test illustrates.")
    code_base64: str = Field(
        ...,
        description="Base64-encoded standalone C11 program that follows all constraints.",
    )


class GeneratedCasesPayload(BaseModel):
    cases: List[GeneratedCaseModel]


class RepairPayload(BaseModel):
    code_base64: str = Field(..., description="Base64-encoded C11 program after repairs.")


class TestCaseGeneralizationAgent:
    """Agent responsible for synthesizing and refining generalized test cases."""

    def __init__(self, llm) -> None:
        self.generation_parser = JsonOutputParser(pydantic_schema=GeneratedCasesPayload)
        self.repair_parser = JsonOutputParser(pydantic_schema=RepairPayload)

        generation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Generalization Agent. Given a vulnerable or fixed exemplar,"
                    " design standalone C11 test cases that either reproduce the vulnerability"
                    " (buggy variant) or demonstrate the correct usage (fixed variant)."
                    "All generated programs must:\n"
                    "- compile with gcc -std=c11 without extra flags\n"
                    "- avoid inline assembly and goto statements\n"
                    "- keep the code minimal yet illustrative\n"
                    "- for vulnerable cases, include '// CHECK-MESSAGES:' before the buggy line\n"
                    "- encode every C source file in Base64 inside the code_base64 field\n"
                    "Respond strictly following these instructions:\n{format_instructions}",
                ),
                (
                    "human",
                    "漏洞触发条件: {pattern}\n"
                    "示例代码:```c\n{exemplar}\n```\n"
                    "生成目标: {variant_label}\n"
                    "需要的测试用例数量: {case_count}\n"
                    "附加约束: {extra_requirements}\n",
                ),
            ]
        ).partial(format_instructions=self.generation_parser.get_format_instructions())

        repair_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Repair Agent. Adjust the provided C test case so it compiles"
                    " cleanly without changing the intended vulnerability status. Follow the"
                    " previous constraints (no goto, standalone, etc.). Encode the final"
                    " code using Base64 and obey: {format_instructions}",
                ),
                (
                    "human",
                    "漏洞触发条件: {pattern}\n变体: {variant_label}\n"
                    "原始测试用例:```c\n{code}\n```\n"
                    "编译器报错信息:```\n{compile_log}\n```\n"
                    "请输出 JSON。",
                ),
            ]
        ).partial(format_instructions=self.repair_parser.get_format_instructions())

        self.generation_chain = generation_prompt | llm | self.generation_parser
        self.repair_chain = repair_prompt | llm | self.repair_parser

    def generate_cases(
        self,
        pattern: str,
        exemplar_code: str,
        variant_label: str,
        case_count: int,
        extra_requirements: str,
    ) -> List[GeneratedCase]:
        response = self.generation_chain.invoke(
            {
                "pattern": pattern,
                "exemplar": exemplar_code,
                "variant_label": variant_label,
                "case_count": case_count,
                "extra_requirements": extra_requirements,
            }
        )
        if isinstance(response, dict):
            cases_payload = response.get("cases", [])
        else:
            cases_payload = response.cases
        results: List[GeneratedCase] = []
        for item in cases_payload:
            name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else "case")
            rationale = getattr(item, "rationale", None) or (
                item.get("rationale") if isinstance(item, dict) else ""
            )
            encoded = getattr(item, "code_base64", None) or (
                item.get("code_base64") if isinstance(item, dict) else ""
            )
            results.append(
                GeneratedCase(
                    name=name or "case",
                    code=self._decode_source(encoded or ""),
                    rationale=rationale or "",
                )
            )
        return results

    def repair_case(
        self,
        pattern: str,
        variant_label: str,
        code: str,
        compile_log: str,
    ) -> str:
        response = self.repair_chain.invoke(
            {
                "pattern": pattern,
                "variant_label": variant_label,
                "code": code,
                "compile_log": compile_log,
            }
        )
        if isinstance(response, dict):
            encoded = response.get("code_base64", "")
        elif hasattr(response, "code_base64"):
            encoded = response.code_base64
        else:
            encoded = ""
        decoded = self._decode_source(encoded)
        return decoded or code

    @staticmethod
    def _decode_source(encoded: str) -> str:
        try:
            return base64.b64decode(encoded).decode("utf-8")
        except Exception:
            return encoded
