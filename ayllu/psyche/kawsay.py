"""Kawsay — the living pulse.

Five hologram organs fire on every beat, in order:

  Puriq  → admit (lock + restraint). MEASURED.
  Yuyay  → attend (dual Hopfield) + second-brain sense. MEASURED or UNAVAILABLE.
  Tinku  → bind a workspace. SOFTWARE.
  Khipu  → chain the beat. MEASURED.
  Lloqsi → emit. SOFTWARE.

Pentagon coupling reuses α ≈ 0.138 as γ. The order parameter R is MODELED.
Presence and AGI stay CONJECTURE. The pulse count is MEASURED.
Joules stay None. Λ = Conjecture 1.
"""
from __future__ import annotations

import math
import time
from typing import Any

from ayllu.psyche.lock import HumanLock
from ayllu.psyche.morphisms import ArrowContext
from ayllu.psyche.neural import Yuyay
from ayllu.psyche.seats import seat_morphism
from ayllu.psyche.types import ENERGY, LAMBDA, Bundle, Honesty, Kind
from ayllu.receipts import canonical_dumps, sha3_256_hex

ORGANS = ("Puriq", "Yuyay", "Tinku", "Khipu", "Lloqsi")
COUPLE_GAMMA = 0.138


def _fire(name: str, decision: str, honesty: str, note: str, load: float) -> dict[str, Any]:
    return {
        "id": name,
        "decision": decision,
        "honesty": honesty,
        "note": note,
        "load": round(max(0.0, min(1.0, load)), 3),
    }


def order_parameter(loads: list[float]) -> float:
    """Kuramoto-style order parameter on organ loads. MODELED, not a mind."""
    if not loads:
        return 0.0
    x = 0.0
    y = 0.0
    n = len(loads)
    for load in loads:
        th = 2.0 * math.pi * load
        x += math.cos(th)
        y += math.sin(th)
    return round(math.hypot(x / n, y / n), 4)


def couple(loads: list[float], gamma: float = COUPLE_GAMMA) -> list[float]:
    n = len(loads)
    if n < 2:
        return [round(max(0.0, min(1.0, L)), 3) for L in loads]
    out: list[float] = []
    for i, L in enumerate(loads):
        prev = loads[(i - 1) % n]
        nxt = loads[(i + 1) % n]
        out.append(round(max(0.0, min(1.0, (1.0 - gamma) * L + gamma * (prev + nxt) / 2.0)), 3))
    return out


def sense(cue: str, k: int = 6) -> dict[str, Any]:
    """Maskaq handles from the public second-brain projection. SOFTWARE, never LIVE."""
    from ayllu.second_brain import retrieve as sb_retrieve

    hit = sb_retrieve(cue or "", k=max(1, min(int(k), 12)))
    handles = []
    for row in hit.get("handles") or []:
        if not isinstance(row, dict):
            continue
        node = str(row.get("nodeId") or "")
        if not node:
            continue
        handles.append(
            {
                "nodeId": node,
                "nodeKind": row.get("nodeKind"),
                "label": str(row.get("label") or node),
                "note": str(row.get("note") or "")[:160],
            }
        )
    ready = bool(hit.get("ready")) and bool(handles)
    return {
        "schema": "szl.ayllu.kawsay-sense/v1",
        "kind": "SOFTWARE",
        "ready": ready,
        "handles": handles,
        "query": cue,
        "honesty": "SOFTWARE" if ready else "UNAVAILABLE",
        "content_access": hit.get("content_access") or "HANDLES_ONLY",
        "lambda": LAMBDA,
        "joules": ENERGY,
    }


