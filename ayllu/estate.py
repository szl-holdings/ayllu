"""Public catalog of what Ayllu showcases.

Every URL is a public origin. Health is REPORTED from this process only —
never a claim that a remote Space is LIVE unless this process probed it.
"""
from __future__ import annotations

from ayllu import SCHEMA_COUNCIL, __version__

ORIGINS = {
    "product": "https://a-11-oy.com",
    "proof": "https://a11oy.net",
    "github": "https://github.com/szl-holdings/ayllu",
    "hub": "https://huggingface.co/SZLHOLDINGS",
    "space": "https://huggingface.co/spaces/SZLHOLDINGS/ayllu",
    "never": "a11oy.com — foreign storefront, not ours",
}

CONSOLIDATED = [
    {
        "name": "Ayllu Counsel",
        "kind": "product",
        "origin": "this repository",
        "honesty": "SOFTWARE FastAPI + holographic chamber. LIVE only when a backend is reachable.",
        "urls": [ORIGINS["github"], ORIGINS["space"]],
    },
    {
        "name": "Legal Matter Command",
        "kind": "counsel organ",
        "origin": "this repository /counsel",
        "honesty": "Live a11oy legal vertical + grok-4.5 when XAI_API_KEY is set. Human Lock fail-closed. Continuance of retired Counsel, not a deletion.",
        "urls": [
            "https://huggingface.co/spaces/SZLHOLDINGS/ayllu",
            "https://a-11-oy.com/api/a11oy/v1/vert/legal",
        ],
    },
    {
        "name": "Retired Counsel artifact",
        "kind": "superseded organ",
        "origin": "https://github.com/szl-holdings/platform",
        "honesty": "SUPERSEDED, retained in place. Not deleted.",
        "urls": ["https://github.com/szl-holdings/platform"],
    },
    {
        "name": "a11oy organ /ayllu",
        "kind": "flagship organ",
        "origin": "https://github.com/szl-holdings/a11oy",
        "honesty": "The council still ships inside a11oy. This repo is the split-out product.",
        "urls": ["https://a-11-oy.com/ayllu", "https://github.com/szl-holdings/a11oy"],
    },
    {
        "name": "CHASKI-R2",
        "kind": "model lineage",
        "origin": "https://github.com/szl-holdings/szl-forge",
        "honesty": "Local Unsloth bf16 LoRA on Qwen3.5-0.8B. Hub PUT skipped when HF_TOKEN is 401.",
        "urls": ["https://huggingface.co/SZLHOLDINGS/chaski"],
    },
    {
        "name": "Λ gate hologram",
        "kind": "hologram",
        "origin": "https://github.com/szl-holdings/lambda-gate-holo",
        "honesty": "Λ = Conjecture 1, never a theorem, never green.",
        "urls": ["https://huggingface.co/spaces/SZLHOLDINGS/lambda-gate-holo"],
    },
    {
        "name": "Governed-norm hologram",
        "kind": "hologram",
        "origin": "https://github.com/szl-holdings/governed-norm-holo",
        "honesty": "Inspectable WILLAY refusal classifiers. Honest REPORTED/UNAVAILABLE.",
        "urls": ["https://huggingface.co/spaces/SZLHOLDINGS/governed-norm-holo"],
    },
    {
        "name": "Khipu",
        "kind": "receipt chain",
        "origin": "https://github.com/szl-holdings/szl-khipu",
        "honesty": "Knot the run. Hash the proof. Fail closed.",
        "urls": ["https://huggingface.co/SZLHOLDINGS"],
    },
    {
        "name": "IMMUNE",
        "kind": "defense matrix",
        "origin": "https://github.com/szl-holdings/immune",
        "honesty": "Append-only SHA-256 receipt chain + SENTRA/GATE admission.",
        "urls": ["https://huggingface.co/spaces/SZLHOLDINGS/immune"],
    },
    {
        "name": "Living anatomy",
        "kind": "organism",
        "origin": "https://github.com/szl-holdings/anatomy",
        "honesty": "Five organs instilled into Ayllu as a SOFTWARE map. 3D Space is separate.",
        "urls": ["https://huggingface.co/spaces/SZLHOLDINGS/anatomy"],
    },
    {
        "name": "Second Brain",
        "kind": "retrieval hologram",
        "origin": "https://github.com/szl-holdings/szl-second-brain",
        "honesty": (
            "SOFTWARE navigator over the public 575-chunk projection. "
            "Handles only. YACHAY organ. Never the private 9464-node graph. "
            "Does not overwrite SZLHOLDINGS/SZL-Khipu-1.5B-BrainNavigator."
        ),
        "urls": [
            "https://huggingface.co/spaces/SZLHOLDINGS/second-brain",
            "https://github.com/szl-holdings/szl-second-brain",
        ],
    },
    {
        "name": "Hatun MCP",
        "kind": "mcp gateway",
        "origin": "https://github.com/szl-holdings/hatun-mcp",
        "honesty": "healthz is process liveness. tools/list not fabricated.",
        "urls": ["https://huggingface.co/spaces/SZLHOLDINGS/hatun-mcp"],
    },
    {
        "name": "Ouroboros",
        "kind": "bounded loop",
        "origin": "https://github.com/szl-holdings/ouroboros",
        "honesty": "Always terminates. receipts.in ≡ receipts.out. Not perpetual motion.",
        "urls": ["https://github.com/szl-holdings/szl-ouroboros"],
    },
    {
        "name": "Invariants",
        "kind": "kernel",
        "origin": "https://github.com/szl-holdings/szl-invariants",
        "honesty": "Eight falsifiable receipt checks. SOFTWARE, not weights.",
        "urls": ["https://huggingface.co/SZLHOLDINGS/szl-invariants"],
    },
    {
        "name": "lutar-lean",
        "kind": "formal corpus",
        "origin": "https://github.com/szl-holdings/lutar-lean",
        "honesty": "Doctrine v11 LOCKED. 749 declarations · 14 axioms · 163 tracked sorries.",
        "urls": ["https://doi.org/10.5281/zenodo.20434308"],
    },
]

