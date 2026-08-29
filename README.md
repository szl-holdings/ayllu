---
title: Ayllu Counsel
emoji: 💠
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Holographic agent counsel. 11 seats. Conjecture 1.
tags:
  - agent-council
  - holographic
  - governance
  - fail-closed
  - quechua
---

# Ayllu Counsel

**Ayllu** (Quechua): a self-governing kinship community. This is SZL Holdings'
evidence-bound holographic agent counsel — eleven named seats around a khipu
knot, fail-closed Λ-gate, debate-then-converge, UNSIGNED-honest receipts.

- Product origin: [a-11-oy.com](https://a-11-oy.com)
- Proof origin: [a11oy.net](https://a11oy.net)
- Source: [github.com/szl-holdings/ayllu](https://github.com/szl-holdings/ayllu)
- Space: [SZLHOLDINGS/ayllu](https://huggingface.co/spaces/SZLHOLDINGS/ayllu)

Λ uniqueness is **Conjecture 1** and is never a theorem.

## What you get

| Surface | What it is |
|---|---|
| `GET /` | 0-CDN holographic council chamber |
| `GET /api/v1/ayllu/roster` | 11 personas + honest backend mode |
| `POST /api/v1/ayllu/ask` | one seat, bounded, receipted |
| `POST /api/v1/ayllu/council` | capped fan-out; optional 2-round debate |
| `GET /api/v1/ayllu/manifest` | machine-readable contract |
| `GET /api/v1/ayllu/estate` | consolidated SZL surfaces |
| `GET /api/v1/ayllu/leaders` | what we studied, what we own |

Personas are **roles on one routed backend**, not eleven trained models.
State-changing actions require two-person attestation. Semantic consensus
is **NOT_MEASURED**. Honest dissent is first-class.

Backend honesty:

- **LIVE** — a reachable OpenAI-compatible endpoint answered (CHASKI-R2 `:8098` or Ollama `:11434`). Text is still unverified model output.
- **SOFTWARE** — no reachable live backend. The seat still speaks from its remit, clearly labeled, never fabricated as LIVE.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ayllu.selftest
uvicorn app:app --host 127.0.0.1 --port 8099
```

Optional live backend (CHASKI-R2 serve already used on this estate):

```
set AYLLU_OPENAI_BASE=http://127.0.0.1:8098/v1
set AYLLU_MODEL=chaski-r2
```

## Frontier (ours, not theirs)

Leaders in this space — Unanimous AI Hyperchat/(Co)agents, 3D LLM Council
WebGL chambers, AutoGen/CrewAI/CAMEL, Multiagent Debate, EvoTavern Council —
were **studied, not copied**. We took presence, role-scoped turns, and
exactly-two-round debate. We kept:

1. Dissent retained (no fake "best answer" collapse).
2. Fail-closed Λ-gate (attestation binds; Λ is advisory).
3. Hash-chained UNSIGNED receipts (never a fabricated signature).
4. 0 runtime CDN hologram (khipu torus knot + eleven seats).
5. MEASURED / REPORTED / SOFTWARE / LIVE / UNAVAILABLE labels.

See [docs/LEADERS.md](docs/LEADERS.md) and [HONEST_DISCLOSURE.md](HONEST_DISCLOSURE.md).

## License

Apache-2.0. Doctrine v11. Λ = Conjecture 1.
