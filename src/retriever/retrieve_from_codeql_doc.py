# 根据query检索最相关的doc片段
# Embedding 模型: /root/code_check/src/retriever/embedding_model/bge-large-en-v1.5
# Chroma 向量库: /root/code_check/src/retriever/vector_db/codeql_doc_vector_db

from __future__ import annotations

from bge_embedding import sequential_encode
from typing import List, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from dataclasses import dataclass


MODEL_PATH = Path("/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5")
VECTOR_DB_PATH = Path("/root/code_check/src/retriever/vector_db/codeql_doc_vector_db")
COLLECTION_NAME = "codeql_docs"


@dataclass
class RetrievedDoc:
    rank: int
    text: str
    source: str | None = None
    chunk_id: str | None = None
    similarity: float | None = None
    distance: float | None = None


def _ensure_resources() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"模型路径不存在: {MODEL_PATH}")
    if not VECTOR_DB_PATH.exists():
        raise FileNotFoundError(f"向量库路径不存在: {VECTOR_DB_PATH}")


def _distance_to_similarity(distance: float | None) -> float | None:
    if isinstance(distance, (int, float)):
        return 1.0 / (1.0 + distance)
    return None


def retrieve_relevant_doc(query: str, top_k: int = 5) -> List[RetrievedDoc]:
    """Embed the query and fetch the top-k CodeQL doc chunks from Chroma."""
    _ensure_resources()
    client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH), settings=Settings())
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        raise RuntimeError(f"无法加载集合 {COLLECTION_NAME}: {error}") from error
    query_embedding = sequential_encode([query], str(MODEL_PATH), batch_size=16)[0].tolist()
    result = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    documents: List[str] = result.get("documents", [[]])[0]
    metadatas: List[Dict[str, Any]] = result.get("metadatas", [[]])[0]
    distances_container = result.get("distances", [[]])
    distances = distances_container[0] if distances_container else [None] * len(documents)
    retrieved: List[RetrievedDoc] = []
    for idx, doc in enumerate(documents):
        meta = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None
        retrieved.append(
            RetrievedDoc(
                rank=idx + 1,
                text=doc,
                source=meta.get("source"),
                chunk_id=meta.get("chunk_id"),
                similarity=_distance_to_similarity(distance),
                distance=distance,
            )
        )
    return retrieved

if __name__ == "__main__":
    query = "Finding every private field and checking for initialization"
    relevant_docs = retrieve_relevant_doc(query, top_k=3)
    if not relevant_docs:
        print("未检索到相关文档片段。")
    else:
        for doc in relevant_docs:
            sim = f"{doc.similarity:.4f}" if isinstance(doc.similarity, float) else "-"
            print(f"[Top {doc.rank}] similarity={sim} source={doc.source} chunk={doc.chunk_id}")
            print(doc.text)
            print("-" * 80)

