from config import global_config as config
from loguru import logger
import json
import torch
import os
import time
from retriever.bge_embedding import parallel_encode,sequential_encode,top_k_per_query

ast_api_db_path = "src/embedding_db/ast_api_db.pt"
ast_matcher_database=[]

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
    documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        ast_api_json = json.load(f)
    
    apilist = {}
    separator = ' '
    ast_class_list = ast_api_json['class']
    for ast_class  in ast_class_list:
        method_list = ast_class['methods']  
        class_name =  ast_class['name']    
        for method in method_list:
            method_name = method['name']
            method_name = separator.join(split_camel_case(method_name))
            class_name = separator.join(split_camel_case(class_name))
            if method['returnType'] =="bool":
                api_context =f"Check whether the {class_name} {method_name}"
                documents.append(api_context)
                apilist[api_context]=str(method['method_signature'])
            else:
                api_context =f"{method_name} of {class_name}"
                documents.append(api_context)
                apilist[api_context]=str(method['method_signature'])  

    ast_struct_list = ast_api_json['struct']
    for ast_struct  in ast_struct_list:
        method_list = ast_struct['methods']  
        struct_name =  ast_struct['name']    
        for method in method_list:
            method_name = method['name']
            method_name = separator.join(split_camel_case(method_name))
            struct_name = separator.join(split_camel_case(struct_name))
            if method['returnType'] =="bool":
                api_context =f"Check whether the {struct_name} {method_name}"
                documents.append(api_context)
                apilist[api_context]=str(method['method_signature'])
            else:
                api_context =f"{method_name} of {struct_name}"
                documents.append(api_context)
                apilist[api_context]=str(method['method_signature'])
    return apilist

# 待考虑
def embedding_ast_api():
    if os.path.exists(ast_api_db_path):
        logger.info(f"AST API embedding database already exists at {ast_api_db_path}. Skipping embedding.")
        saved =  torch.load(ast_api_db_path, weights_only=False)
        ast_matcher_database.clear()
        ast_matcher_database.extend(saved)
        # 提取文档列表
        ast_api_documents = [item['document'] for item in ast_matcher_database]

        # 提取嵌入向量列表
        sentence_embeddings = [item['embedding'] for item in ast_matcher_database]
        return ast_api_documents , sentence_embeddings
    logger.info("Starting embedding of AST API...")
    # 清空知识库
    ast_matcher_database.clear()
    # 获取知识库
    ast_api_documents=[]
    ast_api_dict= get_data(config['knowledge_base']['ast_api_path'])
    ast_api_documents=list(ast_api_dict.keys())

    embedding_start_time = time.perf_counter()
    logger.info(f"Total AST API documents to embed: {len(ast_api_documents)}")

    sentence_embeddings = parallel_encode(
        texts=ast_api_documents,
        model_path=config['embedding_model']['bge_model_path'],
        num_workers=4,
        batch_size=64,
    )
    embedding_end_time = time.perf_counter()
    logger.info(f"Completed embedding AST API documents in {embedding_end_time - embedding_start_time:.2f} seconds.")

    for doc, emb in zip(ast_api_documents, sentence_embeddings):
        ast_matcher_database.append({
            'document': doc,
            'embedding': emb,
            'api_signature': ast_api_dict[doc]
            })


    torch.save(ast_matcher_database, ast_api_db_path)