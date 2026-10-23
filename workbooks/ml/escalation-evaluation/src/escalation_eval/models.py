"""Two baselines and one learned model. Each returns a score per ticket; higher means flag first."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data import CATEGORICAL, FEATURES, NUMERIC, check_features


def constant_scores(frame: pd.DataFrame) -> np.ndarray:
    """Always "no escalation": the free baseline every model must beat."""
    return np.zeros(len(frame))


def rule_scores(frame: pd.DataFrame) -> np.ndarray:
    """Today's manual rule: flag large refunds or chargebacks. Scores are 0/1, so its only threshold is 0.5."""
    return ((frame["amount"] >= 500) | (frame["tag"] == "chargeback")).astype(float).to_numpy()


def build_logistic(features: tuple[str, ...] = FEATURES) -> Pipeline:
    """Scaling and encoding live inside the pipeline, so they are fitted on training rows only."""
    check_features(features)
    numeric = [name for name in features if name in NUMERIC]
    categorical = [name for name in features if name in CATEGORICAL]
    prep = ColumnTransformer([("numeric", StandardScaler(), numeric),
                              ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical)])
    return Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=2000))])


def fit_logistic(train: pd.DataFrame, features: tuple[str, ...] = FEATURES) -> Pipeline:
    return build_logistic(features).fit(train[list(features)], train["y"])


def model_scores(model: Pipeline, frame: pd.DataFrame, features: tuple[str, ...] = FEATURES) -> np.ndarray:
    return model.predict_proba(frame[list(features)])[:, 1]
