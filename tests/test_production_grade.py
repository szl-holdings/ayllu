import os

os.environ["AYLLU_FORCE_SOFTWARE"] = "1"

from fastapi.testclient import TestClient

from app import app
from ayllu.production import contract


def test_production_contract_does_not_upgrade_authority_or_agi() -> None:
    body = contract()
    assert body["runtime"] == "OPERATIONAL"
    assert body["grade"] == "PRODUCTION"
    assert body["legal_authority"] == "PROPOSAL_ONLY"
    assert body["filing"] is False
    assert body["agi"] == "CONJECTURE"
    assert body["presence"] == "CONJECTURE"
    assert body["phi_s"] == "UNAVAILABLE"
    assert body["joules"] is None


def test_health_and_manifest_keep_operational_counsel() -> None:
    c = TestClient(app)
    health = c.get("/health").json()
    assert health["ok"] is True
    assert health["counsel"] == "operational"
    assert health["psyche"] == "operational"
    assert health["lambda"] == "CONJECTURE_1"
    manifest = c.get("/api/v1/ayllu/manifest").json()
    assert manifest["authority"] == "PROPOSAL_ONLY"
    assert manifest["lambda"]["never_a_theorem"] is True


def test_counsel_surfaces_are_wired() -> None:
    c = TestClient(app)
    assert c.get("/counsel").status_code == 200
    assert c.get("/api/v1/counsel/allodial").status_code == 200
    infer = c.post(
        "/api/v1/counsel/infer",
        json={
            "action": "policy",
            "prompt": "Production policy scan without licensed-counsel impersonation.",
            "human_lock": True,
        },
    )
    assert infer.status_code == 200
    body = infer.json()
    assert body["blocked"] is False
    assert body["receipt"]["honesty_tier"] == "MEASURED"
