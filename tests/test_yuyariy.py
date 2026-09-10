from fastapi.testclient import TestClient

from ayllu.psyche.engine import Psyche
from ayllu.psyche.expose import yuyariy_from
from ayllu.psyche.yuyariy import yuyariy
from ayllu.space import occupy_boot


def test_yuyariy_empty_until_beat_then_compresses() -> None:
    p = Psyche()
    empty = yuyariy(p)
    assert empty["schema"] == "szl.ayllu.yuyariy/v1"
    assert empty["honesty"] == "SOFTWARE"
    assert empty["agi"] == "CONJECTURE"
    assert empty["presence"] == "CONJECTURE"
    assert empty["copied"] is False
    assert empty["count"] >= 1
    assert "No beat" in empty["observations"][0]
    p.set_lock(True)
    p.beat("yuyariy observation", seat="Maskaq")
    filled = yuyariy_from(p)
    assert filled["pulses"] >= 1
    assert filled["agi"] == "CONJECTURE"
    assert any("Pulse" in line for line in filled["observations"])
    assert "Mastra-source" in filled["not"]


def test_yuyariy_http_route() -> None:
    occupy_boot()
    from ayllu.space import app

    c = TestClient(app)
    y = c.get("/api/v1/psyche/yuyariy")
    assert y.status_code == 200
    body = y.json()
    assert body["schema"] == "szl.ayllu.yuyariy/v1"
    assert body["honesty"] == "SOFTWARE"
    assert body["agi"] == "CONJECTURE"
    assert body["copied"] is False
    man = c.get("/api/v1/ayllu/manifest")
    assert man.status_code == 200
    psyche = man.json()["psyche"]
    assert psyche["yuyariy"] == "/api/v1/psyche/yuyariy"
    ready = c.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["agi"] == "CONJECTURE"
