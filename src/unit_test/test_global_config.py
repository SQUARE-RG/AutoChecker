
import sys
from pathlib import Path
import types

import pytest
import yaml



# from global_config import logger
def _import_global_config():
    # Create a lightweight fake `loguru` module so tests don't require external deps.
    # if 'loguru' not in sys.modules:
    #     fake_loguru = types.ModuleType('loguru')
    #     class _Logger:
    #         def info(self, *a, **k):
    #             return None
    #         def warning(self, *a, **k):
    #             return None
    #         def error(self, *a, **k):
    #             return None
    #     fake_loguru.logger = _Logger()
    #     sys.modules['loguru'] = fake_loguru
   

    # Ensure `src` is on sys.path so we can import `global_config` module
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from global_config import GlobalConfig
    return GlobalConfig


def test_singleton_class():
    # usages: pytest src/unit_test/test_global_config.py::test_singleton_class
    GlobalConfig = _import_global_config()
    gc1 = GlobalConfig()
    gc2 = GlobalConfig()
    assert gc1 is gc2


def test_load_config_from_generated_file():
    """Use the repo-provided config-generate.yaml and llm_keys.yaml (no temp files)."""
    # usages pytest src/unit_test/test_global_config.py::test_load_config_from_generated_file
    GlobalConfig = _import_global_config()

    # Locate the repo root and the provided config file (these are absolute in this repo)
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "config-generate.yaml"

    assert config_path.exists(), f"Expected config file at {config_path}"

    # Instantiate GlobalConfig with the provided YAML file
    gc = GlobalConfig(config_path=config_path)

    # Basic checks: values from config-generate.yaml
    assert gc.get("LLVM_dir") == "/root/code_check/llvm-project"
    assert gc.get("model") == "deepseek-chat"
    assert gc.get("result_dir") == "/root/code_check/result-generation"
    assert gc.get("key_file") == "/root/code_check/llm_keys.yaml"
    # key_file in config-generate.yaml is an absolute path in this repo
    keys_path_value = gc.get("key_file")
    assert keys_path_value, "config 'key_file' must be present"
    keys_path = Path(keys_path_value)

    # If path in config is not found, try a few repo-relative candidates
    if not keys_path.exists():
        # candidate: repo root joined with the stripped path
        keys_candidate = repo_root / keys_path_value.lstrip("/")
        if keys_candidate.exists():
            keys_path = keys_candidate
        else:
            # candidate: repo root + basename (handles cases where config uses /code_check/..)
            keys_candidate2 = repo_root / Path(keys_path_value).name
            if keys_candidate2.exists():
                keys_path = keys_candidate2

    assert keys_path.exists(), f"LLM keys file not found at {keys_path}"

    # Load expected keys from the existing file
    with open(keys_path, 'r') as f:
        expected_keys = yaml.safe_load(f) or {}

    # Ensure GlobalConfig loaded keys; if it didn't (because config used a different
    # absolute path), instruct gc to load from the discovered keys_path so we can
    # compare the actual loaded keys with the file on disk.
    # if not gc.get_key_config():
    #     gc.load_llm_key(str(keys_path))


    actual_keys = gc.get_key_config() or {}
    assert actual_keys["deepseek_key"] == expected_keys["deepseek_key"]
    assert actual_keys["base_url"] == expected_keys["base_url"]
    assert actual_keys == expected_keys

    # actual_keys = gc.get_key_config() or {}
    # assert isinstance(actual_keys, dict)

    # #逐字段比较：确保 expected 中的每个字段在实际值中存在且相等
    # for k, expected_v in expected_keys.items():
    #     assert k in actual_keys, f"Missing key '{k}' in gc._keys"
    #     assert actual_keys[k] == expected_v, f"Value mismatch for key '{k}': expected {expected_v!r}, got {actual_keys[k]!r}"

    # # 可选：确保没有遗漏的额外字段
    # assert set(actual_keys.keys()) == set(expected_keys.keys()), "Actual keys differ from expected keys"

