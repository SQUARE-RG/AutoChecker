from typing import TypedDict


class QueryState(TypedDict, total=False):
    messages: list
    query_code: str
    query_path: str
    final_query_path: str
    candidate_count: int
    generation_phase: str
    attempt: int
    calls: int
    tool_calls: int
    parse_retries: int
    compile_repairs: int
    semantic_repairs: int
    evidence_request_count: int
    evidence_request: dict
    history: list
    feedback: str
    route: str
    final_status: str
    evaluation: dict
    last_compilable_query: str
