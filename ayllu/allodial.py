"""Experimental Allodial composite. Not locked-8. Not a land patent.

Pushed as a frontier onto Ayllu Counsel without replacing the eleven seats.
"""

FORMULA = "A = [sum w_k * SEAL_k / 4] * (1 - DCI) * 100"
DCI = 0.41
SEALS = {
    "model_weights": 2,
    "inference_compute": 1,
    "data_residency": 1,
    "chain_of_title": 3,
    "governance_keys": 0,
}


def score(seals: dict[str, int] | None = None, dci: float = DCI) -> dict:
    s = seals or SEALS
    weighted = sum((v / 4) * (1 / len(s)) for v in s.values())
    a = round(weighted * (1 - min(1, max(0, dci))) * 100, 1)
    return {
        "A": a,
        "dci": dci,
        "seals": s,
        "honesty": "MODELED",
        "experimental": True,
        "locked": False,
        "lambda": "Conjecture 1",
        "caveat": "EXPERIMENTAL — not locked-8, not a theorem, not a sovereign-citizen claim.",
        "formula": FORMULA,
    }
