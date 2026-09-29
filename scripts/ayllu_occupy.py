#!/usr/bin/env python3
"""Verify the SZLHOLDINGS/ayllu occupancy from outside. Read-only.

This script never writes the Hub and needs no token. The only writer of the
Space is .github/workflows/hf-space.yml (reusable-hf-deploy, lock
hf-write/space/SZLHOLDINGS/ayllu), which runs on every push to main. To
publish, merge to main or dispatch that workflow.

Space secrets such as XAI_API_KEY are owner settings on the Hub; this script
does not set them. Absent XAI_API_KEY, the backend stays SOFTWARE.

Never fabricates LIVE. Λ = Conjecture 1.
Runtime OPERATIONAL. Legal authority PROPOSAL_ONLY.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

HF = "SZLHOLDINGS/ayllu"
HOST = "https://SZLHOLDINGS-ayllu.hf.space"
PAGE = "https://huggingface.co/spaces/SZLHOLDINGS/ayllu"
SMOKE = [
    "/",
    "/counsel",
    "/psyche",
    "/health",
    "/readyz",
    "/api/v1/ayllu/roster",
    "/api/v1/ayllu/manifest",
    "/api/v1/ayllu/retrieve?q=lambda",
    "/api/v1/counsel/health",
    "/api/v1/counsel/docket",
    "/api/v1/counsel/snapshot",
    "/api/v1/counsel/allodial",
    "/api/v1/psyche/health",
    "/api/v1/psyche/winay",
    "/api/v1/psyche/cogitate",
    "/api/v1/psyche/lattice",
    "/api/v1/psyche/ruray",
]


def get(url: str, timeout: int = 20):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return res.status, res.read()[:4000]
    except urllib.error.HTTPError as err:
        return err.code, err.read()[:400] if err.fp else b""
    except Exception as err:
        return 0, str(err).encode()


def post(url: str, payload: dict, timeout: int = 30):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read()[:4000]
    except urllib.error.HTTPError as err:
        return err.code, err.read()[:400] if err.fp else b""
    except Exception as err:
        return 0, str(err).encode()


def space_info() -> dict | None:
    """Anonymous Space API read. None when the Hub does not answer with JSON."""
    try:
        with urllib.request.urlopen(f"https://huggingface.co/api/spaces/{HF}", timeout=20) as res:
            return json.loads(res.read())
    except Exception:  # noqa: BLE001 — reported as UNAVAILABLE, never raised
        return None


def main() -> int:
    info = space_info()
    if info is None:
        print("Space API UNAVAILABLE — Hub occupancy not measured. Not fabricated LIVE.")
        return 2
    runtime = info.get("runtime") or {}
    print(f"REPORTED space id={info.get('id')} sha={info.get('sha')} "
          f"stage={runtime.get('stage')} runtime_sha={runtime.get('sha')}")
    print("page", PAGE)
    print("runtime", HOST)
    deadline = time.time() + 600
    last = {}
    while time.time() < deadline:
        last = {}
        ok = True
        for path in SMOKE:
            status, _ = get(HOST + path)
            last[path] = status
            if status != 200:
                ok = False
        print("smoke", json.dumps(last))
        if ok:
            beat_status, beat_body = post(
                HOST + "/api/v1/psyche/beat",
                {"cue": "occupy production pulse", "human_lock": True, "seat": "Maskaq"},
            )
            infer_status, infer_body = post(
                HOST + "/api/v1/counsel/infer",
                {
                    "action": "policy",
                    "prompt": "Production occupy policy scan. Informational only.",
                    "human_lock": True,
                },
            )
            print("beat", beat_status)
            print("infer_policy", infer_status)
            if beat_status != 200 or infer_status != 200:
                print("ROADMAP — POST smoke failed. Do not label LIVE.")
                print(beat_body[:400])
                print(infer_body[:400])
                return 6
            print("OCCUPANCY MEASURED")
            print("runtime OPERATIONAL legal_authority PROPOSAL_ONLY agi CONJECTURE")
            return 0
        time.sleep(15)
    print("ROADMAP — smoke not all-200 in 600s. Do not label LIVE.")
    print(json.dumps(last))
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
