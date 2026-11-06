"""Malformed client input is a fixed-text 400, never a 500, and never reaches an effect.

Offline: AYLLU_FORCE_SOFTWARE keeps the backend on the SOFTWARE path, the rate
buckets are stubbed per test, and the Psyche instance is a fresh local one.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app as app_module
from ayllu.psyche.engine import Psyche

OPEN = SimpleNamespace(check=lambda: (True, 0))


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AYLLU_FORCE_SOFTWARE", "1")
    for bucket in ("_ASK_BUCKET", "_COUNCIL_BUCKET", "_PSYCHE_BUCKET"):
        monkeypatch.setattr(app_module, bucket, OPEN)
    p = Psyche()
    monkeypatch.setattr(app_module, "PSYCHE", p)
    c = TestClient(app_module.app, raise_server_exceptions=False)
    yield c, p
    c.close()


def _raw(c: TestClient, route: str, text: str):
    return c.post(route, content=text.encode("utf-8"), headers={"content-type": "application/json"})


@pytest.mark.parametrize("value", ["hard", [1], {"a": 1}])
def test_ask_malformed_difficulty_is_400(client, value) -> None:
    c, _ = client
    r = c.post("/api/v1/ayllu/ask", json={"prompt": "hi", "difficulty": value})
    assert r.status_code == 400
    assert r.json() == {"error": "must be a finite number"}


@pytest.mark.parametrize("literal", ["Infinity", "-Infinity", "NaN", "1e999"])
def test_ask_non_finite_difficulty_is_400(client, literal) -> None:
    c, _ = client
    r = _raw(c, "/api/v1/ayllu/ask", '{"prompt": "hi", "difficulty": %s}' % literal)
    assert r.status_code == 400
    assert r.json() == {"error": "must be a finite number"}


@pytest.mark.parametrize("value", [0.7, "0.7", 1, None])
def test_ask_accepts_historic_difficulty_values(client, value) -> None:
    c, _ = client
    r = c.post("/api/v1/ayllu/ask", json={"prompt": "hi", "difficulty": value})
    assert r.status_code == 200
    assert r.json()["receipt"]["signed"] is False


@pytest.mark.parametrize(
    "route,field,effect",
    [
        ("replay", "rounds", "replay"),
        ("sense", "k", "sense"),
        ("graft", "k", "graft"),
    ],
)
@pytest.mark.parametrize("value", [[1], {"a": 1}, "abc", "2.5"])
def test_psyche_malformed_integer_is_400_before_effects(client, monkeypatch, route, field, effect, value) -> None:
    c, p = client
    spy = Mock(wraps=getattr(p, effect))
    monkeypatch.setattr(p, effect, spy)
    r = c.post("/api/v1/psyche/" + route, json={"cue": "synthetic fixture", field: value})
    assert r.status_code == 400
    assert r.json() == {"error": "must be an integer"}
    spy.assert_not_called()


def test_psyche_infinite_rounds_is_400(client) -> None:
    c, p = client
    before = p.snapshot()
    r = _raw(c, "/api/v1/psyche/replay", '{"rounds": Infinity}')
    assert r.status_code == 400
    assert r.json() == {"error": "must be an integer"}
    assert p.snapshot() == before


@pytest.mark.parametrize("value", [3, "3", 0, None])
def test_psyche_accepts_historic_integer_values(client, value) -> None:
    c, _ = client
    r = c.post("/api/v1/psyche/sense", json={"cue": "ouroboros loop", "k": value})
    assert r.status_code == 200
    r = c.post("/api/v1/psyche/replay", json={"rounds": value})
    assert r.status_code == 200
    # The Human Lock still decides; parsing never grants a state change.
    assert r.json()["blocked"] is True


def test_specific_client_messages_survive_the_catalogue(client) -> None:
    c, _ = client
    assert c.post("/api/v1/ayllu/ask", json={"persona": "Amaru"}).json() == {"error": "prompt is required"}
    assert c.post("/api/v1/ayllu/council", json={}).json() == {"error": "prompt is required"}
    r = c.post("/api/v1/ayllu/council", json={"prompt": "x", "personas": "Amaru"})
    assert r.status_code == 400
    assert r.json() == {"error": "personas must be a list of names"}
    r = c.post("/api/v1/ayllu/ask", json={"prompt": "x", "persona": "Nobody"})
    assert r.json() == {"error": "unknown persona"}


def test_oversized_compose_uses_the_fixed_413_text(client) -> None:
    c, p = client
    spy = Mock(wraps=p.compose_turn)
    p.compose_turn = spy
    big = "x" * (app_module.MAX_BODY_BYTES + 1)
    r = _raw(c, "/api/v1/psyche/compose", '{"cue": "%s"}' % big)
    assert r.status_code == 413
    assert r.json() == {"error": f"request body exceeds {app_module.MAX_BODY_BYTES} bytes"}
    spy.assert_not_called()
