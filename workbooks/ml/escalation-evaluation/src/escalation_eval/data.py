"""Load the shared ticket dataset and split it the way the model will be used: by time."""
import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DATASET = (Path(__file__).resolve().parents[5] / "shared-assets" / "quickcart-escalation-tickets"
           / "data" / "quickcart-tickets-2025.csv")
NUMERIC = ("amount", "prior_tickets_30d", "account_age_days")
CATEGORICAL = ("tag", "channel", "language")
FEATURES = NUMERIC + CATEGORICAL
# Known only after the outcome, or identifiers the model could memorize. Never model inputs.
FORBIDDEN = frozenset({"assigned_queue", "escalated", "ticket_id", "customer_id", "customer_fold", "month"})
EXPECTED_COLUMNS = {"ticket_id", "customer_id", "customer_fold", "month", "amount", "tag", "prior_tickets_30d",
                    "account_age_days", "channel", "language", "assigned_queue", "escalated"}


class DataContractError(ValueError):
    """The input data or a split violates the documented contract; evaluation must not continue."""


@dataclass(frozen=True)
class Splits:
    train: pd.DataFrame       # months 1-8: fit parameters
    validation: pd.DataFrame  # months 9-10: compare, choose thresholds, analyse errors (used many times)
    test: pd.DataFrame        # months 11-12: report once, after choices are frozen


def dataset_path() -> Path:
    """The shared CSV inside this repository, or QUICKCART_TICKETS_CSV when working outside it."""
    path = Path(os.environ.get("QUICKCART_TICKETS_CSV", DATASET))
    if not path.is_file():
        raise DataContractError(f"Dataset not found at {path}. Work inside a clone of the course repository, "
                                "or set QUICKCART_TICKETS_CSV to the shared quickcart-tickets-2025.csv.")
    return path


def load_tickets(path: Path | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path or dataset_path())
    frame.columns = [name.split("#")[-1] for name in frame.columns]  # Strip Orange's type prefixes.
    if set(frame.columns) != EXPECTED_COLUMNS:
        raise DataContractError(f"Unexpected columns: {sorted(set(frame.columns) ^ EXPECTED_COLUMNS)}")
    if frame.isna().any().any():
        raise DataContractError("Dataset contains missing values")
    if not set(frame["escalated"]) <= {"yes", "no"} or not frame["month"].between(1, 12).all():
        raise DataContractError("Label or month outside the documented values")
    frame["y"] = (frame["escalated"] == "yes").astype(int)
    return frame


def check_features(features: tuple[str, ...] = FEATURES) -> None:
    leaked = FORBIDDEN.intersection(features)
    if leaked:
        raise DataContractError(f"Forbidden model inputs: {sorted(leaked)}")


def check_splits(splits: Splits) -> None:
    """Fail loudly if a split could leak future data or let the model meet a customer twice."""
    parts = [splits.train, splits.validation, splits.test]
    if any(part.empty for part in parts):
        raise DataContractError("Every split must contain tickets")
    for earlier, later in zip(parts, parts[1:]):
        if earlier["month"].max() >= later["month"].min():
            raise DataContractError("Splits overlap in time or are out of order")
    for index, first in enumerate(parts):
        for second in parts[index + 1:]:
            if set(first["customer_id"]) & set(second["customer_id"]):
                raise DataContractError("A customer appears in more than one split")


def time_split(frame: pd.DataFrame) -> Splits:
    splits = Splits(train=frame[frame["month"] <= 8], validation=frame[frame["month"].isin([9, 10])],
                    test=frame[frame["month"] >= 11])
    check_splits(splits)
    return splits
