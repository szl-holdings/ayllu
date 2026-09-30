"""Local synthetic memory regression tests; no services or approval grants."""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app as app_module
import ayllu.psyche.engine as engine_module
import ayllu.psyche.kawsay as kawsay_module
from ayllu.psyche.engine import Psyche
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.types import Honesty

BAD_FLAGS = [None, "false", "true", "", 0, 1, [], {}]
ROUTES = ["lock", "imprint", "replay", "compose", "graft", "beat"]
ALIASES = [(route, alias) for route in ROUTES for alias in (["engaged", "human_lock", "humanLock", "lock"] if route == "lock" else ["human_lock", "humanLock", "lock"])]


@pytest.fixture
def local_demo(monkeypatch):
    p = Psyche()
    monkeypatch.setattr(app_module, "PSYCHE", p)
    monkeypatch.setattr(app_module, "_PSYCHE_BUCKET", SimpleNamespace(check=lambda: (True, 0)))
    empty = lambda *_args, **_kwargs: {"handles": [], "ready": False, "honesty": "UNAVAILABLE", "kind": "SOFTWARE"}
    monkeypatch.setattr(engine_module, "kawsay_sense", empty)
    monkeypatch.setattr(kawsay_module, "sense", empty)
    client = TestClient(app_module.app)
    yield client, p
    client.close()


def payload():
    return {"text": "synthetic fixture", "cue": "synthetic fixture", "honesty": "SOFTWARE", "rounds": 1, "k": 1}


def spy_effects(monkeypatch, p):
    spies = []
    for name in ("set_lock", "imprint", "replay", "compose_turn", "graft", "beat"):
        spy = Mock(wraps=getattr(p, name))
        monkeypatch.setattr(p, name, spy)
        spies.append(spy)
    return spies


@pytest.mark.parametrize("route,alias", ALIASES)
@pytest.mark.parametrize("value", BAD_FLAGS)
def test_malformed_aliases_rejected_before_effects(local_demo, monkeypatch, route, alias, value):
    c, p = local_demo
    before = deepcopy(p.snapshot())
    spies = spy_effects(monkeypatch, p)
    response = c.post("/api/v1/psyche/" + route, json={**payload(), alias: value})
    assert response.status_code == 400
    assert "boolean" in response.json()["error"]
    assert p.snapshot() == before
    for spy in spies:
        spy.assert_not_called()


@pytest.mark.parametrize("route", ROUTES)
def test_conflicting_aliases_rejected_without_mutation(local_demo, monkeypatch, route):
    c, p = local_demo
    p.set_lock(True)
    before = deepcopy(p.snapshot())
    spies = spy_effects(monkeypatch, p)
    response = c.post("/api/v1/psyche/" + route, json={**payload(), "human_lock": False, "humanLock": True})
    assert response.status_code == 400
    assert "conflicting" in response.json()["error"]
    assert p.snapshot() == before
    for spy in spies:
        spy.assert_not_called()


@pytest.mark.parametrize("value", BAD_FLAGS)
def test_compose_imprint_type_checked_before_lock_effect(local_demo, monkeypatch, value):
    c, p = local_demo
    spies = spy_effects(monkeypatch, p)
    response = c.post("/api/v1/psyche/compose", json={**payload(), "human_lock": True, "imprint": value})
    assert response.status_code == 400
    assert p.lock.engaged is False
    assert p.pulses == 0
    for spy in spies:
        spy.assert_not_called()


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("alias", ["human_lock", "humanLock", "lock"])
def test_explicit_false_clears_previous_demo_engagement(local_demo, route, alias):
    c, p = local_demo
    p.set_lock(True)
    response = c.post("/api/v1/psyche/" + route, json={**payload(), alias: False})
    assert response.status_code == 200
    assert p.lock.engaged is False
    assert p.lock.snapshot()["two_person_attested"] is False
    assert p.yuyay.patterns == []


def test_missing_and_null_lock_flags_are_distinct(local_demo):
    c, p = local_demo
    p.set_lock(True)
    assert c.post("/api/v1/psyche/lock", json={}).json()["engaged"] is False
    p.set_lock(True)
    assert c.post("/api/v1/psyche/lock", json={"engaged": None}).status_code == 400
    assert p.lock.engaged is True


def test_missing_write_flag_preserves_intent_but_never_approval(local_demo):
    c, p = local_demo
    p.set_lock(True)
    response = c.post("/api/v1/psyche/imprint", json=payload())
    assert response.json()["blocked"] is True
    assert p.lock.engaged is True
    assert response.json()["gate"]["autonomy"]["two_person_attested"] is False


