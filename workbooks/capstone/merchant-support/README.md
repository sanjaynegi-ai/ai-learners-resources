# W-CAP-01 — QuickCart merchant-support delivery

Can another engineer reproduce and operate the merchant-support system you deliver?

> **Your goal:** Integrate grounded answers, trusted order lookup and current approval for a durable simulated effect.<br>
> **You need:** Complete the [RAG, reliability, delivery and operations prerequisites](../../../README.md#ordered-capability-map).<br>
> **Estimated effort:** 24 h guided/reference delivery and evidence + 12 h independent change; 4 h defense/remediation reserve within phase 6, not an extra phase. Details below; estimates, unpiloted<br>
> **You will produce:** A reproducible integrated project, evaluated release decision and independent changed brief.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**QuickCart context:** the fictional commerce platform now needs one integrated support workflow combining policy evidence, trusted order lookup, current approval and a durable simulated refund. Earlier projects taught the mechanisms; this capstone asks you to connect and defend them.

**Starting route:** begin with discovery and acceptance, then follow the named checkpoints below. Keep the sibling retrieval package and relative dependency layout intact in your personal clone. Reuse prior evidence where applicable; do not rebuild every prerequisite or copy its entire application into this project.

**Evidence boundary:** guided reference checks, your independent changed brief, real-model review, deployment evidence and individual ownership are separate gates. Keep pending or denied live checks visible; visual polish or a passing reference suite does not close them.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-CAP-01 · **Status:** Draft guided reference; author local checks only, unpiloted<br>
> **Audience:** Experienced backend engineers completing the Developer path<br>
> **Central question:** Can another engineer reproduce, challenge and operate the complete system you claim to have delivered?<br>
> **Prerequisites:** [permission-aware RAG](../../langchain/02-rag-capstone-workbook/README.md), [safe actions](../../llm/safe-actions/README.md), [versioned evaluation](../../llm/eval-harness/README.md), [delivery](../../delivery/README.md), [AWS](../../aws/bedrock-worker/README.md), [operations](../../operations/release-watch/README.md). Read at need; do not rebuild each prerequisite.<br>
> **Outcome:** Integrate grounded policy answers, trusted order lookup, approval and a durable simulated refund; evaluate, package, recover and hand over with honest evidence<br>
> **Artifact:** Reproducible repository, tests/evaluation, discovery/requirements, diagram/ADRs, threat model, cost sheet, release/incident/runbook/handover, independent changed brief and individual defense<br>
> **Acceptance:** See [requirements](01-discovery-and-acceptance.md), [independent criteria](06-independent-delivery.md) and [delivery evidence gates](07-evidence-and-defense.md); mock-only results do not meet final program requirements<br>
> **Effort:** 24 h guided/reference delivery and evidence + 12 h independent change; 4 h defense/remediation reserve within phase 6, not an extra phase. Details below; estimates, unpiloted<br>
> **Environment:** Windows PowerShell, uv 0.13.1/Python 3.11.13; locked FastAPI 0.142.1, Uvicorn 0.54.0, Boto3 1.43.113; local retrieval package 0.1.0. Docker Linux/amd64 path documented separately<br>
> **Last verification:** 2026-10-15; [author review](../../../docs/c13-implementation-review.md). Real-model review and independent defense remain pending; no graduation/publication claim

</details>

## Route and named checkpoints

This is one evolving project, not a copy of every earlier application. The RAG package is a local declared dependency at `../../langchain/02-rag-capstone-workbook/retrieval-lab`; its reviewed synthetic corpus, ACLs, ranking and quote validation are reused directly. The integration adds a single-process HTTP boundary, asynchronous provider boundary, SQLite approvals/effects, evaluation and operational records. The earlier safe-action and operations lessons supply mechanisms; their standalone demos are not pasted into this application. Complete `src/merchant_support` is an inspectable reference. Guided tasks reconstruct focused functions in a personal copy before comparison.

| Checkpoint | Read/build | Required evidence | Active effort estimate |
|---|---|---|---|
| `cap-0-contract` | [01 Discovery and acceptance](01-discovery-and-acceptance.md) | Scenario facts versus assumptions, frozen requirement IDs and review capacity | 2 h |
| `cap-1-grounded` | [02 Guided application](02-guided-build.md), stages 1–3 | Tenant/role isolation, missing/conflicting evidence and HTTP validation | 4 h |
| `cap-2-approved` | Chapter 02, stages 4–5 | Current approval, deletion/revocation, restart, atomic simulated effect | 4 h |
| `cap-3-evaluated` | [03 Evaluation and failures](03-evaluation-and-failures.md) | Versioned development/held-out control reports, fault/repair and limits | 3 h |
| `cap-4-delivered` | [04 Delivery and live evidence](04-delivery.md) | Reviewed deployment artifact/configuration, smoke/restart, separately authorized real-model run and human review | 4 h including setup; access/download waits vary |
| `cap-5-operated` | [05 Operations and handover](05-operations-and-handover.md) | Incident timeline, halt/recovery, cost analysis, handover and cleanup | 4 h |
| `cap-6-reviewed` | [07 Evidence and defense](07-evidence-and-defense.md) | Integrity inventory, critical gates, disclosure and no-release/release recommendation | 3 h |
| `cap-transfer` | [06 Independent delivery](06-independent-delivery.md) | Two current approvals, changed effective date/deletion and unseen change | 12 h |

The 24 guided hours include about 4 h reading/design, 2 h setup, 11 h implementation, 5 h evaluation/delivery/incident checks and 2 h records/review. The existing five delivery records occupy the records/design activity; do not add their earlier estimate again. The 4 h repair/defense reserve is separate from the 36 h above. Phase 6 also allocates time for course-level defense/remediation and learner-specific gaps; reconcile its remaining 20 h before any timetable promise. A blocked paid/model/account setup can change elapsed time; never claim zero time because a check is pending.

There are no release tags for these checkpoints. They name the expected state and evidence, not historical commits. Save your own changes, lockfile and hashes at each checkpoint. The complete reference is `capstone-0.1.0`; earlier chapter tasks identify exactly which function to reconstruct. Preserve the dependency folder and relative layout when making a personal working copy; alternatively build the container from repository root. Do not copy entire applications into each checkpoint.

## First local run

From repository root in PowerShell:

**Execution requirements:** Windows PowerShell, uv 0.13.1/Python 3.11.13; locked FastAPI 0.142.1, Uvicorn 0.54.0, Boto3 1.43.113; local retrieval package 0.1.0. Docker Linux/amd64 path documented separately. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/capstone/merchant-support
uv sync --locked --python 3.11
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m merchant_support.evaluate --split development --out runs/dev-01.json
uv run --locked python -m merchant_support.evaluate --split heldout --out runs/heldout-01.json
```

Expected properties: 21 tests pass; development has 4/4 correct outcomes, held-out 8/8, zero forbidden retrieval. Both reports say `delivery_decision: NO_RELEASE`. Authored controls cannot establish real-model competence, representative semantic quality or independent ownership. The first authorized real invocation was denied by IAM; [follow-up evidence](../../../docs/review-evidence/capstone-live-attempt.json) preserves that failure separately. Read the chapters before treating this as completion; “run all commands” is not the capstone.

No default model/cloud calls, real customers, actual refunds or external messages occur. Public `demo-*` tokens are synthetic fixtures, unsuitable for real access. The service always uses the offline provider. Paid Bedrock evaluation is a separately gated CLI, never an environment switch accidentally enabling inference in the HTTP service.

Deep explanations remain in [retrieval/grounding](../../../study-guides/retrieval-foundations/permissions-and-grounding.md), [reliability](../../../study-guides/llm-reliability/docs/00-reliable-model-calls.md) and [LLMOps](../../../study-guides/application-llmops/README.md). Framework orchestration is unnecessary for this short flow; extend it only when durable workflow requirements exceed this design.

[Previous: operations](../../operations/release-watch/README.md) · [Course map](../../../README.md) · [Public assessment](../../../assessments/capstone-evidence.md) · [Sources](sources.md)

## Completion checkpoint

**You can now:** trace one supported answer and one approved simulated effect, then explain the missing delivery/ownership evidence. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** start the guided route at [01 — Discovery and acceptance](01-discovery-and-acceptance.md). The independent changed brief (06) comes after the guided checkpoints.

## Stage defense practice

> [!IMPORTANT]
> A correct-looking answer does not authorize a refund. Current trusted membership, policy evidence and approval must still be checked at the execution boundary.

**Pause and decide:** a local reference passes every test, but the real Bedrock attempt is denied. Which delivery claims can you defend, and what is still missing?

<details>
<summary>Show the reasoning and a common misconception</summary>

You can defend the checks and local deployment actually executed, with their synthetic scope and limitations. You cannot claim real-model quality from an IAM-denied request, independent ownership from copied code, or graduation from a test count. A common mistake is treating “the pipeline ran” as evidence that every milestone passed. Keep the denied attempt and unexecuted cases visible, then request only the scoped access/verification needed for the next authorized run.

</details>

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p13--independent-integrated-delivery) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.

**Customer delivery thread:** reuse the [phase-4 rehearsal](../../delivery/customer-rehearsal.md), freeze [versioned UAT cases/results](customer-acceptance.md) at discovery/change, and hand over the current acceptance/impact record. This replaces 40 minutes of existing acceptance/reflection work, with zero net phase-6 addition; all simulated dialogue and unobserved adoption remain explicit.
