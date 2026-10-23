"""Evaluate reviewed run records. No provider calls and no automatic model judge."""
import hashlib
import json
import math
from pathlib import Path

HARNESS_VERSION = "0.1.0"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(bundle):
    if bundle["schema_version"] != 1 or not bundle["dataset_version"]:
        raise ValueError("Unsupported schema or missing dataset version")
    if bundle["evidence_kind"] not in ("synthetic", "real-model-reviewed"):
        raise ValueError("Unknown evidence kind")
    gates = bundle["gates"]
    if type(gates["minimum_slice_n"]) is not int or gates["minimum_slice_n"] < 1:
        raise ValueError("Invalid minimum sample")
    for key in ("minimum_accuracy", "minimum_quality", "maximum_regression", "minimum_answerable_coverage",
                "maximum_p95_ms", "maximum_cost_per_request_usd"):
        value = gates[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid gate")
        if key in ("minimum_accuracy", "minimum_quality", "maximum_regression", "minimum_answerable_coverage") and value > 1:
            raise ValueError("Fraction gate outside [0, 1]")
    cases = bundle["cases"]
    ids, groups = set(), {"development": set(), "heldout": set()}
    if not cases:
        raise ValueError("Empty dataset")
    for case in cases:
        if case["id"] in ids or case["split"] not in groups:
            raise ValueError("Duplicate case or unknown split")
        ids.add(case["id"])
        groups[case["split"]].add(case["group"])
        if case["expected"] not in ("ready", "abstained") or not case["slices"]:
            raise ValueError("Invalid expectation or missing slices")
    if not all(groups.values()) or groups["development"] & groups["heldout"]:
        raise ValueError("Missing split or related-case leakage between splits")
    for version, run in bundle["runs"].items():
        if not all(run["versions"].get(k) for k in ("application", "prompt", "model", "schema", "pricing")):
            raise ValueError("Missing reproduction version")
        if set(run["records"]) != ids:
            raise ValueError(f"Missing or extra records: {version}")
        for record in run["records"].values():
            if record["status"] not in ("ready", "abstained", "failed"):
                raise ValueError("Invalid outcome")
            if type(record["correct"]) is not bool or type(record["unsafe"]) is not bool:
                raise ValueError("Review labels must be booleans")
            for key in ("latency_ms", "cost_usd"):
                value = record[key]
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    raise ValueError("Invalid measurement")


def metrics(cases, records):
    rows = [records[c["id"]] for c in cases]
    n = len(rows)
    ready = sum(r["status"] == "ready" for r in rows)
    correct_ready = sum(r["status"] == "ready" and r["correct"] and not r["unsafe"] for r in rows)
    answerable = sum(c["expected"] == "ready" for c in cases)
    served = sum(c["expected"] == "ready" and records[c["id"]]["status"] == "ready"
                 and records[c["id"]]["correct"] and not records[c["id"]]["unsafe"] for c in cases)
    matched = sum(records[c["id"]]["status"] == c["expected"] and records[c["id"]]["correct"]
                  and not records[c["id"]]["unsafe"] for c in cases)
    latencies = sorted(r["latency_ms"] for r in rows)
    return {"requests": n, "ready": ready, "correct_ready": correct_ready,
            "quality": correct_ready / ready if ready else None,
            "coverage": ready / n, "answerable": answerable, "served_answerable": served,
            "answerable_coverage": served / answerable if answerable else None,
            "matched": matched, "outcome_accuracy": matched / n,
            "unsafe": sum(r["unsafe"] for r in rows),
            "failed": sum(r["status"] == "failed" for r in rows),
            "latency_p95_ms": latencies[math.ceil(.95 * n) - 1],
            "total_cost_usd": sum(r["cost_usd"] for r in rows),
            "cost_per_request_usd": sum(r["cost_usd"] for r in rows) / n}


def evaluate(bundle, candidate, baseline, split):
    validate(bundle)
    if candidate == baseline or split not in ("development", "heldout"):
        raise ValueError("Choose distinct candidate/baseline and a valid split")
    cases = [c for c in bundle["cases"] if c["split"] == split]
    names = sorted({s for c in cases for s in c["slices"]})
    report = {"harness_version": HARNESS_VERSION, "dataset_version": bundle["dataset_version"],
              "bundle_sha256": digest(bundle), "gate_sha256": digest(bundle["gates"]),
              "split": split, "candidate": candidate, "baseline": baseline,
              "evidence_kind": bundle["evidence_kind"], "versions": {}, "metrics": {}}
    for version in (baseline, candidate):
        run = bundle["runs"][version]
        report["versions"][version] = run["versions"]
        report["metrics"][version] = {"all": metrics(cases, run["records"])}
        for name in names:
            report["metrics"][version][name] = metrics([c for c in cases if name in c["slices"]], run["records"])
    reasons = []
    gates = bundle["gates"]
    for name, current in report["metrics"][candidate].items():
        before = report["metrics"][baseline][name]
        if current["requests"] < gates["minimum_slice_n"]:
            reasons.append(f"{name}: insufficient sample")
        if current["unsafe"]:
            reasons.append(f"{name}: critical unsafe output")
        if current["quality"] is not None and current["quality"] < gates["minimum_quality"]:
            reasons.append(f"{name}: ready quality below floor")
        if current["outcome_accuracy"] < gates["minimum_accuracy"]:
            reasons.append(f"{name}: accuracy below floor")
        if current["outcome_accuracy"] < before["outcome_accuracy"] - gates["maximum_regression"]:
            reasons.append(f"{name}: accuracy regression")
        if current["answerable_coverage"] is not None and current["answerable_coverage"] < gates["minimum_answerable_coverage"]:
            reasons.append(f"{name}: answerable coverage below floor")
        if current["latency_p95_ms"] > gates["maximum_p95_ms"]:
            reasons.append(f"{name}: latency above ceiling")
        if current["cost_per_request_usd"] > gates["maximum_cost_per_request_usd"]:
            reasons.append(f"{name}: cost above ceiling")
    report["gate_passed"] = not reasons
    report["reasons"] = reasons
    report["decision"] = "NO_RELEASE" if reasons else "PASS_RECORDED_GATES_REQUIRES_REVIEW"
    # Passing finite fixtures is never authorization to publish/deploy.
    return report


def freeze(bundle, candidate, baseline):
    report = evaluate(bundle, candidate, baseline, "development")
    if not report["gate_passed"]:
        raise ValueError("Development gates failed; cannot freeze candidate")
    return {"bundle_sha256": digest(bundle), "candidate": candidate, "baseline": baseline,
            "development_report_sha256": digest(report), "harness_version": HARNESS_VERSION}


def final(bundle, lock):
    expected = freeze(bundle, lock["candidate"], lock["baseline"])
    if lock != expected:
        raise ValueError("Frozen candidate or evidence changed; start a new evaluation cycle")
    report = evaluate(bundle, lock["candidate"], lock["baseline"], "heldout")
    report["selection_sha256"] = digest(lock)
    return report
