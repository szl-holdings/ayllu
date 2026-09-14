"""Offline unit regressions: no global psyche, network, weights, or live beats."""
import importlib.util
import json
from pathlib import Path
import sys
import types

import pytest


def load(name, filename):
    path = Path(__file__).resolve().parents[1] / "ayllu" / "psyche" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kutiy = load("kutiy_observation_unit", "kutiy.py")


def test_zero_preserved_and_nested_zero_wins():
    assert kutiy._snapshot({"H": 0.0, "Q": 0, "Y": 0}) == {"H": 0, "Q": 0, "Y": 0}
    assert kutiy._snapshot({"huklla": {"H": 0}, "H": 9})["H"] == 0


@pytest.mark.parametrize("value", [None, True, False, "0", float("nan"), float("inf"), -float("inf"), 10**400])
def test_non_observations_are_missing(value):
    assert kutiy._snapshot({"H": value})["H"] is None


def test_partial_observation_is_not_zero_delta():
    assert kutiy._delta({}, {}) is None
    assert kutiy._delta({"H": 0, "Q": 0}, {"H": 0, "Q": 0}) is None
    assert kutiy._delta({"H": 1e308, "Q": 0, "Y": 0}, {"H": -1e308, "Q": 0, "Y": 0}) is None


class Psyche:
    pulses = 1
    def __init__(self, before, after=None):
        self.last_winay = before
        self.after = before if after is None else after
        self.calls = 0
    def beat(self, *args, **kwargs):
        self.calls += 1
        self.last_winay = self.after


def test_incomplete_initial_state_does_not_request_a_beat():
    psyche = Psyche({})
    result = kutiy.kutiy(psyche)
    assert psyche.calls == 0
    assert result["halt"] == "incomplete-observation"
    assert result["task_verified"] is False


def test_missing_after_beat_stops_unknown():
    psyche = Psyche({"H": 0, "Q": 0, "Y": 0}, {})
    result = kutiy.kutiy(psyche)
    assert psyche.calls == 1
    assert result["honesty"] == "UNAVAILABLE"
    assert result["delta"] is None
    json.dumps(result, allow_nan=False)


def test_complete_stationarity_is_not_task_verified():
    result = kutiy.kutiy(Psyche({"H": 0, "Q": 0, "Y": 0}))
    assert result["observation_status"] == "OBSERVED_STATIONARY"
    assert result["last_step_delta"] == 0
    assert result["task_verified"] is False


@pytest.mark.parametrize("kwargs", [{"r_max": True}, {"r_max": 0}, {"r_max": 9}, {"r_max": 1.5},
    {"eps": True}, {"eps": 0}, {"eps": float("nan")}, {"eps": float("inf")}])
def test_invalid_controls_fail_before_beat(kwargs):
    psyche = Psyche({"H": 0, "Q": 0, "Y": 0})
    with pytest.raises(ValueError):
        kutiy.kutiy(psyche, **kwargs)
    assert psyche.calls == 0


def test_receipt_first_observation_and_missing_metric_are_not_stable(monkeypatch):
    bind = load("kutiy_bind_unit", "bind.py")
    yuyariy = types.ModuleType("ayllu.psyche.yuyariy")
    yuyariy.yuyariy = lambda psyche: {"count": 0, "observations": []}
    monkeypatch.setitem(sys.modules, "ayllu.psyche.kutiy", kutiy)
    monkeypatch.setitem(sys.modules, "ayllu.psyche.yuyariy", yuyariy)
    psyche = Psyche({"H": 0, "Q": 0, "Y": 0})
    first = bind.stamp(psyche)["kutiy_gate"]
    assert first["stable"] is False and first["delta"] is None
    second = bind.stamp(psyche)["kutiy_gate"]
    assert second["stable"] is True and second["task_verified"] is False
    psyche.last_winay = {"H": 0, "Q": 0}
    third = bind.stamp(psyche)["kutiy_gate"]
    assert third["stable"] is False and third["delta"] is None
    json.dumps(third, allow_nan=False)
