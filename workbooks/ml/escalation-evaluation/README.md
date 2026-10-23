# W-ML-EVAL-01 — Evaluate an escalation model honestly, then decide under a changed requirement

**Is this model better than what QuickCart does today, and does it meet the requirement that just changed?** This workbook turns the ML guides' evaluation ideas into a report you can inspect and a decision you can defend.

> **Your goal:** Compare a real model with simple alternatives without hiding leakage, groups where it fails or the limits of how many flags people can review.<br>
> **You need:** The Python bridge, plus [SG-ML-00](../../../study-guides/ml-foundations/docs/00-learning-from-examples.md) and [SG-ML-01](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md).<br>
> **Effort:** 20 minutes reading, 60 minutes guided, 45 minutes on your own and 60 minutes for analysis and your decision (estimates).<br>
> **You will produce:** A tested slice function, your validation and test reports, and a decision note that always says "out of how many".

<details>
<summary>Reference: unit metadata, tested versions and historical checks</summary>

> **Unit ID:** W-ML-EVAL-01 · **Capability:** AI-ML-01 · **Classification:** Required evidence for AI-ML-01<br>
> **Audience:** Experienced backend engineers who have finished the [Python bridge](../../python/README.md) and read [SG-ML-00](../../../study-guides/ml-foundations/docs/00-learning-from-examples.md) and [SG-ML-01](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md)<br>
> **Central question:** Is this model better than what QuickCart does today, for whom, and is it good enough for a requirement that just changed?<br>
> **Effort:** Reading 20 min; guided evaluation 60 min; independent slice exercise 45 min; error analysis and decision note 60 min. Editorial estimates, not pilot timings<br>
> **Artifact:** A completed slice function that passes its check, the validation and test reports, and a decision note with denominators<br>
> **Status:** Draft. 14 reference tests, the exercise check and both fault drills author-verified offline; no learner pilot<br>
> **Environment:** Windows PowerShell, uv 0.8.3, Python 3.11.13; scikit-learn 1.9.1, pandas 3.0.6, NumPy 2.4.6 (exact versions in `uv.lock`); synthetic data; no network, model provider or paid service

</details>

**QuickCart** is our fictional online shop. Its support team wants to flag tickets that are likely to need a supervisor. A supplied logistic-regression model gives each ticket a score based on its features. Your job is to **find out whether this model deserves to ship**. You will:

- compare it with two baselines;
- choose a threshold on validation under review capacity;
- score the test set exactly once;
- break the evaluation on purpose, twice;
- look for where it fails;
- decide, with numbers, what to do when Operations changes the requirement.

**Intuition:** treat this like a performance review before releasing a service. You compare it with the current version (the baselines), you check it in a staging environment you never tune against (the test set), and you look at the slowest endpoints, not just the average (slices). The comparison has a limit: a load test measures the system you built, but a model evaluation also measures the *data*, and data from before a policy change can quietly stop describing the world the model is about to face.

This is what most ML work in a backend team looks like: evaluation, error analysis and a decision you can defend, rather than designing models. You will use the standard tools: **scikit-learn** pipelines and **pandas**.

## Starting state

Work on a branch of your clone of the course repository. The dataset lives in [`shared-assets/quickcart-escalation-tickets`](../../../shared-assets/quickcart-escalation-tickets/README.md), and the code finds it by its repository-relative path. If you copy this folder elsewhere, set `QUICKCART_TICKETS_CSV` to the CSV's full path.

| Path | Role |
|---|---|
| `src/escalation_eval/data.py` | Loads and validates the dataset contract; time split (train months 1–8, validation 9–10, test 11–12); guards against forbidden features and leaky splits |
| `src/escalation_eval/metrics.py` | `Counts` and `Rate`: every percentage keeps its numerator, denominator and Wilson 95% interval; 0/0 stays "n/a" |
| `src/escalation_eval/models.py` | Constant and rule baselines; a scikit-learn `Pipeline` (scaling + one-hot encoding + `LogisticRegression`) |
| `src/escalation_eval/thresholds.py` | Lowest-cost threshold within review capacity |
| `src/escalation_eval/report.py` | `--stage validation` (repeatable) and `--stage test` (once, with the frozen threshold) |
| `tests/test_reference.py` | 14 tests of the reference behavior |
| `exercises/` | Your slice exercise, its check, the inspectable reference, a slice runner and the decision-note template |

## Setup and verify

**Before you run anything:** the author's checks used Windows PowerShell, uv 0.8.3 and Python 3.11.13, with scikit-learn 1.9.1, pandas 3.0.6 and NumPy 2.4.6 pinned in `uv.lock`. The sync may download packages. Everything runs on local, made-up data: no model provider, no paid calls and no server. Reports are written to `results/`; keep your decision evidence before you clean up.

