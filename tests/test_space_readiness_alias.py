"""Exercise the shipped alias functions without importing Space startup or Psyche."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.testclient import TestClient


SOURCE = Path(__file__).resolve().parents[1] / "ayllu" / "space.py"


def alias_app(result: Any = None, *, missing: bool = False) -> FastAPI:
    """Compile only route definitions; never execute module imports or boot code."""
    app = FastAPI()
    if not missing:
        @app.get("/readyz", response_model=None)
        def readyz():
            return result

    source = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
    names = {"_readyz_body", "healthz"}
    nodes = [node for node in source.body if isinstance(node, ast.FunctionDef)
             and node.name in names]
    if {node.name for node in nodes} != names:
        raise AssertionError("Space readiness alias definitions are missing")
    module = ast.Module(body=nodes, type_ignores=[])
    namespace = {"app": app, "Any": Any, "JSONResponse": JSONResponse,
                 "Response": Response}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return app


class SpaceReadinessAliasTests(unittest.TestCase):
    def test_positive_and_negative_dictionary_evidence_is_preserved(self):
        for ready in (True, False):
            with self.subTest(ready=ready):
                body = {"ready": ready, "ship": False, "evidence": "fixture"}
                client = TestClient(alias_app(body))
                self.assertEqual(client.get("/readyz").json(),
                                 client.get("/healthz").json())

    def test_json_response_preserves_negative_status_body_and_headers(self):
        original = JSONResponse(
            {"ready": False, "state": "BLOCKED", "evidence": {"receipt": None}},
            status_code=503, headers={"Retry-After": "60", "Cache-Control": "no-store"},
        )
        client = TestClient(alias_app(original))
        actual = client.get("/healthz")
        self.assertEqual(actual.status_code, 503)
        self.assertEqual(actual.content, original.body)
        self.assertEqual(actual.headers["retry-after"], "60")
        self.assertEqual(actual.headers["cache-control"], "no-store")

    def test_negative_evidence_in_http_200_is_not_promoted(self):
        original = JSONResponse({"ready": False, "state": "UNAVAILABLE"})
        actual = TestClient(alias_app(original)).get("/healthz")
        self.assertEqual(actual.status_code, 200)
        self.assertEqual(actual.content, original.body)

    def test_positive_json_response_is_forwarded_without_reconstruction(self):
        original = JSONResponse({"ready": True, "evidence": "fixture"},
                                headers={"X-Evidence": "fixture"})
        actual = TestClient(alias_app(original)).get("/healthz")
        self.assertEqual(actual.status_code, 200)
        self.assertEqual(actual.content, original.body)
        self.assertEqual(actual.headers["x-evidence"], "fixture")

    def test_other_response_failure_is_not_replaced_with_success(self):
        original = Response("maintenance", status_code=502, media_type="text/plain")
        actual = TestClient(alias_app(original)).get("/healthz")
        self.assertEqual(actual.status_code, 502)
        self.assertEqual(actual.content, original.body)

    def test_missing_readiness_endpoint_fails_closed(self):
        actual = TestClient(alias_app(missing=True)).get("/healthz")
        self.assertEqual(actual.status_code, 503)
        self.assertIs(actual.json()["ready"], False)
        self.assertEqual(actual.json()["state"], "READINESS_EVIDENCE_UNAVAILABLE")

    def test_unsupported_readiness_results_fail_closed(self):
        for result in (None, True, "ready", [], 1):
            with self.subTest(result=result):
                actual = TestClient(alias_app(result)).get("/healthz")
                self.assertEqual(actual.status_code, 503)
                self.assertIs(actual.json()["ready"], False)


if __name__ == "__main__":
    unittest.main()
