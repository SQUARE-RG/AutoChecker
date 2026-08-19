#!/usr/bin/env python3
"""测试 src/llm_interface/llm_provider.py 是否正常工作。

检查项：
1. llm_client 初始化
2. 简单 LLM 调用
3. 计费字段完整（model/token/cost/pricing_source/currency）

用法:
    cd /root/code_check
    /root/anaconda3/envs/code_check/bin/python scripts/test_llm_provider.py
"""

import os
import sys
from pathlib import Path

# 统一约束：必须从项目根目录运行（.env 与 config 路径依赖 CWD）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
os.chdir(str(_PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(_PROJECT_ROOT / ".env")

from llm_interface.llm_provider import (  # noqa: E402
    llm_client, llm_invoke, calculate_deepseek_cost,
)


def main() -> None:
    print("=== 1. 客户端初始化 ===")
    print(f"  llm_client: {type(llm_client).__name__}")
    print(f"  MODEL_NAME: {os.getenv('MODEL_NAME')}")

    print()
    print("=== 2. 简单调用 ===")
    try:
        answer, cb = llm_invoke(llm_client, "What is 3*7? Answer in one short sentence.")
        print(f"  调用成功: {answer.strip()}")
    except Exception as e:
        print(f"  调用失败: {type(e).__name__}: {e}")
        sys.exit(1)

    print()
    print("=== 3. 计费字段 ===")
    cost = calculate_deepseek_cost(cb)
    for k in ["model", "prompt_tokens", "completion_tokens", "cached_tokens",
              "reasoning_tokens", "total_tokens", "total_cost",
              "pricing_source", "currency"]:
        print(f"  {k}: {cost.get(k)}")

    print()
    print("=== 测试通过：llm_provider 正常工作 ===")


if __name__ == "__main__":
    main()
