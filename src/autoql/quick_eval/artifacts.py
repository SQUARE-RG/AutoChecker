import hashlib
import json
import os
from pathlib import Path


def digest(path):
    return 'sha256:' + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n', encoding='utf-8')
    os.replace(tmp,path)


def safe_numbers(value):
    if isinstance(value, bool): return value
    if isinstance(value, int) and abs(value) > 9007199254740991:
        return {'kind':'integer','decimal':str(value)}
    if isinstance(value, list): return [safe_numbers(v) for v in value]
    if isinstance(value, dict): return {k:safe_numbers(v) for k,v in value.items()}
    return value
