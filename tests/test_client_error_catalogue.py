"""4xx bodies come from the fixed catalogue, chosen by the message this module raised.

Regression tests for d154a87 ("resolve CodeQL findings — py/stack-trace-exposure"),
which moved every 4xx body onto ``_client_error`` but:

* left two of this module's own messages out of the catalogue, so they collapsed
  to the generic "invalid request body";
* matched catalogue entries by plain substring, so request content quoted inside
  a message (a persona name, an ``int()`` error repeating the value) could pick a
  different entry -- a valid JSON body answered "invalid JSON body";
* kept one handler returning ``str(exc)`` (``/api/v1/psyche/compose`` 413).

Offline: AYLLU_FORCE_SOFTWARE keeps the backend on the SOFTWARE path, the rate
buckets are stubbed open, and the Psyche instance is a fresh local one.
"""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app as app_module
from ayllu.psyche.engine import Psyche

OPEN = SimpleNamespace(check=lambda: (True, 0))
GENERIC = "invalid request body"
FIXED_TEXTS = set(app_module._CLIENT_ERROR_CATALOGUE) | {GENERIC}
TOO_LARGE = f"request body exceeds {app_module.MAX_BODY_BYTES} bytes"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AYLLU_FORCE_SOFTWARE", "1")
    for bucket in ("_ASK_BUCKET", "_COUNCIL_BUCKET", "_COUNSEL_BUCKET", "_PSYCHE_BUCKET"):
        monkeypatch.setattr(app_module, bucket, OPEN)
    monkeypatch.setattr(app_module, "PSYCHE", Psyche())
    c = TestClient(app_module.app, raise_server_exceptions=False)
    yield c
    c.close()


@pytest.mark.parametrize(
    "route,body,expected",
    [
        ("/api/v1/ayllu/ask", {"persona": "Amaru"}, "prompt is required"),
        ("/api/v1/ayllu/council", {}, "prompt is required"),
        ("/api/v1/ayllu/council", {"prompt": "x", "personas": "Amaru"}, "personas must be a list of names"),
    ],
)
def test_module_messages_are_not_collapsed_to_generic(client, route, body, expected) -> None:
    r = client.post(route, json=body)
    assert r.status_code == 400
    assert r.json() == {"error": expected}


@pytest.mark.parametrize(
    "injected",
    ["invalid JSON body", "request body must be a JSON object", TOO_LARGE, "prompt is required"],
)
def test_persona_name_cannot_select_another_message(client, injected) -> None:
    r = client.post("/api/v1/ayllu/council", json={"prompt": "x", "personas": [injected]})
    assert r.status_code == 400
    assert r.json() == {"error": "unknown persona"}


@pytest.mark.parametrize("route,field", [("replay", "rounds"), ("sense", "k"), ("graft", "k")])
def test_quoted_integer_value_cannot_select_another_message(client, route, field) -> None:
    injected = "request body must be a JSON object"
    r = client.post("/api/v1/psyche/" + route, json={"cue": "synthetic fixture", field: injected})
    assert r.status_code == 400
    error = r.json()["error"]
    assert error != injected
    assert error in FIXED_TEXTS


@pytest.mark.parametrize(
    "raised,expected",
    [
        ("prompt is required", "prompt is required"),
        ("unknown persona: Nobody", "unknown persona"),
        ("engaged must be a JSON boolean", "must be a JSON boolean"),
        ("conflicting boolean aliases: human_lock, humanLock, lock", "conflicting boolean aliases"),
        ("unknown persona: invalid JSON body", "unknown persona"),
        ("invalid literal for int() with base 10: 'invalid JSON body'", GENERIC),
        ("invalid literal for int() with base 10: 'x must be a JSON boolean'", GENERIC),
        ("x invalid JSON body", GENERIC),
        ("not one field must be a JSON boolean", GENERIC),
        ("something else entirely", GENERIC),
    ],
)
def test_catalogue_match_is_anchored(raised, expected) -> None:
    r = app_module._client_error(ValueError(raised), 400)
    assert r.status_code == 400
    assert r.body == ('{"error":"%s"}' % expected).encode()


@pytest.mark.parametrize(
    "route",
    [
        "/api/v1/ayllu/ask",
        "/api/v1/ayllu/council",
        "/api/v1/counsel/infer",
        "/api/v1/psyche/lock",
        "/api/v1/psyche/imprint",
        "/api/v1/psyche/recall",
        "/api/v1/psyche/replay",
        "/api/v1/psyche/compose",
        "/api/v1/psyche/sense",
        "/api/v1/psyche/graft",
        "/api/v1/psyche/beat",
    ],
)
def test_oversized_body_is_the_fixed_413_text(client, route) -> None:
    big = "x" * (app_module.MAX_BODY_BYTES + 1)
    r = client.post(route, content=('{"cue": "%s"}' % big).encode(), headers={"content-type": "application/json"})
    assert r.status_code == 413
    assert r.json() == {"error": TOO_LARGE}


def test_no_app_handler_puts_a_caught_exception_in_a_response() -> None:
    """Source guard for py/stack-trace-exposure in app.py.

    Inside every ``except ... as name:`` block the caught exception may only be
    chained (``raise ... from name``) or handed to ``_client_error(name, ...)``.
    """
    tree = ast.parse(Path(app_module.__file__).read_text(encoding="utf-8"))
    offenders = []
    for handler in ast.walk(tree):
        if not isinstance(handler, ast.ExceptHandler) or not handler.name:
            continue
        allowed = set()
        for node in ast.walk(handler):
            if isinstance(node, ast.Raise) and isinstance(node.cause, ast.Name):
                allowed.add(id(node.cause))
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_client_error"
                and node.args
                and isinstance(node.args[0], ast.Name)
            ):
                allowed.add(id(node.args[0]))
        for node in ast.walk(handler):
            if isinstance(node, ast.Name) and node.id == handler.name and id(node) not in allowed:
                offenders.append(f"app.py:{node.lineno} uses caught exception {handler.name!r}")
    assert offenders == []
