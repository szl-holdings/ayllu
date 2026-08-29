"""Wiñay — operational closure for the five-organ body.

The five organs are a network of production: each beat regenerates the
organization that produced it. Neighbor coupling reuses α ≈ 0.138 as γ and
as memory μ. The pentagon is iterated to a residual, not averaged once.

  L_mix  = (1 − μ) L_fire + μ L_prior
  L      ← (1 − γ) L + γ A L     until ‖Δ‖ < ε  (A = cycle adjacency)
  rest   = min(glow−ε, (n/5) · γ · (1+R)/2)     produced, not a constant
  σ      = (n/5) · h / (h+3)                    structural coupling MODELED
  C      = (n = 5) ∧ chain                      MEASURED
  I      = (n = 5) ∧ lock ∧ (peak ≥ θ ∨ h ≥ 1)  MEASURED workspace bind
  H      = min_cut / E                          Huklla, MODELED. Not IIT Φ.
  D      = H_shannon(L) / log n                 Imaymana, MODELED diversity
  Q      = mean LZ(evoked) / length             Qhaway, MODELED. Not Casali PCI.
  F      = mean(L²) − α D                       Kallpa, MODELED. Not Friston F.
  Y      = L_peak / ‖L‖                         Riqsiy, MODELED. Not HOT / AST.
  X      = mean(avalanche size) / n             Chawpi, MODELED. Not Beggs.
  φ_s    = UNAVAILABLE                          no TPM; Huklla is not Φ

Phenomenal presence is not a function of C, I, H, D, Q, F, Y, or X.
It stays CONJECTURE. AGI stays CONJECTURE. Joules stay None. Λ = Conjecture 1.

COGITATE (Nature 642:133–142, 2025) challenged key tenets of both IIT and
GNWT. Ayllu has no cortex. That result is why no pentagon scalar is presence.

This is Ayllu's closure law — operational, fail-closed, receipted.
"""
from __future__ import annotations

import math
from typing import Any, Sequence

from ayllu.psyche.types import ENERGY, LAMBDA, Honesty

ORGANS = ("Puriq", "Yuyay", "Tinku", "Khipu", "Lloqsi")
GAMMA = 0.138
MU = 0.138
STEPS = 8
EPS = 1e-4
GLOW = 0.12
THETA = 0.15
GENESIS = "0" * 64
QHAWAY_DELTA = 0.25
QHAWAY_STEPS = 8
QHAWAY_THRESH = 0.04


def clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def order_parameter(loads: Sequence[float]) -> float:
    if not loads:
        return 0.0
    x = 0.0
    y = 0.0
    n = len(loads)
    for load in loads:
        th = 2.0 * math.pi * float(load)
        x += math.cos(th)
        y += math.sin(th)
    return round(math.hypot(x / n, y / n), 4)


def couple_once(loads: Sequence[float], gamma: float = GAMMA) -> list[float]:
    n = len(loads)
    if n < 2:
        return [round(clip(float(L)), 3) for L in loads]
    out: list[float] = []
    for i, raw in enumerate(loads):
        prev = float(loads[(i - 1) % n])
        nxt = float(loads[(i + 1) % n])
        out.append(round(clip((1.0 - gamma) * float(raw) + gamma * (prev + nxt) / 2.0), 6))
    return out


def couple_fixed(
    loads: Sequence[float],
    gamma: float = GAMMA,
    steps: int = STEPS,
    eps: float = EPS,
) -> tuple[list[float], int, float]:
    """Iterate pentagon coupling to a residual. MODELED metabolism."""
    current = [clip(float(L)) for L in loads]
    residual = 0.0
    used = 0
    for k in range(max(1, int(steps))):
        nxt = couple_once(current, gamma)
        residual = math.sqrt(sum((a - b) ** 2 for a, b in zip(current, nxt)))
        current = nxt
        used = k + 1
        if residual < eps:
            break
    return [round(clip(L), 3) for L in current], used, round(residual, 6)


