"""Evaluation report. Validation may be run many times; test only with a configuration frozen on validation.

    python -m escalation_eval.report --stage validation [--capacity 0.10] [--errors 10] [--curve tag=returns --months 10]
    python -m escalation_eval.report --stage test
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from .data import FEATURES, dataset_path, load_tickets, time_split
from .metrics import Counts
from .models import constant_scores, fit_logistic, model_scores, rule_scores
from .thresholds import choose_threshold

RESULTS = Path(os.environ.get("ESCALATION_EVAL_RESULTS", "results"))
FN_COST, FP_COST = 40.0, 4.0  # Hypothetical minutes per missed escalation / false alarm (SG-ML-01, section 5).


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def row(name: str, counts: Counts) -> dict:
    return {"name": name, "flags": str(counts.flag_rate()), "precision": str(counts.precision()),
            "recall": str(counts.recall()), "accuracy": str(counts.accuracy()),
            "cost_minutes": counts.cost(FN_COST, FP_COST), "counts": counts.__dict__}


def print_rows(title: str, rows: list[dict]) -> None:
    print(f"\n{title}")
    for item in rows:
        print(f"  {item['name']:34} flags {item['flags']}\n{'':36} precision {item['precision']}\n"
              f"{'':36} recall {item['recall']}\n{'':36} accuracy {item['accuracy']}   cost {item['cost_minutes']:.0f} min")


def compare(frame: pd.DataFrame, scores: np.ndarray, threshold: float, label: str) -> list[dict]:
    actual = frame["y"].to_numpy()
    return [row("Constant (always no)", Counts.from_arrays(actual, constant_scores(frame) > 0.5)),
            row("Rule (amount >= 500 or chargeback)", Counts.from_arrays(actual, rule_scores(frame) >= 0.5)),
            row("Logistic regression @ 0.5", Counts.from_arrays(actual, scores >= 0.5)),
            row(f"Logistic regression @ {threshold:.3f} ({label})", Counts.from_arrays(actual, scores >= threshold))]


def show_errors(frame: pd.DataFrame, scores: np.ndarray, threshold: float, limit: int) -> None:
    view = frame.assign(score=scores.round(3), flagged=scores >= threshold)
    columns = ["ticket_id", "month", "amount", "tag", "prior_tickets_30d", "account_age_days", "channel", "language", "score"]
    missed = view[(view["y"] == 1) & ~view["flagged"]].sort_values("score")
    alarms = view[(view["y"] == 0) & view["flagged"]].sort_values("score", ascending=False)
    print(f"\nMissed escalations: {len(missed)} (lowest scores first; first {limit})")
    print(missed[columns].head(limit).to_string(index=False))
    print(f"\nFalse alarms: {len(alarms)} (highest scores first; first {limit})")
    print(alarms[columns].head(limit).to_string(index=False))


def show_curve(frame: pd.DataFrame, scores: np.ndarray, condition: str, months: list[int] | None) -> None:
    column, _, value = condition.partition("=")
    if column not in frame.columns or not value:
        raise SystemExit(f"--curve expects column=value, for example tag=returns; got {condition!r}")
    mask = frame[column].astype(str) == value
    if months:
        mask &= frame["month"].isin(months)
    actual = frame.loc[mask, "y"].to_numpy()[np.argsort(-scores[mask.to_numpy()], kind="stable")]
    print(f"\nRanking within {condition}{' months ' + str(months) if months else ''}: "
          f"{mask.sum()} tickets, {int(actual.sum())} escalated, out of {len(frame)} tickets in the split")
    for top in sorted({10, 20, 40, 60, 80, 100, 120, 160, 200, int(mask.sum())}):
        if top <= mask.sum():
            print(f"  flag top {top:4} -> caught {int(actual[:top].sum()):3} of {int(actual.sum())}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="QuickCart escalation evaluation (synthetic data, offline)")
    parser.add_argument("--stage", choices=["validation", "test"], required=True)
    parser.add_argument("--capacity", type=float, default=0.10, help="Max fraction of tickets supervisors can review")
    parser.add_argument("--errors", type=int, default=0, help="Validation only: list this many errors of each kind")
    parser.add_argument("--curve", help="Validation only: rank within a slice, e.g. tag=returns")
    parser.add_argument("--months", type=int, nargs="*", help="Restrict --curve to these validation months")
    args = parser.parse_args(argv)

    path = dataset_path()
    splits = time_split(load_tickets(path))
    model = fit_logistic(splits.train)
    RESULTS.mkdir(exist_ok=True)
    frozen_path, test_path = RESULTS / "frozen.json", RESULTS / "test-report.json"

    if args.stage == "validation":
        scores = model_scores(model, splits.validation)
        choice = choose_threshold(scores, splits.validation["y"], capacity=args.capacity, fn_cost=FN_COST, fp_cost=FP_COST)
        positives = int(splits.validation["y"].sum())
        print(f"Validation: months 9-10, {len(splits.validation)} tickets, {positives} escalated "
              f"({positives / len(splits.validation):.1%}). Training: months 1-8, {len(splits.train)} tickets.")
        print(f"Capacity {args.capacity:.0%} -> at most {int(np.floor(args.capacity * len(splits.validation)))} flags; "
              f"costs: missed {FN_COST:.0f} min, false alarm {FP_COST:.0f} min (hypothetical).")
        rows = compare(splits.validation, scores, choice.threshold, "chosen on validation")
        print_rows("Validation results", rows)
        if args.errors:
            show_errors(splits.validation, scores, choice.threshold, args.errors)
        if args.curve:
            show_curve(splits.validation, scores, args.curve, args.months)
        frozen = {"threshold": choice.threshold, "capacity": args.capacity, "fn_cost": FN_COST, "fp_cost": FP_COST,
                  "features": list(FEATURES), "train_months": "1-8", "dataset_sha256_16": fingerprint(path)}
        frozen_path.write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
        print(f"\nFrozen configuration written to {frozen_path}. Score the test set once with --stage test.")
        return

    if not frozen_path.exists():
        raise SystemExit("No frozen configuration. Run --stage validation first; thresholds are never chosen on test.")
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if frozen["features"] != list(FEATURES) or frozen["dataset_sha256_16"] != fingerprint(path):
        raise SystemExit("Features or dataset changed since the configuration was frozen; re-run validation.")
    if test_path.exists():
        previous = json.loads(test_path.read_text(encoding="utf-8"))
        if previous["frozen"] != frozen:
            raise SystemExit(f"The test set was already scored with a different configuration ({test_path}). "
                             "Rescoring after changes turns the test set into validation. Use a new test period, "
                             "or delete the file and record that you did so in your decision note.")
    scores = model_scores(model, splits.test)
    rows = compare(splits.test, scores, frozen["threshold"], "frozen")
    positives = int(splits.test["y"].sum())
    print(f"Test: months 11-12, {len(splits.test)} tickets, {positives} escalated ({positives / len(splits.test):.1%}).")
    print_rows("Test results (scored once with the frozen threshold)", rows)
    test_path.write_text(json.dumps({"frozen": frozen, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"\nTest report written to {test_path}.")


if __name__ == "__main__":
    main()
