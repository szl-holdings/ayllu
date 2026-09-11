"""Gold policy recall. Not courtroom skill. Not AGI."""
from ayllu.eval.score import evaluate


def test_gold_ten_hits() -> None:
    out = evaluate()
    missed = [row["id"] for row in out["rows"] if not row["match"]]
    assert out["n"] == 10
    assert missed == [], missed
    assert out["hits"] == 10
    assert out["effectiveness"] == "MEASURED"
    assert out["legal_authority"] == "PROPOSAL_ONLY"
