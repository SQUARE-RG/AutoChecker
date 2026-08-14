
from dotenv import load_dotenv
import loguru
import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
import chromadb

load_dotenv()
def load_config(config_path: str = "src/config.json") -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)  
            return config
    except Exception as e:
        return {}


global_config = load_config("src/config.json")    


AUTOCHECKER_ROOT_DIR = os.environ.get("AUTOCHECKER_ROOT_DIR", os.path.dirname(os.path.abspath(__file__)))

CODEQL_HOME = os.environ.get("CODEQL_HOME")
CODEQL_PATH = os.environ.get("CODEQL_PATH", f"{CODEQL_HOME}/codeql")

JAVA_SECURITY_QLPACK_PATH= os.environ.get("JAVA_SECURITY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/java-queries/")
JAVA_LIBRARY_QLPACK_PATH = os.environ.get("JAVA_LIBRARY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/java-all/")

CPP_SECURITY_QLPACK_PATH = os.environ.get("CPP_SECURITY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/cpp-queries/")
CPP_LIBRARY_QLPACK_PATH = os.environ.get("CPP_LIBRARY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/cpp-all/")

PYTHON_SECURITY_QLPACK_PATH = os.environ.get("PYTHON_SECURITY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/python-queries/")
PYTHON_LIBRARY_QLPACK_PATH = os.environ.get("PYTHON_LIBRARY_QLPACK_PATH", f"{CODEQL_HOME}/qlpacks/codeql/python-all/")



# ChromaDB connection settings
# Set CHROMA_HOST to use HTTP client (Docker/remote), unset for local PersistentClient
CHROMA_HOST = os.environ.get("CHROMA_HOST", None)
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
CHROMA_AUTH_TOKEN = os.environ.get("CHROMA_AUTH_TOKEN", "test")
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH",os.path.join(AUTOCHECKER_ROOT_DIR,  "codeql_collect_uniform", "chroma_db"))

CHROMA_MCP_PATH='mcp__chroma__'  # Prefix for MCP tool calls to ChromaDB in prompts
def get_chroma_client():
    """Return a ChromaDB client based on environment configuration.

    - If CHROMA_HOST is set: returns HttpClient (for Docker / remote ChromaDB server)
    - Otherwise: returns PersistentClient (for local development)
    """
    if chromadb is None:
        raise ImportError("chromadb is required to create a Chroma client")
    if CHROMA_HOST:
        return chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            headers={"Authorization": f"Bearer {CHROMA_AUTH_TOKEN}"} if CHROMA_AUTH_TOKEN else None,
        )
    else:
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
      
        return chromadb.PersistentClient(path=CHROMA_DB_PATH)