from sentence_transformers import SentenceTransformer
import numpy as np
import math
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from typing import List, Tuple

# Worker globals
_worker_model = None
_worker_batch_size = None


def _init_worker(model_path: str, batch_size: int):
    """Initializer for worker processes: load model once per process."""
    global _worker_model, _worker_batch_size
    _worker_batch_size = batch_size
    _worker_model = SentenceTransformer(model_path, device='cpu')


def _encode_chunk_worker(texts: List[str]):
    """Encode a chunk inside worker process using the cached model."""
    # Access globals initialized by _init_worker
    global _worker_model, _worker_batch_size
    if _worker_model is None:
        raise RuntimeError("Worker not initialized with model")
    return _worker_model.encode(
        texts,
        batch_size=_worker_batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def _split_chunks(texts: List[str], num_chunks: int) -> List[List[str]]:
    n = len(texts)
    if n == 0:
        return []
    chunk_size = max(1, math.ceil(n / num_chunks))
    return [texts[i:i + chunk_size] for i in range(0, n, chunk_size)]


def parallel_encode(texts: List[str], model_path: str, num_workers: int = None, batch_size: int = 64) -> np.ndarray:
    """Encode a list of texts in parallel using a process pool.

    Each worker process loads the model once. Returns a numpy array of embeddings.
    """
    if texts is None:
        return np.empty((0, 0))
    n = len(texts)
    if n == 0:
        return np.empty((0, 0))

    if num_workers is None:
        num_workers = max(1, min(4, cpu_count()))
    num_workers = max(1, int(num_workers))

    # If small workload, do single-process encode to avoid model copies
    if num_workers <= 1 or n <= batch_size * 2:
        model = SentenceTransformer(model_path, device='cpu')
        return model.encode(texts, batch_size=batch_size, convert_to_numpy=True, normalize_embeddings=True)

    chunks = _split_chunks(texts, num_workers)

    with ProcessPoolExecutor(max_workers=num_workers, initializer=_init_worker, initargs=(model_path, batch_size)) as exe:
        futures = [exe.submit(_encode_chunk_worker, chunk) for chunk in chunks]
        results = [f.result() for f in futures]

    return np.vstack(results)


def sequential_encode(texts: List[str], model_path: str, batch_size: int = 64) -> np.ndarray:
    """Encode texts sequentially in the current process (no parallelism).

    Useful when running on a single CPU/GPU or to avoid the memory overhead of
    spawning multiple processes that each load a model copy.
    """
    if texts is None:
        return np.empty((0, 0))
    n = len(texts)
    if n == 0:
        return np.empty((0, 0))

    model = SentenceTransformer(model_path, device='cpu')
    return model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def top_k_per_query(query_emb: np.ndarray, doc_emb: np.ndarray, k: int = 3) -> List[List[Tuple[int, float]]]:
    """For each query embedding, find top-k most similar documents (cosine similarity).

    Assumes embeddings are normalized (so dot product = cosine similarity).
    Returns a list (len = num_queries) of lists of (doc_index, score) sorted by score desc.
    """
    if query_emb.size == 0 or doc_emb.size == 0:
        return [[] for _ in range(query_emb.shape[0])]

    sims = np.dot(query_emb, doc_emb.T)
    num_queries = sims.shape[0]
    k = min(k, doc_emb.shape[0])
    results = []
    for i in range(num_queries):
        row = sims[i]
        # get top-k indices
        idx = np.argpartition(-row, k-1)[:k]
        top_idx = idx[np.argsort(-row[idx])]
        results.append([(int(j), float(row[j])) for j in top_idx])
    return results


def run_example():
    model_path = "/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5"

    queries = [
        "how to implement binary search algorithm",
        "what is gradient descent in machine learning",
    ]

    documents = [
        "Binary search is an efficient algorithm for finding an item from a sorted list of items.",
        "Gradient descent is an optimization algorithm used to minimize some function.",
        "Python is a popular programming language for machine learning.",
    ]

    print("Encoding queries (parallel)...")
    q_emb = sequential_encode(queries, model_path, batch_size=32)
    print(q_emb.shape)
    # (2,1024)
    print("Encoding documents (parallel)...")
    d_emb = sequential_encode(documents, model_path, batch_size=32)

    print("Computing top-k similarities...")
    k = 2
    topk = top_k_per_query(q_emb, d_emb, k=k)

    for qi, row in enumerate(topk):
        print(f"Query {qi}: '{queries[qi]}' top {k} docs:")
        for doc_idx, score in row:
            print(f"  doc {doc_idx} (score={score:.4f}): {documents[doc_idx]}")


# if __name__ == "__main__":
#     run_example()
