"""Council meta-judging arithmetic for the counsel harness.

Absorbs, at harness level only (source cards: docs/LEADERS-STUDY.md,
leader-study PR ayllu#80):
- Meta-Judges, arXiv:2504.17087 -- thresholded aggregation over judge
  scores with abstention when judges disagree.
- L-MAD council matrix pattern, arXiv:2607.09099 -- per-question by
  per-judge verdict matrix with per-question adjudication.

HONEST SCOPE: this module is arithmetic over scores that a caller
supplies. It never calls an LLM, never measures courtroom or agent
effectiveness, and a pass threshold is a policy knob, not a quality
proof. Cohen's kappa is NOT computed; the agreement figure is simple
percent agreement inside a tolerance window, labelled as such.
"""
from __future__ import annotations

import statistics
from typing import Any

SCHEMA = "szl.ayllu.meta-judges/v1"

# Score-mod taxonomy: classify the sign and magnitude of a score change.
def score_mod(before: float, after: float, *, band: float = 0.1) -> str:
    """Classify a score delta into the score-mod taxonomy."""
    delta = after - before
    if delta > band:
        return "IMPROVED"
    if delta < -band:
        return "REGRESSED"
    return "NEUTRAL"


def agreement(scores: list[float], *, window: float = 0.25) -> float:
    """Fraction of judge pairs whose scores fall within `window`."""
    if len(scores) < 2:
        return 1.0 if scores else 0.0
    n = len(scores)
    total = n * (n - 1) // 2
    ok = 0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(scores[i] - scores[j]) <= window:
                ok += 1
    return ok / total


def aggregate(
    scores: list[float],
    *,
    threshold: float = 0.5,
    min_agreement: float = 0.5,
    window: float = 0.25,
    abstain_below_agreement: bool = True,
) -> dict[str, Any]:
    """Thresholded Meta-Judges aggregation with abstention on disagreement."""
    if not scores:
        return {
            "schema": SCHEMA,
            "n": 0,
            "verdict": "ABSTAIN",
            "reason": "no_scores",
            "note": "No judge scores supplied.",
        }
    agree = agreement(scores, window=window)
    mean = statistics.fmean(scores)
    if abstain_below_agreement and agree < min_agreement:
        verdict = "ABSTAIN"
        reason = "low_agreement"
    else:
        verdict = "PASS" if mean >= threshold else "FAIL"
        reason = "mean_vs_threshold"
    return {
        "schema": SCHEMA,
        "n": len(scores),
        "mean": mean,
        "median": statistics.median(scores),
        "percent_agreement_within_window": agree,
        "agreement_statistic": "percent_within_window_not_kappa",
        "threshold": threshold,
        "verdict": verdict,
        "reason": reason,
        "not": ["effectiveness", "kappa", "llm_output"],
    }


def council_matrix(
    rows: list[dict[str, Any]],
    *,
    threshold: float = 0.5,
    min_agreement: float = 0.5,
) -> dict[str, Any]:
    """Per-question by per-judge matrix with per-question adjudication.

    `rows`: dicts with keys question_id, judge, score (0.0-1.0).
    Returns a receipt dict with the matrix, per-question verdicts and a
    per-judge summary. Deterministic: rows are ordered by question then
    judge (Python's stable sort) before any output is built.
    """
    ordered = sorted(rows, key=lambda r: (str(r.get("question_id")), str(r.get("judge"))))
    by_q: dict[str, list[float]] = {}
    for r in ordered:
        by_q.setdefault(str(r.get("question_id")), []).append(float(r.get("score", 0.0)))
    matrix_out: dict[str, dict[str, float]] = {}
    for r in ordered:
        matrix_out.setdefault(str(r.get("question_id")), {})[str(r.get("judge"))] = float(r.get("score", 0.0))
    per_question: dict[str, dict[str, Any]] = {}
    for q, sc in by_q.items():
        per_question[q] = aggregate(sc, threshold=threshold, min_agreement=min_agreement)
    judges = sorted({str(r.get("judge")) for r in ordered})
    judged = [q for q in per_question if per_question[q]["verdict"] != "ABSTAIN"]
    council_score = (
        statistics.fmean([per_question[q]["mean"] for q in judged]) if judged else None
    )
    verdict = "ABSTAIN" if judged == [] else (
        "PASS" if council_score is not None and council_score >= threshold else "FAIL"
    )
    return {
        "schema": SCHEMA,
        "kind": "council_matrix",
        "judges": judges,
        "questions": sorted(by_q),
        "matrix": matrix_out,
        "per_question": per_question,
        "council_score": council_score,
        "verdict": verdict,
        "threshold": threshold,
        "not": ["court_outcome", "agent_effectiveness", "llm_invocation"],
    }
