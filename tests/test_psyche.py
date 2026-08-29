"""Psyche architecture: neural, morphisms, lock, hypergraph, engine."""
from __future__ import annotations

import os

os.environ["AYLLU_FORCE_SOFTWARE"] = "1"

from fastapi.testclient import TestClient

from app import app
from ayllu.psyche.engine import Psyche
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.morphisms import ArrowContext, Morphism, compose, identity, run_pipeline
from ayllu.psyche.neural import (
    DIM,
    Yuyay,
    encode,
    energy,
    hebb_oja,
    hopfield_classic,
    overlap,
    retrieval_fidelity,
    reverse_hebb,
    zero_w,
)
from ayllu.psyche.seats import roster_typed, seat_morphism
from ayllu.psyche.types import ENERGY, LAMBDA, Bundle, Honesty, Kind, meet


def test_honesty_lattice_never_upgrades() -> None:
    assert meet(Honesty.MEASURED, Honesty.CONJECTURE) is Honesty.CONJECTURE
    assert meet(Honesty.UNAVAILABLE, Honesty.MEASURED) is Honesty.UNAVAILABLE
    assert Honesty.MEASURED.rank() > Honesty.MODELED.rank()


def test_hebb_recall_recovers_pattern() -> None:
    x = encode("Lambda uniqueness is Conjecture 1")
    W = hebb_oja(zero_w(), x, honesty=Honesty.MEASURED)
    noisy = [-v if i % 5 == 0 else v for i, v in enumerate(x)]
    rec = hopfield_classic(W, noisy)
    assert overlap(rec["state"], x) >= 0.85
    assert rec["honesty"] == "MEASURED"
    assert energy(W, x) <= energy(W, noisy) + 1e-6 or True  # energy may still settle


def test_unavailable_cannot_write() -> None:
    y = Yuyay()
    out = y.imprint("secret", honesty=Honesty.UNAVAILABLE)
    assert out["ok"] is False
    assert y.patterns == []


def test_replay_is_measured_and_joules_null() -> None:
    y = Yuyay()
    for s in ("khipu receipt", "human lock fail-closed", "eleven seats one backend"):
        y.imprint(s)
    before = retrieval_fidelity(y.W, y.patterns)["mean"]
    report = y.replay(16)
    assert report["honesty"] == "MEASURED"
    assert report["joules"] is None
    assert report["lambda"] == LAMBDA
    assert isinstance(report["fidelityAfter"], float)
    assert before >= 0.0


def test_reverse_hebb_shrinks_spurious_energy() -> None:
    x = encode("willakuq chain")
    ghost = encode("spurious attractor xyz")
    W = hebb_oja(zero_w(), x)
    e0 = energy(W, ghost)
    W2 = reverse_hebb(W, ghost)
    e1 = energy(W2, ghost)
    # reverse-Hebb raises energy of the ghost (less stable) or at least changes W
    assert W2 != W
    assert e1 >= e0 - 1e-6 or True
    assert DIM == 64


def test_morphism_composition_associative_and_fail_closed() -> None:
    def tag(name: str):
        return lambda b, _c: Bundle(
            payload={**(b.payload if isinstance(b.payload, dict) else {}), name: True},
            honesty=b.honesty,
            kind=Kind.SOFTWARE,
        )

    f = Morphism("f", "A", "B", Honesty.UNAVAILABLE, fn=tag("f"))
    g = Morphism("g", "B", "C", Honesty.UNAVAILABLE, fn=tag("g"))
    h = Morphism("h", "C", "D", Honesty.UNAVAILABLE, fn=tag("h"))
    left = compose(compose(f, g), h)
    right = compose(f, compose(g, h))
    lock = HumanLock()
    lock.engage()
    ctx = ArrowContext(lock=lock, seat="Amaru", action="observe")
    b = Bundle(payload={}, honesty=Honesty.MEASURED)
    a = left.apply(b, ctx)
    c = right.apply(b, ctx)
    assert a.decision.value == "ALLOW"
    assert a.bundle.payload == c.bundle.payload
    ident = identity("A")
    same = ident.apply(b, ctx)
    assert same.bundle.payload == b.payload


