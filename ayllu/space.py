"""Space entry. Same FastAPI app plus frontier HTTP.

Dockerfile CMD targets this module so SZLHOLDINGS/ayllu occupies
/cogitate /lattice /ruray /kutiy /yuyariy /ship /eval.
AGI stays CONJECTURE. Presence stays CONJECTURE.
"""
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse, RedirectResponse

from app import app
from ayllu.production import contract
from ayllu.psyche.engine import PSYCHE
from ayllu.psyche.expose import (
    cogitate_from,
    counsel_eval_from,
    kutiy_from,
    lattice_from,
    ruray_from,
    ship_from,
    yuyariy_from,
)


def occupy_boot() -> dict[str, Any]:
    """One real five-organ beat at process start. Not a mock. Not AGI."""
    try:
        from ayllu.psyche.bind import install

        install(PSYCHE)
        if PSYCHE.pulses < 1:
            PSYCHE.beat("boot occupy \u2014 five organs", seat="Maskaq")
        return ruray_from(PSYCHE)
    except Exception as exc:  # noqa: BLE001 — boot must stay up
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


@app.get("/api/v1/psyche/yuyariy")
def psyche_yuyariy() -> JSONResponse:
    return JSONResponse(yuyariy_from(PSYCHE))


@app.get("/api/v1/psyche/ship")
def psyche_ship() -> JSONResponse:
    return JSONResponse(ship_from())


@app.get("/api/v1/counsel/eval")
def counsel_eval() -> JSONResponse:
    return JSONResponse(counsel_eval_from())


@app.get("/counsel/")
def slash_counsel() -> RedirectResponse:
    return RedirectResponse("/counsel", status_code=307)


@app.get("/psyche/")
def slash_psyche() -> RedirectResponse:
    return RedirectResponse("/psyche", status_code=307)


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


def _rebind(name: str, wrapper) -> None:
    """FastAPI serves dependant.call, not only route.endpoint."""
    wrapper.__name__ = name
    for route in app.routes:
        endpoint = getattr(route, "endpoint", None)
        if getattr(endpoint, "__name__", "") != name:
            continue
        route.endpoint = wrapper
        dependant = getattr(route, "dependant", None)
        if dependant is not None:
            dependant.call = wrapper
        break


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
        gate = ship_from()
        body["occupancy"] = rur.get("occupancy")
        body["ruray"] = rur.get("competence")
        body["pulses"] = rur.get("pulses")
        body["agi"] = "CONJECTURE"
        body["presence"] = "CONJECTURE"
        body["production"] = "/api/v1/ayllu/production"
        passed = gate.get("pass", gate.get("ready"))
        body["ship"] = passed
        yuy = getattr(PSYCHE, "last_yuyariy", None) or {}
        body["yuyariy"] = int(yuy.get("count") or 0)
        if passed is False:
            body["ready"] = False
        return body

    _rebind("readyz", readyz)


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
            psyche["yuyariy"] = "/api/v1/psyche/yuyariy"
            psyche["ship"] = "/api/v1/psyche/ship"
            psyche["counsel_eval"] = "/api/v1/counsel/eval"
        if isinstance(body, dict):
            body["organ_grade"] = "PRODUCTION"
            body["legal_authority"] = "PROPOSAL_ONLY"
            body["production"] = "/api/v1/ayllu/production"
        return body

    _rebind("manifest", manifest)


_annotate_manifest()
_annotate_readyz()
_register_startup()
BOOT_RECEIPT = occupy_boot()
