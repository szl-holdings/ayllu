"""Standalone model backend for Ayllu.

Probe order (first reachable live path wins):

0. XAI_API_KEY → https://api.x.ai/v1  (grok-4.5) — Space LIVE path
1. AYLLU_OPENAI_BASE (default http://127.0.0.1:8098/v1) — CHASKI-R2 OpenAI-compat
2. OLLAMA_HOST OpenAI-compat (default http://127.0.0.1:11434/v1)
3. OPENAI_BASE_URL if explicitly set

If none of those answer, `model_complete` returns a clearly-labeled SOFTWARE
advisory from the persona domain. It NEVER fabricates LIVE, never pretends a
missing backend answered, and never claims verified truth.

This module does not import a11oy. The a11oy organ still exists; this is the
product split-out.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

DEFAULT_OPENAI = os.environ.get("AYLLU_OPENAI_BASE", "http://127.0.0.1:8098/v1").rstrip("/")
DEFAULT_OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
XAI_BASE = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/")
DEFAULT_TIMEOUT = 2.5


def _headers(extra: dict[str, str] | None = None, bearer: str | None = None) -> dict[str, str]:
    h = {"Accept": "application/json"}
    if extra:
        h.update(extra)
    if bearer:
        h["Authorization"] = f"Bearer {bearer}"
    return h


def _get(url: str, timeout: float = DEFAULT_TIMEOUT, bearer: str | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET", headers=_headers(bearer=bearer))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", "replace")
    except Exception as exc:
        return 0, str(exc)[:160]


def _post_json(
    url: str,
    body: dict[str, Any],
    timeout: float,
    bearer: str | None = None,
) -> tuple[int, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers=_headers({"Content-Type": "application/json"}, bearer=bearer),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return int(resp.status), json.loads(raw)
            except json.JSONDecodeError:
                return int(resp.status), {"raw": raw[:400]}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            return int(exc.code), json.loads(raw)
        except Exception:
            return int(exc.code), {"error": raw[:400]}
    except Exception as exc:
        return 0, {"error": str(exc)[:160]}


def _probe_openai(base: str) -> dict[str, Any]:
    status, body = _get(f"{base}/models")
    ok = status == 200
    return {
        "base": base,
        "reachable": ok,
        "http_status": status,
        "hint": body[:180] if not ok else "ok",
    }


def _probe_xai() -> dict[str, Any]:
    key = (os.environ.get("XAI_API_KEY") or "").strip()
    if not key:
        return {
            "base": XAI_BASE,
            "reachable": False,
            "http_status": 0,
            "hint": "XAI_API_KEY absent — no LIVE grok fabricated.",
            "model": "grok-4.5",
        }
    status, body = _get(f"{XAI_BASE}/models", timeout=4.0, bearer=key)
    return {
        "base": XAI_BASE,
        "reachable": status == 200,
        "http_status": status,
        "hint": "ok" if status == 200 else body[:180],
        "model": "grok-4.5",
        "key_present": True,
    }


def backend_status() -> dict[str, Any]:
    """Side-effect-free snapshot of what this process can do NOW."""
    if os.environ.get("AYLLU_FORCE_SOFTWARE", "").strip() in ("1", "true", "yes"):
        return {
            "mode": "software",
            "chosen": None,
            "probes": {"forced": True},
            "note": "AYLLU_FORCE_SOFTWARE — SOFTWARE path, no LIVE fabricated.",
            "backend": "ayllu.backend.model_complete",
            "lambda": "CONJECTURE_1",
        }
    xai = _probe_xai()
    chaski = _probe_openai(DEFAULT_OPENAI)
    ollama_openai = _probe_openai(f"{DEFAULT_OLLAMA}/v1")
    ollama_tags_status, ollama_tags_body = _get(f"{DEFAULT_OLLAMA}/api/tags")
    explicit = os.environ.get("OPENAI_BASE_URL", "").rstrip("/")
    explicit_probe = _probe_openai(explicit) if explicit else None

    if xai["reachable"]:
        mode, chosen = "live", {"kind": "xai-grok", **xai}
    elif chaski["reachable"]:
        mode, chosen = "live", {"kind": "chaski-r2", **chaski}
    elif ollama_openai["reachable"] or ollama_tags_status == 200:
        mode, chosen = "live", {
            "kind": "ollama",
            "openai": ollama_openai,
            "tags_http": ollama_tags_status,
        }
    elif explicit_probe and explicit_probe["reachable"]:
        mode, chosen = "live", {"kind": "openai-compat", **explicit_probe}
    else:
        mode, chosen = "software", None

    return {
        "mode": mode,
        "chosen": chosen,
        "probes": {
            "xai_grok": xai,
            "chaski_r2": chaski,
            "ollama_openai": ollama_openai,
            "ollama_tags_http": ollama_tags_status,
            "explicit_openai": explicit_probe,
        },
        "note": {
            "live": (
                "real model answers via a reachable OpenAI-compatible endpoint "
                "(grok-4.5 when XAI_API_KEY is set). Outputs remain unverified "
                "model text — not MEASURED truth."
            ),
            "software": (
                "no reachable live backend — clearly-labeled SOFTWARE advisory "
                "from persona domain. No fabrication of LIVE."
            ),
        }.get(mode, ""),
        "backend": "ayllu.backend.model_complete",
        "lambda": "CONJECTURE_1",
    }


def software_complete(system: str, prompt: str, *, persona: Optional[str] = None) -> dict[str, Any]:
    """Domain-bound SOFTWARE advisory. Never labeled LIVE."""
    head = (system or "").strip().splitlines()
    title = head[0][:120] if head else (persona or "persona")
    clipped = (prompt or "").strip()[:600]
    text = (
        f"[SOFTWARE] {persona or 'persona'} speaking. No reachable live model backend.\n"
        f"Identity: {title}\n"
        f"House law: fail-closed Λ-gate; two-person attestation for state changes; "
        f"Λ uniqueness is Conjecture 1 and is never a theorem; proposal-only.\n"
        f"Question:\n{clipped}\n\n"
        "Domain-bound advisory (SOFTWARE, not LIVE, not MEASURED):\n"
        "- I will not invent a LIVE completion, a signature, a joule, or a proven Λ.\n"
        "- I stay inside my remit; questions outside it belong to another seat.\n"
        "- Honest dissent beats false consensus.\n"
        "- If you set XAI_API_KEY (grok-4.5), or wire CHASKI-R2 on :8098 / Ollama on :11434, "
        "this seat answers LIVE and still remains unverified model text.\n"
        "I don't know anything I have not grounded in a receipt."
    )
    return {
        "text": text,
        "model": "ayllu-software",
        "stub": True,
        "timeout": False,
        "kind": "SOFTWARE",
        "honesty": (
            "SOFTWARE advisory — no reachable live backend; no answer fabricated as LIVE."
        ),
    }


async def model_complete(
    system: str,
    prompt: str,
    tier: Optional[str] = None,
    *,
    persona: Optional[str] = None,
    max_tokens: int = 384,
    temperature: float = 0.4,
    timeout_s: float = 45.0,
    **_ignored: Any,
) -> dict[str, Any]:
    """Adapter matching ayllu.loop.run_turn's model_complete contract."""
    status = backend_status()
    bounded_tokens = max(1, min(int(max_tokens), 2048))
    bounded_timeout = max(0.1, min(float(timeout_s), 120.0))
    messages = [
        {"role": "system", "content": system or ""},
        {"role": "user", "content": prompt or ""},
    ]

    if status["mode"] != "live":
        out = software_complete(system, prompt, persona=persona)
        out["token_budget"] = bounded_tokens
        out["timeout_s"] = bounded_timeout
        out["tier_advisory"] = tier
        out["backend_status"] = status
        return out

    chosen = status["chosen"] or {}
    kind = chosen.get("kind")
    bearer: str | None = None
    if kind == "xai-grok":
        url = f"{XAI_BASE}/chat/completions"
        model = os.environ.get("AYLLU_MODEL", "grok-4.5")
        bearer = (os.environ.get("XAI_API_KEY") or "").strip() or None
    elif kind == "chaski-r2":
        url = f"{DEFAULT_OPENAI}/chat/completions"
        model = os.environ.get("AYLLU_MODEL", "chaski-r2")
    elif kind == "ollama":
        url = f"{DEFAULT_OLLAMA}/v1/chat/completions"
        model = os.environ.get("AYLLU_MODEL", os.environ.get("OLLAMA_MODEL", "khipu"))
    else:
        base = (chosen.get("base") or os.environ.get("OPENAI_BASE_URL", "")).rstrip("/")
        url = f"{base}/chat/completions"
        model = os.environ.get("AYLLU_MODEL", "gpt-4o-mini")

    code, body = _post_json(
        url,
        {
            "model": model,
            "messages": messages,
            "max_tokens": bounded_tokens,
            "temperature": temperature,
        },
        bounded_timeout,
        bearer=bearer,
    )
    if code != 200 or not isinstance(body, dict):
        out = software_complete(system, prompt, persona=persona)
        out["token_budget"] = bounded_tokens
        out["timeout_s"] = bounded_timeout
        out["honesty"] = (
            f"SOFTWARE fallback — live probe was up but completion HTTP {code}; "
            "no LIVE answer fabricated."
        )
        out["upstream"] = {"http": code, "body": str(body)[:240]}
        return out

    try:
        text = body["choices"][0]["message"]["content"]
    except Exception:
        out = software_complete(system, prompt, persona=persona)
        out["honesty"] = (
            "SOFTWARE fallback — upstream JSON missing choices[0].message.content; "
            "no LIVE answer fabricated."
        )
        return out

    used = (body.get("model") or model)
    return {
        "text": text,
        "model": used,
        "stub": False,
        "timeout": False,
        "kind": "LIVE",
        "token_budget": bounded_tokens,
        "timeout_s": bounded_timeout,
        "honesty": (
            "LIVE via reachable OpenAI-compatible backend. Unverified model text — "
            "not MEASURED truth, not a theorem."
        ),
        "usage": body.get("usage"),
    }
