# Escalation model: evaluation and decision note

Copy this file to your personal notes and fill in every section. Use counts with denominators (for example "38.8% (85/219)"), not bare percentages. Say which split each number comes from.

**Author / date / repository revision:**
**Dataset fingerprint (from `results/frozen.json`):**

## 1. Baselines and model on validation

| | Flags (of 2,000) | Caught (of 219) | Precision | Recall | Cost (min) |
|---|---|---|---|---|---|
| Constant | | | | | |
| Rule | | | | | |
| Logistic regression @ 0.5 | | | | | |
| Logistic regression @ chosen threshold | | | | | |

Does the model beat the best baseline by a margin that matters? Why is the 0.5 threshold the wrong default here?

## 2. Test result (scored once)

Frozen threshold, test counts, and how test differs from validation. Give one reason for the difference.

## 3. Slices

Which slices did you choose **before** looking, and why? Which are too small to judge? Which difference is real, and which might be noise?

## 4. Error analysis (validation)

| Pattern among missed escalations or false alarms | Count | Example ticket IDs | Likely cause | Fixable by the model? |
|---|---|---|---|---|
| | | | | |

## 5. Changed requirement: decision

State the requirement, whether it can be met with evidence, your decision (release, partial release, or no release), the options you rejected, what you need from Operations, and when you would re-evaluate.

## 6. Limitations and owner

What this evaluation cannot tell you (synthetic data, one model family, label delay, no live traffic), and who owns the next decision.
