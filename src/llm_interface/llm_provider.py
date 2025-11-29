import os
from dotenv import load_dotenv
from torch import lu
from config import global_config as config  
from langchain_openai import ChatOpenAI

load_dotenv()




def get_llm_client():
    model_name = os.getenv("MODEL_NAME", "deepseek")
    if model_name == "deepseek":
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client  = ChatOpenAI(
            model_name="deepseek-chat",
            openai_api_key=API_KEY,
            openai_api_base=BASE_URL,
            temperature=0.7)
        return client
    
def llm_invoke(llm_provider ,prompt: str) -> str:
    messages = build_messages(prompt)
    response  = llm_provider.invoke(messages).content
    return response

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


def build_messages(prompt: str):
    messages = []
    messages.append({"role": "user", "content": prompt})
    return messages
llm_client = get_llm_client()