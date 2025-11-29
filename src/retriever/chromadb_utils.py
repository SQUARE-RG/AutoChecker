# import chromadb


# # 使用 PersistentClient 将数据持久化到本地目录（推荐）
# # 这样即使程序重启，数据也不会丢失
# def initialize_chromadb_client():
#     client = chromadb.PersistentClient(path="/root/code_check/src/embedding_db")
#     return client
# chromadb_client = initialize_chromadb_client()



import chromadb
from bge_embedding import sequential_encode
chroma_client = chromadb.PersistentClient(path="/root/code_check/src/embedding_db")

# collection = chroma_client.create_collection(name="my_collection")
# doc =["This is a document about engineer", "This is a document about steak"]
# doc_embeddings = sequential_encode(doc, model_path="/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5", batch_size=2)
# query = ["Which food is the best?"]
# query_embeddings = sequential_encode(query, model_path="/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5", batch_size=1)
# collection.add(
#     documents=["This is a document about engineer", "This is a document about steak"],
#     embeddings=doc_embeddings,
#     ids=["id1", "id2"]
# )

# results = collection.query(
#     query_embeddings=query_embeddings,
#     n_results=2
# )

# # 打印结果
# print("最相关的 AST Matcher 是：")
# for i, doc in enumerate(results['documents'][0]):
#     print(f"{i+1}. {doc}")
#     print(f"   相似度距离: {results['distances'][0][i]:.4f}") # 距离越小越相似



new_collection = chroma_client.get_collection(name="my_collection")

new_query = ["What is engineering?"]
new_query_embeddings = sequential_encode(new_query, model_path="/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5", batch_size=1)
new_results = new_collection.query(
    query_embeddings=new_query_embeddings,
    n_results=2
)
print("最相关的 AST Matcher 是：")
for i, doc in enumerate(new_results['documents'][0]):
    print(f"{i+1}. {doc}")
    print(f"   相似度距离: {new_results['distances'][0][i]:.4f}") # 距离越小越相似