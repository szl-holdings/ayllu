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
    text = page.text
    assert "Ayllu" in text
    assert "holographic" in text.lower()
    for eid in ("organs", "sb", "hatun", "ouroboros", "invariants", "convene", "askone"):
        assert f'id="{eid}"' in text, eid
    for call in (
        'api("anatomy")',
        'api("second-brain")',
        'api("hatun")',
        'api("ouroboros")',
        'api("invariants")',
        'api("council")',
        'api("ask")',
    ):
        assert call in text, call
    assert "UNAVAILABLE" in text
    assert "three.js" not in text.lower()
    assert "cdn.jsdelivr" not in text.lower()
    assert "unpkg.com" not in text.lower()


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
    anatomy = a.json()
    assert len(anatomy["organs"]) == 5
    yachay = next(o for o in anatomy["organs"] if o["id"] == "yachay")
    assert "SZLHOLDINGS/second-brain" in yachay["space"]
    assert anatomy["yachay_space"].endswith("/second-brain")
    cat = c.get("/api/v1/ayllu/estate")
    assert cat.status_code == 200
    assert "Second Brain" in [x["name"] for x in cat.json()["consolidated"]]
    sb = c.get("/api/v1/ayllu/second-brain")
    assert sb.status_code == 200
    body = sb.json()
    assert body["system_id"] == "SZL-Khipu-Second-Brain-v1"
    assert body["ready_for_grounded_navigation"] in (True, False)
    mem = body["memory"]
    assert mem["built"] is True
    assert mem["chunk_count"] == 575
    assert mem["training_authority_rows"] == 0
    assert body["training_boundary"]["raw_brain_nodes_admitted_to_gradients"] == 0
    assert body["hard_boundaries"]["index_is_model_weights"] is False
    hat = c.get("/api/v1/ayllu/hatun")
    assert hat.status_code == 200
    assert hat.json()["schema"] == "szl.ayllu.hatun/v1"
    ouro = c.get("/api/v1/ayllu/ouroboros")
    assert ouro.status_code == 200
    assert ouro.json()["terminating"] is True
    inv = c.get("/api/v1/ayllu/invariants")
    assert inv.status_code == 200
    assert inv.json()["count"] == 8


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


def test_ouroboros_and_invariants_get_unavailable_without_receipt() -> None:
    c = TestClient(app)
    o = c.get("/api/v1/ayllu/ouroboros")
    assert o.status_code == 200
    body = o.json()
    assert body["kind"] == "SOFTWARE"
    assert body["last"] == "UNAVAILABLE"
    assert body["last_label"] == "UNAVAILABLE"
    assert body["exit"] == "UNAVAILABLE"
    assert body["lambda"] == "CONJECTURE_1"
    inv = c.get("/api/v1/ayllu/invariants")
    assert inv.status_code == 200
    catalog = inv.json()
    assert catalog["kind"] == "SOFTWARE"
    assert catalog["count"] == 8
    assert catalog["last"] == "UNAVAILABLE"
    assert catalog["ok"] is None
    assert len(catalog["catalog"]) == 8
