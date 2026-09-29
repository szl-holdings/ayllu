"""BLOCKED survives composition (FF-08).

`f.then(g)` used to run `g` inside the composite's `fn`, take the blocked
bundle `g` returned, and wrap it as `Decision.ALLOW`. These tests pin the
fix: a block anywhere in a composite is the composite's decision, with the
blocking arrow's own reasons and blocked bundle.

A lock-based probe does not reproduce the old leak, because `then()` ORs
`state_changing` and `lock_required` into the composite, so the composite's
own gate already blocked. The probes below use an honesty-floor block and a
remit block, which only the inner arrow can see.
"""
from __future__ import annotations

from typing import Any

import pytest

from ayllu.psyche.lock import HumanLock
from ayllu.psyche.morphisms import ArrowContext, Morphism, compose, identity, run_pipeline
from ayllu.psyche.types import Bundle, Decision, Honesty, Kind


def _ctx(lock: HumanLock | None = None) -> ArrowContext:
    # Willakuq is not one of the seats that may cross remits.
    return ArrowContext(lock=lock or HumanLock(), seat="Willakuq", action="observe")


def _passthrough(name: str, domain: str, codomain: str, **kw: Any) -> Morphism:
    return Morphism(name, domain, codomain, kw.pop("honesty_floor", Honesty.UNAVAILABLE), fn=lambda b, _c: b, **kw)


def _stamp(remit: str):
    """An fn that moves the bundle into `remit`; the composite's own gate cannot see this."""

    def fn(b: Bundle, _c: ArrowContext) -> Bundle:
        return Bundle(payload=b.payload, honesty=b.honesty, kind=b.kind, remit=remit, notes=b.notes)

    return fn


def _honesty_case() -> tuple[Morphism, Morphism, Bundle]:
    """g alone blocks: CONJECTURE input under a MEASURED floor."""
    f = _passthrough("f", "A", "B")
    g = _passthrough("g", "B", "C", honesty_floor=Honesty.MEASURED)
    return f, g, Bundle(payload={"x": 1}, honesty=Honesty.CONJECTURE)


def _remit_case() -> tuple[Morphism, Morphism, Bundle]:
    """g alone blocks: f moves the bundle into remit 'ledger', g only admits 'counsel'."""
    f = Morphism("f", "A", "B", Honesty.UNAVAILABLE, fn=_stamp("ledger"))
    g = _passthrough("g", "B", "C", remit="counsel")
    return f, g, Bundle(payload={"x": 1}, honesty=Honesty.MEASURED)


CASES = {"honesty_floor": _honesty_case, "remit": _remit_case}


@pytest.mark.parametrize("case", sorted(CASES))
def test_then_returns_blocked_with_g_reasons_when_g_alone_blocks(case: str) -> None:
    f, g, bundle = CASES[case]()
    ctx = _ctx()
    g_input = f.apply(bundle, ctx)
    assert g_input.decision is Decision.ALLOW
    g_alone = g.apply(g_input.bundle, ctx)
    assert g_alone.decision is Decision.BLOCKED
    assert g_alone.reasons

    composed = f.then(g).apply(bundle, ctx)

    assert composed.decision is Decision.BLOCKED
    assert composed.reasons == g_alone.reasons
    assert composed.bundle == g_alone.bundle
    assert composed.bundle.payload["blocked"] is True
    assert composed.name == "f∘g"
    assert (composed.domain, composed.codomain) == ("A", "C")


@pytest.mark.parametrize("case", sorted(CASES))
def test_then_and_run_pipeline_agree(case: str) -> None:
    f, g, bundle = CASES[case]()
    ctx = _ctx()
    composed = f.then(g).apply(bundle, ctx)
    ran = run_pipeline([f, g], bundle, ctx)
    assert ran["decision"] == composed.decision.value == Decision.BLOCKED.value
    assert ran["steps"][-1]["reasons"] == list(composed.reasons)
    assert ran["out"] == composed.bundle.as_dict()


@pytest.mark.parametrize("case", sorted(CASES))
def test_three_deep_compose_with_middle_blocked_is_blocked(case: str) -> None:
    f, g, bundle = CASES[case]()
    ran_h: list[Any] = []

    def h_fn(b: Bundle, _c: ArrowContext) -> Bundle:
        ran_h.append(b.payload)
        return b

    h = Morphism("h", "C", "D", Honesty.UNAVAILABLE, fn=h_fn)
    ctx = _ctx()
    g_alone = g.apply(f.apply(bundle, ctx).bundle, ctx)

    for label, chain in (
        ("compose(f, g, h)", compose(f, g, h)),
        ("(f.g).h", compose(compose(f, g), h)),
        ("f.(g.h)", compose(f, compose(g, h))),
    ):
        arrow = chain.apply(bundle, ctx)
        assert arrow.decision is Decision.BLOCKED, label
        assert arrow.reasons == g_alone.reasons, label
        assert arrow.bundle == g_alone.bundle, label
        assert (arrow.domain, arrow.codomain) == ("A", "D"), label

    # BLOCKED is absorbing: the arrow after the block never runs.
    assert ran_h == []


