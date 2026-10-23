"""Versioned local evaluation; real model evidence is explicitly opt-in and unreviewed."""
import argparse
import asyncio
import json
import math
from pathlib import Path
import tempfile
import time

from .core import Engine, OfflineProvider, VERSION, digest, fixture_paths
from .provider import BedrockProvider


async def evaluate(cases_path, provider, split):
    bundle = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    corpus, metadata = fixture_paths()
    records = []
    scheduled = [c for c in bundle["cases"] if c["split"] == split]
    stopped = None
    for case in scheduled:
        with tempfile.TemporaryDirectory() as tmp:
            engine = Engine(tmp, corpus, metadata, provider, timeout=12 if provider.kind != "synthetic" else 2)
            observed = []
            start = time.monotonic()
            try:
                result = await engine.ask(case["token"], case["query"], observe_retrieval=observed.extend)
                calls = engine.store.db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
            finally:
                engine.close()
            citations_valid = all(c["document"] in case["documents"] and
                c["quote"] == metadata["documents"][c["document"]]["claim"] for c in result["citations"])
            records.append({"id": case["id"], "slice": case["slice"], "status": result["status"],
                "expected": case["expected"], "correct": result["status"] == case["expected"] and citations_valid,
                "retrieval_hits": len(set(observed) & set(case["documents"])),
                "relevant": len(case["documents"]),
                "forbidden": len(set(observed)-set(case["documents"])),
                "latency_ms": (time.monotonic()-start)*1000, "calls": calls,
                "usage": getattr(provider, "last_usage", None) if calls else None,
                "provider_error": getattr(provider, "last_error", None) if calls else None})
            if records[-1]["provider_error"] in ("AccessDeniedException", "ValidationException", "ResourceNotFoundException"):
                stopped = records[-1]["provider_error"]
                break  # A repeated deployment/access/configuration failure cannot improve by spending on more cases.
    ready = [r for r in records if r["status"] == "ready"]
    relevant = sum(r["relevant"] for r in records)
    correct = sum(r["correct"] for r in records)
    return {"application": VERSION, "prompt": "exact-quote-v1", "schema": "citations-v1", "model": provider.model,
        "evidence_kind": provider.kind, "semantic_review": "authored-control-labels" if provider.kind == "synthetic" else "pending-human-review",
        "split": split, "cases_sha256": digest(bundle), "metadata_sha256": digest(metadata),
        "corpus_sha256": {p.name: digest(p.read_text(encoding="utf-8")) for p in sorted(corpus.glob("*.md"))},
        "configuration": {"deadline_seconds": 12 if provider.kind != "synthetic" else 2, "attempts_per_request": 1,
                          "concurrency": 2, "maximum_output_tokens": 256},
        "counts": {"scheduled_requests": len(scheduled), "unexecuted": len(scheduled)-len(records),
                   "requests": len(records), "ready": len(ready), "correct": correct,
                   "abstained": sum(r["status"] == "abstained" for r in records),
                   "failed": sum(r["status"] == "failed" for r in records), "provider_calls": sum(r["calls"] for r in records)},
        "quality": sum(r["correct"] for r in ready)/len(ready) if ready else None,
        "coverage": len(ready)/len(records) if records else None,
        "p95_ms": sorted(r["latency_ms"] for r in records)[math.ceil(.95*len(records))-1] if records else None,
        "retrieval": {"hits": sum(r["retrieval_hits"] for r in records), "relevant": relevant,
                      "recall": sum(r["retrieval_hits"] for r in records)/relevant if relevant else None,
                      "forbidden": sum(r["forbidden"] for r in records)},
        "slices": {s: {"n": sum(r["slice"] == s for r in records),
                       "correct": sum(r["slice"] == s and r["correct"] for r in records)} for s in sorted({r["slice"] for r in records})},
        "stopped_reason": stopped,
        "control_gate": "pass" if records and len(records) == len(scheduled) and correct == len(records) and not sum(r["forbidden"] for r in records) else "halt",
        "delivery_decision": "NO_RELEASE", "cost": {"actual_usd": None, "reason": "no current verified price inputs; tokens retained for later costing"},
        "records": records, "limits": ["public tiny controls overlap earlier learning data; not independent unseen competence",
            "conditional ready quality does not establish usefulness at population scale", "no live price or deployment evidence"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=("development", "heldout"), required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--live", action="store_true")
    p.add_argument("--confirm-paid-calls", action="store_true")
    p.add_argument("--model")
    args = p.parse_args()
    if args.live and (not args.confirm_paid_calls or not args.model):
        p.error("live requires --confirm-paid-calls and an approved --model; see delivery preflight")
    if args.out.exists():
        p.error("output exists; preserve evidence and choose a new path")
    provider = BedrockProvider(args.model) if args.live else OfflineProvider()
    result = asyncio.run(evaluate("cases.json", provider, args.split))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"kind": result["evidence_kind"], "control_gate": result["control_gate"],
                      "delivery_decision": result["delivery_decision"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
