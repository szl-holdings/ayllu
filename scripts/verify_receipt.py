"""Replay an Ayllu UNSIGNED receipt. Fail closed if signatures are claimed
without being present, or if payload bytes do not match payloadSha256.
"""
from __future__ import annotations

import base64
import hashlib
import json
import sys


def verify(env: dict) -> dict:
    reasons = []
    if env.get("signed") and not env.get("signatures"):
        reasons.append("signed=true but signatures empty — fabricated claim")
    payload_b64 = env.get("payload") or ""
    try:
        raw = base64.b64decode(payload_b64)
    except Exception:
        reasons.append("payload is not base64")
        raw = b""
    digest = hashlib.sha256(raw).hexdigest()
    declared = env.get("payloadSha256")
    if declared and declared != digest:
        reasons.append("payloadSha256 mismatch")
    return {
        "ok": not reasons,
        "reasons": reasons,
        "payloadSha256": digest,
        "signed": bool(env.get("signed")),
        "honesty": env.get("honesty"),
    }


def main() -> int:
    env = json.load(sys.stdin)
    result = verify(env)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
