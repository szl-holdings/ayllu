"""UNSIGNED-honest council receipts.

Never fabricates a signature, a joule, a LIVE label, or a proven Λ.
When no Cosign/DSSE signer is injected, the envelope is explicitly UNSIGNED
and still hash-chained so a reader can replay the bytes.
"""
from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any, Callable, Optional

# Shared canonicalisation (szl-holdings/szl-evidence-core @ de27568d706c): identical bytes to
# the local implementation below for every valid JSON value, with the profile declared
# explicitly (CANON_UTF8: UTF-8). One deliberate difference: NaN/Infinity
# raise at emit time instead of producing text no conforming JSON reader can parse.
# The local implementation stays as the fallback so nothing here depends on the package.
try:
    from szl_evidence_core.canonical import CANON_UTF8 as _CANON_PROFILE
    from szl_evidence_core.canonical import canonical_bytes as _shared_canonical_bytes
    _CANON_SOURCE = "szl_evidence_core"
except Exception:  # pragma: no cover - fallback to the local implementation
    _CANON_PROFILE = 'szl.lambda/v1'
    _shared_canonical_bytes = None
    _CANON_SOURCE = "local"


PAYLOAD_TYPE = "application/vnd.szl.ayllu.receipt+json"


def canonical_dumps(value: Any) -> bytes:
    if _shared_canonical_bytes is not None:
        return _shared_canonical_bytes(value, profile=_CANON_PROFILE, check=False)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_dumps(value)).hexdigest()


def sha3_256_hex(data: bytes) -> str:
    return hashlib.sha3_256(data).hexdigest()


def wrap_unsigned(payload: dict[str, Any], *, honesty: str | None = None) -> dict[str, Any]:
    body = canonical_dumps(payload)
    return {
        "payloadType": PAYLOAD_TYPE,
        "payload": base64.b64encode(body).decode("ascii"),
        "payloadSha256": hashlib.sha256(body).hexdigest(),
        "payloadSha3_256": sha3_256_hex(body),
        "signatures": [],
        "signed": False,
        "honesty": honesty
        or "UNSIGNED — no Cosign/DSSE signer injected; no signature fabricated.",
    }


def make_receipt(
    payload: dict[str, Any],
    *,
    sign_fn: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Prefer an injected signer; otherwise emit an honest UNSIGNED envelope."""
    stamped = dict(payload)
    stamped.setdefault("issued_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    stamped.setdefault("lambda", {
        "status": "CONJECTURE_1",
        "never_a_theorem": True,
        "role": "advisory",
    })
    if callable(sign_fn):
        try:
            env = sign_fn(stamped)
            if isinstance(env, dict):
                out = dict(env)
                out.setdefault("signed", True)
                return out
        except Exception as exc:
            return wrap_unsigned(
                stamped,
                honesty=(
                    f"UNSIGNED — signer raised ({str(exc)[:80]}); "
                    "no signature fabricated."
                ),
            )
    return wrap_unsigned(stamped)


def chain_turns(turns: list[dict[str, Any]], *, genesis: str = "ayllu-genesis") -> dict[str, Any]:
    """Hash-chain each turn. SOFTWARE chain, not DSSE, not a proof of truth."""
    prev = genesis
    links = []
    for i, turn in enumerate(turns):
        digest = sha256_json({
            "persona": turn.get("persona"),
            "round": turn.get("round"),
            "answer": turn.get("answer"),
            "honesty": turn.get("honesty"),
            "stub": turn.get("stub"),
            "model": turn.get("model"),
        })
        link = {
            "index": i,
            "persona": turn.get("persona"),
            "round": turn.get("round", 1),
            "turn_sha256": digest,
            "prev": prev,
            "link_sha256": hashlib.sha256(f"{prev}:{digest}".encode()).hexdigest(),
        }
        prev = link["link_sha256"]
        links.append(link)
    return {
        "schema": "szl.ayllu.turn-chain/v1",
        "kind": "SOFTWARE",
        "head": prev,
        "count": len(links),
        "links": links,
        "honesty": "Hash chain over turn bytes. Not semantic consensus. Not DSSE.",
    }
