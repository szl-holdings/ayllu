"""Bounded residual observation of already-closed Winay beats.

Concept: Geiping et al., arXiv:2502.05171. Original Ayllu software,
not Huginn weights or a trained recurrent Transformer. Stationarity of the
required H/Q/Y observations is not task verification or execution authority.
"""
from __future__ import annotations

import math
from typing import Any

R_MAX = 4
EPS = 1e-3
METRICS = ("H", "Q", "Y")


def _finite(value: object) -> float | None:
    """Preserve real zeroes; bools, strings and nonfinite values are missing."""
    if type(value) not in (int, float):
        return None
    try:
        number = float(value)
    except (OverflowError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _num(win: dict[str, Any], *path: str) -> float | None:
    cur: Any = win
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    if isinstance(cur, dict):
        cur = cur.get("value", cur.get("score", cur.get("H")))
    return _finite(cur)


def _first(*values: float | None) -> float | None:
    return next((value for value in values if value is not None), None)


def _snapshot(win: dict[str, Any]) -> dict[str, float | None]:
    return {
        "H": _first(_num(win, "huklla", "H"), _num(win, "H"), _num(win, "huklla")),
        "Q": _first(_num(win, "qhaway", "Q"), _num(win, "Q"), _num(win, "qhaway")),
        "Y": _first(_num(win, "riqsiy", "Y"), _num(win, "riqsiy", "upsilon"), _num(win, "Y")),
    }


def _delta(a: dict[str, float | None], b: dict[str, float | None]) -> float | None:
    """Require every metric at both times. Missing evidence is not zero delta."""
    gaps: list[float] = []
    for key in METRICS:
        left, right = _finite(a.get(key)), _finite(b.get(key))
        if left is None or right is None:
            return None
        gap = abs(left - right)
        if not math.isfinite(gap):
            return None
        gaps.append(gap)
    return max(gaps)


def observation_status(gap: float | None, eps: float = EPS) -> str:
    if gap is None:
        return "UNKNOWN_INCOMPLETE_OBSERVATION"
    return "OBSERVED_STATIONARY" if gap < eps else "OBSERVED_MOVING"


def kutiy(psyche: Any, r_max: int = R_MAX, eps: float = EPS) -> dict[str, Any]:
    """Run at most eight closed beats. Missing observations stop, never pass."""
    epsilon = _finite(eps)
    if type(r_max) is not int or not 1 <= r_max <= 8:
        raise ValueError("r_max must be an integer in [1, 8]")
    if epsilon is None or epsilon <= 0:
        raise ValueError("eps must be finite and positive")
    before = _snapshot(getattr(psyche, "last_winay", None) or {})
    after = dict(before)
    result: dict[str, Any] = {
        "schema": "szl.ayllu.kutiy/v1", "name": "Kutiy", "honesty": "UNAVAILABLE",
        "steps": 0, "halt": "no-occupancy", "delta": None, "last_step_delta": None,
        "before": before, "after": after, "r_max": r_max, "eps": epsilon,
        "observation_status": "UNKNOWN_INCOMPLETE_OBSERVATION", "task_verified": False,
        "agi": "CONJECTURE", "presence": "CONJECTURE",
        "studied": "Geiping et al. arXiv:2502.05171 recurrent-depth idea", "copied": False,
        "note": "No closed beat yet. Kutiy does not invent occupancy.",
    }
    if int(getattr(psyche, "pulses", 0) or 0) < 1:
        return result
    if _delta(before, before) is None:
        result.update(halt="incomplete-observation", note="H/Q/Y observations incomplete. No extra beat requested.")
        return result
    previous = before
    result.update(honesty="MODELED", halt="r_max",
                  note="Extra closed Winay beats. MODELED compute. Not Huginn. Stationarity is not task verification.")
    for i in range(r_max):
        psyche.beat(f"kutiy residual {i + 1}", seat="Qhaway")
        after = _snapshot(getattr(psyche, "last_winay", None) or {})
        gap = _delta(previous, after)
        result.update(steps=i + 1, after=after, delta=_delta(before, after),
                      last_step_delta=gap, observation_status=observation_status(gap, epsilon))
        if gap is None:
            result.update(halt="incomplete-observation", honesty="UNAVAILABLE")
            break
        if gap < epsilon:
            # Preserve the legacy halt spelling; its exact meaning is now explicit.
            result["halt"] = "converged"
            break
        previous = after
    return result