From `workbooks/ml/escalation-evaluation` in your clone:

```powershell
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
```

**Expected:** `Ran 14 tests ... OK`. `--locked` stops setup if the lockfile is out of date, so you get exactly the versions the author used.

## Step 1 — Predict, then run the validation report

Write your answers down first. Validation is September–October: 2,000 tickets, 219 escalated (10.9%).
1. What accuracy does "always no" score?
2. Today's rule flags tickets with amount ≥ 500 or a `chargeback` tag. What fraction of escalations will it catch?
3. The model at the conventional 0.5 threshold: many flags, or few?

```powershell
uv run python -m escalation_eval.report --stage validation
```

**Observed (author run, 2026-10-14):**

| On validation | Flags | Precision | Recall | Cost (min) |
|---|---|---|---|---|
| Constant (always no) | 0 / 2,000 | n/a (0/0) | 0.0% (0/219) | 8,760 |
| Rule | 126 / 2,000 | 43.7% (55/126) | 25.1% (55/219) | 6,844 |
| Logistic regression @ 0.5 | 34 / 2,000 | 73.5% (25/34) | 11.4% (25/219) | 7,796 |
| Logistic regression @ 0.164, chosen | 193 / 2,000 | 44.0% (85/193) | 38.8% (85/219) | 5,792 |

Costs use SG-ML-01's hypothetical figures: a missed escalation costs 40 minutes, a false alarm 4 minutes, and capacity is 10% of tickets (200 flags).

<details><summary>What to notice</summary>

- "Always no" is 89.0% accurate and catches nothing. Accuracy is printed, but do not decide with it.
- At 0.5 the model is *precise* but timid: it flags 34 tickets and catches 25 escalations, **worse than the rule** on recall and cost. A rare class needs a lower threshold.
- `choose_threshold` tries every distinct score, discards options above 200 flags, and keeps the cheapest: 0.164, which catches 85 escalations against the rule's 55 at similar precision.
- Each Wilson interval shows how far a number might move. Recall 38.8% (85/219) has a 95% interval of about 33%–45%.

</details>

The run writes `results/frozen.json`, which records the threshold, capacity, costs, features and a fingerprint of the dataset. You can rerun validation as often as you like.

> [!IMPORTANT]
> Freeze the candidate before consulting test results. Validation can guide changes; a test result already inspected cannot become fresh evidence by deleting its report or rerunning a command.

## Step 2 — Score the test set once

```powershell
uv run python -m escalation_eval.report --stage test
```

**Observed:** test is November–December, with 2,000 tickets and 231 escalated (11.6%). At the frozen threshold, the model flags 191, with precision **35.1% (67/191)** and recall **29.0% (67/231)**. The rule catches 45/231 (19.5%). Cost is 7,056 minutes for the model against 7,820 for the rule.

Test recall is about ten points lower than on validation. The model still beats the rule, but by less; keep that in mind for Step 5.

Once a test report exists, the tool refuses to score the test set again with a *changed* frozen configuration, but it will replay the same configuration. A replay is not a new, independent evaluation. If what you see changes the model or its features, you need a later period of data that nobody has looked at for the next release estimate. The guard only compares the recorded configuration, not every possible code change, so it cannot keep the evaluation honest on its own; that is your job.

## Step 3 — Break the evaluation on purpose

These drills edit `src/escalation_eval/data.py` and `models.py`. Record your starting state and make them on your working branch. Afterwards, reverse only the deliberate fault edits; a blanket restore can discard your own unfinished work. Keep the original test report and decision evidence separate from these validation-only experiments.

**Drill A: the leaky field.** In `data.py`, add `"assigned_queue"` to `CATEGORICAL`. Run the validation report.
- **Observed:** it stops with `DataContractError: Forbidden model inputs: ['assigned_queue']`.
- Now, in `models.py`, comment out `check_features(features)` in `build_logistic` and run again. The report "succeeds": recall at the chosen threshold jumps to **87.2% (191/219)**, with precision 95.5%.
- Run the tests: `test_forbidden_features_are_refused` and the capacity test fail.
- **Diagnose:** a near-perfect result from one new field means the field knows the answer. `assigned_queue` is written after a supervisor accepts an escalation.
- **Repair:** restore both files and rerun the tests.

**Drill B: the random split.** In `time_split`, replace the month filters with a shuffled split (`frame.sample(frac=1, random_state=0)` sliced into 8,000 / 2,000 / 2,000 rows).
- **Observed:** `DataContractError: Splits overlap in time or are out of order`.
- **Diagnose:** a random split puts December tickets in training to "predict" November, and scatters repeat customers across splits.
- **Repair:** restore the time split.

