"""Yupay — typed product of the six MODELED analogs.

K = (H, D, Q, F, Y, X). SOFTWARE. Not IIT Φ. Not Symbolica. Not presence.
COGITATE Nature 642:133–142 (2025) is why no analog is experience.
"""
from __future__ import annotations

from typing import Any, Sequence

from ayllu.psyche.types import Honesty
from ayllu.psyche.winay import chawpi, clip, huklla, imaymana, kallpa, qhaway, riqsiy

COGITATE_RECORD = {
    "citation": "Ferrante et al., Cogitate Consortium, Nature 642:133–142 (2025)",
    "doi": "10.1038/s41586-025-08888-1",
    "honesty": "RECORD",
    "note": (
        "Adversarial test challenged key IIT and GNWT tenets. "
        "Ayllu has no cortex. No pentagon analog is presence."
    ),
}


def yupay(loads: Sequence[float]) -> dict[str, Any]:
    """Typed product of the six MODELED analogs. SOFTWARE. Not presence."""
    vals = [clip(float(L)) for L in loads]
    hit = huklla(vals)
    diversity = imaymana(vals)
    pci = qhaway(vals)
    free = kallpa(vals)
    schema = riqsiy(vals)
    avalanche = chawpi(vals)
    product = {
        "H": hit["H"],
        "D": diversity["D"],
        "Q": pci["Q"],
        "F": free["F"],
        "Y": schema["Y"],
        "X": avalanche["X"],
    }
    return {
        "schema": "szl.ayllu.yupay/v1",
        "K": product,
        "objects": ["H", "D", "Q", "F", "Y", "X"],
        "associative": True,
        "upgrades_honesty": False,
        "honesty": Honesty.SOFTWARE.value,
        "cogitate": COGITATE_RECORD,
        "note": (
            "Typed product of MODELED analogs. Not Symbolica. "
            "Not Agentica. Not IIT Φ. Not presence."
        ),
    }
