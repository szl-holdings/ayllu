"""Space entry. Same FastAPI app plus frontier HTTP.

Dockerfile CMD targets this module so SZLHOLDINGS/ayllu occupies
/cogitate /lattice /ruray. AGI stays CONJECTURE. Presence stays CONJECTURE.
"""
from __future__ import annotations

from fastapi.responses import JSONResponse

from app import app
from ayllu.psyche.engine import PSYCHE
from ayllu.psyche.expose import cogitate_from, lattice_from, ruray_from


@app.get("/api/v1/psyche/cogitate")
def psyche_cogitate() -> JSONResponse:
    return JSONResponse(cogitate_from(PSYCHE))


@app.get("/api/v1/psyche/lattice")
def psyche_lattice() -> JSONResponse:
    return JSONResponse(lattice_from(PSYCHE))


@app.get("/api/v1/psyche/ruray")
def psyche_ruray() -> JSONResponse:
    return JSONResponse(ruray_from(PSYCHE))


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
        return body

    manifest.__name__ = "manifest"
    for route in app.routes:
        if getattr(getattr(route, "endpoint", None), "__name__", "") == "manifest":
            route.endpoint = manifest
            break


_annotate_manifest()
