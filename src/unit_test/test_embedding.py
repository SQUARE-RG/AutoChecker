# from sentence_transformers import SentenceTransformer
# import numpy as np
# import os

# # 设置环境变量（可选，加速下载）
# os.environ['HF_ENDPOINT'] = "https://hf-mirror.com"

# # 加载本地模型，明确指定使用CPU
# model_path = "/root/code_check/src/retriever/embeding_model/bge-large-en-v1.5"  # 替换为你的实际路径
# model = SentenceTransformer(model_path, device='cpu')

# # 准备示例文本（代码和英文文本混合）
# texts = [
#     "def calculate_sum(a, b):\n    return a + b",
#     "This function computes the square of a number.",
#     "class DataProcessor:\n    def __init__(self):\n        self.data = []",
#     "Natural language processing with transformer models."
# ]

# # 生成嵌入向量
# embeddings = model.encode(texts, show_progress_bar=True)

# print(f"嵌入向量形状: {embeddings.shape}")
# print(f"向量维度: {embeddings[0].shape}")

# # 计算相似度
# similarities = np.dot(embeddings, embeddings.T)
# print("文本间相似度矩阵:")
# print(similarities)


from sentence_transformers import SentenceTransformer
import numpy as np
import math
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# Worker globals (populated in each worker process by initializer)
_worker_model = None
_worker_batch_size = None


def _init_worker(model_path: str, batch_size: int):
    """Initializer run in each worker process to load the model once."""
    global _worker_model, _worker_batch_size
    _worker_batch_size = batch_size
    _worker_model = SentenceTransformer(model_path, device='cpu')


