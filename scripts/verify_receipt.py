"""Replay an Ayllu UNSIGNED receipt. Fail closed if signatures are claimed
without being present, if the required payload/digest fields are malformed,
or if payload bytes do not match payloadSha256.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import sys


def verify(env: dict) -> dict:
    if not isinstance(env, dict):
        return {
            "ok": False,
            "reasons": ["receipt must be a JSON object"],
            "payloadSha256": None,
            "signed": False,
            "honesty": None,
        }
    reasons = []
    if env.get("signed") and not env.get("signatures"):
        reasons.append("signed=true but signatures empty — fabricated claim")
    payload_b64 = env.get("payload")
    try:
        if not isinstance(payload_b64, str) or not payload_b64:
            raise ValueError("payload must be a non-empty base64 string")
        raw = base64.b64decode(payload_b64, validate=True)
    except (ValueError, binascii.Error):
        reasons.append("payload must be a non-empty valid base64 string")
        raw = b""
    digest = hashlib.sha256(raw).hexdigest()
    declared = env.get("payloadSha256")
    if not isinstance(declared, str) or re.fullmatch(r"[0-9a-f]{64}", declared) is None:
        reasons.append("payloadSha256 must be a lowercase SHA-256 digest")
    elif declared != digest:
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