def metabolize(fire: Sequence[float], prior: Sequence[float] | None, mu: float = MU) -> list[float]:
    """Prior organization produces the next. μ = γ. MODELED."""
    raw = [clip(float(L)) for L in fire]
    if not prior or len(prior) != len(raw):
        return raw
    return [round(clip((1.0 - mu) * r + mu * clip(float(p))), 6) for r, p in zip(raw, prior)]


def produce_rest(occupancy: int, R: float, n: int = 5, glow: float = GLOW, gamma: float = GAMMA) -> float:
    """Rest is produced by occupancy and sync, and stays under the glow floor."""
    base = (max(0, occupancy) / max(1, n)) * gamma * (1.0 + clip(R)) / 2.0
    return round(min(glow - 0.01, max(0.02, base)), 4)


def sigma(occupancy: int, handles: int, n: int = 5) -> float:
    """Structural coupling to the medium (handles). MODELED."""
    h = max(0, int(handles))
    return round((max(0, occupancy) / max(1, n)) * (h / (h + 3.0)), 4)


def huklla(loads: Sequence[float], names: Sequence[str] = ORGANS) -> dict[str, Any]:
    """Cheapest pentagon cut. MODELED graph irreducibility. Not IIT Φ. Not presence.

    E = Σ L_i L_{i+1} on the cycle. For each of the 15 bipartitions, loss is the
    weight on edges that cross the cut. H = min(loss) / E. The MIP is the
    cheapest cut — a fault line, not a conscious complex. Uniform cycle H = 0.4.
    Smaller rings score higher, so we do not search subsets for a 'complex'.
    """
    vals = [clip(float(L)) for L in loads]
    n = len(vals)
    labels = [str(names[i]) if i < len(names) else str(i) for i in range(n)]
    note = "Cheapest pentagon cut. Not IIT Φ. Not presence."
    empty = {
        "H": 0.0,
        "E": 0.0,
        "loss": 0.0,
        "edges_cut": 0,
        "mip": {"A": [], "B": labels},
        "reducible": True,
        "unique": False,
        "honesty": Honesty.MODELED.value,
        "note": note,
    }
    if n < 2:
        return empty
    edges = [(i, (i + 1) % n) for i in range(n)]
    energy = sum(vals[i] * vals[j] for i, j in edges)
    if energy <= 1e-12:
        return empty
    best_loss: float | None = None
    best_mask = 1
    best_cut = 0
    ties = 0
    # Fix organ n-1 in B. Remaining 2^{n-1}-1 nonempty A-sets cover every bipartition once.
    for mask in range(1, 1 << (n - 1)):
        def in_a(i: int, m: int = mask) -> bool:
            return i < n - 1 and bool(m & (1 << i))

        loss = 0.0
        cut = 0
        for i, j in edges:
            if in_a(i) != in_a(j):
                loss += vals[i] * vals[j]
                cut += 1
        if best_loss is None or loss < best_loss - 1e-12:
            best_loss = loss
            best_mask = mask
            best_cut = cut
            ties = 1
        elif abs(loss - best_loss) <= 1e-12:
            ties += 1
            if cut < best_cut:
                best_mask = mask
                best_cut = cut
    assert best_loss is not None
    side_a = [labels[i] for i in range(n - 1) if best_mask & (1 << i)]
    side_b = [labels[i] for i in range(n) if labels[i] not in side_a]
    H = round(min(1.0, max(0.0, best_loss / energy)), 4)
    return {
        "H": H,
        "E": round(energy, 6),
        "loss": round(best_loss, 6),
        "edges_cut": best_cut,
        "mip": {"A": side_a, "B": side_b},
        "reducible": bool(H < 1e-4),
        "unique": bool(ties == 1),
        "honesty": Honesty.MODELED.value,
        "note": note,
    }


