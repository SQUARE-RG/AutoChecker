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
        msg = llm_provider.invoke(messages)
    # 把响应的标准字段附加到 cb 上，供 calculate_deepseek_cost 读取：
    # - 实际模型名（response_metadata["model_name"]）
    # - 标准化用量（usage_metadata，含 cache_read / reasoning 细分）
    cb.llm_model_name = msg.response_metadata.get("model_name") or os.getenv("MODEL_NAME")
    cb.llm_usage_metadata = msg.usage_metadata
    return msg.content, cb


# deepseek 系列模型定价表（元 / 百万 tokens）
DEEPSEEK_PRICE_PER_1M_TOKENS = {
    "deepseek-v4-flash": {
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
    model_name = getattr(cb, "llm_model_name", None) or model_name or os.getenv("MODEL_NAME", "deepseek-chat")

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