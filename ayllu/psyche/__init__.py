"""Ayllu Psyche — neural-symbolic living architecture.

Yuyay (associative memory) · Tinku (fail-closed morphisms) · Khipu (typed hypergraph)
· Human Lock (alignment) · eleven seats as typed arrows.

Stdlib only. Joules stay None. Λ = Conjecture 1.
"""
from __future__ import annotations

from ayllu.psyche.engine import PSYCHE, Psyche
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.morphisms import Morphism, compose, identity, run_pipeline
from ayllu.psyche.neural import Yuyay, encode, hebb_oja, hopfield_classic, hopfield_softmax
from ayllu.psyche.types import ENERGY, LAMBDA, SCHEMA, Bundle, Honesty

__all__ = [
    "PSYCHE",
    "Psyche",
    "Yuyay",
    "HumanLock",
    "Morphism",
    "Bundle",
    "Honesty",
    "compose",
    "identity",
    "run_pipeline",
    "encode",
    "hebb_oja",
    "hopfield_classic",
    "hopfield_softmax",
    "ENERGY",
    "LAMBDA",
    "SCHEMA",
]
