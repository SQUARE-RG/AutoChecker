import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_default_api_key_here")
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")

