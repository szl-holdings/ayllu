"""Living anatomy instilled into Ayllu.

Five systems from szl-holdings/anatomy — HEART/YUYAY, YAWAR, YACHAY,
NERVOUS, SKELETON — mapped onto council seats. This is SOFTWARE anatomy,
not a claim that the 3D Space is embedded. Λ stays Conjecture 1.
"""
from __future__ import annotations

from typing import Any

# Anatomy README: HEART · YUYAY, CIRCULATORY · YAWAR, BRAIN · YACHAY,
# NERVOUS · OTel, SKELETON · Khipu. Formula map F1→BRAIN, F4+F11→HEART, …
ORGANS = (
    {
        "id": "yuyay",
        "name": "HEART / YUYAY",
        "role": "trust gate — 13-axis conjunctive critique",
        "formula": "F4+F11",
        "seats": ["Yupaq", "Qhaway"],
        "color": "#ff7a9c",
    },
    {
        "id": "yawar",
        "name": "CIRCULATORY / YAWAR",
        "role": "append-only receipt bus",
        "formula": "F7+F22",
        "seats": ["Willakuq"],
        "color": "#e8c074",
    },
    {
        "id": "yachay",
        "name": "BRAIN / YACHAY",
        "role": "read-only reasoning cortex — second brain retrieval",
        "formula": "F1",
        "seats": ["Amaru", "Maskaq"],
        "color": "#3af4c8",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/second-brain",
        "github": "https://github.com/szl-holdings/szl-second-brain",
        "note": (
            "YACHAY points at the public Second Brain Space: SOFTWARE handles-only "
            "retrieval over 575 chunks. Not a Three.js rewrite of anatomy. "
            "Private 9464-node graph is not admitted. Λ = Conjecture 1."
        ),
    },
    {
        "id": "nervous",
        "name": "NERVOUS / OTel",
        "role": "observability and organ health",
        "formula": "F12",
        "seats": ["Hampiq", "Yanapaq"],
        "color": "#7ad7ff",
    },
    {
        "id": "skeleton",
        "name": "SKELETON / Khipu",
        "role": "orchestration spine — bounded loop",
        "formula": "F18+F19",
        "seats": ["Kamachiq", "Chaka", "Ruwaq", "Qhatuq"],
        "color": "#c9d6e2",
    },
)


def organ_for_persona(name: str) -> dict[str, Any] | None:
    key = (name or "").strip().lower()
    for organ in ORGANS:
        if any(s.lower() == key for s in organ["seats"]):
            return organ
    return None


def anatomy() -> dict[str, Any]:
    return {
        "schema": "szl.ayllu.anatomy/v1",
        "source": "https://github.com/szl-holdings/anatomy",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/anatomy",
        "kernel": "https://github.com/szl-holdings/szl-khipu",
        "organs": list(ORGANS),
        "locked_eight": ["F1", "F4", "F7", "F11", "F12", "F18", "F19", "F22"],
        "lambda": "CONJECTURE_1",
        "khipu_bft": "CONJECTURE_2",
        "yachay_space": "https://huggingface.co/spaces/SZLHOLDINGS/second-brain",
        "honesty": (
            "SOFTWARE organ map instilled into Ayllu. Not the 3D Anatomy Space. "
            "Not a claim that organs are LIVE GPUs. YACHAY notes the Second Brain "
            "Space; that hologram is handles-only SOFTWARE retrieval."
        ),
    }
