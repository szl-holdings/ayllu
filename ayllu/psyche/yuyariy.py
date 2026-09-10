"""Yuyariy — observation log over Khipu receipts.

Studied from the public claim that raw turn history should compress
into observations rather than being replayed verbatim. Original SZL
software. No third-party TypeScript. No knowledge graph.

Honesty: SOFTWARE memory. AGI CONJECTURE. Presence CONJECTURE.
"""
from __future__ import annotations

from typing import Any

SCHEMA = "szl.ayllu.yuyariy/v1"
STUDIED = (
    "Public observational-compression claim (text observations, not a KG). "
    "Original SZL code. Not Mastra source. Not Project Astra memory."
)


def _scalar(block: Any, key: str) -> float | None:
    if not isinstance(block, dict):
        return None
    raw = block.get(key)
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def yuyariy(psyche: Any) -> dict[str, Any]:
    win = getattr(psyche, "last_winay", None) or {}
    pulses = int(getattr(psyche, "pulses", 0) or 0)
    closure = win.get("closure") or {}
    occupancy = int(closure.get("occupancy") or 0)
    closed = bool(closure.get("value"))
    h = _scalar(win.get("huklla"), "H")
    q = _scalar(win.get("qhaway"), "Q")
    y = _scalar(win.get("riqsiy"), "Y")
    observations: list[str] = []
    if pulses < 1:
        observations.append("No beat this process. Observation log empty.")
    else:
        observations.append(
            f"Pulse {pulses}: occupancy {occupancy}/5, "
            f"{'closed' if closed else 'open'} cycle."
        )
        if h is not None:
            observations.append(f"Huklla H={h:.3f} MODELED cheapest pentagon cut. Not Φ.")
        if q is not None:
            observations.append(f"Qhaway Q={q:.3f} MODELED load-gated LZ. Not PCI.")
        if y is not None:
            observations.append(f"Riqsiy Υ={y:.3f} MODELED spotlight. Not AST/HOT.")
        observations.append("Joules null. φ_s UNAVAILABLE. Presence CONJECTURE.")
        if closed and occupancy == 5:
            observations.append("Ruray competence MEASURED. Competence is not AGI.")
        else:
            observations.append("Ruray competence UNAVAILABLE until occupancy-5 closed beat.")
    return {
        "schema": SCHEMA,
        "name": "Yuyariy",
        "honesty": "SOFTWARE",
        "observations": observations,
        "count": len(observations),
        "pulses": pulses,
        "occupancy": occupancy,
        "closed": closed,
        "studied": STUDIED,
        "copied": False,
        "not": ["Mastra-source", "Project-Astra-memory", "multimodal-presence", "AGI"],
        "agi": "CONJECTURE",
        "presence": "CONJECTURE",
        "note": "Compressed beat receipt. SOFTWARE memory. Not a mind.",
    }
