"""Tests for ayllu.eval.meta_judges (Meta-Judges / L-MAD absorb). Stdlib only."""
from __future__ import annotations

from ayllu.eval.meta_judges import aggregate, council_matrix, score_mod


def test_score_mod_taxonomy():
    assert score_mod(0.4, 0.7) == "IMPROVED"
    assert score_mod(0.7, 0.4) == "REGRESSED"
    assert score_mod(0.5, 0.55) == "NEUTRAL"


def test_aggregate_pass_on_high_scores():
    r = aggregate([0.8, 0.9, 0.85], threshold=0.5)
    assert r["verdict"] == "PASS"
    assert r["n"] == 3
    assert 0 < r["percent_agreement_within_window"] <= 1.0


def test_aggregate_abstains_on_disagreement():
    r = aggregate([1.0, 0.0, 1.0, 0.0], threshold=0.5, min_agreement=0.5)
    assert r["verdict"] == "ABSTAIN"
    assert r["reason"] == "low_agreement"


def test_aggregate_fail_below_threshold():
    r = aggregate([0.2, 0.3, 0.25], threshold=0.5)
    assert r["verdict"] == "FAIL"


def test_aggregate_empty():
    r = aggregate([])
    assert r["verdict"] == "ABSTAIN"
    assert r["reason"] == "no_scores"


def test_council_matrix_shape_and_determinism():
    rows = [
        {"question_id": "q2", "judge": "a", "score": 0.9},
        {"question_id": "q1", "judge": "b", "score": 0.8},
        {"question_id": "q1", "judge": "a", "score": 0.7},
        {"question_id": "q2", "judge": "b", "score": 0.6},
    ]
    r1 = council_matrix(rows)
    r2 = council_matrix(list(reversed(rows)))
    assert r1["schema"] == r2["schema"]
    assert r1["matrix"] == r2["matrix"]  # deterministic regardless of input order
    assert r1["judges"] == ["a", "b"]
    assert r1["questions"] == ["q1", "q2"]
    assert r1["per_question"]["q1"]["verdict"] == "PASS"
    assert r1["verdict"] == "PASS"
    assert r1["per_question"]["q1"]["agreement_statistic"] == "percent_within_window_not_kappa"
