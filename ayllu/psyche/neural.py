"""Yuyay neural substrate.

Stdlib-only associative memory. Dual recall (classical Hopfield + softmax).
Writes are leak-bounded Hebb+Oja, honesty-weighted, with BCM homeostasis.
Replay uses reverse-Hebb on spurious attractors.

Joules stay None. Capacity α vs 0.138 is MODELED, not a proof.
Λ uniqueness is Conjecture 1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from ayllu.psyche.types import ENERGY, ETA_GAIN, Honesty, LAMBDA, meet

DIM = 64
SPARSE_K = 12
ETA = 0.08
DECAY = 0.012
BETA = 8.0
CLASSICAL_ALPHA = 0.138
BCM_TAU = 0.05
FRO_BOUND_SCALE = 1.0


def zero_w(dim: int = DIM) -> list[float]:
    return [0.0] * (dim * dim)


def _fnv(text: str) -> int:
    seed = 2166136261
    for ch in text:
        seed ^= ord(ch)
        seed = (seed * 16777619) & 0xFFFFFFFF
    return seed


def encode(text: str, dim: int = DIM, k: int = SPARSE_K) -> list[int]:
    """Dense bipolar pattern. Deterministic FNV-1a seed. MEASURED encoding.

    k is retained for the sparse probe generator; stored engrams are dense ±1
    so classical Hopfield overlap and α-capacity are well-defined.
    """
    v = [0] * dim
    s = (text or "").strip().lower()
    seed = _fnv(s)

    def rnd() -> int:
        nonlocal seed
        seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
        return seed

    for i in range(dim):
        v[i] = 1 if (rnd() % 2 == 0) else -1
    return v


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    n = min(len(a), len(b))
    return sum(a[i] * b[i] for i in range(n))


def overlap(a: Sequence[float], b: Sequence[float]) -> float:
    n = min(len(a), len(b)) or 1
    return round(dot(a, b) / n, 4)


def frobenius(W: Sequence[float]) -> float:
    return math.sqrt(sum(w * w for w in W))


def _clip_fro(W: list[float], dim: int = DIM) -> list[float]:
    bound = dim * FRO_BOUND_SCALE
    nrm = frobenius(W)
    if nrm > bound and nrm > 0:
        scale = bound / nrm
        return [w * scale for w in W]
    return W


def hebb_oja(
    W: Sequence[float],
    x: Sequence[float],
    *,
    dim: int = DIM,
    eta: float = ETA,
    decay: float = DECAY,
    honesty: Honesty = Honesty.MEASURED,
) -> list[float]:
    """Outer-product Hebb with leak, zero diagonal, Frobenius bound.

    Gain is honesty-weighted. UNAVAILABLE writes the identity (no change).
    """
    gain = ETA_GAIN[Honesty(honesty)]
    if gain <= 0:
        return list(W)
    step = eta * gain
    out = list(W)
    for i in range(dim):
        xi = x[i]
        row = i * dim
        for j in range(dim):
            if i == j:
                out[row + j] = 0.0
                continue
            out[row + j] = (1.0 - decay) * out[row + j] + step * xi * x[j]
    return _clip_fro(out, dim)


def reverse_hebb(
    W: Sequence[float],
    x: Sequence[float],
    *,
    dim: int = DIM,
    eta: float = 0.045,
) -> list[float]:
    out = list(W)
    for i in range(dim):
        xi = x[i]
        row = i * dim
        for j in range(dim):
            if i == j:
                out[row + j] = 0.0
                continue
            out[row + j] = out[row + j] - eta * xi * x[j]
    return _clip_fro(out, dim)


def energy(W: Sequence[float], x: Sequence[float], dim: int = DIM) -> float:
    e = 0.0
    for i in range(dim):
        xi = x[i]
        row = i * dim
        for j in range(dim):
            e -= 0.5 * xi * W[row + j] * x[j]
    return round(e, 4)


def hopfield_classic(
    W: Sequence[float],
    x: Sequence[float],
    steps: int = 8,
    dim: int = DIM,
) -> dict[str, Any]:
    s = [1 if v >= 0 else -1 for v in x]
    hist = [energy(W, s, dim)]
    for _ in range(steps):
        nxt = s[:]
        for i in range(dim):
            a = 0.0
            row = i * dim
            for j in range(dim):
                a += W[row + j] * s[j]
            nxt[i] = 1 if a >= 0 else -1
        s = nxt
        hist.append(energy(W, s, dim))
    return {"state": s, "hist": hist, "honesty": Honesty.MEASURED.value}


def hopfield_softmax(
    patterns: Sequence[Sequence[float]],
    cue: Sequence[float],
    beta: float = BETA,
) -> dict[str, Any]:
    if not patterns:
        return {
            "state": list(cue),
            "weights": [],
            "peak": 0.0,
            "honesty": Honesty.UNAVAILABLE.value,
        }
    scores = [beta * dot(p, cue) for p in patterns]
    peak_score = max(scores)
    exps = [math.exp(s - peak_score) for s in scores]
    z = sum(exps) or 1.0
    weights = [e / z for e in exps]
    dim = len(cue)
    state = [0.0] * dim
    for k, p in enumerate(patterns):
        wk = weights[k]
        for i in range(dim):
            state[i] += wk * p[i]
    return {
        "state": state,
        "weights": [round(w, 6) for w in weights],
        "peak": round(max(weights), 4),
        "honesty": Honesty.MEASURED.value,
    }


def capacity(p: int, n: int = DIM) -> dict[str, Any]:
    alpha = (p / n) if n else 0.0
    return {
        "P": p,
        "N": n,
        "alpha": round(alpha, 4),
        "classicalFloor": CLASSICAL_ALPHA,
        "classicalOk": alpha < CLASSICAL_ALPHA,
        "honesty": Honesty.MODELED.value,
    }


def kleiber_engrams(p: int) -> dict[str, Any]:
    return {
        "wattsAnalog": round(70.0 * (max(1, p) ** 0.75), 2),
        "joules": ENERGY,
        "honesty": Honesty.MODELED.value,
    }


def random_sparse(dim: int = DIM, k: int = SPARSE_K, seed: int = 1) -> list[int]:
    v = [0] * dim
    s = seed & 0xFFFFFFFF or 1

    def rnd() -> int:
        nonlocal s
        s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
        return s

    idx: set[int] = set()
    while len(idx) < min(k, dim):
        idx.add(rnd() % dim)
    for i in idx:
        v[i] = 1 if (rnd() % 2 == 0) else -1
    return v


def near_stored(state: Sequence[float], patterns: Sequence[Sequence[float]], thresh: float = 0.42) -> bool:
    return any(overlap(state, p) >= thresh for p in patterns)


def crosstalk(patterns: Sequence[Sequence[float]]) -> dict[str, Any]:
    total = 0.0
    peak = 0.0
    pairs = 0
    for i, a in enumerate(patterns):
        for b in patterns[i + 1 :]:
            o = abs(overlap(a, b))
            total += o
            if o > peak:
                peak = o
            pairs += 1
    return {
        "mean": round(total / pairs, 4) if pairs else 0.0,
        "peak": round(peak, 4),
        "pairs": pairs,
        "honesty": Honesty.MEASURED.value,
    }


def retrieval_fidelity(W: Sequence[float], patterns: Sequence[Sequence[float]], dim: int = DIM) -> dict[str, Any]:
    if not patterns:
        return {"mean": 0.0, "honesty": Honesty.UNAVAILABLE.value}
    acc = 0.0
    for p in patterns:
        noisy = [-v if (i % 5 == 0) else v for i, v in enumerate(p)]
        rec = hopfield_classic(W, noisy, 8, dim)
        acc += overlap(rec["state"], p)
    return {"mean": round(acc / len(patterns), 4), "honesty": Honesty.MEASURED.value}


def spurious_rate(
    W: Sequence[float],
    patterns: Sequence[Sequence[float]],
    trials: int = 12,
    dim: int = DIM,
) -> dict[str, Any]:
    if not patterns:
        return {"rate": 0.0, "trials": trials, "honesty": Honesty.UNAVAILABLE.value}
    sp = 0
    for i in range(trials):
        cue = random_sparse(dim, SPARSE_K, 9001 + i * 19)
        settled = hopfield_classic(W, cue, 10, dim)
        if not near_stored(settled["state"], patterns):
            sp += 1
    return {"rate": round(sp / trials, 3), "trials": trials, "honesty": Honesty.MEASURED.value}


def replay_round(
    W: Sequence[float],
    patterns: Sequence[Sequence[float]],
    seed: int,
    dim: int = DIM,
) -> dict[str, Any]:
    cue = random_sparse(dim, SPARSE_K, seed)
    settled = hopfield_classic(W, cue, 10, dim)
    spurious = bool(patterns) and not near_stored(settled["state"], patterns)
    nxt = reverse_hebb(W, settled["state"], dim=dim) if spurious else list(W)
    return {
        "W": nxt,
        "spurious": spurious,
        "energy": settled["hist"][-1] if settled["hist"] else 0.0,
    }


def bcm_step(
    W: Sequence[float],
    x: Sequence[float],
    theta: Sequence[float],
    *,
    dim: int = DIM,
    eta: float = ETA,
    tau: float = BCM_TAU,
) -> tuple[list[float], list[float]]:
    """Sliding-threshold BCM on local fields. Homeostasis, not a joule meter."""
    h = [0.0] * dim
    for i in range(dim):
        row = i * dim
        acc = 0.0
        for j in range(dim):
            acc += W[row + j] * x[j]
        h[i] = math.tanh(acc)
    nxt_theta = [((1.0 - tau) * theta[i] + tau * (h[i] * h[i])) for i in range(dim)]
    out = list(W)
    for i in range(dim):
        yi = h[i]
        drive = yi * (yi - nxt_theta[i])
        row = i * dim
        for j in range(dim):
            if i == j:
                out[row + j] = 0.0
                continue
            out[row + j] = out[row + j] + eta * drive * x[j]
    return _clip_fro(out, dim), nxt_theta


def energy_slice(
    W: Sequence[float],
    axis_a: Sequence[float],
    axis_b: Sequence[float],
    cells: int = 24,
    dim: int = DIM,
) -> list[float]:
    na = math.sqrt(dot(axis_a, axis_a)) or 1.0
    a = [v / na for v in axis_a]
    proj = dot(axis_b, a)
    b0 = [axis_b[i] - proj * a[i] for i in range(dim)]
    nb = math.sqrt(dot(b0, b0)) or 1.0
    b = [v / nb for v in b0]
    grid: list[float] = []
    for yi in range(cells):
        v = -1.15 + (2.3 * yi) / max(cells - 1, 1)
        for xi in range(cells):
            u = -1.15 + (2.3 * xi) / max(cells - 1, 1)
            x = [1 if (a[i] * u + b[i] * v) >= 0 else -1 for i in range(dim)]
            grid.append(energy(W, x, dim))
    return grid


@dataclass
class Yuyay:
    """Operational second-brain neural organ. In-process. Not eleven models."""

    dim: int = DIM
    W: list[float] = field(default_factory=zero_w)
    patterns: list[list[int]] = field(default_factory=list)
    texts: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    hashes: list[str] = field(default_factory=list)
    honesty_trace: list[str] = field(default_factory=list)
    theta: list[float] = field(default_factory=lambda: [0.2] * DIM)
    imprint_count: int = 0
    replay_count: int = 0
    last_replay: dict[str, Any] | None = None

    def imprint(
        self,
        text: str,
        source: str = "pulse",
        honesty: Honesty | str = Honesty.MEASURED,
        digest: str = "",
    ) -> dict[str, Any]:
        raw = (text or "").strip()
        if not raw:
            return {"ok": False, "error": "Empty engram.", "honesty": Honesty.MEASURED.value}
        if raw in self.texts:
            return {"ok": False, "error": "Already imprinted.", "honesty": Honesty.MEASURED.value}
        h = Honesty(honesty)
        if ETA_GAIN[h] <= 0:
            return {
                "ok": False,
                "error": "UNAVAILABLE cannot write synapses.",
                "honesty": Honesty.UNAVAILABLE.value,
            }
        vec = encode(raw, self.dim)
        self.W = hebb_oja(self.W, vec, dim=self.dim, honesty=h)
        self.W, self.theta = bcm_step(self.W, vec, self.theta, dim=self.dim)
        self.patterns.append(vec)
        self.texts.append(raw)
        self.sources.append(source)
        self.hashes.append(digest)
        self.honesty_trace.append(h.value)
        self.imprint_count += 1
        if len(self.patterns) > 80:
            self.patterns = self.patterns[-80:]
            self.texts = self.texts[-80:]
            self.sources = self.sources[-80:]
            self.hashes = self.hashes[-80:]
            self.honesty_trace = self.honesty_trace[-80:]
        return {
            "ok": True,
            "index": len(self.patterns) - 1,
            "text": raw,
            "source": source,
            "energy": energy(self.W, vec, self.dim),
            "honesty": Honesty.MEASURED.value,
            "writeHonesty": h.value,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }

    def forget(self, index: int) -> None:
        if index < 0 or index >= len(self.patterns):
            return
        del self.patterns[index]
        del self.texts[index]
        del self.sources[index]
        del self.hashes[index]
        del self.honesty_trace[index]
        self.W = zero_w(self.dim)
        self.theta = [0.2] * self.dim
        for vec, h in zip(self.patterns, self.honesty_trace):
            self.W = hebb_oja(self.W, vec, dim=self.dim, honesty=Honesty(h))

    def reset(self) -> None:
        self.W = zero_w(self.dim)
        self.patterns.clear()
        self.texts.clear()
        self.sources.clear()
        self.hashes.clear()
        self.honesty_trace.clear()
        self.theta = [0.2] * self.dim
        self.imprint_count = 0
        self.replay_count = 0
        self.last_replay = None

    def recall(self, cue: str) -> dict[str, Any]:
        raw = (cue or "").strip()
        if not raw or not self.patterns:
            return {
                "ok": False,
                "ranked": [],
                "classic": None,
                "softmax": None,
                "honesty": Honesty.UNAVAILABLE.value,
                "joules": ENERGY,
            }
        q = encode(raw, self.dim)
        soft = hopfield_softmax(self.patterns, q)
        classic = hopfield_classic(self.W, q, dim=self.dim)
        ranked = sorted(
            (
                {
                    "text": self.texts[i],
                    "source": self.sources[i],
                    "weight": soft["weights"][i] if i < len(soft["weights"]) else 0.0,
                    "overlap": overlap(q, self.patterns[i]),
                    "honesty": self.honesty_trace[i],
                }
                for i in range(len(self.patterns))
            ),
            key=lambda r: r["weight"],
            reverse=True,
        )
        return {
            "ok": True,
            "ranked": ranked[:5],
            "classicEnergy": classic["hist"][-1] if classic["hist"] else 0.0,
            "softmaxPeak": soft["peak"],
            "honesty": meet(Honesty.MEASURED, Honesty.MEASURED).value,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }

    def replay(self, rounds: int = 24) -> dict[str, Any]:
        patterns = self.patterns
        fid_b = retrieval_fidelity(self.W, patterns, self.dim)
        sp_b = spurious_rate(self.W, patterns, dim=self.dim)
        nxt = list(self.W)
        killed = 0
        seed0 = 4242 + self.replay_count * 17
        for i in range(max(1, min(int(rounds), 64))):
            step = replay_round(nxt, patterns, seed0 + i * 9973, self.dim)
            nxt = step["W"]
            if step["spurious"]:
                killed += 1
        self.W = nxt
        self.replay_count += 1
        fid_a = retrieval_fidelity(self.W, patterns, self.dim)
        sp_a = spurious_rate(self.W, patterns, dim=self.dim)
        report = {
            "rounds": rounds,
            "killed": killed,
            "fidelityBefore": fid_b["mean"],
            "fidelityAfter": fid_a["mean"],
            "spuriousBefore": sp_b["rate"],
            "spuriousAfter": sp_a["rate"],
            "honesty": Honesty.MEASURED.value,
            "joules": ENERGY,
            "lambda": LAMBDA,
        }
        self.last_replay = report
        return report

    def stats(self) -> dict[str, Any]:
        cap = capacity(len(self.patterns), self.dim)
        load = kleiber_engrams(len(self.patterns))
        xt = crosstalk(self.patterns)
        fid = retrieval_fidelity(self.W, self.patterns, self.dim)
        return {
            **cap,
            **load,
            "dim": self.dim,
            "imprints": self.imprint_count,
            "stored": len(self.patterns),
            "replays": self.replay_count,
            "crosstalk": xt["mean"],
            "crosstalkPeak": xt["peak"],
            "fidelity": fid["mean"],
            "frobenius": round(frobenius(self.W), 4),
            "lastReplay": self.last_replay,
            "lambda": LAMBDA,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "szl.ayllu.yuyay/v1",
            "stats": self.stats(),
            "engrams": [
                {
                    "text": t,
                    "source": s,
                    "honesty": h,
                    "hash": digest or None,
                }
                for t, s, h, digest in zip(self.texts, self.sources, self.honesty_trace, self.hashes)
            ],
            "joules": ENERGY,
            "lambda": LAMBDA,
        }