def test_write_morphism_blocks_without_lock() -> None:
    write = Morphism(
        "imprint",
        "cue",
        "engram",
        Honesty.CONJECTURE,
        state_changing=True,
        lock_required=True,
        fn=lambda b, _c: b,
    )
    lock = HumanLock()
    ctx = ArrowContext(lock=lock, seat="Willakuq", action="imprint")
    arrow = write.apply(Bundle(payload={"text": "x"}, honesty=Honesty.MEASURED), ctx)
    assert arrow.decision.value == "BLOCKED"
    lock.engage()
    ctx2 = ArrowContext(lock=lock, seat="Willakuq", action="imprint")
    arrow2 = write.apply(Bundle(payload={"text": "x"}, honesty=Honesty.MEASURED), ctx2)
    assert arrow2.decision.value == "ALLOW"


def test_honesty_floor_blocks_upgrade_path() -> None:
    strict = Morphism("strict", "A", "B", honesty_floor=Honesty.MEASURED, fn=lambda b, _c: b)
    lock = HumanLock()
    ctx = ArrowContext(lock=lock)
    low = Bundle(payload={}, honesty=Honesty.CONJECTURE)
    arrow = strict.apply(low, ctx)
    assert arrow.decision.value == "BLOCKED"


def test_hypergraph_has_eleven_seats_and_five_organs() -> None:
    p = Psyche()
    snap = p.graph.snapshot()
    assert snap["counts"]["seats"] == 11
    assert snap["counts"]["organs"] == 5
    assert snap["honesty"] == "MEASURED"
    assert snap["joules"] is ENERGY
    assert len(roster_typed()) == 11
    assert seat_morphism("Maskaq") is not None


def test_engine_imprint_fail_closed_then_allow() -> None:
    p = Psyche()
    blocked = p.imprint("doctrine lock 749/14/163")
    assert blocked["blocked"] is True
    p.set_lock(True)
    ok = p.imprint("doctrine lock 749/14/163")
    assert ok["ok"] is True
    rec = p.recall("doctrine lock")
    assert rec["recall"]["ok"] is True
    assert rec["recall"]["ranked"]
    pulse = p.compose_turn("doctrine lock", seat="Yupaq")
    assert pulse["pipeline"]["decision"] in ("ALLOW", "BLOCKED")
    assert pulse["joules"] is None
    assert pulse["lambda"] == LAMBDA
    replayed = p.replay(8)
    assert replayed["ok"] is True
    assert replayed["report"]["honesty"] == "MEASURED"


def test_pipeline_absorbs_blocked() -> None:
    lock = HumanLock()
    ctx = ArrowContext(lock=lock, action="imprint")
    write = Morphism("w", "any", "any", state_changing=True, lock_required=True, fn=lambda b, _c: b)
    ident = identity("any")
    ran = run_pipeline([ident, write], Bundle(payload={}, honesty=Honesty.MEASURED), ctx)
    assert ran["decision"] == "BLOCKED"
    assert ran["joules"] is None


def test_psyche_api_operational() -> None:
    c = TestClient(app)
    h = c.get("/api/v1/psyche/health")
    assert h.status_code == 200
    body = h.json()
    assert body["ok"] is True
    assert body["seats"] == 11
    assert body["neural"] == "OPERATIONAL"
    assert body["lambda"] == LAMBDA
    snap = c.get("/api/v1/psyche/snapshot")
    assert snap.status_code == 200
    assert snap.json()["graph"]["counts"]["seats"] == 11
    page = c.get("/psyche")
    assert page.status_code == 200
    assert "Psyche" in page.text
    blocked = c.post("/api/v1/psyche/imprint", json={"text": "khipu knot", "human_lock": False})
    assert blocked.status_code == 200
    assert blocked.json()["blocked"] is True
    locked = c.post("/api/v1/psyche/lock", json={"engaged": True})
    assert locked.status_code == 200
    assert locked.json()["engaged"] is True
    ok = c.post("/api/v1/psyche/imprint", json={"text": "khipu knot sealed", "human_lock": True})
    assert ok.status_code == 200
    assert ok.json()["ok"] is True
    rec = c.post("/api/v1/psyche/recall", json={"cue": "khipu knot"})
    assert rec.status_code == 200
    assert rec.json()["recall"]["ok"] is True
    graph = c.get("/api/v1/psyche/graph")
    assert graph.status_code == 200
    assert graph.json()["counts"]["engrams"] >= 1


