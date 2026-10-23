"""Validate review records and preserve disagreement; never infer human identity."""
import argparse
import json
from pathlib import Path
from .core import digest, load

DIMENSIONS = ("support", "task", "language", "safety")


def validate_row(row, language, languages):
    if set(row["scores"]) != set(DIMENSIONS) or not isinstance(row.get("reason"), str) or len(row["reason"].strip()) < 4:
        raise ValueError("All dimensions and an evidence-based reason are required")
    for value in row["scores"].values():
        if value is not None and (type(value) is not int or value not in (0, 1)):
            raise ValueError("Scores are 0, 1 or null (uncertain), never coerced")
    if language not in languages and any(v is not None for v in row["scores"].values()):
        raise ValueError("Unreviewable language must remain uncertain")


def validate_review(review, packet, rubric):
    if review.get("packet_sha256") != digest(packet) or review.get("rubric_sha256") != digest(rubric):
        raise ValueError("Packet or rubric changed; retain this pass and start a new round")
    reviewer = review["reviewer"]
    if (not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip()
            or reviewer.get("kind") not in ("human", "authored_demo")
            or type(reviewer.get("blind_to_other_pass")) is not bool
            or not isinstance(reviewer.get("languages"), list)):
        raise ValueError("Missing reviewer identity, evidence kind or independence declaration")
    cases = {c["id"]: c for c in packet["cases"]}
    if not 1 <= len(cases) <= 12 or len(cases) != len(packet["cases"]) or set(review["labels"]) != set(cases):
        raise ValueError("Require exactly one label record per unique case")
    for case_id, row in review["labels"].items():
        validate_row(row, cases[case_id]["language"], reviewer["languages"])


def compare(packet, rubric, first, second, adjudication=None):
    validate_review(first, packet, rubric)
    validate_review(second, packet, rubric)
    a, b = first["reviewer"], second["reviewer"]
    mode = ("authored_demo" if "authored_demo" in (a["kind"], b["kind"]) else
            "self_calibration" if a["id"] == b["id"] else
            "independent_human_attested" if a["blind_to_other_pass"] and b["blind_to_other_pass"] else
            "non_independent")
    agreement = {}
    for dimension in DIMENSIONS:
        pairs = [(first["labels"][case["id"]]["scores"][dimension],
                  second["labels"][case["id"]]["scores"][dimension]) for case in packet["cases"]]
        comparable = [(x, y) for x, y in pairs if x is not None and y is not None]
        matches = sum(x == y for x, y in comparable)
        agreement[dimension] = dict(matches=matches, comparable=len(comparable), total=len(pairs),
                                    fraction=matches / len(comparable) if comparable else None)
    disagreements = {}
    for case in packet["cases"]:
        left, right = first["labels"][case["id"]]["scores"], second["labels"][case["id"]]["scores"]
        disputed = [d for d in DIMENSIONS if left[d] is None or right[d] is None or left[d] != right[d]]
        if disputed:
            disagreements[case["id"]] = disputed
    resolutions = {}
    if adjudication is not None:
        if (adjudication.get("first_sha256") != digest(first) or adjudication.get("second_sha256") != digest(second)
                or adjudication.get("rubric_sha256") != digest(rubric)
                or adjudication.get("kind") not in ("human", "authored_demo")
                or not adjudication.get("adjudicator")):
            raise ValueError("Adjudication must identify unchanged passes, rubric and owner")
        if set(adjudication["resolutions"]) != set(disagreements):
            raise ValueError("Resolve every disputed/uncertain case; do not invent additional resolutions")
        for case_id, row in adjudication["resolutions"].items():
            case = next(c for c in packet["cases"] if c["id"] == case_id)
            validate_row(row, case["language"], adjudication.get("languages", []))
            resolutions[case_id] = row
    unresolved = [case_id for case_id in disagreements if case_id not in resolutions
                  or any(v is None for v in resolutions[case_id]["scores"].values())]
    if mode == "independent_human_attested" and adjudication and adjudication["kind"] != "human":
        mode = "authored_demo"  # Human passes cannot launder an authored resolution into human evidence.
    critical_cases = []
    for case in packet["cases"]:
        case_id = case["id"]
        final = resolutions.get(case_id, first["labels"][case_id])["scores"]
        if case_id not in unresolved and final["safety"] == 0:
            critical_cases.append(case_id)
    return dict(mode=mode, identity_verification="Declarations only; tool cannot verify people or blindness",
                packet_sha256=digest(packet), rubric_sha256=digest(rubric),
                first_sha256=digest(first), second_sha256=digest(second),
                agreement=agreement, disagreements=disagreements, resolutions=resolutions, unresolved=unresolved,
                critical_cases=critical_cases,
                independent_evidence_complete=mode == "independent_human_attested" and not unresolved,
                original_passes=[first, second], adjudication=adjudication,
                release_decision="NOT_A_RELEASE_GATE; preserve existing application/semantic/reviewer gates")


def template(packet, rubric, reviewer_id):
    return dict(packet_sha256=digest(packet), rubric_sha256=digest(rubric),
                reviewer=dict(id=reviewer_id, kind="human", languages=[], blind_to_other_pass=False),
                labels={c["id"]: dict(scores={d: None for d in DIMENSIONS}, reason="Not yet reviewed") for c in packet["cases"]})


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("template", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--packet", type=Path, default=Path("calibration/sample.json"))
        p.add_argument("--rubric", type=Path, default=Path("calibration/rubric-v1.json"))
        p.add_argument("--output", type=Path, required=True)
        if name == "template":
            p.add_argument("--reviewer", required=True)
        else:
            p.add_argument("--first", type=Path, required=True)
            p.add_argument("--second", type=Path, required=True)
            p.add_argument("--adjudication", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output exists; preserve the prior record and choose a new path")
    packet, rubric = load(args.packet), load(args.rubric)
    result = (template(packet, rubric, args.reviewer) if args.command == "template" else
              compare(packet, rubric, load(args.first), load(args.second),
                      load(args.adjudication) if args.adjudication else None))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as destination:
        json.dump(result, destination, ensure_ascii=False, indent=2)
        destination.write("\n")
    print("Review record written; evidence kind and unresolved cases remain explicit")


if __name__ == "__main__":
    main()
