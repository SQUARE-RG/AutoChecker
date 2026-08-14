import os
from dotenv import load_dotenv
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

load_dotenv()


def get_llm_client():
    model_name = os.getenv("MODEL_NAME", "deepseek")
    if "deepseek" in model_name:
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client = ChatOpenAI(
            model=model_name,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.7)
        return client


def llm_invoke(llm_provider, prompt: str, system_prompt: str = None) -> str:
    messages = build_messages(prompt, system_prompt)
    with get_openai_callback() as cb:
        response = llm_provider.invoke(messages).content
    return response, cb


def calculate_deepseek_cost(cb, model_name=None):
    """根据一次 LLM 调用的 callback 返回用量和花费信息（纯函数，不累积）。

    返回 dict:
        model, prompt_tokens, completion_tokens, cached_tokens,
        total_tokens, total_cost, cost_breakdown
    """
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")

    price_per_1k_tokens = {
        "deepseek-chat":       {"input": 0.002,  "output": 0.003},
        "deepseek-v4-flash":   {"input": 0.002,  "output": 0.003},
        "deepseek-reasoner":   {"input": 0.004,  "output": 0.016},
    }

    if model_name not in price_per_1k_tokens:
        model_name = "deepseek-chat"

    prices = price_per_1k_tokens[model_name]
    input_cost = (cb.prompt_tokens / 1000) * prices["input"]
    output_cost = (cb.completion_tokens / 1000) * prices["output"]

    return {
        "model": model_name,
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "cached_tokens": getattr(cb, "prompt_tokens_cached", 0),
        "total_tokens": cb.total_tokens,
        "total_cost": input_cost + output_cost,
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