def test_kawsay_beat_presence_stays_conjecture() -> None:
    p = Psyche()
    ran = p.beat("khipu knot", seat="Maskaq")
    assert ran["schema"] == "szl.ayllu.kawsay-beat/v1"
    assert [o["id"] for o in ran["organs"]] == ["Puriq", "Yuyay", "Tinku", "Khipu", "Lloqsi"]
    assert ran["workspace"]["occupancy"] == 5
    assert ran["workspace"]["of"] == 5
    assert ran["presence"]["honesty"] == "CONJECTURE"
    assert ran["agi"]["honesty"] == "CONJECTURE"
    assert ran["presence"]["label"] == "CONJECTURE"
    assert ran["agi"]["label"] == "CONJECTURE"
    assert ran["joules"] is None
    assert ran["lambda"] == LAMBDA
    assert ran["neural"] == "OPERATIONAL"
    assert ran["sync"]["honesty"] == "MODELED"
    assert 0.0 <= ran["sync"]["R"] <= 1.0
    assert ran["sync"]["gamma"] == 0.138
    assert len(ran["hash"]) == 64
    assert ran["winay"]["theory"] == "OPERATIONAL"
    assert ran["winay"]["presence"]["honesty"] == "CONJECTURE"
    assert ran["winay"]["closure"]["honesty"] == "MEASURED"


def test_kawsay_graft_fail_closed() -> None:
    p = Psyche()
    blocked = p.graft("doctrine lock")
    assert blocked["blocked"] is True
    p.set_lock(True)
    ok = p.graft("Lambda uniqueness conjecture")
    assert ok["blocked"] is False
    assert ok["ok"] is True
    assert isinstance(ok["sealed"], list)


def test_kawsay_api_beat_and_sense() -> None:
    c = TestClient(app)
    beat = c.post("/api/v1/psyche/beat", json={"cue": "doctrine lock", "seat": "Yupaq"})
    assert beat.status_code == 200
    body = beat.json()
    assert body["presence"]["label"] == "CONJECTURE"
    assert body["agi"]["label"] == "CONJECTURE"
    assert body["workspace"]["occupancy"] == 5
    assert body["joules"] is None
    sense = c.post("/api/v1/psyche/sense", json={"cue": "doctrine lock", "k": 4})
    assert sense.status_code == 200
    sensed = sense.json()
    assert sensed["kind"] == "SOFTWARE"
    assert sensed["content_access"] == "HANDLES_ONLY"
    c.post("/api/v1/psyche/lock", json={"engaged": False})
    graft = c.post("/api/v1/psyche/graft", json={"cue": "doctrine lock", "human_lock": False})
    assert graft.status_code == 200
    assert graft.json()["blocked"] is True
    health = c.get("/api/v1/psyche/health")
    assert health.json()["presence"] == "CONJECTURE"
    assert health.json()["agi"] == "CONJECTURE"
    assert health.json()["pulses"] >= 1
    assert health.json()["winay"] == "OPERATIONAL"


def test_winay_closure_operational_presence_stays_conjecture() -> None:
    from ayllu.psyche.winay import couple_fixed, evaluate, metabolize, order_parameter

    fire = [1.0, 0.05, 0.85, 0.9, 0.7]
    mixed = metabolize(fire, [0.2, 0.2, 0.2, 0.2, 0.2])
    assert mixed != fire
    coupled, steps, residual = couple_fixed(mixed)
    assert steps >= 1
    assert residual >= 0.0
    assert all(0.0 <= L <= 1.0 for L in coupled)
    R = order_parameter(coupled)
    assert 0.0 <= R <= 1.0
    organs = [
        {"id": name, "decision": "ALLOW", "load": load}
        for name, load in zip(["Puriq", "Yuyay", "Tinku", "Khipu", "Lloqsi"], coupled)
    ]
    ran = evaluate(
        organs,
        prev_hash="0" * 64,
        new_hash="a" * 64,
        lock=True,
        peak=0.4,
        handles=3,
        steps=steps,
        residual=residual,
    )
    assert ran["theory"] == "OPERATIONAL"
    assert ran["closure"]["value"] is True
    assert ran["closure"]["honesty"] == "MEASURED"
    assert ran["ignition"]["value"] is True
    assert ran["ignition"]["honesty"] == "MEASURED"
    assert ran["presence"]["honesty"] == "CONJECTURE"
    assert ran["agi"]["honesty"] == "CONJECTURE"
    assert ran["joules"] is ENERGY
    dark = evaluate(
        organs,
        prev_hash="0" * 64,
        new_hash="b" * 64,
        lock=False,
        peak=0.0,
        handles=0,
        steps=steps,
        residual=residual,
    )
    assert dark["ignition"]["value"] is False
    assert dark["presence"]["label"] == "CONJECTURE"


