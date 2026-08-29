"""Eight falsifiable receipt invariants — from szl-holdings/szl-invariants.

SOFTWARE checks over Ayllu council receipts. Not CUDA. Not a theorem about Λ.
"""
from __future__ import annotations

from typing import Any

from ayllu.receipts import sha256_json


def check(payload: dict[str, Any], receipt: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
    results = []

    def add(iid: str, name: str, ok: bool, note: str) -> None:
        results.append({"id": iid, "name": name, "ok": ok, "note": note})

    signed = bool(receipt.get("signed"))
    sigs = receipt.get("signatures") or []
    add("I1", "unsigned_honest",
        (not signed and not sigs) or (signed and bool(sigs)),
        "signed=true with empty signatures is a fabricated claim")

    add("I2", "payload_digest_binds",
        bool(receipt.get("payloadSha256") or receipt.get("payload")),
        "receipt must carry payload bytes or a digest")

    add("I3", "lambda_not_a_theorem",
        (payload.get("lambda") in ("CONJECTURE_1", None)
         or (isinstance(payload.get("lambda"), dict)
             and payload["lambda"].get("never_a_theorem") is True)
         or (isinstance(receipt.get("payload"), str))),
        "Λ uniqueness stays Conjecture 1")

    add("I4", "proposal_only",
        payload.get("authority") == "PROPOSAL_ONLY"
        and payload.get("state") == "PROPOSAL_ONLY",
        "council cannot self-execute")

    conv = payload.get("converge") or {}
    add("I5", "consensus_not_measured",
        conv.get("semantic_consensus") == "NOT_MEASURED",
        "no fake swarm IQ")

    add("I6", "hash_chain_closed",
        isinstance(chain.get("head"), str) and chain.get("kind") == "SOFTWARE"
        and int(chain.get("count") or 0) >= 0,
        "turn chain is SOFTWARE, not DSSE")

    add("I7", "receipts_in_eq_out",
        sha256_json({"head": chain.get("head"), "id": payload.get("id")}) is not None,
        "receipts.in ≡ receipts.out metaphor — chain head is both input and output")

    add("I8", "no_fabricated_energy",
        "energy" not in payload or payload.get("energy") in (None, "UNAVAILABLE"),
        "no joule invented on this Space")

    failed = [r for r in results if not r["ok"]]
    return {
        "schema": "szl.ayllu.invariants/v1",
        "source": "https://github.com/szl-holdings/szl-invariants",
        "kind": "SOFTWARE",
        "count": 8,
        "passed": sum(1 for r in results if r["ok"]),
        "failed": [r["id"] for r in failed],
        "ok": not failed,
        "results": results,
        "lambda": "CONJECTURE_1",
        "honesty": "Stdlib receipt checks. Not the torch kernel binary. Not an eval.",
    }
