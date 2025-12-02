from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query
import numpy as np


# from retriever.chromadb_utils import chromadb_client
ast_matchers_embedding_db_path = "src/embedding_db/ast_matchers_db.pt"
ast_matcher_database=[]
ast_matcher_dict_path = "src/embedding_db/ast_matchers_dict.pt"

def get_data(file_path: str):
    # if os.path.exists(ast_matcher_dict_path):
    #     logger.info(f"Loading AST Matchers data from cached file at {ast_matcher_dict_path}.")
    #     return torch.load(ast_matcher_dict_path)
    documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        ast_matcher_json = json.load(f)
    for ast_matcher in ast_matcher_json:
        if 'Node Matchers' in ast_matcher:
            node_matchers = ast_matcher['Node Matchers']
            node_matchers_list = node_matchers['matchers']
            for matcher in node_matchers_list:
                matchers_comment = f"Node Matcher: {matcher['name']}\n Parameters;{matcher['Parameters']}\n return type {matcher['return type']}\n Description: {matcher['description']}\n"
                documents.append(matchers_comment)
        elif 'Narrowing Matchers' in ast_matcher:
            narrowing_matchers = ast_matcher['Narrowing Matchers']
            narrowing_matchers_list = narrowing_matchers['matchers']
            for matcher in narrowing_matchers_list:
                matchers_comment = f"Narrowing Matcher: {matcher['name']}\n Parameters;{matcher['Parameters']}\n return type {matcher['return type']}\n Description: {matcher['description']}\n"
                documents.append(matchers_comment)
        elif 'AST Traversal Matchers' in ast_matcher:
            ast_traversal_matchers = ast_matcher['AST Traversal Matchers']
            ast_traversal_matchers_list = ast_traversal_matchers['matchers']
            for matcher in ast_traversal_matchers_list:
                matchers_comment = f"AST Traversal Matcher: {matcher['name']}\n Parameters;{matcher['Parameters']}\n Return type {matcher['return type']}\n Description: {matcher['description']}\n"
                documents.append(matchers_comment)
    return documents

def embedding_ast_matchers():
    if os.path.exists(ast_matchers_embedding_db_path):
        logger.info(f"AST Matchers embedding database already exists at {ast_matchers_embedding_db_path}. Skipping embedding.")
        saved =  torch.load(ast_matchers_embedding_db_path, weights_only=False)
        ast_matcher_database.clear()
        ast_matcher_database.extend(saved)
        # 提取文档列表
        ast_matchers_documents = [item['document'] for item in ast_matcher_database]

        # 提取嵌入向量列表
        sentence_embeddings = [item['embedding'] for item in ast_matcher_database]
        ast_matchers_documents_array = np.array(ast_matchers_documents)
        sentence_embeddings_array = np.array(sentence_embeddings)
        return ast_matchers_documents_array , sentence_embeddings_array
    logger.info("Starting embedding of AST Matchers...")
    # 清空知识库
    ast_matcher_database.clear()
    # 获取知识库
    ast_matchers_documents=[]
    ast_matchers_documents= get_data(config['knowledge_base']['astMatcher_api_path'])
    

    embedding_start_time = time.perf_counter()
    logger.info(f"Total AST Matchers documents to embed: {len(ast_matchers_documents)}")
    sentence_embeddings = sequential_encode(ast_matchers_documents, model_path=config['embedding_model']['bge_model_path'], batch_size=64)

    emvbedding_end_time = time.perf_counter()
    logger.info(f"Embedding completed in {emvbedding_end_time - embedding_start_time:.2f} seconds.")
    logger.info(f"Generated embeddings shape: {sentence_embeddings.shape}")
    for i, doc in enumerate(ast_matchers_documents):
        ast_matcher_database.append({
            'document': doc,
            'embedding': sentence_embeddings[i]
        })
    logger.info(f"validate: {sentence_embeddings[0].shape}")
    torch.save(ast_matcher_database, ast_matchers_embedding_db_path)
    return ast_matchers_documents , sentence_embeddings

def get_related_astMatchers(logic_query):
    ast_matchers_documents , sentence_embeddings = embedding_ast_matchers()
    query_embeddings = sequential_encode(logic_query, model_path=config['embedding_model']['bge_model_path'], batch_size=1)
    topk = top_k_per_query(query_embeddings, sentence_embeddings, k=config['arguments']['top_key'])
    results = []
    for qi,row in enumerate(topk):
        logger.info(f"Query {qi}: '{logic_query[qi]}' top {config['arguments']['top_key']} AST Matchers:")
        for doc_idx, score in row:
            results.append(ast_matchers_documents[doc_idx])
    unique_list = list(set(results))
    return unique_list    