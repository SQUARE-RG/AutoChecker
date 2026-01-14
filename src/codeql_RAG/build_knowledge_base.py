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
import re

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


@dataclass
class Segment:
	text: str
	kind: str


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


LIST_PATTERN = re.compile(r"^(\s*)([-*+]\s+|\d+[\.)]\s+)")
RST_HEADING_CHARS = {"=", "-", "~", "`", ":", "'", '"', "^", "_", "*", "+", "#", "<", ">"}


def _consume_indented_block(lines: List[str], start_idx: int) -> tuple[str, int]:
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
	return "".join(block), idx


def _consume_fenced_code(lines: List[str], start_idx: int) -> tuple[str, int]:
	fence = lines[start_idx].strip()
	block = [lines[start_idx]]
	idx = start_idx + 1
	while idx < len(lines):
		line = lines[idx]
		block.append(line)
		stripped = line.strip()
		if stripped.startswith("```") and (not fence or stripped.startswith(fence[:3])):
			idx += 1
			break
		idx += 1
	return "".join(block), idx


def _is_rst_directive(line: str) -> bool:
	stripped = line.strip()
	return stripped.startswith(".. ") and stripped.endswith("::")


def _is_literal_block_header(line: str) -> bool:
	stripped = line.strip()
	if stripped.startswith(".."):
		return False
	return stripped.endswith("::")


def _literal_block_continues(lines: List[str], idx: int) -> bool:
	peek = idx + 1
	while peek < len(lines) and lines[peek].strip() == "":
		peek += 1
	if peek >= len(lines):
		return False
	return lines[peek].startswith((" ", "\t"))


def _consume_markdown_heading(lines: List[str], start_idx: int) -> tuple[str, int]:
	heading = [lines[start_idx]]
	idx = start_idx + 1
	while idx < len(lines) and lines[idx].strip() == "":
		heading.append(lines[idx])
		idx += 1
	return "".join(heading), idx


def _consume_rst_heading(lines: List[str], start_idx: int) -> tuple[str, int] | None:
	if start_idx + 1 >= len(lines):
		return None
	title = lines[start_idx].rstrip("\n")
	underline = lines[start_idx + 1].strip("\n")
	if not title.strip() or not underline.strip():
		return None
	if len(underline.strip()) < len(title.strip()):
		return None
	if len(set(underline.strip())) != 1:
		return None
	char = underline.strip()[0]
	if char not in RST_HEADING_CHARS:
		return None
	idx = start_idx + 2
	lines_out = [lines[start_idx], lines[start_idx + 1]]
	while idx < len(lines) and lines[idx].strip() == "":
		lines_out.append(lines[idx])
		idx += 1
	return "".join(lines_out), idx


def _flush_paragraph(buffer: List[str], segments: List[Segment]) -> None:
	if not buffer:
		return
	text = "".join(buffer)
	if text.strip():
		segments.append(Segment(text=text, kind="paragraph"))
	buffer.clear()


def tokenize_semantic_units(text: str) -> List[Segment]:
	lines = text.splitlines(keepends=True)
	segments: List[Segment] = []
	buffer: List[str] = []
	i = 0
	while i < len(lines):
		line = lines[i]
		stripped = line.strip()
		if stripped.startswith("```"):
			_flush_paragraph(buffer, segments)
			block, i = _consume_fenced_code(lines, i)
			segments.append(Segment(text=block, kind="code"))
			continue
		if _is_rst_directive(line):
			_flush_paragraph(buffer, segments)
			block, i = _consume_indented_block(lines, i)
			segments.append(Segment(text=block, kind="directive"))
			continue
		if _is_literal_block_header(line) and _literal_block_continues(lines, i):
			_flush_paragraph(buffer, segments)
			block, i = _consume_indented_block(lines, i)
			segments.append(Segment(text=block, kind="literal"))
			continue
		if stripped.startswith("#"):
			_flush_paragraph(buffer, segments)
			block, i = _consume_markdown_heading(lines, i)
			segments.append(Segment(text=block, kind="heading"))
			continue
		rst_heading = _consume_rst_heading(lines, i)
		if rst_heading:
			_flush_paragraph(buffer, segments)
			block, i = rst_heading
			segments.append(Segment(text=block, kind="heading"))
			continue
		if stripped and LIST_PATTERN.match(stripped):
			_flush_paragraph(buffer, segments)
			list_block: List[str] = []
			while i < len(lines):
				candidate = lines[i]
				cand_strip = candidate.strip()
				if cand_strip == "":
					list_block.append(candidate)
					i += 1
					continue
				if LIST_PATTERN.match(cand_strip):
					list_block.append(candidate)
					i += 1
				else:
					break
			segments.append(Segment(text="".join(list_block), kind="list"))
			continue
		buffer.append(line)
		i += 1
	_flush_paragraph(buffer, segments)
	return segments


def _segments_length(segments: List[Segment], start: int, end: int) -> int:
	return sum(len(segments[i].text) for i in range(start, end))


def _choose_split_index(segments: List[Segment], start: int, end: int) -> int:
	mid = (start + end) / 2
	best_idx = start + 1
	best_score = float("-inf")
	for idx in range(start + 1, end):
		left_kind = segments[idx - 1].kind
		right_kind = segments[idx].kind
		score = 0.0
		if "heading" in (left_kind, right_kind):
			score += 4.0
		if "list" in (left_kind, right_kind):
			score += 2.0
		if "directive" in (left_kind, right_kind) or "literal" in (left_kind, right_kind):
			score += 1.5
		if "code" in (left_kind, right_kind):
			score += 2.5
		distance_penalty = abs(idx - mid) / (end - start)
		score -= distance_penalty
		if score > best_score:
			best_score = score
			best_idx = idx
	return best_idx


def _recursive_partition(
	segments: List[Segment],
	start: int,
	end: int,
	max_chars: int,
	chunks: List[str],
):
	total_len = _segments_length(segments, start, end)
	if total_len <= max_chars or end - start == 1:
		chunk = "".join(seg.text for seg in segments[start:end]).strip()
		if chunk:
			chunks.append(chunk)
		return
	split_idx = _choose_split_index(segments, start, end)
	_recursive_partition(segments, start, split_idx, max_chars, chunks)
	_recursive_partition(segments, split_idx, end, max_chars, chunks)


def _merge_small_chunks(chunks: List[str], max_chars: int, min_chars: int) -> List[str]:
	if not chunks:
		return []
	merged = [chunks[0]]
	for chunk in chunks[1:]:
		if len(chunk) < min_chars and len(merged[-1]) + len(chunk) <= max_chars:
			merged[-1] = merged[-1].rstrip() + "\n\n" + chunk.lstrip()
		else:
			merged.append(chunk)
	return [piece for piece in merged if piece.strip()]


def split_semantic_chunks(text: str, max_chars: int = CHUNK_CHAR_LIMIT) -> List[str]:
	segments = tokenize_semantic_units(text)
	if not segments:
		return []
	raw_chunks: List[str] = []
	_recursive_partition(segments, 0, len(segments), max_chars, raw_chunks)
	return _merge_small_chunks(raw_chunks, max_chars, CHUNK_CHAR_MIN)


def build_chunks(doc_root: Path) -> List[Chunk]:
	chunks: List[Chunk] = []
	for doc_idx, (path, text) in enumerate(iter_documents(doc_root)):
		parts = split_semantic_chunks(text)
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
		vectors = parallel_encode(texts, str(model_path), batch_size=32)
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

