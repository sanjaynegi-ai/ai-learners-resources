"""Optional authored reranking mechanics, not learned relevance scoring."""
from dataclasses import asdict
import json
import math
from pathlib import Path
import re
import tempfile
import time

from .core import rank
from .grounded import Store


def authored_scores(query, chunks):
    # Intentionally overbroad: helps approval queries, harms return-window queries.
    return [(c.id, 10.0 if "refund" in query.lower() and "require supervisor" in c.text.lower() else 0.0)
            for c in chunks]


def compare_query(store, session, query, *, now=100, pool_size=4, scorer=authored_scores,
                  before_scoring=None, after_scoring=None):
    if type(pool_size) is not int or not 1 <= pool_size <= 8:
        raise ValueError("Candidate pool must be 1..8")
    if not isinstance(query, str) or not 0 < len(query.strip()) <= 200:
        raise ValueError("Query must contain 1..200 characters")
    started = time.perf_counter_ns()
    chunks = store.candidates(session, now)  # Trusted current tenant/role/expiry/revision filtering first.
    pool = [c for c, _ in rank(chunks, query, mode="lexical", k=pool_size)]
    snapshots = {c.id: store.allowed(session, c.document, now)["revision"] for c in pool}
    baseline_finished = time.perf_counter_ns()

    def current():
        try:
            for c in pool:
                doc = store.allowed(session, c.document, now)
                if not doc or doc["revision"] != snapshots[c.id] or doc["hash"] != c.source_sha256:
                    return False
            store.principal(session)
            return True
        except PermissionError:
            return False

    if before_scoring:
        before_scoring()
    if not current():
        return {"baseline": [], "reranked": [], "pool": [], "status": "stale_or_denied"}
    if not pool:
        return {"baseline": [], "reranked": [], "pool": [], "status": "no_candidates"}
    proposed = scorer(query, tuple(pool))  # Local authored function only; no provider request.
    if (not isinstance(proposed, list) or len(proposed) != len(pool)
            or any(not isinstance(row, (list, tuple)) or len(row) != 2 for row in proposed)):
        raise ValueError("Require exactly one score per input candidate")
    seen = set()
    for identity, score in proposed:
        if (not isinstance(identity, str) or identity not in snapshots or identity in seen
                or type(score) not in (int, float) or not math.isfinite(score)):
            raise ValueError("Unknown/duplicate ID or non-finite score")
        seen.add(identity)
    if after_scoring:
        after_scoring()
    if not current():
        return {"baseline": [], "reranked": [], "pool": [], "status": "stale_or_denied"}
    trusted = {c.id: c for c in pool}
    ordered = [trusted[identity] for identity, score in sorted(proposed, key=lambda row: (-row[1], row[0]))]
    finished = time.perf_counter_ns()
    def payload(c):
        return dict(asdict(c), publication_revision=snapshots[c.id])
    return dict(baseline=[payload(c) for c in pool[:1]], reranked=[payload(c) for c in ordered[:1]],
                pool=[payload(c) for c in pool], status="ranked",
                timing=dict(local_baseline_ms=(baseline_finished-started)/1_000_000,
                            local_rerank_and_rechecks_ms=(finished-baseline_finished)/1_000_000))


def seed(store, fixture, directory):
    corpus = Path(directory)
    documents = fixture["documents"]
    if not 1 <= len(documents) <= 20 or any(
            not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,50}\.md", name)
            or not isinstance(item["text"], str) or len(item["text"].encode("utf-8")) > 100_000
            for name, item in documents.items()):
        raise ValueError("Require 1..20 bounded flat Markdown fixture sources")
    metadata = {"members": {"alice": ["A", "support"]}, "documents": {}}
    for name, item in fixture["documents"].items():
        (corpus / name).write_text(item["text"], encoding="utf-8")
        metadata["documents"][name] = item["metadata"]
    store.seed(corpus, metadata)


def evidence_hit(rows, case):
    return bool(case["relevant"] and any(r["document"] == case["relevant"]
                and case["required_text"] in r["text"] for r in rows))


def run(fixture):
    if not 1 <= len(fixture["cases"]) <= 8:
        raise ValueError("Comparison accepts 1..8 fixed cases")
    with tempfile.TemporaryDirectory() as directory:
        store = Store()
        try:
            seed(store, fixture, directory)
            results = []
            for case in fixture["cases"]:
                elapsed = []
                baseline_times, rerank_times = [], []
                # Wall time for this local control path only, not a model benchmark.
                for _ in range(20):
                    start = time.perf_counter_ns()
                    compared = compare_query(store, "alice", case["query"])
                    elapsed.append((time.perf_counter_ns() - start) / 1_000_000)
                    if "timing" in compared:
                        baseline_times.append(compared["timing"]["local_baseline_ms"])
                        rerank_times.append(compared["timing"]["local_rerank_and_rechecks_ms"])
                results.append(dict(case=case["id"], relevant=case["relevant"],
                                    baseline_hit=evidence_hit(compared["baseline"], case),
                                    reranked_hit=evidence_hit(compared["reranked"], case),
                                    no_answer_with_candidates=not case["relevant"] and bool(compared["pool"]),
                                    local_combined_control_p95_ms=sorted(elapsed)[18], repetitions=20,
                                    local_baseline_p95_ms=sorted(baseline_times)[18] if baseline_times else None,
                                    local_rerank_and_rechecks_p95_ms=sorted(rerank_times)[18] if rerank_times else None,
                                    **compared))
            answerable = [r for r in results if r["relevant"]]
            gains = [r["case"] for r in answerable if r["reranked_hit"] and not r["baseline_hit"]]
            regressions = [r["case"] for r in answerable if r["baseline_hit"] and not r["reranked_hit"]]
            return dict(fixture_version=fixture["version"], evidence_kind="authored-rule control comparison",
                        cases=results, answerable_n=len(answerable),
                        baseline_hits=sum(r["baseline_hit"] for r in answerable),
                        reranked_hits=sum(r["reranked_hit"] for r in answerable),
                        gains=gains, regressions=regressions,
                        cost={"paid_provider_calls": 0, "provider_charge_usd": 0,
                              "local_compute": "not priced", "learned_reranker_latency_cost": "NOT MEASURED"},
                        decision="REJECT_ADOPTION; retain only optional mechanics exercise",
                        reason="One targeted gain does not compensate for a diagnosed regression; no learned-reranker evidence")
        finally:
            store.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=Path("reranking-cases.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.fixture.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as destination:
        json.dump(result, destination, indent=2)
        destination.write("\n")
    print(json.dumps({key: result[key] for key in ("baseline_hits", "reranked_hits", "answerable_n", "gains", "regressions", "decision")}))
