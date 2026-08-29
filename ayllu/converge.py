"""Dissent-first convergence — the category we own.

Leaders in the space (Unanimous Hyperchat, 3D LLM Council, CrewAI crews)
optimize for a single synthesized answer. Ayllu refuses fake consensus.

This module only reports lexical agreement/dissent markers. Semantic
consensus and council effectiveness stay NOT_MEASURED until a labeled
eval exists. Honest dissent is first-class output.
"""
from __future__ import annotations

from typing import Any

DISSENT_MARKERS = (
    "dissent",
    "disagree",
    "i do not agree",
    "i don't agree",
    "object:",
    "contra",
    "however,",
    "on the contrary",
    "i reject",
)
AGREE_MARKERS = (
    "i agree",
    "agree with",
    "concur",
    "align with",
    "same conclusion",
)


def _hay(turn: dict[str, Any]) -> str:
    return " ".join(
        str(turn.get(k) or "") for k in ("answer", "honesty")
    ).lower()


def synthesize(prompt: str, rounds: list[dict[str, Any]]) -> dict[str, Any]:
    dissent: list[dict[str, Any]] = []
    agreement: list[dict[str, Any]] = []
    unanswered: list[str] = []
    stubs: list[str] = []

    for turn in rounds:
        name = str(turn.get("persona") or "unknown")
        text = _hay(turn)
        if turn.get("answer") in (None, ""):
            unanswered.append(name)
        if turn.get("stub"):
            stubs.append(name)
        hits_d = [m for m in DISSENT_MARKERS if m in text]
        hits_a = [m for m in AGREE_MARKERS if m in text]
        if hits_d:
            dissent.append({"persona": name, "round": turn.get("round", 1), "markers": hits_d})
        if hits_a:
            agreement.append({"persona": name, "round": turn.get("round", 1), "markers": hits_a})

    final = [t for t in rounds if t.get("round") in (None, 2) or t.get("round") == max(
        (r.get("round") or 1) for r in rounds
    )] if rounds else []
    voices = sorted({t.get("persona") for t in rounds if t.get("answer")})

    return {
        "schema": "szl.ayllu.converge/v1",
        "prompt_sha256": __import__("hashlib").sha256(
            (prompt or "").encode("utf-8")
        ).hexdigest(),
        "voices_that_answered": voices,
        "lexical_dissent": dissent,
        "lexical_agreement": agreement,
        "unanswered": unanswered,
        "stub_personas": stubs,
        "final_round_count": len(final),
        "semantic_consensus": "NOT_MEASURED",
        "effectiveness": "NOT_MEASURED",
        "authority": "PROPOSAL_ONLY",
        "frontier": (
            "Dissent is retained as a first-class set. Ayllu does not collapse "
            "the table into one 'best' answer the way 3D LLM councils and "
            "Hyperchat amplification products do."
        ),
        "honesty": (
            "Lexical marker scan only. Not a judge of truth, not a swarm IQ, "
            "not MEASURED consensus."
        ),
    }
