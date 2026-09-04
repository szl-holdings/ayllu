#!/usr/bin/env python3
"""Free Hugging Face path. Token is free. No xAI. No paid endpoints."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen3-0.6B",
]
ROUTER = "https://router.huggingface.co/v1/chat/completions"


def get(url: str, timeout: int = 8):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read()[:4000]
    except urllib.error.HTTPError as err:
        return err.code, err.read()[:400] if err.fp else b""
    except Exception as err:
        return 0, str(err).encode()


def catalog():
    print("== Hub catalog (no token) ==")
    for mid in MODELS:
        st, body = get("https://huggingface.co/api/models/" + mid, timeout=8)
        print(mid, st)


def infer(token: str) -> int:
    print("== free inference (HF_TOKEN) ==")
    payload = json.dumps({
        "model": MODELS[0],
        "max_tokens": 80,
        "messages": [
            {"role": "system", "content": "You are Maskaq. Fail-closed. Λ = Conjecture 1. Under 60 words."},
            {"role": "user", "content": "Name the Ayllu retrieve contract in one sentence."},
        ],
    }).encode()
    req = urllib.request.Request(
        ROUTER,
        data=payload,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as res:
            data = json.loads(res.read().decode())
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content")
        print("LIVE-HF", MODELS[0], (text or "")[:400])
        return 0
    except urllib.error.HTTPError as err:
        print("HF inference HTTP", err.code, "SOFTWARE fallback. Not fabricated LIVE.")
        return 2
    except Exception as err:
        print("HF inference UNAVAILABLE", type(err).__name__, "SOFTWARE fallback.")
        return 2


def main() -> int:
    catalog()
    token = os.environ.get("HF_TOKEN") or ""
    if not token:
        print("HF_TOKEN UNAVAILABLE — catalog only. Inference 401 without the free token.")
        return 2
    return infer(token)


if __name__ == "__main__":
    raise SystemExit(main())
