from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query
import numpy as np
from typing import List
ast_matchers_meta_op_embedding_db_path = "src/embedding_db/ast_matchers_meta_op_db.pt"
ast_matcher_meta_op_database=[]

def get_data(file_path: str):
    documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        ast_matcher_meta_op_json = json.load(f)
    filter_rule = config['arguments']['filter_rule']
    for op_info in ast_matcher_meta_op_json:
        if filter_rule in op_info['reference_path']:
            continue
        documents.append(str(op_info['meta_op']))
    return documents


def embedding_ast_matchers_meta_op():
    if os.path.exists(ast_matchers_meta_op_embedding_db_path):
        logger.info(f"AST Matchers Meta Op embedding database already exists at {ast_matchers_meta_op_embedding_db_path}. Skipping embedding.")
        saved =  torch.load(ast_matchers_meta_op_embedding_db_path, weights_only=False)
        ast_matcher_meta_op_database.clear()
        ast_matcher_meta_op_database.extend(saved)
        # 提取文档列表
        ast_matchers_meta_op_documents = [item['document'] for item in ast_matcher_meta_op_database]

        # 提取嵌入向量列表
        sentence_embeddings = [item['embedding'] for item in ast_matcher_meta_op_database]
        ast_matchers_meta_op_documents_array = np.array(ast_matchers_meta_op_documents)
        sentence_embeddings_array = np.array(sentence_embeddings)
        return ast_matchers_meta_op_documents_array , sentence_embeddings_array
    logger.info("Starting embedding of AST Matchers Meta Op...")
    # 清空知识库
    ast_matcher_meta_op_database.clear()
    # 获取知识库
    ast_matchers_meta_op_documents=[]
    ast_matchers_meta_op_documents= get_data(config['knowledge_base']['ast_matcher_meta_operation_path'])
    

    embedding_start_time = time.perf_counter()
    sentence_embeddings = sequential_encode(
        ast_matchers_meta_op_documents,
        model_path=config['embedding_model']['bge_model_path'],
        batch_size=64
    )
    embedding_end_time = time.perf_counter()
    logger.info(f"Completed embedding of {len(ast_matchers_meta_op_documents)} AST Matchers Meta Op in {embedding_end_time - embedding_start_time:.2f} seconds.")

    for doc, emb in zip(ast_matchers_meta_op_documents, sentence_embeddings):
        ast_matcher_meta_op_database.append({
            'document': doc,
            'embedding': emb,
        })
    logger.info(f"validate: {sentence_embeddings[0].shape}")
    torch.save(ast_matcher_meta_op_database, ast_matchers_meta_op_embedding_db_path)
    return ast_matchers_meta_op_documents , sentence_embeddings
def get_impl_form_op(meta_op:List[str]):
    with open(config['knowledge_base']['ast_matcher_meta_operation_path'], 'r', encoding='utf-8') as f:
        ast_matcher_meta_op_json = json.load(f)
    result = []
    for op_info in ast_matcher_meta_op_json:
        if  str(op_info['meta_op']) in meta_op:
            logger.info(f"Found implementation for meta op: {op_info['meta_op']}")
            result.append(op_info['meta_impl'])
    return result
def get_related_astMatchers_meta_op(logic_query):
    ast_matchers_meta_op_documents , sentence_embeddings = embedding_ast_matchers_meta_op()
    query_embeddings = sequential_encode(logic_query, model_path=config['embedding_model']['bge_model_path'], batch_size=1)
    topk = top_k_per_query(query_embeddings, sentence_embeddings, k=config['arguments']['top_key'])
    results = []
    for qi,row in enumerate(topk):
        # logger.info(f"Query {qi}: '{logic_query[qi]}' top {config['arguments']['top_key']} AST Matchers Meta Op:")
        for doc_idx, score in row:
            results.append(ast_matchers_meta_op_documents[doc_idx])
    unique_list = list(set(results))
    result = get_impl_form_op(unique_list)
    return result 