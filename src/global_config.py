import loguru
import yaml
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = loguru.logger
class GlobalConfig:
    """Class to manage global configuration settings.

    This class implements a simple singleton pattern so that any call to
    `GlobalConfig()` returns the same object. If a different `config_path` is
    provided on a subsequent call, the instance will reload configuration from
    that path.
    """
    _instance: Optional['GlobalConfig'] = None

    def __new__(cls, config_path: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # mark as not yet initialized
            cls._instance._singleton_initialized = False
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        # First initialization: set up state and load config
        if not getattr(self, "_singleton_initialized", False):
            self.config_path = config_path 
            # 项目配置
            self.config: Dict[str, Any] = {}
            # llm 配置
            self._keys: Dict[str, Any] = {}
            self.load_config(config_path)
            self._singleton_initialized = True
            
            return

        # If already initialized but a new config_path is provided and differs,
        # update the path and reload configuration.
        if config_path is not None:
            new_path = config_path if isinstance(config_path, Path) else Path(config_path)
            if new_path != getattr(self, "config_path", None):
                self.config_path = new_path
                self.load_config()
    def _init_logger(self):
        """Initialize the logger settings."""
        log_dir =Path("./logs")
        if not log_dir.exists():
            log_dir.mkdir()
        result_name = Path(str(self.get("result_dir"))).stem
        time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        logger.add(
            f"{log_dir}/{result_name}-{time_stamp}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG",
        )
    def load_config(self, config_path: str = "config.yaml") -> None:
        """Load configuration from a YAML file."""
        try:
            with open(str(config_path), 'r') as file:
                self.config = yaml.safe_load(file) or {}
                logger.info(f"Configuration loaded from {config_path}.")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")

        # 获取llm keys
        keys_path = self.get("key_file", "llm_keys.yaml")
        # llm api keys保存到_keys字典里
        self.load_llm_key(keys_path)
        self._init_logger()

    def load_llm_key(self, path: str):
        try:
            with open(path, 'r') as file:
                self._keys = yaml.safe_load(file) or {}
                logger.info(f"LLM keys loaded from {path}.")
        except Exception as e:
            logger.error(f"Failed to load LLM keys file: {e}")
                
    def get_key_config(self) -> Dict[str, Any]:
        """Get the LLM keys configuration."""
        return self._keys
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key."""
        self.config[key] = value
        logger.info(f"Set config '{key}' to '{value}'.")

    def save_config(self) -> None:
        """Save the current configuration to a YAML file."""
        try:
            with open(self.config_path, 'w') as file:
                yaml.safe_dump(self.config, file)
                logger.info(f"Configuration saved to {self.config_path}.")
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")

global_config = GlobalConfig()


