"""统一检索层 — 根据 LanguageConfig.retrieval_mode 分发到不同检索路径。

- "legacy"   → 复用现有 C++ 检索（retrieve_from_codeql_api / op / doc）
- "chromadb" → 全部走 ChromaDB，doc 维度多 collection 各取 top_k 合并
"""

from typing import List

from loguru import logger

# Legacy (C++) 检索 — 不动现有代码，直接 import
from retriever.retrieve_from_codeql_api import get_related_api as _cpp_get_api
from retriever.retrieve_from_codeql_op import get_related_codeql_query_op as _cpp_get_query_op
from retriever.retrieve_from_codeql_doc import get_related_doc as _cpp_get_doc

# ChromaDB 检索
from retriever.bge_embedding import sequential_encode
from codeql_language_config import LanguageConfig, PYTHON_CONFIG
from config import get_chroma_client

# BGE 模型路径
_MODEL_PATH = "/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5"

# Python ChromaDB 检索配置
_PYTHON_DOC_COLLECTIONS = [
    "python_codeql_stdlib",
    "python_codeql_language_guides",
    "python_codeql_local_queries",
    "codeql_ql_reference",
]

_PYTHON_API_COLLECTIONS: list = []        # 待采集 python-all qlpack API 签名

_PYTHON_QUERYOP_COLLECTIONS: list = []   # 待将 codeql_query_op.json 导入 ChromaDB

_top_key = 2  # 每个 collection 检索的文档数（从 5 降到 2，控制 prompt 大小）


def _query_chroma_collections(query_texts: List[str],
                               collection_names: List[str],
                               top_k: int = _top_key) -> List[str]:
    """批量检索：一次性编码所有 query，再对每个 collection 做 ChromaDB 查询。"""
    if not collection_names:
        return []

    # 批量编码所有 query text（远远快于逐条 batch_size=1 调用）
    if len(query_texts) > 1:
        query_embs = sequential_encode(query_texts, _MODEL_PATH, batch_size=min(len(query_texts), 128))
    else:
        query_embs = sequential_encode(query_texts, _MODEL_PATH, batch_size=1)

    client = get_chroma_client()
    # 预加载各 collection，避免每条 query 都 get_collection
    collections_cache = {}
    for coll_name in collection_names:
        try:
            collections_cache[coll_name] = client.get_collection(name=coll_name)
        except Exception:
            logger.debug(f"Collection '{coll_name}' not found, skipping")

    all_results: List[str] = []
    for i, query_text in enumerate(query_texts):
        query_emb = query_embs[i].tolist()
        for coll_name in collection_names:
            coll = collections_cache.get(coll_name)
            if coll is None:
                continue
            try:
                res = coll.query(query_embeddings=[query_emb], n_results=top_k)
                docs = res.get("documents", [[]])[0]
                all_results.extend(docs)
            except Exception:
                logger.debug(f"Query failed on '{coll_name}', skipping")

    # 去重保序
    seen = set()
    unique = []
    for doc in all_results:
        if doc not in seen:
            seen.add(doc)
            unique.append(doc)
    return unique


# ── 对外接口（与现有函数签名兼容）──────────────────────────

def get_related_api_uniform(logics: List[str], lang_config: LanguageConfig) -> List[str]:
    """按语言策略检索相关的 CodeQL API 上下文。"""
    if lang_config.retrieval_mode == "chromadb":
        return _query_chroma_collections(logics, _PYTHON_API_COLLECTIONS, top_k=_top_key)
    else:
        return _cpp_get_api(logics)


def get_related_doc_uniform(logics: List[str], lang_config: LanguageConfig) -> List[str]:
    """按语言策略检索相关的 CodeQL 文档上下文。"""
    if lang_config.retrieval_mode == "chromadb":
        return _query_chroma_collections(logics, _PYTHON_DOC_COLLECTIONS, top_k=_top_key)
    else:
        return _cpp_get_doc(logics)


def get_related_query_op_uniform(logics: List[str], lang_config: LanguageConfig) -> List[str]:
    """按语言策略检索相关的 CodeQL 查询操作上下文。"""
    if lang_config.retrieval_mode == "chromadb":
        return _query_chroma_collections(logics, _PYTHON_QUERYOP_COLLECTIONS, top_k=_top_key)
    else:
        return _cpp_get_query_op(logics)


def get_most_similar_api_doc_query_op_uniform(logics_json, lang_config: LanguageConfig):
    """统一检索入口 — 根据语言配置返回 (api_suggest, doc_suggest, query_op_suggest)。

    与现有 get_most_similar_api_doc_query_op 签名格式兼容：
    - logics_json: LLM 返回的 logics JSON
    - lang_config: LanguageConfig 实例
    """
    from help.code_ql_utils import get_logic_json

    api_suggest_string = ""
    doc_suggest_string = ""
    query_op_suggest_string = ""

    logics_for_codeql_query = get_logic_json(logics_json)

    related_api = get_related_api_uniform(logics_for_codeql_query, lang_config)
    related_doc = get_related_doc_uniform(logics_for_codeql_query, lang_config)
    related_query_op = get_related_query_op_uniform(logics_for_codeql_query, lang_config)

    for a in related_api:
        api_suggest_string += a + "\n"
    for d in related_doc:
        doc_suggest_string += d + "\n"
    for q in related_query_op:
        query_op_suggest_string += q + "\n"

    return api_suggest_string, doc_suggest_string, query_op_suggest_string


def get_suggest_string_from_hint_uniform(hint: list, lang_config: LanguageConfig):
    """从 hint 列表检索上下文的统一入口。"""
    api_suggest_string = ""
    doc_suggest_string = ""
    query_op_suggest_string = ""

    related_api = get_related_api_uniform(hint, lang_config)
    related_doc = get_related_doc_uniform(hint, lang_config)
    related_query_op = get_related_query_op_uniform(hint, lang_config)

    for a in related_api:
        api_suggest_string += a + "\n"
    for d in related_doc:
        doc_suggest_string += d + "\n"
    for q in related_query_op:
        query_op_suggest_string += q + "\n"

    return api_suggest_string, doc_suggest_string, query_op_suggest_string
