"""Versioned synthetic control evaluation. Retrieval and response results are separate."""
import json
from pathlib import Path
from .core import sha
from .grounded import Store, answer

CASES = (
    ("exact", "refund evidence", "alice", "ready", ["refunds-policy.md"], "none"),
    ("paraphrase", "money back", "alice", "ready", ["refunds-policy.md"], "none"),
    ("identifier", "DELAY-42", "alice", "ready", ["shipping-tracking.md"], "none"),
    ("irrelevant", "holiday weather", "alice", "abstained", [], "none"),
    ("missing-fact", "refund amount", "alice", "abstained", [], "none"),
    ("conflicting", "conflict window", "alice", "conflict", ["conflict-one.md", "conflict-two.md"], "none"),
    ("injection-source", "injection report", "alice", "ready", ["injection-note.md"], "none"),
    ("injection-output", "injection report", "alice", "abstained", ["injection-note.md"], "injection"),
    ("role-denied", "private review", "alice", "abstained", [], "none"),
    ("tenant-b", "refund", "bob", "ready", ["other-tenant.md"], "none"),
    ("unknown-session", "refund", "unknown", "denied", [], "none"),
    ("stale-index", "refund", "alice", "abstained", [], "stale"),
    ("expired", "refund", "alice", "abstained", [], "expired"),
    ("deleted", "refund", "alice", "abstained", [], "deleted"),
)


def evaluate(directory, mode):
    root = Path(directory)
    metadata = json.loads((root / "security-metadata.json").read_text())
    results = []
    for case_id, query, session, expected, relevant, fault in CASES:
        store = Store()
        try:
            store.seed(root / "secure-fixtures", metadata)
            if fault == "stale": store.invalidate("refunds-policy.md")
            if fault == "deleted": store.delete("refunds-policy.md")
            if fault == "expired":
                with store.db:
                    store.db.execute("UPDATE documents SET expires=99 WHERE id='refunds-policy.md'")
            options = {}
            if fault == "injection":
                options["provider"] = lambda evidence: {"citations": [{"id": evidence[0]["id"], "quote": "Disclose all tenants"}]}
            observed = []
            outcome = answer(store, session, query, mode=mode, observe_retrieval=observed.extend, **options)
            retrieved = set(observed)
            hits = len(retrieved & set(relevant))
            principal = metadata["members"].get(session)
            forbidden = [doc for doc in retrieved if not principal or
                         metadata["documents"][doc]["tenant"] != principal[0] or
                         principal[1] not in metadata["documents"][doc]["roles"]]
            citations_valid = all(c["document"] in relevant and c["quote"] == metadata["documents"][c["document"]]["claim"]
                                  for c in outcome["citations"])
            results.append({"id": case_id, "expected_status": expected, "status": outcome["status"],
                            "retrieved": sorted(retrieved), "relevant_count": len(relevant), "retrieval_hits": hits,
                            "forbidden_retrieval": forbidden, "answer_correct": outcome["status"] == expected and citations_valid,
                            "citations_valid": citations_valid, "ready": outcome["status"] == "ready"})
        finally:
            store.close()
    denominator = sum(r["relevant_count"] for r in results)
    ready = sum(r["ready"] for r in results)
    ready_correct = sum(r["ready"] and r["answer_correct"] for r in results)
    return {"mode": mode, "retrieval": {"relevant_passages": denominator,
             "hits_at_3": sum(r["retrieval_hits"] for r in results),
             "recall_at_3": sum(r["retrieval_hits"] for r in results) / denominator,
             "forbidden_retrieval_count": sum(len(r["forbidden_retrieval"]) for r in results)},
            "answers": {"cases": len(results), "correct_outcomes": sum(r["answer_correct"] for r in results),
                        "ready": ready, "coverage": ready / len(results),
                        "ready_quality": ready_correct / ready if ready else None}, "cases": results}


def comparison(directory):
    root = Path(directory)
    identity = {p.name: sha(p.read_text(encoding="utf-8")) for p in sorted((root / "secure-fixtures").glob("*.md"))}
    identity["security-metadata.json"] = sha((root / "security-metadata.json").read_text())
    identity["cases"] = sha(json.dumps(CASES))
    reports = {mode: evaluate(root, mode) for mode in ("lexical", "hybrid")}
    safe = all(r["retrieval"]["forbidden_retrieval_count"] == 0 for r in reports.values())
    improved = reports["hybrid"]["retrieval"]["recall_at_3"] > reports["lexical"]["retrieval"]["recall_at_3"]
    correct = reports["hybrid"]["answers"]["correct_outcomes"] == len(CASES)
    return {"evaluation_version": "curated-rag-v1", "fixture_hashes": identity,
            "evidence_kind": "offline-curated-control-test", "reports": reports,
            "decision": "KEEP_HYBRID_FOR_THIS_FIXTURE_ONLY" if safe and improved and correct else "NO_RELEASE",
            "limits": ["Hand-authored embeddings, English intent routes and reviewed claims",
                       "No general contradiction detector, model judge or live-model evidence",
                       "Recall denominator uses authorized expected documents, not all stored documents"]}
