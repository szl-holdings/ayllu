"""The one reviewed Grok model pin for Ayllu's xAI path.

`DEFAULT_GROK_MODEL` is the only place the xAI model id is written. Counsel,
the xAI backend, disclosures and labels all derive from it. Changing it is a
model change and gets its own review plus an owner canary receipt.

`SZL_GROK_MODEL` is a server-side environment override (never a browser
variable). It is trimmed; empty or whitespace uses the default. Any other
value must be a member of `ALLOWED_GROK_MODELS` (the pin plus the single
reviewed rollback target). A value outside the allowlist fails closed:
`grok_model()` returns None, callers return their existing honest
UNAVAILABLE / SOFTWARE result, and no request is sent to xAI. It never
silently falls back to the default.

`AYLLU_MODEL` is not read on the xAI path. It still selects the model for the
CHASKI-R2, Ollama and OpenAI-compatible backends in `ayllu.backend`.
"""
from __future__ import annotations

import os

DEFAULT_GROK_MODEL = "grok-4.7"
# The pin plus the one reviewed rollback target (the previous live pin).
# Adding an id here is itself a reviewed model change.
ALLOWED_GROK_MODELS: tuple[str, ...] = (DEFAULT_GROK_MODEL, "grok-4.5")
GROK_MODEL_ENV = "SZL_GROK_MODEL"


def grok_model() -> str | None:
    """Resolve the xAI model id for this call, or None to fail closed."""
    raw = (os.environ.get(GROK_MODEL_ENV) or "").strip()
    if not raw:
        return DEFAULT_GROK_MODEL
    if raw in ALLOWED_GROK_MODELS:
        return raw
    return None


def grok_label(model: str | None = DEFAULT_GROK_MODEL) -> str:
    """Human label for a model id: "grok-4.7" -> "Grok 4.7"."""
    if not model:
        return "Grok"
    if model.startswith("grok-"):
        return "Grok " + model[len("grok-"):]
    return model


def rejected_hint() -> str:
    """Honest reason text for a rejected override. Never echoes the value."""
    return (
        f"{GROK_MODEL_ENV} is set to an id outside ALLOWED_GROK_MODELS "
        f"({', '.join(ALLOWED_GROK_MODELS)}). Fail-closed: no xAI request sent."
    )


__all__ = [
    "ALLOWED_GROK_MODELS",
    "DEFAULT_GROK_MODEL",
    "GROK_MODEL_ENV",
    "grok_label",
    "grok_model",
    "rejected_hint",
]
