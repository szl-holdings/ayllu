"""Ouroboros bounded loop — from szl-holdings/ouroboros.

The TypeScript kernel (runLoop) MUST terminate on one of:
  converged | consistent | aborted | budgetExhausted
and emit a governance receipt. The trace is the product.

Hatun-MCP README: hatun does NOT implement this kernel; Ayllu does, as a
SOFTWARE tax on council rounds. receipts.in ≡ receipts.out.
"""
from __future__ import annotations

from typing import Any

MAX_ROUNDS = 2  # debate = 2, single = 1 — never open-ended


def identity() -> dict[str, Any]:
    """SOFTWARE kernel identity. No tax without a council receipt this request."""
    return {
        "schema": "szl.ayllu.ouroboros/v1",
        "source": "https://github.com/szl-holdings/ouroboros",
        "kernel_twin": "https://github.com/szl-holdings/szl-ouroboros",
        "kind": "SOFTWARE",
        "identity": "receipts.in ≡ receipts.out",
        "budget": MAX_ROUNDS,
        "rounds_spent": 0,
        "tax": None,
        "exit": "UNAVAILABLE",
        "chain_head": None,
        "last": "UNAVAILABLE",
        "last_label": "UNAVAILABLE",
        "terminating": True,
        "perpetual_motion": False,
        "lambda": "CONJECTURE_1",
        "honesty": (
            "SOFTWARE bounded-loop kernel identity. Last tax is UNAVAILABLE until a "
            "council receipt exists on this request. Always terminates. Not the "
            "TypeScript runLoop binary. Not measured CUDA."
        ),
    }


def tax(mode: str, round_count: int, chain_head: str) -> dict[str, Any]:
    rounds = int(round_count)
    budget = MAX_ROUNDS
    if mode == "debate" and rounds >= 2:
        exit_state = "converged"
    elif rounds >= 1:
        exit_state = "consistent"
    elif rounds <= 0:
        exit_state = "aborted"
    else:
        exit_state = "consistent"
    if rounds > budget:
        exit_state = "budgetExhausted"

    return {
        "schema": "szl.ayllu.ouroboros/v1",
        "source": "https://github.com/szl-holdings/ouroboros",
        "kernel_twin": "https://github.com/szl-holdings/szl-ouroboros",
        "kind": "SOFTWARE",
        "identity": "receipts.in ≡ receipts.out",
        "budget": budget,
        "rounds_spent": rounds,
        "tax": rounds,  # 1 unit per round
        "exit": exit_state,
        "chain_head": chain_head,
        "terminating": True,
        "perpetual_motion": False,
        "lambda": "CONJECTURE_1",
        "honesty": (
            "Bounded loop tax. Always terminates. Not the TypeScript runLoop binary. "
            "Not a claim of measured CUDA."
        ),
    }