def test_true_matching_aliases_are_demo_intent_only(local_demo):
    c, p = local_demo
    response = c.post("/api/v1/psyche/lock", json={"engaged": True, "human_lock": True, "humanLock": True, "lock": True})
    assert response.status_code == 200
    assert response.json()["honesty"] == "MODELED"
    assert response.json()["approval_status"] == "UNVERIFIED_DEMO"
    assert response.json()["two_person_attested"] is False
    assert response.json()["write_authorized"] is False
    blocked = c.post("/api/v1/psyche/imprint", json={**payload(), "human_lock": True})
    assert blocked.json()["blocked"] is True
    assert p.yuyay.patterns == []


def test_compound_compose_write_stays_blocked_with_demo_intent(local_demo):
    c, p = local_demo
    p.yuyay.imprint("synthetic fixture", honesty=Honesty.SOFTWARE)
    p.graph.add_engram("1", "synthetic fixture", "test", Honesty.SOFTWARE, "0" * 64)
    before = deepcopy((p.yuyay.__dict__, p.graph.snapshot()))
    response = c.post("/api/v1/psyche/compose", json={**payload(), "human_lock": True, "imprint": True})
    assert response.status_code == 200
    assert response.json()["imprint"]["blocked"] is True
    assert response.json()["pipeline"]["decision"] == "BLOCKED"
    assert response.json()["receipt"]["decision"] == "BLOCKED"
    assert response.json()["imprint"]["gate"]["two_person_attested"] is False
    assert (p.yuyay.__dict__, p.graph.snapshot()) == before


def test_read_only_beat_with_demo_intent_preserves_seeded_memory(local_demo):
    c, p = local_demo
    p.yuyay.imprint("synthetic fixture", honesty=Honesty.SOFTWARE)
    p.graph.add_engram("1", "synthetic fixture", "test", Honesty.SOFTWARE, "0" * 64)
    before = deepcopy((p.yuyay.__dict__, p.graph.snapshot()))
    response = c.post("/api/v1/psyche/beat", json={**payload(), "human_lock": True})
    assert response.status_code == 200
    assert p.lock.snapshot()["two_person_attested"] is False
    assert (p.yuyay.__dict__, p.graph.snapshot()) == before


@pytest.mark.parametrize("value", BAD_FLAGS)
def test_backend_boolean_boundaries_leave_state_unchanged(value):
    p = Psyche()
    before = deepcopy(p.snapshot())
    with pytest.raises(ValueError, match="boolean"):
        p.set_lock(value)
    with pytest.raises(ValueError, match="boolean"):
        p.compose_turn("synthetic fixture", imprint=value)
    with pytest.raises(ValueError, match="boolean"):
        HumanLock(engaged=value)
    assert p.snapshot() == before


@pytest.mark.parametrize("action", ["imprint", "forget", "reset", "replay", "commit", "act"])
def test_demo_intent_and_false_override_cannot_attest_named_write(action):
    lock = HumanLock(engaged=True)
    decision = lock.admit(action, state_changing=False)
    assert decision["decision"] == "BLOCKED"
    assert decision["state_changing"] is True
    assert decision["two_person_attested"] is False
    assert decision["autonomy"]["two_person_attested"] is False


@pytest.mark.parametrize("value", BAD_FLAGS[1:])
def test_malformed_state_change_flag_is_fail_closed(value):
    decision = HumanLock(engaged=True).admit("observe", state_changing=value)
    assert decision["decision"] == "BLOCKED"
    assert decision["state_changing"] is True
    assert any("boolean" in reason for reason in decision["reasons"])


@pytest.mark.parametrize("method,args", [("imprint", ("synthetic fixture",)), ("replay", (1,)), ("graft", ("synthetic fixture",)), ("forget", (0,)), ("reset", ())])
def test_blocked_mutations_preserve_synthetic_memory(method, args):
    p = Psyche()
    # Seed isolated algorithm data directly; this grants no route/gate authority.
    p.yuyay.imprint("synthetic fixture", honesty=Honesty.SOFTWARE)
    p.graph.add_engram("1", "synthetic fixture", "test", Honesty.SOFTWARE, "0" * 64)
    p.set_lock(True)
    before = deepcopy((p.yuyay.__dict__, p.graph.snapshot()))
    result = getattr(p, method)(*args)
    assert result["blocked"] is True
    assert result["receipt"]["decision"] == "BLOCKED"
    assert (p.yuyay.__dict__, p.graph.snapshot()) == before


def test_read_only_observation_does_not_require_demo_engagement():
    decision = HumanLock().admit("observe", state_changing=False)
    assert decision["decision"] == "ALLOW"
    assert decision["autonomy"]["two_person_attested"] is False
