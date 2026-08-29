import os

os.environ["AYLLU_FORCE_SOFTWARE"] = "1"

from fastapi.testclient import TestClient

from app import app
from ayllu.second_brain import navigator_context, rag_status, retrieve


def test_retrieve_api_handles_only() -> None:
    c = TestClient(app)
    res = c.get("/api/v1/ayllu/retrieve", params={"q": "Lambda uniqueness conjecture 1", "k": 5})
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "SOFTWARE"
    assert body["content_access"] == "HANDLES_ONLY"
    assert body["ready"] is True
    assert body["handles"]
    assert body["raw_graph_nodes_admitted_to_gradients"] == 0
    for h in body["handles"]:
        assert "text" not in h
        assert "_toks" not in h
        assert h["nodeId"]
    honesty = (body.get("honesty") or "").lower()
    assert body["kind"] != "LIVE"
    assert "software" in honesty or "not live" in honesty or "never" in honesty


def test_maskaq_ask_attaches_handles() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/ask", json={
        "persona": "Maskaq",
        "prompt": "Lambda uniqueness conjecture",
    })
    assert res.status_code == 200
    body = res.json()
    turn = body["turn"]
    grounding = turn.get("grounding") or {}
    assert grounding.get("content_access") == "HANDLES_ONLY"
    assert grounding.get("kind") == "SOFTWARE"
    assert grounding.get("ready") is True
    assert grounding.get("handles")
    for h in grounding["handles"]:
        assert "text" not in h
        assert set(h) <= {"nodeId", "nodeKind", "label", "note"}
    blob = ((turn.get("answer") or "") + (turn.get("honesty") or "")).lower()
    assert "software" in blob
    assert turn.get("stub") is True
    assert grounding.get("kind") != "LIVE"


def test_maskaq_abstains_when_ungrounded() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/ask", json={
        "persona": "Maskaq",
        "prompt": "zzqxymplughq",
    })
    assert res.status_code == 200
    turn = res.json()["turn"]
    grounding = turn.get("grounding") or {}
    assert grounding.get("ready") is False
    assert grounding.get("handles") == []
    assert "ABSTAIN" in (turn.get("answer") or "").upper()
    honesty = (turn.get("honesty") or "").lower()
    assert "live" not in honesty or "never live" in honesty


def test_council_maskaq_grounding() -> None:
    c = TestClient(app)
    res = c.post("/api/v1/ayllu/council", json={
        "prompt": "Lambda uniqueness conjecture",
        "personas": ["Maskaq", "Yupaq"],
        "debate": False,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["ouroboros"]["terminating"] is True
    assert body["invariants"]["ok"] is True
    maskaq = next(r for r in body["rounds"] if r["persona"] == "Maskaq")
    grounding = maskaq.get("grounding") or {}
    assert grounding.get("content_access") == "HANDLES_ONLY"
    assert grounding.get("kind") == "SOFTWARE"


def test_rag_status_public_projection() -> None:
    st = rag_status()
    assert st["built"] is True
    assert st["chunk_count"] == 575
    assert st["training_authority_rows"] == 0
    hit = retrieve("Khipu receipt", k=3)
    assert hit["ready"] is True
    ctx = navigator_context("ouroboros loop", k=3)
    assert ctx["content_access"] == "HANDLES_ONLY"
    assert ctx["kind"] == "SOFTWARE"