Record each failure and the passing rerun. These are explicit data-contract checks backed by tests, which is why leakage checks belong in CI.

## Step 4 — Independent: slice the results

Averages hide failing groups. Implement `slice_table` in `exercises/slices.py`. For each value of a column, it returns tickets, escalations, caught, flags, recall and precision as `Rate` objects, and a `small` flag when there are fewer than `min_positives` escalations. The docstring and TODOs give the full contract. Write one or two checks of your own first, then run:

```powershell
uv run python exercises/check_slices.py
uv run python exercises/run_slices.py --by tag
uv run python exercises/run_slices.py --by language
uv run python exercises/run_slices.py --by tag --split test
```

**Expected:** the check prints `slices: slice checks passed...`. On the untouched starter it stops with `NotImplementedError`. `--reference` runs the inspectable reference; consult it only after recording your attempt, and disclose it.

**Before you look, decide which slices matter and why.** Then compare with what you see.

<details><summary>What the author's run shows, and why it matters</summary>

- **Returns** recall is about 18% on both validation (9/50) and test (20/112), far below the average. On test, returns are the largest group of escalations.
- **Chargeback** recall is high (34/38 on validation), mostly because the rule-like signal is strong.
- **Language:** `other` shows 60.0% recall against 36.1% for `en`, **but on only 25 escalations** (95% interval roughly 41%–77%). The dataset was generated with *no* language effect, so this "difference" is noise. Small slices invite false stories; the `small` flag is there to stop you telling one.

</details>

## Step 5 — Error analysis on validation

Look at the individual mistakes. Do it on **validation**, never on test, because what you learn here will shape changes.

```powershell
uv run python -m escalation_eval.report --stage validation --errors 20
```

Group the missed escalations and false alarms into patterns, and fill in section 4 of the [decision-note template](exercises/decision-note-template.md). Use pandas on `load_tickets()` if you want to count patterns systematically.

<details><summary>Hint</summary>

Count misses by `tag` and `month`, and check how many missed tickets share a `customer_id`.

</details>

<details><summary>Worked reasoning</summary>

Of 134 missed escalations at the chosen threshold, the largest single group is **October returns (34)**. Returns escalated in 12 of 189 September tickets, but 38 of 154 October tickets: the 1 October policy change is visible *inside* validation, and the model, trained on January–August, has never seen it. **58 misses** come from the 40 repeat customers, whose escalation depends on a trait no feature records; no threshold will fix those without new data. The rest are low-amount tickets with few prior contacts, where the signal is weak. So the main fixable problem is not the algorithm: it is stale training data after a policy change.

</details>

## Step 6 — The requirement changes

> **From Support Operations, effective 1 November:** "After the new returns policy, at least **80% of escalating returns tickets** must reach a supervisor. Also, two supervisors are moving to the chargebacks team, so review capacity falls from 10% to **8% of tickets**."

Decide, with evidence, what to do. Use validation only. Useful commands:

```powershell
uv run python -m escalation_eval.report --stage validation --capacity 0.08
uv run python -m escalation_eval.report --stage validation --capacity 0.08 --curve tag=returns --months 10
```

The second command ranks October's returns tickets (the only month you have after the policy change) by model score, and shows how many escalations the top N flags would catch. Write section 5 of your decision note: can the requirement be met, what do you recommend, what did you reject, what do you need from Operations, and when will you re-evaluate?

**Note:** these `--capacity 0.08` runs rewrite `results/frozen.json` with a new threshold (0.195 instead of 0.164). The slice runner reads its threshold from that file, so any slice tables you produce afterwards use the 8% threshold. Label them clearly, or rerun the Step 1 command (without `--capacity`) to go back to the 10% configuration before you compare with your earlier evidence.

<details><summary>Progressive hint</summary>

80% of October's 38 returns escalations is 31. How many flags does the curve need to reach 31? October had 1,000 tickets, so how many flags does 8% capacity allow in the whole month, for *all* tags?

</details>

<details><summary>Worked reasoning (one defensible answer)</summary>

- **Arithmetic:** the curve reaches 31 of 38 only at the **top 100** October returns tickets. At 8%, October's entire capacity is **80 flags** across all tags. Meeting the returns target alone would need more than the whole budget, before a single chargeback or refund is flagged. **The requirement cannot be met by this model at this capacity.** The estimate rests on 38 escalations, so its uncertainty is wide; that is a reason for caution, not for optimism.
- **What the model can do at 8%:** on validation it catches 74/219 escalations (33.8%) with 155 flags, still better than the rule's 55/219.
- **Recommendation:** do **not** report the returns requirement as met. Release the model for flagging within 8% capacity, as an improvement over the rule. Ask Operations to choose between:
  - a separate returns-review queue, staffed outside supervisor capacity;
  - a temporary rule sending all post-policy returns over a chosen amount to that queue;
  - relaxing the 80% target until data exists.
