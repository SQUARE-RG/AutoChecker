#!/usr/bin/env python3
"""Simple LLM connectivity test using DEEPSEEK_* env vars from repository .env.

Behavior:
- Locate a repository `.env` file (searching upward from script dir).
- Load env vars found there into the process environment (non-destructive).
- Send a small chat completion request to `${DEEPSEEK_BASE_URL}/chat/completions`.
- Print HTTP status and returned JSON (or error) so user can verify connectivity.

This is intentionally minimal and safe for quick connectivity checks.
"""

from pathlib import Path
import os
import json
import sys


def load_dotenv_search(start_dir: Path, filename: str = ".env"):
    cur = start_dir.resolve()
    root = Path(cur.root)
    while True:
        cand = cur / filename
        if cand.exists():
            return cand
        if cur == root:
            return None
        cur = cur.parent


def parse_and_apply_env(path: Path):
    applied = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        # Do not overwrite already-set environment variables
        if k not in os.environ:
            os.environ[k] = v
            applied[k] = v
    return applied


def main():
    start = Path(__file__).parent
    env_path = load_dotenv_search(start)
    if not env_path:
        print("No .env found in parent chain.")
    else:
        applied = parse_and_apply_env(env_path)
        print(f"Loaded .env from: {env_path} (applied {len(applied)} vars)")

    # Required vars
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL")
    model = os.environ.get("MODEL_NAME") or os.environ.get("MODEL")

    if not api_key or not base_url:
        print("Missing DEEPSEEK_API_KEY or DEEPSEEK_BASE_URL in environment.")
        return 2

    # construct endpoint; assume chat/completions is supported
    endpoint = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": model or "gpt-5-mini",
        "messages": [
            {"role": "user", "content": "Say hello in one short sentence."}
        ],
        "max_tokens": 64,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        import requests
    except Exception:
        print("`requests` not available. Please install it (pip install requests).", file=sys.stderr)
        return 3

    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    except Exception as e:
        print(f"Request failed: {e}")
        return 4

    print(f"HTTP {resp.status_code}")
    # Try to print nice JSON if possible
    try:
        j = resp.json()
        print(json.dumps(j, ensure_ascii=False, indent=2))
    except Exception:
        print(resp.text[:1000])

    return 0 if resp.status_code == 200 else 5


if __name__ == "__main__":
    raise SystemExit(main())
