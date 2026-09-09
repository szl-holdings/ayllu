from ayllu.psyche.engine import Psyche
from ayllu.psyche.expose import ruray_from
from ayllu.space import occupy_boot
from ayllu.psyche.engine import PSYCHE

from fastapi.testclient import TestClient

from ayllu.space import app


def test_occupy_boot_measures_competence_without_upgrading_agi() -> None:
    occupy_boot()
    rur = ruray_from(PSYCHE)
    assert PSYCHE.pulses >= 1
    assert rur["agi"] == "CONJECTURE"
    assert rur["presence"] == "CONJECTURE"
    if rur["occupancy"] == 5 and rur["closed"]:
        assert rur["competence"] == "MEASURED"


def test_fresh_psyche_still_unavailable_until_beat() -> None:
    p = Psyche()
    rur = ruray_from(p)
    assert rur["competence"] == "UNAVAILABLE"
    assert rur["agi"] == "CONJECTURE"


def test_production_and_livez_http() -> None:
    occupy_boot()
    c = TestClient(app)
    prod = c.get("/api/v1/ayllu/production")
    assert prod.status_code == 200
    body = prod.json()
    assert body["runtime"] == "OPERATIONAL"
    assert body["grade"] == "PRODUCTION"
    assert body["legal_authority"] == "PROPOSAL_ONLY"
    assert body["agi"] == "CONJECTURE"
    assert body["presence"] == "CONJECTURE"
    assert body["phi_s"] == "UNAVAILABLE"
    assert body["counsel"] == "operational"
    live = c.get("/livez")
    assert live.status_code == 200
    assert live.json()["agi"] == "CONJECTURE"
    ready = c.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["agi"] == "CONJECTURE"
    assert ready.json()["presence"] == "CONJECTURE"
    man = c.get("/api/v1/ayllu/manifest")
    assert man.status_code == 200
    assert man.json()["organ_grade"] == "PRODUCTION"
    assert man.json()["legal_authority"] == "PROPOSAL_ONLY"
