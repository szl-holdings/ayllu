from ayllu.psyche.rimanakuy import BODIES, EXPECTED, rimanakuy, score


def test_canonical_bodies_match_locked_contract() -> None:
    for name, vals in BODIES.items():
        got = score(vals)
        want = EXPECTED[name]
        assert got == want, (name, got, want)


def test_h_and_y_diverge_on_one_hot_versus_uniform() -> None:
    ran = rimanakuy()
    assert ran["schema"] == "szl.ayllu.cogitate/v1"
    assert ran["diverge"]["H_prefers"] == "uniform"
    assert ran["diverge"]["Y_prefers"] == "one_hot"
    assert ran["diverge"]["same_order"] is False
    assert ran["iit"]["phi_s"] is None
    assert ran["presence"]["honesty"] == "CONJECTURE"
    assert ran["cogitate"]["honesty"] == "RECORD"
    assert ran["cogitate"]["not_the_experiment"] is True
    assert "10.1038/s41586-025-08888-1" in ran["cogitate"]["reference"]
    assert ran["battery"]["silent"]["Q"] == 0.0
    assert ran["battery"]["one_hot"]["Y"] == 1.0
    assert ran["battery"]["uniform"]["H"] == 0.4
