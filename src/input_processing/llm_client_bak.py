from __future__ import annotations

import os


def create_llm_client(
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    timeout_seconds: int = 300,
    max_retries: int = 0,
):
    try:
        from dotenv import load_dotenv
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Rule extraction requires python-dotenv and langchain-openai"
        ) from exc

    load_dotenv()
    resolved_model = model or os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or "deepseek-chat"
    resolved_key = (
        api_key
        or os.getenv("LLM_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    resolved_url = (
        base_url
        or os.getenv("LLM_BASE_URL")
        or os.getenv("DEEPSEEK_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
    )
    if not resolved_url and "deepseek" in resolved_model.lower():
        resolved_url = "https://api.deepseek.com"
    if not resolved_key or resolved_key == "your_default_api_key_here":
        raise RuntimeError(
            "LLM API key is missing; set LLM_API_KEY or DEEPSEEK_API_KEY"
        )
    kwargs = dict(
        model=resolved_model,
        api_key=resolved_key,
        temperature=0,
        timeout=timeout_seconds,
        # Retries are handled by the input-processing pipeline so that every
        # attempt is logged and bounded consistently across providers.
        max_retries=max_retries,
    )
    if resolved_url:
        kwargs["base_url"] = resolved_url
    return ChatOpenAI(**kwargs)


def invoke_text(client, user_prompt: str, system_prompt: str) -> str:
    response = client.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            str(item.get("text", "")) if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)
