from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query
import numpy as np

codeql_query_op_db_path = "src/embedding_db/codeql_query_op_db.pt"
codeql_query_op_database=[]

def get_data(file_path: str):
    documents_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        check_op_json = json.load(f)
    filter_rule = config['arguments']['filter_rule']
    for op_info in check_op_json:
        if filter_rule in op_info['reference_path']:
            continue
        documents_dict[str(op_info['meta_op'])]=str(op_info['meta_impl'])
    return documents_dict

def embedding_codeql_query_op():
    if os.path.exists(codeql_query_op_db_path):
        logger.info(f"CodeQL Query Op embedding database already exists at {codeql_query_op_db_path}. Skipping embedding.")
        saved =  torch.load(codeql_query_op_db_path, weights_only=False)
        codeql_query_op_database.clear()
        codeql_query_op_database.extend(saved)
        # 提取文档列表
        codeql_query_op_documents = [item['document'] for item in codeql_query_op_database]

        # 提取嵌入向量列表
        sentence_embeddings = [item['embedding'] for item in codeql_query_op_database]
        codeql_query_op_documents_array = np.array(codeql_query_op_documents)
        sentence_embeddings_array = np.array(sentence_embeddings)
        return codeql_query_op_documents_array , sentence_embeddings_array
    logger.info("Starting embedding of CodeQL Query Op...")
    codeql_query_op_database.clear()
    # 获取知识库
    codeql_query_op_documents=[]
    codeql_query_op_documents_dict= get_data(config['codeql_knowledge_base']['codeql_query_op_path'])
    codeql_query_op_documents = list(codeql_query_op_documents_dict.keys())

    embedding_start_time = time.perf_counter()
    sentence_embeddings = sequential_encode(
        codeql_query_op_documents,
        model_path=config['embedding_model']['bge_model_path'],
        batch_size=64
    )
    embedding_end_time = time.perf_counter()
    logger.info(f"CodeQL Query Op embedding completed in {embedding_end_time - embedding_start_time:.2f} seconds.")

    for doc,emb in zip(codeql_query_op_documents, sentence_embeddings):
        codeql_query_op_database.append({
            'document': doc,
            'embedding': emb
        })
    torch.save(codeql_query_op_database, codeql_query_op_db_path)
    return codeql_query_op_documents, sentence_embeddings

def get_related_codeql_query_op(logic:str):
    codeql_query_op_doc, codeql_query_op_emb = embedding_codeql_query_op()
    query_embeddings = sequential_encode(logic, model_path=config['embedding_model']['bge_model_path'], batch_size=4)
    topk = top_k_per_query(
        query_emb=query_embeddings,
        doc_emb=codeql_query_op_emb,
        k=config['arguments']['top_key']
    )
    results = []
    codeql_query_op_documents_dict= get_data(config['codeql_knowledge_base']['codeql_query_op_path'])
    logger.info(f"Top-K results for related CodeQL Query Op retrieval:")
    for qi,row in enumerate(topk):
        logger.info(f"Logic: {logic[qi]}")
        # logger.info(f"Query: {logic_query[qi]}")
        for doc_idx , score in row:
            logger.info(f"doc_idx: {doc_idx}, score: {score:.4f}: {codeql_query_op_documents_dict[codeql_query_op_doc[doc_idx]]}")
            # logger.info(f"doc_idx: {doc_idx}, score: {score:.4f}: {check_op_documents[doc_idx]}")
            results.append(codeql_query_op_documents_dict[codeql_query_op_doc[doc_idx]])

    unique_list = list(set(results))
    return unique_list