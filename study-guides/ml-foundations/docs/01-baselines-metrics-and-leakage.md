# Baselines, Metrics and Leakage

**A dashboard says the model is 94% accurate. Is it useful, or is the evaluation misleading?**

> **Your goal:** Compare a model with simple alternatives, always ask "out of how many?", and defend a decision to release or not.<br>
> **You need:** [SG-ML-00](00-learning-from-examples.md), especially what training, validation and test sets are for. Percentages and basic arithmetic are enough.<br>
> **Effort:** 75–90 minutes of reading (estimate).<br>
> **You will produce:** Your worked metric calculations and a written release decision for the routing challenge.

QuickCart, our fictional online shop, now needs evidence that its escalation model actually helps support staff. The question is no longer "does the model learn?" but "which mistakes matter, how many flags can people review, and can we trust the evaluation?"

**How to study this guide:** work through each calculation before opening its answer. Keep a short decision record as you go: the baseline, each number with what it was divided by, the review capacity, any requirement that failed, and your release decision. This is reading only; you need no library installs and no paid service.

<details>
<summary>Reference: unit metadata and existing verification scope</summary>

> **Unit ID:** SG-ML-01 · **Capability:** AI-ML-01 · [Course map](../../../README.md#ordered-capability-map)

> **Series status:** Draft for chapters 00–01. Conceptual material with author-checked arithmetic; no learner pilot. Apply it in the hands-on [W-ML-EVAL-01 evaluation exercise](../../../workbooks/ml/escalation-evaluation/README.md).

> **Chapter 01 · Self-study guide · Estimated study time: 75–90 minutes**
>
> **Audience:** Experienced backend engineers who have read SG-ML-00.
>
> **Prerequisites:** [SG-ML-00 — How models learn from examples](00-learning-from-examples.md).
>
> **Running example:** QuickCart's escalation model from SG-ML-00, now reported as "94% accurate".
>
> **Central question:** How do you know a reported score means the model is useful, and not that the evaluation is broken?
>
> **Outcome:** Compare a model against baselines using counts and denominators, choose a threshold under cost and capacity constraints, detect common leakage, and make a defended release or no-release decision.
>
> **Evidence:** Worked calculations, knowledge-check answers, and a written release decision for the closing challenge.

</details>

## Learning objectives

> [!TIP]
> For each reported percentage, write “out of what?” beside it. Then name the decision it supports and the group it might hide.

By the end of this chapter, you should be able to:

- Compute and interpret accuracy, precision and recall from a confusion matrix, always stating the denominator.
- Explain why a score means nothing without a baseline, and choose suitable baselines.
- Choose a decision threshold on validation data using error costs and review capacity.
- Show how an aggregate score can hide a failing slice, and how small denominators widen uncertainty.
- Recognize six forms of leakage, with a check you could automate for each.
- Write an evaluation summary that supports a release, or a justified no-release, decision.

## 1. Start with intuition: the desert forecaster

A weather forecaster in a desert says "no rain" every day and is right 95% of the time. Nobody would hire them, because the 5% they miss are the only days that matter. The 95% describes the desert, not the forecaster.

Many prediction problems look like this: the outcome you care about is rare, so a system that never predicts it still looks accurate. The analogy has a limit: a forecast does not change the weather, but a QuickCart model that routes tickets changes how agents behave, and that changes the data you collect next (SG-ML-00, section 10).

## 2. The QuickCart problem: "94% accurate"

The data-science contractor reports that the escalation model scored **94.0% accuracy** on the Nov–Dec test set of 2,000 tickets. Product wants to switch it on.

**Pause and predict:** before reading further, is 94% good? What one number would you ask for first?

<details>
<summary>Reveal the reasoning</summary>

Ask for the **base rate**: what fraction of test tickets actually escalated. It is 160 of 2,000, or 8.0%. So "always predict no" scores 1,840 of 2,000, which is **92.0%** accuracy. The model beats doing nothing by two percentage points. That may or may not be valuable; accuracy alone cannot tell you.

</details>

## 3. Baselines: the score you get for free

A baseline is the simplest sensible alternative, measured on **the same test data**. A model is only worth its cost if it beats the best baseline by enough to matter to the business.

| Baseline | QuickCart version | Why include it |
|---|---|---|
| **Majority class** | Always predict "no escalation" | Exposes imbalance; the floor any model must beat |
| **Simple rule** | Flag if amount ≥ 500 or the tag is `chargeback` | Often captures most of the value at near-zero cost |
| **Current process** | Today's manual triage, if it was recorded | The real alternative the model replaces |

A model that cannot clearly beat a simple rule should usually not ship: the rule is cheaper, faster, explainable and cannot drift. That conclusion is a successful evaluation, not a failure.

## 4. Mechanism: the confusion matrix and its denominators

![A confusion matrix of 2,000 test tickets. Actual escalated: 160; actual not escalated: 1,840. True positives 112, false alarms 72, missed escalations 48, correctly left alone 1,768. A side panel shows accuracy 94.0 percent, base rate 8.0 percent, precision 112 of 184 equals 60.9 percent, recall 112 of 160 equals 70.0 percent, and notes that always predicting no gives 92.0 percent accuracy with 0 percent recall.](../diagrams/evaluation/01-confusion-matrix.svg)

**Diagram walkthrough:** Columns are what actually happened; rows are what the model predicted. Each ticket lands in exactly one cell, so the four cells sum to 2,000. Read down a column for the denominator of **recall**: of the 160 real escalations, the model caught 112. Read across the top row for the denominator of **precision**: of the 184 tickets it flagged, 112 were real. Green cells are correct, amber cells are errors, and the two error types cost different amounts. The figure omits the score threshold that produced these predictions (section 5) and any uncertainty (section 7).

| Metric | Formula | QuickCart value | Question it answers |
|---|---|---|---|
| **Accuracy** | (TP + TN) / all | (112 + 1,768) / 2,000 = **94.0%** | How often is it right overall? Misleading when classes are imbalanced. |
| **Precision** | TP / (TP + FP) | 112 / 184 = **60.9%** | When it flags a ticket, how often is that worth a supervisor's time? |
| **Recall** | TP / (TP + FN) | 112 / 160 = **70.0%** | Of tickets that needed a supervisor, how many did it catch? |
| **F1** | 2 · P · R / (P + R) | ≈ **0.65** | One number balancing precision and recall. Convenient, but it hides which one moved. |

The precision and recall definitions follow [Google's ML Crash Course](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall), which makes the same desert-forecaster point: a model that always predicts the majority class can score very high accuracy and still be useless.

Now compare against the baselines on the same 2,000 tickets:

| | Flags | Caught (TP) | Missed (FN) | False alarms (FP) | Accuracy | Precision | Recall |
|---|---|---|---|---|---|---|---|
| Always "no" | 0 | 0 | 160 | 0 | 92.0% | n/a (0 flags) | 0.0% |
| Rule: amount ≥ 500 or `chargeback` | 132 | 72 | 88 | 60 | 92.6% | 54.5% | 45.0% |
| Model | 184 | 112 | 48 | 72 | 94.0% | 60.9% | 70.0% |

Accuracy moves only from 92.0% to 94.0%, but **recall rises from 45% to 70%**: the model catches 40 more real escalations than the rule, at the price of 52 more flags to review. Whether that is worth it is a business question, and it can be answered with numbers.

**Precision has no value when nothing is flagged.** Report "n/a (0 flags)", not 0% or 100%. This is the same denominator discipline the course applies to abstentions and coverage in LLM evaluation.

## 5. Choosing a threshold: cost and capacity

Most models output a **score** between 0 and 1, and you choose the cut-off above which a ticket is flagged. Lower thresholds catch more escalations and raise more false alarms. **Choose the threshold on validation data, never on test.**

Assume, as hypothetical planning figures, that a missed escalation costs about **40 minutes** of supervisor rework and customer recovery, and a false alarm costs about **4 minutes** of review. Supervisors can review at most **200 flags per 2,000 tickets**. On the Sep–Oct validation set (2,000 tickets, 150 escalations):

| Threshold | Flags | Caught of 150 | Precision | Recall | Cost: FN × 40 + FP × 4 (minutes) | Within 200-flag capacity? |
|---|---|---|---|---|---|---|
| 0.3 | 260 | 120 | 46.2% | 80.0% | 30 × 40 + 140 × 4 = **1,760** | No |
| 0.5 | 170 | 105 | 61.8% | 70.0% | 45 × 40 + 65 × 4 = **2,060** | Yes |
| 0.7 | 90 | 66 | 73.3% | 44.0% | 84 × 40 + 24 × 4 = **3,456** | Yes |

<details>
<summary>Reveal the decision and reasoning</summary>

Threshold 0.3 has the lowest cost but needs 260 reviews when supervisors can do 200. Flags beyond capacity are not reviewed, so the cost estimate would be fiction. **Choose 0.5:** the lowest-cost option that fits capacity. Revisit the choice if review capacity grows. The test-set results in section 4 were produced at this frozen threshold, which is why the test is legitimate.

For comparison on the test set: the model at 0.5 costs 48 × 40 + 72 × 4 = **2,208** minutes, the rule 88 × 40 + 60 × 4 = **3,760**, and always-no 160 × 40 = **6,400**. Under these assumptions the model saves about 1,550 minutes per 2,000 tickets compared with the rule. If the cost assumptions change, the decision may change too; state them.

</details>

## 6. Slices: averages hide failures

QuickCart receives tickets in several languages. Split the same test results by language:

| Slice | Real escalations | Caught | Recall | Flags | Precision |
|---|---|---|---|---|---|
| English | 120 | 94 | 78.3% | 140 | 67.1% |
| Other languages | 40 | 18 | **45.0%** | 44 | 40.9% |
| **All** | 160 | 112 | 70.0% | 184 | 60.9% |

The overall 70% recall is a weighted average of a 78% slice and a 45% slice. Customers writing in other languages get escalation help at roughly the rule's level, while the headline number suggests otherwise. Decide the important slices **before** looking at results: language, customer tier, ticket channel, new versus returning customers. Then report each with its counts.

## 7. Small denominators and uncertainty

A percentage computed from few examples is noisy. A rough 95% range for a proportion `p` measured on `n` examples is `p ± 1.96 × √(p(1 − p) / n)`. This normal approximation is crude for small `n` or extreme `p`; use a proper binomial interval such as Wilson's when it matters.

| Measurement | p | n | Approximate 95% range |
|---|---|---|---|
| Overall recall | 70.0% | 160 escalations | about 63% to 77% |
| Other-language recall | 45.0% | 40 escalations | about 30% to 60% |

The denominator for recall is the number of **real escalations**, not 2,000 tickets. A slice with 40 positives cannot distinguish 45% from 55% recall. Report counts beside percentages, and do not celebrate a two-point improvement measured on 40 cases.

## 8. Leakage: when the evaluation sees what production will not

Leakage happens when the model or the evaluation gets information that will not exist at the moment of a real prediction. Scores look better than they really are, sometimes dramatically, and the model then does worse in production. scikit-learn's guide describes it as using "information that would not be available at prediction time" when building the model, producing "overly optimistic performance estimates" ([scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)).

![Six pipeline stages in two rows: collect and label, split, fit preprocessing, then train, tune on validation, test once. Amber notes mark leaks: a field set after the outcome; one customer in two splits; later months in training; statistics fit on all rows; tuning against the test set; test cases reused in prompts or examples. A footer lists automatable checks.](../diagrams/evaluation/02-leakage-points.svg)

**Diagram walkthrough:** Follow the arrows in the order work happens: collect and label, split, fit preprocessing, then train, tune and test. Each amber note marks where outside information can enter. Training (stage 4) has no leak of its own; it faithfully learns whatever leaked into steps 1–3. The invariant is that every value the model or the evaluation uses must have been knowable, for that ticket, at prediction time, and that the test set influences no decision. The footer turns each leak into a check you can automate. Leaks in monitoring and live feature pipelines are omitted here.

| Leak | QuickCart example | Symptom | Check you can automate |
|---|---|---|---|
| **L1 Target leakage** | `assigned_queue` is set when a supervisor accepts an escalation | Suspiciously high scores; one feature dominates | Each feature's "known at" timestamp ≤ the ticket's prediction time; live values are not all null |
| **L2 Group leakage** | One customer's six near-identical tickets split across training and test | Random-split scores well above grouped-split scores | No customer ID appears in more than one split |
| **L3 Temporal leakage** | Random split puts December tickets in training to predict November | Scores fall when you switch to a time split | Maximum training timestamp < minimum validation timestamp |
| **L4 Preprocessing leakage** | Text vocabulary or average amount computed over all 12,000 tickets | Usually small inflation; invalid by construction | Preprocessing is fitted inside the training pipeline only |
| **L5 Selection leakage** | Trying feature sets until the test score improves | Test score drifts upward across iterations | Test-set access is logged; one scoring per frozen candidate |
| **L6 Evaluation contamination** | Test tickets pasted into an LLM prompt's examples, or a public benchmark the hosted model has seen | Unusually good results on exactly those cases | Evaluation cases are versioned and never used as examples; prefer fresh private cases |

**Preprocessing leakage is easy to underestimate.** scikit-learn's guide shows a striking case: selecting features using all the data before splitting produced about 0.76 accuracy on data that was pure random noise, where the honest answer is about 0.5. Fitting the same steps on the training split only removed the illusion.

### Worked diagnosis: the 99% model

After adding `assigned_queue`, validation recall jumps from 70% to 97% and precision to 95%. **Pause and predict:** is this a breakthrough?

<details>
<summary>Reveal the diagnosis</summary>

Treat a sudden jump as a bug until proven otherwise.

1. **Which feature drives it?** Feature-importance output shows `assigned_queue` dominating.
2. **When is it known?** Tracing the write path shows the routing service sets `assigned_queue = supervisors` *after* a supervisor accepts the escalation. It is nearly a copy of the label.
3. **What does live traffic contain?** In a shadow run on new tickets, the field is null for 100% of them.
4. **Repair and regression check:** remove the feature, add the timestamp assertion to the training pipeline so the field cannot return, and re-validate. Recall returns to about 70%.

The 97% was never a model property; it measured a database field. Its write timing was the clue, which is why backend engineers are often the ones who find leaks.

</details>

### Leakage checks as ordinary tests

Leak checks are assertions over data, and they belong in the same CI as your other tests. Conceptual sketch, not a complete implementation:

```text
assert max(train.created_at) < min(validation.created_at) < min(test.created_at)
assert customers(train) ∩ customers(test) == ∅
for feature in model.features:
    assert feature.known_at(ticket) <= ticket.prediction_time   # per ticket, from lineage metadata
assert preprocessing.fitted_on == "train"
assert test_set.version == frozen_release.test_set_version and test_set.scored_count == 1
```

Omitted: how lineage timestamps are recorded, near-duplicate detection for text, and access control on the test set. Each needs real engineering.

## 9. Choosing metrics for the decision

| Situation | Prefer | Avoid |
|---|---|---|
| Rare positives, misses are costly (escalation, fraud) | Recall at a fixed review capacity, precision, cost per 1,000 tickets | Accuracy alone |
| Flags trigger expensive or irreversible action | Precision; human approval for the action | Optimizing recall alone |
| Several classes (W-PY-API-01's four triage categories) | Per-class recall and precision, plus the confusion between important pairs | One overall accuracy |
| Scores are shown to people as confidence | A calibration check: do "0.8" tickets escalate about 80% of the time? | Presenting raw scores as probabilities without checking |
| Any production model | Latency, failure rate and cost per prediction, beside the quality metrics | Quality metrics alone |

Whatever you choose, **state the denominator**, include abstentions and failures in it, and report the baseline beside the model.

## 10. Design boundaries and misconceptions

| Misconception | Correction |
|---|---|
| "94% accuracy is excellent." | Compare with the base rate: always-no scores 92%. |
| "Higher F1 always means a better model." | F1 weighs precision and recall equally; your costs usually do not. |
| "We picked the threshold that looked best on test." | That turns the test set into validation. Pick on validation; score the test once. |
| "A big jump after adding a feature is good news." | Suspect leakage first; check when the feature becomes known. |
| "The overall metric covers everyone." | Report pre-chosen slices with counts; averages hide failing groups. |
| "No release means the project failed." | A defended no-release, or "use the rule", is a correct engineering outcome. |

## 11. Production concerns

- **Labels arrive late.** Escalation is known within days, but some outcomes take weeks, so live quality is always measured on a delay. Monitor input distributions and flag rates in the meantime; a sudden change in either is your early warning.
- **Drift:** new products, policies or customer segments change the data. Re-evaluate on recent periods on a schedule, not only when someone complains.
- **Versioning:** a result is reproducible only if you can name the data snapshot, split definition, feature code, model artifact, threshold and evaluation set. The [capstone evidence brief](../../../assessments/capstone-evidence.md) requires the same for LLM applications.
- **Security and privacy:** evaluation sets are copies of production data. Restrict access, define retention, and prefer synthetic or redacted cases for anything shared.
- **Ownership:** someone must own the evaluation set and the release decision, and be accountable for the slices that matter.

A minimal evaluation summary, as a conceptual contract:

```json
{
  "model": "escalation-2027-01-a",
  "data_snapshot": "tickets-2026-12-31",
  "split": {"train": "Jan-Aug", "validation": "Sep-Oct", "test": "Nov-Dec", "grouped_by": "customer_id"},
  "test_counts": {"tickets": 2000, "escalated": 160},
  "threshold": {"value": 0.5, "chosen_on": "validation", "constraint": "<= 200 flags per 2000"},
  "test_results": {"tp": 112, "fp": 72, "fn": 48, "tn": 1768},
  "baselines": {"always_no_recall": 0.0, "rule_recall": 0.45},
  "slices": {"other_languages": {"escalated": 40, "caught": 18}},
  "leakage_checks": ["time_order", "customer_disjoint", "feature_known_at", "train_only_preprocessing"],
  "decision": "release as suggestion only; other-language slice routed to the existing manual queue",
  "owner": "support-platform team"
}
```

## 12. Knowledge checks

**1.** A model flags 50 of 1,000 tickets; 30 flags are real escalations, and 60 tickets escalated in total. Compute precision, recall and accuracy.

<details>
<summary>Show answer and explanation</summary>

TP = 30, FP = 20, FN = 30, TN = 1,000 − 30 − 20 − 30 = 920. Precision = 30 / 50 = **60%**. Recall = 30 / 60 = **50%**. Accuracy = (30 + 920) / 1,000 = **95.0%**. Always-no would score 940 / 1,000 = 94.0%, so the accuracy gain looks tiny even though the model catches half the escalations.

</details>

**2.** Your random-split recall is 84%; the same model with a customer-grouped split scores 70%. Which number do you report, and what does the gap suggest?

<details>
<summary>Show answer and explanation</summary>

Report 70%. Live traffic includes new customers, and the grouped split imitates that. The 14-point gap suggests the model partly recognizes repeat customers' wording, which is group leakage (L2) in the random split.

</details>

**3.** A slice has 25 real escalations and recall 60%. Roughly how wide is the uncertainty, and what would you tell a product manager?

<details>
<summary>Show answer and explanation</summary>

`1.96 × √(0.6 × 0.4 / 25) ≈ 0.19`, so roughly 41% to 79%. Tell them the slice is too small to judge precisely. Either collect more labelled cases from that slice, or treat it conservatively, for example by keeping it on the manual route, until you have them.

</details>

**4.** An LLM triage prompt scores 98% on your 50-case evaluation set. You built the prompt's examples by copying the 10 hardest cases from that set. What is wrong?

<details>
<summary>Show answer and explanation</summary>

Evaluation contamination (L6): the prompt was fitted to 10 of the 50 cases, so the score is inflated by an unknown amount. Remove those cases from evaluation, or better, build a fresh held-out set and keep the original as a development set.

</details>

## 13. Design challenge: ship the triage classifier?

QuickCart wants to auto-route tickets into four queues using a classifier like the one behind W-PY-API-01's triage endpoint. Misrouting a **returns** ticket to **billing** delays the customer's refund by about two days. Policy requires returns recall of at least 85% before any automatic routing. Results on 1,000 held-out tickets, scored once at a threshold chosen on validation:

| Actual class | Tickets | Correctly routed | Recall |
|---|---|---|---|
| billing | 300 | 270 | 90.0% |
| shipping | 400 | 372 | 93.0% |
| returns | 200 | 150 | 75.0% |
| other | 100 | 60 | 60.0% |
| **All** | 1,000 | 852 | 85.2% accuracy |

Baselines: always "shipping" scores 40.0% accuracy; the current keyword router scores 78.0%. Of the 50 misrouted returns tickets, 40 went to billing.

**Your tasks:**

1. Decide: release automatic routing, release partially, or do not release. Justify it with the numbers.
2. Name the evidence you would need to change your decision.
3. State one metric you would monitor after any release, with its denominator.

<details>
<summary>Show one reasonable solution</summary>

1. **Do not release automatic routing on this evidence.** Overall accuracy (85.2%) beats both baselines, but returns recall of 75% (150 of 200) fails the explicit 85% policy gate, and 40 of 200 returns tickets would suffer a refund delay. A high overall score cannot compensate for a failed critical requirement. Routing only predictions labelled billing or shipping does not resolve the failure: those 40 returns tickets are predicted as billing and would still be automated. Keep suggestions under human review. Consider a partial automatic route only after its separately defined scope meets the applicable policy gate on fresh evidence; the current table does not establish that.
2. Returns recall of at least 85% on a fresh held-out set, scored once, with a range that clears the gate. With 200 returns tickets, a measured 85% has a range of roughly ±5 points, so you would want a measurement comfortably above 85%. Also a check that the improvement is not leakage, and per-slice results by language.
3. Weekly rate of returns tickets later moved from billing, divided by returns tickets created that week. It needs a label from agents' manual reroutes, and it arrives with a delay.

</details>

## 14. Revision and transition

| Question | Short answer |
|---|---|
| First number to ask for? | The base rate, then the best baseline on the same data. |
| Precision versus recall? | Precision: of the flags, how many were real. Recall: of the real cases, how many were flagged. |
| Where is the threshold chosen? | On validation, using costs and review capacity; the test is scored once. |
| Why report counts? | Percentages over small denominators are noisy and can hide failing slices. |
| What is leakage? | Information unavailable at prediction time reaching the model or the evaluation. |
| Is "do not ship" a valid result? | Yes, when the evidence shows a gate is not met or a rule is as good. |

**Reflect before moving on:** think of a dashboard number you trust at work, such as an error rate, conversion rate or SLO. What is its denominator? Which slice could be failing inside it, and what would change in your decision if you saw that slice separately? Write two or three sentences; you will apply the same questions to every LLM evaluation later in the course.

**Glossary:** *base rate, baseline, confusion matrix, true/false positive, true/false negative, precision, recall, F1, threshold, slice, confidence range, target leakage, group leakage, temporal leakage, preprocessing leakage, selection leakage, evaluation contamination, calibration, drift.* Each is defined in sections 3–9 above.

**Sources:** [Google ML Crash Course — Accuracy, recall, precision](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall); [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) (data leakage, including the feature-selection example); deep dive: S. Kaufman, S. Rosset, C. Perlich and O. Stitelman, "Leakage in Data Mining: Formulation, Detection, and Avoidance", *ACM Transactions on Knowledge Discovery from Data* 6(4), 2012, [doi:10.1145/2382577.2382579](https://doi.org/10.1145/2382577.2382579). Records are in the [source ledger](../../../docs/source-ledger.md). All QuickCart figures are made up and calculated by the author.

## Completion checkpoint

**You can now:** choose a baseline, read precision and recall together with what they are divided by, pick a threshold that fits review capacity, and name the leakage checks you would automate.

**Show it:** your answer to the section 13 design challenge.

**Next:** do the hands-on [W-ML-EVAL-01 evaluation exercise](../../../workbooks/ml/escalation-evaluation/README.md) in scikit-learn: baselines, a threshold limited by review capacity, a single held-out evaluation, slices, error analysis and a decision when a requirement changes. *Optional classroom demo:* the no-code [W-ML-ORANGE-01 Orange demo](../../../workbooks/ml/orange-experiments/README.md) shows the same effects without code. After the exercise, the course map continues with [SG-LLM-00 — How LLMs generate text](../../llm-foundations/docs/00-how-llms-generate-text.md).

[Previous: SG-ML-00 — How models learn from examples](00-learning-from-examples.md) · [Course map](../../../README.md#ordered-capability-map)
