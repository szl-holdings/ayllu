"""Offline workflow hygiene: least privilege, SHA pins, and no dispatch secret in a logged env."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

WORKFLOWS = sorted((Path(__file__).resolve().parents[1] / ".github" / "workflows").glob("*.yml"))
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _steps(wf: dict):
    for job in (wf.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            yield step


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_top_level_permissions_are_declared_and_not_write_all(path: Path) -> None:
    wf = _load(path)
    assert "permissions" in wf, f"{path.name}: no top-level permissions"
    assert wf["permissions"] not in ("write-all", "read-all"), path.name


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_every_action_and_reusable_is_sha_pinned(path: Path) -> None:
    wf = _load(path)
    refs = [job["uses"] for job in (wf.get("jobs") or {}).values() if "uses" in job]
    refs += [step["uses"] for step in _steps(wf) if "uses" in step]
    for ref in refs:
        if ref.startswith("./"):
            continue
        _, _, pin = ref.partition("@")
        assert SHA40.match(pin), f"{path.name}: {ref} is not pinned by commit sha"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_dispatch_inputs_never_ride_in_a_masking_step_env(path: Path) -> None:
    # The runner prints a step's env in its log header before ::add-mask:: takes effect.
    for step in _steps(_load(path)):
        if "add-mask" not in str(step.get("run") or ""):
            continue
        for value in (step.get("env") or {}).values():
            assert "github.event.inputs" not in str(value), f"{path.name}: {step.get('name')}"
            assert "inputs." not in str(value), f"{path.name}: {step.get('name')}"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_dispatch_inputs_never_ride_in_a_masking_step_condition(path: Path) -> None:
    # With step debug logging on, the runner traces the realized `if:` expression
    # ("Expanded: ...") before the step runs, so the unmasked value would be printed.
    for step in _steps(_load(path)):
        if "add-mask" not in str(step.get("run") or ""):
            continue
        condition = str(step.get("if") or "")
        assert "inputs." not in condition, f"{path.name}: {step.get('name')}"
