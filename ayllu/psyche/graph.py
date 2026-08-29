"""Typed hypergraph of seats, organs, and engrams.

Vertices carry a type and an honesty label.
Hyperedges are organs (seats they span) and khipu chains (engrams they bind).
Incidence is SOFTWARE topology, not a claim of LIVE GPUs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ayllu.organs import ORGANS
from ayllu.personas import ROSTER
from ayllu.psyche.types import ENERGY, Honesty, LAMBDA, SCHEMA


@dataclass
class Vertex:
    id: str
    kind: str  # seat | organ | engram
    label: str
    honesty: Honesty
    remit: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "honesty": self.honesty.value,
            "remit": self.remit,
            "data": self.data,
        }


@dataclass
class Hyperedge:
    id: str
    kind: str  # organ | khipu | tinku
    incident: tuple[str, ...]
    honesty: Honesty
    label: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "incident": list(self.incident),
            "honesty": self.honesty.value,
            "label": self.label,
        }


class TypedHypergraph:
    def __init__(self) -> None:
        self.vertices: dict[str, Vertex] = {}
        self.edges: dict[str, Hyperedge] = {}
        self._seed()

    def _seed(self) -> None:
        for p in ROSTER:
            self.add_vertex(Vertex(
                id=f"seat:{p.name}",
                kind="seat",
                label=p.name,
                honesty=Honesty.MEASURED,
                remit=p.domain,
                data={"quechua": p.quechua, "archetype": p.archetype},
            ))
        for organ in ORGANS:
            vids = tuple(f"seat:{s}" for s in organ["seats"])
            self.add_vertex(Vertex(
                id=f"organ:{organ['id']}",
                kind="organ",
                label=organ["name"],
                honesty=Honesty.SOFTWARE,
                remit=organ["role"],
                data={"formula": organ.get("formula"), "color": organ.get("color")},
            ))
            self.add_edge(Hyperedge(
                id=f"hedge:{organ['id']}",
                kind="organ",
                incident=vids + (f"organ:{organ['id']}",),
                honesty=Honesty.SOFTWARE,
                label=organ["name"],
            ))
        self.add_edge(Hyperedge(
            id="hedge:tinku",
            kind="tinku",
            incident=tuple(f"organ:{o['id']}" for o in ORGANS),
            honesty=Honesty.MODELED,
            label="Tinku composition",
        ))

    def add_vertex(self, v: Vertex) -> None:
        self.vertices[v.id] = v

    def add_edge(self, e: Hyperedge) -> None:
        self.edges[e.id] = e

    def add_engram(self, eid: str, text: str, source: str, honesty: Honesty, prev: str) -> None:
        vid = f"engram:{eid}"
        self.add_vertex(Vertex(
            id=vid,
            kind="engram",
            label=text[:72],
            honesty=honesty,
            remit=source,
            data={"source": source, "prev": prev},
        ))
        chain_ids = [v.id for v in self.vertices.values() if v.kind == "engram"]
        self.add_edge(Hyperedge(
            id="hedge:khipu",
            kind="khipu",
            incident=tuple(chain_ids),
            honesty=Honesty.MEASURED,
            label="khipu chain",
        ))

    def drop_engrams(self) -> None:
        drop = [vid for vid, v in self.vertices.items() if v.kind == "engram"]
        for vid in drop:
            self.vertices.pop(vid, None)
        self.edges.pop("hedge:khipu", None)

    def neighbors(self, vid: str) -> list[str]:
        out: set[str] = set()
        for e in self.edges.values():
            if vid in e.incident:
                out.update(e.incident)
        out.discard(vid)
        return sorted(out)

    def incidence(self) -> dict[str, list[str]]:
        table: dict[str, list[str]] = {vid: [] for vid in self.vertices}
        for e in self.edges.values():
            for vid in e.incident:
                if vid in table:
                    table[vid].append(e.id)
        return table

    def snapshot(self) -> dict[str, Any]:
        seats = sum(1 for v in self.vertices.values() if v.kind == "seat")
        organs = sum(1 for v in self.vertices.values() if v.kind == "organ")
        engrams = sum(1 for v in self.vertices.values() if v.kind == "engram")
        return {
            "schema": SCHEMA,
            "vertices": [v.as_dict() for v in self.vertices.values()],
            "edges": [e.as_dict() for e in self.edges.values()],
            "counts": {
                "seats": seats,
                "organs": organs,
                "engrams": engrams,
                "edges": len(self.edges),
            },
            "incidence": self.incidence(),
            "honesty": Honesty.MEASURED.value if seats == 11 else Honesty.UNAVAILABLE.value,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }


def seed_graph() -> TypedHypergraph:
    return TypedHypergraph()
