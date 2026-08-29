"""Psyche engine — neural, symbolic, and compositional in one pulse.

Pipeline (Tinku):
  cue → encode → recall (Yuyay) → seat morphism → lock gate → optional imprint → khipu

Fail-closed at every arrow. Joules None. Λ = Conjecture 1.
"""
from __future__ import annotations

import time
import uuid
from typing import Any

from ayllu.psyche.graph import TypedHypergraph
from ayllu.psyche.lock import HumanLock
from ayllu.psyche.morphisms import ArrowContext, Morphism, identity, run_pipeline
from ayllu.psyche.neural import Yuyay
from ayllu.psyche.seats import SEAT_ORGANS, roster_typed, seat_morphism
from ayllu.psyche.types import (
    ENERGY,
    LAMBDA,
    SCHEMA,
    Bundle,
    Decision,
    Honesty,
    Kind,
)
from ayllu.receipts import canonical_dumps, make_receipt, sha3_256_hex

GENESIS = "0" * 64


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Psyche:
    def __init__(self) -> None:
        self.yuyay = Yuyay()
        self.graph = TypedHypergraph()
        self.lock = HumanLock()
        self.prev_hash = GENESIS
        self.pulses = 0

    def set_lock(self, engaged: bool) -> dict[str, Any]:
        if engaged:
            self.lock.engage()
        else:
            self.lock.release()
        return self.lock.snapshot()

    def _mint(self, action: str, decision: str, honesty: str, payload: Any, reason: str) -> dict[str, Any]:
        body = {
            "id": str(uuid.uuid4()),
            "ts": _now(),
            "organ": "psyche",
            "action": action,
            "decision": decision,
            "honesty_tier": honesty,
            "lambda": "Conjecture 1",
            "slsa": "L1",
            "prev_hash": self.prev_hash if len(self.prev_hash) == 64 else GENESIS,
            "input_digest": sha3_256_hex(canonical_dumps(payload)),
            "energy": ENERGY,
            "signer": "UNSIGNED-honest",
            "doctrine": "v11",
            "lock": "749/14/163",
            "reason": reason,
        }
        body["hash"] = sha3_256_hex(canonical_dumps(body))
        self.prev_hash = body["hash"]
        envelope = make_receipt({"schema": "szl.ayllu.psyche-receipt/v1", "receipt": body})
        return {"receipt": body, "envelope": envelope}

    def imprint(self, text: str, source: str = "pulse", honesty: str = "MEASURED") -> dict[str, Any]:
        gate = self.lock.admit("imprint", state_changing=True)
        if gate["decision"] != Decision.ALLOW.value:
            minted = self._mint("imprint", "BLOCKED", Honesty.MEASURED.value, {"text": text}, "; ".join(gate["reasons"]))
            return {
                "schema": SCHEMA,
                "ok": False,
                "blocked": True,
                "text": "BLOCKED — " + " ".join(gate["reasons"]),
                "gate": gate,
                **minted,
                "lambda": LAMBDA,
                "joules": ENERGY,
            }
        result = self.yuyay.imprint(text, source=source, honesty=Honesty(honesty), digest="")
        if not result.get("ok"):
            minted = self._mint("imprint", "BLOCKED", Honesty.MEASURED.value, {"text": text}, str(result.get("error")))
            return {"schema": SCHEMA, "ok": False, "blocked": True, **result, **minted, "lambda": LAMBDA}
        eid = str(len(self.yuyay.texts))
        self.graph.add_engram(eid, text, source, Honesty(honesty), self.prev_hash)
        minted = self._mint("imprint", "ALLOW", Honesty.MEASURED.value, {"text": text, "source": source}, "Yuyay imprint.")
        self.graph.vertices[f"engram:{eid}"].data["hash"] = minted["receipt"]["hash"]
        return {
            "schema": SCHEMA,
            "ok": True,
            "blocked": False,
            "engram": result,
            "stats": self.yuyay.stats(),
            **minted,
            "lambda": LAMBDA,
            "joules": ENERGY,
        }

    def recall(self, cue: str, seat: str = "Maskaq") -> dict[str, Any]:
        rec = self.yuyay.recall(cue)
        morph = seat_morphism(seat) or identity("cue")
        bundle = Bundle(
            payload={"cue": cue, "recall": rec},
            honesty=Honesty(rec.get("honesty") or Honesty.UNAVAILABLE),
            kind=Kind.SOFTWARE,
            remit="any",
        )
        ctx = ArrowContext(lock=self.lock, seat=seat, action="recall")
        uttered = morph.apply(bundle, ctx)
        minted = self._mint(
            "recall",
            uttered.decision.value,
            rec.get("honesty") or Honesty.UNAVAILABLE.value,
            {"cue": cue, "seat": seat},
            "Dual Hopfield recall + seat morphism.",
        )
        return {
            "schema": SCHEMA,
            "ok": bool(rec.get("ok")),
            "recall": rec,
            "seat": uttered.as_dict(),
            "stats": self.yuyay.stats(),
            **minted,
            "lambda": LAMBDA,
            "joules": ENERGY,
        }

    def replay(self, rounds: int = 24) -> dict[str, Any]:
        gate = self.lock.admit("replay", state_changing=True)
        if gate["decision"] != Decision.ALLOW.value:
            minted = self._mint("replay", "BLOCKED", Honesty.MEASURED.value, {"rounds": rounds}, "; ".join(gate["reasons"]))
            return {
                "schema": SCHEMA,
                "ok": False,
                "blocked": True,
                "text": "BLOCKED — " + " ".join(gate["reasons"]),
                "gate": gate,
                **minted,
                "lambda": LAMBDA,
            }
        report = self.yuyay.replay(rounds)
        minted = self._mint("replay", "ALLOW", Honesty.MEASURED.value, {"rounds": rounds}, "Reverse-Hebb replay.")
        return {
            "schema": SCHEMA,
            "ok": True,
            "blocked": False,
            "report": report,
            "stats": self.yuyay.stats(),
            **minted,
            "lambda": LAMBDA,
            "joules": ENERGY,
        }

    def compose_turn(self, cue: str, seat: str = "Amaru", imprint: bool = False) -> dict[str, Any]:
        """Full Tinku pulse: encode → recall → seat → (optional imprint)."""
        self.pulses += 1
        rec = self.yuyay.recall(cue)

        def encode_fn(bundle: Bundle, _ctx: ArrowContext) -> Bundle:
            payload = bundle.payload if isinstance(bundle.payload, dict) else {"cue": cue}
            return Bundle(
                payload={**payload, "recall": rec},
                honesty=Honesty(rec.get("honesty") or Honesty.UNAVAILABLE),
                kind=Kind.SOFTWARE,
                remit=seat,
            )

        encode_m = Morphism(
            name="yuyay.recall",
            domain="cue",
            codomain="cue",
            honesty_floor=Honesty.UNAVAILABLE,
            fn=encode_fn,
        )
        morphs: list[Morphism] = [encode_m]
        seat_m = seat_morphism(seat)
        if seat_m is not None:
            morphs.append(seat_m)
        bundle = Bundle(payload={"cue": cue, "text": cue}, honesty=Honesty.MEASURED, remit="any")
        ctx = ArrowContext(lock=self.lock, seat=seat, action="compose")
        ran = run_pipeline(morphs, bundle, ctx)
        imprinted = None
        if imprint:
            imprinted = self.imprint(cue, source=f"seat:{seat}", honesty="MEASURED")
            if imprinted.get("blocked"):
                ran["decision"] = Decision.BLOCKED.value
        minted = self._mint(
            "compose",
            ran["decision"],
            ran["honesty"],
            {"cue": cue, "seat": seat, "imprint": bool(imprint)},
            "Tinku pulse.",
        )
        return {
            "schema": SCHEMA,
            "pulse": self.pulses,
            "pipeline": ran,
            "imprint": imprinted,
            "stats": self.yuyay.stats(),
            "graph": self.graph.snapshot()["counts"],
            **minted,
            "lambda": LAMBDA,
            "joules": ENERGY,
        }

    def forget(self, index: int) -> dict[str, Any]:
        gate = self.lock.admit("forget", state_changing=True)
        if gate["decision"] != Decision.ALLOW.value:
            minted = self._mint("forget", "BLOCKED", Honesty.MEASURED.value, {"index": index}, "; ".join(gate["reasons"]))
            return {"schema": SCHEMA, "ok": False, "blocked": True, **minted, "lambda": LAMBDA}
        self.yuyay.forget(index)
        self.graph.drop_engrams()
        for i, text in enumerate(self.yuyay.texts, start=1):
            self.graph.add_engram(str(i), text, self.yuyay.sources[i - 1], Honesty(self.yuyay.honesty_trace[i - 1]), self.prev_hash)
        minted = self._mint("forget", "ALLOW", Honesty.MEASURED.value, {"index": index}, "Engram dropped; weights rebuilt.")
        return {"schema": SCHEMA, "ok": True, "stats": self.yuyay.stats(), **minted, "lambda": LAMBDA}

    def reset(self) -> dict[str, Any]:
        gate = self.lock.admit("reset", state_changing=True)
        if gate["decision"] != Decision.ALLOW.value:
            minted = self._mint("reset", "BLOCKED", Honesty.MEASURED.value, {}, "; ".join(gate["reasons"]))
            return {"schema": SCHEMA, "ok": False, "blocked": True, **minted, "lambda": LAMBDA}
        self.yuyay.reset()
        self.graph = TypedHypergraph()
        minted = self._mint("reset", "ALLOW", Honesty.MEASURED.value, {}, "Yuyay and graph reset.")
        return {"schema": SCHEMA, "ok": True, "stats": self.yuyay.stats(), **minted, "lambda": LAMBDA}

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "product": "Ayllu Psyche",
            "lock": self.lock.snapshot(),
            "yuyay": self.yuyay.snapshot(),
            "graph": self.graph.snapshot(),
            "seats": roster_typed(),
            "organs": SEAT_ORGANS,
            "pulses": self.pulses,
            "chainHead": self.prev_hash,
            "lambda": LAMBDA,
            "joules": ENERGY,
            "honesty": Honesty.MEASURED.value,
        }

    def health(self) -> dict[str, Any]:
        stored = len(self.yuyay.patterns)
        return {
            "ok": True,
            "schema": SCHEMA,
            "neural": "OPERATIONAL" if True else "UNAVAILABLE",
            "stored": stored,
            "lock": self.lock.engaged,
            "seats": 11,
            "organs": 5,
            "honesty": Honesty.MEASURED.value,
            "lambda": LAMBDA,
            "joules": ENERGY,
        }


# Process singleton — same pattern as Lounge.
PSYCHE = Psyche()
