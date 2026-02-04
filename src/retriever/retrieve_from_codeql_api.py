from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query
import numpy as np
# 对API列表进行向量化处理后保存为pt文件，方便后续加载
codeql_api_db_path = "src/embedding_db/codeql_api_db.pt"

codeql_api_database = []

# 从json文件中提取API列表，保存为pt文件，方便后续加载
codeql_api_list_path = "src/embedding_db/codeql_api_list.pt"
def split_camel_case(method_name: str):
    words = []
    start_index = 0
    for i in range(1, len(method_name)):
        if method_name[i].isupper():
            if i - start_index >= 2:
                words.append(method_name[start_index:i].lower())
                start_index = i
    words.append(method_name[start_index:].lower())
    return words

def get_data(file_path: str):
    if os.path.exists(codeql_api_list_path):
        logger.info(f"API list already exists at {codeql_api_list_path}. Loading existing data.")
        apilist = {}
        apilist = torch.load(codeql_api_list_path, weights_only=False)
        return apilist
    # documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        codeql_api_json = json.load(f)


    apilist = {}
    separator = ' '
    predicate_list = codeql_api_json['predicate']
    for predicate in predicate_list:
        predicate_name = predicate['name']
    
        api_context = f"Predicate {predicate_name}\nDescription: {predicate['comments']}\nSignature: {predicate['signature']}"
        # documents.append(api_context)
        apilist[api_context] = str(predicate['signature'])

    class_list = codeql_api_json['class']
    for cls in class_list:
        class_name = cls['name']
        class_comment = cls['comments']
        class_predicate_list = cls['predicate']
        class_method_list = cls['method']
        for predicate in class_predicate_list:
            predicate_name = predicate['name']
            api_context = f"Predicate {predicate_name} of class {class_name}\nDescription: {predicate['comments']}\nSignature: {predicate['signature']}"
            # documents.append(api_context)
            apilist[api_context] = str(predicate['signature'])
        for method in class_method_list:
            method_name = method['name']
            api_context = f"Method {method_name} of class {class_name}\nDescription: {method['comments']}\nSignature: {method['signature']}"
            # documents.append(api_context)
            apilist[api_context] = str(method['signature'])
    torch.save(apilist, codeql_api_list_path)
    return apilist
def embedding_ast_api():
    if os.path.exists(codeql_api_db_path):
        logger.info(f"CodeQL API database already exists at {codeql_api_db_path}. Skipping embedding.")
        saved = torch.load(codeql_api_db_path, weights_only=False)
        codeql_api_database.clear()
        codeql_api_database.extend(saved)

        codeql_api_documents = [item['document'] for item in codeql_api_database]
        sentence_embeddings = [item['embedding'] for item in codeql_api_database]
        codeql_api_documents_array = np.array(codeql_api_documents)
        sentence_embeddings_array = np.array(sentence_embeddings)
        return codeql_api_documents_array, sentence_embeddings_array,codeql_api_database

    logger.info("Starting embedding of CodeQL API...")
    codeql_api_database.clear()
    codeql_api_documents = []
    codeql_api_list = get_data(config['codeql_knowledge_base']['codeql_api_path'])
    codeql_api_documents = list(codeql_api_list.keys())

    embedding_start_time = time.perf_counter()
    logger.info(f"Total CodeQL API documents to embed: {len(codeql_api_documents)}")

    sentence_embeddings = parallel_encode(
        texts=codeql_api_documents,
        model_path=config['embedding_model']['bge_model_path'],
        num_workers=4,
        batch_size=64,
    )

    embedding_end_time = time.perf_counter()
    logger.info(f"Completed embedding CodeQL API documents in {embedding_end_time - embedding_start_time:.2f} seconds.")
    for doc, emb in zip(codeql_api_documents, sentence_embeddings):
        codeql_api_database.append({
            'document': doc,
            'embedding': emb,
            'api_signature': codeql_api_list[doc]
            })
        
    torch.save(codeql_api_database, codeql_api_db_path)
    return codeql_api_documents , sentence_embeddings,codeql_api_database

def get_related_api(logic_for_ast_api:list):
    """根据逻辑描述，检索相关的CodeQL API上下文"""
    api_documents, api_embeddings, _ = embedding_ast_api()

    logics_embeddings = sequential_encode(logic_for_ast_api,
        model_path=config['embedding_model']['bge_model_path'],
        batch_size=64,)
    
    codeql_api_list = get_data(config['codeql_knowledge_base']['codeql_api_path'])
    related_api = []
    top_k_results = top_k_per_query(
        query_emb=logics_embeddings,
        doc_emb=api_embeddings,
        k  = config['arguments']['top_key']
    )
    for qi,row in enumerate(top_k_results):
        for doc_idx,score in row:
            related_api.append( codeql_api_list[api_documents[doc_idx]] )
    unique_list = list(set(related_api))
    return unique_list
  