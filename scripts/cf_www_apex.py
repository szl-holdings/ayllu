"""Idempotent Cloudflare edge for a-11-oy.com.

Needs CF_API_TOKEN (Zone DNS Edit + Zone Redirect Edit).
Optional CF_ZONE_ID. Skips cleanly when the token is absent.
Does not add www as a Hugging Face custom domain.
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
KILLINCHU = "killinchu.a-11-oy.com"
KILLINCHU_TARGET = "szlholdings-killinchu.hf.space"


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


def _upsert_cname(token: str, zone_id: str, name: str, content: str, proxied: bool) -> None:
    recs = _req(
        "GET",
        f"/zones/{zone_id}/dns_records?" + urllib.parse.urlencode({"name": name}),
        token,
    )
    records = recs.get("result") or []
    want = {
        "type": "CNAME",
        "name": name,
        "content": content,
        "proxied": proxied,
        "ttl": 1,
    }
    cname = next((r for r in records if r.get("type") == "CNAME"), None)
    extras = [r for r in records if r.get("type") != "CNAME"]
    for extra in extras:
        _req("DELETE", f"/zones/{zone_id}/dns_records/{extra['id']}", token)
        print("deleted", extra.get("type"), extra.get("name"), extra.get("content"))
    if cname:
        _req("PUT", f"/zones/{zone_id}/dns_records/{cname['id']}", token, want)
        print("updated CNAME", name, "->", content, "proxied", proxied)
    else:
        _req("POST", f"/zones/{zone_id}/dns_records", token, want)
        print("created CNAME", name, "->", content, "proxied", proxied)


def _www_redirect(token: str, zone_id: str) -> None:
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


def main() -> int:
    token = (os.environ.get("CF_API_TOKEN") or "").strip()
    if not token:
        print("CF_API_TOKEN UNAVAILABLE — www redirect skipped. Not fabricated LIVE.")
        return 0
    zone_id = (os.environ.get("CF_ZONE_ID") or "").strip()
    if not zone_id:
        listed = _req("GET", "/zones?" + urllib.parse.urlencode({"name": ZONE_NAME}), token)
        results = listed.get("result") or []
        if not results:
            raise SystemExit(f"No Cloudflare zone named {ZONE_NAME}")
        zone_id = results[0]["id"]
    print("zone", zone_id)

    _upsert_cname(token, zone_id, WWW, ZONE_NAME, True)
    _www_redirect(token, zone_id)
    _upsert_cname(token, zone_id, KILLINCHU, KILLINCHU_TARGET, False)
    print("www 301 wired; killinchu CNAME grey-cloud to HF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