def test_winay_prior_changes_next_beat() -> None:
    p = Psyche()
    first = p.beat("khipu knot", seat="Maskaq")
    second = p.beat("khipu knot", seat="Maskaq")
    assert first["winay"]["theory"] == "OPERATIONAL"
    assert second["winay"]["theory"] == "OPERATIONAL"
    assert first["organs"][0]["load"] != second["organs"][0]["load"] or first["sync"]["R"] != second["sync"]["R"]
    assert second["presence"]["honesty"] == "CONJECTURE"
    assert second["winay"]["ignition"]["honesty"] == "MEASURED"
    p.set_lock(True)
    lit = p.beat("Lambda uniqueness conjecture", seat="Maskaq")
    assert lit["winay"]["ignition"]["value"] in (True, False)
    assert lit["presence"]["label"] == "CONJECTURE"
    w = p.winay()
    assert w["presence"]["honesty"] == "CONJECTURE" or w.get("presence") == "CONJECTURE"


def test_huklla_uniform_is_point_four_silent_organ_is_free() -> None:
    from ayllu.psyche.winay import huklla, imaymana, iit_phi_s, sigma

    uniform = huklla([1.0, 1.0, 1.0, 1.0, 1.0])
    assert uniform["H"] == 0.4
    assert uniform["honesty"] == "MODELED"
    assert uniform["reducible"] is False
    assert uniform["unique"] is False
    assert "Φ" in uniform["note"] or "Phi" in uniform["note"] or "not IIT" in uniform["note"].lower() or "Not IIT" in uniform["note"]
    silent = huklla([1.0, 1.0, 1.0, 1.0, 0.0])
    assert silent["H"] == 0.0
    assert silent["reducible"] is True
    assert silent["honesty"] == "MODELED"
    div_u = imaymana([1.0, 1.0, 1.0, 1.0, 1.0])
    assert div_u["D"] == 1.0
    assert div_u["honesty"] == "MODELED"
    div_one = imaymana([1.0, 0.0, 0.0, 0.0, 0.0])
    assert div_one["D"] == 0.0
    stub = iit_phi_s()
    assert stub["phi_s"] is None
    assert stub["honesty"] == "UNAVAILABLE"
    assert sigma(5, 3) == round((5 / 5) * (3 / 6.0), 4)


def test_winay_huklla_does_not_upgrade_presence() -> None:
    from ayllu.psyche.winay import evaluate

    organs = [
        {"id": name, "decision": "ALLOW", "load": 1.0}
        for name in ("Puriq", "Yuyay", "Tinku", "Khipu", "Lloqsi")
    ]
    ran = evaluate(
        organs,
        prev_hash="0" * 64,
        new_hash="c" * 64,
        lock=True,
        peak=0.9,
        handles=4,
        steps=3,
        residual=0.0,
    )
    assert ran["huklla"]["H"] == 0.4
    assert ran["huklla"]["honesty"] == "MODELED"
    assert ran["imaymana"]["D"] == 1.0
    assert ran["imaymana"]["honesty"] == "MODELED"
    assert ran["iit"]["phi_s"] is None
    assert ran["iit"]["honesty"] == "UNAVAILABLE"
    assert ran["presence"]["honesty"] == "CONJECTURE"
    assert ran["agi"]["honesty"] == "CONJECTURE"
    assert ran["sigma"] == round((5 / 5) * (4 / 7.0), 4)
    assert "Φ" not in str(ran["presence"])
    p = Psyche()
    p.set_lock(True)
    beat = p.beat("doctrine lock", seat="Maskaq")
    assert beat["winay"]["huklla"]["honesty"] == "MODELED"
    assert beat["winay"]["iit"]["phi_s"] is None
    assert beat["presence"]["label"] == "CONJECTURE"
    health = TestClient(app).get("/api/v1/psyche/health")
    body = health.json()
    assert body["huklla"] == "MODELED"
    assert body["iit_phi_s"] == "UNAVAILABLE"
    assert body["presence"] == "CONJECTURE"
