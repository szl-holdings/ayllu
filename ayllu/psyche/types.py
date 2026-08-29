"""Honesty lattice and typed bundles.

Honesty is a partial order. Morphisms are honesty-non-increasing.
LIVE / SOFTWARE are backend kinds, orthogonal to honesty.
Joules are always None. Λ uniqueness is Conjecture 1, never a theorem.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

LAMBDA = "CONJECTURE_1"
DOCTRINE = "v11"
LOCK_ID = "749/14/163"
SLSA = "L1"
SCHEMA = "szl.ayllu.psyche/v1"
ENERGY: None = None


class Honesty(str, Enum):
    MEASURED = "MEASURED"
    REPORTED = "REPORTED"
    MODELED = "MODELED"
    CONJECTURE = "CONJECTURE"
    SOFTWARE = "SOFTWARE"
    LIVE = "LIVE"
    UNAVAILABLE = "UNAVAILABLE"

    def rank(self) -> int:
        return {
            Honesty.MEASURED: 6,
            Honesty.REPORTED: 5,
            Honesty.MODELED: 4,
            Honesty.CONJECTURE: 3,
            Honesty.LIVE: 3,
            Honesty.SOFTWARE: 2,
            Honesty.UNAVAILABLE: 0,
        }[self]


def meet(*values: Honesty | str) -> Honesty:
    """Greatest lower bound. Composition cannot upgrade honesty."""
    ranked = [Honesty(v) if not isinstance(v, Honesty) else v for v in values] or [Honesty.UNAVAILABLE]
    return min(ranked, key=lambda h: h.rank())


def can_flow(src: Honesty | str, dst_floor: Honesty | str) -> bool:
    """A morphism may fire only if source honesty is at least the domain floor."""
    return Honesty(src).rank() >= Honesty(dst_floor).rank()


# Synaptic write gain. UNAVAILABLE writes nothing — alignment in the rule.
ETA_GAIN: Mapping[Honesty, float] = {
    Honesty.MEASURED: 1.0,
    Honesty.REPORTED: 0.70,
    Honesty.MODELED: 0.45,
    Honesty.CONJECTURE: 0.25,
    Honesty.LIVE: 0.40,
    Honesty.SOFTWARE: 0.30,
    Honesty.UNAVAILABLE: 0.0,
}


class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCKED = "BLOCKED"


class Kind(str, Enum):
    SOFTWARE = "SOFTWARE"
    LIVE = "LIVE"


@dataclass(frozen=True)
class Bundle:
    """Typed payload. Energy is structurally None."""

    payload: Any
    honesty: Honesty
    kind: Kind = Kind.SOFTWARE
    remit: str = "any"
    energy: None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def degrade(self, honesty: Honesty | str, note: str = "") -> "Bundle":
        h = meet(self.honesty, Honesty(honesty))
        notes = self.notes + ((note,) if note else ())
        return Bundle(self.payload, h, self.kind, self.remit, None, notes)

    def as_dict(self) -> dict[str, Any]:
        return {
            "payload": self.payload,
            "honesty": self.honesty.value,
            "kind": self.kind.value,
            "remit": self.remit,
            "energy": None,
            "notes": list(self.notes),
            "lambda": LAMBDA,
        }


def blocked_bundle(reason: str, remit: str = "any") -> Bundle:
    return Bundle(
        payload={"blocked": True, "reason": reason},
        honesty=Honesty.MEASURED,
        kind=Kind.SOFTWARE,
        remit=remit,
        notes=(reason,),
    )
