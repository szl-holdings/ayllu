"""Production command cycle for Legal Matter Command.

Pulls live Federal Register + Hub estate, writes a SOFTWARE brief,
mints an UNSIGNED-honest receipt. legal_authority stays PROPOSAL_ONLY.
AGI stays CONJECTURE. Presence stays CONJECTURE. Not a filing.
"""
from __future__ import annotations

from typing import Any

from ayllu.allodial import score as allodial_score
from ayllu.counsel import (
    DISCLAIMER,
    GENESIS,
    evaluate_policy,
    hub_estate,
    legal_docket,
    mint_counsel_receipt,
)


def command_cycle(
    *,
    prompt: str = "",
    human_lock: bool = False,
    prev_hash: str = GENESIS,
) -> dict[str, Any]:
    text = (prompt or "").strip()
    policy = evaluate_policy(text or "command cycle over live docket", "docket-brief", bool(human_lock))
    docket = legal_docket(8)
    estate = hub_estate()
    allo = allodial_score()
    federal = [row for row in (docket.get("federal") or []) if isinstance(row, dict)][:6]
    courts = [row for row in (docket.get("courts") or []) if isinstance(row, dict)][:4]
    models = estate.get("models") if isinstance(estate.get("models"), list) else []
    spaces = estate.get("spaces") if isinstance(estate.get("spaces"), list) else []
    datasets = estate.get("datasets") if isinstance(estate.get("datasets"), list) else []

    lines = [
        "Ayllu Counsel command cycle — SOFTWARE, grounded in live feeds.",
        "legal_authority = PROPOSAL_ONLY. Not a filing. Not legal advice.",
        "AGI = CONJECTURE. Presence = CONJECTURE. Signer = UNSIGNED-honest.",
        DISCLAIMER,
        "",
        f"Matter: {text or '(no prompt — brief the live docket)'}",
        f"Human Lock: {bool(human_lock)}",
        f"Policy: {policy.get('decision')} — {'; '.join(policy.get('reasons') or []) or 'ALLOW local command'}",
        "",
        f"Federal Register count={docket.get('federal_count')} live={docket.get('live')} honesty={docket.get('honesty_tier')}",
    ]
    for row in federal:
        lines.append(
            f"- FR {row.get('date') or ''} · {row.get('agency') or ''} · {row.get('title') or '(untitled)'}"
        )
    lines.append(f"CourtListener count={docket.get('court_count')}")
    for row in courts:
        title = row.get("title") or row.get("caseName") or row.get("name") or "(untitled)"
        lines.append(f"- CT {row.get('date') or row.get('dateFiled') or ''} · {title}")
    lines.append(
        f"Hub estate models={len(models)} spaces={len(spaces)} datasets={len(datasets)} honesty={estate.get('honesty_tier')}"
    )
    lines.append(
        f"Allodial A={allo.get('A')} dci={allo.get('dci')} honesty={allo.get('honesty')} experimental={allo.get('experimental')}"
    )
    lines.append("")
    lines.append(
        "Recommendation (advisory only): a licensed attorney must independently verify every citation. "
        "This organ does not file, appear, or bind the estate."
    )
    brief = "\n".join(lines)
    blocked = policy.get("decision") == "BLOCKED" and bool(text)
    minted = mint_counsel_receipt(
        action="command",
        decision="BLOCKED" if blocked else "ALLOW",
        honesty="REPORTED",
        prev=prev_hash,
        payload={"action": "command", "prompt": text, "human_lock": human_lock},
        model=None,
        reason="Grounded SOFTWARE command cycle over live docket and Hub estate.",
    )
    return {
        "schema": "szl.ayllu.counsel-command/v1",
        "runtime": "OPERATIONAL",
        "legal_authority": "PROPOSAL_ONLY",
        "backend": "SOFTWARE",
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "phi_s": "UNAVAILABLE",
        "blocked": blocked,
        "text": brief if not blocked else "BLOCKED — " + " ".join(policy.get("reasons") or []),
        "policy": policy,
        "docket": {
            "ok": bool(docket.get("ok")),
            "live": bool(docket.get("live")),
            "federal_count": docket.get("federal_count"),
            "court_count": docket.get("court_count"),
            "honesty_tier": docket.get("honesty_tier"),
            "federal": federal,
        },
        "estate": {
            "ok": bool(estate.get("ok")),
            "models": len(models),
            "spaces": len(spaces),
            "datasets": len(datasets),
            "honesty_tier": estate.get("honesty_tier"),
        },
        "allodial": {"A": allo.get("A"), "honesty": allo.get("honesty"), "experimental": True},
        "lambda": "CONJECTURE_1",
        **minted,
    }
