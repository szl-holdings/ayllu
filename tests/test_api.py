import os

os.environ["AYLLU_FORCE_SOFTWARE"] = "1"

from fastapi.testclient import TestClient

from app import app
from ayllu.personas import ROSTER


def test_health_and_roster() -> None:
    c = TestClient(app)
    h = c.get("/health")
    assert h.status_code == 200
    assert h.json()["lambda"] == "CONJECTURE_1"
    r = c.get("/api/v1/ayllu/roster")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 11
    assert len(body["personas"]) == len(ROSTER)


def test_chamber_html() -> None:
    c = TestClient(app)
    page = c.get("/")
    assert page.status_code == 200
    assert "Ayllu" in page.text
    assert "holographic" in page.text.lower()


def test_council_software_and_unsigned() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/council", json={
        "prompt": "Should we claim Lambda is a theorem?",
        "personas": ["Yupaq", "Amaru", "Willakuq"],
        "debate": False,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["converge"]["semantic_consensus"] == "NOT_MEASURED"
    assert body["receipt"]["signed"] is False
    assert body["chain"]["kind"] == "SOFTWARE"
    assert len(body["rounds"]) == 3
    assert body["lambda"] == "CONJECTURE_1"


def test_organism_routes() -> None:
    c = TestClient(app)
    a = c.get("/api/v1/ayllu/anatomy")
    assert a.status_code == 200
    assert len(a.json()["organs"]) == 5
    sb = c.get("/api/v1/ayllu/second-brain")
    assert sb.status_code == 200
    assert sb.json()["system_id"] == "SZL-Khipu-Second-Brain-v1"
    assert sb.json()["ready_for_grounded_navigation"] in (True, False)


def test_council_ouroboros_and_invariants() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/council", json={
        "prompt": "Should we claim Lambda is a theorem?",
        "personas": ["Yupaq", "Amaru", "Willakuq"],
        "debate": False,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["ouroboros"]["terminating"] is True
    assert body["ouroboros"]["exit"] in ("consistent", "converged", "aborted", "budgetExhausted")
    assert body["invariants"]["count"] == 8
    assert body["invariants"]["ok"] is True
    assert body["rounds"][0]["organ"]


def test_ask_unknown_persona() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/ask", json={"persona": "NotASeat", "prompt": "hi"})
    assert res.status_code == 400
