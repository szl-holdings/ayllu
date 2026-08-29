---
title: Ayllu Counsel
emoji: 💠
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Holographic counsel + Legal Matter Command. 11 seats. grok-4.5. Conjecture 1.
tags:
  - agent-council
  - holographic
  - governance
  - fail-closed
  - quechua
  - legal
---

# Ayllu Counsel

**Ayllu** (Quechua): a self-governing kinship community. This is SZL Holdings'
evidence-bound holographic agent counsel — eleven named seats around a khipu
knot, fail-closed Λ-gate, debate-then-converge, UNSIGNED-honest receipts —
plus **Legal Matter Command**, the live continuance of retired Counsel.

- Product origin: [a-11-oy.com](https://a-11-oy.com)
- Proof origin: [a11oy.net](https://a11oy.net)
- Source: [github.com/szl-holdings/ayllu](https://github.com/szl-holdings/ayllu)
- Space: [SZLHOLDINGS/ayllu](https://huggingface.co/spaces/SZLHOLDINGS/ayllu)

Λ uniqueness is **Conjecture 1** and is never a theorem.

Retired Counsel (`platform/artifacts/counsel`) is SUPERSEDED and **retained**.
This organ is the continuance. The eleven seats are not deleted.

## What you get

| Surface | What it is |
|---|---|
| `GET /` | 0-CDN holographic council chamber |
| `GET /counsel` | Legal Matter Command — live docket, Allodial, grok-4.5, Human Lock |
| `GET /api/v1/ayllu/roster` | 11 personas + honest backend mode |
| `POST /api/v1/ayllu/ask` | one seat, bounded, receipted |
| `POST /api/v1/ayllu/council` | capped fan-out; optional 2-round debate |
| `GET /api/v1/counsel/docket` | live Federal Register + CourtListener via a11oy |
| `GET /api/v1/counsel/estate` | live SZLHOLDINGS Hub scrape |
| `GET /api/v1/counsel/allodial` | experimental MODELED composite (not locked-8) |
| `POST /api/v1/counsel/infer` | grok-4.5 matter brief; fail-closed Human Lock |
| `GET /api/v1/ayllu/manifest` | machine-readable contract |

Personas are **roles on one routed backend**, not eleven trained models.
State-changing actions require two-person attestation. Semantic consensus
is **NOT_MEASURED**. Honest dissent is first-class.

Backend honesty:

- **LIVE** — grok-4.5 when `XAI_API_KEY` is set, else a reachable OpenAI-compatible endpoint (CHASKI-R2 `:8098` or Ollama `:11434`). Text is still unverified model output.
- **SOFTWARE** — no reachable live backend. The seat still speaks from its remit, clearly labeled, never fabricated as LIVE.
- **UNAVAILABLE** — a scrape or key is missing. Never upgraded to LIVE.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ayllu.selftest
uvicorn app:app --host 127.0.0.1 --port 8099
```

Optional live backend:

```
set XAI_API_KEY=...
set AYLLU_MODEL=grok-4.5
```

On the Hugging Face Space, set `XAI_API_KEY` as a Space secret so Counsel
and the eleven seats answer LIVE. Absent the key, answers stay SOFTWARE.

## Frontier (ours, not theirs)

Leaders in this space — Unanimous AI Hyperchat/(Co)agents, 3D LLM Council
WebGL chambers, AutoGen/CrewAI/CAMEL, Multiagent Debate, EvoTavern Council,
Credo / Arthur / Fiddler / Lakera / OneTrust / Galileo / watsonx — were
**studied, not copied**. We took presence, role-scoped turns, and
exactly-two-round debate. We kept:

1. Dissent retained (no fake "best answer" collapse).
2. Fail-closed Λ-gate (attestation binds; Λ is advisory).
3. Hash-chained UNSIGNED receipts (never a fabricated signature).
4. 0 runtime CDN hologram (khipu torus knot + eleven seats).
5. MEASURED / REPORTED / SOFTWARE / LIVE / UNAVAILABLE labels.
6. Legal Matter Command as continuance, not a deletion.

See [docs/LEADERS.md](docs/LEADERS.md) and [HONEST_DISCLOSURE.md](HONEST_DISCLOSURE.md).

## License

Apache-2.0. Doctrine v11. Λ = Conjecture 1.
