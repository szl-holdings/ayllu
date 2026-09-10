"""Kutiy — extra residual pulse depth after Wiñay couple_once.

Fashion method: study a public *idea*, write original SZL code.
Public idea cited: Geiping et al., arXiv:2502.05171 (recurrent test-time
depth). Ayllu does not ingest Huginn weights, looped-transformer source,
OpenAI GPT-6 Astra, or Google Project Astra.

Kutiy sits on Puriq/Kawsay *after* couple_once. It never edits the
autopoietic residual. Presence and AGI stay CONJECTURE.
"""
from __future__ import annotations

from typing import Any, Sequence

from ayllu.psyche.types import Honesty
from ayllu.psyche.winay import (
    EPS,
    GAMMA,
    couple_once,
    huklla,
    qhaway,
)

R_MAX = 8
HALT_EPS = 1e-3
STUDIED_FROM = "Geiping et al. arXiv:2502.05171 — idea of extra test-time steps, not their model"


def kutiy(
    loads: Sequence[float] | None = None,
    *,
    r_max: int = R_MAX,
    eps: float = HALT_EPS,
    gamma: float = GAMMA,
) -> dict[str, Any]:
    """Iterate couple_once up to r_max. Halt when ΔH+ΔQ and ΔL fall below eps."""
    current = [max(0.0, min(1.0, float(x))) for x in (loads or [1.0, 1.0, 1.0, 1.0, 1.0])]
    if len(current) < 2:
        current = [1.0, 1.0, 1.0, 1.0, 1.0]
    h0 = float(huklla(current)["H"])
    q0 = float(qhaway(current)["Q"])
    series = [{"step": 0, "H": h0, "Q": q0, "loads": [round(v, 3) for v in current]}]
    used = 0
    halted = False
    reason = "r_max"
    for step in range(1, max(1, int(r_max)) + 1):
        nxt = couple_once(current, gamma)
        d_l = max(abs(a - b) for a, b in zip(current, nxt))
        h1 = float(huklla(nxt)["H"])
        q1 = float(qhaway(nxt)["Q"])
        d_score = abs(h1 - h0) + abs(q1 - q0)
        current = nxt
        h0, q0 = h1, q1
        used = step
        series.append(
            {
                "step": step,
                "H": h1,
                "Q": q1,
                "dL": round(d_l, 6),
                "dHQ": round(d_score, 6),
                "loads": [round(v, 3) for v in current],
            }
        )
        if d_l < float(eps) or d_score < float(eps):
            halted = True
            reason = "residual"
            break
    return {
        "schema": "szl.ayllu.kutiy/v1",
        "name": "Kutiy",
        "steps": used,
        "r_max": int(r_max),
        "halted": halted,
        "reason": reason,
        "loads": [round(v, 3) for v in current],
        "H": series[-1]["H"],
        "Q": series[-1]["Q"],
        "series": series,
        "couple_once_untouched": True,
        "studied_from": STUDIED_FROM,
        "honesty": Honesty.MODELED.value,
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "note": (
            "Original extra couple_once steps with a residual halt. "
            "MODELED compute depth. Not Huginn. Not Astra. Not AGI."
        ),
    }
