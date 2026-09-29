"""ayllu.autonomy — a11oy's bounded-autonomy gate for ayllu personas.

This is the single most important adaptation from the tribe. The tribe's souls carry
a "fully agentic, no sandbox, execute don't narrate" mandate. a11oy REJECTS that. Every
ayllu action passes this fail-closed gate:

  * a state-changing action is DENIED unless two-person attested;
  * if a Λ score is supplied and falls below the advisory floor, it is DENIED;
  * if a Λ score is supplied and is not a Λ, it is DENIED before any compare, using
    the szl.lambda/v1 error codes: not a real number (LAMBDA_TYPE_INVALID), NaN or
    ±Inf (LAMBDA_NONFINITE_AXIS), outside [0, 1] (LAMBDA_AXIS_OUT_OF_RANGE); a floor
    that is not a threshold in (0, 1] denies it too, checked first (LAMBDA_TAU_INVALID);
  * read-only / non-state-changing actions are allowed.

An ABSENT Λ is unchanged: attestation stays the binding gate and the unchecked floor
is annotated as an advisory. Making an absent Λ deny is an owner decision:
HumanLock.admit has no Λ source, so it would block every psyche write.

The gate mirrors the discipline of a11oy_agent_loop.AgentLoop's local PURIQ gate so
that behaviour is consistent whether or not the full orchestrator is wired in.
"""
from __future__ import annotations

import math
from typing import Any, Optional

LAMBDA_FLOOR_DEFAULT = 0.90


def _is_real(x: Any) -> bool:
    # szl.lambda/v1: a real number is an int or a float, and bool is not a number.
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _lambda_error(score: Any, floor: Any) -> Optional[str]:
    """The szl.lambda/v1 error code for a supplied Λ and its floor, or None if both are valid.

    The floor is checked first, as v1's gate checks τ first. A NaN floor or Λ would
    otherwise make `score < floor` False and fall through to allow.
    """
    if not _is_real(floor) or not 0 < floor <= 1:  # also false for NaN and ±Inf
        return "LAMBDA_TAU_INVALID"
    if not _is_real(score):
        return "LAMBDA_TYPE_INVALID"
    if isinstance(score, float) and not math.isfinite(score):
        return "LAMBDA_NONFINITE_AXIS"
    if not 0 <= score <= 1:
        return "LAMBDA_AXIS_OUT_OF_RANGE"
    return None


def _show(x: Any) -> str:
    """A short rendering of a supplied value for a reason: never an arbitrary object."""
    if isinstance(x, float) or (_is_real(x) and x.bit_length() <= 64):
        return repr(x)
    return f"<{type(x).__name__}>"


def gate(
    action: str,
    *,
    state_changing: bool,
    persona: Any = None,
    two_person_attested: bool = False,
    lambda_score: Optional[float] = None,
    lambda_floor: float = LAMBDA_FLOOR_DEFAULT,
) -> dict[str, Any]:
    reasons: list[str] = []
    advisories: list[str] = []
    allow = True

    # Hard, fail-closed gate: state-changing actions need two-person attestation.
    # This is the BINDING guard — it never silently passes.
    if state_changing and not two_person_attested:
        allow = False
        reasons.append("state-changing action requires two-person attestation "
                       "(a11oy fail-closed law)")

    # Λ floor is ADVISORY (matching a11oy's org-Λ advisory-floor surface): a supplied
    # score below the floor denies; an ABSENT score on a state-change is not silently
    # treated as a pass — it is annotated so the claim stays honest.
    lambda_checked = lambda_score is not None
    lambda_error = _lambda_error(lambda_score, lambda_floor) if lambda_checked else None
    if lambda_error is not None:
        allow = False
        reasons.append(f"Λ={_show(lambda_score)} with floor {_show(lambda_floor)} is outside "
                       f"the szl.lambda/v1 contract ({lambda_error}) — FAIL-CLOSED")
    elif lambda_checked and float(lambda_score) < float(lambda_floor):
        allow = False
        reasons.append(f"Λ={float(lambda_score):.3f} < floor {float(lambda_floor):.2f} "
                       "— FAIL-CLOSED")
    elif state_changing and not lambda_checked:
        advisories.append(f"Λ advisory floor {float(lambda_floor):.2f} UNCHECKED "
                          "(no score supplied); attestation is the binding gate")

    if reasons:
        reason = "; ".join(reasons)
    elif advisories:
        reason = "allowed (attestation satisfied); " + "; ".join(advisories)
    else:
        reason = "allowed (non-state-changing, or attested with Λ ≥ floor)"

    return {
        "action": action,
        "allow": allow,
        "state_changing": bool(state_changing),
        "two_person_attested": bool(two_person_attested),
        "lambda_checked": lambda_checked,
        "lambda_error": lambda_error,
        "lambda_floor": None if lambda_error == "LAMBDA_TAU_INVALID" else float(lambda_floor),
        "persona": getattr(persona, "name", None),
        "reason": reason,
        "advisories": advisories,
        "law": "a11oy bounded-autonomy — attestation is the binding fail-closed gate; "
               "the Λ floor is advisory; the tribe's unbounded 'always execute' mandate "
               "is NOT in force",
    }
