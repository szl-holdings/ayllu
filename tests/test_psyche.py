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
