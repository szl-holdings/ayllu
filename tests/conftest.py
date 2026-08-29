"""Put the sibling second-brain product on PYTHONPATH when present.

Append, never insert(0): second-brain also ships app.py, and putting it first
shadows Ayllu's FastAPI app so /api/v1/ayllu/* 404s.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SIB = Path(__file__).resolve().parents[2] / "second-brain"
# Ayllu root first so `from app import app` is this product.
_root = str(_ROOT)
if _root in sys.path:
    sys.path.remove(_root)
sys.path.insert(0, _root)
if _SIB.is_dir() and str(_SIB) not in sys.path:
    sys.path.append(str(_SIB))
