"""Classify a raw model output by the first layer that rejects it: syntax, schema, business, or none.

    refund-drafts-diagnose            # runs fixtures/diagnosis-cases.json against fixtures/eval orders

"passed" does not mean "good": it means no automated check objected. Some failures only a person can see.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .domain import FIXTURES, Order, load_records
from .schema import DraftOut
from .validate import DEFAULT_CHECKS, Check, validate


@dataclass(frozen=True)
class Diagnosis:
    layer: str          # "syntax" | "schema" | "business" | "passed"
    codes: list[str]


def diagnose(text: str, order: Order, checks: tuple[Check, ...] = DEFAULT_CHECKS) -> Diagnosis:
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return Diagnosis("syntax", ["not_json"])
    try:
        draft = DraftOut.from_json(text)
    except ValidationError as error:
        return Diagnosis("schema", sorted({f"{'.'.join(map(str, item['loc'])) or 'object'}:{item['type']}"
                                           for item in error.errors()}))
    problems = validate(draft, order, checks)
    return Diagnosis("business", problems) if problems else Diagnosis("passed", [])


def load_cases(path: Path = FIXTURES / "diagnosis-cases.json") -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def run(checks: tuple[Check, ...] = DEFAULT_CHECKS) -> list[tuple[dict, Diagnosis]]:
    orders = load_records(FIXTURES / "eval").orders
    return [(case, diagnose(case["text"], orders[case["order_id"]], checks)) for case in load_cases()]


def main() -> None:
    results = run()
    print(f"{'case':5} {'expected':9} {'actual':9} codes")
    for case, diagnosis in results:
        mark = "" if diagnosis.layer == case["expected_layer"] else "  <- differs from expected"
        print(f"{case['case_id']:5} {case['expected_layer']:9} {diagnosis.layer:9} {', '.join(diagnosis.codes) or '-'}{mark}")
        if diagnosis.layer == "passed" and case.get("what_is_wrong"):
            print(f"{'':25} human review: {case['what_is_wrong']}")
    print(f"\n{sum(d.layer == 'passed' for _, d in results)}/{len(results)} outputs passed every automated check; "
          "read each one before calling it correct.")


if __name__ == "__main__":
    main()
