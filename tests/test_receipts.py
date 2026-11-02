import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from io import StringIO

from ayllu.receipts import make_receipt, sha256_json
from scripts.verify_receipt import verify


def test_unsigned_receipt_verifies() -> None:
    env = make_receipt({"hello": "ayllu"})
    result = verify(env)
    assert result["ok"] is True
    assert result["signed"] is False
    raw = json.loads(__import__("base64").b64decode(env["payload"]))
    assert raw["hello"] == "ayllu"
    assert sha256_json({"a": 1}) == sha256_json({"a": 1})


def test_forged_signed_flag_fails() -> None:
    env = make_receipt({"hello": "ayllu"})
    env["signed"] = True
    result = verify(env)
    assert result["ok"] is False


@pytest.mark.parametrize("envelope", [
    {},
    {"payload": base64.b64encode(b"{}").decode()},
    {"payload": "", "payloadSha256": hashlib.sha256(b"").hexdigest()},
    {"payload": "!!!!", "payloadSha256": hashlib.sha256(b"").hexdigest()},
    {"payload": "e30=!!!!", "payloadSha256": hashlib.sha256(b"{}").hexdigest()},
    {"payload": "e30=", "payloadSha256": None},
    {"payload": "e30=", "payloadSha256": 0},
    {"payload": "e30=", "payloadSha256": "0" * 64},
    {"payload": 123, "payloadSha256": hashlib.sha256(b"").hexdigest()},
    None,
    [],
])
def test_incomplete_or_malformed_receipts_fail_closed(envelope) -> None:
    result = verify(envelope)
    assert result["ok"] is False
    assert result["reasons"]


def test_receipt_payload_tampering_fails() -> None:
    env = make_receipt({"hello": "ayllu"})
    env["payload"] = base64.b64encode(b'{"hello":"changed"}').decode()
    assert verify(env)["ok"] is False


def test_verifier_cli_rejects_missing_digest() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_receipt.py"
    result = subprocess.run(
        [sys.executable, str(script)], input='{"payload":"e30="}',
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["ok"] is False
