import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import message_chunk_to_message

load_dotenv()


_DEFAULT_LLM_SETTINGS = {
    "streaming": False,
    "stream_output": True,
    "stream_usage": True,
    "timeout_seconds": 600,
    "max_retries": 3,
    "retry_base_delay_seconds": 2,
}


class EmptyLLMResponseError(RuntimeError):
    """Raised when a completed model response has no text or tool calls."""


def get_llm_settings() -> dict[str, Any]:
    """Load the shared LLM runtime settings from src/config.json."""
    config_path = Path(__file__).resolve().parents[1] / "config.json"
    settings = dict(_DEFAULT_LLM_SETTINGS)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        configured = payload.get("llm", {})
        if isinstance(configured, dict):
            settings.update(configured)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(f"读取LLM配置失败，使用默认值: {type(exc).__name__}: {exc}")

    settings["streaming"] = bool(settings["streaming"])
    settings["stream_output"] = bool(settings["stream_output"])
    settings["stream_usage"] = bool(settings["stream_usage"])
    settings["timeout_seconds"] = max(1, int(settings["timeout_seconds"]))
    settings["max_retries"] = max(0, int(settings["max_retries"]))
    settings["retry_base_delay_seconds"] = max(
        0.0, float(settings["retry_base_delay_seconds"])
    )
    return settings


def get_llm_client():
    settings = get_llm_settings()
    model_name = os.getenv("MODEL_NAME", "deepseek")
    if "deepseek" in model_name:
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client = ChatOpenAI(
            model=model_name,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.7,
            timeout=settings["timeout_seconds"],
            # The shared invocation layer owns retries so partial streams can
            # be discarded deterministically before retrying the whole call.
            max_retries=0,
        )
        return client


def llm_invoke(llm_provider, prompt: str, system_prompt: str = None):
    messages = build_messages(prompt, system_prompt)
    msg, cb = llm_invoke_messages(llm_provider, messages)
    return _message_text(msg), cb


def llm_invoke_messages(llm_provider, messages, label: str = ""):
    """Invoke an LLM in configured mode and always return one complete message.

    Streaming chunks are visible while arriving, but callers receive the same
    complete AIMessage shape as the non-streaming path. This preserves text
    parsing and LangGraph tool_calls behavior.
    """
    settings = get_llm_settings()
    total_attempts = settings["max_retries"] + 1
    last_error = None
    for attempt in range(1, total_attempts + 1):
        try:
            with get_openai_callback() as cb:
                if settings["streaming"]:
                    msg = _invoke_streaming(
                        llm_provider,
                        messages,
                        stream_usage=settings["stream_usage"],
                        stream_output=settings["stream_output"],
                        label=label,
                        attempt=attempt,
                    )
                else:
                    msg = llm_provider.invoke(messages)
            _attach_usage(cb, msg)
            return msg, cb
        except Exception as exc:
            last_error = exc
            if not _is_retryable(exc) or attempt >= total_attempts:
                raise
            delay = min(
                60.0,
                settings["retry_base_delay_seconds"] * (2 ** (attempt - 1)),
            )
            logger.warning(
                "LLM请求失败，丢弃本次不完整响应并重试 "
                f"label={label or '-'} attempt={attempt}/{total_attempts} "
                f"error={type(exc).__name__}: {str(exc)[:200]} delay={delay:.1f}s"
            )
            if delay:
                time.sleep(delay)
    raise RuntimeError(f"LLM request failed: {last_error}")


def _invoke_streaming(
    llm_provider,
    messages,
    *,
    stream_usage: bool,
    stream_output: bool,
    label: str,
    attempt: int,
):
    chunks = []
    if stream_output:
        logger.info(f"LLM流式响应开始 label={label or '-'} attempt={attempt}")
    stream = llm_provider.stream(messages, stream_usage=stream_usage)
    try:
        for chunk in stream:
            chunks.append(chunk)
            if stream_output:
                text = _message_text(chunk)
                if text:
                    sys.stdout.write(text)
                    sys.stdout.flush()
    except BaseException:
        close = getattr(stream, "close", None)
        if callable(close):
            close()
        if stream_output:
            sys.stdout.write("\n")
            sys.stdout.flush()
        raise
    if stream_output:
        sys.stdout.write("\n")
        sys.stdout.flush()
        logger.info(f"LLM流式响应结束 label={label or '-'} attempt={attempt}")
    if not chunks:
        raise RuntimeError("LLM streaming response contained no events")
    aggregate = chunks[0]
    for chunk in chunks[1:]:
        aggregate += chunk
    message = message_chunk_to_message(aggregate)
    # An OpenAI-compatible endpoint may emit role/usage/final SSE events while
    # returning neither text nor a tool call.  Such a stream is not useful to
    # any caller and must enter the same whole-request retry path as a broken
    # connection.  Empty text remains valid for agent tool-call responses.
    if not _message_text(message).strip() and not getattr(message, "tool_calls", None):
        logger.warning(
            "LLM流式响应没有有效内容 "
            f"events={len(chunks)} "
            f"response_metadata={getattr(message, 'response_metadata', {})!r} "
            f"usage_metadata={getattr(message, 'usage_metadata', None)!r} "
            f"additional_kwargs={getattr(message, 'additional_kwargs', {})!r}"
        )
        raise EmptyLLMResponseError(
            "LLM streaming response contained events but no text or tool calls"
        )
    return message


