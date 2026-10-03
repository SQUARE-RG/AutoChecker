"""LLM connectivity, streaming, token usage, and retry integration tests.

Run explicitly because this test accesses the configured remote model and costs money:

    RUN_LLM_INTEGRATION_TEST=1 \
      /root/anaconda3/envs/code_check/bin/python -m pytest -q -s \
      src/unit_test/test_llm_model_connectivity.py

It can also be run directly:

    /root/anaconda3/envs/code_check/bin/python \
      src/unit_test/test_llm_model_connectivity.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable

import pytest
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, AIMessageChunk


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
load_dotenv(PROJECT_ROOT / ".env")

from llm_interface.llm_provider import (  # noqa: E402
    DEEPSEEK_PRICE_PER_1M_TOKENS,
    calculate_deepseek_cost,
    build_messages,
    llm_client,
    llm_invoke,
)
from llm_interface import llm_provider as provider_module  # noqa: E402


StreamFactory = Callable[[], Iterable[AIMessageChunk]]


def _chunk_text(chunk: AIMessageChunk) -> str:
    """Return text from both string and content-block streaming chunks."""
    content = chunk.content
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") in {"text", "output_text"}:
            parts.append(str(block.get("text") or ""))
    return "".join(parts)


def _consume_stream_with_retries(
    stream_factory: StreamFactory,
    *,
    max_attempts: int,
    retry_delay: float = 0,
) -> dict[str, Any]:
    """Consume one complete stream, discarding partial output before a retry."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        chunks: list[AIMessageChunk] = []
        text_parts: list[str] = []
        first_event_at: float | None = None
        first_content_at: float | None = None
        started_at = time.monotonic()
        stream = stream_factory()
        try:
            for chunk in stream:
                now = time.monotonic()
                if first_event_at is None:
                    first_event_at = now
                text = _chunk_text(chunk)
                if text and first_content_at is None:
                    first_content_at = now
                chunks.append(chunk)
                text_parts.append(text)
        except Exception as exc:
            close = getattr(stream, "close", None)
            if callable(close):
                close()
            last_error = exc
            if not _is_retryable(exc) or attempt >= max_attempts:
                raise
            if retry_delay:
                time.sleep(retry_delay)
            continue

        if not chunks:
            raise AssertionError("Streaming endpoint returned no events")
        aggregate = chunks[0]
        for chunk in chunks[1:]:
            aggregate += chunk
        completed_at = time.monotonic()
        return {
            "answer": "".join(text_parts),
            "message": aggregate,
            "attempts": attempt,
            "event_count": len(chunks),
            "content_event_count": sum(bool(_chunk_text(chunk)) for chunk in chunks),
            "first_event_seconds": round((first_event_at - started_at), 3),
            "first_content_seconds": (
                round((first_content_at - started_at), 3)
                if first_content_at is not None
                else None
            ),
            "total_seconds": round(completed_at - started_at, 3),
        }
    raise AssertionError(f"Streaming request failed: {last_error}")


