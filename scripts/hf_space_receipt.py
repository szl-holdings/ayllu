#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Space contract and post-deploy receipt for SZLHOLDINGS/ayllu.

Used only by .github/workflows/hf-space.yml, the single Hub writer for this
Space. Stdlib only. Reads the public Hub API anonymously and never writes the
Hub: the write happens inside szl-holdings/.github reusable-hf-deploy.yml.

  contract  Validate .hf-space.json against the workflow's literal target and
            print GitHub step outputs: smoke_paths, wait_running and
            hub_oid_before (the Hub head before this run wrote anything).
  receipt   After the deploy, read the Hub back and fail closed unless
            hub_oid == created_oid, the Space runtime reports that same sha in
            RUNNING, and GET /healthz returns HTTP 200. Writes a JSON receipt.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

HUB = "https://huggingface.co"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_SMOKE = "/healthz"

# fetch(url) -> (http_status, body_bytes). Injected so tests never touch the network.
Fetch = Callable[[str], "tuple[int, bytes]"]


class ContractError(Exception):
    """The committed Space contract or the Hub state does not hold."""


def http_fetch(url: str, timeout: int = 20) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "Cache-Control": "no-cache"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as err:
        return err.code, err.read() if err.fp else b""
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return 0, str(err).encode()


def fetch_json(fetch: Fetch, url: str, retries: int = 5, delay: float = 5.0) -> Any:
    last = "not attempted"
    for attempt in range(max(1, retries)):
        status, body = fetch(url)
        if status == 200:
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                last = "HTTP 200 with a non-JSON body"
        else:
            last = f"HTTP {status}"
        if attempt + 1 < retries:
            time.sleep(delay)
    raise ContractError(f"{url}: {last}")


def space_origin(space: str) -> str:
    owner, _, name = space.partition("/")
    if not owner or not name or "/" in name:
        raise ContractError(f"Space id must be <owner>/<name>: {space!r}")
    return f"https://{owner.lower()}-{name.lower()}.hf.space"


def hub_head(fetch: Fetch, space: str) -> str:
    body = fetch_json(fetch, f"{HUB}/api/spaces/{space}/revision/main")
    sha = str((body or {}).get("sha") or "")
    if not SHA40.match(sha):
        raise ContractError(f"Hub revision/main for {space} has no 40-hex sha: {sha!r}")
    return sha


# --------------------------------------------------------------------------- #
# contract
# --------------------------------------------------------------------------- #
def load_contract(path: Path, *, space: str, github_repo: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"{path}: unreadable Space contract ({exc})") from exc
    if data.get("target") != space:
        raise ContractError(
            f"{path}: target {data.get('target')!r} != workflow target {space!r}"
        )
    if data.get("source_repository") != github_repo:
        raise ContractError(
            f"{path}: source_repository {data.get('source_repository')!r} "
            f"!= running repository {github_repo!r}"
        )
    smoke = data.get("smoke_paths")
    if not isinstance(smoke, list) or not smoke or not all(
        isinstance(p, str) and p.startswith("/") and not p.startswith("//") for p in smoke
    ):
        raise ContractError(f"{path}: smoke_paths must be a list of same-host paths")
    if REQUIRED_SMOKE not in smoke:
        raise ContractError(f"{path}: smoke_paths must include {REQUIRED_SMOKE}")
    wait = data.get("wait_running_seconds")
    if not isinstance(wait, int) or isinstance(wait, bool) or not 60 <= wait <= 1800:
        raise ContractError(f"{path}: wait_running_seconds must be an int in [60, 1800]")
    return {"smoke_paths": smoke, "wait_running": wait}


