"""The Space manifest's effectiveness label comes from the gold eval it names, not a constant."""
from __future__ import annotations

import os

os.environ["AYLLU_FORCE_SOFTWARE"] = "1"

from fastapi.testclient import TestClient

import ayllu.space as space_module


def _manifest() -> dict:
    return TestClient(space_module.app).get("/api/v1/ayllu/manifest").json()


def test_manifest_label_matches_the_live_gold_eval() -> None:
    c = TestClient(space_module.app)
    man = c.get("/api/v1/ayllu/manifest").json()
    ev = c.get(man["effectiveness_eval"]).json()
    assert ev["schema"] == "szl.ayllu.counsel-eval/v1"
    assert man["effectiveness"] == ev["effectiveness"] == "MEASURED"
    assert man["effectiveness_scope"] == ev["scope"] == "local-policy-ALLOW-BLOCKED"
    # The council itself is still not measured; the policy eval does not upgrade it.
    assert man["council_effectiveness"] == "NOT_MEASURED"
    assert man["semantic_consensus"] == "NOT_MEASURED"


def test_unavailable_eval_is_not_reported_as_measured(monkeypatch) -> None:
    monkeypatch.setattr(space_module, "counsel_eval_from", lambda: {"effectiveness": "UNAVAILABLE"})
    assert _manifest()["effectiveness"] == "UNAVAILABLE"


def test_broken_gold_set_fails_closed(monkeypatch) -> None:
    def broken() -> dict:
        raise FileNotFoundError("gold.json")

    monkeypatch.setattr(space_module, "counsel_eval_from", broken)
    man = _manifest()
    assert man["effectiveness"] == "UNAVAILABLE"
    assert man["council_effectiveness"] == "NOT_MEASURED"
