import os
from dotenv import load_dotenv
from torch import lu
# from config import global_config as config  
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
load_dotenv()
def get_llm_client():
    model_name = os.getenv("MODEL_NAME", "deepseek")
    if model_name == "deepseek":
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        # client  = ChatOpenAI(
        #     model="deepseek-chat",
        #     openai_api_key=API_KEY,
        #     openai_api_base=BASE_URL,
        #     temperature=0.7)
        client  = ChatOpenAI(
            model="deepseek-chat",
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.7)
        return client
    if model_name == "gpt-5.4-mini":
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.ifopen.ai/v1")
        client  = ChatOpenAI(
            model="gpt-5.4-mini",
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.7)
        return client
    
def llm_invoke(llm_provider ,prompt: str) -> str:
    messages = build_messages(prompt)
    with get_openai_callback() as cb:
        response  = llm_provider.invoke(messages).content
    return response,cb

# ...existing code...
# def llm_invoke(llm_provider ,prompt: str):
#     messages = build_messages(prompt)

#     # call provider and keep full response object if available
#     resp = llm_provider.invoke(messages)
#     content = resp.content
#     usage = None
#     if hasattr(resp, 'usage'):
#         usage = resp.usage
#     elif hasattr(resp, 'raw_response') and hasattr(resp.raw_response, 'usage'):
#         usage = resp.raw_response.usage
#     elif hasattr(resp, 'raw_response') and 'usage' in resp.raw_response:
#         usage = resp.raw_response['usage']
#     elif hasattr(resp, 'usage'):
#         usage = resp.usage

#     return content, usage
def calculate_deepseek_cost(cb, model_name="deepseek-chat"):
    """
    根据token使用量计算DeepSeek模型调用成本
    """
    # 定义模型单价（元/千tokens）。请注意，具体价格请以DeepSeek官方或您所用平台的最新公告为准。
    # 此处示例价格参考了腾讯云平台的计费规则[1,2](@ref)
    price_per_1k_tokens = {
        "deepseek-chat": {"input": 0.002, "output": 0.003},        # 例如 DeepSeek-V3 系列
        "deepseek-reasoner": {"input": 0.004, "output": 0.016},     # 例如 DeepSeek-R1 系列
        # 您可以在此添加更多模型及其单价
    }

    if model_name not in price_per_1k_tokens:
        raise ValueError(f"未找到模型 {model_name} 的定价信息。请检查模型名称或手动指定价格。")

    prices = price_per_1k_tokens[model_name]

    # 计算成本（元）
    # 从 cb 对象中获取总token数（提示词+补全）
    total_tokens = cb.total_tokens
    # 计算输入token成本（如果cb对象能区分输入输出，可用 cb.prompt_tokens 更精确计算）
    input_cost = (cb.prompt_tokens / 1000) * prices["input"]
    # 计算输出token成本（如果cb对象能区分输入输出，可用 cb.completion_tokens 更精确计算）
    output_cost = (cb.completion_tokens / 1000) * prices["output"]
    total_cost = input_cost + output_cost

    cost_info = {
        "model": model_name,
        "total_tokens": total_tokens,
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_cost": total_cost,
        "cost_breakdown": {
            "input_cost": input_cost,
            "output_cost": output_cost
        }
    }
    return cost_info

def build_messages(prompt: str):
    messages = []
    messages.append({"role": "user", "content": prompt})
    return messages

llm_client = get_llm_client()

# print(llm_invoke(llm_client, "Hello, how are you?"))