
import loguru
import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

def load_config(config_path: str = "src/config.json") -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)  
            return config
    except Exception as e:
        return {}


global_config = load_config("src/config.json")    
