"""Ayllu controller binding to the public second-brain projection.

Prefers `second_brain.retrieve` (sibling product on PYTHONPATH /
AYLLU_SECOND_BRAIN_ROOT). If that package is absent, loads the vendored
public corpus with the same SOFTWARE BM25 ranker.

Never admits the private 9464-node graph. Handles only. Never LIVE retrieval.
Λ = Conjecture 1.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_AYLLU_ROOT = Path(__file__).resolve().parent.parent
_VENDORED_CORPUS = _AYLLU_ROOT / "data" / "brain-corpus.public.jsonl"
_VENDORED_RETRIEVE = Path(__file__).resolve().parent / "vendor_retrieve.py"


def _roots() -> list[Path]:
    env = (os.environ.get("AYLLU_SECOND_BRAIN_ROOT") or os.environ.get("SECOND_BRAIN_ROOT") or "").strip()
    here = Path(__file__).resolve()
    out: list[Path] = []
    if env:
        out.append(Path(env))
    out.extend([
        here.parents[2] / "second-brain",
        here.parents[1] / "second-brain",
        Path("/app/second-brain"),
        here.parents[2] / "szl-second-brain",
    ])
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        key = str(p.resolve()) if p.exists() else str(p)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def bootstrap_pythonpath() -> Path | None:
    """Put the sibling second-brain product on sys.path when present."""
    for root in _roots():
        retrieve_py = root / "second_brain" / "retrieve.py"
        if retrieve_py.is_file():
            s = str(root)
            if s not in sys.path:
                sys.path.insert(0, s)
            return root
    return None


def _load_module() -> ModuleType | None:
    bootstrap_pythonpath()
    try:
        import importlib
        return importlib.import_module("second_brain.retrieve")
    except Exception:
        pass
    for root in _roots():
        retrieve_py = root / "second_brain" / "retrieve.py"
        if not retrieve_py.is_file():
            continue
        spec = importlib.util.spec_from_file_location("szl_second_brain_retrieve", retrieve_py)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            return mod
        except Exception:
            continue
    if _VENDORED_RETRIEVE.is_file():
        spec = importlib.util.spec_from_file_location(
            "ayllu.vendor_retrieve", _VENDORED_RETRIEVE
        )
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                return mod
            except Exception:
                pass
    return None


def _corpus_file() -> Path | None:
    env = (os.environ.get("AYLLU_BRAIN_CORPUS") or os.environ.get("SECOND_BRAIN_CORPUS") or "").strip()
    candidates = [Path(env)] if env else []
    for root in _roots():
        candidates.append(root / "data" / "brain-corpus.public.jsonl")
    candidates.append(_VENDORED_CORPUS)
    for p in candidates:
        if p.is_file():
            return p
    return None


_IDX = None


def _index():
    global _IDX
    if _IDX is not None:
        return _IDX
    mod = _load_module()
    if mod is None:
        return None
    path = _corpus_file()
    getter = getattr(mod, "index", None)
    cls = getattr(mod, "SecondBrainIndex", None)
    try:
        if path is not None and cls is not None:
            _IDX = cls(path)
        elif callable(getter):
            _IDX = getter()
        elif cls is not None:
            _IDX = cls()
        else:
            return None
    except Exception:
        return None
    return _IDX


def rag_status() -> dict[str, Any]:
    idx = _index()
    if idx is None:
        return {
            "built": False,
            "state": "UNAVAILABLE",
            "chunk_count": 0,
            "chunks": 0,
            "document_count": 0,
            "corpus_chunk_count": 0,
            "brain_handle_count": 0,
            "training_authority_rows": 0,
            "raw_graph_nodes_admitted_to_gradients": 0,
            "mode": "SOFTWARE_BM25",
            "kind": "SOFTWARE",
            "integrity_state": "UNAVAILABLE",
            "honesty": (
                "Public second-brain corpus not on PYTHONPATH and not vendored. "
                "No LIVE retrieval fabricated. Private 9464-node graph is not here."
            ),
        }
    return idx.rag_status()


def retrieve(query: str, k: int = 6) -> dict[str, Any]:
    idx = _index()
    if idx is None:
        return {
            "schema": "szl.second-brain.retrieve/v1",
            "query": query,
            "handles": [],
            "ready": False,
            "kind": "SOFTWARE",
            "content_access": "HANDLES_ONLY",
            "honesty": (
                "Index UNAVAILABLE. No LIVE retrieval fabricated. "
                "Private 9464-node graph is not here."
            ),
        }
    return idx.search(query, k=k)


def navigator_context(query: str, k: int = 6) -> dict[str, Any]:
    idx = _index()
    if idx is None:
        return {
            "schema": "szl.brain.navigator-context/v1",
            "state": "ABSTAIN_NO_GROUNDED_HANDLES",
            "ready": False,
            "content_access": "HANDLES_ONLY",
            "handles": [],
            "evidence": [],
            "grounded_count": 0,
            "kind": "SOFTWARE",
            "honesty": (
                "Index UNAVAILABLE. Maskaq abstains. No LIVE retrieval fabricated."
            ),
        }
    return idx.navigator_context(query, k=k)


def is_maskaq(persona: str | None) -> bool:
    return (persona or "").strip().lower() == "maskaq"
