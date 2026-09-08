from ayllu.psyche.expose import ruray_from
from ayllu.psyche.rimanakuy import BODIES, EXPECTED, rimanakuy, score


def test_canonical_bodies_match_locked_contract() -> None:
    for name, vals in BODIES.items():
        got = score(vals)
        want = EXPECTED[name]
        assert got == want, (name, got, want)


def test_h_and_y_diverge_on_one_hot_versus_uniform() -> None:
    ran = rimanakuy()
    assert ran["schema"] == "szl.ayllu.cogitate/v1"
    assert ran["diverge"]["H_prefers"] == "uniform"
    assert ran["diverge"]["Y_prefers"] == "one_hot"
    assert ran["diverge"]["same_order"] is False
    assert ran["iit"]["phi_s"] is None
    assert ran["presence"]["honesty"] == "CONJECTURE"
    assert ran["cogitate"]["honesty"] == "RECORD"
    assert ran["cogitate"]["not_the_experiment"] is True
    assert "10.1038/s41586-025-08888-1" in ran["cogitate"]["reference"]
    assert ran["battery"]["silent"]["Q"] == 0.0
    assert ran["battery"]["one_hot"]["Y"] == 1.0
    assert ran["battery"]["uniform"]["H"] == 0.4


def test_ruray_does_not_upgrade_agi() -> None:
    from ayllu.psyche.engine import Psyche

    p = Psyche()
    before = ruray_from(p)
    assert before["agi"] == "CONJECTURE"
    assert before["presence"] == "CONJECTURE"
    assert before["competence"] == "UNAVAILABLE"
    p.set_lock(True)
    beat = p.beat("ruray competence", seat="Maskaq")
    after = ruray_from(p)
    assert after["agi"] == "CONJECTURE"
    assert after["presence"] == "CONJECTURE"
    assert beat["presence"]["label"] == "CONJECTURE"
    if after["occupancy"] == 5 and after["closed"]:
        assert after["competence"] == "MEASURED"


def test_cogitate_lattice_ruray_http_routes() -> None:
    from fastapi.testclient import TestClient

    from ayllu.space import app

    c = TestClient(app)
    cog = c.get("/api/v1/psyche/cogitate")
    assert cog.status_code == 200
    body = cog.json()
    assert body["schema"] == "szl.ayllu.cogitate/v1"
    assert body["name"] == "Rimanakuy"
    assert body["diverge"]["same_order"] is False
    assert body["cogitate"]["honesty"] == "RECORD"
    assert body["cogitate"]["not_the_experiment"] is True
    assert body["presence"]["label"] == "CONJECTURE"
    assert body["agi"]["label"] == "CONJECTURE"
    lat = c.get("/api/v1/psyche/lattice")
    assert lat.status_code == 200
    assert lat.json()["schema"] == "szl.ayllu.yupay/v1"
    assert lat.json()["honesty"] == "SOFTWARE"
    rur = c.get("/api/v1/psyche/ruray")
    assert rur.status_code == 200
    assert rur.json()["agi"] == "CONJECTURE"
    assert rur.json()["presence"] == "CONJECTURE"
    man = c.get("/api/v1/ayllu/manifest")
    assert man.status_code == 200
    psyche = man.json()["psyche"]
    assert psyche["cogitate"] == "/api/v1/psyche/cogitate"
    assert psyche["lattice"] == "/api/v1/psyche/lattice"
    assert psyche["ruray"] == "/api/v1/psyche/ruray"
    page = c.get("/psyche")
    assert page.status_code == 200
