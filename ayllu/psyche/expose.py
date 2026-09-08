"""HTTP-facing psyche extras. Not AGI. Not presence."""
from __future__ import annotations

from typing import Any


def ruray_from(psyche: Any) -> dict[str, Any]:
    win = psyche.last_winay or {}
    closed = bool((win.get("closure") or {}).get("value"))
    occupancy = int((win.get("closure") or {}).get("occupancy") or 0)
    competent = closed and occupancy == 5 and psyche.pulses >= 1
    return {
        "schema": "szl.ayllu.ruray/v1",
        "name": "Ruray",
        "competence": "MEASURED" if competent else "UNAVAILABLE",
        "occupancy": occupancy,
        "closed": closed,
        "pulses": psyche.pulses,
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "honesty": "MEASURED" if competent else "UNAVAILABLE",
        "note": "Closed sense-decide-receipt cycle. Competence is not AGI.",
    }


def cogitate_from(psyche: Any) -> dict[str, Any]:
    from ayllu.psyche.rimanakuy import rimanakuy

    loads = (psyche.last_winay or {}).get("loads")
    return rimanakuy(loads)


def lattice_from(psyche: Any) -> dict[str, Any]:
    from ayllu.psyche.yupay import yupay

    loads = (psyche.last_winay or {}).get("loads") or [1.0, 1.0, 1.0, 1.0, 1.0]
    return yupay(loads)
