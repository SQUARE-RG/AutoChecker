# embedding模型的设置
queries和documents的示例如下：
queries = [
    "how to implement binary search algorithm",
    "what is gradient descent in machine learning"
]

documents = [
    "Binary search is an efficient algorithm for finding an item from a sorted list of items.",
    "Gradient descent is an optimization algorithm used to minimize some function.",
    "Python is a popular programming language for machine learning."
]

请你使用bge-large-en模型完成如下任务：

1.模型的路径在/root/code_check/src/retriever/embeding_model/bge-large-en-v1.5
2.使用并行方式，同时对queries数组里面的多个元素并行计算嵌入向量
3.使用并行方式，同时对documents数组里面的多个元素并行计算嵌入向量
4.计算queries数组中每个元素对应的documents数组中相似度最高的k个元素
