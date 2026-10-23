"""Choose a flagging threshold on validation data under a review-capacity limit."""
from dataclasses import dataclass

import numpy as np

from .metrics import Counts


@dataclass(frozen=True)
class ThresholdChoice:
    threshold: float
    counts: Counts
    cost: float


def choose_threshold(scores, actual, *, capacity: float, fn_cost: float, fp_cost: float) -> ThresholdChoice:
    """Lowest-cost threshold whose flag rate stays within capacity (a fraction of tickets).

    Candidates are the distinct scores themselves, so every achievable flag set is considered.
    Flags beyond capacity would not be reviewed, so over-capacity options are never chosen.
    """
    if not 0 < capacity <= 1 or fn_cost < 0 or fp_cost < 0:
        raise ValueError("capacity must be in (0, 1] and costs must be non-negative")
    scores, actual = np.asarray(scores, dtype=float), np.asarray(actual).astype(bool)
    if scores.shape != actual.shape or scores.size == 0:
        raise ValueError("scores and actual must be non-empty and the same length")
    limit = int(np.floor(capacity * scores.size))
    best: ThresholdChoice | None = None
    for threshold in np.unique(np.append(scores, np.inf)):  # inf = flag nothing, always feasible
        counts = Counts.from_arrays(actual, scores >= threshold)
        if counts.flags > limit:
            continue
        cost = counts.cost(fn_cost, fp_cost)
        if best is None or cost < best.cost:
            best = ThresholdChoice(float(threshold), counts, cost)
    assert best is not None
    return best
