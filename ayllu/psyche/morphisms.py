"""Fail-closed morphisms (Tinku).

Objects are honesty-typed remits. Morphisms cannot upgrade honesty.
Composition is associative. BLOCKED is absorbing.
State-changing arrows require Human Lock.

This is Ayllu's composition law — typed, fail-closed, receipted.
Λ uniqueness stays Conjecture 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from ayllu.psyche.lock import HumanLock
from ayllu.psyche.types import (
    ENERGY,
    LAMBDA,
    SCHEMA,
    Bundle,
    Decision,
    Honesty,
    Kind,
    blocked_bundle,
    can_flow,
    meet,
)

ApplyFn = Callable[[Bundle, "ArrowContext"], Bundle]


@dataclass
class ArrowContext:
    lock: HumanLock
    seat: str = "Amaru"
    action: str = "observe"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Arrow:
    """One evaluated morphism. Always labeled. Energy is None."""

    name: str
    decision: Decision
    bundle: Bundle
    domain: str
    codomain: str
    reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "decision": self.decision.value,
            "domain": self.domain,
            "codomain": self.codomain,
            "reasons": list(self.reasons),
            "bundle": self.bundle.as_dict(),
            "joules": ENERGY,
            "lambda": LAMBDA,
        }


@dataclass
class Morphism:
    name: str
    domain: str
    codomain: str
    honesty_floor: Honesty = Honesty.CONJECTURE
    state_changing: bool = False
    lock_required: bool = False
    remit: str = "any"
    fn: ApplyFn | None = None

    def apply(self, bundle: Bundle, ctx: ArrowContext) -> Arrow:
        reasons: list[str] = []
        if self.lock_required or self.state_changing:
            gate = ctx.lock.admit(ctx.action or self.name, state_changing=self.state_changing)
            if gate["decision"] != Decision.ALLOW.value:
                reasons.extend(gate["reasons"])
        if not can_flow(bundle.honesty, self.honesty_floor):
            reasons.append(
                f"honesty {bundle.honesty.value} below floor {self.honesty_floor.value}"
            )
        if self.remit != "any" and bundle.remit not in ("any", self.remit) and ctx.seat not in (
            "Amaru",
            "Kamachiq",
        ):
            reasons.append(f"remit {bundle.remit} cannot enter {self.remit}")
        if reasons:
            blocked = blocked_bundle("; ".join(reasons), remit=self.codomain)
            return Arrow(self.name, Decision.BLOCKED, blocked, self.domain, self.codomain, tuple(reasons))
        payload = bundle
        if self.fn is not None:
            payload = self.fn(bundle, ctx)
        out = payload.degrade(meet(bundle.honesty, payload.honesty))
        return Arrow(self.name, Decision.ALLOW, out, self.domain, self.codomain)

    def then(self, other: "Morphism") -> "Morphism":
        if self.codomain != other.domain and other.domain != "any" and self.codomain != "any":
            raise TypeError(f"cannot compose {self.name}:{self.codomain} then {other.name}:{other.domain}")

        def composed(bundle: Bundle, ctx: ArrowContext) -> Bundle:
            a = self.apply(bundle, ctx)
            if a.decision is Decision.BLOCKED:
                return a.bundle
            b = other.apply(a.bundle, ctx)
            return b.bundle

        return Morphism(
            name=f"{self.name}∘{other.name}",
            domain=self.domain,
            codomain=other.codomain,
            honesty_floor=meet(self.honesty_floor, other.honesty_floor),
            state_changing=self.state_changing or other.state_changing,
            lock_required=self.lock_required or other.lock_required,
            remit=other.remit if other.remit != "any" else self.remit,
            fn=composed,
        )


def identity(object_name: str = "any") -> Morphism:
    return Morphism(
        name="id",
        domain=object_name,
        codomain=object_name,
        honesty_floor=Honesty.UNAVAILABLE,
        fn=lambda b, _ctx: b,
    )


def compose(*morphisms: Morphism) -> Morphism:
    if not morphisms:
        return identity()
    acc = morphisms[0]
    for m in morphisms[1:]:
        acc = acc.then(m)
    return acc


def run_pipeline(morphisms: Sequence[Morphism], bundle: Bundle, ctx: ArrowContext) -> dict[str, Any]:
    """Evaluate left-to-right. Stop on first BLOCKED. Honesty never upgrades."""
    steps: list[dict[str, Any]] = []
    current = bundle
    decision = Decision.ALLOW
    for m in morphisms:
        arrow = m.apply(current, ctx)
        steps.append(arrow.as_dict())
        if arrow.decision is Decision.BLOCKED:
            decision = Decision.BLOCKED
            current = arrow.bundle
            break
        current = arrow.bundle
    return {
        "schema": SCHEMA,
        "decision": decision.value,
        "steps": steps,
        "out": current.as_dict(),
        "kind": Kind.SOFTWARE.value,
        "joules": ENERGY,
        "lambda": LAMBDA,
        "honesty": current.honesty.value,
    }