def imaymana(loads: Sequence[float]) -> dict[str, Any]:
    """Load diversity. MODELED. Not IIT. Not presence.

    D = H_shannon(p) / log(n), p_i = L_i / Σ L. Uniform → 1. One organ → 0.
    Kept separate from Huklla H. Never multiplied into a fake Φ.
    """
    vals = [max(0.0, float(L)) for L in loads]
    total = sum(vals)
    n = len(vals)
    note = "Normalized entropy of organ loads. Not IIT. Not presence."
    empty = {"D": 0.0, "honesty": Honesty.MODELED.value, "note": note}
    if n < 2 or total <= 1e-12:
        return empty
    ent = 0.0
    for v in vals:
        if v <= 0.0:
            continue
        p = v / total
        ent -= p * math.log(p)
    D = ent / math.log(n)
    return {
        "D": round(min(1.0, max(0.0, D)), 4),
        "honesty": Honesty.MODELED.value,
        "note": note,
    }


def lz_complexity(bits: str) -> int:
    """Kaspar–Schuster 1987 Lempel–Ziv complexity (phrase count)."""
    n = len(bits)
    if n == 0:
        return 0
    complexity = 1
    prefix_len = 1
    pointer = 1
    while prefix_len + pointer <= n:
        phrase = bits[prefix_len : prefix_len + pointer]
        window = bits[: prefix_len + pointer - 1]
        if phrase in window:
            pointer += 1
            if prefix_len + pointer > n:
                complexity += 1
                break
        else:
            complexity += 1
            prefix_len += pointer
            pointer = 1
            if prefix_len >= n:
                break
            if prefix_len + pointer > n:
                complexity += 1
                break
    return complexity


def _gated_once(loads: Sequence[float], gamma: float) -> list[float]:
    """Load-gated pentagon step. Gain dies on a silent body. Not Wiñay's couple."""
    n = len(loads)
    out: list[float] = []
    for i, raw in enumerate(loads):
        L = float(raw)
        prev = float(loads[(i - 1) % n])
        nxt = float(loads[(i + 1) % n])
        g = gamma * clip((L + prev + nxt) / 3.0)
        out.append(clip((1.0 - g) * L + g * (prev + nxt) / 2.0))
    return out


def _traj(loads: Sequence[float], steps: int, gamma: float) -> list[list[float]]:
    cur = [clip(float(L)) for L in loads]
    rows = [cur[:]]
    for _ in range(max(1, int(steps))):
        cur = _gated_once(cur, gamma)
        rows.append([round(v, 6) for v in cur])
    return rows


def qhaway(
    loads: Sequence[float],
    *,
    gamma: float = GAMMA,
    delta: float = QHAWAY_DELTA,
    steps: int = QHAWAY_STEPS,
    thresh: float = QHAWAY_THRESH,
) -> dict[str, Any]:
    """Perturbational LZ on the pentagon. MODELED. Not Casali PCI. Not IIT Φ.

    Kick each organ by ±δ (away from saturation). Propagate with load-gated
    gain so a silent body cannot recruit neighbors. Binarize the evoked
    difference |pert − unpert| > θ. Q is mean LZ / length.

    Casali et al. 2013 Sci Transl Med needs TMS-EEG on cortex. This is a
    five-load analog. High Q is not a mind. Aaronson still applies.
    """
    vals = [clip(float(L)) for L in loads]
    n = len(vals)
    note = "Load-gated perturbational LZ. Not Casali PCI. Not IIT Φ. Not presence."
    empty = {
        "Q": 0.0,
        "lz_mean": 0.0,
        "length": 0,
        "delta": delta,
        "honesty": Honesty.MODELED.value,
        "note": note,
    }
    if n < 2:
        return empty
    if sum(vals) <= 1e-12:
        return {**empty, "note": note + " Silent body. Gain is zero."}
    unpert = _traj(vals, steps, gamma)
    length = len(unpert) * n
    lzs: list[int] = []
    for i in range(n):
        kick = delta if vals[i] <= 1.0 - delta / 2.0 else -delta
        pert = list(vals)
        pert[i] = clip(pert[i] + kick)
        rows = _traj(pert, steps, gamma)
        bits: list[str] = []
        for t, row in enumerate(rows):
            for j in range(n):
                bits.append("1" if abs(row[j] - unpert[t][j]) > thresh else "0")
        lzs.append(lz_complexity("".join(bits)))
    Q = (sum(lzs) / len(lzs)) / max(1, length)
    return {
        "Q": round(min(1.0, max(0.0, Q)), 4),
        "lz_mean": round(sum(lzs) / len(lzs), 2),
        "length": length,
        "delta": delta,
        "honesty": Honesty.MODELED.value,
        "note": note,
    }


