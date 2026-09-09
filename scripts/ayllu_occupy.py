#!/usr/bin/env python3
"""Occupy SZLHOLDINGS/ayllu from this checkout.

HF_TOKEN required. XAI_API_KEY optional.
Never fabricates LIVE. Λ = Conjecture 1.
Runtime OPERATIONAL. Legal authority PROPOSAL_ONLY.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError

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


def main() -> int:
    token = os.environ.get("HF_TOKEN") or ""
    if not token:
        print("HF_TOKEN UNAVAILABLE — Hub occupancy ROADMAP. Not fabricated LIVE.")
        return 2
    api = HfApi(token=token)
    try:
        info = api.repo_info(repo_id=HF, repo_type="space")
        print(f"REPORTED space exists id={info.id}")
    except HfHubHTTPError as exc:
        code = exc.response.status_code if exc.response is not None else 0
        print(f"repo_info status={code} — creating Docker Space")
        try:
            api.create_repo(
                repo_id=HF,
                repo_type="space",
                space_sdk="docker",
                exist_ok=True,
                private=False,
            )
            print("created", HF)
        except HfHubHTTPError as create_exc:
            print("create_repo FAILED. Rate limit? Keep the name ayllu.")
            print(create_exc)
            return 3
    api.upload_folder(
        folder_path=".",
        repo_id=HF,
        repo_type="space",
        ignore_patterns=[
            ".git*",
            "tests/*",
            ".venv/*",
            ".pytest_cache/*",
            "**/__pycache__/*",
            "**/*.pyc",
        ],
    )
    print("uploaded →", HF)
    xai = os.environ.get("XAI_API_KEY") or ""
    if xai:
        api.add_space_secret(HF, "XAI_API_KEY", xai)
        print("secret XAI_API_KEY set")
    else:
        print("XAI_API_KEY UNAVAILABLE — backend stays SOFTWARE")
    api.add_space_variable(HF, "AYLLU_MODEL", "grok-4.5")
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
