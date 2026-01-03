import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
def get_llm_client():
    model_name = os.getenv("MODEL_NAME", "deepseek")
    if model_name == "deepseek":
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
        BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client  = ChatOpenAI(
            model="deepseek-chat",
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.7)
        return client
    
def llm_invoke(llm_provider ,prompt: str) -> str:
    messages = build_messages(prompt)
    response  = llm_provider.invoke(messages).content
    return response

def build_messages(prompt: str):
    messages = []
    messages.append({"role": "user", "content": prompt})
    return messages
llm_client = get_llm_client()