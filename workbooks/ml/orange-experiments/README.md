# W-ML-ORANGE-01 — Live demo: overfitting, baselines and leakage in Orange

> **Unit ID:** W-ML-ORANGE-01 · **Capability:** AI-ML-01 · **Classification:** Optional no-code demo; not required evidence<br>
> **Format:** Instructor-led live demonstration in the [Orange Data Mining](https://orangedatamining.com/download/) desktop app, for audiences who do not code. Self-study learners can follow the same steps.<br>
> **Central question:** When you evaluate a model yourself, which of the guides' warnings actually show up, and how large are they?<br>
> **Prerequisites:** none for the audience. The facilitator should know [SG-ML-00](../../../study-guides/ml-foundations/docs/00-learning-from-examples.md) and [SG-ML-01](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md).<br>
> **Time:** Facilitator rehearsal 45–60 min; live demo 45–60 min; optional group decision 15 min. Editorial estimates<br>
> **Status:** Draft. The dataset's effects were checked with scikit-learn (`check_demo_effects.py`). **The Orange click-through has not been rehearsed by the author**, so record your own numbers before the first class.<br>
> **Environment:** Orange 3.40.0 desktop app (Windows installer, portable zip, or macOS). No code, account or paid service

**The problem it addresses:** teams often approve a model on the strength of one impressive number, and stakeholders who do not code have no way to question it. After this demo, they know the three questions to ask: compared with what baseline, measured on which data, and could the model have seen the answer?

This unit is a **demo script**, not a coding lesson. Orange lets a non-coding audience watch a model being evaluated: connect boxes, change one setting, and the scores update within seconds. Use it to make three ideas visible before anyone writes code:

1. A perfect score on the training data can be worse than doing nothing on new data.
2. Accuracy can look fine while the model is useless for the rare cases that matter.
3. One leaked field, a repeated customer or the wrong split can make a weak model look excellent.

The course's coding route does **not** use Orange. Learners implement the same checks with scikit-learn in the hands-on [W-ML-EVAL-01 evaluation exercise](../escalation-evaluation/README.md).

## The dataset

[`quickcart-tickets-2025.csv`](../../../shared-assets/quickcart-escalation-tickets/data/quickcart-tickets-2025.csv), in `shared-assets/quickcart-escalation-tickets/data/`, holds 12,000 invented QuickCart support tickets, 1,000 per month. **993 escalated (8.3%)**, so always answering "no" is right 91.7% of the time. The [shared generator](../../../shared-assets/quickcart-escalation-tickets/README.md) creates the file deterministically from readable rules; the scikit-learn evaluation exercise uses the same file.

| Column | Role in Orange | Meaning |
|---|---|---|
| `amount`, `prior_tickets_30d`, `account_age_days` | Feature (numeric) | Refund amount, the customer's tickets in the prior 30 days, account age |
| `tag`, `channel`, `language` | Feature (categorical) | Ticket topic, email or chat, `en` or `other` |
| `assigned_queue` | Feature (categorical) | **Planted leak:** written after a supervisor accepts an escalation |
| `escalated` | Target | `yes` or `no` |
| `ticket_id`, `customer_id`, `customer_fold`, `month` | Meta (ignored by learners) | Identifiers, a 5-way customer bucket for grouped evaluation, month 1–12 |

The planted ground truth:
- Larger amounts, `chargeback` tags and more prior tickets raise escalation risk.
- From **1 October**, a new returns policy makes returns tickets escalate far more often: 112 of the 357 November–December returns tickets escalated (31%).
- Twenty repeat customers a month each send six near-identical tickets. Whether they escalate depends on a hidden trait the features do not show.

## Before class: set up and rehearse

1. Install Orange from the [download page](https://orangedatamining.com/download/). On Windows, the standard installer does not need administrator rights, and the portable zip needs no installation. This guide assumes 3.40.0; later 3.x releases may relabel controls.
2. Copy this folder to your machine and save workflows there, not in the course repository.
3. In the File widget, open `shared-assets/quickcart-escalation-tickets/data/quickcart-tickets-2025.csv` from your copy of the repository.
4. Build the workflows below once and fill in the **rehearsal record** at the end. In class you will quote *your* numbers, so you are never surprised live.
5. Save the finished workflow (`.ows`) so a dropped connection or crash does not cost you the demo.

## Demo 1 — The perfect model that is worse than guessing (15 min)

**Build:** File → **Select Columns** → **Test and Score**.
- In the File widget, check the roles: `escalated` is the target; the four ID/month columns are meta.
- In Select Columns, move `assigned_queue` to **Ignored**.
- Add and connect four learners:
  - **Constant**: the do-nothing baseline.
  - **Tree** with default settings.
  - A second **Tree** renamed `Tree, no limits`, with all four limits unticked: "Min. number of instances in leaves", "Do not split subsets smaller than", "Limit the maximal tree depth to" and "Stop when majority reaches".
  - **Logistic Regression**.
- In Test and Score, set the target class selector ("Evaluation results for target" or "Target class") to **yes**. Otherwise precision and recall are averaged over both classes.

**Ask the room first:** "If a model scores 100% on the tickets it studied, how will it do on new ones?" Take a show of hands.

**Show:** select **Test on train data**: `Tree, no limits` scores 100%. Switch to **Cross validation** (5 folds, Stratified, the default): its accuracy drops **below Constant's 91.7%**.

**Point out:**
- It memorized amounts, ages and the repeat customers' near-copies. Studying the answers is not learning.
- Logistic Regression's accuracy lands at about the Constant level, yet its **AUC** (ranking quality, where 0.5 is a coin flip) is well above 0.5. The model has found real signal; accuracy hides it because escalations are rare.

## Demo 2 — Why accuracy misleads (10 min)

**Build:** Test and Score → **Confusion Matrix**, still under cross-validation. Show the number of instances, and click through the learners.

**Ask:** "Of the 993 real escalations, how many did each model catch?"

**Point out:** read each model's caught count out of 993, then out of the tickets it flagged. Write both on the board as fractions, using your rehearsal numbers: "caught N of 993" says more than "92% accurate". Constant catches **none** and still scores 91.7%. Each model flags a different number of tickets, so a fair comparison fixes how many tickets supervisors can review. This is SG-ML-01, section 5.

## Demo 3 — Three ways an evaluation fools you (20–25 min)

### 3a. The field that knows the answer

**Break it:** in Select Columns, move `assigned_queue` back to **Features**. Every model's recall and accuracy jump. Logistic Regression catches nearly every escalation.

**Diagnose live:** connect Select Columns → **Rank**. `assigned_queue` scores several times higher than any other field. Ask: *"When is this field filled in?"* After a supervisor accepts the escalation. A brand-new ticket would always say `agents`, so the model would be useless in production.

**Repair:** move it back to Ignored and show the scores return to Demo 1's levels.

### 3b. The customer the model has already met

**Change:** Test and Score sampling → **Cross validation by feature** → `customer_fold`. Each customer's tickets now stay together, like a real launch, where new customers arrive.

**Ask:** "Which model will suffer: the one that memorizes, or the simple one?"

**Point out:** `Tree, no limits` loses a clear share of its recall once it can no longer recognize repeat customers' near-copies. Logistic Regression barely moves, because it cannot memorize individuals. Then show the default Tree and ask the room why it behaves as it does. Group leakage flatters a model in proportion to its ability to memorize.

### 3c. Training on the future

**Build:**
- Add two **Select Rows** widgets after Select Columns, with `assigned_queue` ignored.
- In the first, keep `month` **is between** 1 and 8, and connect it to Test and Score's **Data** input.
- In the second, keep `month` **is between** 11 and 12, and connect it to **Test Data**; choose that input in the link dialog.
- Set sampling to **Test on test data**.

**Then narrow it:** add the condition `tag` **is** `returns` to the second Select Rows. 112 of these 357 tickets escalated, yet every model, trained on January–August, catches only a handful.

**Point out:** the models never saw post-policy behavior. Random cross-validation over the whole year mixes October–December into training and hides this. Evaluate the way you will deploy: train on the past, test on the future.

## Optional group decision (15 min)

Give the room SG-ML-01's assumptions: a missed escalation costs 40 minutes, a false alarm 4 minutes, and supervisors can review at most 10% of tickets (1,200 of 12,000). Using the **grouped** Confusion Matrix counts from your rehearsal, groups compute each model's cost (missed × 40 + false alarms × 4) and check its flag count against capacity.

<details><summary>Facilitator notes</summary>

Steer the discussion toward three conclusions:
- The cheapest model at Orange's default cut-off may not be the most accurate one, because misses cost ten times more than false alarms.
- Comparing models that flag different numbers of tickets is unfair. The better comparison fixes the review volume, which in code means choosing each model's threshold on validation data.
- "None of these, as configured" is a legitimate answer, especially given 3c.

</details>

## What each demo maps to in engineering practice

| What the audience saw | What an engineering team does about it |
|---|---|
| A perfect training score, cross-validated score below baseline | Never report training metrics as quality; evaluate only on held-out data |
| Accuracy at the baseline, AUC well above 0.5 | Report base rate, baseline, precision and recall with denominators; choose thresholds on validation |
| One field dominating the ranking | Check that every feature is known at prediction time; automate the check |
| Recall dropping when customers stay together | Split by customer, with a test proving no customer appears in two splits |
| Post-policy returns almost all missed | Time-based splits, slice reports and monitoring after policy changes |

**Reflect (closing question for the room):** which of your predictions today was furthest off? Where in your own work is a field written *after* the event someone might want to predict?

## Rehearsal record (facilitator)

Fill this in from your own Orange run before the first class, and note the Orange version. Quote these numbers live.

| Demo | Setting | What to record |
|---|---|---|
| 1 | Test on train data | `Tree, no limits` CA and recall |
| 1 | Cross validation, 5 folds | CA and AUC for all four learners |
| 2 | Confusion Matrix | Caught, false alarms and flags for Logistic Regression and Tree |
| 3a | `assigned_queue` included | Logistic Regression recall; the top two Rank scores |
| 3b | Cross validation by `customer_fold` | Recall for each learner |
| 3c | Months 1–8 → 11–12, returns only | Caught out of 112 for each learner |

## Troubleshooting during a live session

| Symptom | Likely cause | Fix |
|---|---|---|
| "Data has no target variable" | `escalated` loaded as a feature | In the File widget, set `escalated` to **target**. |
| Precision and recall look odd | The target class is set to the class average | Set the target class selector to **yes**. |
| "Cross validation by feature" is greyed out | `customer_fold` is not a categorical meta | In the File widget, set `customer_fold` to **categorical**, role **meta**. |
| "Missing separate test data input" | The Nov–Dec Select Rows is linked to **Data** | Redraw the link and choose **Test Data**. |
| Numbers differ from your rehearsal | Different settings, fold count or version | Check 5 folds, Stratified, and the target class. The direction of each effect is what matters. |
| Logistic Regression shows a warning icon | The optimizer may stop early on unscaled amounts | Safe to continue for this demo; mention it if asked. |

## Limits and next step

Cleanup: close Orange after the session. The demos write nothing to the repository; delete any workflow files you saved for the rehearsal if you do not need them.

The data and its rules are synthetic and deliberately simple. Orange's defaults are not production recommendations. The demo builds intuition only; it produces no learner evidence for AI-ML-01. Afterwards, coders continue to the hands-on [W-ML-EVAL-01 scikit-learn evaluation exercise](../escalation-evaluation/README.md), then the course map's AI-LLM-01 row. Return to the [course map](../../../README.md#ordered-capability-map).

## Completion checkpoint

**You can now:** run the three live demos, collect the room's predictions first, and connect each observation to an engineering control.

**Show it:** your completed rehearsal record.

**Next:** learners continue with the hands-on [W-ML-EVAL-01 evaluation exercise](../escalation-evaluation/README.md).

## For maintainers: regenerate and check the dataset

From this directory:

```powershell
python ../../../shared-assets/quickcart-escalation-tickets/generate_tickets.py --check
uv run --no-project --python 3.11 --exclude-newer 2026-09-30 --with scikit-learn==1.9.1 python check_demo_effects.py
```

The first command proves the committed shared CSV matches its seeded generator; it uses only the standard library, and CI runs it. The second uses **scikit-learn, not Orange**, to assert that every effect the demos point out is present, in direction and rough size:
- memorization below baseline;
- accuracy at baseline with AUC above 0.75;
- leak dominance and recall jump;
- group-leak recall drop for the memorizing tree only;
- post-policy returns missed.

It deliberately does not reproduce Orange's exact numbers, so facilitators record those in the rehearsal sheet. Tested on 2026-10-14 with scikit-learn 1.9.1 on Python 3.11.13. If you change the generator, rerun both commands and re-rehearse the demo.

**Sources:** [Orange download page](https://orangedatamining.com/download/) and [Test and Score widget documentation](https://orangedatamining.com/widget-catalog/evaluate/testandscore/), checked 2026-10-14. Recorded in the [source ledger](../../../docs/source-ledger.md).
