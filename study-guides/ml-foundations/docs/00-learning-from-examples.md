# How Models Learn from Examples

**A model fits historical tickets perfectly. What would convince you it will work on next week's tickets?**

> **Your goal:** Explain how a model learns and why it may fail on new data, then design an honest way to split your data for testing.<br>
> **You need:** The [Python route](../../../workbooks/python/README.md) and everyday backend ideas about how data flows. No machine-learning or statistics background; comfort with percentages is enough.<br>
> **Effort:** 60–75 minutes of reading (estimate).<br>
> **You will produce:** Your answers to the prediction questions and a written split plan for the refund-abuse challenge.

QuickCart is the fictional online shop used across the course. Its support team wants to spot new tickets that are likely to need a supervisor, using past tickets where the outcome is already known. All the numbers here are made up.

**How to study this guide:** read sections 1–4 to see how learning works, then sections 5–7 on choosing inputs and splitting data, and finish with the knowledge checks and the closing challenge. You need no Python, no account and no paid service to read it.

<details>
<summary>Reference: unit metadata and existing verification scope</summary>

> **Unit ID:** SG-ML-00 · **Capability:** AI-ML-01 · [Course map](../../../README.md#ordered-capability-map)

> **Series status:** Draft for chapters 00–01. Conceptual material with author-checked arithmetic; no learner pilot. This guide contains no executable project. An optional no-code [Orange live demo](../../../workbooks/ml/orange-experiments/README.md) follows chapter 01; the hands-on [W-ML-EVAL-01 evaluation exercise](../../../workbooks/ml/escalation-evaluation/README.md) applies both chapters with scikit-learn.

> **Chapter 00 · Self-study guide · Estimated study time: 60–75 minutes**
>
> **Audience:** Experienced backend engineers with no machine-learning or statistics background. Comfort with percentages is enough.
>
> **Prerequisites:** [AI-PY-01 Python route](../../../workbooks/python/README.md). The [W-PY-API-01 triage endpoint](../../../workbooks/python/quickcart-api/README.md) is useful context but not required.
>
> **Running example:** QuickCart, a fictional online shop, wants to predict which new support tickets will need a supervisor.
>
> **Central question:** A model scores well on the tickets it learned from. What evidence would show it will work on next week's tickets?
>
> **Outcome:** Explain learning, features, generalization and overfitting, and design a training/validation/test split for a QuickCart prediction task.
>
> **Evidence:** Your answers to the prediction prompts and knowledge checks, plus a written split design for the closing challenge.

</details>

## Learning objectives

By the end of this chapter, you should be able to:

- Explain, without equations, what it means for a model to "learn" parameters from labelled examples.
- Decide whether a candidate feature is available at prediction time, and explain why that matters.
- Distinguish fitting the training data from generalizing to new data, and recognize overfitting from a training/validation gap.
- Assign distinct jobs to training, validation and test data, and explain why the test set is used once.
- Choose between random, time-based and grouped splits for a stated use.
- Name situations where a plain rule is a better engineering choice than a learned model.

## 1. Start with intuition: the apprentice agent

A new support agent spends a week reading a thousand old tickets and noting which ones a supervisor eventually took over. By Friday they have a sense of the pattern: large refunds, angry repeat contacts and chargeback threats tend to escalate. On Monday they start flagging new tickets.

That is the core of supervised machine learning: **learn a mapping from examples whose outcome is already known, then apply it to examples whose outcome is not yet known.**

The analogy breaks in three useful places:

- The apprentice understands refund policy. A model understands nothing; it only finds patterns in the recorded fields that happened to go along with the outcome.
- The apprentice can ask why a ticket escalated. A model sees only the columns you give it, including any that are mistakes or that quietly reveal the answer.
- If the apprentice memorizes ticket numbers instead of patterns, a supervisor would notice in a day. A model that memorizes can look *perfect* on the tickets it studied. Spotting that is most of this chapter.

## 2. The QuickCart problem

QuickCart's support team handles about 2,000 tickets a week. Roughly 8% end up escalated to a supervisor, usually after an agent has already spent time on them. The product team asks: *can we flag likely escalations when the ticket arrives, so the right person sees them first?*

The team has 12,000 historical tickets from last year. Each has the ticket's fields at creation time and a recorded outcome, escalated or not. All the numbers in this chapter are synthetic.

**Why this is your problem as a backend engineer:** you will own the pipeline that extracts the training data, the API that computes features for each live ticket, and the evaluation that decides whether the model ships. Most real ML failures look like data-handling bugs: a field read at the wrong time, a join that copies rows, or two code paths that compute "the same" value differently. Those are exactly the failures backend engineers are trained to find.

## 3. Vocabulary, tied to consequences

| Term | Plain meaning | QuickCart consequence |
|---|---|---|
| **Example** | One record the model learns from or predicts for | One ticket |
| **Label** (target) | The known outcome for a training example | `escalated = yes/no`, recorded when the ticket closed |
| **Feature** | An input value the model may use | Refund amount, tags, number of tickets from this customer in the last 30 days |
| **Model** | A function from features to a prediction, with adjustable parameters | "Flag if amount ≥ T," or a far larger function |
| **Parameter** | A number the training process chooses | The threshold `T` |
| **Training** | Searching for parameter values that make predictions match the labels | Trying thresholds and keeping the one with the fewest mistakes |
| **Inference** (prediction) | Running the trained model on a new example | Scoring a ticket inside the ticket-creation API call |
| **Generalization** | Performing well on examples not used for training | Working on next week's tickets, not only last year's |

## 4. Mechanism: learning, in miniature

Real models tune thousands to billions of parameters automatically, but the idea behind it fits in a table. Take a one-parameter model: **flag a ticket if its refund amount is at least `T`**. Here are ten training tickets, sorted by amount (synthetic units):

| Amount | 5 | 12 | 20 | 35 | 45 | 60 | 80 | 150 | 220 | 400 |
|---|---|---|---|---|---|---|---|---|---|---|
| Escalated? | no | no | no | no | no | **yes** | no | **yes** | **yes** | **yes** |

**Pause and predict:** which threshold makes the fewest mistakes on these ten tickets?

Training means trying candidate values and counting errors:

| Threshold `T` | Flagged | Mistakes on training tickets |
|---|---|---|
| 0 (flag everything) | all 10 | 6 false alarms |
| 50 | 60, 80, 150, 220, 400 | 1 (80 is a false alarm) |
| 70 | 80, 150, 220, 400 | 2 (80 false alarm, 60 missed) |
| 100 | 150, 220, 400 | 1 (60 missed) |
| 500 (flag nothing) | none | 4 missed |

<details>
<summary>Reveal the reasoning</summary>

`T = 50` and `T = 100` tie with one mistake each. **The training data cannot choose between them.** You need either more data or a different kind of evidence: unseen tickets, or knowledge that a missed escalation costs more than a false alarm. Chapter 01 makes that cost argument with numbers.

</details>

Now consider a "model" that simply memorizes: *flag exactly the amounts 60, 150, 220 and 400*. It makes **zero** training mistakes. It is also useless: next week's refunds will be 55 or 90, never exactly 60.

Five new tickets the model never saw show the difference:

| Amount | 30 | 55 | 70 | 90 | 300 |
|---|---|---|---|---|---|
| Escalated? | no | **yes** | no | **yes** | **yes** |

| Model | Mistakes on the 5 new tickets |
|---|---|
| `T = 50` | 1 (70 is a false alarm) |
| `T = 100` | 2 (55 and 90 missed) |
| Memorize exact amounts | 3 (misses 55, 90 and 300) |

The model with zero training errors is the worst on new tickets. **Training error measures fit to the past; only unseen examples measure generalization.** Five tickets is far too few to trust in practice; the point is the mechanism, not the numbers.

## 5. Features: what the model may know, and when

A feature is only legitimate if the live system can compute it **at the moment of prediction**, in the same way it was computed for training. For QuickCart, prediction happens inside the ticket-creation request.

**Pause and predict:** which of these candidate features can be used?

| Candidate feature | Usable at creation time? |
|---|---|
| Refund amount requested | ? |
| Tags chosen by the customer | ? |
| Tickets from this customer in the last 30 days | ? |
| `resolution_code` | ? |
| Minutes until the first agent reply | ? |
| `assigned_queue` | ? |

<details>
<summary>Reveal the reasoning</summary>

The **first three** are usable: they exist when the ticket is created. The 30-day count must be computed as of the ticket's creation time, not as of today. A nightly report that counts *later* tickets would leak the future.

The **last three** are not. `resolution_code` and the first-reply time are written after the outcome is known or under way. `assigned_queue` sounds harmless, but at QuickCart it is set *when a supervisor accepts an escalation*, so it is almost a copy of the label. A model trained with it would score superbly in testing and be useless live, because the field is empty for every new ticket. This is **target leakage**, covered in detail in [SG-ML-01](01-baselines-metrics-and-leakage.md).

</details>

**Train/serve skew** is the backend version of the same problem. Suppose training computes "tickets in the last 30 days" with a SQL window over a warehouse table, while the live API reads a cached counter that resets weekly. The two code paths produce different numbers for the same ticket, and the model receives inputs it never saw in training. Treat feature computation as a contract with one implementation, or with tests that prove two implementations agree.

## 6. Generalization and overfitting

![A chart with model flexibility on the horizontal axis and error on the vertical axis. Training error falls steadily toward zero. Validation error falls, bottoms out in the middle, then rises again. Zones are labelled too rigid, useful range, and memorizing.](../diagrams/learning/01-fit-versus-generalize.svg)

**Diagram walkthrough:** Read from left to right as the model becomes more flexible. A very rigid model (left), such as "flag everything over 500", misses real patterns, so **both** curves stay high. As flexibility grows, the model captures genuine patterns and both errors fall. Past a point, extra flexibility fits accidents in the training data, like specific amounts or ticket IDs: training error keeps falling while validation error rises. That rising gap is **overfitting**. The dot marks where you would choose the model, using validation data, never training error. The curves are an illustrative shape, not measurements; real curves are noisy, and the "best" point is a range.

A realistic comparison on QuickCart's validation tickets (synthetic figures) looks like this:

| Model | Training accuracy | Validation accuracy | What the gap says |
|---|---|---|---|
| Amount threshold | 90.5% | 90.1% | Little overfitting, little power |
| Tree ensemble over 300 features | 99.6% | 93.8% | Clear overfitting, yet the best validation score |
| Lookup of ticket IDs | 100.0% | 92.0% | Pure memorization: IDs never repeat, so it always predicts "no" on new tickets |

Two lessons hide in that table. First, a training/validation gap indicates overfitting, but the model with a gap can still be the most useful one. You choose by validation performance, not by the size of the gap. Second, 92.0% is exactly what you get by predicting "no escalation" for every ticket when 8% escalate. A lookup that has learned nothing scores 92% accuracy. Judging whether 93.8% is actually good needs a baseline and better metrics: the subject of [SG-ML-01](01-baselines-metrics-and-leakage.md).

Common ways to reduce overfitting, at the level you need for engineering decisions:

- **More representative data:** more tickets, especially more escalations. Usually the most reliable fix.
- **A simpler model or fewer features:** remove identifiers and anything that cannot plausibly generalize.
- **Regularization:** training settings that penalize complexity. Your data-science colleagues tune these on validation data.
- **Stop when validation stops improving**, rather than when training error is minimal.

## 7. Training, validation and test: three different jobs

> [!IMPORTANT]
> A dataset's role comes from how you use it. If its results guide a change, it is development evidence, even when the filename says `test`.

| Set | Job | How often it is used | QuickCart split |
|---|---|---|---|
| **Training** | Fit parameters | Every training run | Jan–Aug, 8,000 tickets |
| **Validation** | Compare models, choose features and thresholds | Many times during development | Sep–Oct, 2,000 tickets |
| **Test** | Estimate performance on unseen data, after every choice is frozen | Once per final candidate | Nov–Dec, 2,000 tickets |

Every time you look at a score and change something because of it, a little of that data's information leaks into your model, even though no parameter was fitted to it. The validation set is there to absorb that influence. The test set is kept untouched so that one number stays free of all your decisions. If you check the test score, dislike it, and change the model, the test set has become a second validation set. You then need fresh data to get an honest estimate again; reusing it "wears it out" ([Google ML Crash Course](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets)).

**Backend analogy, with its limit:** the test set is like a production canary you check once before rollout. Unlike a canary, rerunning it does not give you fresh evidence; the same tickets give the same answer, and your memory of the result biases the next change.

### Choose the split to match how the model will be used

![A January-to-December timeline: training January to August with 8,000 tickets, validation September to October with 2,000, test November to December with 2,000. Arrows show training fits parameters, validation is used many times to compare models and pick a threshold, and test is reported once. A marker shows a refund policy change on 1 October. Below, a correct example keeps all six tickets from one customer in training, while a random split puts three in training and three in test.](../diagrams/learning/02-time-and-group-split.svg)

**Diagram walkthrough:** The top bar is time, the axis on which the model will actually be used: it learns from the past and predicts the future. The three arrows give each period its single job. The policy-change marker falls inside validation, so validation and test both include tickets written under the new refund rules, which training never saw. That is deliberate: the evaluation measures the model in the conditions it will face. The bottom pair shows the second rule. One customer's near-identical tickets must land in the same split; otherwise the model is tested on text it has effectively already read. The diagram omits label delay (outcomes that take weeks to become known) and class balance across splits, both covered in the challenge.

| Split method | Use when | Danger if misused |
|---|---|---|
| **Random rows** | Examples are independent and the future looks like the past | Mixes future into training; scatters duplicates across splits |
| **Time-based** | You predict forward in time, which is most production use | Needs enough recent data for validation and test |
| **Grouped** (customer, account, device) | Several rows share a source the model could memorize | Must be combined with time order where both apply |

When data is scarce, **cross-validation** rotates which slice serves as validation and averages the results ([scikit-learn: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)). The same time and group rules still apply, and a final, untouched test set is still needed. Treat cross-validation details as reference material, not a core requirement of this course.

## 8. How this applies to LLMs

You will mostly use pre-trained language models rather than train your own. The discipline above still applies directly:

- **Prompt iteration is tuning.** Each time you rewrite a prompt after reading outputs, you are fitting to those examples. Keep a development set for that, and a separate held-out set you score only for release decisions.
- **Few-shot examples are training data.** Copying evaluation tickets into a prompt's examples is the same mistake as training on the test set.
- **You cannot inspect a hosted model's training data.** A public benchmark may already be inside it. Prefer fresh, private, task-specific cases, ideally written after the model's stated training cutoff.

## 9. Design boundaries: when not to learn

| Situation | Better choice | Why |
|---|---|---|
| The rule is policy: "refunds over 500 need a supervisor" | Write the rule in code | Deterministic, auditable, testable; nothing to learn |
| Only a few dozen escalations have ever happened | Rules plus human judgment; collect labelled data first | Too few positive examples to learn or to evaluate reliably |
| Labels are inconsistent: agents escalate for different reasons | Fix the labelling process first | The model will learn the inconsistency |
| Each decision must be explained to the affected person | A transparent rule, or a model with a review step | Learned patterns may not yield acceptable reasons |
| A wrong prediction causes irreversible harm | Model as a suggestion with human approval | Error rates are never zero |

### Common misconceptions

| Misconception | Correction |
|---|---|
| "99% training accuracy means the model works." | It means the model fits the training tickets. Only unseen data shows generalization. |
| "More features always help." | Each feature can add noise, cost, privacy exposure and leakage risk. |
| "Random splitting is the neutral default." | It is a choice. For forward-in-time prediction it usually overstates performance. |
| "We can check the test score as often as we like; we're not training on it." | Every decision made after seeing it leaks information into the model. |
| "Using a hosted LLM means evaluation is someone else's job." | The provider evaluated their model; you must evaluate your task, data and prompts. |

## 10. Production concerns

- **Labels encode past behavior.** "Escalated" reflects what supervisors used to do, including inconsistency and bias, for example escalating some customer segments more readily. A model will reproduce that unless someone checks.
- **Feedback loops:** once the model routes tickets, its predictions change who gets escalated, and so change future labels. Keep a small, randomly selected sample handled the old way if you need unbiased labels later.
- **Privacy:** ticket text contains personal data. Use only the fields the model needs, define retention for training extracts, and keep evaluation sets synthetic or properly governed.
- **Ownership:** someone must own the label definition, the feature code, the evaluation set and the decision to ship. "The model" is not an owner.
- **Cost:** a model adds a dependency to the ticket-creation path, with latency, failure modes and running cost. The [W-PY-API-01](../../../workbooks/python/quickcart-api/README.md) triage endpoint shows the shape: bounded call, allowlisted output, explicit failure status.

## 11. Knowledge checks

**1.** A teammate reports: "Training accuracy 97%, validation 96%, so no overfitting, ship it." What is missing?

<details>
<summary>Show answer and explanation</summary>

A comparison with a baseline. If 95% of validation tickets are "no escalation", always predicting "no" scores 95%, and the model barely beats doing nothing. A small gap shows the model is not badly overfitting; it does not show the model is useful. Ask for the base rate and the metrics in chapter 01.

</details>

**2.** You tuned features for two weeks against the Nov–Dec tickets, then reported a Nov–Dec score. What is wrong, and how do you get an honest number?

<details>
<summary>Show answer and explanation</summary>

Nov–Dec acted as validation: two weeks of decisions fitted it. The reported score is optimistic by an unknown amount. Get an honest estimate from data none of those decisions touched: for example January's tickets as a new test set, scored once with the frozen model.

</details>

**3.** QuickCart's ticket table has a `customer_id`. Should it be a feature?

<details>
<summary>Show answer and explanation</summary>

No, as a raw identifier. It lets the model memorize individual customers, which does not generalize to new customers and raises privacy concerns. Derived, time-correct features such as "tickets in the prior 30 days" or "account age at ticket creation" can carry the useful signal. The identifier is still essential for *grouped splitting*.

</details>

**4.** Training computes "account age" in days; the live API sends it in months. The model's live flag rate suddenly drops. Name the problem and a test that would have caught it.

<details>
<summary>Show answer and explanation</summary>

Train/serve skew in feature computation. A contract test that runs both code paths on the same fixture tickets and asserts equal feature values would have caught it, as would monitoring live feature distributions against training ranges.

</details>

## 12. Design challenge: refund-abuse flag

QuickCart wants to flag refund requests that may be abusive. You have 18 months of requests (about 90,000). About 0.5% were later confirmed as abuse. Confirmation can take up to 60 days after the request. Some people use several accounts from one household; the data includes a hashed payment instrument and a shipping-address hash. Investigators record `investigation_outcome` and `investigator_notes`.

**Your tasks:**

1. Propose a training/validation/test split, with dates, and justify the method.
2. List three features you would allow and two you would forbid, with reasons.
3. Explain what the 60-day confirmation delay does to your most recent data.
4. State one reason a learned model might be the wrong first step here.

<details>
<summary>Show one reasonable solution</summary>

1. **Time-based and grouped.** Use months 1–12 for training, 13–15 for validation and 16 for test, keeping each payment instrument and address hash entirely within one split. If a group spans the boundary, assign it to the earlier split and exclude its later rows from evaluation. Time order matches use; grouping stops the model from recognizing a household it has already seen.
2. **Allow:** refund amount relative to order value; account age at request time; refunds in the prior 90 days as of the request time. **Forbid:** `investigation_outcome` (it is the label) and `investigator_notes` (written after the request, and they reveal the outcome).
3. Requests from the last 60 days do not have final labels yet, and many "not abuse" labels there are really "not yet confirmed". Exclude months 17–18 from evaluation, or the test set will count future confirmations as false alarms.
4. At 0.5%, the test month holds only about 25 confirmed cases, too few to measure recall precisely (chapter 01 shows how wide that uncertainty is). Simple velocity rules plus investigator review may deliver most of the value while labelled data accumulates.

</details>

## 13. Revision and transition

| Question | Short answer |
|---|---|
| What does training do? | Searches for parameter values that make predictions match labels on training examples. |
| Why is zero training error suspicious? | It is reachable by memorizing, which does not generalize. |
| What makes a feature legitimate? | It is available at prediction time, computed identically for training and serving. |
| What is overfitting? | Fitting accidents in the training data; validation error rises while training error falls. |
| Validation versus test? | Validation guides decisions repeatedly; test is scored once after decisions are frozen. |
| Which split for forward prediction? | Time-based, grouped by any source that repeats. |

**Glossary:** *example, label, feature, parameter, training, inference, generalization, overfitting, train/serve skew, validation set, test set, grouped split, cross-validation.* Each is defined in sections 3–7 above.

**Sources:** [Google ML Crash Course — Dividing the original dataset](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets) (what training, validation and test sets are for, test sets wearing out, duplicates across splits); [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) (reference only). Records are in the [source ledger](../../../docs/source-ledger.md). All QuickCart figures are made up and calculated by the author.

## Completion checkpoint

**You can now:** explain why fitting past tickets is not enough, and defend a split plan that checks when each input is available, keeps time order, groups related records and allows for labels that arrive late.

**Show it:** your section 12 plan, including one tempting input you left out and why.

**Next:** a model can generalize and still not be useful. Is 93.8% impressive when 92% comes free, and which mistakes matter most? Continue to [SG-ML-01 — Baselines, metrics and leakage](01-baselines-metrics-and-leakage.md).

[Previous: W-PY-API-01 — QuickCart API](../../../workbooks/python/quickcart-api/README.md) · [Course map](../../../README.md#ordered-capability-map)
