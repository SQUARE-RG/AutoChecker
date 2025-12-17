from langchain_community.callbacks import get_openai_callback
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from llm_interface.llm_provider import llm_client
from llm_interface.llm_provider import llm_invoke


# 计算本次调用的成本
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

# 初始化模型和模板
# llm = OpenAI(model_name="gpt-3.5-turbo-instruct")  # 使用补全模型
template = PromptTemplate.from_template("请写一首关于{theme}的五言绝句。")

query = template.format_prompt(theme="春天")
# 使用 get_openai_callback 跟踪调用

response,cb = llm_invoke(llm_client, query.to_string())
print(f"模型回复: {response}")



# 调用完成后，打印汇总的 token 使用情况
print(f"\n=== Token 消耗统计 ===")
print(f"提示词 Token 数 (Prompt Tokens): {cb.prompt_tokens}")
print(f"补全 Token 数 (Completion Tokens): {cb.completion_tokens}")
print(f"总 Token 数 (Total Tokens): {cb.total_tokens}")
# print(f"估算成本 (USD): ${cb.total_cost:.6f}")
cost = calculate_deepseek_cost(cb, model_name="deepseek-chat")
print(f"估算成本 (元): ¥{cost['total_cost']:.6f}")