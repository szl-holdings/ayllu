"""CPU-only fail-closed local generation budget tests for Ayllu."""
import asyncio

import pytest

from ayllu import backend


@pytest.mark.parametrize("raw", ["0", "385", "abc", " ", "", "-1", "99999", "3.5"])
def test_invalid_completion_ceiling_refused(monkeypatch, raw):
    monkeypatch.setenv("AYLLU_COMPLETION_MAX_TOKENS", raw)
    with pytest.raises(ValueError, match="AYLLU_COMPLETION_MAX_TOKENS_INVALID"):
        backend.bounded_completion_tokens(384)


def test_ceiling_never_increases_requested_tokens(monkeypatch):
    monkeypatch.setenv("AYLLU_COMPLETION_MAX_TOKENS", "16")
    assert backend.bounded_completion_tokens(384) == 16
    assert backend.bounded_completion_tokens(8) == 8
    assert backend.bounded_completion_tokens(99999) == 16
    monkeypatch.delenv("AYLLU_COMPLETION_MAX_TOKENS")
    assert backend.bounded_completion_tokens(384) == 384
    assert backend.bounded_completion_tokens(99999) == 2048


def test_invalid_config_blocks_before_any_backend_network_probe(monkeypatch):
    monkeypatch.setenv("AYLLU_COMPLETION_MAX_TOKENS", "invalid")
    def forbidden():
        pytest.fail("a malformed local cap touched the model backend")
    monkeypatch.setattr(backend, "backend_status", forbidden)
    with pytest.raises(ValueError, match="AYLLU_COMPLETION_MAX_TOKENS_INVALID"):
        asyncio.run(backend.model_complete(
            "Public synthetic system", "Public synthetic prompt",
            max_tokens=384, persona="Amaru",
        ))


def test_synthetic_local_completion_respects_cap_without_network(monkeypatch):
    monkeypatch.setenv("AYLLU_COMPLETION_MAX_TOKENS", "12")
    monkeypatch.setenv("AYLLU_MODEL", "mistral:7b")
    monkeypatch.setattr(backend, "backend_status", lambda: {
        "mode": "live", "chosen": {"kind": "ollama"}, "lambda": "CONJECTURE_1",
    })
    called = []

    def fake_post(url, body, timeout, bearer=None):
        called.append((url, body, timeout, bearer))
        return 200, {
            "model": "mistral:7b",
            "choices": [{"message": {"content": "Synthetic proposal."}}],
        }

    monkeypatch.setattr(backend, "_post_json", fake_post)
    result = asyncio.run(backend.model_complete(
        "Public synthetic system", "Public synthetic prompt",
        max_tokens=384, persona="Amaru",
    ))
    assert len(called) == 1
    url, body, timeout, bearer = called[0]
    assert url == backend.DEFAULT_OLLAMA + "/v1/chat/completions"
    assert body["max_tokens"] == 12
    assert body["model"] == "mistral:7b"
    assert bearer is None
    assert result["kind"] == "LIVE" and result["stub"] is False
    assert result["token_budget"] == 12
    assert result["text"] == "Synthetic proposal."
    assert "Unverified model text" in result["honesty"]


def test_software_fallback_keeps_cap_but_not_live_claim(monkeypatch):
    monkeypatch.setenv("AYLLU_COMPLETION_MAX_TOKENS", "4")
    monkeypatch.setattr(backend, "backend_status", lambda: {
        "mode": "software", "chosen": None, "lambda": "CONJECTURE_1",
    })
    result = asyncio.run(backend.model_complete(
        "Public synthetic system", "Public synthetic prompt",
        persona="Amaru",
    ))
    assert result["token_budget"] == 4
    assert result["stub"] is True
    assert result["kind"] == "SOFTWARE"
