from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query

check_op_db_path = "src/embedding_db/check_op_db.pt"
check_op_database=[]

def get_data(file_path: str):
    documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        check_op_json = json.load(f)
    filter_rule = config['arguments']['filter_rule']
    for op_info in check_op_json:
        if filter_rule in op_info['reference_path']:
            continue
        documents.append(str(op_info['check_op']))
    return documents

def embedding_check_op():
    if os.path.exists(check_op_db_path):
        logger.info(f"Check Op embedding database already exists at {check_op_db_path}. Skipping embedding.")
        saved =  torch.load(check_op_db_path, weights_only=False)
        check_op_database.clear()
        check_op_database.extend(saved)
        # 提取文档列表
        check_op_documents = [item['document'] for item in check_op_database]

        # 提取嵌入向量列表
        sentence_embeddings = [item['embedding'] for item in check_op_database]
        return check_op_documents , sentence_embeddings
    logger.info("Starting embedding of Check Op...")
    # 清空知识库
    check_op_database.clear()
    # 获取知识库
    check_op_documents=[]
    check_op_documents= get_data(config['knowledge_base']['check_operation_path'])
    

    embedding_start_time = time.perf_counter()
    sentence_embeddings = sequential_encode(
        check_op_documents,
        model_path=config['embedding_model']['bge_model_path'],
        batch_size=64
    )
    embedding_end_time = time.perf_counter()
    logger.info(f"Completed embedding of {len(check_op_documents)} Check Op in {embedding_end_time - embedding_start_time:.2f} seconds.")

    for doc, emb in zip(check_op_documents, sentence_embeddings):
        check_op_database.append({
            'document': doc,
            'embedding': emb,
        })
    logger.info(f"validate: {sentence_embeddings[0].shape}")
    torch.save(check_op_database, check_op_db_path)
    return check_op_documents , sentence_embeddings

def get_related_check_op(logic_query):
    check_op_documents , sentence_embeddings = embedding_check_op()
    query_embeddings = sequential_encode(logic_query, model_path=config['embedding_model']['bge_model_path'], batch_size=1)
    topk = top_k_per_query(query_embeddings, sentence_embeddings, k=config['arguments']['top_key'])
    results = []
    for qi,row in enumerate(topk):
        logger.info(f"Query: {logic_query[qi]}")
        for rk,score_idx in enumerate(row):
            score, idx = score_idx
            results.append(check_op_documents[idx])
            logger.info(f"Top {rk+1} Check Op (Score: {score:.4f}):\n{check_op_documents[idx]}")
    return results