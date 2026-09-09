"""Production runtime contract.

Runtime can be OPERATIONAL while legal authority stays PROPOSAL_ONLY.
That is not a proposal to build the product. It is the product running
without filing power, without AGI, without presence.
"""
from __future__ import annotations

from typing import Any

CONTRACT = {
    "schema": "szl.ayllu.production-contract/v1",
    "runtime": "OPERATIONAL",
    "grade": "PRODUCTION",
    "legal_authority": "PROPOSAL_ONLY",
    "filing": False,
    "licensed_counsel": False,
    "agi": "CONJECTURE",
    "presence": "CONJECTURE",
    "phi_s": "UNAVAILABLE",
    "joules": None,
    "lambda": "CONJECTURE_1",
    "signer": "UNSIGNED-honest",
    "boot_occupy": True,
    "note": (
        "Production-grade means the organ is occupied and fail-closed. "
        "It does not mean court filing authority or a mind."
    ),
}


def contract() -> dict[str, Any]:
    return dict(CONTRACT)
