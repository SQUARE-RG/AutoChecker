"""Shared persistence and bounded subprocess execution; no agent access to host shell."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time
from dataclasses import asdict, dataclass


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Limits:
    analysis_max_model_calls: int = 30
    analysis_max_tool_calls: int = 60
    spec_repair_limit: int = 2
    evidence_refresh_limit: int = 1
    query_model_calls_per_attempt: int = 8
    query_tool_calls_per_attempt: int = 8
    search_queries_per_call: int = 3
    retrieval_top_k: int = 2
    document_max_chars: int = 6000
    query_parse_retries: int = 1
    max_compile_repairs: int = 3
    max_semantic_repairs: int = 3
    max_query_attempts: int = 7
    max_query_model_calls: int = 40
    llm_transport_retries: int = 2
    llm_request_timeout_seconds: int = 600
    llm_connect_timeout_seconds: int = 30
    llm_read_timeout_seconds: int = 300
    llm_write_timeout_seconds: int = 60
    llm_pool_timeout_seconds: int = 30
    retrieval_timeout_seconds: int = 30
    compile_timeout_seconds: int = 180
    database_run_timeout_seconds: int = 300
    task_wall_timeout_seconds: int = 1800
    query_graph_recursion_limit: int = 256

    def __post_init__(self):
        if any(not isinstance(v, int) or v < 0 for v in asdict(self).values()):
            raise ValueError('Limits must be nonnegative integers')


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(text, encoding='utf-8')
    os.replace(temporary, path)


def write_json(path: Path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')


def remaining(deadline: float, timeout: float) -> float:
    value = min(timeout, deadline - time.time())
    if value <= 0:
        raise BudgetExceeded('Task wall-clock budget exhausted')
    return value


def command(args: list[str], timeout=120, cwd=None) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace')[-12000:])
    return result.stdout.decode('utf-8')
