#!/usr/bin/env python3
"""预热 embedding 缓存 — 在运行 main.py 之前执行，避免首次运行边跑边编码。

对 clang-tidy 流程的 4 个知识库（astMatchers / astMatchers_meta_op /
check_op / ast_api）提前做 BGE 全量编码并缓存为 .pt 文件。
缓存已存在时秒级跳过，可重复运行。

用法（必须从项目根目录运行）:
    python scripts/prewarm_embeddings.py            # 仅 clang-tidy 流程的 4 个
    python scripts/prewarm_embeddings.py --all      # 含 CodeQL 流程的 2 个
"""

import os

# 必须在任何 tokenizers/sentence-transformers import 之前设置：
# 禁止 tokenizers 线程池，避免后续 parallel_encode 的 fork 死锁
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import sys
import time
from pathlib import Path

# 统一约束：必须从 /root/code_check 运行（config 和 embedding_db 路径依赖 CWD）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
os.chdir(str(_PROJECT_ROOT))

from loguru import logger  # noqa: E402

# 确保 embedding_db 目录存在（torch.save 不会自动建目录）
EMBEDDING_DB_DIR = os.path.join(_PROJECT_ROOT, "src", "embedding_db")
os.makedirs(EMBEDDING_DB_DIR, exist_ok=True)
logger.info(f"Embedding DB directory ready: {EMBEDDING_DB_DIR}")

# (函数, 数据源名) — clang-tidy 流程
CLANG_TIDY_TASKS = [
    ("retriever.retrieve_from_astMatchers", "embedding_ast_matchers", "AST Matchers"),
    ("retriever.retrieve_from_astMatchers_meta_op", "embedding_ast_matchers_meta_op", "AST Matchers Meta Op"),
    ("retriever.retrieve_from_check_op", "embedding_check_op", "Check Op"),
    ("retriever.retrieve_from_ast_api", "embedding_ast_api", "AST API"),
]

# (函数, 数据源名) — CodeQL 流程（legacy 检索）
CODEQL_TASKS = [
    ("retriever.retrieve_from_codeql_api", "embedding_ast_api", "CodeQL API"),
    ("retriever.retrieve_from_codeql_op", "embedding_codeql_query_op", "CodeQL Query Op"),
]


def run_task(module_name: str, func_name: str, label: str) -> None:
    """执行单个 embedding 任务并计时。"""
    logger.info(f"=== Prewarming: {label} ===")
    start = time.perf_counter()
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        result = func()
        if isinstance(result, tuple) and result:
            docs = result[0]
            count = len(docs) if hasattr(docs, "__len__") else "?"
            logger.info(f"{label}: {count} documents embedded")
    except Exception as e:
        logger.error(f"{label} prewarm FAILED: {e}")
        raise
    elapsed = time.perf_counter() - start
    logger.info(f"{label} done in {elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prewarm embedding caches for clang-tidy/CodeQL retrievers")
    parser.add_argument("--all", action="store_true",
                        help="Also prewarm CodeQL legacy retrievers (codeql_api, codeql_query_op)")
    args = parser.parse_args()

    logger.info("Starting embedding prewarm...")
    total_start = time.perf_counter()

    for module_name, func_name, label in CLANG_TIDY_TASKS:
        run_task(module_name, func_name, label)

    if args.all:
        for module_name, func_name, label in CODEQL_TASKS:
            run_task(module_name, func_name, label)

    total_elapsed = time.perf_counter() - total_start
    logger.info(f"All prewarm tasks completed in {total_elapsed:.1f}s")
    logger.info("main.py can now start with cached embeddings.")


if __name__ == "__main__":
    main()