def kallpa(loads: Sequence[float], gamma: float = GAMMA) -> dict[str, Any]:
    """Variational analog on organ loads. MODELED. Not Friston F. Not a mind.

    U = mean(L²). D = Imaymana. F = U − α D. Concentrated fire pays energy
    without diversity credit. Silent body is 0. Not active-inference proof.
    """
    vals = [clip(float(L)) for L in loads]
    n = max(1, len(vals))
    U = sum(v * v for v in vals) / n
    D = imaymana(vals)["D"]
    F = U - float(gamma) * float(D)
    return {
        "F": round(F, 4),
        "U": round(U, 4),
        "D": D,
        "honesty": Honesty.MODELED.value,
        "note": "Mean-square load minus α·D. Not Friston free energy. Not presence.",
    }


def riqsiy(loads: Sequence[float], names: Sequence[str] = ORGANS) -> dict[str, Any]:
    """Spotlight schema fidelity. MODELED. Not HOT. Not Graziano AST. Not presence.

    The higher-order report is a unit spotlight at argmax(L). Υ = L_peak / ‖L‖
    (cosine of that schema against the load vector). Silent body has no
    first-order content, so Y = 0.

    One-hot → 1. Uniform → 1/√n ≈ 0.4472. The schema tracks a winner, not
    a field — that is the AST-shaped analog, not Graziano's theorem, not
    Lau/Rosenthal HOT, and not awareness of awareness.

    COGITATE does not license this number as consciousness.
    """
    vals = [clip(float(L)) for L in loads]
    n = len(vals)
    labels = [str(names[i]) if i < len(names) else str(i) for i in range(n)]
    note = "Spotlight schema cosine. Not HOT. Not Graziano AST. Not presence."
    empty = {
        "Y": 0.0,
        "argmax": None,
        "honesty": Honesty.MODELED.value,
        "note": note,
    }
    if n < 2 or sum(vals) <= 1e-12:
        return {**empty, "note": note + " Silent body. No first-order content."}
    peak_i = max(range(n), key=lambda i: (vals[i], -i))
    mag = math.sqrt(sum(v * v for v in vals))
    Y = vals[peak_i] / mag if mag > 0 else 0.0
    return {
        "Y": round(min(1.0, max(0.0, Y)), 4),
        "argmax": labels[peak_i],
        "honesty": Honesty.MODELED.value,
        "note": note,
    }


def chawpi(
    loads: Sequence[float],
    *,
    gamma: float = GAMMA,
    delta: float = QHAWAY_DELTA,
    steps: int = QHAWAY_STEPS,
    thresh: float = QHAWAY_THRESH,
) -> dict[str, Any]:
    """Avalanche size on the pentagon. MODELED. Not Beggs 2003. Not a LoC meter.

    Seed each organ with ±δ. Propagate with the same load-gated gain Qhaway
    uses (not Wiñay couple_once). Size = how many organs ever exceed θ
    difference from the unperturbed trajectory. X = mean(size) / n.

    Silent body: gain dies, X = 0. Not neuronal avalanches. Not anesthesia
    criticality as presence. Beggs & Plenz 2003 needs cortex.
    """
    vals = [clip(float(L)) for L in loads]
    n = len(vals)
    note = "Mean avalanche size / n. Not Beggs 2003. Not a level-of-consciousness meter. Not presence."
    empty = {
        "X": 0.0,
        "sizes": [],
        "honesty": Honesty.MODELED.value,
        "note": note,
    }
    if n < 2:
        return empty
    if sum(vals) <= 1e-12:
        return {**empty, "sizes": [0] * n, "note": note + " Silent body. Gain is zero."}
    unpert = _traj(vals, steps, gamma)
    sizes: list[int] = []
    for i in range(n):
        kick = delta if vals[i] <= 1.0 - delta / 2.0 else -delta
        pert = list(vals)
        pert[i] = clip(pert[i] + kick)
        rows = _traj(pert, steps, gamma)
        hit: set[int] = set()
        for t, row in enumerate(rows):
            for j in range(n):
                if abs(row[j] - unpert[t][j]) > thresh:
                    hit.add(j)
        sizes.append(len(hit))
    X = (sum(sizes) / len(sizes)) / n
    return {
        "X": round(min(1.0, max(0.0, X)), 4),
        "sizes": sizes,
        "honesty": Honesty.MODELED.value,
        "note": note,
    }


