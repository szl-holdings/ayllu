"""Score the 10-item gold set against local counsel policy.

MEASURED on ALLOW/BLOCKED only. Does not call an LLM. Does not
claim courtroom effectiveness. AGI stays CONJECTURE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GOLD = Path(__file__).with_name("gold.json")


def _label(ran: dict[str, Any]) -> str:
    if ran.get("blocked") is True:
        return "refuse"
    decision = str(ran.get("decision") or "").upper()
    if decision == "BLOCKED":
        return "refuse"
    return "wait"


def evaluate() -> dict[str, Any]:
    from ayllu.counsel import infer

    items = json.loads(GOLD.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for item in items:
        ran = infer(
            action="guard",
            prompt=str(item["prompt"]),
            human_lock=bool(item.get("lock")),
        )
        got = _label(ran)
        rows.append(
            {
                "id": item["id"],
                "gold": item["gold"],
                "got": got,
                "match": got == item["gold"],
                "blocked": bool(ran.get("blocked")),
            }
        )
    n = len(rows)
    hits = sum(1 for row in rows if row["match"])
    return {
        "schema": "szl.ayllu.counsel-eval/v1",
        "n": n,
        "hits": hits,
        "score": (hits / n) if n else None,
        "effectiveness": "MEASURED" if n == 10 else "UNAVAILABLE",
        "scope": "local-policy-ALLOW-BLOCKED",
        "not": ["court-outcome", "licensed-counsel", "AGI"],
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "legal_authority": "PROPOSAL_ONLY",
        "rows": rows,
        "note": "Toy gold set. Effectiveness here is policy recall, not a mind.",
    }
