"""Grok model pin: one reviewed constant, allowlisted override, fail-closed.

Every network call is mocked. No test here contacts xAI.
"""
from __future__ import annotations

import asyncio
import json
import re
import urllib.request
from pathlib import Path

import pytest

from ayllu import backend, counsel
from ayllu.grok_model import (
    ALLOWED_GROK_MODELS,
    DEFAULT_GROK_MODEL,
    GROK_MODEL_ENV,
    grok_label,
    grok_model,
)

ROOT = Path(__file__).resolve().parents[1]
# Parameters xAI rejects on reasoning models. Never send them.
FORBIDDEN_PARAMS = {"stop", "presence_penalty", "frequency_penalty", "presencePenalty", "frequencyPenalty"}


class _Resp:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _Recorder:
    """Stands in for urllib.request.urlopen and records every request."""

    def __init__(self, content: str = "mocked completion") -> None:
        self.calls: list[tuple[str, dict | None]] = []
        self.content = content

    def __call__(self, req, timeout=None):  # noqa: ANN001
        url = req.full_url if hasattr(req, "full_url") else str(req)
        body = json.loads(req.data.decode("utf-8")) if getattr(req, "data", None) else None
        self.calls.append((url, body))
        if url.endswith("/chat/completions"):
            return _Resp({"choices": [{"message": {"content": self.content}}]})
        return _Resp({"data": []})

    def xai_calls(self) -> list[tuple[str, dict | None]]:
        return [c for c in self.calls if c[0].startswith(backend.XAI_BASE) or c[0].startswith(counsel.XAI)]


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in (GROK_MODEL_ENV, "XAI_API_KEY", "AYLLU_MODEL"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def recorder(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    rec = _Recorder()
    monkeypatch.setattr(urllib.request, "urlopen", rec)
    return rec


# ---- resolver ---------------------------------------------------------------


def test_default_is_grok_4_7(clean_env: pytest.MonkeyPatch) -> None:
    assert DEFAULT_GROK_MODEL == "grok-4.7"
    assert ALLOWED_GROK_MODELS == ("grok-4.7", "grok-4.5")
    assert grok_model() == "grok-4.7"
    assert grok_label() == "Grok 4.7"


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_blank_override_uses_default(clean_env: pytest.MonkeyPatch, blank: str) -> None:
    clean_env.setenv(GROK_MODEL_ENV, blank)
    assert grok_model() == DEFAULT_GROK_MODEL


@pytest.mark.parametrize("value", ["grok-4.5", "  grok-4.5  "])
def test_rollback_override_is_honoured(clean_env: pytest.MonkeyPatch, value: str) -> None:
    clean_env.setenv(GROK_MODEL_ENV, value)
    assert grok_model() == "grok-4.5"


@pytest.mark.parametrize(
    "value",
    ["grok-4.6", "grok-4.7-latest", "grok-latest", "GROK-4.7", "grok-4.5 ; drop", "gpt-4o-mini"],
)
def test_unlisted_override_fails_closed(clean_env: pytest.MonkeyPatch, value: str) -> None:
    clean_env.setenv(GROK_MODEL_ENV, value)
    assert grok_model() is None


# ---- counsel (legal briefs) ------------------------------------------------


def test_counsel_sends_default_pin(clean_env: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    out = counsel.grok_complete("sys", "matter")
    assert out["ok"] is True
    assert out["model"] == "grok-4.7"
    assert len(recorder.calls) == 1
    url, body = recorder.calls[0]
    assert url == f"{counsel.XAI}/chat/completions"
    assert body["model"] == "grok-4.7"
    assert not FORBIDDEN_PARAMS & set(body)


def test_counsel_honours_rollback_override(clean_env: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.5")
    out = counsel.grok_complete("sys", "matter")
    assert out["model"] == "grok-4.5"
    assert recorder.calls[0][1]["model"] == "grok-4.5"


def test_counsel_unlisted_override_is_unavailable_with_zero_calls(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.6")
    out = counsel.grok_complete("sys", "matter")
    assert out["ok"] is False
    assert out["honesty"] == "UNAVAILABLE"
    assert out["model"] is None
    assert out["text"].startswith("UNAVAILABLE")
    assert "grok-4.6" not in out["text"]  # the rejected value is never echoed
    assert "test-not-a-real-key" not in out["text"]
    assert recorder.calls == []


def test_counsel_missing_key_is_unavailable_with_zero_calls(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    out = counsel.grok_complete("sys", "matter")
    assert out["honesty"] == "UNAVAILABLE"
    assert out["model"] is None
    assert recorder.calls == []


def test_counsel_receipt_names_resolved_model(clean_env: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    out = counsel.infer(action="estate-synth", prompt="Summarize the catalog.", human_lock=True)
    assert out["model"] == "grok-4.7"
    assert out["receipt"]["model"] == "grok-4.7"
    assert out["receipt"]["reason"] == "Live grok-4.7 completion. Unverified. Informational only."


def test_counsel_infer_unlisted_override_receipt_is_unavailable(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.6")
    out = counsel.infer(action="estate-synth", prompt="Summarize the catalog.", human_lock=True)
    assert out["honesty"] == "UNAVAILABLE"
    assert out["receipt"]["model"] is None
    assert out["receipt"]["honesty_tier"] == "UNAVAILABLE"
    assert recorder.calls == []


# ---- backend (eleven seats) -------------------------------------------------


def _live_xai_status() -> dict:
    return {"mode": "live", "chosen": {"kind": "xai-grok", "base": backend.XAI_BASE}}


def _run(coro):  # noqa: ANN001
    return asyncio.run(coro)


def test_backend_xai_path_ignores_ayllu_model(clean_env: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv("AYLLU_MODEL", "gpt-4o-mini")
    clean_env.setattr(backend, "backend_status", _live_xai_status)
    out = _run(backend.model_complete("sys", "question", persona="Amaru"))
    assert out["kind"] == "LIVE"
    assert len(recorder.calls) == 1
    url, body = recorder.calls[0]
    assert url == f"{backend.XAI_BASE}/chat/completions"
    assert body["model"] == "grok-4.7"
    assert not FORBIDDEN_PARAMS & set(body)


def test_backend_xai_path_honours_rollback_override(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.5")
    clean_env.setattr(backend, "backend_status", _live_xai_status)
    _run(backend.model_complete("sys", "question", persona="Amaru"))
    assert recorder.calls[0][1]["model"] == "grok-4.5"


def test_backend_xai_path_unlisted_override_zero_calls(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.6")
    clean_env.setattr(backend, "backend_status", _live_xai_status)
    out = _run(backend.model_complete("sys", "question", persona="Amaru"))
    assert out["kind"] == "SOFTWARE"
    assert out["stub"] is True
    assert "ALLOWED_GROK_MODELS" in out["honesty"]
    assert recorder.calls == []


def test_backend_status_unlisted_override_fails_closed_without_xai_probe(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.delenv("AYLLU_FORCE_SOFTWARE", raising=False)
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    clean_env.setenv(GROK_MODEL_ENV, "grok-4.6")
    status = backend.backend_status()
    # Local probes (CHASKI-R2 / Ollama) still run and would answer here, but
    # the operator asked for xAI: fail closed, no reroute, no xAI request.
    assert status["mode"] == "software"
    assert status["chosen"] is None
    assert status["probes"]["xai_grok"]["model_rejected"] is True
    assert status["probes"]["xai_grok"]["model"] is None
    assert recorder.xai_calls() == []


def test_backend_status_reports_resolved_model(clean_env: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    clean_env.delenv("AYLLU_FORCE_SOFTWARE", raising=False)
    clean_env.setenv("XAI_API_KEY", "test-not-a-real-key")
    status = backend.backend_status()
    assert status["mode"] == "live"
    assert status["chosen"]["kind"] == "xai-grok"
    assert status["chosen"]["model"] == "grok-4.7"
    # Only the /models probe went to xAI; no completion was requested.
    assert [c[0] for c in recorder.xai_calls()] == [f"{backend.XAI_BASE}/models"]


def test_backend_non_xai_paths_still_read_ayllu_model(
    clean_env: pytest.MonkeyPatch, recorder: _Recorder
) -> None:
    clean_env.setenv("AYLLU_MODEL", "chaski-r2-local")
    clean_env.setattr(
        backend,
        "backend_status",
        lambda: {"mode": "live", "chosen": {"kind": "chaski-r2", "base": backend.DEFAULT_OPENAI}},
    )
    _run(backend.model_complete("sys", "question", persona="Amaru"))
    assert recorder.calls[0][1]["model"] == "chaski-r2-local"
    assert recorder.xai_calls() == []


# ---- one constant per repo --------------------------------------------------


def test_no_grok_literal_outside_the_pin_module() -> None:
    pattern = re.compile(r"grok-\d")
    sources = [ROOT / "app.py", *sorted((ROOT / "ayllu").rglob("*.py")), *sorted((ROOT / "ayllu").rglob("*.html"))]
    offenders = []
    for path in sources:
        if path.name == "grok_model.py":
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{lineno}")
    assert offenders == []


def test_counsel_page_has_no_hardcoded_model_label() -> None:
    html = (ROOT / "ayllu" / "static" / "counsel.html").read_text(encoding="utf-8")
    assert "Run Grok" in html
    assert "grok_model_label" in html