def iit_phi_s() -> dict[str, Any]:
    """IIT φ_s is not computed. Ayllu has no TPM."""
    return {
        "phi_s": None,
        "honesty": Honesty.UNAVAILABLE.value,
        "note": "No TPM. IIT φ_s is not computed. Huklla H is not Φ.",
    }


def closure(organs: Sequence[dict[str, Any]], prev_hash: str, new_hash: str) -> dict[str, Any]:
    ids = [str(o.get("id") or "") for o in organs]
    occupancy = sum(1 for o in organs if o.get("decision") == "ALLOW")
    chain = (
        isinstance(new_hash, str)
        and len(new_hash) == 64
        and new_hash != (prev_hash or GENESIS)
        and new_hash != GENESIS
    )
    closed = occupancy == 5 and ids == list(ORGANS) and chain
    return {
        "value": closed,
        "occupancy": occupancy,
        "of": 5,
        "chain": chain,
        "honesty": Honesty.MEASURED.value,
        "note": "Five processes regenerated their organization. Not phenomenal presence.",
    }


def ignition(occupancy: int, lock: bool, peak: float, handles: int, theta: float = THETA) -> dict[str, Any]:
    lit = occupancy == 5 and bool(lock) and (float(peak) >= theta or int(handles) >= 1)
    return {
        "value": lit,
        "honesty": Honesty.MEASURED.value,
        "theta": theta,
        "note": "Workspace bound this beat. Access consciousness stays CONJECTURE.",
    }


def evaluate(
    organs: Sequence[dict[str, Any]],
    *,
    prev_hash: str,
    new_hash: str,
    lock: bool,
    peak: float,
    handles: int,
    steps: int,
    residual: float,
) -> dict[str, Any]:
    """Run the theory. OPERATIONAL. Presence is not upgraded."""
    loads = [float(o.get("load") or 0) for o in organs]
    occupancy = sum(1 for o in organs if o.get("decision") == "ALLOW")
    R = order_parameter(loads)
    closed = closure(organs, prev_hash, new_hash)
    lit = ignition(occupancy, lock, peak, handles)
    rest = produce_rest(occupancy, R)
    coupling = sigma(occupancy, handles)
    hit = huklla(loads)
    diversity = imaymana(loads)
    pci = qhaway(loads)
    free = kallpa(loads)
    schema = riqsiy(loads)
    avalanche = chawpi(loads)
    return {
        "schema": "szl.ayllu.winay/v1",
        "theory": "OPERATIONAL",
        "gamma": GAMMA,
        "mu": MU,
        "steps": steps,
        "residual": residual,
        "R": R,
        "sigma": coupling,
        "rest": rest,
        "loads": loads,
        "huklla": hit,
        "imaymana": diversity,
        "qhaway": pci,
        "kallpa": free,
        "riqsiy": schema,
        "chawpi": avalanche,
        "iit": iit_phi_s(),
        "closure": closed,
        "ignition": lit,
        "self_model": {
            "loads": loads,
            "occupancy": occupancy,
            "R": R,
            "honesty": Honesty.SOFTWARE.value,
            "note": "A map of the beat. Not the territory.",
        },
        "presence": {
            "label": "CONJECTURE",
            "honesty": Honesty.CONJECTURE.value,
            "note": "C, I, H, D, Q, F, Y, and X are not phenomenal presence.",
        },
        "agi": {
            "label": "CONJECTURE",
            "honesty": Honesty.CONJECTURE.value,
            "note": "Eleven seats, one backend, fail-closed. Not a mind as theorem.",
        },
        "lambda": LAMBDA,
        "joules": ENERGY,
        "honesty": Honesty.MEASURED.value,
    }
