"""Idempotent Cloudflare edge for a-11-oy.com.

www → apex 301 (proxied CNAME + dynamic redirect).
killinchu → szlholdings-killinchu.hf.space CNAME DNS-only so HF TLS can issue.

Token from CF_API_TOKEN env (secret or workflow_dispatch input).
Skips cleanly when the token is absent. Never prints the token.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"
ZONE_NAME = "a-11-oy.com"
WWW = "www.a-11-oy.com"
APEX = "https://a-11-oy.com"
KILL = "killinchu.a-11-oy.com"
KILL_TARGET = "szlholdings-killinchu.hf.space"


def _req(method: str, path: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "SZL-ayllu-edge/1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            body = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"Cloudflare {method} {path} HTTP {exc.code}: {err[:800]}") from exc
    if not body.get("success"):
        raise SystemExit(f"Cloudflare {method} {path} failed: {body}")
    return body


def _wire_www(token: str, zone_id: str) -> None:
    recs = _req(
        "GET",
        f"/zones/{zone_id}/dns_records?" + urllib.parse.urlencode({"name": WWW}),
        token,
    )
    records = recs.get("result") or []
    want = {"type": "CNAME", "name": WWW, "content": ZONE_NAME, "proxied": True, "ttl": 1}
    cname = next((r for r in records if r.get("type") == "CNAME"), None)
    if cname:
        _req("PUT", f"/zones/{zone_id}/dns_records/{cname['id']}", token, want)
        print("updated www CNAME proxied to apex")
    else:
        for extra in records:
            _req("DELETE", f"/zones/{zone_id}/dns_records/{extra['id']}", token)
            print("deleted", extra.get("type"), extra.get("name"))
        _req("POST", f"/zones/{zone_id}/dns_records", token, want)
        print("created www CNAME proxied to apex")

    rule = {
        "ref": "www_to_apex",
        "description": "www.a-11-oy.com 301 to apex",
        "expression": f'http.request.uri.host eq "{WWW}"',
        "action": "redirect",
        "action_parameters": {
            "from_value": {
                "target_url": {
                    "expression": f'concat("{APEX}", http.request.uri.path)',
                },
                "status_code": 301,
                "preserve_query_string": True,
            }
        },
    }
    try:
        current = _req(
            "GET",
            f"/zones/{zone_id}/rulesets/phases/http_request_dynamic_redirect/entrypoint",
            token,
        )
        ruleset = current.get("result") or {}
        rid = ruleset.get("id")
        existing = [r for r in (ruleset.get("rules") or []) if r.get("ref") != "www_to_apex"]
        existing.append(rule)
        _req(
            "PUT",
            f"/zones/{zone_id}/rulesets/{rid}",
            token,
            {
                "name": ruleset.get("name") or "Redirect rules",
                "kind": "zone",
                "phase": "http_request_dynamic_redirect",
                "rules": existing,
            },
        )
        print("updated redirect ruleset", rid)
    except SystemExit as exc:
        if "404" not in str(exc):
            raise
        _req(
            "POST",
            f"/zones/{zone_id}/rulesets",
            token,
            {
                "name": "Redirect rules",
                "kind": "zone",
                "phase": "http_request_dynamic_redirect",
                "rules": [rule],
            },
        )
        print("created redirect ruleset")
    print("www 301 wired")


def _wire_killinchu(token: str, zone_id: str) -> None:
    recs = _req(
        "GET",
        f"/zones/{zone_id}/dns_records?" + urllib.parse.urlencode({"name": KILL}),
        token,
    )
    records = recs.get("result") or []
    want = {
        "type": "CNAME",
        "name": KILL,
        "content": KILL_TARGET,
        "proxied": False,
        "ttl": 1,
    }
    good = next(
        (
            r
            for r in records
            if r.get("type") == "CNAME" and r.get("content") == KILL_TARGET
        ),
        None,
    )
    for extra in records:
        if good and extra.get("id") == good.get("id"):
            continue
        _req("DELETE", f"/zones/{zone_id}/dns_records/{extra['id']}", token)
        print("deleted killinchu", extra.get("type"), extra.get("content"))
    if good:
        _req("PUT", f"/zones/{zone_id}/dns_records/{good['id']}", token, want)
        print("updated killinchu CNAME DNS-only to", KILL_TARGET)
    else:
        _req("POST", f"/zones/{zone_id}/dns_records", token, want)
        print("created killinchu CNAME DNS-only to", KILL_TARGET)


def main() -> int:
    token = (os.environ.get("CF_API_TOKEN") or "").strip()
    if not token:
        print("CF_API_TOKEN UNAVAILABLE — edge skipped. Not fabricated LIVE.")
        return 0
    zone_id = (os.environ.get("CF_ZONE_ID") or "").strip()
    if not zone_id:
        listed = _req("GET", "/zones?" + urllib.parse.urlencode({"name": ZONE_NAME}), token)
        results = listed.get("result") or []
        if not results:
            raise SystemExit(f"No Cloudflare zone named {ZONE_NAME}")
        zone_id = results[0]["id"]
    print("zone", zone_id)
    _wire_www(token, zone_id)
    _wire_killinchu(token, zone_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