def test_first_arrow_blocked_stops_the_chain() -> None:
    ran: list[str] = []

    def mark(name: str):
        def fn(b: Bundle, _c: ArrowContext) -> Bundle:
            ran.append(name)
            return b

        return fn

    f = Morphism("f", "A", "B", Honesty.MEASURED, fn=mark("f"))
    g = Morphism("g", "B", "C", Honesty.UNAVAILABLE, fn=mark("g"))
    arrow = f.then(g).apply(Bundle(payload={}, honesty=Honesty.CONJECTURE), _ctx())
    assert arrow.decision is Decision.BLOCKED
    assert arrow.reasons == ("honesty CONJECTURE below floor MEASURED",)
    assert ran == []


def test_lock_block_still_blocks_through_composition() -> None:
    f = _passthrough("f", "any", "any")
    write = Morphism("w", "any", "any", Honesty.UNAVAILABLE, state_changing=True, lock_required=True, fn=lambda b, _c: b)
    bundle = Bundle(payload={}, honesty=Honesty.MEASURED)
    blocked = f.then(write).apply(bundle, _ctx())
    assert blocked.decision is Decision.BLOCKED
    assert blocked.reasons
    lock = HumanLock()
    lock.engage()
    assert f.then(write).apply(bundle, _ctx(lock)).decision is Decision.ALLOW


def test_honesty_never_upgrades_through_composition() -> None:
    def claim_measured(b: Bundle, _c: ArrowContext) -> Bundle:
        return Bundle(payload={"claimed": True}, honesty=Honesty.MEASURED, kind=Kind.SOFTWARE)

    f = Morphism("f", "A", "B", Honesty.UNAVAILABLE, fn=claim_measured)
    g = _passthrough("g", "B", "C")
    h = _passthrough("h", "C", "D")
    low = Bundle(payload={}, honesty=Honesty.CONJECTURE)
    for chain in (f.then(g), compose(f, g, h), compose(compose(f, g), h), compose(f, compose(g, h))):
        arrow = chain.apply(low, _ctx())
        assert arrow.decision is Decision.ALLOW
        assert arrow.bundle.honesty is Honesty.CONJECTURE
        assert arrow.bundle.payload == {"claimed": True}

    # The upgraded claim cannot be used to pass a stricter floor downstream.
    strict = _passthrough("strict", "B", "C", honesty_floor=Honesty.MEASURED)
    blocked = f.then(strict).apply(low, _ctx())
    assert blocked.decision is Decision.BLOCKED
    assert blocked.reasons == ("honesty CONJECTURE below floor MEASURED",)
    assert "claimed" not in blocked.bundle.payload


def test_compose_of_nothing_is_still_the_identity() -> None:
    ident = compose()
    assert ident.name == identity().name == "id"
    assert (ident.domain, ident.codomain) == ("any", "any")
    b = Bundle(payload={"k": "v"}, honesty=Honesty.REPORTED, remit="counsel")
    arrow = ident.apply(b, _ctx())
    assert arrow.decision is Decision.ALLOW
    assert arrow.reasons == ()
    assert arrow.bundle == b

    # Identity laws hold for a blocking arrow too: id.g and g.id block exactly as g does.
    f, g, bundle = _honesty_case()
    g_alone = g.apply(bundle, _ctx())
    for chain in (compose().then(g), g.then(compose())):
        arrow = chain.apply(bundle, _ctx())
        assert arrow.decision is Decision.BLOCKED
        assert arrow.reasons == g_alone.reasons


def test_composition_flattens_parts_and_does_not_use_fn() -> None:
    f = _passthrough("f", "A", "B")
    g = _passthrough("g", "B", "C")
    h = _passthrough("h", "C", "D")
    left = compose(compose(f, g), h)
    right = compose(f, compose(g, h))
    assert left.parts == right.parts == (f, g, h)
    assert left.fn is None and right.fn is None
    assert f.parts == ()


def test_morphism_with_both_fn_and_parts_is_refused() -> None:
    f = _passthrough("f", "A", "B")
    with pytest.raises(TypeError, match="fn or parts, not both"):
        Morphism("both", "A", "B", fn=lambda b, _c: b, parts=(f,))
