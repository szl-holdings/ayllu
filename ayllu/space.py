"""Space entry. Same FastAPI app plus frontier HTTP.

Dockerfile CMD targets this module so SZLHOLDINGS/ayllu occupies
/cogitate /lattice /ruray /kutiy. AGI stays CONJECTURE. Presence stays CONJECTURE.
"""
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse

from app import app
from ayllu.production import contract
from ayllu.psyche.engine import PSYCHE
from ayllu.psyche.expose import cogitate_from, kutiy_from, lattice_from, ruray_from


def occupy_boot() -> dict[str, Any]:
    """One real five-organ beat at process start. Not a mock. Not AGI."""
    try:
        if PSYCHE.pulses < 1:
            PSYCHE.set_lock(True)
            PSYCHE.beat("boot occupy — five organs", seat="Maskaq")
        return ruray_from(PSYCHE)
    except Exception as exc:
        return {
            "schema": "szl.ayllu.ruray/v1",
            "name": "Ruray",
            "competence": "UNAVAILABLE",
            "occupancy": 0,
            "closed": False,
            "pulses": int(getattr(PSYCHE, "pulses", 0) or 0),
            "agi": "CONJECTURE",
            "presence": "CONJECTURE",
            "honesty": "UNAVAILABLE",
            "boot_error": type(exc).__name__,
            "note": "Boot occupy failed closed. HTTP still serves.",
        }


def _register_startup() -> None:
    """FastAPI 0.141 has no add_event_handler. Never die at import."""
    handler = getattr(app, "add_event_handler", None)
    if callable(handler):
        try:
            handler("startup", occupy_boot)
            return
        except Exception:
            pass
    on_event = getattr(app, "on_event", None)
    if callable(on_event):
        try:
            on_event("startup")(occupy_boot)
            return
        except Exception:
            pass
    occupy_boot()


@app.get("/api/v1/psyche/cogitate")
def psyche_cogitate() -> JSONResponse:
    return JSONResponse(cogitate_from(PSYCHE))


@app.get("/api/v1/psyche/lattice")
def psyche_lattice() -> JSONResponse:
    return JSONResponse(lattice_from(PSYCHE))


@app.get("/api/v1/psyche/ruray")
def psyche_ruray() -> JSONResponse:
    return JSONResponse(ruray_from(PSYCHE))


@app.get("/api/v1/psyche/kutiy")
def psyche_kutiy() -> JSONResponse:
    return JSONResponse(kutiy_from(PSYCHE))


@app.get("/api/v1/ayllu/production")
def production_contract() -> dict[str, Any]:
    body = contract()
    rur = ruray_from(PSYCHE)
    body["occupancy"] = rur.get("occupancy")
    body["ruray"] = rur.get("competence")
    body["pulses"] = rur.get("pulses")
    body["counsel"] = "operational"
    return body


@app.get("/livez")
def livez() -> dict[str, Any]:
    return {"live": True, "lambda": "CONJECTURE_1", "agi": "CONJECTURE"}


def _annotate_readyz() -> None:
    original = None
    for route in app.routes:
        endpoint = getattr(route, "endpoint", None)
        if getattr(endpoint, "__name__", "") == "readyz":
            original = endpoint
            break
    if original is None:
        return

    def readyz():
        body = original()
        if not isinstance(body, dict):
            return body
        rur = ruray_from(PSYCHE)
        body["occupancy"] = rur.get("occupancy")
        body["ruray"] = rur.get("competence")
        body["pulses"] = rur.get("pulses")
        body["agi"] = "CONJECTURE"
        body["presence"] = "CONJECTURE"
        body["production"] = "/api/v1/ayllu/production"
        return body

    readyz.__name__ = "readyz"
    for route in app.routes:
        if getattr(getattr(route, "endpoint", None), "__name__", "") == "readyz":
            route.endpoint = readyz
            break


def _annotate_manifest() -> None:
    """Keep GET /api/v1/ayllu/manifest honest about the live routes."""
    original = None
    for route in app.routes:
        endpoint = getattr(route, "endpoint", None)
        if getattr(endpoint, "__name__", "") == "manifest":
            original = endpoint
            break
    if original is None:
        return

    def manifest():
        body = original()
        psyche = body.get("psyche") if isinstance(body, dict) else None
        if isinstance(psyche, dict):
            psyche["cogitate"] = "/api/v1/psyche/cogitate"
            psyche["lattice"] = "/api/v1/psyche/lattice"
            psyche["ruray"] = "/api/v1/psyche/ruray"
            psyche["kutiy"] = "/api/v1/psyche/kutiy"
        if isinstance(body, dict):
            body["organ_grade"] = "PRODUCTION"
            body["legal_authority"] = "PROPOSAL_ONLY"
            body["production"] = "/api/v1/ayllu/production"
        return body

    manifest.__name__ = "manifest"
    for route in app.routes:
        if getattr(getattr(route, "endpoint", None), "__name__", "") == "manifest":
            route.endpoint = manifest
            break


_annotate_manifest()
_annotate_readyz()
_register_startup()
