"""Integrity/completeness check, never an automated claim of independent competence."""
import argparse
import hashlib
import json
from pathlib import Path

ARTIFACTS = ("discovery", "requirements", "acceptance", "architecture", "threat_model", "decisions",
             "cost", "runbook", "incident", "handover", "evaluation", "tests", "assistance")
GATES = ("authorization", "bounded_execution", "secret_review", "truthful_evidence", "evaluation_failures_visible")
MILESTONES = ("real_model_review", "deployment", "individual_defense", "independent_transfer")


def check(root, manifest):
    root = Path(root).resolve()
    reasons = []
    checked = {}
    for name in ARTIFACTS:
        item = manifest.get("artifacts", {}).get(name, {})
        relative = item.get("path", "")
        path = (root/relative).resolve()
        if not relative or not path.is_relative_to(root) or not path.is_file():
            reasons.append(f"artifact_missing_or_outside:{name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item.get("sha256"):
            reasons.append(f"artifact_changed:{name}")
        checked[name] = {"path": relative, "sha256": actual}
    for name in GATES:
        gate = manifest.get("gates", {}).get(name, {})
        if gate.get("status") != "pass" or not gate.get("evidence") or not gate.get("reviewer"):
            reasons.append(f"gate_not_demonstrated:{name}")
    for name in MILESTONES:
        milestone = manifest.get("milestones", {}).get(name, {})
        if milestone.get("status") != "pass" or not milestone.get("evidence") or not milestone.get("reviewer"):
            reasons.append(f"milestone_pending:{name}")
    return {"decision": "NO_RELEASE" if reasons else "REVIEW_REQUIRED", "reasons": reasons,
            "checked_artifacts": checked,
            "limits": "Hashes check integrity only. Human reviewers must inspect evidence paths, results, identity and competency; declarations alone never confer graduation."}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--root", type=Path, default=Path.cwd())
    args = p.parse_args()
    result = check(args.root, json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
    raise SystemExit(2 if result["decision"] == "NO_RELEASE" else 0)
