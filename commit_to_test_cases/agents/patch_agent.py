from dataclasses import dataclass, asdict
from typing import Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from utils.json_utils import extract_json_from_text


@dataclass
class PatchPattern:
    description: str
    vulnerability_type: str
    trigger_conditions: str
    impact: str
    fix_strategy: str
    key_apis: List[str]

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class PatchAnalysisAgent:
    """Summarise the vulnerability pattern from the provided patch description."""

    def __init__(self, llm):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Patch-Analysis agent in a multi-agent testing system. "
                    "Summarise the vulnerability pattern from Linux kernel patches. "
                    "Respond in Chinese when possible and output strict JSON without extra text.",
                ),
                (
                    "human",
                    "读取补丁描述并总结漏洞信息。必须输出JSON，字段: \n"
                    "- description: 对补丁及缺陷的简要描述\n"
                    "- vulnerability_type: 漏洞类型或分类\n"
                    "- trigger_conditions: 触发该问题所需的条件\n"
                    "- impact: 未修复时的影响\n"
                    "- fix_strategy: 修复思路/关键要点\n"
                    "- key_apis: 受影响或需要特别关注的API名列表\n\n"
                    "补丁内容如下:\n{patch_md}",
                ),
            ]
        )
        self.chain = prompt | llm | StrOutputParser()

    def analyze(self, patch_text: str) -> PatchPattern:
        response = self.chain.invoke({"patch_md": patch_text})
        payload = extract_json_from_text(response)
        key_apis = payload.get("key_apis") or []
        if isinstance(key_apis, str):
            key_apis = [item.strip() for item in key_apis.split(",") if item.strip()]
        return PatchPattern(
            description=payload.get("description", ""),
            vulnerability_type=payload.get("vulnerability_type", ""),
            trigger_conditions=payload.get("trigger_conditions", ""),
            impact=payload.get("impact", ""),
            fix_strategy=payload.get("fix_strategy", ""),
            key_apis=key_apis,
        )
