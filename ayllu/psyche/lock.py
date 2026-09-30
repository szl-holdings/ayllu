"""Human Lock, restraint ladder, doctrine lock.

State-changing morphisms fail closed without the lock.
Engagement is demo intent, never verified two-person approval.
Restraint rungs demand evidence. Joules stay None.
Λ floor is advisory; attestation is binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ayllu.autonomy import gate as autonomy_gate
from ayllu.psyche.types import DOCTRINE, ENERGY, Honesty, LAMBDA, LOCK_ID, Decision

RUNGS = (
    {"n": 0, "name": "observe", "need": 0.0},
    {"n": 1, "name": "advise", "need": 0.25},
    {"n": 2, "name": "propose", "need": 0.5},
    {"n": 3, "name": "commit", "need": 0.75},
    {"n": 4, "name": "act", "need": 0.92},
)

WRITE_ACTIONS = frozenset({"imprint", "forget", "reset", "replay", "commit", "act"})


@dataclass
class HumanLock:
    engaged: bool = False
    doctrine: str = DOCTRINE
    lock: str = LOCK_ID

    def __post_init__(self) -> None:
        if type(self.engaged) is not bool:
            raise ValueError("engaged must be a boolean")

    def engage(self) -> None:
        self.engaged = True

    def release(self) -> None:
        self.engaged = False

    def evidence(self) -> float:
        return 0.8 if self.engaged is True else 0.2

    def ladder(self) -> dict[str, Any]:
        ev = self.evidence()
        allowed = [r["name"] for r in RUNGS if ev >= r["need"]]
        blocked = [r["name"] for r in RUNGS if ev < r["need"]]
        return {
            "evidence": ev,
            "allowed": allowed,
            "blocked": blocked,
            "honesty": Honesty.MODELED.value,
            "lock": self.engaged,
            "approval_status": "UNVERIFIED_DEMO",
            "write_authorized": False,
        }

    def admit(self, action: str, *, state_changing: bool | None = None) -> dict[str, Any]:
        reasons: list[str] = []
        invalid_changing = state_changing is not None and type(state_changing) is not bool
        changing = action in WRITE_ACTIONS or state_changing is True or invalid_changing
        if invalid_changing:
            reasons.append("state_changing must be a boolean (fail-closed).")
        if type(self.engaged) is not bool:
            reasons.append("Demo engagement must be a boolean (fail-closed).")
        if changing and self.engaged is not True:
            reasons.append("Human Lock is required for this action (fail-closed).")
        ladder = self.ladder()
        if changing and "commit" not in ladder["allowed"]:
            reasons.append("Restraint blocks commit at this evidence.")
        auto = autonomy_gate(
            action,
            state_changing=changing,
            # No trusted verifier is configured. Caller intent cannot satisfy
            # the binding requirement for verified two-person approval.
            two_person_attested=False,
        )
        if not auto["allow"]:
            reasons.append(auto["reason"])
        decision = Decision.BLOCKED if reasons else Decision.ALLOW
        return {
            "decision": decision.value,
            "reasons": reasons,
            "action": action,
            "state_changing": changing,
            "lock": self.engaged,
            "ladder": ladder,
            "autonomy": auto,
            "approval_status": "UNVERIFIED_DEMO",
            "two_person_attested": False,
            "doctrine": self.doctrine,
            "lockId": self.lock,
            "honesty": Honesty.MEASURED.value,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "engaged": self.engaged,
            "doctrine": self.doctrine,
            "lock": self.lock,
            "ladder": self.ladder(),
            "honesty": Honesty.MODELED.value if self.engaged is True else Honesty.UNAVAILABLE.value,
            "approval_status": "UNVERIFIED_DEMO",
            "two_person_attested": False,
            "write_authorized": False,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }


def require_rung(ladder: dict[str, Any], name: str) -> bool:
    allowed: Iterable[str] = ladder.get("allowed") or []
    return name in set(allowed)
