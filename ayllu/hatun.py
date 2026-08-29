"""Hatun-MCP probe — live public health, fail-closed tools.

Canonical: https://github.com/szl-holdings/hatun-mcp
Hosted:    https://szlholdings-hatun-mcp.hf.space

Anonymous healthz is LIVE process liveness only. tools/list and state-changing
calls need a session / key — we never fabricate a tool result.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

HATUN_BASE = os.environ.get(
    "HATUN_MCP_URL", "https://szlholdings-hatun-mcp.hf.space"
).rstrip("/")


def _get(path: str, timeout: float = 6.0) -> tuple[int, Any]:
    url = HATUN_BASE + path
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return int(resp.status), json.loads(raw)
            except json.JSONDecodeError:
                return int(resp.status), {"raw": raw[:400]}
    except urllib.error.HTTPError as exc:
        return int(exc.code), {"error": exc.reason}
    except Exception as exc:
        return 0, {"error": str(exc)[:160]}


def status() -> dict[str, Any]:
    code, body = _get("/healthz")
    ready_code, ready_body = _get("/readyz")
    live = code == 200 and isinstance(body, dict) and body.get("status") == "ok"
    return {
        "schema": "szl.ayllu.hatun/v1",
        "source": "https://github.com/szl-holdings/hatun-mcp",
        "endpoint": HATUN_BASE,
        "healthz": {"http": code, "body": body, "label": "LIVE" if live else "UNAVAILABLE"},
        "readyz": {
            "http": ready_code,
            "body": ready_body,
            "label": "LIVE" if ready_code == 200 else "UNAVAILABLE",
            "note": "readyz=200 is signer+chain readiness, not organ uptime",
        },
        "tools_list": "NOT_PROBED — initialize/tools/list may require a session; not fabricated",
        "ok": live,
        "honesty": (
            "healthz is process liveness only. Upstream a11oy/killinchu organs are "
            "not implied LIVE. State-changing tools stay gated."
        ),
    }
