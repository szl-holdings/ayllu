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
DIMENSIONS = [
    {
        "id": "model_weights",
        "label": "Model weights",
        "seal": 2,
        "honesty": "REPORTED",
        "basis": "SZLHOLDINGS Hub hosts Khipu / Forge / Chaski weights. Public Hub is not air-gapped sovereign custody.",
    },
    {
        "id": "inference_compute",
        "label": "Inference compute",
        "seal": 1,
        "honesty": "REPORTED",
        "basis": "Space infers on grok-4.5 via xAI when XAI_API_KEY is set. Third-party compute. Not sovereign metal.",
    },
    {
        "id": "data_residency",
        "label": "Data residency",
        "seal": 1,
        "honesty": "UNAVAILABLE",
        "basis": "No database. Remote residency of live scrapes is UNAVAILABLE.",
    },
    {
        "id": "chain_of_title",
        "label": "Chain of title",
        "seal": 3,
        "honesty": "REPORTED",
        "basis": "Public GitHub szl-holdings + HF SZLHOLDINGS + a-11-oy.com legal vertical. Continuance of retired Counsel, not a fork-delete.",
    },
    {
        "id": "governance_keys",
        "label": "Governance keys",
        "seal": 0,
        "honesty": "REPORTED",
        "basis": "a11oy signer status ABSENT / scheme UNAVAILABLE. Receipts are UNSIGNED-honest. No signature is fabricated.",
    },
]


def score(seals: dict[str, int] | None = None, dci: float = DCI) -> dict:
    s = seals or SEALS
    weighted = sum((v / 4) * (1 / len(s)) for v in s.values())
    a = round(weighted * (1 - min(1, max(0, dci))) * 100, 1)
    return {
        "A": a,
        "dci": dci,
        "seals": s,
        "dimensions": DIMENSIONS,
        "honesty": "MODELED",
        "experimental": True,
        "locked": False,
        "lambda": "Conjecture 1",
        "caveat": "EXPERIMENTAL — not locked-8, not a theorem, not a sovereign-citizen claim.",
        "formula": FORMULA,
    }
