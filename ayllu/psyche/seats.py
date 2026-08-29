"""Eleven seats as typed morphisms.

Each seat is a remit-typed arrow on one routed backend.
Not eleven separately trained models. Souls remain in ayllu.personas.
"""
from __future__ import annotations

from typing import Any

from ayllu.personas import ROSTER, Persona
from ayllu.psyche.morphisms import Morphism
from ayllu.psyche.types import Bundle, Honesty, Kind

SEAT_ORGANS = {
    "Yupaq": "yuyay",
    "Qhaway": "yuyay",
    "Willakuq": "yawar",
    "Amaru": "yachay",
    "Maskaq": "yachay",
    "Hampiq": "nervous",
    "Yanapaq": "nervous",
    "Kamachiq": "skeleton",
    "Chaka": "skeleton",
    "Ruwaq": "skeleton",
    "Qhatuq": "skeleton",
}


def _speak(persona: Persona) -> Morphism:
    def fn(bundle: Bundle, ctx) -> Bundle:
        text = ""
        payload = bundle.payload
        if isinstance(payload, dict):
            text = str(payload.get("text") or payload.get("cue") or "")
        elif isinstance(payload, str):
            text = payload
        note = (
            f"{persona.name} ({persona.archetype}) speaks from {persona.domain}. "
            f"Cue clipped to remit. Authority PROPOSAL_ONLY."
        )
        return Bundle(
            payload={
                "seat": persona.name,
                "quechua": persona.quechua,
                "archetype": persona.archetype,
                "organ": SEAT_ORGANS.get(persona.name),
                "cue": text[:400],
                "note": note,
            },
            honesty=Honesty.SOFTWARE,
            kind=Kind.SOFTWARE,
            remit=persona.name,
            notes=(note,),
        )

    return Morphism(
        name=f"seat:{persona.name}",
        domain="cue",
        codomain="utterance",
        honesty_floor=Honesty.UNAVAILABLE,
        state_changing=False,
        lock_required=False,
        remit=persona.name,
        fn=fn,
    )


SEAT_MORPHISMS: dict[str, Morphism] = {p.name: _speak(p) for p in ROSTER}


def seat_morphism(name: str) -> Morphism | None:
    key = (name or "").strip()
    if key in SEAT_MORPHISMS:
        return SEAT_MORPHISMS[key]
    lower = key.lower()
    for p in ROSTER:
        if p.name.lower() == lower:
            return SEAT_MORPHISMS[p.name]
    return None


def roster_typed() -> list[dict[str, Any]]:
    return [
        {
            **p.metadata(),
            "organ": SEAT_ORGANS.get(p.name),
            "morphism": SEAT_MORPHISMS[p.name].name,
            "domain": "cue",
            "codomain": "utterance",
        }
        for p in ROSTER
    ]
