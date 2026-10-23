"""Independent exercise: per-slice metrics with denominators. Do not open slices_reference.py first."""
from dataclasses import dataclass

import pandas as pd

from escalation_eval.metrics import Rate


@dataclass(frozen=True)
class SliceRow:
    value: str           # the slice value, e.g. "returns"
    tickets: int         # tickets in the slice
    positives: int       # real escalations in the slice
    caught: int          # escalations that were flagged
    flags: int           # tickets flagged in the slice
    recall: Rate         # caught / positives
    precision: Rate      # caught / flags
    small: bool          # True when positives < min_positives: too few to judge


def slice_table(frame: pd.DataFrame, flagged, by: str, min_positives: int = 30) -> list[SliceRow]:
    """Return one SliceRow per distinct value of column `by`.

    `frame` has a 0/1 column `y`; `flagged` is a boolean sequence aligned with frame's rows.
    Order rows by positives (descending), then by value (ascending) so the output is deterministic.
    """
    # TODO 1: validate that `by` is a column and that `flagged` has one entry per row (raise ValueError).
    # TODO 2: group by the column; count tickets, positives, caught (flagged & y == 1) and flags per value.
    # TODO 3: build Rate objects so 0/0 stays "n/a" instead of becoming 0% or 100%.
    # TODO 4: mark small slices and sort as documented.
    raise NotImplementedError("Implement slice_table")
