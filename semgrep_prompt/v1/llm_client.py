#!/usr/bin/env python3
"""LLM client wrapper used by the Semgrep rule tool."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


DEFAULT_LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.ifopen.ai/v1")
DEFAULT_LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-5.4-mini")
DEFAULT_LLM_API_KEY = os.environ.get("LLM_API_KEY", "")


@dataclass
class LLMConfig:
    api_key: str = DEFAULT_LLM_API_KEY
    base_url: str = DEFAULT_LLM_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    timeout: float = 120.0
    retries: int = 2


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.retries,
        )
        self.model = config.model

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        last_response = ""
        for attempt in range(3):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            content = self._content(response)
            if content.strip():
                return content
            last_response = str(response)
            time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"LLM returned empty content: {last_response[:500]}")

    def ask_json(self, prompt: str, retries: int = 2) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": prompt},
        ]
        last_response = ""
        for _ in range(retries + 1):
            last_response = self.chat(messages, temperature=0.0)
            try:
                return extract_json_object(last_response)
            except ValueError as exc:
                messages.extend(
                    [
                        {"role": "assistant", "content": last_response},
                        {"role": "user", "content": f"JSON parse failed: {exc}. Return strict JSON only."},
                    ]
                )
        raise ValueError(f"Failed to parse JSON response: {last_response[:600]}")

    @staticmethod
    def _content(response: Any) -> str:
        if not response.choices:
            return ""
        return response.choices[0].message.content or ""


def create_llm_client(
    api_key: str,
    base_url: str,
    model: str,
    request_timeout: float,
    request_retries: int,
) -> LLMClient:
    return LLMClient(
        LLMConfig(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout=request_timeout,
            retries=request_retries,
        )
    )


def strip_code_fence(text: str) -> str:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json|yaml|yml)?", "", value).strip()
        if value.endswith("```"):
            value = value[:-3].strip()
    return value


def extract_json_object(text: str) -> dict[str, Any]:
    clean = strip_code_fence(text)
    candidates = [clean]
    first = clean.find("{")
    last = clean.rfind("}")
    if first != -1 and last > first:
        candidates.append(clean[first : last + 1])

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    raise ValueError("LLM response is not a JSON object")
