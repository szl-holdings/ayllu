import json
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