LEADERS_STUDIED = [
    {
        "name": "Unanimous AI — Hyperchat / (Co)agents",
        "took": "Proactive seats that speak into a live deliberation; scale past a 7–10 person table.",
        "own": "We do not swarm humans. We run 11 named kinship seats with receipts, a hard fan-out cap, and dissent retained.",
        "url": "https://unanimous.ai/hyperchat-ai/",
    },
    {
        "name": "Multiagent Debate (arXiv:2305.14325)",
        "took": "Exactly two rounds: positions, then explicit dissent and revision.",
        "own": "Hard cap of two rounds. Never an open-ended debate loop. Semantic consensus stays NOT_MEASURED.",
        "url": "https://arxiv.org/abs/2305.14325",
    },
    {
        "name": "3D LLM Council / WebGL chambers",
        "took": "A round table you can watch. Speaking seats. Presence instead of a chat box.",
        "own": "0 runtime CDN canvas hologram. 11 Quechua seats around a khipu knot. No Three.js, no model zoo.",
        "url": "https://github.com/ghwmelite-dotcom/my-llm-council",
    },
    {
        "name": "AutoGen / Microsoft Agent Framework, CrewAI, CAMEL, MetaGPT",
        "took": "Role-scoped turns, visible handoffs, society-of-agents.",
        "own": "Reject unbounded execute-don't-narrate. Two-person attestation. Personas are roles, not eleven weight files.",
        "url": "https://arxiv.org/abs/2308.08155",
    },
    {
        "name": "siyu-deng/council (EvoTavern 2026)",
        "took": "A round table with chairs that light when a seat speaks, and a decision card that may record remaining dissent.",
        "own": "Decision card is a receipt: UNSIGNED-honest, hash-chained, PROPOSAL_ONLY.",
        "url": "https://github.com/siyu-deng/council",
    },
]


def catalog() -> dict:
    return {
        "schema": "szl.ayllu.estate-catalog/v1",
        "product": "Ayllu Counsel",
        "version": __version__,
        "council_schema": SCHEMA_COUNCIL,
        "origins": ORIGINS,
        "consolidated": CONSOLIDATED,
        "leaders_studied": LEADERS_STUDIED,
        "honesty": (
            "Catalog of public origins. Not live health. Not adoption. "
            "Λ = Conjecture 1."
        ),
    }
