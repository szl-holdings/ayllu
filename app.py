"""Ayllu Counsel — standalone FastAPI product.

Holographic chamber at GET /
Evidence-bound council at POST /api/v1/ayllu/council
Honesty labels: LIVE / SOFTWARE / UNSIGNED / NOT_MEASURED / CONJECTURE_1
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from ayllu import SCHEMA_COUNCIL, __version__
from ayllu import backend as _backend
from ayllu.converge import synthesize
from ayllu.estate import catalog
from ayllu.hatun import status as hatun_status
from ayllu.invariants import check as check_invariants
from ayllu.loop import run_turn
from ayllu.lounge import Lounge
from ayllu.model_binding import second_brain_binding
from ayllu.organs import anatomy, organ_for_persona
from ayllu.ouroboros import tax as ouroboros_tax
from ayllu.personas import ROSTER, get_persona
from ayllu.receipts import chain_turns, make_receipt, sha256_json

CHAMBER = Path(__file__).resolve().parent / "ayllu" / "static" / "chamber.html"
MAX_PROMPT_CHARS = 6000
MAX_BODY_BYTES = 24 * 1024
COUNCIL_MAX = 5
COUNCIL_DEBATE_MAX = 3
COUNCIL_DEFAULT = ["Amaru", "Kamachiq", "Qhatuq"]
ASK_MAX_TOKENS = 384
COUNCIL_MAX_TOKENS = 192
NS = "ayllu"

app = FastAPI(
    title="Ayllu Counsel",
    version=__version__,
    description="Evidence-bound holographic agent counsel. Λ = Conjecture 1.",
)
_LOUNGE = Lounge()


class _BodyTooLarge(ValueError):
    pass


class _RateBucket:
    def __init__(self, limit: int, window_s: float) -> None:
        self.limit = int(limit)
        self.window = float(window_s)
        self._hits: list[float] = []
        self._lock = threading.Lock()

    def check(self) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            self._hits = [t for t in self._hits if now - t < self.window]
            if len(self._hits) >= self.limit:
                retry = self.window - (now - self._hits[0])
                return False, max(1, int(retry) + 1)
            self._hits.append(now)
            return True, 0


_ASK_BUCKET = _RateBucket(30, 60.0)
_COUNCIL_BUCKET = _RateBucket(8, 60.0)


async def _bounded_json_body(request: Request) -> dict[str, Any]:
    declared = request.headers.get("content-length")
    if declared is not None:
        try:
            size = int(declared)
        except ValueError as exc:
            raise ValueError("invalid content-length") from exc
        if size < 0 or size > MAX_BODY_BYTES:
            raise _BodyTooLarge(f"request body exceeds {MAX_BODY_BYTES} bytes")
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_BODY_BYTES:
            raise _BodyTooLarge(f"request body exceeds {MAX_BODY_BYTES} bytes")
        data.extend(chunk)
    try:
        value = json.loads(bytes(data).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JSON body") from exc
    if not isinstance(value, dict):
        raise ValueError("request body must be a JSON object")
    return value


def _clip_prompt(raw: Any) -> str:
    text = str(raw or "").strip()
    if len(text) > MAX_PROMPT_CHARS:
        raise ValueError(f"prompt exceeds {MAX_PROMPT_CHARS} characters")
    return text


def _personas(names: list[str] | None) -> list:
    chosen = names or list(COUNCIL_DEFAULT)
    out = []
    seen = set()
    for name in chosen:
        p = get_persona(str(name))
        if p is None:
            raise ValueError(f"unknown persona: {name}")
        key = p.name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
        if len(out) >= COUNCIL_MAX:
            break
    if not out:
        raise ValueError("no personas selected")
    return out


@app.get("/health")
def health() -> dict[str, Any]:
    st = _backend.backend_status()
    return {
        "ok": True,
        "product": "Ayllu Counsel",
        "version": __version__,
        "backend": st,
        "lambda": "CONJECTURE_1",
        "organs": [o["id"] for o in anatomy()["organs"]],
        "origins": catalog()["origins"],
    }


@app.get("/", response_class=HTMLResponse)
def chamber() -> HTMLResponse:
    return HTMLResponse(CHAMBER.read_text(encoding="utf-8"))


@app.get("/ayllu", response_class=HTMLResponse)
def chamber_alias() -> HTMLResponse:
    return chamber()


@app.get("/api/v1/ayllu/roster")
def roster() -> dict[str, Any]:
    st = _backend.backend_status()
    return {
        "schema": "szl.ayllu.roster/v1",
        "version": __version__,
        "personas": [p.metadata() for p in ROSTER],
        "count": len(ROSTER),
        "backend": st,
        "honesty": (
            "Eleven roles on one routed backend. Not eleven separately trained models."
        ),
        "lambda": "CONJECTURE_1",
    }


@app.get("/api/v1/ayllu/manifest")
def manifest() -> dict[str, Any]:
    return {
        "schema": "szl.ayllu.council-manifest/v1",
        "contract_version": "2.0",
        "council_schema": SCHEMA_COUNCIL,
        "authority": "PROPOSAL_ONLY",
        "semantic_consensus": "NOT_MEASURED",
        "effectiveness": "NOT_MEASURED",
        "lambda": {"status": "CONJECTURE_1", "never_a_theorem": True, "role": "advisory"},
        "limits": {
            "max_prompt_chars": MAX_PROMPT_CHARS,
            "council_max": COUNCIL_MAX,
            "debate_max": COUNCIL_DEBATE_MAX,
            "debate_rounds": 2,
        },
        "default_seats": COUNCIL_DEFAULT,
        "receipts": "UNSIGNED-honest unless a signer is injected",
        "product_origin": "https://a-11-oy.com",
        "proof_origin": "https://a11oy.net",
        "github": "https://github.com/szl-holdings/ayllu",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/ayllu",
    }


@app.get("/api/v1/ayllu/estate")
def estate() -> dict[str, Any]:
    return catalog()


@app.get("/api/v1/ayllu/leaders")
def leaders() -> dict[str, Any]:
    cat = catalog()
    return {
        "schema": "szl.ayllu.leaders-studied/v1",
        "leaders_studied": cat["leaders_studied"],
        "honesty": cat["honesty"],
        "frontier": (
            "Dissent-first evidence-bound counsel with holographic 0-CDN presence, "
            "hash-chained UNSIGNED receipts, and Λ never a theorem."
        ),
    }


@app.get("/api/v1/ayllu/anatomy")
def anatomy_route() -> dict[str, Any]:
    return anatomy()


@app.get("/api/v1/ayllu/second-brain")
def second_brain_route() -> dict[str, Any]:
    return second_brain_binding(
        namespace="ayllu",
        backend_status=_backend.backend_status(),
        signer_ready=False,
    )


@app.get("/api/v1/ayllu/hatun")
def hatun_route() -> dict[str, Any]:
    return hatun_status()


@app.get("/api/v1/ayllu/lounge")
def lounge_feed() -> dict[str, Any]:
    return {
        "schema": "szl.ayllu.lounge/v1",
        "feed": _LOUNGE.recent(),
        "honesty": "Opt-in in-memory feed. Public ask/council do not auto-publish.",
    }


@app.post("/api/v1/ayllu/ask")
async def ask(request: Request) -> JSONResponse:
    ok, retry = _ASK_BUCKET.check()
    if not ok:
        return JSONResponse({"error": "rate limited", "retry_after": retry}, status_code=429)
    try:
        body = await _bounded_json_body(request)
        prompt = _clip_prompt(body.get("prompt") or body.get("q"))
        persona = get_persona(str(body.get("persona") or "Amaru"))
        if persona is None:
            raise ValueError("unknown persona")
        if not prompt:
            raise ValueError("prompt is required")
    except _BodyTooLarge as exc:
        return JSONResponse({"error": str(exc)}, status_code=413)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    difficulty = body.get("difficulty")
    turn = await run_turn(
        persona,
        prompt,
        model_complete=_backend.model_complete,
        difficulty=None if difficulty is None else float(difficulty),
    )
    payload = {
        "schema": "szl.ayllu.ask-receipt/v1",
        "id": str(uuid.uuid4()),
        "prompt_sha256": sha256_json(prompt),
        "turn": {
            "persona": turn.get("persona"),
            "answer": turn.get("answer"),
            "honesty": turn.get("honesty"),
            "model": turn.get("model"),
            "stub": turn.get("stub"),
        },
        "authority": "PROPOSAL_ONLY",
    }
    receipt = make_receipt(payload)
    return JSONResponse({
        "schema": "szl.ayllu.ask/v1",
        "turn": turn,
        "receipt": receipt,
        "honesty": turn.get("honesty"),
        "lambda": "CONJECTURE_1",
    })


@app.post("/api/v1/ayllu/council")
async def council(request: Request) -> JSONResponse:
    ok, retry = _COUNCIL_BUCKET.check()
    if not ok:
        return JSONResponse({"error": "rate limited", "retry_after": retry}, status_code=429)
    try:
        body = await _bounded_json_body(request)
        prompt = _clip_prompt(body.get("prompt") or body.get("q"))
        if not prompt:
            raise ValueError("prompt is required")
        names = body.get("personas") or body.get("seats")
        if names is not None and not isinstance(names, list):
            raise ValueError("personas must be a list of names")
        debate = bool(body.get("debate"))
        seats = _personas(names)
        if debate and len(seats) > COUNCIL_DEBATE_MAX:
            seats = seats[:COUNCIL_DEBATE_MAX]
    except _BodyTooLarge as exc:
        return JSONResponse({"error": str(exc)}, status_code=413)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    result = await _LOUNGE.deliberate(
        prompt,
        seats,
        model_complete=_backend.model_complete,
        debate=debate,
        publish_to_lounge=bool(body.get("publish_to_lounge")),
    )
    converge = synthesize(prompt, result["rounds"])
    chain = chain_turns(result["rounds"])
    for turn in result["rounds"]:
        organ = organ_for_persona(str(turn.get("persona") or ""))
        turn["organ"] = (organ or {}).get("id")
        turn["organ_name"] = (organ or {}).get("name")
    payload = {
        "schema": SCHEMA_COUNCIL,
        "id": str(uuid.uuid4()),
        "prompt_sha256": sha256_json(prompt),
        "participants": result["participants"],
        "mode": result["mode"],
        "converge": {
            "semantic_consensus": converge["semantic_consensus"],
            "effectiveness": converge["effectiveness"],
            "dissent_count": len(converge["lexical_dissent"]),
        },
        "chain_head": chain["head"],
        "authority": "PROPOSAL_ONLY",
        "state": "PROPOSAL_ONLY",
        "lambda": "CONJECTURE_1",
    }
    receipt = make_receipt(payload)
    loop = ouroboros_tax(result["mode"], len(result["rounds"]), chain["head"])
    inv = check_invariants(payload, receipt, chain)
    return JSONResponse({
        "schema": SCHEMA_COUNCIL,
        "prompt": prompt,
        "participants": result["participants"],
        "rounds": result["rounds"],
        "mode": result["mode"],
        "converge": converge,
        "chain": chain,
        "receipt": receipt,
        "ouroboros": loop,
        "invariants": inv,
        "anatomy": anatomy(),
        "honesty": result.get("note"),
        "lambda": "CONJECTURE_1",
    })


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots() -> str:
    return "User-agent: *\nAllow: /\n"


@app.get("/readyz")
def readyz() -> dict[str, Any]:
    return {"ready": True, "version": __version__, "lambda": "CONJECTURE_1"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", os.environ.get("AYLLU_PORT", "8099")))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