- **Rejected:** lowering the threshold for returns only (it breaks capacity); retraining now (October is one month, with 38 post-policy escalations, too few to learn from or to evaluate).
- **Re-evaluate:** once November–December labels mature, retrain on data including the post-policy period, and evaluate on a *later* untouched period. The current test set has already been used.

A "no" on the requirement, with numbers and options, is the correct engineering output here.

</details>

## Completion evidence

- [ ] `uv run python -m unittest discover -s tests -v` passes on your restored branch.
- [ ] Both drills: failure output, diagnosis and the passing rerun.
- [ ] `exercises/check_slices.py` passes on **your** `slice_table`, plus your own checks. Disclose any use of the reference.
- [ ] Your validation report, your single test report, and the slice tables you used.
- [ ] A completed decision note (all six sections) with denominators and a justified decision under the changed requirement.

The decision note is the main evidence. For independent verification, expect to explain one number in it and to make a small, unseen change: for example, a different capacity or cost ratio, a new slice, or a different post-policy month.

## Troubleshooting

| Symptom | Likely cause | Diagnostic and repair |
|---|---|---|
| `DataContractError: Dataset not found` | The project was copied outside the repository | Work in your clone, or set `QUICKCART_TICKETS_CSV` to the shared CSV's full path. |
| `No frozen configuration` | The test stage was run before validation | Run `--stage validation` first. Thresholds are never chosen on test. |
| `The test set was already scored with a different configuration` | Frozen settings changed after scoring test | Preserve the report and record the changed candidate. Continue exploration on validation; use a later untouched period for a new release estimate. Deleting the report does not restore independence. |
| `Features or dataset changed since the configuration was frozen` | Inputs changed after validation | Rerun validation. If test was already inspected, do not present the same test period as a fresh release estimate for the changed candidate. |
| `ModuleNotFoundError: slices` | `run_slices.py` was run from a different directory | Run from `workbooks/ml/escalation-evaluation` with `uv run`. |
| Numbers differ slightly from the README | Different library versions | Use `uv sync` with the lockfile. The relative ordering and conclusions should hold. |

## Compare the solution before selecting a model

Begin the [solution-selection exercise](solution-selection.md) with your ML decision note, then finish it after LLM foundations. It adds 85-115 minutes within phase 1 and compares four approaches against one fixed QuickCart brief; capstone discovery reuses your record. Model measurements remain pending until separately performed.

## Cleanup, limits and next step

Keep your decision note, frozen configuration and reports as evidence. When finished, remove generated `results/` and `.venv` only from your own working copy after verifying their resolved paths. Do not discard the evidence needed to explain which candidate was tested. No servers, cloud resources or paid calls are involved.

**Limitations:**
- One model family, and one synthetic year whose rules you can read.
- No label delay: outcomes are known immediately.
- No live traffic or monitoring.
- Costs and capacity are hypothetical.

Real evaluations also need a fairness review across real customer groups, data governance and monitoring after release ([SG-ML-01, section 11](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md#11-production-concerns)).

**Sources:** scikit-learn: [Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html), [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html), [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html); pandas: [Group by](https://pandas.pydata.org/docs/user_guide/groupby.html). Recorded in the [source ledger](../../../docs/source-ledger.md). All data is made up.

## Stage defense practice

Use the [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p02--ml-evaluation-and-leakage) to practise coding, debugging, design and writing a short update for a stakeholder. Pick from them during this module's reflection and own-work time; you do not need to do every prompt. Note your prediction, the checks you actually ran, any help used and what your evidence cannot show. Practising with public prompts or the reference is different from the final review, where a reviewer chooses an unseen change.

## Completion checkpoint

**You can now:** compare a model with baselines and say what every number is divided by, choose a threshold on validation within review capacity, score the test set once, find a group where the model fails, and defend a release or no-release decision when the requirement changes.

**Show it:** your decision note.

**Next:** AI-LLM-01 starts with [SG-LLM-00 — How LLMs generate text](../../../study-guides/llm-foundations/docs/00-how-llms-generate-text.md), followed by [SG-LLM-01 — Designing prompts and context](../../../study-guides/llm-foundations/docs/01-designing-prompts-and-context.md), before any framework setup. Every later evaluation in the course, including of LLM outputs, reuses the habits you practised here: baselines, denominators, validation versus test, slices and a written decision.

[Previous: SG-ML-01 — Baselines, metrics and leakage](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) · [Course map](../../../README.md#ordered-capability-map)
