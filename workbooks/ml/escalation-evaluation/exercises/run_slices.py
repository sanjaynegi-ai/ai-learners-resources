"""Print slice tables at the frozen threshold, using your slice_table (or the reference with --reference).

From the escalation-evaluation directory, after `python -m escalation_eval.report --stage validation`:
    uv run python exercises/run_slices.py --by tag [--split validation|test] [--reference]
"""
import argparse
import json

from escalation_eval.data import load_tickets, time_split
from escalation_eval.models import fit_logistic, model_scores
from escalation_eval.report import RESULTS

parser = argparse.ArgumentParser()
parser.add_argument("--by", default="tag", help="Column to slice by: tag, language, channel or month")
parser.add_argument("--split", choices=["validation", "test"], default="validation")
parser.add_argument("--min-positives", type=int, default=30)
parser.add_argument("--reference", action="store_true")
args = parser.parse_args()
if args.reference:
    from slices_reference import slice_table
else:
    from slices import slice_table

frozen_path = RESULTS / "frozen.json"
if not frozen_path.exists():
    raise SystemExit("Run `python -m escalation_eval.report --stage validation` first.")
if args.split == "test" and not (RESULTS / "test-report.json").exists():
    raise SystemExit("Score the test set once with --stage test before slicing it; slicing does not choose anything.")
threshold = json.loads(frozen_path.read_text(encoding="utf-8"))["threshold"]
splits = time_split(load_tickets())
frame = getattr(splits, args.split)
flagged = model_scores(fit_logistic(splits.train), frame) >= threshold
print(f"{args.split} split, threshold {threshold:.3f}, sliced by {args.by} (small = fewer than {args.min_positives} escalations)")
print(f"  {'value':12} {'tickets':>7} {'escal.':>6} {'flags':>5}  recall                              precision")
for row in slice_table(frame, flagged, args.by, args.min_positives):
    print(f"  {row.value:12} {row.tickets:7} {row.positives:6} {row.flags:5}  {str(row.recall):35} {row.precision}"
          f"{'  <- small' if row.small else ''}")
