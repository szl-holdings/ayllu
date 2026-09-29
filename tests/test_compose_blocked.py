"""BLOCKED survives composition (FF-08).

`f.then(g)` used to run `g` inside the composite's `fn`, take the blocked
bundle `g` returned, and wrap it as `Decision.ALLOW`. These tests pin the
fix: a block anywhere in a composite is the composite's decision, with the
blocking arrow's own reasons and blocked bundle.

A lock-based probe does not reproduce the old leak, because `then()` ORs
`state_changing` and `lock_required` into the composite, so the composite's
own gate already blocked. The probes below use an honesty-floor block and a
remit block, which only the inner arrow can see.

A composite has a gate of its own as well as its parts, and that gate can be
stricter than its parts: it may be built by hand, tightened after `then()`,
or carry a remit that an inner arrow re-stamps. Composing it must not drop
that gate, whichever side of the composition it sits on.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

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
    f_out = f.apply(bundle, ctx).bundle
    g_alone = g.apply(f_out, ctx)

    # For each grouping: the top-level operand that holds g, and the bundle it sees.
    for label, chain, operand, operand_in in (
        ("compose(f, g, h)", compose(f, g, h), compose(f, g), bundle),
        ("(f.g).h", compose(compose(f, g), h), compose(f, g), bundle),
        ("f.(g.h)", compose(f, compose(g, h)), compose(g, h), f_out),
    ):
        arrow = chain.apply(bundle, ctx)
        assert arrow.decision is Decision.BLOCKED, label
        assert arrow.reasons == g_alone.reasons, label
        # BLOCKED is passed up unchanged: the chain's block is exactly the one the
        # blocking operand gives alone. (In f.(g.h) with a remit block, g∘h's own
        # gate refuses first, with g's reason, stamped with g∘h's codomain.)
        alone = operand.apply(operand_in, ctx)
        assert alone.decision is Decision.BLOCKED, label
        assert arrow.bundle == alone.bundle, label
        assert arrow.bundle.payload == g_alone.bundle.payload, label
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


def _leaves(m: Morphism) -> tuple[Morphism, ...]:
    return tuple(leaf for part in m.parts for leaf in _leaves(part)) if m.parts else (m,)


def test_then_keeps_each_operand_whole_and_does_not_use_fn() -> None:
    f = _passthrough("f", "A", "B")
    g = _passthrough("g", "B", "C")
    h = _passthrough("h", "C", "D")
    fg, gh = f.then(g), g.then(h)
    assert fg.parts == (f, g) and fg.fn is None
    left, right = fg.then(h), f.then(gh)
    # Operands are kept whole, never flattened, so neither loses its own gate...
    assert left.parts[0] is fg and left.parts[1] is h
    assert right.parts[0] is f and right.parts[1] is gh
    assert left.fn is None and right.fn is None
    # ...and both groupings still walk the same arrows in the same order.
    assert _leaves(left) == _leaves(right) == _leaves(compose(f, g, h)) == (f, g, h)
    assert f.parts == ()


# --- A composite's own gate survives composition (review B1) -----------------


@dataclass
class GatedCase:
    """`x` blocks on `x_in` by its own gate, even though its parts alone allow.

    `e` turns `chain_in` into `x_in`, so `x` sees the same bundle wherever it sits.
    """

    x: Morphism
    e: Morphism
    chain_in: Bundle
    h_remit: str = "any"


def _floor_parts() -> tuple[Morphism, Morphism]:
    return _passthrough("f", "A", "B"), _passthrough("g", "B", "C")


def _hand_built_floor() -> GatedCase:
    x = Morphism("x", "A", "C", Honesty.MEASURED, parts=_floor_parts())
    return GatedCase(x, _passthrough("e", "Z", "A"), Bundle(payload={"x": 1}, honesty=Honesty.CONJECTURE))


def _floor_tightened_after_then() -> GatedCase:
    f, g = _floor_parts()
    x = replace(f.then(g), name="x", honesty_floor=Honesty.MEASURED)
    return GatedCase(x, _passthrough("e", "Z", "A"), Bundle(payload={"x": 1}, honesty=Honesty.CONJECTURE))


def _restamp(name: str, domain: str, codomain: str, to: str, **kw: Any) -> Morphism:
    return Morphism(name, domain, codomain, Honesty.UNAVAILABLE, fn=_stamp(to), **kw)


def _remit_case_for(x: Morphism) -> GatedCase:
    # e moves the bundle into 'ledger'; x only admits 'counsel'; h admits 'ledger',
    # so no outer gate can see the block and only x's own gate stands in the way.
    e = _restamp("e", "Z", "A", "ledger")
    return GatedCase(x, e, Bundle(payload={"x": 1}, honesty=Honesty.MEASURED), h_remit="ledger")


def _hand_built_remit() -> GatedCase:
    return _remit_case_for(Morphism("x", "A", "C", Honesty.UNAVAILABLE, remit="counsel", parts=_floor_parts()))


def _remit_tightened_after_then() -> GatedCase:
    f, g = _floor_parts()
    return _remit_case_for(replace(f.then(g), name="x", remit="counsel"))


def _remit_built_by_then_with_restamp() -> GatedCase:
    # Built only by then(): x's remit gate is 'counsel', but f re-stamps into
    # 'counsel' and g re-stamps back to 'ledger', so the parts alone allow a
    # 'ledger' bundle that x itself refuses.
    f = _restamp("f", "A", "B", "counsel")
    g = _restamp("g", "B", "C", "ledger", remit="counsel")
    return _remit_case_for(f.then(g))


GATED: dict[str, Callable[[], GatedCase]] = {
    "hand_built_floor": _hand_built_floor,
    "floor_tightened_after_then": _floor_tightened_after_then,
    "hand_built_remit": _hand_built_remit,
    "remit_tightened_after_then": _remit_tightened_after_then,
    "remit_built_by_then_with_restamp": _remit_built_by_then_with_restamp,
}


@pytest.mark.parametrize("case", sorted(GATED))
def test_composite_with_its_own_gate_stays_blocked_on_either_side(case: str) -> None:
    c = GATED[case]()
    ctx = _ctx()
    x_in = c.e.apply(c.chain_in, ctx)
    assert x_in.decision is Decision.ALLOW
    x_alone = c.x.apply(x_in.bundle, ctx)
    assert x_alone.decision is Decision.BLOCKED
    assert x_alone.reasons
    # The block is x's own gate: its parts alone let the same bundle through.
    assert run_pipeline(list(c.x.parts), x_in.bundle, ctx)["decision"] == Decision.ALLOW.value

    ran_h: list[Any] = []

    def h_fn(b: Bundle, _c: ArrowContext) -> Bundle:
        ran_h.append(b.payload)
        return b

    h = Morphism("h", "C", "D", Honesty.UNAVAILABLE, remit=c.h_remit, fn=h_fn)
    x, e = c.x, c.e
    chains = (
        ("x.then(h)", x.then(h), x_in.bundle),
        ("compose(x, h)", compose(x, h), x_in.bundle),
        ("e.then(x)", e.then(x), c.chain_in),
        ("compose(e, x)", compose(e, x), c.chain_in),
        ("compose(e, x, h)", compose(e, x, h), c.chain_in),
        ("e.then(x.then(h))", e.then(x.then(h)), c.chain_in),
    )
    for label, chain, bundle in chains:
        arrow = chain.apply(bundle, ctx)
        assert arrow.decision is Decision.BLOCKED, label
        assert arrow.reasons == x_alone.reasons, label
        assert arrow.bundle.payload["blocked"] is True, label

    # BLOCKED is absorbing: nothing after x runs.
    assert ran_h == []


def test_morphism_with_both_fn_and_parts_is_refused() -> None:
    f = _passthrough("f", "A", "B")
    with pytest.raises(TypeError, match="fn or parts, not both"):
        Morphism("both", "A", "B", fn=lambda b, _c: b, parts=(f,))