def _encode_chunk_worker(texts):
    """Encode a chunk of texts in a worker process using the cached model."""
    # Access globals initialized by _init_worker
    global _worker_model, _worker_batch_size
    if _worker_model is None:
        raise RuntimeError("Worker model not initialized")
    return _worker_model.encode(
        texts,
        batch_size=_worker_batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


class BGEEncoderCPU:
    """Encoder that parallelizes encoding of many small texts using a process pool.

    Each worker process loads its own SentenceTransformer instance once (via
    initializer) and encodes chunks assigned to it. This is efficient when there
    are many small documents and model loading cost is amortized across tasks.
    """

    def __init__(self, model_path: str, num_workers: int | None = None, batch_size: int = 64):
        self.model_path = model_path
        self.batch_size = batch_size
        if num_workers is None:
            self.num_workers = max(1, min(4, cpu_count()))
        else:
            self.num_workers = max(1, int(num_workers))

    def _split_chunks(self, texts, num_chunks):
        n = len(texts)
        if n == 0:
            return []
        chunk_size = max(1, math.ceil(n / num_chunks))
        return [texts[i:i + chunk_size] for i in range(0, n, chunk_size)]

    def encode_documents(self, documents):
        """Encode a list of documents in parallel (optimized for many small docs)."""
        if not documents:
            return np.empty((0, 0))

        # If only one worker or small number of documents, do single-process encode
        if self.num_workers <= 1 or len(documents) <= self.batch_size * 2:
            model = SentenceTransformer(self.model_path, device='cpu')
            return model.encode(
                documents,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

        # Create chunks for workers
        chunks = self._split_chunks(documents, self.num_workers)

        with ProcessPoolExecutor(max_workers=self.num_workers, initializer=_init_worker, initargs=(self.model_path, self.batch_size)) as exe:
            futures = [exe.submit(_encode_chunk_worker, chunk) for chunk in chunks]
            results = [f.result() for f in futures]

        return np.vstack(results)

    def encode_queries(self, queries):
        """Encode queries (with instruction prefix)."""
        instruction = "Represent this sentence for searching relevant passages: "
        instruction_queries = [instruction + q for q in queries]
        return self.encode_documents(instruction_queries)

    def calculate_similarity(self, queries, documents):
        """Compute similarity matrix between queries and documents."""
        query_embeddings = self.encode_queries(queries)
        doc_embeddings = self.encode_documents(documents)
        return np.dot(query_embeddings, doc_embeddings.T)

# 使用示例
encoder = BGEEncoderCPU("/root/code_check/src/retriever/embeding_model/bge-large-en-v1.5")

queries = [
    "how to implement binary search algorithm",
    "what is gradient descent in machine learning"
]

documents = [
    "Binary search is an efficient algorithm for finding an item from a sorted list of items.",
    "Gradient descent is an optimization algorithm used to minimize some function.",
    "Python is a popular programming language for machine learning."
]

similarities = encoder.calculate_similarity(queries, documents)
print("查询-文档相似度矩阵:")
print(similarities)




# from sentence_transformers import SentenceTransformer
# import numpy as np
# from concurrent.futures import ProcessPoolExecutor, as_completed
# from multiprocessing import cpu_count
# import math

# class BGEEncoderCPU:
#     def __init__(self, model_path):
#         self.model = SentenceTransformer(model_path, device='cpu')
#         self.model_path = model_path
        
#     def encode_queries(self, queries, batch_size=32, num_workers=None):
#         """编码查询（添加检索指令）- 并行版本"""
#         instruction = "Represent this sentence for searching relevant passages: "
#         instruction_queries = [instruction + q for q in queries]
#         return self._encode_parallel(instruction_queries, batch_size, num_workers)
    
#     def encode_documents(self, documents, batch_size=32, num_workers=None):
#         """编码文档（不添加指令）- 并行版本"""
#         return self._encode_parallel(documents, batch_size, num_workers)
    
#     def _encode_parallel(self, texts, batch_size=32, num_workers=None):
#         """
#         并行编码文本的核心方法
#         """
#         if num_workers is None:
#             num_workers = min(cpu_count(), 8)  # 限制最大进程数
        
#         if len(texts) < batch_size * 2:  # 文本数量较少时使用单进程
#             return self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
        
#         # 将文本分成多个块
#         chunks = self._split_into_chunks(texts, num_workers)
        
#         # 使用多进程并行处理
#         with ProcessPoolExecutor(max_workers=num_workers) as executor:
#             futures = {}
            
#             # 提交所有任务
#             for i, chunk in enumerate(chunks):
#                 future = executor.submit(self._encode_chunk, chunk, batch_size)
#                 futures[future] = i
            
#             # 收集结果
#             results = [None] * len(chunks)
#             for future in as_completed(futures):
#                 chunk_index = futures[future]
#                 try:
#                     results[chunk_index] = future.result()
#                 except Exception as e:
#                     print(f"处理块 {chunk_index} 时出错: {e}")
#                     # 出错时使用单进程处理该块
#                     results[chunk_index] = self.model.encode(
#                         chunks[chunk_index], 
#                         batch_size=batch_size, 
#                         show_progress_bar=False, 
#                         normalize_embeddings=True
#                     )
        
#         # 合并所有结果
#         return np.vstack(results)
    
#     def _split_into_chunks(self, texts, num_chunks):
#         """将文本列表分成多个块"""
#         chunk_size = math.ceil(len(texts) / num_chunks)
#         chunks = []
#         for i in range(0, len(texts), chunk_size):
#             chunks.append(texts[i:i + chunk_size])
#         return chunks
    
#     def _encode_chunk(self, texts, batch_size):
#         """处理单个文本块的函数（在每个子进程中运行）"""
#         # 每个子进程需要重新加载模型
#         model = SentenceTransformer(self.model_path, device='cpu')
#         return model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
    
#     def calculate_similarity(self, queries, documents, batch_size=32, num_workers=None):
#         """计算查询和文档之间的相似度 - 并行版本"""
#         query_embeddings = self.encode_queries(queries, batch_size, num_workers)
#         doc_embeddings = self.encode_documents(documents, batch_size, num_workers)
        
#         similarity_scores = np.dot(query_embeddings, doc_embeddings.T)
#         return similarity_scores

#     def encode_parallel_optimized(self, texts, batch_size=64, max_workers=None):
#         """
#         优化版本的并行编码，自动调整参数
#         """
#         if max_workers is None:
#             max_workers = min(cpu_count(), 4)  # 保守设置，避免内存溢出
        
#         total_texts = len(texts)
#         if total_texts < 100:  # 文本数量少时使用单进程
#             return self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
        
#         # 动态调整批处理大小
#         optimal_batch_size = self._get_optimal_batch_size(total_texts, batch_size, max_workers)
        
#         # 使用更精细的并行策略
#         chunk_size = max(10, total_texts // (max_workers * 2))
#         chunks = [texts[i:i + chunk_size] for i in range(0, total_texts, chunk_size)]
        
#         with ProcessPoolExecutor(max_workers=max_workers) as executor:
#             futures = [executor.submit(self._encode_chunk, chunk, optimal_batch_size) for chunk in chunks]
            
#             results = []
#             for future in as_completed(futures):
#                 try:
#                     results.append(future.result())
#                 except Exception as e:
#                     print(f"处理块时出错: {e}")
#                     # 备用方案：主进程处理
#                     chunk_index = futures.index(future)
#                     results.append(self.model.encode(
#                         chunks[chunk_index], 
#                         batch_size=optimal_batch_size, 
#                         normalize_embeddings=True
#                     ))
        
#         return np.vstack(results)
    
#     def _get_optimal_batch_size(self, total_texts, base_batch_size, max_workers):
#         """根据文本数量和可用资源计算最优批处理大小"""
#         if total_texts < 1000:
#             return min(base_batch_size, 32)
#         elif total_texts < 10000:
#             return min(base_batch_size, 64)
#         else:
#             return min(base_batch_size, 128)

# # 使用示例
# if __name__ == "__main__":
#     # 初始化编码器
#     encoder = BGEEncoderCPU("/root/code_check/src/retriever/embeding_model/bge-large-en-v1.5")
    
#     queries = [
#         "how to implement binary search algorithm",
#         "what is gradient descent in machine learning"
#     ]
    
#     documents = [
#         "Binary search is an efficient algorithm for finding an item from a sorted list of items.",
#         "Gradient descent is an optimization algorithm used to minimize some function.",
#         "Python is a popular programming language for machine learning."
#     ]
    
#     print("=== 原始方法（单进程）===")
#     similarities = encoder.calculate_similarity(queries, documents)
#     print("查询-文档相似度矩阵:")
#     print(similarities)
    
#     print("\n=== 并行方法 ===")
#     # 使用并行编码
#     similarities_parallel = encoder.calculate_similarity(
#         queries, documents, 
#         batch_size=32, num_workers=4
#     )
#     print("并行计算后的相似度矩阵:")
#     print(similarities_parallel)
    
#     # 测试大量文本的并行处理
#     print("\n=== 大量文本并行处理测试 ===")
#     large_documents = documents * 100  # 生成300个文档
#     print(f"处理 {len(large_documents)} 个文档...")
    
#     # 使用优化后的并行方法
#     doc_embeddings = encoder.encode_parallel_optimized(
#         large_documents, 
#         batch_size=64, 
#         max_workers=4
#     )
#     print(f"嵌入向量形状: {doc_embeddings.shape}")