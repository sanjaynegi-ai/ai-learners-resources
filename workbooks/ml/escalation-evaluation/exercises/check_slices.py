"""Acceptance check for slice_table; run explicitly, it is not part of tests/.

From the escalation-evaluation directory:
    uv run python exercises/check_slices.py              # checks your exercises/slices.py
    uv run python exercises/check_slices.py --reference  # checks the inspectable reference
"""
import sys

import numpy as np
import pandas as pd

if "--reference" in sys.argv:
    from slices_reference import slice_table
else:
    from slices import slice_table

toy = pd.DataFrame({"tag": ["a", "a", "a", "b", "b", "c"], "y": [1, 1, 0, 1, 0, 0]})
flagged = [True, False, True, False, False, False]
rows = slice_table(toy, flagged, "tag", min_positives=2)
assert [row.value for row in rows] == ["a", "b", "c"], "Sort by positives desc, then value"
a, b, c = rows
assert (a.tickets, a.positives, a.caught, a.flags) == (3, 2, 1, 2), "Counts for slice a"
assert (a.recall.numerator, a.recall.denominator) == (1, 2) and (a.precision.numerator, a.precision.denominator) == (1, 2)
assert not a.small and b.small and c.small, "Slices with fewer than min_positives positives are small"
assert b.precision.value is None and c.recall.value is None, "0/0 must stay undefined, not 0% or 100%"
assert sum(row.tickets for row in rows) == len(toy) and sum(row.caught for row in rows) == 1, "Slices must partition rows"
assert toy.equals(pd.DataFrame({"tag": ["a", "a", "a", "b", "b", "c"], "y": [1, 1, 0, 1, 0, 0]})), "Do not mutate input"
for bad in (lambda: slice_table(toy, flagged, "missing"), lambda: slice_table(toy, flagged[:-1], "tag")):
    try:
        bad()
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid column or misaligned flags must raise ValueError")
assert len(slice_table(toy, np.array(flagged), "tag", min_positives=2)) == 3, "Accept NumPy arrays too"
print(f"{slice_table.__module__}: slice checks passed; explain your implementation independently.")
