"""Release decision: candidate against the current baseline, on the held-out split, through versioned gates.

Every run is appended to a registry with its manifest. Held-out reuse is counted: each new candidate scored on
the same held-out split makes it a little more of a development set, so the decision says so.
"""
import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path

from .harness import Run

GATES = Path(__file__).resolve().parents[2] / "data" / "gates.json"
RESULTS = Path(os.environ.get("EVAL_HARNESS_RESULTS", "results"))
Gate = Callable[[Run, Run], tuple[str, str]]  # (status, detail); status is pass | fail | insufficient


def load_gates(path: Path = GATES) -> dict:
    gates = json.loads(path.read_text(encoding="utf-8"))
    # Fingerprint of the thresholds themselves (not file bytes or line endings): an edited gate file cannot pass as
    # the reviewed one, even if its gates_version name is left unchanged.
    canonical = json.dumps(gates, sort_keys=True, separators=(",", ":"))
    return gates | {"gates_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]}


def record(run: Run, registry: Path | None = None) -> None:
    registry = registry or RESULTS / "registry.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"manifest": run.manifest, "summary": run.summary}, ensure_ascii=False) + "\n")


def heldout_candidates(registry: Path | None = None) -> set[str]:
    registry = registry or RESULTS / "registry.jsonl"
    if not registry.exists():
        return set()
    entries = [json.loads(line) for line in registry.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {e["manifest"]["prompt_sha256"] for e in entries if e["manifest"]["split"] == "heldout"}


def _pp(rate: dict) -> float:
    return 100 * (rate["value"] or 0.0)


def decide(baseline: Run, candidate: Run, gates: dict | None = None, extra_gates: tuple[Gate, ...] = (),
           registry: Path | None = None) -> dict:
    gates = gates or load_gates()
    if baseline.manifest["split"] != "heldout" or candidate.manifest["split"] != "heldout":
        raise ValueError("Release decisions use the held-out split; development results guide work, not releases")
    if baseline.manifest["dataset_sha256"] != candidate.manifest["dataset_sha256"]:
        raise ValueError("Baseline and candidate were evaluated on different data")
    b, c = baseline.summary, candidate.summary
    results = []

    def gate(name, status, detail, critical=False):
        results.append({"gate": name, "status": status, "detail": detail, "critical": critical})

    harmful = c["harmful_ready"]["k"]
    gate("harmful ready drafts", "pass" if harmful <= gates["critical"]["harmful_ready_max"] else "fail",
         f"{harmful}/{c['harmful_ready']['n']} ready drafts harmful (max {gates['critical']['harmful_ready_max']})", True)
    for key, limit in (("correct", gates["correct_max_drop_pp"]), ("coverage", gates["coverage_max_drop_pp"])):
        drop = _pp(b[key]) - _pp(c[key])
        gate(f"{key} non-regression", "pass" if drop <= limit else "fail",
             f"{c[key]['k']}/{c[key]['n']} vs baseline {b[key]['k']}/{b[key]['n']} (change {-drop:+.1f} pp; max drop {limit})")
    for name, current in candidate.slices.items():
        before = baseline.slices[name]["correct"]
        now = current["correct"]
        if now["n"] < gates["slice_min_cases"]:
            gate(f"slice {name}", "insufficient", f"only {now['n']} cases (< {gates['slice_min_cases']})")
            continue
        drop = _pp(before) - _pp(now)
        gate(f"slice {name}", "pass" if drop <= gates["slice_max_drop_pp"] else "fail",
             f"{now['k']}/{now['n']} vs {before['k']}/{before['n']} (change {-drop:+.1f} pp; max drop {gates['slice_max_drop_pp']})")
    wrong = c["wrong_language_ready"]
    gate("wrong language on ready drafts", "pass" if (wrong["value"] or 0) <= gates["wrong_language_ready_max_rate"] else "fail",
         f"{wrong['k']}/{wrong['n']} (max rate {gates['wrong_language_ready_max_rate']})")
    gate("latency p95", "pass" if c["latency_s"]["p95"] <= gates["latency_p95_max_s"] else "fail",
         f"{c['latency_s']['p95']} s (max {gates['latency_p95_max_s']})")
    gate("cost per 1,000", "pass" if c["cost_usd_per_1000"] <= gates["cost_usd_per_1000_max"] else "fail",
         f"${c['cost_usd_per_1000']} (max ${gates['cost_usd_per_1000_max']}; baseline ${b['cost_usd_per_1000']}; hypothetical prices)")
    for extra in extra_gates:
        status, detail = extra(baseline, candidate)
        gate(getattr(extra, "__name__", "extra gate"), status, detail, True)

    warnings = []
    reused = heldout_candidates(registry) - {candidate.manifest["prompt_sha256"]}
    if len(reused) >= gates["heldout_reuse_warning_after"]:
        warnings.append(f"held-out split already scored for {len(reused)} other prompt versions: it is drifting "
                        "toward a development set; refresh it before trusting small differences")
    failed = [r for r in results if r["status"] == "fail"]
    decision = "NO-RELEASE" if failed else "RELEASE"
    return {"decision": decision, "gates_version": gates["gates_version"], "gates_sha256": gates.get("gates_sha256"),
            "baseline": baseline.manifest["prompt_version"], "candidate": candidate.manifest["prompt_version"],
            "failed_gates": [r["gate"] for r in failed], "gates": results, "warnings": warnings}
