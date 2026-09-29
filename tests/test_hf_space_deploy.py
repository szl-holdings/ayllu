"""Contract for the single Hub writer of SZLHOLDINGS/ayllu.

Offline: the workflow, Dockerfile and Space contract are parsed from the
checkout, and the receipt logic runs against an injected fake Hub.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "hf-space.yml"
SPACE = "SZLHOLDINGS/ayllu"
LOCK = "hf-write/space/SZLHOLDINGS/ayllu"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _load_receipt_module():
    spec = importlib.util.spec_from_file_location(
        "hf_space_receipt", ROOT / "scripts" / "hf_space_receipt.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["hf_space_receipt"] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load_receipt_module()


@pytest.fixture()
def wf() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_workflow_is_a_thin_pinned_reusable_caller(wf: dict) -> None:
    deploy = wf["jobs"]["deploy"]
    uses = deploy["uses"]
    path, _, ref = uses.partition("@")
    assert path == "szl-holdings/.github/.github/workflows/reusable-hf-deploy.yml"
    assert SHA40.match(ref), f"reusable must be pinned by commit sha, got {ref!r}"
    w = deploy["with"]
    assert w["hf-repo"] == SPACE
    assert w["ref"] == "${{ github.sha }}"
    assert w["require-default-branch-tip"] is True
    assert "healthz" not in str(w.get("smoke-paths")), "smoke paths come from .hf-space.json"
    assert deploy["secrets"] == {"HF_TOKEN": "${{ secrets.HF_TOKEN }}"}


def test_workflow_holds_one_per_asset_lock(wf: dict) -> None:
    conc = wf["concurrency"]
    assert conc == {"group": LOCK, "cancel-in-progress": False}
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "event_name" not in text
    assert f"--lock {LOCK}" in text


def test_missing_credential_fails_instead_of_skipping(wf: dict) -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "sys.exit(0)" not in text
    assert "skipped" not in text.lower()
    steps = wf["jobs"]["plan"]["steps"]
    gate = next(s for s in steps if "HF_TOKEN_PRESENT" in (s.get("env") or {}))
    assert gate["env"]["HF_TOKEN_PRESENT"] == "${{ secrets.HF_TOKEN != '' }}"
    assert "exit 2" in gate["run"]
    assert wf["jobs"]["deploy"]["needs"] == "plan"


def test_every_action_is_sha_pinned(wf: dict) -> None:
    for name, job in wf["jobs"].items():
        for step in job.get("steps") or []:
            uses = step.get("uses")
            if uses:
                assert SHA40.match(uses.partition("@")[2]), f"{name}: {uses}"


def test_receipt_job_reads_back_the_hub(wf: dict) -> None:
    job = wf["jobs"]["receipt"]
    assert job["needs"] == ["plan", "deploy"]
    run = next(s["run"] for s in job["steps"] if "hf_space_receipt.py receipt" in (s.get("run") or ""))
    for flag in ("--manifest evidence/hf-deploy-manifest.json", "--source-sha", "--hub-oid-before", "--auth PAT"):
        assert flag in run


def test_space_contract_matches_workflow() -> None:
    contract = R.load_contract(ROOT / ".hf-space.json", space=SPACE, github_repo="szl-holdings/ayllu")
    assert contract["smoke_paths"][0] == "/healthz"
    data = json.loads((ROOT / ".hf-space.json").read_text(encoding="utf-8"))
    assert data["lock"] == LOCK
    assert data["writer"] == ".github/workflows/hf-space.yml"
    assert "files" not in data, "the deploy set is derived from Dockerfile COPY, never listed"


def test_dockerfile_is_digest_pinned_with_healthz() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    froms = [ln for ln in text.splitlines() if ln.startswith("FROM ")]
    assert froms and all(re.search(r"@sha256:[0-9a-f]{64}(\s|$)", ln) for ln in froms), froms
    assert re.search(r"^HEALTHCHECK .*\\$", text, re.M)
    assert "http://127.0.0.1:7860/healthz" in text
    for src in re.findall(r"^COPY\s+(\S+)\s+\S+$", text, re.M):
        assert (ROOT / src).exists(), f"COPY source missing: {src}"


def test_no_other_hub_writer_in_this_repo() -> None:
    mutators = re.compile(
        r"\b(upload_folder|upload_file|create_commit|create_repo|delete_repo|"
        r"add_space_secret|add_space_variable|restart_space|HfApi\s*\()"
    )
    offenders = []
    for path in list(ROOT.glob("*.py")) + list((ROOT / "ayllu").rglob("*.py")) + list((ROOT / "scripts").glob("*.py")):
        if mutators.search(path.read_text(encoding="utf-8", errors="replace")):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"Hub write paths outside hf-space.yml: {offenders}"


def test_healthz_route_serves_200() -> None:
    from fastapi.testclient import TestClient

    from ayllu.space import app

    res = TestClient(app).get("/healthz")
    assert res.status_code == 200
    assert res.json()["lambda"] == "CONJECTURE_1"


# --------------------------------------------------------------------------- #
# receipt logic against a fake Hub
# --------------------------------------------------------------------------- #
SRC = "a" * 40
BEFORE = "b" * 40
CREATED = "c" * 40


def _manifest(**over):
    m = {
        "hf_commit_oid": CREATED,
        "hf_repo": SPACE,
        "github_repo": "szl-holdings/ayllu",
        "ref": SRC,
        "unresolved_sources": [],
        "files_deployed": 75,
        "pruned": [],
    }
    m.update(over)
    return m


def _hub(head=CREATED, stage="RUNNING", runtime_sha=CREATED, healthz=200, title=None):
    title = title if title is not None else f"deploy(hf): sync szl-holdings/ayllu@{SRC} derived COPY set"

    def fetch(url):
        if url.endswith("/revision/main"):
            return 200, json.dumps({"sha": head}).encode()
        if "/commits/main" in url:
            return 200, json.dumps([{"id": head, "title": title}]).encode()
        if url.endswith(f"/api/spaces/{SPACE}"):
            return 200, json.dumps({"runtime": {"stage": stage, "sha": runtime_sha}}).encode()
        if url == "https://szlholdings-ayllu.hf.space/healthz":
            return healthz, b"{}"
        raise AssertionError(url)

    return fetch


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(R.time, "sleep", lambda _s: None)


def _receipt(fetch, manifest=None, before=BEFORE):
    return R.build_receipt(
        fetch,
        manifest=manifest or _manifest(),
        space=SPACE,
        github_repo="szl-holdings/ayllu",
        source_sha=SRC,
        hub_oid_before=before,
        run_url="https://github.com/szl-holdings/ayllu/actions/runs/1",
        auth="PAT",
        lock=LOCK,
        poll_seconds=0,
        now=lambda: "2026-09-29T00:00:00Z",
    )


def test_receipt_pass_records_hub_oid_equal_created_oid() -> None:
    rec = _receipt(_hub())
    assert rec["verdict"] == "PASS", rec["failures"]
    assert rec["hub_oid"] == rec["created_oid"] == CREATED
    assert rec["hub_oid_equals_created_oid"] is True
    assert rec["new_commit"] is True
    assert rec["runtime_stage"] == "RUNNING" and rec["healthz_http"] == 200


def test_receipt_fails_when_the_hub_moved_past_our_commit() -> None:
    rec = _receipt(_hub(head="d" * 40))
    assert rec["verdict"] == "FAIL"
    assert rec["hub_oid_equals_created_oid"] is False


def test_receipt_fails_on_unhealthy_or_stale_runtime() -> None:
    assert _receipt(_hub(healthz=503))["verdict"] == "FAIL"
    assert _receipt(_hub(stage="BUILD_ERROR"))["verdict"] == "FAIL"
    assert _receipt(_hub(runtime_sha=BEFORE))["verdict"] == "FAIL"


def test_receipt_fails_when_commit_does_not_name_source() -> None:
    assert _receipt(_hub(title="Upload folder using huggingface_hub"))["verdict"] == "FAIL"


def test_noop_deploy_is_honest_about_no_new_commit() -> None:
    rec = _receipt(_hub(), before=CREATED)
    assert rec["verdict"] == "PASS", rec["failures"]
    assert rec["new_commit"] is False


def test_receipt_fails_on_manifest_for_another_ref() -> None:
    assert _receipt(_hub(), manifest=_manifest(ref="e" * 40))["verdict"] == "FAIL"


def test_contract_rejects_missing_healthz(tmp_path) -> None:
    bad = json.loads((ROOT / ".hf-space.json").read_text(encoding="utf-8"))
    bad["smoke_paths"] = ["/"]
    p = tmp_path / "c.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(R.ContractError):
        R.load_contract(p, space=SPACE, github_repo="szl-holdings/ayllu")
    bad["smoke_paths"] = ["/healthz"]
    bad["target"] = "SZLHOLDINGS/other"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(R.ContractError):
        R.load_contract(p, space=SPACE, github_repo="szl-holdings/ayllu")
