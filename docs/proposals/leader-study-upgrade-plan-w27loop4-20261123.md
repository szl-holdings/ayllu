# Leader-Study Upgrade Plan - W27 loop-4 - 2026-11-23

Status: PROPOSE-ONLY DRAFT - DO NOT MERGE. Owner-gated: merging requires governing approval and the estate signature-wall owner unlock.

Repo: ayllu - Ayllu Counsel — evidence-bound holographic agent council. 11 Quechua seats, fail-closed Λ-gate, Maskaq vertical search, UNSIGNED-honest receipts. SOFTWARE/LIVE honesty. Apache-2.0 · Doctrine v11 · Λ = Conjecture 1.

Frame: OUROBOROS loop-4 leader study. Governing seat: Kimi kimi-k3.1-pro (json_ok, think off). Advisory seats: Astra/Sol/Claude community rails (provenance unverified, advisory only). Leader evidence web-verified 2026-11-23.

## Leader moats to absorb
- LangGraph: Durable stateful agents with human-in-the-loop checkpoints. Moat: Durable execution and explicit checkpointing make long-running agent workflows resumable and interruptible.
- AutoGen / Microsoft Agent Framework: Conversational multi-agent orchestration. Moat: Mature multi-agent conversation patterns and framework-level coordination.
- CrewAI: Role/task crews for multi-agent work. Moat: Simple role-and-task abstraction for assigning work across agents.
- MetaGPT: Role-based multi-agent software workflow. Moat: Structured role specialization and artifact-oriented collaboration.

## Honest gaps (grounded in repo facts)
- The facts describe receipt replay only as a truncated sentence: 'The verifier recomputes the payload'. The verification scope, failure behavior, and whether replay covers full execution state are not established.
- The README states that live output requires a reachable configured backend and that missing dependencies remain SOFTWARE or UNAVAILABLE; it does not establish production availability or verified model output.
- The eleven seats are roles on one routed backend, not eleven separately trained models, so the council's diversity should not be represented as independent model diversity.
- Receipts remain UNSIGNED and Λ remains Conjecture 1; the facts therefore do not support claims of cryptographic receipt authenticity or a proven governance theorem.
- The facts identify a full route list at /docs but provide no evidence of durable cross-restart workflow checkpoints comparable to LangGraph's stated durable execution.
- The facts assert two-person attestation and Human Lock for protected state changes, but do not establish out-of-process security isolation or a general pre-dispatch approval gate for every external action.
- The provided facts do not include test results, CI status, backend configuration, threat model, or independent security review, so those properties remain unverified rather than absent.

## Dosed upgrade plan
- First publish a narrow receipt-replay specification from the existing implementation: exact payload fields, recomputation steps, expected mismatch behavior, and explicit UNSIGNED limitations. Do not change admission semantics in this step.
- Add conformance fixtures for SOFTWARE, UNAVAILABLE, unverified model output, and live output, asserting that labels survive routing, replay, and API responses.
- Design a propose-only durable checkpoint envelope for council runs, including run ID, seat role, routed backend identity, evidence references, admission state, attestation state, and resume status; keep it separate from protected-state mutation.
- Prototype checkpoint and resume only for read-only evaluation flows, with fail-closed behavior on incomplete or inconsistent state and no claim of live backend verification.
- Map every protected state-changing route to an explicit admission decision record covering Λ-gate, Human Lock, and two-person attestation; add negative tests showing dispatch is blocked when any required record is missing.
- If process isolation is needed, propose an out-of-process dispatcher with a narrow capability schema and deny-by-default transport, then document its trust boundary and test it independently before enabling any live action.
- Only after replay and admission tests pass, compare interrupted/resumed read-only runs against LangGraph-style checkpoint behavior and publish measured limitations alongside the results.
- Risk note: Checkpointing or external dispatch could accidentally turn incomplete evidence into executable authority, leak sensitive legal-matter state, or imply stronger verification than UNSIGNED receipts provide. The largest near-term risk is overstating durability, isolation, and verification without repository and runtime evidence; changes should remain read-only and fail-closed until tested.
- Propose-only note: This is a proposal derived only from the supplied facts, not a representation that these features exist or that repository changes have been made. Preserve SOFTWARE/LIVE honesty, UNSIGNED receipts, separate action admission, Human Lock, two-person attestation, and Λ = Conjecture 1 throughout.

## Advisory notes (unverified rails, non-binding)
- astra: acoustic-validation: Proprietary high-fidelity benchmark datasets for PDE solver verification. ayllu: Formal verification proofs for multi-agent consensus and evidence-binding. aifor-science-protocol: Institutional adoption as the standard for AI-driven research pre-registration.
- sol: acoustic-validation: Proprietary high-fidelity synthetic datasets for benchmark validation. ayllu: Formal verification proofs for multi-agent consensus and evidence-binding. aifor-science-protocol: Standardized, machine-readable registration schema adopted by major journals.
- claude: acoustic-validation: Proprietary benchmark datasets of verified physical ground-truth measurements. ayllu: A standardized, cryptographically verifiable audit trail for multi-agent consensus. aifor-science-protocol: Institutional endorsement and integration into peer-review submission pipelines.

## DO NOT MERGE
This plan is a proposal artifact of the 10-pass OUROBOROS loop (loop-4 of 10). No code, no CI, no behavior changes in this file. A reviewer with authority may convert to a work order later.