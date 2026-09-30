"""A supplied non-finite or out-of-range Λ is not a pass (FF-09).

`gate()` compared `float(lambda_score) < float(lambda_floor)` and allowed
everything else. Every comparison with NaN is False, so a NaN Λ (or a NaN
floor) fell through to allow; +Inf and 1.5 are not below 0.90, so they passed
too. Λ is a weighted geometric mean of scores in [0, 1], so a value outside
[0, 1] is not a Λ at all.

These tests pin the fix, using the error codes of the szl.lambda/v1 contract:

* a supplied Λ that is NaN or ±Inf denies with LAMBDA_NONFINITE_AXIS;
* a supplied Λ below 0 or above 1 denies with LAMBDA_AXIS_OUT_OF_RANGE;
* a supplied Λ that is not a real number (bool is not) denies with
  LAMBDA_TYPE_INVALID;
* a floor that is not a threshold in (0, 1] denies with LAMBDA_TAU_INVALID,
  checked first, as the v1 gate checks τ first;
* an ABSENT Λ is unchanged: attestation stays the binding gate and the
  unchecked floor is an annotated advisory. Making an absent Λ deny is an
  owner decision: `HumanLock.admit` has no Λ source, so it would block
  every psyche write.
"""
from __future__ import annotations

import pytest

from ayllu.autonomy import LAMBDA_FLOOR_DEFAULT, gate
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.types import Decision

NAN = float("nan")
INF = float("inf")


def _attested_write(lambda_score, **kw):
    return gate("write", state_changing=True, two_person_attested=True,
                lambda_score=lambda_score, **kw)


# --- non-finite Λ ------------------------------------------------------------

@pytest.mark.parametrize("x", [NAN, INF, -INF], ids=["nan", "+inf", "-inf"])
def test_nonfinite_lambda_denies_attested_state_change(x) -> None:
    g = _attested_write(x)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_NONFINITE_AXIS"
    assert "LAMBDA_NONFINITE_AXIS" in g["reason"]
    assert g["lambda_checked"] is True
    assert g["advisories"] == []


@pytest.mark.parametrize("x", [NAN, INF, -INF], ids=["nan", "+inf", "-inf"])
def test_nonfinite_lambda_denies_read_too(x) -> None:
    # A supplied Λ is checked on every action, as a sub-floor Λ already is.
    g = gate("read", state_changing=False, lambda_score=x)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_NONFINITE_AXIS"


def test_nonfinite_lambda_without_attestation_reports_both_reasons() -> None:
    g = gate("write", state_changing=True, two_person_attested=False, lambda_score=NAN)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_NONFINITE_AXIS"
    assert "two-person attestation" in g["reason"]
    assert "LAMBDA_NONFINITE_AXIS" in g["reason"]


# --- out-of-range Λ ----------------------------------------------------------

@pytest.mark.parametrize("x", [1.5, 1.0 + 1e-12, 1e308, -0.1, -1e-12, -1.0])
def test_out_of_range_lambda_denies_attested_state_change(x) -> None:
    g = _attested_write(x)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_AXIS_OUT_OF_RANGE"
    assert "LAMBDA_AXIS_OUT_OF_RANGE" in g["reason"]
    assert g["lambda_checked"] is True


def test_out_of_range_lambda_denies_even_with_permissive_floor() -> None:
    # 1.5 clears any floor numerically; it is still not a Λ.
    g = _attested_write(1.5, lambda_floor=0.01)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_AXIS_OUT_OF_RANGE"


# --- the domain edges are valid Λ values -------------------------------------

def test_lambda_of_one_is_in_range_and_passes_the_floor() -> None:
    g = _attested_write(1.0)
    assert g["allow"] is True
    assert g["lambda_error"] is None
    assert g["lambda_checked"] is True


def test_int_lambda_in_range_is_accepted() -> None:
    g = _attested_write(1)
    assert g["allow"] is True
    assert g["lambda_error"] is None


@pytest.mark.parametrize("x", [0.0, -0.0])
def test_lambda_of_zero_is_a_veto_not_an_error(x) -> None:
    g = _attested_write(x)
    assert g["allow"] is False
    assert g["lambda_error"] is None
    assert "< floor" in g["reason"]


