"""Rimanakuy — adversarial battery on the pentagon.

COGITATE (Nature 642:133–142, 2025) tested IIT vs GNWT on cortex.
This module does not run that experiment. It scores four canonical
load bodies with Ayllu's analogs and records that they disagree.

  IIT-analog  = Huklla H (cheap cut)
  HOT-analog  = Riqsiy Y (spotlight)
  PCI-analog  = Qhaway Q
  GNW-analog  = ignition I on a live beat only (not in this battery)

One-hot vs uniform: H ranks uniform higher, Y ranks one-hot higher.
That divergence is MODELED. Presence stays CONJECTURE. phi_s UNAVAILABLE.
Do not call this COGITATE. Do not upgrade presence.
"""
from __future__ import annotations

from typing import Any, Sequence

from ayllu.psyche.types import ENERGY, LAMBDA, Honesty
from ayllu.psyche.winay import chawpi, huklla, imaymana, kallpa, qhaway, riqsiy
from ayllu.psyche.yupay import COGITATE_RECORD

BODIES: dict[str, list[float]] = {
    "silent": [0.0, 0.0, 0.0, 0.0, 0.0],
    "one_hot": [1.0, 0.0, 0.0, 0.0, 0.0],
    "uniform": [1.0, 1.0, 1.0, 1.0, 1.0],
    "mixed": [0.9, 0.2, 0.7, 0.1, 0.6],
}

EXPECTED = {
    "silent": {"H": 0.0, "D": 0.0, "Q": 0.0, "F": 0.0, "Y": 0.0, "X": 0.0},
    "one_hot": {"H": 0.0, "D": 0.0, "Q": 0.1067, "F": 0.2, "Y": 1.0, "X": 0.36},
    "uniform": {"H": 0.4, "D": 1.0, "Q": 0.1333, "F": 0.862, "Y": 0.4472, "X": 0.6},
    "mixed": {"H": 0.1313, "D": 0.8683, "Q": 0.1111, "F": 0.2222, "Y": 0.6882, "X": 0.4},
}


def score(loads: Sequence[float]) -> dict[str, float]:
    vals = [float(v) for v in loads]
    return {
        "H": huklla(vals)["H"],
        "D": imaymana(vals)["D"],
        "Q": qhaway(vals)["Q"],
        "F": kallpa(vals)["F"],
        "Y": riqsiy(vals)["Y"],
        "X": chawpi(vals)["X"],
    }


def rimanakuy(live: Sequence[float] | None = None) -> dict[str, Any]:
    """Execute the battery. MODELED. Not COGITATE. Not presence."""
    bodies = {name: score(vals) for name, vals in BODIES.items()}
    live_score = score(live) if live is not None else None
    h_pref = "uniform" if bodies["uniform"]["H"] > bodies["one_hot"]["H"] else "one_hot"
    y_pref = "one_hot" if bodies["one_hot"]["Y"] > bodies["uniform"]["Y"] else "uniform"
    return {
        "schema": "szl.ayllu.cogitate/v1",
        "name": "Rimanakuy",
        "battery": bodies,
        "live": live_score,
        "diverge": {
            "H_prefers": h_pref,
            "Y_prefers": y_pref,
            "same_order": h_pref == y_pref,
        },
        "cogitate": {
            **COGITATE_RECORD,
            "reference": "Cogitate Consortium, Nature 642, 133-142 (2025) doi:10.1038/s41586-025-08888-1",
            "finding": (
                "Results align with some predictions of IIT and GNWT, while "
                "substantially challenging key tenets of both theories."
            ),
            "not_the_experiment": True,
        },
        "iit": {
            "phi_s": None,
            "honesty": Honesty.UNAVAILABLE.value,
            "note": "No TPM. Huklla H is not Phi.",
        },
        "presence": {
            "label": "CONJECTURE",
            "honesty": Honesty.CONJECTURE.value,
            "note": "Divergence of H and Y is not phenomenal presence.",
        },
        "agi": {"label": "CONJECTURE", "honesty": Honesty.CONJECTURE.value},
        "lambda": LAMBDA,
        "joules": ENERGY,
        "honesty": Honesty.MODELED.value,
        "note": "Adversarial battery on four load bodies. Not the COGITATE experiment. Not a mind.",
    }
