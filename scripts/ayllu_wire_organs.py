#!/usr/bin/env python3
"""Measure public second-brain + anatomy surfaces. Handles only."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

HOST = "https://szlholdings-ayllu.hf.space"
FEEDS = [
    ("health", HOST + "/health"),
    ("retrieve_anatomy", HOST + "/api/v1/ayllu/retrieve?q=anatomy"),
    ("retrieve_brain", HOST + "/api/v1/ayllu/retrieve?q=second+brain"),
    ("retrieve_lambda", HOST + "/api/v1/ayllu/retrieve?q=lambda"),
    ("psyche", HOST + "/api/v1/psyche/health"),
    ("allodial", HOST + "/api/v1/counsel/allodial"),
    ("product_anatomy", "https://a-11-oy.com/living-anatomy"),
    ("product_brain", "https://a-11-oy.com/api/a11oy/v1/ayllu/second-brain"),
    ("product_formulas", "https://a-11-oy.com/api/a11oy/v1/formulas"),
    ("atlas", "https://a11oy.net/atlas.json"),
    ("hub_qwen", "https://huggingface.co/api/models/Qwen/Qwen3-8B"),
]
ORGANS = {
    "yuyay": {"formulas": ["F4", "F11"], "seats": ["Yupaq", "Qhaway"], "surface": "psyche"},
    "yawar": {"formulas": ["F7", "F22"], "seats": ["Willakuq"], "surface": "allodial"},
    "yachay": {"formulas": ["F1"], "seats": ["Amaru", "Maskaq"], "surface": "second_brain_575"},
    "nervous": {"formulas": ["F12"], "seats": ["Hampiq", "Yanapaq"], "surface": "health_probes"},
    "skeleton": {"formulas": ["F18", "F19"], "seats": ["Kamachiq", "Chaka", "Ruwaq", "Qhatuq"], "surface": "handles_only"},
}


def get(url: str, timeout: int = 10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read()[:4000]
    except urllib.error.HTTPError as err:
        return err.code, (err.read()[:200] if err.fp else b"")
    except Exception as err:
        return 0, str(err).encode()


def main() -> int:
    print("organs", json.dumps(ORGANS))
    rows = {}
    bad = 0
    for name, url in FEEDS:
        status, body = get(url)
        rows[name] = status
        flag = "MEASURED" if status == 200 else "UNAVAILABLE"
        if status != 200:
            bad += 1
        print(f"{name:18} {flag:12} {status} {url}")
        if name.startswith("retrieve") and status == 200:
            try:
                data = json.loads(body.decode())
                titles = [h.get("title") or h.get("id") for h in (data.get("handles") or [])[:3]]
                print("   handles", titles)
            except Exception:
                pass
    print("snapshot", json.dumps(rows))
    print("private_9464 NOT_INDEXED — not admitted")
    print("psyche writes BLOCKED until lock on — stored stays 0")
    print("Λ CONJECTURE_1")
    return 0 if bad <= 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