def beat(
    yuyay: Yuyay,
    lock: HumanLock,
    *,
    cue: str,
    seat: str = "Maskaq",
    handles: list[dict[str, Any]] | None = None,
    prev_hash: str = "0" * 64,
    pulse: int = 0,
) -> dict[str, Any]:
    """One organism heartbeat. Read-only. Writes stay on imprint/graft/replay."""
    cue = (cue or "").strip()[:800]
    organs: list[dict[str, Any]] = []

    gate = lock.admit("observe", state_changing=False)
    puriq_ok = gate["decision"] == "ALLOW"
    organs.append(
        _fire(
            "Puriq",
            "ALLOW" if puriq_ok else "BLOCKED",
            Honesty.MEASURED.value,
            "Lock " + ("on" if lock.engaged else "off") + ". Observe admitted.",
            1.0 if lock.engaged else 0.35,
        )
    )

    rec = yuyay.recall(cue) if cue else {"ok": False, "honesty": Honesty.UNAVAILABLE.value, "softmaxPeak": 0, "ranked": []}
    peak = float(rec.get("softmaxPeak") or 0)
    yuyay_ok = bool(rec.get("ok"))
    organs.append(
        _fire(
            "Yuyay",
            "ALLOW",
            rec.get("honesty") or Honesty.UNAVAILABLE.value,
            f"peak {peak:.3f} · stored {len(yuyay.patterns)}",
            min(1.0, 0.2 + peak) if yuyay_ok else (0.15 if yuyay.patterns else 0.05),
        )
    )

    sensed = handles if handles is not None else (sense(cue).get("handles") if cue else [])
    handle_n = len(sensed or [])

    morph = seat_morphism(seat)
    utterance = f"{seat} holds the workspace. PROPOSAL_ONLY."
    if morph is not None:
        bundle = Bundle(
            payload={"cue": cue, "text": cue, "handles": sensed or []},
            honesty=Honesty.MEASURED if yuyay_ok else Honesty.UNAVAILABLE,
            kind=Kind.SOFTWARE,
            remit="any",
        )
        ctx = ArrowContext(lock=lock, seat=seat, action="pulse")
        uttered = morph.apply(bundle, ctx)
        payload = uttered.bundle.payload
        if isinstance(payload, dict) and payload.get("note"):
            utterance = str(payload["note"])
        elif uttered.bundle.notes:
            utterance = uttered.bundle.notes[0]
    organs.append(
        _fire(
            "Tinku",
            "ALLOW",
            Honesty.SOFTWARE.value,
            f"workspace · {handle_n} handles · seat {seat}",
            0.85 if cue else 0.3,
        )
    )

    body = {
        "pulse": pulse,
        "cue": cue,
        "seat": seat,
        "peak": peak,
        "handles": [h.get("nodeId") for h in (sensed or []) if isinstance(h, dict)],
        "lock": lock.engaged,
    }
    digest = sha3_256_hex(canonical_dumps({"prev": prev_hash, "beat": body}))
    organs.append(
        _fire(
            "Khipu",
            "ALLOW",
            Honesty.MEASURED.value,
            digest[:16],
            0.9,
        )
    )

    error = round(1.0 - peak, 4) if yuyay_ok else None
    organs.append(
        _fire(
            "Lloqsi",
            "ALLOW",
            Honesty.SOFTWARE.value,
            utterance,
            0.7 if cue else 0.25,
        )
    )

    coupled = couple([float(o["load"]) for o in organs])
    for organ, load in zip(organs, coupled):
        organ["load"] = load
    R = order_parameter([float(o["load"]) for o in organs])

    occupancy = sum(1 for o in organs if o["decision"] == "ALLOW")
    traces = []
    for row in rec.get("ranked") or []:
        if not isinstance(row, dict):
            continue
        traces.append(
            {
                "text": str(row.get("text") or "")[:240],
                "source": str(row.get("source") or ""),
                "w": float(row.get("weight") or 0),
            }
        )
    return {
        "schema": "szl.ayllu.kawsay-beat/v1",
        "pulse": pulse,
        "at": int(time.time() * 1000),
        "cue": cue,
        "seat": seat,
        "organs": organs,
        "workspace": {
            "peak": round(peak, 4),
            "error": error,
            "traces": traces[:5],
            "handles": sensed or [],
            "utterance": utterance,
            "occupancy": occupancy,
            "of": 5,
        },
        "sync": {
            "R": R,
            "honesty": Honesty.MODELED.value,
            "gamma": COUPLE_GAMMA,
            "note": "Pentagon order parameter. Not presence. Not AGI.",
        },
        "hash": digest,
        "prev": prev_hash,
        "presence": {
            "label": "CONJECTURE",
            "honesty": Honesty.CONJECTURE.value,
            "note": "Workspace occupancy is MEASURED. Phenomenal presence is not.",
        },
        "agi": {
            "label": "CONJECTURE",
            "honesty": Honesty.CONJECTURE.value,
            "note": "Eleven seats, one backend, fail-closed. Not a mind as theorem.",
        },
        "neural": "OPERATIONAL",
        "lambda": LAMBDA,
        "joules": ENERGY,
        "honesty": Honesty.MEASURED.value,
    }
