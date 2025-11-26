
import loguru
import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

# class GlobalConfig:
#     def __init__(self,config_path: str = "src/config.json"): 
#         self.load_config_json(config_path)
#         self._init_logger()
#     def load_config_json(self,config_path: str = "src/config.json"):
#         with open(config_path, 'r') as f:
#             self.config = json.load(f)
#     def _init_logger(self):
#         """Initialize the logger settings."""
#         log_dir =Path("./logs")
#         if not log_dir.exists():
#             log_dir.mkdir()
#         result_name = Path(str(self.get("result_dir"))).stem
#         time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
#         logger.add(
#             f"{log_dir}/{result_name}-{time_stamp}.log",
#             rotation="1 day",
#             retention="7 days",
#             level="DEBUG",
#         )


# global_config =  GlobalConfig(config_path="src/config.json")
def load_config(config_path: str = "src/config.json") -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)  
            return config
    except Exception as e:
        return {}


global_config = load_config("src/config.json")    
# init_logger()