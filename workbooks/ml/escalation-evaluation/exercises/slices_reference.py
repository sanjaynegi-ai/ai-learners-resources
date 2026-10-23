"""Inspectable reference for the slice exercise. Consulting it is disclosed assistance, not independent evidence."""
import numpy as np
import pandas as pd

from escalation_eval.metrics import Rate
from slices import SliceRow


def slice_table(frame: pd.DataFrame, flagged, by: str, min_positives: int = 30) -> list[SliceRow]:
    flagged = np.asarray(flagged).astype(bool)
    if by not in frame.columns:
        raise ValueError(f"Unknown slice column: {by}")
    if flagged.shape != (len(frame),):
        raise ValueError("flagged must have one entry per row")
    view = frame.assign(_flag=flagged, _caught=flagged & (frame["y"].to_numpy() == 1))
    rows = []
    for value, group in view.groupby(by, sort=False):
        positives, caught, flags = int(group["y"].sum()), int(group["_caught"].sum()), int(group["_flag"].sum())
        rows.append(SliceRow(value=str(value), tickets=len(group), positives=positives, caught=caught, flags=flags,
                             recall=Rate(caught, positives), precision=Rate(caught, flags),
                             small=positives < min_positives))
    return sorted(rows, key=lambda row: (-row.positives, row.value))
