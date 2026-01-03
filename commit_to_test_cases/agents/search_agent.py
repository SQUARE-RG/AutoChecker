from dataclasses import dataclass
from typing import List, Optional, Sequence

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from utils.code_utils import (
    collect_missing_symbols,
    parse_compile_errors,
    slice_source_window,
)
from utils.json_utils import extract_json_from_text


@dataclass
class StubSynthesis:
    updated_code: str
    added_functions: List[str]


class SearchAgent:
    """Search helper that injects fake implementations for missing symbols."""

    def __init__(self, llm):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Search Agent. Given a function name and an optional snippet from"
                    " the original kernel source, craft a tiny fake implementation so that the"
                    " standalone test can compile. The body should be trivial and safe (return 0,"
                    " false, or allocate dummy memory). Respond with JSON containing 'stub'.",
                ),
                (
                    "human",
                    "函数名: {function_name}\n漏洞模式: {pattern}\n"
                    "原始上下文(若为空可自行推断):```c\n{context}\n```\n"
                    "编译器报错: {compile_feedback}\n"
                    "请输出JSON: {{\"stub\": \"...\"}}，仅包含函数定义。",
                ),
            ]
        )
        self.stub_chain = prompt | llm | StrOutputParser()

    def enrich_with_stubs(
        self,
        base_code: str,
        before_source: str,
        pattern: str,
        compile_feedback: Optional[str] = None,
        allowed_symbols: Sequence[str] | None = None,
    ) -> StubSynthesis:
        missing = collect_missing_symbols(base_code, allowed_symbols)
        missing.update(parse_compile_errors(compile_feedback or ""))
        if not missing:
            return StubSynthesis(updated_code=base_code, added_functions=[])
        new_sections: List[str] = []
        added: List[str] = []
        for name in sorted(missing):
            context = slice_source_window(before_source, name)
            response = self.stub_chain.invoke(
                {
                    "function_name": name,
                    "context": context or "",
                    "compile_feedback": compile_feedback or "无",
                    "pattern": pattern,
                }
            )
            payload = extract_json_from_text(response)
            stub = payload.get("stub", "").strip()
            if not stub:
                continue
            new_sections.append(stub)
            added.append(name)
        if not new_sections:
            return StubSynthesis(updated_code=base_code, added_functions=[])
        combined = base_code.rstrip() + "\n\n" + "\n\n".join(new_sections) + "\n"
        return StubSynthesis(updated_code=combined, added_functions=added)