def test_lambda_below_floor_still_denies_without_error_code() -> None:
    g = _attested_write(0.5)
    assert g["allow"] is False
    assert g["lambda_error"] is None
    assert "< floor" in g["reason"]


def test_lambda_at_or_above_floor_with_attestation_allows() -> None:
    for x in (LAMBDA_FLOOR_DEFAULT, 0.95):
        g = _attested_write(x)
        assert g["allow"] is True, x
        assert g["lambda_error"] is None
        assert g["advisories"] == []


def test_valid_lambda_without_attestation_still_denies() -> None:
    g = gate("write", state_changing=True, two_person_attested=False, lambda_score=0.95)
    assert g["allow"] is False
    assert g["lambda_error"] is None


# --- the floor itself must be a valid threshold ------------------------------

@pytest.mark.parametrize("floor", [NAN, INF, -INF, 1.5, -0.1, 0.0, True, "0.9", 10**400],
                         ids=["nan", "+inf", "-inf", "1.5", "-0.1", "zero", "bool", "str",
                              "huge-int"])
def test_invalid_floor_denies_a_supplied_lambda(floor) -> None:
    # A NaN floor made `x < floor` False for every x, so any Λ passed. A zero
    # floor would pass a vetoed Λ = 0 (v1: τ in (0, 1]).
    g = _attested_write(0.0, lambda_floor=floor)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_TAU_INVALID"
    assert "LAMBDA_TAU_INVALID" in g["reason"]
    assert g["lambda_floor"] is None  # an invalid floor is never reported as a number


def test_floor_of_one_is_valid() -> None:
    assert _attested_write(1.0, lambda_floor=1)["allow"] is True
    assert _attested_write(0.99, lambda_floor=1.0)["allow"] is False


def test_invalid_floor_is_reported_before_invalid_lambda() -> None:
    g = _attested_write(NAN, lambda_floor=NAN)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_TAU_INVALID"


# --- a Λ that is not a real number --------------------------------------------

@pytest.mark.parametrize("x", [True, False, "0.95", "nan", [0.95], object()],
                         ids=["true", "false", "str", "str-nan", "list", "object"])
def test_non_real_lambda_denies(x) -> None:
    # float(True) == 1.0 and float("0.95") == 0.95 used to pass the floor.
    g = _attested_write(x)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_TYPE_INVALID"
    assert "LAMBDA_TYPE_INVALID" in g["reason"]


@pytest.mark.parametrize("x", [10**400, -(10**400), 10**5000], ids=["1e400", "-1e400", "1e5000"])
def test_huge_int_lambda_is_out_of_range_not_a_crash(x) -> None:
    # Too large for a float and, at 5000 digits, too long for repr(): still a deny.
    g = _attested_write(x)
    assert g["allow"] is False
    assert g["lambda_error"] == "LAMBDA_AXIS_OUT_OF_RANGE"


# --- an absent Λ is unchanged (owner decision deferred) ----------------------

def test_absent_lambda_on_attested_state_change_stays_annotated_advisory() -> None:
    g = gate("deploy", state_changing=True, two_person_attested=True)
    assert g["allow"] is True
    assert g["lambda_checked"] is False
    assert g["lambda_error"] is None
    assert g["advisories"] and "UNCHECKED" in g["advisories"][0]


def test_absent_lambda_without_attestation_still_denies() -> None:
    g = gate("deploy", state_changing=True)
    assert g["allow"] is False
    assert g["lambda_error"] is None


def test_absent_lambda_on_read_allows_without_advisory() -> None:
    g = gate("read", state_changing=False)
    assert g["allow"] is True
    assert g["lambda_error"] is None
    assert g["advisories"] == []


def test_demo_human_lock_does_not_attest_two_person_approval() -> None:
    lock = HumanLock()
    assert lock.admit("imprint")["decision"] == Decision.BLOCKED.value
    lock.engage()
    adm = lock.admit("imprint")
    assert adm["decision"] == Decision.BLOCKED.value
    assert adm["autonomy"]["two_person_attested"] is False
    assert adm["approval_status"] == "UNVERIFIED_DEMO"
    assert adm["autonomy"]["lambda_error"] is None

