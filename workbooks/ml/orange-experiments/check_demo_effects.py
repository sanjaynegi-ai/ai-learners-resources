"""Maintainer check: prove the synthetic dataset still produces every effect the Orange demo points out.

The live demo runs in the Orange GUI; this script does not use Orange. It re-creates each comparison
with scikit-learn and asserts the *direction and rough size* of the effect, not Orange's exact numbers.
From this directory:

    uv run --no-project --python 3.11 --with scikit-learn==1.9.1 python check_demo_effects.py
"""
import csv
from pathlib import Path

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATA = Path(__file__).resolve().parents[3] / "shared-assets" / "quickcart-escalation-tickets" / "data" / "quickcart-tickets-2025.csv"
NUMERIC = ["amount", "prior_tickets_30d", "account_age_days"]
CATEGORICAL = ["tag", "channel", "language"]

with DATA.open(encoding="utf-8", newline="") as stream:
    # Strip Orange's type prefixes (C#, D#, cD#, m...) from the header; the code uses plain names.
    rows = [{key.split("#")[-1]: value for key, value in row.items()} for row in csv.DictReader(stream)]
y = np.array([row["escalated"] == "yes" for row in rows], dtype=int)
month = np.array([int(row["month"]) for row in rows])
customer = np.array([row["customer_id"] for row in rows])
tag = np.array([row["tag"] for row in rows])


def table(columns):
    return np.array([[row[name] for name in columns] for row in rows], dtype=object)


def model(kind, categorical):
    # Preprocessing lives inside the pipeline, so each fold fits it on that fold's training rows only.
    prep = ColumnTransformer([("num", StandardScaler(), list(range(len(NUMERIC)))),
                              ("cat", OneHotEncoder(handle_unknown="ignore"),
                               list(range(len(NUMERIC), len(NUMERIC) + len(categorical))))])
    estimator = {"constant": DummyClassifier(strategy="most_frequent"),
                 "tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, random_state=0),
                 "tree_no_limits": DecisionTreeClassifier(random_state=0),
                 "logistic": LogisticRegression(max_iter=2000)}[kind]
    return make_pipeline(prep, estimator)


def evaluate(categorical, splitter, groups=None):
    X = table(NUMERIC + categorical)
    out = {}
    for kind in ("constant", "tree", "tree_no_limits", "logistic"):
        proba = cross_val_predict(model(kind, categorical), X, y, cv=splitter, groups=groups, method="predict_proba")[:, 1]
        predicted = (proba >= 0.5).astype(int)
        out[kind] = {"accuracy": accuracy_score(y, predicted), "recall": recall_score(y, predicted, zero_division=0),
                     "auc": roc_auc_score(y, proba)}
    return out


def show(title, results):
    print(f"\n{title}")
    for kind, metrics in results.items():
        print(f"  {kind:15} accuracy {metrics['accuracy']:.3f}  recall {metrics['recall']:.3f}  AUC {metrics['auc']:.3f}")


random_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
honest = evaluate(CATEGORICAL, random_cv)
show("Random 5-fold CV, honest features", honest)

# Experiment 1: memorizing versus generalizing.
X_honest = table(NUMERIC + CATEGORICAL)
train_accuracy = model("tree_no_limits", CATEGORICAL).fit(X_honest, y).score(X_honest, y)
print(f"\nUnlimited tree accuracy on its own training data: {train_accuracy:.3f}")
assert train_accuracy == 1.0, "Unlimited tree should memorize its training data"
assert honest["tree_no_limits"]["accuracy"] < honest["constant"]["accuracy"], "Unlimited tree should fall below the baseline"
assert abs(honest["logistic"]["accuracy"] - honest["constant"]["accuracy"]) < 0.015, "Logistic accuracy should tie the baseline"
# The demo's point: accuracy ties the baseline while ranking quality (AUC) shows real signal.
# Which tree ranks how well depends on the tree settings, so only claims that hold for any tree are checked.
assert honest["logistic"]["auc"] > 0.75, "Logistic regression should rank escalations well above chance"
assert honest["logistic"]["auc"] > honest["tree_no_limits"]["auc"] + 0.1, "Memorizing should hurt ranking quality"

# Experiment 3a: target leakage.
leaky = evaluate(CATEGORICAL + ["assigned_queue"], random_cv)
show("Random 5-fold CV, with the leaky assigned_queue", leaky)
assert leaky["logistic"]["recall"] > 0.9 > honest["logistic"]["recall"] + 0.5, "The leak should transform recall"
names = NUMERIC + CATEGORICAL + ["assigned_queue"]
encoded = np.column_stack([table(NUMERIC).astype(float),
                           OrdinalEncoder().fit_transform(table(CATEGORICAL + ["assigned_queue"]))])
information = dict(zip(names, mutual_info_classif(encoded, y, discrete_features=[False] * 3 + [True] * 4, random_state=0)))
print("\nMutual information:", {name: round(value, 3) for name, value in sorted(information.items(), key=lambda item: -item[1])})
others = max(value for name, value in information.items() if name != "assigned_queue")
# Exact ratios depend on the scoring method (Orange's Rank uses different estimators); "several times" holds for both.
assert information["assigned_queue"] > 5 * others, "The leaky field should dominate any feature ranking"

# Experiment 3b: group leakage.
grouped = evaluate(CATEGORICAL, StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0), groups=customer)
show("Customer-grouped 5-fold CV, honest features", grouped)
# Group leakage helps only models able to memorize small groups; a tree needing 20 tickets per leaf barely moves.
assert grouped["tree_no_limits"]["recall"] < 0.8 * honest["tree_no_limits"]["recall"],     "The memorizing tree's recall should drop once customers stay together"
assert abs(grouped["logistic"]["recall"] - honest["logistic"]["recall"]) < 0.03, "Logistic regression should barely move"

# Experiment 3c: temporal leakage and the 1 October returns policy.
train, test = month <= 8, month >= 11
returns_after = test & (tag == "returns")
rate = y[returns_after].mean()
print(f"\nNov-Dec returns tickets: {returns_after.sum()}, escalated {y[returns_after].sum()} ({rate:.1%})")
assert rate > 0.25 > y[train & (tag == "returns")].mean() * 3, "Returns escalation should jump after the policy change"
for kind in ("tree", "tree_no_limits", "logistic"):
    fitted = model(kind, CATEGORICAL).fit(X_honest[train], y[train])
    recall = recall_score(y[returns_after], fitted.predict(X_honest[returns_after]), zero_division=0)
    print(f"  {kind:15} recall on post-policy returns: {recall:.3f}")
    assert recall < 0.2, f"{kind} trained on Jan-Aug should miss most post-policy returns escalations"

print("\nAll demo effects present.")
