"""Kutiy is original residual depth. Not Huginn. Not AGI."""
from ayllu.psyche.kutiy import kutiy
from ayllu.psyche.engine import PSYCHE


def test_kutiy_unavailable_without_beat() -> None:
    class Empty:
        pulses = 0
        last_winay = {}

        def beat(self, *_a, **_k) -> None:
            raise AssertionError("must not beat without occupancy")

    body = kutiy(Empty())
    assert body["honesty"] == "UNAVAILABLE"
    assert body["copied"] is False
    assert body["agi"] == "CONJECTURE"
    assert body["steps"] == 0


def test_kutiy_modeled_after_occupy() -> None:
    PSYCHE.set_lock(True)
    if PSYCHE.pulses < 1:
        PSYCHE.beat("kutiy test occupy", seat="Maskaq")
    body = kutiy(PSYCHE, r_max=2, eps=1.0)
    assert body["copied"] is False
    assert body["agi"] == "CONJECTURE"
    assert body["presence"] == "CONJECTURE"
    assert body["honesty"] == "MODELED"
    assert body["steps"] >= 1
    assert "Huginn" not in body["note"] or "Not Huginn" in body["note"]