def _message_text(message) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
        return "".join(parts)
    return str(content or "")


def _attach_usage(cb, msg) -> None:
    response_metadata = getattr(msg, "response_metadata", {}) or {}
    response_model = response_metadata.get("model_name")
    cb.llm_response_model_name = response_model
    # Keep billing based on the configured alias when the provider maps it to
    # an internal response model that is absent from our price table.
    cb.llm_model_name = os.getenv("MODEL_NAME") or response_model
    cb.llm_usage_metadata = getattr(msg, "usage_metadata", None)


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, EmptyLLMResponseError):
        return True
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


# deepseek 系列模型定价表（元 / 百万 tokens）
DEEPSEEK_PRICE_PER_1M_TOKENS = {
    "deepseek-v4-flash": {
        "input_cache_hit": 0.05,
        "input_cache_miss": 1.5,
        "output": 4.5,
    },
    "deepseek-v4-flash-krill": {
        "input_cache_hit": 0.05,
        "input_cache_miss": 1.5,
        "output": 4.5,
    },
    "deepseek-v4-flash-itkk":{
        "input_cache_hit": 0.05,
        "input_cache_miss": 1.5,
        "output": 4.5,
    },
    "deepseek-v4-flash-ustc-ascend":{
        "input_cache_hit": 0.05,
        "input_cache_miss": 1.5,
        "output": 4.5,
    },
    "deepseek-v4.1-flash-itkk":{
        "input_cache_hit": 0.05,
        "input_cache_miss": 1.5,
        "output": 4.5,
    }
}


def calculate_deepseek_cost(cb, model_name=None):
    """根据一次 LLM 调用的响应计算用量和花费（纯函数，不累积）。

    计价策略：
    - deepseek 系列模型 → 自定义定价表 DEEPSEEK_PRICE_PER_1M_TOKENS（元）
    - 其他模型 → langchain 官方 callback 的定价（USD，cb.total_cost）
    - 两者都查不到 → cost = 0，token 用量照常读取

    model 和 token 均从真实响应的标准字段读取：
    - model: response_metadata["model_name"]（回调附加在 cb.llm_model_name）
    - 用量: usage_metadata（input_tokens / output_tokens / cache_read / reasoning）

    返回 dict:
        model, prompt_tokens, completion_tokens, cached_tokens,
        reasoning_tokens, total_tokens, total_cost, pricing_source,
        currency, cost_breakdown
    """
    # 1. model：优先从响应读，其次显式参数，最后环境变量
    model_name = os.getenv("MODEL_NAME", "deepseek-chat") or model_name or getattr(cb, "llm_model_name", None)

    # 2. token：优先从响应的 usage_metadata 读，fallback 到 callback 属性
    um = getattr(cb, "llm_usage_metadata", None)
    if um:
        prompt_tokens = um.get("input_tokens", cb.prompt_tokens)
        completion_tokens = um.get("output_tokens", cb.completion_tokens)
        input_details = um.get("input_token_details") or {}
        output_details = um.get("output_token_details") or {}
        cached_tokens = input_details.get("cache_read", 0)
        reasoning_tokens = output_details.get("reasoning", 0)
    else:
        prompt_tokens = cb.prompt_tokens
        completion_tokens = cb.completion_tokens
        cached_tokens = getattr(cb, "prompt_tokens_cached", 0)
        reasoning_tokens = 0

    # 3. 计价：deepseek 系列用自定义表，其余用 langchain 官方 callback
    if "deepseek" in model_name:
        prices = DEEPSEEK_PRICE_PER_1M_TOKENS.get(model_name)
        if prices is None:
            logger.warning(f"deepseek 模型 {model_name} 不在自定义定价表中，cost 记为 0")
            total_cost = 0.0
            input_cost = 0.0
            output_cost = 0.0
            pricing_source = "none"
            currency = "CNY"
        else:
            uncached_prompt = max(prompt_tokens - cached_tokens, 0)
            input_cost_cached = (cached_tokens / 1_000_000) * prices["input_cache_hit"]
            input_cost_uncached = (uncached_prompt / 1_000_000) * prices["input_cache_miss"]
            output_cost = (completion_tokens / 1_000_000) * prices["output"]
            input_cost = input_cost_cached + input_cost_uncached
            total_cost = input_cost + output_cost
            pricing_source = "deepseek_table"
            currency = "CNY"
    else:
        # langchain 官方 callback 内置价格表（USD）；查不到时 cb.total_cost 为 0
        total_cost = getattr(cb, "total_cost", 0.0) or 0.0
        input_cost = 0.0   # 官方 callback 不提供输入/输出成本拆分
        output_cost = 0.0
        pricing_source = "langchain_official"
        currency = "USD"

    return {
        "model": model_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cached_tokens": cached_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "total_cost": total_cost,
        "pricing_source": pricing_source,
        "currency": currency,
        "cost_breakdown": {
            "input_cost": input_cost,
            "output_cost": output_cost,
        },
    }

def build_messages(prompt: str, system_prompt: str = None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages
llm_client = get_llm_client()
