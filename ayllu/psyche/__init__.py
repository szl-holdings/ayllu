"""Ayllu Psyche — neural-symbolic living architecture.

Yuyay (associative memory) · Tinku (fail-closed morphisms) · Khipu (typed hypergraph)
· Human Lock (alignment) · eleven seats as typed arrows · Kawsay (five-organ pulse).

Stdlib only. Joules stay None. Λ = Conjecture 1.
Presence and AGI stay CONJECTURE.
"""
from __future__ import annotations

from ayllu.psyche.engine import PSYCHE, Psyche
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.kawsay import beat, couple, order_parameter, sense
from ayllu.psyche.morphisms import Morphism, compose, identity, run_pipeline
from ayllu.psyche.neural import Yuyay, encode, hebb_oja, hopfield_classic, hopfield_softmax
from ayllu.psyche.types import ENERGY, LAMBDA, SCHEMA, Bundle, Honesty
from ayllu.psyche.winay import couple_fixed, evaluate as winay_evaluate, huklla, imaymana, metabolize

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
    "beat",
    "sense",
    "couple",
    "order_parameter",
    "couple_fixed",
    "metabolize",
    "huklla",
    "imaymana",
    "winay_evaluate",
    "ENERGY",
    "LAMBDA",
    "SCHEMA",
]
