"""Counts first, percentages second: every rate carries its numerator and denominator."""
import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Rate:
    numerator: int
    denominator: int

    @property
    def value(self) -> float | None:
        """None when nothing was counted: a 0/0 precision is undefined, not 0% or 100%."""
        return self.numerator / self.denominator if self.denominator else None

    def interval(self, z: float = 1.96) -> tuple[float, float] | None:
        """Wilson score interval; better behaved than p ± z·SE for small denominators."""
        n = self.denominator
        if not n:
            return None
        p = self.numerator / n
        centre = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return max(0.0, centre - half), min(1.0, centre + half)

    def __str__(self) -> str:
        if self.value is None:
            return f"n/a ({self.numerator}/{self.denominator})"
        low, high = self.interval()
        return f"{self.value:.1%} ({self.numerator}/{self.denominator}; 95% CI {low:.0%}-{high:.0%})"


@dataclass(frozen=True)
class Counts:
    tp: int
    fp: int
    fn: int
    tn: int

    @classmethod
    def from_arrays(cls, actual, flagged) -> "Counts":
        actual, flagged = np.asarray(actual).astype(bool), np.asarray(flagged).astype(bool)
        if actual.shape != flagged.shape:
            raise ValueError("actual and flagged must have the same length")
        return cls(tp=int(np.sum(flagged & actual)), fp=int(np.sum(flagged & ~actual)),
                   fn=int(np.sum(~flagged & actual)), tn=int(np.sum(~flagged & ~actual)))

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    @property
    def flags(self) -> int:
        return self.tp + self.fp

    @property
    def positives(self) -> int:
        return self.tp + self.fn

    def precision(self) -> Rate:
        return Rate(self.tp, self.flags)

    def recall(self) -> Rate:
        return Rate(self.tp, self.positives)

    def accuracy(self) -> Rate:
        return Rate(self.tp + self.tn, self.total)

    def flag_rate(self) -> Rate:
        return Rate(self.flags, self.total)

    def cost(self, fn_cost: float, fp_cost: float) -> float:
        return self.fn * fn_cost + self.fp * fp_cost
