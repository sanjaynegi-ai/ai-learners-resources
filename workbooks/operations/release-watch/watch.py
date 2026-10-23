"""Offline release monitoring. All traffic, timings, labels and costs are synthetic."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sqlite3

VERSION = "0.1.0"
GATES = {"minimum_n": 8, "minimum_review_fraction": 1.0,
         "minimum_quality": .95, "minimum_coverage": .75,
         "maximum_quality_drop": .05, "maximum_p95_ms": 1000,
         "maximum_cost_per_request_usd": .01, "maximum_failure_fraction": .1}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def artifact(timeout_ms):
    return {"application": VERSION, "prompt": "refund-v2", "model": "simulated-v1",
            "schema": "draft-v1", "data": "policy-v1", "evaluation": "review-v1",
            "pricing": "hypothetical-v1", "config": {"timeout_ms": timeout_ms}}


def traffic(manifest):
    """Ten fixed synthetic requests; timeout change reproduces a configuration incident."""
    rows = []
    for i in range(10):
        latency = 400 if i < 6 else 900
        failed = latency > manifest["config"]["timeout_ms"]
        rows.append({"status": "failed" if failed else "ready" if i < 8 else "abstained",
                     "correct": not failed, "unsafe": False, "reviewed": True,
                     "latency_ms": min(latency, manifest["config"]["timeout_ms"]),
                     "cost_usd": .002, "slice": "routine" if i < 6 else "slow",
                     "prompt": "SYNTHETIC_PRIVATE_TICKET", "authorization": "SYNTHETIC_SECRET",
                     "tool_result": {"email": "synthetic@example.invalid"}})
    return rows


def safe_event(row):
    """Allowlist projection: never serialize arbitrary strings, IDs, nested data or exceptions."""
    if row.get("status") not in ("ready", "abstained", "failed"):
        raise ValueError("invalid status")
    if row.get("slice") not in ("routine", "slow"):
        raise ValueError("invalid slice")
    for key in ("correct", "unsafe", "reviewed"):
        if type(row.get(key)) is not bool:
            raise ValueError("invalid label")
    for key in ("latency_ms", "cost_usd"):
        value = row.get(key)
        if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
            raise ValueError("invalid measurement")
    if row["unsafe"] and row["status"] != "ready":
        raise ValueError("unsafe label requires ready outcome")
    return {key: row[key] for key in ("status", "slice", "correct", "unsafe", "reviewed",
                                    "latency_ms", "cost_usd")}


def metrics(rows):
    n = len(rows)
    ready = [r for r in rows if r["status"] == "ready"]
    reviewed = [r for r in ready if r["reviewed"]]
    good = sum(r["correct"] and not r["unsafe"] for r in reviewed)
    costs = sum(r["cost_usd"] for r in rows)
    return {"requests": n, "ready": len(ready), "reviewed_ready": len(reviewed),
            "good_ready": good, "quality": good / len(reviewed) if reviewed else None,
            "review_fraction": len(reviewed) / len(ready) if ready else None,
            "coverage": len(ready) / n if n else None,
            "abstained": sum(r["status"] == "abstained" for r in rows),
            "failed": sum(r["status"] == "failed" for r in rows),
            "unsafe": sum(r["unsafe"] for r in rows),
            "p95_ms": sorted(r["latency_ms"] for r in rows)[math.ceil(.95*n)-1] if n else None,
            "total_cost_usd": costs, "cost_per_request_usd": costs/n if n else None,
            "cost_per_good_ready_usd": costs/good if good else None}


def report(rows, manifest, baseline=None):
    safe = [safe_event(r) for r in rows]
    all_metrics = metrics(safe)
    reasons = []
    m = all_metrics
    if m["requests"] < GATES["minimum_n"]:
        reasons.append("insufficient_sample")
    for key, threshold in (("quality", "minimum_quality"), ("coverage", "minimum_coverage"),
                           ("review_fraction", "minimum_review_fraction")):
        if m[key] is None or m[key] < GATES[threshold]:
            reasons.append(key)
    if m["unsafe"]:
        reasons.append("unsafe")
    if m["requests"] and m["failed"] / m["requests"] > GATES["maximum_failure_fraction"]:
        reasons.append("failures")
    if m["p95_ms"] is not None and m["p95_ms"] > GATES["maximum_p95_ms"]:
        reasons.append("latency")
    if m["cost_per_request_usd"] is not None and m["cost_per_request_usd"] > GATES["maximum_cost_per_request_usd"]:
        reasons.append("cost")
    if baseline:
        if baseline["input_contract"] != "quickcart-ten-v1" or baseline["gates_sha256"] != digest(GATES):
            raise ValueError("incompatible baseline")
        old = baseline["metrics"]["quality"]
        if old is None or m["quality"] is None or old-m["quality"] > GATES["maximum_quality_drop"]:
            reasons.append("quality_regression")
    return {"monitor_version": VERSION, "evidence_kind": "synthetic", "input_contract": "quickcart-ten-v1",
            "artifact": manifest, "artifact_sha256": digest(manifest), "window_sha256": digest(safe),
            "gates": GATES.copy(), "gates_sha256": digest(GATES),
            "metrics": m, "slices": {s: metrics([r for r in safe if r["slice"] == s]) for s in ("routine", "slow")},
            "halt": bool(reasons), "reasons": reasons}


class Store:
    """Local single-operator SQLite store; role must come from trusted caller in a service."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS events (at INTEGER NOT NULL, body TEXT NOT NULL)")

    def append(self, row, at):
        if type(at) is not int or at < 0:
            raise ValueError("invalid clock")
        with self.db:
            self.db.execute("INSERT INTO events VALUES (?, ?)", (at, json.dumps(safe_event(row))))

    def read(self, role):
        if role not in ("oncall", "reviewer"):
            raise PermissionError("telemetry access denied")
        return [json.loads(r[0]) for r in self.db.execute("SELECT body FROM events ORDER BY at, rowid")]

    def expire(self, now, retention_seconds=604800):
        if type(now) is not int or now < 0 or type(retention_seconds) is not int or retention_seconds < 1:
            raise ValueError("invalid retention")
        with self.db:
            return self.db.execute("DELETE FROM events WHERE at <= ?", (now-retention_seconds,)).rowcount

    def close(self):
        self.db.close()


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def exercise(out):
    """Reversible synthetic canary incident, with an actual on-disk active artifact."""
    out.mkdir(parents=True, exist_ok=False)
    stable, candidate = artifact(1200), artifact(500)
    registry = {digest(m): m for m in (stable, candidate)}
    write_new(out / "registry.json", registry)
    write_new(out / "active.json", candidate)
    base = report(traffic(stable), stable)
    bad = report(traffic(candidate), candidate, base)
    write_new(out / "baseline.json", base)
    write_new(out / "canary.json", bad)
    store = Store(out / "telemetry.sqlite")
    try:
        for row in traffic(candidate):
            store.append(row, 100)
        assert len(store.read("oncall")) == 10
        expired = store.expire(604900)
    finally:
        store.close()
    if not bad["halt"]:
        raise RuntimeError("exercise failed to detect incident")
    write_new(out / "rollout.json", {"halted": True, "owner": "application-oncall", "candidate": digest(candidate)})
    restored = registry[base["artifact_sha256"]]
    if digest(restored) != base["artifact_sha256"] or restored["schema"] != candidate["schema"]:
        raise ValueError("rollback artifact invalid or incompatible")
    (out / "active.json").write_text(json.dumps(restored, indent=2)+"\n", encoding="utf-8")
    active = json.loads((out / "active.json").read_text(encoding="utf-8"))
    recovery = report(traffic(active), active, base)
    write_new(out / "recovery.json", recovery)
    if recovery["halt"]:
        raise RuntimeError("recovery failed; keep rollout halted")
    timeline = {"evidence_kind": "synthetic", "time_basis": "logical minutes, not measured response time",
                "events": [{"minute": 0, "action": "canary timeout 1200 to 500 ms"},
                           {"minute": 1, "action": "detect coverage/failure regression; application-oncall owns incident"},
                           {"minute": 2, "action": "halt rollout; compare manifest config and slow slice"},
                           {"minute": 3, "action": "restore compatible stable artifact; preserve halt"},
                           {"minute": 4, "action": "replay recovery probes; all gates pass"}],
                "expired_events": expired, "rollout_remains_halted": True,
                "diagnosis": "500 ms deadline rejects four 900 ms requests, including two answerable cases",
                "pending": ["independent review before resume", "live provider and deployment verification"]}
    write_new(out / "incident.json", timeline)
    (out / "runbook-update.md").write_text(
        "# Exercise amendment — timeout regression\n\n"
        "Observed slow-slice failures after the only manifest change: timeout 1200 → 500 ms. "
        "Before timeout changes, replay slow answerable and abstaining probes; compare coverage and "
        "failure counts even when conditional quality stays 1.0. Application-oncall owns this gate. "
        "Keep rollout halted after recovery until a separate reviewer approves new evidence. "
        "This amendment records the synthetic exercise, not a production incident.\n", encoding="utf-8")
    return {"baseline_halt": base["halt"], "canary_halt": bad["halt"], "recovery_halt": recovery["halt"],
            "expired_events": expired, "restored_artifact": digest(active)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new output directory; existing work is never overwritten")
    args = parser.parse_args()
    print(json.dumps(exercise(args.out), indent=2))
