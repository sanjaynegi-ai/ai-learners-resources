# W-OPS-01 — Monitor a release and recover a configuration incident

QuickCart gets faster responses, but fewer useful answers. Can you detect and contain the regression?

> **Your goal:** Monitor quality, coverage, latency and cost; halt a failed rollout and verify recovery.<br>
> **You need:** Read [application LLMOps](../../../study-guides/application-llmops/README.md) and complete evaluation/delivery prerequisites.<br>
> **Estimated effort:** 3 h including setup, build, incident, independent work and repair; plus the guide's 40–50 min. Unpiloted estimates.<br>
> **You will produce:** Versioned reports, safe telemetry, an incident record and independent slice gate.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Project route:** start a personal copy of this independent Release Watch package. It consumes synthetic manifests, traffic and reviewer labels; it does not deploy or monitor your real AWS worker. Preserve its registry and incident reports separately from cloud/model evidence.

**Study route:** inspect stable and canary configuration, predict how the smaller timeout changes outcomes, run the offline incident, then verify halt/recovery and complete the independent slice gate. A restored configuration does not automatically authorize resuming rollout.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-OPS-01 · **Status:** Draft, unpiloted<br>
> **Central question:** Can you contain lost useful work even when conditional quality looks perfect?<br>
> **Prerequisites:** [SG-OPS-00](../../../study-guides/application-llmops/README.md), [W-LLM-EVAL-01](../../llm/eval-harness/README.md) and [delivery](../../delivery/README.md). The root path places operations after [AWS delivery](../../aws/bedrock-worker/README.md); this local checkpoint can run without an AWS account.<br>
> **Effort:** Reading 20 min, setup 10, guided implementation 35, incident diagnosis 30, independent task 50, evidence/defense 20, repair reserve 15: 3 hours estimated; plus guide 40–50 min. No extra compulsory week<br>
> **Environment:** Windows PowerShell, Python 3.13.1 direct tests and Python 3.12.10 fresh locked verification; standard library only; uv 0.13.1. Python >=3.11 declared; other Python/OS combinations unverified<br>
> **Outcome / evidence:** Versioned reports, sanitized telemetry tests, incident timeline, restored artifact, runbook amendment and independent slice-gate implementation<br>
> **Last verified:** 2026-10-15: 12 reference tests, fresh-copy CLI and two caught source mutations. Synthetic traffic and local files only; no provider, cloud or hosted monitoring

</details>

## 1. Starting checkpoint and acceptance

You start with the complete inspectable `watch.py` reference and `test_watch.py`. This is a small operational extension of the evaluation discipline, not another refund application. It does not invoke or replace the earlier application pipeline: the synthetic workload isolates monitoring and recovery, and its artifacts name the simulated model explicitly. Real integration requires trusted measurements at the existing application's boundary and separately reviewed live-model evidence.

Copy the folder for your own changes before editing. There is no hidden reference branch. Checkpoint **reference-0.1.0** is the supplied implementation; **guided-watch** is your reconstructed metric function; **incident-recovered** is the generated output; **slice-transfer** is your independent gate. Record file hashes and actual results with your submission.

Completion requires correct denominators, rejection of missing evidence, removal of raw sensitive fields, verified expiry/access behavior, a halted canary, restored compatible configuration and fresh recovery probes. Independent work must catch a slice regression that the aggregate passes. A copied reference run is practice evidence, not independently verified competence.

## 2. Setup and baseline

From repository root in PowerShell:

**Execution requirements:** Windows PowerShell, Python 3.13.1 direct tests and Python 3.12.10 fresh locked verification; standard library only; uv 0.13.1. Python >=3.11 declared; other Python/OS combinations unverified. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/operations/release-watch
python --version
python -m unittest -v
python watch.py --out runs/incident-01
```

No dependencies, keys, `.env` loading or paid operations are needed. If using uv, from this same directory use `uv sync --locked` then `uv run --locked python -m unittest -v`. Initial Python provisioning may need network access. The lockfile contains no third-party packages.

The expected test result is 12 passing tests. The CLI creates a **new** output directory and refuses to overwrite one. Its summary must show `baseline_halt: false`, `canary_halt: true`, `recovery_halt: false`, and ten expired events. These are expected properties; the [dated record](../../../docs/review-evidence/application-llmops.json) records actual author verification.

Read `runs/incident-01/baseline.json` and `canary.json`:

```powershell
Get-Content runs/incident-01/baseline.json
Get-Content runs/incident-01/canary.json
```

Pause and predict why quality stays 1.0 while the canary halts. Explain which requests enter the quality denominator and which disappear from it. The slow slice has four requests; do not mistake its small count for population evidence.

<details><summary>Reveal the reasoning</summary>

Quality is measured over reviewed ready drafts only. In the baseline, the four slow requests produced two ready drafts and two abstentions. At the 500 ms timeout all four fail, so the two drafts that were ready leave the quality denominator, while the six routine drafts remain good. Coverage falls from 8/10 to 6/10 (below the 0.75 floor) and failures rise from 0 to 4 (above the 0.1 limit), so the canary halts on both the coverage and failure gates even though quality stays 1.0.

</details>

## 3. Reconstruct the monitoring mechanism

Before looking at the implementation, write the expected fields for ten requests, eight ready, two abstained, eight reviewed and eight good. Then, in **your copied** `watch.py`, replace the complete `metrics(rows)` function from your own reasoning. Keep its return-field contract and preserve the supplied tests. Work in three stages:

1. Compute request, ready, reviewed, good, abstention and failure counts. Quality uses reviewed ready; coverage uses every request. Zero denominator returns `None`, not zero or one. Verify with `python -m unittest -v test_watch.WatchTests.test_no_evidence_never_passes`.
2. Add nearest-rank p95: sort latency values and choose index `ceil(.95*n)-1`. Compute total cost, cost per request and cost per good ready. Include failed attempts in cost. Verify `test_watch.WatchTests.test_baseline_units_and_slices`.
3. Run the full suite, then inspect `report()`'s gates. Why is review fraction a separate gate? Do not weaken thresholds to fit your function. Explain why a four-request slice is reported but does not independently release a candidate.

After attempting, compare your function to the reference copy. This is guided construction with worked code available, not an unseen examination. The report fields follow the earlier harness's quality/coverage principles, but add operational review completeness and retention; read the earlier guide for split selection rather than repeating that implementation here.

Follow `safe_event()` next. It serializes a new dictionary with approved fields only. Nested tool responses, credentials and exception objects are dropped entirely. Enum validation also prevents arbitrary strings from being disguised as outcome labels. Numeric validation rejects NaN, infinity, negative values and booleans masquerading as numbers. Labels are trusted reviewer/application inputs in this offline exercise, never self-assessed model statements.

Run `test_watch.WatchTests.test_redaction_drops_nested_unknown_fields` and `test_watch.WatchTests.test_retention_access_and_restart`. Explain the limit: the role parameter assumes a trusted caller, and direct access to the SQLite file bypasses it. The telemetry contract is tested; production authentication/IAM is not implemented.

## 4. Break, diagnose, contain and recover

The CLI deliberately writes a canary manifest with timeout **500 ms**, versus stable **1200 ms**. `traffic()` simulates six 400 ms requests and four 900 ms requests. It simulates timeout behavior and hypothetical cost, not wall-clock provider measurements. It then performs the complete incident procedure; inspect each checkpoint rather than treating a green CLI as sufficient understanding.

| Generated artifact | What you must verify |
|---|---|
| `registry.json`, `active.json` | Hash-addressed complete manifest; final active configuration is restored to 1200 ms |
| `baseline.json`, `canary.json` | Same input schedule/gates; coverage .8 → .6, failures 0 → 4; quality remains 1.0 |
| `rollout.json` | Further rollout halted; application-oncall named; halt persists after recovery |
| `telemetry.sqlite` | Sanitized events expire at seven days; this is logical deletion only |
| `recovery.json` | Fresh replay against the manifest actually read back from disk; all gates pass |
| `incident.json` | Logical timeline, diagnosis, pending review and explicit synthetic evidence kind |
| `runbook-update.md` | New slow-probe/coverage check, owner and no automatic resume |

Reproduce the failure yourself by evaluating `report(traffic(artifact(500)), artifact(500))` in a Python REPL. Repair with 1200, and run `test_watch.WatchTests.test_metrics_keep_failure_denominator` plus the complete suite. Explain why raising a timeout blindly could worsen queue saturation in a real service. This exercise holds concurrency and traffic fixed; live recovery needs bounded probes, backlog and capacity checks.

Now introduce a second fault in your copy: change the coverage denominator from `n` to `len(ready)` when ready exists. Predict which gate loses its meaning, run the denominator test and observe its failure. Restore the original denominator, rerun it and retain the failed and repaired outputs. The author verifier independently catches this mutation and a mutation that serializes raw rows. Do not commit sensitive raw experiments.

Submit your own incident narrative before comparing the generated diagnosis. Include impact, first signal, alternative hypotheses, manifest difference, containment, compatibility decision, recovery evidence and owner/follow-up. The logical-minute timeline is a teaching sequence, not measured detection or recovery time. For a live incident, use actual timestamped observations and avoid inventing a sequence.

## 5. Operational runbook and data policy

Use the [runbook](runbook.md) during the drill. Local retention is seven days, expiry is inclusive at `at <= now - 604800`, and the exercised clock is trusted logical seconds. Application-oncall owns event expiry and verifies its count; the reviewer can inspect sanitized events. Real deployment needs authenticated principals, distinct write/read roles, restrictive filesystem/storage access, encryption, audit and disposal across backups/exports. This CLI supplies none of that infrastructure. Sanitized reports are retained only for this local exercise; production aggregate/report retention requires a separate approved policy.

Neither an ignored directory nor a hash is an access control. SQLite logical expiry is not secure erasure. Do not adapt this lab to real customer records. No raw request payloads are needed to diagnose this fault.

## 6. Independent transfer: a hidden slow-slice regression

Create `slice_gate.py` in your copy, with `slice_reasons(baseline_rows, candidate_rows)` returning reason strings. Integrate its reasons into a new `report` variant without changing the original global gates. Add independent behavior tests and a short release decision.

Use a new synthetic 100-request schedule: 90 routine and 10 slow; all baseline requests are ready, reviewed, good. In the candidate, two slow ready drafts become wrong and every other request stays good. Coverage, cost and latency stay unchanged. Global quality .98 passes .95 and its drop .02 passes .05. Require each slice to have at least eight reviewed ready samples; a quality drop greater than .10 in any eligible slice halts. Missing/undersized baseline or candidate slices must return insufficient evidence, not pass. Never merge incomparable input schedules or label policies to fill a count.

Acceptance: the original global report passes, your slice gate halts slow .8 versus 1.0; unchanged traffic passes; an absent slow slice and seven reviewed slow examples halt as insufficient; unknown labels and raw fields remain rejected/redacted. Provide your test outputs, changed files, decision and review of small-sample limitations. This gate teaches a policy, not statistical significance.

<details><summary>Hint 1</summary>

Group both windows by the bounded slice enum before calculating denominators. Compare the union of slice names so a disappeared slice remains visible.

</details>

<details><summary>Hint 2 and worked reasoning</summary>

Check reviewed ready counts before quality arithmetic. A missing slice cannot have zero regression assigned. For slow, baseline good/reviewed = 10/10; candidate = 8/10; drop = .20, which exceeds .10. Aggregate good/ready = 98/100 still passes. Test the exact .10 boundary with a one-error candidate; account for floating-point arithmetic explicitly, for example by comparing integer counts or using a documented tolerance. Preserve the global unsafe gate regardless of sample count. Explain whether you would require a larger review window before resuming in production.

</details>

Self-study feedback has four essential dimensions: correct metrics/gates, telemetry boundary, operational recovery, and independent explanation/testing. For each, record **demonstrated**, **repair needed**, or **missing evidence**, with a file/test reference. Raw-sensitive-data export, silently resumed failed rollout, ignored unsafe output or fabricated results require repair regardless of other strengths. This is module self-assessment, not a new program certification policy. Disclose AI assistance and explain a small unseen threshold/traffic change in your own words.

## 7. Troubleshooting, cleanup and next constraint

| Symptom | Likely cause → diagnostic action → repair |
|---|---|
| `FileExistsError` | Existing evidence directory → inspect it → choose a new name; preserve prior learner work |
| `ModuleNotFoundError: watch` | Wrong working directory → check location → run tests inside `release-watch` |
| Everything abstains but quality appears green | Zero denominator incorrectly treated as success → run empty/no-ready test → restore `None` and evidence gate |
| Artifact identity changes | Configuration edited → compare registry and manifest → do not substitute a hash string for actual restored content |
| Expiry removes nothing | Boundary/clock differs → inspect event times and retention seconds → use trusted same-unit clock |
| Telemetry database locked | Another process holds it → close REPL/store → retry; do not delete evidence blindly |

No continuing cloud/model costs exist. Preserve your submission elsewhere if needed. From the project directory, resolve the specific generated directory before deleting it:

```powershell
$exercisePath = (Resolve-Path -LiteralPath runs/incident-01).Path
$runsRoot = (Resolve-Path -LiteralPath runs).Path
if ((Split-Path -Parent $exercisePath) -ne $runsRoot) { throw 'Unexpected cleanup target' }
Remove-Item -LiteralPath $exercisePath -Recurse
```

Limitations: fixed synthetic traffic, authored judgments and prices, complete prompt reviews, single operator, no concurrent rollout controller, no automatic cloud alerting, no real provider/model quality, no executable image rollback, no schema/data migration or external effects. Fresh replay proves this local configuration repair only. Final delivery still requires separately reported real-model/deployment evidence and the earlier security controls.

Next constraint: integrate trusted event production and representative semantic review into a whole system. The guided capstone, [W-CAP-01](../../capstone/merchant-support/README.md), does this; its [public evidence brief](../../../assessments/capstone-evidence.md) defines the handover. [Previous: SG-OPS-00 guide](../../../study-guides/application-llmops/README.md) · [Course map](../../../README.md)

## Record application ownership and evidence

Before the checkpoint, complete the [application-governance record](application-governance.md). It adds 45-75 minutes within phase 5 and maps source owners, readers, retention/deletion surfaces, audit access, provider-approval assumptions and incident duties to exercised evidence or explicit gaps. Keep fictional roles separate from actual approvals. Carry the same private record into capstone design/handover rather than writing a second policy document; no organizational/legal compliance or reviewer entitlement is implied.

## Completion checkpoint

**Show it:** stable/canary reports on the same synthetic schedule, the retained rollout halt, restored manifest identity, recovery probes and your independent slice-gate regression. Label authored labels/prices and simulated timing explicitly; a healthy local replay does not establish live-service quality.

**You can now:** calculate the monitored denominators, preserve a rollout halt and explain the recovery evidence. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** complete the [application-governance record](application-governance.md), then connect these controls in the integrated capstone linked from it. Use the root capability prerequisites when deciding whether to proceed.

## Stage defense practice

> [!TIP]
> Read the counts before the percentages. Conditional quality can stay perfect while failures remove useful work from the ready-answer denominator.

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p12--application-llmops-and-incident-ownership) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