def cmd_contract(args: argparse.Namespace, fetch: Fetch) -> int:
    contract = load_contract(
        Path(args.contract), space=args.space, github_repo=args.github_repo
    )
    before = hub_head(fetch, args.space)
    lines = [
        f"smoke_paths={json.dumps(contract['smoke_paths'], separators=(',', ':'))}",
        f"wait_running={contract['wait_running']}",
        f"hub_oid_before={before}",
    ]
    out = sys.stdout if args.github_output in ("", "-") else open(
        args.github_output, "a", encoding="utf-8"
    )
    try:
        for line in lines:
            out.write(line + "\n")
    finally:
        if out is not sys.stdout:
            out.close()
    print(f"contract OK: {args.space} smoke={len(contract['smoke_paths'])} "
          f"wait={contract['wait_running']}s hub_oid_before={before}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #
# receipt
# --------------------------------------------------------------------------- #
def build_receipt(
    fetch: Fetch,
    *,
    manifest: dict[str, Any],
    space: str,
    github_repo: str,
    source_sha: str,
    hub_oid_before: str,
    run_url: str,
    auth: str,
    lock: str,
    poll_seconds: int = 300,
    poll_interval: float = 10.0,
    now: Callable[[], str] | None = None,
) -> dict[str, Any]:
    failures: list[str] = []

    created_oid = str(manifest.get("hf_commit_oid") or "").lower()
    if not SHA40.match(created_oid):
        failures.append("manifest.hf_commit_oid is not a 40-hex commit sha")
    if manifest.get("hf_repo") != space:
        failures.append(f"manifest.hf_repo {manifest.get('hf_repo')!r} != {space!r}")
    if manifest.get("github_repo") != github_repo:
        failures.append(
            f"manifest.github_repo {manifest.get('github_repo')!r} != {github_repo!r}"
        )
    if manifest.get("ref") != source_sha:
        failures.append(f"manifest.ref {manifest.get('ref')!r} != source sha {source_sha!r}")
    if manifest.get("unresolved_sources") != []:
        failures.append("manifest has unresolved Dockerfile COPY sources")

    hub_oid = ""
    try:
        hub_oid = hub_head(fetch, space)
    except ContractError as exc:
        failures.append(str(exc))
    if hub_oid and created_oid and hub_oid != created_oid:
        failures.append(f"hub_oid {hub_oid} != created_oid {created_oid}")

    new_commit = bool(created_oid) and created_oid != hub_oid_before
    commit_title = None
    if new_commit and created_oid:
        try:
            commits = fetch_json(fetch, f"{HUB}/api/spaces/{space}/commits/main?limit=5")
            match = next(
                (c for c in commits or [] if str(c.get("id") or "") == created_oid), None
            )
            commit_title = (match or {}).get("title")
            if not match:
                failures.append(f"created commit {created_oid} not in the Hub history")
            elif source_sha not in str(commit_title or ""):
                failures.append(f"Hub commit title does not name source sha {source_sha}")
        except ContractError as exc:
            failures.append(str(exc))

    # The reusable deployer already waited for RUNNING at created_oid; poll
    # briefly again so the receipt records what the Hub reports right now.
    stage = runtime_sha = None
    deadline = time.monotonic() + max(0, poll_seconds)
    while True:
        try:
            info = fetch_json(fetch, f"{HUB}/api/spaces/{space}", retries=2, delay=2)
            runtime = (info or {}).get("runtime") or {}
            stage, runtime_sha = runtime.get("stage"), runtime.get("sha")
        except ContractError:
            stage = runtime_sha = None
        if (stage == "RUNNING" and runtime_sha == created_oid) or time.monotonic() >= deadline:
            break
        time.sleep(poll_interval)
    if stage != "RUNNING":
        failures.append(f"runtime.stage is {stage!r}, not RUNNING")
    if runtime_sha != created_oid:
        failures.append(f"runtime.sha {runtime_sha!r} != created_oid {created_oid}")

    healthz_url = space_origin(space) + REQUIRED_SMOKE
    healthz_http = 0
    for attempt in range(6):
        healthz_http, _ = fetch(healthz_url)
        if healthz_http == 200:
            break
        if attempt < 5:
            time.sleep(5)
    if healthz_http != 200:
        failures.append(f"GET {healthz_url} returned HTTP {healthz_http}")

    stamp = now() if now else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": "szl.hf-space-deploy-receipt/v1",
        "ts": stamp,
        "github_repo": github_repo,
        "source_sha": source_sha,
        "hf_repo": space,
        "auth": auth,
        "lock": lock,
        "hub_oid_before": hub_oid_before or None,
        "created_oid": created_oid or None,
        "hub_oid": hub_oid or None,
        "hub_oid_equals_created_oid": bool(hub_oid) and hub_oid == created_oid,
        "new_commit": new_commit,
        "hub_commit_title": commit_title,
        "runtime_stage": stage,
        "runtime_sha": runtime_sha,
        "healthz_url": healthz_url,
        "healthz_http": healthz_http,
        "files_deployed": manifest.get("files_deployed"),
        "pruned": manifest.get("pruned"),
        "run_url": run_url,
        "verdict": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def cmd_receipt(args: argparse.Namespace, fetch: Fetch) -> int:
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"::error::deploy manifest unavailable: {exc}")
        manifest = {}
    receipt = build_receipt(
        fetch,
        manifest=manifest,
        space=args.space,
        github_repo=args.github_repo,
        source_sha=args.source_sha,
        hub_oid_before=args.hub_oid_before,
        run_url=args.run_url,
        auth=args.auth,
        lock=args.lock,
        poll_seconds=args.poll_seconds,
    )
    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(f"### {args.space} deploy receipt: {receipt['verdict']}\n\n")
            fh.write("| field | value |\n|---|---|\n")
            for key in ("source_sha", "created_oid", "hub_oid", "hub_oid_equals_created_oid",
                        "new_commit", "runtime_stage", "runtime_sha", "healthz_http", "auth", "lock"):
                fh.write(f"| `{key}` | `{receipt[key]}` |\n")
            for failure in receipt["failures"]:
                fh.write(f"\n- FAIL: {failure}")
            fh.write("\n")
    for failure in receipt["failures"]:
        print(f"::error title=HF deploy receipt::{failure}")
    return 0 if receipt["verdict"] == "PASS" else 1


def main(argv: list[str] | None = None, fetch: Fetch = http_fetch) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("contract")
    c.add_argument("--contract", default=".hf-space.json")
    c.add_argument("--space", required=True)
    c.add_argument("--github-repo", required=True)
    c.add_argument("--github-output", default="-")

    r = sub.add_parser("receipt")
    r.add_argument("--manifest", required=True)
    r.add_argument("--space", required=True)
    r.add_argument("--github-repo", required=True)
    r.add_argument("--source-sha", required=True)
    r.add_argument("--hub-oid-before", default="")
    r.add_argument("--run-url", default="")
    r.add_argument("--auth", required=True)
    r.add_argument("--lock", required=True)
    r.add_argument("--poll-seconds", type=int, default=300)
    r.add_argument("--out", required=True)
    r.add_argument("--summary", default="")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "contract":
            return cmd_contract(args, fetch)
        return cmd_receipt(args, fetch)
    except ContractError as exc:
        print(f"::error::{exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
