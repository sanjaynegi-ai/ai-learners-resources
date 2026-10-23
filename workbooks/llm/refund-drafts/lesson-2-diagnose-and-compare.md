# W-LLM-API-02 — Diagnose bad outputs, compare prompts, absorb a requirement change

**Which layer should catch a bad output, and what evidence would justify a prompt change?** More examples passing is useful only when the criteria and denominators remain honest.

> **Your goal:** Diagnose failures, compare candidates and add a check for a changed business rule.<br>
> **You need:** Your completed [direct-provider lesson](README.md), in the same personal project.<br>
> **Effort:** 20 minutes reading, 30 diagnosis, 40 comparison and 45 independent work; optional live comparison 30 minutes. Estimates.<br>
> **You will produce:** Predictions, failure/repair evidence, a status-claim check and a prompt-release decision. **Status:** Draft; comparison data is synthetic replay, not live-model evidence.

QuickCart's fictional support team now needs to decide whether a revised refund prompt is safer and more useful. Continue your `api-direct-v1` project, keeping the first lesson's independent work and its locked environment. This is a continuation, not a second application to initialize.

**Before running:** use the same PowerShell/Python 3.11 project environment as [lesson 1](README.md#setup-and-verify-offline). All diagnosis and default comparison commands are offline. Make source faults only in your personal copy and reverse only those changes afterwards. Live comparison is optional and paid, with separate prerequisites below.

<details>
<summary>Reference: detailed unit metadata and historical verification</summary>

> **Unit ID:** W-LLM-API-02 · **Capability:** AI-API-01 · **Checkpoint:** continues `api-direct-v1` in this project<br>
> **Audience:** Learners who completed [W-LLM-API-01](README.md) in this same project<br>
> **Central question:** When a model's output is wrong, which layer should catch it, and how do you prove a prompt change made things better rather than just different?<br>
> **Effort:** Reading 20 min; diagnosis 30 min; prompt comparison 40 min; requirement change 45 min; optional paid live comparison 30 min. Editorial estimates<br>
> **Artifact:** A prediction sheet, a diagnosed fault drill, your status-claims check passing its acceptance test, and a prompt-release decision note with denominators<br>
> **Status:** Draft. 32 offline tests, the fault drill and the exercise check author-verified. **The comparison data is synthetic replay; no live model comparison was run by the author**<br>
> **Environment:** As W-LLM-API-01; offline by default

</details>

The first lesson tested known failure boundaries around a direct model call. This lesson asks harder questions. Of all the ways an output can be wrong, which does your code catch, which does it miss, and how do you change a prompt without fooling yourself?

**Intuition:** think of code review for a teammate whose pull requests are usually fine. Linters catch syntax, type checks catch shapes, tests catch broken rules, and a reviewer catches what none of those can express, such as "this is technically valid but not what the customer asked". Model output needs the same layers. The analogy's limit: a teammate's mistakes repeat in learnable ways, while a model's can shift with every prompt or model version, so the checks must be re-run on every change.

## What a run can and cannot prove

Read this table before running anything in this lesson. It is the most important idea here.

| Kind of run | Proves | Does **not** prove |
|---|---|---|
| Offline tests with the fake provider | Control flow: retries, deadlines, outcome codes, that each check fires | Anything about a real model's answers |
| Replay of recorded outputs (`refund-drafts-compare`) | That the comparison harness, metrics and your decision process work on known inputs | Which prompt a real model would do better with. The recordings here are **hand-written and synthetic** |
| Live run on a stated model and date (`--live`) | How *that* model behaved on *these* cases, that day | Behavior on other models, later versions, or traffic unlike your cases |
| Human review of drafts | Tone, language, relevance, policy fit that no rule expresses | Anything at scale without sampling and denominators |

Report each kind separately, and never quote a replay number as model quality.

> [!IMPORTANT]
> A replay score describes the supplied recordings and your checks. It cannot establish that a prompt improves a real model. Fix release criteria before looking at results, then state the evidence type beside every conclusion.

## Part 1 — Predict, then diagnose

`fixtures/diagnosis-cases.json` holds ten raw outputs. Each is synthetic and written to show one way an output can go wrong. For each, **write down your prediction first**: which layer rejects it first?
- **syntax:** not JSON;
- **schema:** JSON that breaks the contract;
- **business:** a valid shape that breaks a rule;
- **passed:** no automated check objects.

Then, from the `workbooks/llm/refund-drafts` project root (your W-LLM-API-01 project), run:

```powershell
uv run refund-drafts-diagnose
```

**Observed (author run):** D-01 to D-03 are syntax; D-04 to D-06 are schema (`approved:extra_forbidden`, `needs_agent:bool_type`, `refund_date_used:date_parsing`); D-07 and D-08 are business; and **D-09 and D-10 pass every check** even though both are wrong.

<details><summary>Explained answers and what to do at each layer</summary>

| Layer | Cases | Typical repair |
|---|---|---|
| Syntax | Prose instead of JSON (D-01), truncated JSON (D-02), JSON inside a code fence (D-03) | Retry within budget; use the provider's strict structured-output mode; check the stop reason (truncation is usually a budget problem, not a prompt problem) |
| Schema | Extra field, string `"false"` for a boolean, `20/10/2026` for a date | Keep the schema strict and fail closed; never "fix up" types silently |
| Business | A date not in the order (D-07); a forbidden promise (D-08) | Checks against systems of record; route to an agent |
| Passed but wrong | Claims a pending refund was issued (D-09); English reply to a German customer (D-10) | A new rule if the failure is checkable (Part 3); otherwise human review, evaluation sets and monitoring |

**D-03 is a decision, not a bug.** Some teams strip code fences before parsing. That is tolerable if you decide it deliberately and test it. This project fails closed and counts it, so a tolerance you never chose cannot hide a format regression.

</details>

### Break, diagnose, repair: lenient parsing

In `schema.py`, change `ConfigDict(extra="forbid", strict=True)` to `ConfigDict(extra="forbid")`. Predict which case changes, then rerun the diagnosis and the tests.

**Observed:**
- D-05 moves from `schema` to **`passed`**: Pydantic's default lax mode coerces the string `"false"` into `False`.
- The summary changes to "3/10 outputs passed every automated check".
- Three tests fail.

Lenient parsing turns a model's type mistake into a silently accepted answer. Restore `strict=True`, rerun, and record before and after.

## Part 2 — Compare two prompts honestly

`prompts/refund_reply_v2.txt` adds rules for out-of-scope requests and pending refunds, explicit language codes, and "no code fences". Is it better?

**Decide the criteria before you look.** `fixtures/eval/expectations.json` was fixed first: for ten evaluation tickets, whether a correct system should produce `ready` or `needs_agent`. The metrics, with denominators:

- **Unsafe ready:** a draft cleared for sending when it should have gone to an agent. This is the critical gate.
- **Unnecessary escalation:** an agent given work the system could have done. This is the cost.
- **Failed:** no usable output after the attempt budget.
- **Human review notes** on `ready` drafts: problems only a person spotted.

```powershell
uv run refund-drafts-compare
```

**Observed (replay of synthetic recordings):**

| Prompt | Matches expectation | Unsafe ready | Unnecessary escalation | Failed | Human-review notes on ready drafts |
|---|---|---|---|---|---|
| v1 | 5/10 | **3/4** (E-02, E-07, E-09) | 2/6 (E-06, E-08) | 0/10 | E-03, E-04: English reply to German or Hindi customer |
| v2 | 6/10 | **1/4** (E-09) | 2/6 (E-06, E-10) | 1/10 (E-04: code fence, 3 attempts) | E-09: promises a card change |

**Pause and decide:** would you release v2? Write your answer and reasons before opening the worked reasoning.

<details><summary>Worked reasoning</summary>

- **On the critical gate, v2 is clearly better** (3/4 to 1/4 unsafe), but **neither passes** if the gate is "zero unsafe ready". E-09 (a request to refund to a different card) still produces a confident promise. The prompt asked for escalation and the recording ignored it, which is exactly why prompt rules need code-side enforcement where possible.
- **v2 traded one cost for another:** E-08 (the injection) is now answered correctly, but E-10 (an angry German customer) is now escalated unnecessarily. E-04 fails on a code fence despite the new instruction.
- **The denominators are tiny:** ten cases, four "should escalate". One case is 25 percentage points of the unsafe rate, so you cannot claim a general improvement from this.
- **A defensible decision:** do not release automatic sending. Treat v2 as the better candidate *for agent-reviewed drafts*. Add a check for out-of-scope requests, or route them by rule. Expand the evaluation set, and run the live comparison on a named model before any claim about real quality.
- **Above all, this was replay:** the recordings were written to illustrate failure modes. Only a live run produces evidence about a model.

</details>

## Part 3 — Independent: a requirement change

Support Operations, after two complaints: *"Drafts must never say a refund was issued when it was not."* D-09 and replay cases E-02 and E-07 show the problem passing every current check.

Implement `check_status_claims` in `exercises/status_claims.py`, following its docstring. It must:
- reject English and German claims of issue or dispatch when `refund_status` is not `issued`;
- leave issued refunds and holding replies alone.

Write two cases of your own first, then:

```powershell
uv run python exercises/check_status_claims.py
```

**Expected:** `status_claims: status-claim checks passed...`. The checker also re-runs the diagnosis and the replay comparison with your check added. D-09 must now be caught at the business layer, v1's unsafe-ready list must drop to `['E-09']`, and issued-refund drafts must not be newly blocked. The untouched starter raises `NotImplementedError`; `--reference` runs the inspectable reference.

<details><summary>Progressive hints</summary>

1. Return early when the refund really was issued; most false positives come from forgetting this.
2. Collect claim phrases in both languages; compare in lower case. "Rückerstattung" (the noun) is not a claim, so test your German holding reply.
3. Return a list, so this check composes with the others in `DEFAULT_CHECKS`.

</details>

<details><summary>Worked reasoning</summary>

v2's prompt already forbids the claim, so why add code? Prompt wording expresses the desired behavior; a code-side check can reject covered claim patterns even when a model ignores that wording. This replay illustrates the distinction, but it does not measure how often a real model would make the claim. Neither layer guarantees safety for phrasing the check does not recognize.

Name the check's limits in your note. A phrase list misses paraphrases ("the money is with your bank now") and other languages. Hindi is not covered, although E-04 is a Hindi order. That is a reason to keep human review on, and to add any new phrasing you find to the evaluation set.

</details>

Then, in your decision note, propose how you would handle E-09 (out-of-scope requests). Would you add another phrase check, a separate classification step, or route all non-timing questions to agents? Give one reason against each option you reject.

## Part 4 — Optional: the live comparison (paid)

With the live configuration from [W-LLM-API-01](README.md#optional-the-live-check-paid), confirm the account/model, spending budget, execution window and reviewer for this larger run. It allows up to **60 calls** (2 prompts × 10 tickets × up to 3 attempts), with the configured output-token limit per call plus billed input tokens. These request bounds are not a currency spending cap. Keep the default replay route if these conditions are not in place.

```powershell
uv run refund-drafts-compare --live --confirm-paid-calls
```

Record the model name, the date and the full output (`--json`). Read every `ready` draft yourself and note language, tone and policy fit, which the metrics cannot see. Then compare with the replay table, and write one paragraph on what the live run told you that the replay could not. **The author has not run this.**

## Completion evidence

- [ ] Your prediction sheet for D-01 to D-10, with the observed layer beside each prediction.
- [ ] The lenient-parsing drill: before and after diagnosis output, failing tests, repair.
- [ ] `exercises/check_status_claims.py` passes on **your** implementation, with your own cases. Disclose any use of the reference.
- [ ] A prompt-release decision note: criteria fixed beforehand, both versions' metrics with denominators, your release decision, your E-09 proposal, and the limits of replay evidence.
- [ ] Optional: a live comparison record with model, date and your human review, reported separately.

## Troubleshooting

| Symptom | Likely cause | Diagnostic and repair |
|---|---|---|
| `KeyError` from `ReplayProvider` | You added an evaluation ticket without a recording | Add a recording for every version, or run `--live`. Replay must never invent output. |
| Comparison numbers differ from the tables | Recordings, expectations or checks were edited | Run `git diff fixtures/`; changed inputs make a different experiment, so note it. |
| `UnicodeEncodeError` printing German or Hindi text | Windows console code page | Set `$env:PYTHONIOENCODING = "utf-8"` in the terminal. |
| `--live` refuses to run | Missing `--confirm-paid-calls` or live configuration | Intended. See W-LLM-API-01's live section. |

## Limits and next step

Cleanup: follow [W-LLM-API-01's cleanup](README.md#cleanup-limits-and-next-step). This lesson starts no servers; only the optional live comparison costs money, and it stops when you stop running it.

The diagnosis and replay data are small and synthetic by design, so the numbers teach the method, not the size of real effects. Language correctness, tone and out-of-scope detection remain human-review items here.

**You can now:** say which layer catches each kind of bad output, compare two prompts on criteria fixed in advance with honest denominators, and add a code-side check when a prompt rule is not enough. **Show it:** your prompt-release decision note.

**Next:** [W-LC-02 — Models and Messages](../../langchain/01-learning-workbook/02-models-and-messages.md), where the course map's AI-CALL-01 row shows the same call through a framework. Reliability depth follows in AI-RELIABLE-01. Return to the [course map](../../../README.md#ordered-capability-map).

**Sources:** As W-LLM-API-01 ([source ledger](../../../docs/source-ledger.md)); evaluation discipline from [SG-ML-01](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) and [SG-LLM-01, section 9](../../../study-guides/llm-foundations/docs/01-designing-prompts-and-context.md#9-prompts-are-code-version-review-evaluate).
