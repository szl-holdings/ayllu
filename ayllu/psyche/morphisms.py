"""Fail-closed morphisms (Tinku).

Objects are honesty-typed remits. Morphisms cannot upgrade honesty.
Composition is associative in the arrows it walks: (f∘g)∘h and f∘(g∘h)
apply f, g, h in the same order. BLOCKED is absorbing: a composite keeps
each operand's own gate, so composing never removes a block. (When an arrow
re-stamps remit, the two groupings hold different inner composites whose
remit gates see different bundles, so one grouping can block where the other
allows. Neither grouping ever drops a gate.)
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
    """A typed arrow. Either a leaf (`fn`) or a composite (`parts`), never both.

    A composite first runs its own gate on its input, then walks its parts
    exactly as `run_pipeline` does, so a block anywhere inside it is the
    composite's decision. `then()` keeps both operands whole, so every
    operand's own gate runs on the same bundle it would see alone.
    """

    name: str
    domain: str
    codomain: str
    honesty_floor: Honesty = Honesty.CONJECTURE
    state_changing: bool = False
    lock_required: bool = False
    remit: str = "any"
    fn: ApplyFn | None = None
    parts: tuple["Morphism", ...] = ()

    def __post_init__(self) -> None:
        if self.parts and self.fn is not None:
            raise TypeError(f"morphism {self.name} takes fn or parts, not both")

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
        if self.parts:
            last = _walk(self.parts, bundle, ctx)[-1]
            if last.decision is not Decision.ALLOW:
                # BLOCKED is absorbing: the blocking arrow's reasons and bundle are the composite's.
                why = last.reasons or (f"{last.name} did not allow",)
                return Arrow(self.name, Decision.BLOCKED, last.bundle, self.domain, self.codomain, why)
            return Arrow(self.name, Decision.ALLOW, last.bundle.degrade(bundle.honesty), self.domain, self.codomain)
        payload = bundle
        if self.fn is not None:
            payload = self.fn(bundle, ctx)
        out = payload.degrade(meet(bundle.honesty, payload.honesty))
        return Arrow(self.name, Decision.ALLOW, out, self.domain, self.codomain)

    def then(self, other: "Morphism") -> "Morphism":
        if self.codomain != other.domain and other.domain != "any" and self.codomain != "any":
            raise TypeError(f"cannot compose {self.name}:{self.codomain} then {other.name}:{other.domain}")
        return Morphism(
            name=f"{self.name}∘{other.name}",
            domain=self.domain,
            codomain=other.codomain,
            honesty_floor=meet(self.honesty_floor, other.honesty_floor),
            state_changing=self.state_changing or other.state_changing,
            lock_required=self.lock_required or other.lock_required,
            remit=other.remit if other.remit != "any" else self.remit,
            # Each operand stays whole, never flattened: a composite's own gate can be
            # stricter than its parts (built by hand, or a remit an inner arrow
            # re-stamps), and flattening would drop it.
            parts=(self, other),
        )


def _walk(morphisms: Sequence[Morphism], bundle: Bundle, ctx: ArrowContext) -> list[Arrow]:
    """Apply left-to-right and stop at the first arrow that does not ALLOW."""
    arrows: list[Arrow] = []
    current = bundle
    for m in morphisms:
        arrow = m.apply(current, ctx)
        arrows.append(arrow)
        if arrow.decision is not Decision.ALLOW:
            break
        current = arrow.bundle
    return arrows


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
    arrows = _walk(morphisms, bundle, ctx)
    blocked = bool(arrows) and arrows[-1].decision is not Decision.ALLOW
    decision = Decision.BLOCKED if blocked else Decision.ALLOW
    current = arrows[-1].bundle if arrows else bundle
    return {
        "schema": SCHEMA,
        "decision": decision.value,
        "steps": [arrow.as_dict() for arrow in arrows],
        "out": current.as_dict(),
        "kind": Kind.SOFTWARE.value,
        "joules": ENERGY,
        "lambda": LAMBDA,
        "honesty": current.honesty.value,
    }
