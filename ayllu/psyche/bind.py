"""Load-bearing bind. Yuyariy and Kutiy change the next receipt.

Not dashboards. After a closed beat, Yuyariy observations prefix the
next cue. Kutiy residual is stamped from successive Wiñay snapshots
without calling beat() from inside beat() (no recursion).

AGI stays CONJECTURE. Presence stays CONJECTURE.
"""
from __future__ import annotations

from typing import Any

_INSTALLED = False


def _prefix(psyche: Any, cue: str) -> str:
    last = getattr(psyche, "last_yuyariy", None) or {}
    obs = last.get("observations") or []
    if not obs:
        return cue
    head = str(obs[0])[:180]
    if not cue:
        return head
    if head in cue:
        return cue
    return f"{head} | {cue}"


def stamp(psyche: Any, ran: dict[str, Any] | None = None) -> dict[str, Any]:
    """Attach Yuyariy + Kutiy residual to a beat receipt."""
    from ayllu.psyche.kutiy import _delta, _snapshot
    from ayllu.psyche.yuyariy import yuyariy

    body = yuyariy(psyche)
    psyche.last_yuyariy = body
    after = _snapshot(getattr(psyche, "last_winay", None) or {})
    before = getattr(psyche, "_kutiy_prev", None) or after
    gap = _delta(before, after)
    psyche._kutiy_prev = after
    gate = {
        "schema": "szl.ayllu.kutiy-gate/v1",
        "honesty": "MODELED",
        "delta": gap,
        "stable": gap < 1e-3,
        "consumed": True,
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "note": "Residual of successive closed beats. Not Huginn. Not extra couple_once.",
    }
    psyche.last_kutiy_gate = gate
    if isinstance(ran, dict):
        ran["yuyariy"] = {
            "count": body.get("count"),
            "honesty": "SOFTWARE",
            "consumed": True,
            "agi": "CONJECTURE",
        }
        ran["kutiy_gate"] = gate
        return ran
    return {"yuyariy": body, "kutiy_gate": gate}


def install(psyche: Any) -> None:
    """Wrap beat once so observations are load-bearing."""
    global _INSTALLED
    if _INSTALLED or getattr(psyche, "_bind_installed", False):
        return
    original = psyche.beat

    def beat(cue: str = "", seat: str = "Maskaq") -> dict[str, Any]:
        ran = original(_prefix(psyche, cue), seat=seat)
        return stamp(psyche, ran if isinstance(ran, dict) else {})

    psyche.beat = beat
    psyche._bind_installed = True
    _INSTALLED = True