def run_connectivity_probe() -> dict[str, Any]:
    """Call the configured model once and return printable usage/cost details."""
    requested_model = os.getenv("MODEL_NAME", "")
    assert requested_model, "MODEL_NAME is not configured in .env"
    assert llm_client is not None, (
        f"llm_provider did not create a client for MODEL_NAME={requested_model!r}"
    )

    max_attempts = int(os.getenv("LLM_PROBE_MAX_ATTEMPTS", "2"))
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            response, callback = llm_invoke(
                llm_client,
                "这是一次连通性测试。请只回复：PONG",
                "你是API连通性测试助手，严格按用户要求简短回答。",
            )
            break
        except Exception as exc:
            last_error = exc
            if not _is_retryable(exc) or attempt >= max_attempts:
                raise AssertionError(
                    f"Model request failed after {attempt} attempt(s): "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            delay = min(5, attempt * 2)
            print(
                f"LLM probe attempt {attempt}/{max_attempts} failed with "
                f"{type(exc).__name__}; retrying in {delay}s",
                flush=True,
            )
            time.sleep(delay)
    else:  # pragma: no cover - loop always breaks or raises
        raise AssertionError(f"Model request failed: {last_error}")
    answer = str(response).strip()
    assert answer, "The model returned empty content"

    cost = calculate_deepseek_cost(callback)
    prompt_tokens = int(cost["prompt_tokens"])
    completion_tokens = int(cost["completion_tokens"])
    cached_tokens = int(cost["cached_tokens"])
    reasoning_tokens = int(cost["reasoning_tokens"])
    total_tokens = int(cost["total_tokens"])

    assert prompt_tokens > 0, "Response usage did not contain input tokens"
    assert completion_tokens > 0, "Response usage did not contain output tokens"
    assert total_tokens == prompt_tokens + completion_tokens
    assert 0 <= cached_tokens <= prompt_tokens
    assert reasoning_tokens >= 0
    assert cost["pricing_source"] != "none", (
        f"No pricing configured for response model {cost['model']!r}; "
        "add it to DEEPSEEK_PRICE_PER_1M_TOKENS"
    )
    assert float(cost["total_cost"]) > 0

    prices = DEEPSEEK_PRICE_PER_1M_TOKENS.get(str(cost["model"]))
    return {
        "connectivity": "ok",
        "requested_model": requested_model,
        "response_model": cost["model"],
        "response_content": answer,
        "tokens": {
            "input": prompt_tokens,
            "input_cached": cached_tokens,
            "input_uncached": prompt_tokens - cached_tokens,
            "output": completion_tokens,
            "output_reasoning": reasoning_tokens,
            "total": total_tokens,
        },
        "pricing_per_1m_tokens": prices,
        "estimated_cost": {
            "input": cost["cost_breakdown"]["input_cost"],
            "output": cost["cost_breakdown"]["output_cost"],
            "total": cost["total_cost"],
            "currency": cost["currency"],
            "source": cost["pricing_source"],
        },
    }


def run_streaming_probe() -> dict[str, Any]:
    """Verify SSE-style chunks, complete reconstruction, and final usage data."""
    requested_model = os.getenv("MODEL_NAME", "")
    assert requested_model, "MODEL_NAME is not configured in .env"
    assert llm_client is not None, (
        f"llm_provider did not create a client for MODEL_NAME={requested_model!r}"
    )
    messages = build_messages(
        "请只回复以下内容，不要增加解释：STREAM-ONE STREAM-TWO STREAM-THREE",
        "你是API流式响应测试助手，严格按用户要求回答。",
    )
    max_attempts = int(os.getenv("LLM_PROBE_MAX_ATTEMPTS", "2"))
    result = _consume_stream_with_retries(
        lambda: llm_client.stream(messages, stream_usage=True),
        max_attempts=max_attempts,
        retry_delay=2,
    )
    answer = result["answer"].strip()
    message = result.pop("message")
    usage = message.usage_metadata or {}
    input_tokens = int(usage.get("input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or 0)

    assert answer, "Streaming endpoint returned no text content"
    assert result["event_count"] > 1, "Response was not split into multiple stream events"
    assert result["content_event_count"] > 1, (
        "Text arrived in a single event rather than incrementally"
    )
    assert result["event_count"] >= result["content_event_count"]
    assert result["first_content_seconds"] is not None
    assert result["first_content_seconds"] <= result["total_seconds"]
    assert input_tokens > 0, (
        "Streaming response did not include input-token usage; the provider may "
        "not support stream_options.include_usage"
    )
    assert output_tokens > 0, (
        "Streaming response did not include output-token usage; the provider may "
        "not support stream_options.include_usage"
    )
    assert total_tokens == input_tokens + output_tokens

    return {
        "streaming": "ok",
        "requested_model": requested_model,
        "response_model": message.response_metadata.get("model_name"),
        "response_content": answer,
        "attempts": result["attempts"],
        "events": {
            "total": result["event_count"],
            "with_content": result["content_event_count"],
        },
        "timing_seconds": {
            "first_event": result["first_event_seconds"],
            "first_content": result["first_content_seconds"],
            "complete": result["total_seconds"],
        },
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_tokens,
            "details": usage,
        },
        "capabilities": {
            "stream_events": True,
            "complete_response_reconstruction": True,
            "stream_usage": True,
        },
    }


def run_retry_strategy_probe() -> dict[str, Any]:
    """Simulate a broken stream and verify partial output is never reused."""
    created_streams = 0

    def stream_factory():
        nonlocal created_streams
        created_streams += 1
        if created_streams == 1:
            def interrupted_stream():
                yield AIMessageChunk(content="INCOMPLETE-")
                raise ConnectionError("simulated stream interruption")

            return interrupted_stream()
        return iter(
            [
                AIMessageChunk(content="COMPLETE"),
                AIMessageChunk(
                    content="",
                    usage_metadata={
                        "input_tokens": 3,
                        "output_tokens": 1,
                        "total_tokens": 4,
                    },
                ),
            ]
        )

    result = _consume_stream_with_retries(stream_factory, max_attempts=2)
    message = result.pop("message")
    assert result["attempts"] == 2
    assert created_streams == 2
    assert result["answer"] == "COMPLETE"
    assert "INCOMPLETE" not in result["answer"]
    assert message.usage_metadata["total_tokens"] == 4
    return {
        "stream_retry": "ok",
        "attempts": result["attempts"],
        "partial_response_discarded": True,
        "final_response": result["answer"],
    }


def run_all_probes() -> dict[str, Any]:
    return {
        "normal_request": run_connectivity_probe(),
        "streaming_request": run_streaming_probe(),
        "retry_strategy": run_retry_strategy_probe(),
    }


def _is_retryable(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    status_code = getattr(exc, "status_code", None) or getattr(
        response, "status_code", None
    )
    if status_code is not None:
        return status_code == 429 or status_code >= 500
    name = type(exc).__name__.lower()
    return any(
        token in name
        for token in ("timeout", "connection", "ratelimit", "internalserver")
    )


@pytest.mark.skipif(
    os.getenv("RUN_LLM_INTEGRATION_TEST") != "1",
    reason="set RUN_LLM_INTEGRATION_TEST=1 to run the paid network test",
)
def test_configured_model_connectivity_tokens_and_cost() -> None:
    details = run_connectivity_probe()
    print(json.dumps(details, ensure_ascii=False, indent=2))


@pytest.mark.skipif(
    os.getenv("RUN_LLM_INTEGRATION_TEST") != "1",
    reason="set RUN_LLM_INTEGRATION_TEST=1 to run the paid network test",
)
def test_configured_model_streaming_chunks_and_usage() -> None:
    details = run_streaming_probe()
    print(json.dumps(details, ensure_ascii=False, indent=2))


def test_stream_retry_discards_partial_attempt() -> None:
    details = run_retry_strategy_probe()
    assert details["stream_retry"] == "ok"


@contextmanager
def _fake_openai_callback():
    yield SimpleNamespace(
        prompt_tokens=0,
        completion_tokens=0,
        total_cost=0,
        prompt_tokens_cached=0,
    )


def _runtime_settings(*, streaming: bool, max_retries: int = 0) -> dict[str, Any]:
    return {
        "streaming": streaming,
        "stream_output": False,
        "stream_usage": True,
        "timeout_seconds": 600,
        "max_retries": max_retries,
        "retry_base_delay_seconds": 0,
    }


def test_shared_provider_non_streaming_keeps_text_and_usage(monkeypatch) -> None:
    class FakeModel:
        def invoke(self, messages):
            return AIMessage(
                content="NON-STREAM",
                response_metadata={"model_name": "deepseek-v4-flash-krill"},
                usage_metadata={
                    "input_tokens": 7,
                    "output_tokens": 3,
                    "total_tokens": 10,
                },
            )

        def stream(self, messages, **kwargs):
            raise AssertionError("stream() must not be called in non-streaming mode")

    monkeypatch.setattr(
        provider_module, "get_llm_settings", lambda: _runtime_settings(streaming=False)
    )
    monkeypatch.setattr(provider_module, "get_openai_callback", _fake_openai_callback)

    answer, callback = provider_module.llm_invoke(FakeModel(), "ping")

    assert answer == "NON-STREAM"
    assert callback.llm_usage_metadata["total_tokens"] == 10
    assert calculate_deepseek_cost(callback)["total_tokens"] == 10


def test_shared_provider_streaming_preserves_tool_calls_and_usage(monkeypatch) -> None:
    class FakeToolModel:
        def invoke(self, messages):
            raise AssertionError("invoke() must not be called in streaming mode")

        def stream(self, messages, **kwargs):
            assert kwargs["stream_usage"] is True
            yield AIMessageChunk(
                content="",
                tool_call_chunks=[
                    {
                        "name": "lookup",
                        "args": '{"query":',
                        "id": "call-1",
                        "index": 0,
                        "type": "tool_call_chunk",
                    }
                ],
            )
            yield AIMessageChunk(
                content="",
                tool_call_chunks=[
                    {
                        "name": None,
                        "args": '"malloc"}',
                        "id": None,
                        "index": 0,
                        "type": "tool_call_chunk",
                    }
                ],
                response_metadata={"model_name": "deepseek-v4-flash-0731"},
                usage_metadata={
                    "input_tokens": 11,
                    "output_tokens": 4,
                    "total_tokens": 15,
                },
            )

    monkeypatch.setattr(
        provider_module, "get_llm_settings", lambda: _runtime_settings(streaming=True)
    )
    monkeypatch.setattr(provider_module, "get_openai_callback", _fake_openai_callback)

    message, callback = provider_module.llm_invoke_messages(
        FakeToolModel(), [AIMessage(content="test")], label="tool-test"
    )

    assert message.tool_calls == [
        {"name": "lookup", "args": {"query": "malloc"}, "id": "call-1", "type": "tool_call"}
    ]
    assert callback.llm_usage_metadata["total_tokens"] == 15
    assert callback.llm_response_model_name == "deepseek-v4-flash-0731"


def test_shared_provider_retries_whole_stream_without_partial_result(monkeypatch) -> None:
    class FlakyModel:
        attempts = 0

        def stream(self, messages, **kwargs):
            self.attempts += 1
            if self.attempts == 1:
                yield AIMessageChunk(content="PARTIAL")
                raise ConnectionError("broken stream")
            yield AIMessageChunk(content="COMPLETE")
            yield AIMessageChunk(
                content="",
                usage_metadata={
                    "input_tokens": 5,
                    "output_tokens": 2,
                    "total_tokens": 7,
                },
            )

    model = FlakyModel()
    monkeypatch.setattr(
        provider_module,
        "get_llm_settings",
        lambda: _runtime_settings(streaming=True, max_retries=1),
    )
    monkeypatch.setattr(provider_module, "get_openai_callback", _fake_openai_callback)

    answer, callback = provider_module.llm_invoke(model, "ping")

    assert model.attempts == 2
    assert answer == "COMPLETE"
    assert "PARTIAL" not in answer
    assert callback.llm_usage_metadata["total_tokens"] == 7


def test_shared_provider_retries_stream_with_events_but_no_content(monkeypatch) -> None:
    class EmptyThenValidModel:
        attempts = 0

        def stream(self, messages, **kwargs):
            self.attempts += 1
            if self.attempts == 1:
                yield AIMessageChunk(
                    content="",
                    response_metadata={"finish_reason": "stop"},
                    usage_metadata={
                        "input_tokens": 5,
                        "output_tokens": 0,
                        "total_tokens": 5,
                    },
                )
                return
            yield AIMessageChunk(content="VALID")
            yield AIMessageChunk(
                content="",
                usage_metadata={
                    "input_tokens": 5,
                    "output_tokens": 1,
                    "total_tokens": 6,
                },
            )

    model = EmptyThenValidModel()
    monkeypatch.setattr(
        provider_module,
        "get_llm_settings",
        lambda: _runtime_settings(streaming=True, max_retries=1),
    )
    monkeypatch.setattr(provider_module, "get_openai_callback", _fake_openai_callback)

    answer, callback = provider_module.llm_invoke(model, "ping")

    assert model.attempts == 2
    assert answer == "VALID"
    assert callback.llm_usage_metadata["total_tokens"] == 6


if __name__ == "__main__":
    print(json.dumps(run_all_probes(), ensure_ascii=False, indent=2))
