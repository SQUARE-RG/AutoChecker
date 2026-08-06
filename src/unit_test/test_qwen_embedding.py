from openai import OpenAI
import numpy as np


class QwenEmbedder:
    def __init__(self):
        self.client = OpenAI(api_key="rest-llm", base_url="https://tgi.rvpt.top:8443/qwen3-embed/v1")

    def get_one_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            input=text,
            model="Qwen3-Embedding-8B",
            extra_body={"normalize": True},
        )
        return response.data[0].embedding

    def get_embeddings(self, texts: list[str], batch_size: int = 20) -> list[list[float]]:
        """
        Get embeddings for a list of texts in batches.
        :param texts: List of texts to embed.
        :param batch_size: Number of texts to process in each batch, full list if -1.
        :return: List of embeddings for each text.
        """
        if batch_size == -1:
            batch_size = len(texts)
        embeddings = []
        for i in range(0, len(texts), batch_size):
            response = self.client.embeddings.create(
                input=texts[i : i + batch_size],
                model="Qwen3-Embedding-8B",
                extra_body={"normalize": True},
            )
            embeddings.extend(data.embedding for data in response.data)
        return embeddings


def main():
    embedder = QwenEmbedder()
    texts = ["Hello, Qwen!", "Hello, GPT!", "Hello, World!", "Goodbye, World!"]
    embeddings = embedder.get_embeddings(texts)
    for embedding in embeddings:
        print(len(embedding))
    # 计算第一个文本与其他文本的相似度-使用点积
    embeddings_np = np.array(embeddings)
    scores = (embeddings_np[:1]) @ embeddings_np[1:].T
    print(scores)
    # [[0.87445608 0.80231976 0.5032538 ]] 表示 [[1&2相似度, 1&3相似度, 1&4相似度]]


if __name__ == "__main__":
    main()
