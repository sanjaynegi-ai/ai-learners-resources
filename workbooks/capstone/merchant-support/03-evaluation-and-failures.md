# W-CAP-01.3 — Evaluate retrieval, answers and failures separately

**Which report supports a control claim, and which delivery claims remain unverified?**

> **Your goal:** Separate retrieval, answer outcomes and execution failures in a release decision.<br>
> **You need:** [Guided construction](02-guided-build.md) and retained acceptance/fixture versions.<br>
> **Effort:** 3 hours for `cap-3-evaluated`, estimated.<br>
> **You will produce:** Write-once reports, per-case error analysis and a defended no-release recommendation. **Status:** Draft; synthetic reference and independently reviewed delivery are separate.

From the project directory, after [guided construction](02-guided-build.md), run the two commands in the [first run](README.md#first-local-run). Outputs are write-once; choose new filenames to preserve prior results. `cases.json` freezes four development and eight held-out public control cases. Do not edit labels or gates after seeing a candidate to make it pass. The cases are deliberately tiny and reuse public earlier topics; split names preserve the workflow but do not establish unseen, uncontaminated model competence.

Inspect `src/merchant_support/evaluate.py`. Retrieval instrumentation observes candidates before generation, so a failed generation does not erase a retrieval hit. Answer correctness checks expected outcome plus exact reviewed citations. Counts separate ready, abstained, failed, conflict and denied; conflict/denied are visible in per-case records. A production evaluation needs representative categories, calendar policies, reviewer agreement and fresh private hold-out data handled outside this public repository.

**Worked reference:** Held-out controls contain eight requests, five ready, one abstained, one conflict and one denied. Quality is correct ready/ready = 5/5, coverage = 5/8 = .625. Retrieval has seven expected document hits, including two conflicting documents: 7/7 relevant = 1.0. Do not divide by eight requests or call lower coverage a defect when refusal is the labelled correct behavior. The two merchant slices have very different tiny sample counts; report denominators rather than inferring parity from identical ratios.

Local measured latency includes retrieval and provider boundary; it is not live provider latency. Real mode stores actual token usage when returned by Bedrock, with unknown usage remaining null for ambiguity. Costs stay unknown until approved current model/region price inputs exist. Do not fill null with zero. The report always recommends `NO_RELEASE` because it cannot independently verify human review, deployment or ownership; `control_gate: pass` means only the frozen control expectations passed.

## Guided error analysis and fault repair

> [!IMPORTANT]
> A passing control gate describes the frozen public cases. It does not verify real-model semantics, reviewer judgment, deployment or ownership; keep the report's release recommendation and pending milestones visible.

Predict before running: invalid output should abstain without citations; timeout should fail; missing evidence should abstain without a provider call. Run the integration tests, then write a three-row error analysis explaining which enforcement layer and denominator each affects. Add a fourth row where a correct schema contains an unsupported quote.

In your copy of `core.py`, change the provider deadline to an unbounded await and run the timeout test under an external short test-run timeout. Prefer the safe mutation of setting a 0.5 s test delay/2 s gate in your own fault fixture so the exercise itself remains bounded. Diagnose the lost application deadline; restore `asyncio.wait_for` and verify. Do not hang an unbounded real provider call merely to demonstrate a fault.

Run the [provider incident](05-operations-and-handover.md), retain the failed report and write a no-release decision. Include “what evidence would change my decision,” rather than simply listing a failed test. A justified no-release decision demonstrates judgment in this exercise; it does not waive final real-model/deployment requirements.

<details><summary>Self-check and worked reasoning</summary>

Retrieval miss and output rejection are different: a supported source may reach the model, yet its output may be invalid. Generation quality cannot repair unauthorized retrieval. A passing exact-quote check narrows the supported claim surface, but a reviewed claim can itself be outdated or wrong; data governance and effective-date testing remain necessary. Monitoring ready quality alone hides failed requests, which is why coverage/failure counts accompany it.

</details>

## Completion checkpoint

**You can now:** explain a retrieval hit, a rejected answer and a failed request without conflating their denominators. **Show it:** both actual reports, source/label/hash/configuration records, per-case failures and a defended scope limitation. If the provider is scripted, identify that explicitly rather than supplying a model-quality claim.

**Next:** [delivery](04-delivery.md). Its [real-model step](04-delivery.md#real-model-evidence-separate-paid-step) is separately opt-in and paid; this chapter makes no paid call. [Route](README.md)
