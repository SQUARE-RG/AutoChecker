"""构建 CodeQL 文档向量知识库.

说明:
	* 文档根目录: /root/code_check/codeql_collect/codeql_language_guide/cpp
	* Embedding 模型: /root/code_check/src/retriever/embedding_model/bge-large-en-v1.5
	* Chroma 向量库: /root/code_check/src/retriever/vector_db/codeql_doc_vector_db

脚本职责:
	1. 遍历文档树, 读取 markdown / 纯文本内容.
	2. 进行自定义分割, 确保 code block( ``` 包围 ) 不被拆分.
	3. 使用 bge embedding 生成向量, 并持久化存储到 Chroma.

用法:
	python build_knowledge_base.py \
		--doc-root /root/code_check/codeql_collect/codeql_language_guide/cpp \
		--model-path /root/code_check/src/retriever/embedding_model/bge-large-en-v1.5 \
		--vector-db /root/code_check/src/retriever/vector_db/codeql_doc_vector_db
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import chromadb
from chromadb.config import Settings

from bge_embedding import parallel_encode, sequential_encode

DEFAULT_DOC_ROOT = Path("/root/code_check/codeql_collect/codeql_language_guide/cpp")
DEFAULT_MODEL_PATH = Path("/root/code_check/src/retriever/embedding_model/bge-large-en-v1.5")
DEFAULT_VECTOR_DB_PATH = Path("/root/code_check/src/retriever/vector_db/codeql_doc_vector_db")

CHUNK_CHAR_LIMIT = 1200
CHUNK_CHAR_MIN = 200


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
LOGGER = logging.getLogger("build_knowledge_base")


@dataclass
class Chunk:
	doc_path: Path
	chunk_id: int
	text: str

	def make_id(self, prefix: str) -> str:
		rel = self.doc_path.as_posix()
		return f"{prefix}:{rel}:{self.chunk_id}"


def iter_documents(doc_root: Path) -> Iterable[tuple[Path, str]]:
	supported_suffix = {".md", ".markdown", ".txt", ".rst"}
	for path in sorted(doc_root.rglob("*")):
		if not path.is_file():
			continue
		if path.suffix.lower() not in supported_suffix:
			continue
		try:
			text = path.read_text(encoding="utf-8")
		except UnicodeDecodeError:
			LOGGER.warning("跳过无法解码的文件: %s", path)
			continue
		if text.strip():
			yield path, text


def split_preserve_code(text: str, max_chars: int = CHUNK_CHAR_LIMIT) -> List[str]:
	"""按字符数分割文本, 但保持 markdown / RST 代码块完整."""

	def _flush_buffer(buf: List[str]) -> str | None:
		if not buf:
			return None
		joined = "".join(buf).strip()
		buf.clear()
		return joined if joined else None

	def _consume_rst_block(lines: List[str], start_idx: int) -> tuple[str, int]:
		block: List[str] = [lines[start_idx]]
		idx = start_idx + 1
		while idx < len(lines):
			line = lines[idx]
			if line.strip() == "":
				block.append(line)
				idx += 1
				continue
			if line.startswith((" ", "\t")):
				block.append(line)
				idx += 1
			else:
				break
		return "".join(block).strip(), idx

	def _is_literal_block(lines: List[str], idx: int) -> bool:
		line = lines[idx]
		stripped = line.strip()
		if stripped.startswith(".."):
			return False
		if not stripped.endswith("::"):
			return False
		peek = idx + 1
		while peek < len(lines) and lines[peek].strip() == "":
			peek += 1
		if peek >= len(lines):
			return False
		return lines[peek].startswith((" ", "\t"))

	chunks: List[str] = []
	buffer: List[str] = []
	buffer_len = 0

	lines = text.splitlines(keepends=True)
	i = 0
	while i < len(lines):
		line = lines[i]
		stripped = line.strip()
		if stripped.startswith("```"):
			flushed = _flush_buffer(buffer)
			if flushed:
				chunks.append(flushed)
			buffer_len = 0
			code_block = [line]
			i += 1
			while i < len(lines):
				code_line = lines[i]
				code_block.append(code_line)
				if code_line.strip().startswith("```"):
					i += 1
					break
					i += 1
			chunks.append("".join(code_block).strip())
			continue
		if stripped.startswith(".. code-block::"):
			flushed = _flush_buffer(buffer)
			if flushed:
				chunks.append(flushed)
			buffer_len = 0
			block_text, i = _consume_rst_block(lines, i)
			chunks.append(block_text)
			continue
		if _is_literal_block(lines, i):
			flushed = _flush_buffer(buffer)
			if flushed:
				chunks.append(flushed)
			buffer_len = 0
			block_text, i = _consume_rst_block(lines, i)
			chunks.append(block_text)
			continue

		buffer.append(line)
		buffer_len += len(line)
		i += 1

		if buffer_len >= max_chars:
			chunk_text = _flush_buffer(buffer)
			if chunk_text:
				chunks.append(chunk_text)
			buffer_len = 0

	if buffer:
		chunk_text = _flush_buffer(buffer)
		if chunk_text:
			chunks.append(chunk_text)

	merged: List[str] = []
	for piece in chunks:
		if not merged:
			merged.append(piece)
			continue
		if len(piece) < CHUNK_CHAR_MIN and len(merged[-1]) + len(piece) < max_chars:
			merged[-1] = merged[-1] + "\n" + piece
		else:
			merged.append(piece)
	return [m for m in merged if m.strip()]


def build_chunks(doc_root: Path) -> List[Chunk]:
	chunks: List[Chunk] = []
	for doc_idx, (path, text) in enumerate(iter_documents(doc_root)):
		parts = split_preserve_code(text)
		for idx, part in enumerate(parts):
			chunks.append(Chunk(doc_path=path.relative_to(doc_root), chunk_id=idx, text=part))
		LOGGER.info("分割文件 %s -> %d 个片段", path, len(parts))
	LOGGER.info("总计生成 %d 个片段", len(chunks))
	return chunks


def embed_chunks(chunks: List[Chunk], model_path: Path) -> List[List[float]]:
	texts = [chunk.text for chunk in chunks]
	if not texts:
		return []
    
	# 使用并行编码以提速, 少量文本时自动退化为顺序执行.
	try:
		vectors = sequential_encode(texts, str(model_path), batch_size=32)
	except Exception as error:
		LOGGER.warning("并行编码失败 %s, 回退至顺序编码", error)
		vectors = sequential_encode(texts, str(model_path), batch_size=32)
	return vectors.tolist()


def persist_to_chroma(
	chunks: List[Chunk],
	embeddings: List[List[float]],
	vector_db_path: Path,
	collection_name: str = "codeql_docs",
) -> None:
	if not chunks:
		LOGGER.warning("没有可写入的片段, 跳过 Chroma 构建")
		return
	if len(chunks) != len(embeddings):
		raise ValueError("chunks 与 embeddings 数量不匹配")

	client = chromadb.PersistentClient(path=str(vector_db_path), settings=Settings())
	try:
		client.delete_collection(name=collection_name)
	except Exception:
		pass
	collection = client.create_collection(name=collection_name)

	ids = []
	documents = []
	metadatas = []
	for idx, chunk in enumerate(chunks):
		ids.append(chunk.make_id(collection_name))
		documents.append(chunk.text)
		metadatas.append(
			{
				"source": chunk.doc_path.as_posix(),
				"chunk_id": chunk.chunk_id,
			}
		)

	collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
	LOGGER.info("Chroma collection[%s] 写入 %d 条记录", collection_name, len(ids))


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="构建 CodeQL 文档向量知识库")
	parser.add_argument("--doc-root", type=Path, default=DEFAULT_DOC_ROOT)
	parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
	parser.add_argument("--vector-db", type=Path, default=DEFAULT_VECTOR_DB_PATH)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	if not args.doc_root.exists():
		raise FileNotFoundError(f"文档目录不存在: {args.doc_root}")
	if not args.model_path.exists():
		raise FileNotFoundError(f"模型路径不存在: {args.model_path}")

	LOGGER.info("开始加载文档: %s", args.doc_root)
	chunks = build_chunks(args.doc_root)
	LOGGER.info("开始生成向量, 模型: %s", args.model_path)
	embeddings = embed_chunks(chunks, args.model_path)
	LOGGER.info("写入 Chroma, 目录: %s", args.vector_db)
	persist_to_chroma(chunks, embeddings, args.vector_db)
	LOGGER.info("知识库构建完成")


if __name__ == "__main__":
	main()

