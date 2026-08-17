"""CodeQL agent 工具：search_docs / get_doc_detail / read_file / write_query_file。

检索上下文（RetrievalContext）设计：
- query → answer 映射（answer 是检索返回给 agent 的文本，每 doc 截断 500 字符）
- 跨 query 去重依据 answer 里的 ChromaDB chunk_id
- 摘要 = "query: answer 前 120 字符"，注入 prompt
- get_doc_detail(query) 直接返回存储的 answer（纯字典查找）
- 每个规则 run 独立建一个 ctx，不跨规则共享

路径安全：read_file / write_query_file 只允许访问白名单根目录。
"""

import os
import random
from typing import Union

from langchain_core.tools import tool
from loguru import logger

from retriever.retriever_codeql_uniform import (
    query_chroma_docs_with_ids,
    _PYTHON_DOC_COLLECTIONS,
)

_DOC_TRUNCATE = 5120   # 每个文档片段在 answer 中的宽上限截断（5KB：
                      # 覆盖官方查询/API 文档完整内容，挡住 187KB 级巨型 chunk）


class RetrievalContext:
    """run 级检索上下文：query → answer 映射 + doc-id 去重 + 摘要。"""

    def __init__(self):
        self.entries: dict = {}   # query -> {"answer": str, "doc_ids": list, "summary": str}

    def seen_doc_ids(self) -> set:
        ids = set()
        for e in self.entries.values():
            ids.update(e["doc_ids"])
        return ids

    def summaries(self, limit: int = 8) -> list:
        return [e["summary"] for e in list(self.entries.values())[:limit]]

    def find_entry_with_ids(self, doc_ids: list) -> str | None:
        """返回包含这些 doc_id 的已有条目 query 键（用于重复处理）。"""
        for q, e in self.entries.items():
            if any(i in e["doc_ids"] for i in doc_ids):
                return q
        return None

    def rekey(self, old_query: str, new_query: str):
        """把条目从旧 query 键改挂到新 query 键（随机保留一个 query 的实现）。"""
        if old_query in self.entries:
            self.entries[new_query] = self.entries.pop(old_query)


def _make_summary(query: str, answer: str) -> str:
    import re
    # 去掉内部 doc id 标注（[doc xxx] 前缀），摘要只留内容
    clean = re.sub(r"\[doc [^\]]+\]", "", answer)
    flat = " ".join(clean.split())[:120]
    return f"{query}: {flat}"


def build_tools(result_dir: str, test_case_dir: str, rule_name: str,
                ctx: RetrievalContext) -> list:
    """构造工具实例（闭包注入：目录路径、规则名、检索上下文）。"""

    def _check_path(path: str) -> str:
        real = os.path.realpath(path)
        allowed_roots = [os.path.realpath(result_dir), os.path.realpath(test_case_dir)]
        for root in allowed_roots:
            if real == root or real.startswith(root + os.sep):
                return real
        raise PermissionError(f"路径越界，拒绝访问: {path}")

    @tool
    def search_docs(queries: Union[str, list]) -> str:
        """在 CodeQL Python 文档库（ChromaDB）中检索相关内容。

        参数 queries: 一个或多个检索关键词（英文），可一次检索多个 API 概念，
        例如 ["TaintTracking Configuration", "subprocess.run sink"]。

        系统会记住每次检索（query → 结果），重复检索不会返回重复内容。
        返回内容按查询分组，每个文档片段截断至 500 字符。
        """
        if isinstance(queries, str):
            queries = [queries]

        sections = []
        for q in queries[:5]:
            pairs = query_chroma_docs_with_ids([q], _PYTHON_DOC_COLLECTIONS, top_k=2)
            if not pairs:
                sections.append(f"### 检索: {q}\n(未检索到相关文档)")
                continue

            seen = ctx.seen_doc_ids()
            new_pairs = [(cid, text) for cid, text in pairs if cid not in seen]

            if not new_pairs:
                # 全部重复：随机保留一个 query 作为映射键
                dup_query = ctx.find_entry_with_ids([cid for cid, _ in pairs])
                if dup_query and random.random() < 0.5:
                    ctx.rekey(dup_query, q)
                    msg = (f"该内容此前以 query '{dup_query}' 检索过（结果相同），"
                           f"现在改用 '{q}' 引用")
                else:
                    msg = f"该内容此前已检索过（query '{dup_query}'），无新内容"
                sections.append(f"### 检索: {q}\n{msg}")
                continue

            answer_parts = []
            for cid, text in new_pairs:
                answer_parts.append(f"[doc {cid}]\n{text[:_DOC_TRUNCATE]}")
            answer = "\n\n".join(answer_parts)
            ctx.entries[q] = {
                "answer": answer,
                "doc_ids": [cid for cid, _ in new_pairs],
                "summary": _make_summary(q, answer),
            }
            sections.append(f"### 检索: {q}\n{answer}")

        return "\n\n".join(sections) if sections else "(未检索到相关文档)"

    @tool
    def get_doc_detail(query: str) -> str:
        """获取之前用 search_docs 检索过的内容的完整返回文本。

        参数 query: 你在 search_docs 里用过的检索词（原样）。
        例：之前检索过 "TaintTracking"，现在想看完整内容，
        就调用 get_doc_detail(query="TaintTracking")。

        上下文摘要行形如 "TaintTracking: semmle.python.dataflow..."，
        冒号前面的部分就是 query 参数。
        """
        entry = ctx.entries.get(query)
        if entry is None:
            return (f"未检索过 '{query}'。请先调用 search_docs(query=['{query}']) "
                    f"检索该内容。")
        return entry["answer"]

    @tool
    def read_file(path: str) -> str:
        """读取工作区内文件的完整内容。

        可用场景：查看当前 query 代码、查看测试用例源码。
        path 支持绝对路径或相对路径（相对 result_dir）。

        约束：仅允许访问 result_dir 和测试用例目录，其他路径返回权限错误。
        """
        try:
            real = _check_path(path)
        except PermissionError as e:
            return f"错误: {e}"
        if not os.path.exists(real):
            return f"错误: 文件不存在: {real}"
        with open(real, "r", encoding="utf-8") as f:
            return f.read()

    return [search_docs, get_doc_detail, read_file]
