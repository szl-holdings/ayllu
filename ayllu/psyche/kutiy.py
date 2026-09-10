"""Kutiy — extra residual pulse depth.

Studied from the public recurrent-depth *idea* (Geiping et al.,
arXiv:2502.05171): iterate a block until successive states stop
moving. Original Ayllu code. No Huginn weights. Not Project Astra.
Not GPT-6 Astra. Not AGI.

Kutiy wraps already-closed Wiñay beats. It does not enter
couple_once. Presence stays CONJECTURE.
"""
from __future__ import annotations

from typing import Any

R_MAX = 4
EPS = 1e-3


def _num(win: dict[str, Any], *path: str) -> float | None:
    cur: Any = win
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    if isinstance(cur, dict):
        cur = cur.get("value", cur.get("score", cur.get("H")))
    try:
        return float(cur)
    except (TypeError, ValueError):
        return None


def _snapshot(win: dict[str, Any]) -> dict[str, float | None]:
    return {
        "H": _num(win, "huklla", "H") or _num(win, "H") or _num(win, "huklla"),
        "Q": _num(win, "qhaway", "Q") or _num(win, "Q") or _num(win, "qhaway"),
        "Y": _num(win, "riqsiy", "Y") or _num(win, "riqsiy", "upsilon") or _num(win, "Y"),
    }


def _delta(a: dict[str, float | None], b: dict[str, float | None]) -> float:
    gaps: list[float] = []
    for key in ("H", "Q", "Y"):
        left, right = a.get(key), b.get(key)
        if left is None or right is None:
            continue
        gaps.append(abs(left - right))
    return max(gaps) if gaps else 0.0


def kutiy(psyche: Any, r_max: int = R_MAX, eps: float = EPS) -> dict[str, Any]:
    """Run extra closed beats. Halt when scalars stop moving or r_max."""
    steps = 0
    halted = "empty"
    before = _snapshot(getattr(psyche, "last_winay", None) or {})
    after = dict(before)
    if int(getattr(psyche, "pulses", 0) or 0) < 1:
        return {
            "schema": "szl.ayllu.kutiy/v1",
            "name": "Kutiy",
            "honesty": "UNAVAILABLE",
            "steps": 0,
            "halt": "no-occupancy",
            "delta": None,
            "r_max": r_max,
            "eps": eps,
            "agi": "CONJECTURE",
            "presence": "CONJECTURE",
            "studied": "Geiping et al. arXiv:2502.05171 recurrent-depth idea",
            "copied": False,
            "note": "No closed beat yet. Kutiy does not invent occupancy.",
        }
    prev = before
    limit = max(1, min(int(r_max), 8))
    for i in range(limit):
        psyche.beat(f"kutiy residual {i + 1}", seat="Qhaway")
        steps += 1
        after = _snapshot(getattr(psyche, "last_winay", None) or {})
        gap = _delta(prev, after)
        if gap < eps:
            halted = "converged"
            break
        prev = after
        halted = "r_max"
    gap = _delta(before, after)
    return {
        "schema": "szl.ayllu.kutiy/v1",
        "name": "Kutiy",
        "honesty": "MODELED",
        "steps": steps,
        "halt": halted,
        "delta": gap,
        "before": before,
        "after": after,
        "r_max": limit,
        "eps": eps,
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "studied": "Geiping et al. arXiv:2502.05171 recurrent-depth idea",
        "copied": False,
        "note": "Extra closed Wiñay beats. MODELED compute. Not Huginn. Not a mind.",
    }
