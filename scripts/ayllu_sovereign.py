#!/usr/bin/env python3
"""Probe keyless local runtimes and list Hub open weights. No vendor key."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

RUNTIMES = [
    ("ollama", "http://127.0.0.1:11434/v1/models"),
    ("llamacpp", "http://127.0.0.1:8081/v1/models"),
    ("lmstudio", "http://127.0.0.1:1234/v1/models"),
    ("vllm", "http://127.0.0.1:8000/v1/models"),
    ("sglang", "http://127.0.0.1:30000/v1/models"),
    ("chaski", "http://127.0.0.1:8098/v1/models"),
]
WEIGHTS = [
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-0.6B",
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-ai/DeepSeek-V4-Flash",
    "moonshotai/Kimi-K2.6",
]


def get(url: str, timeout: int = 3):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read()[:2000]
    except urllib.error.HTTPError as err:
        return err.code, b""
    except Exception as err:
        return 0, str(err).encode()


def main() -> int:
    extra = os.environ.get("SOVEREIGN_BASE_URL", "").rstrip("/")
    rows = list(RUNTIMES)
    if extra:
        rows.insert(0, ("env", extra + "/v1/models"))
    print("== keyless runtimes ==")
    up = 0
    for name, url in rows:
        status, body = get(url)
        flag = "MEASURED" if status == 200 else "UNAVAILABLE"
        if status == 200:
            up += 1
        print(f"{name:10} {flag:12} {url} {status}")
    print("up", up, "— SOVEREIGN speech only if up>0")
    print("== hub catalog (no token) ==")
    for mid in WEIGHTS:
        print("https://huggingface.co/" + mid)
    q = os.environ.get("HUB_SEARCH", "qwen")
    status, body = get(
        "https://huggingface.co/api/models?search=" + q + "&sort=downloads&limit=5",
        timeout=8,
    )
    print("hub_search", q, status)
    if status == 200:
        try:
            for row in json.loads(body.decode())[:5]:
                print(" ", row.get("id") or row.get("modelId"))
        except Exception:
            pass
    return 0 if up else 2


if __name__ == "__main__":
    raise SystemExit(main())
