# Demonstrate useful work and negotiate the next change

QuickCart's support lead sees a green demo and asks, “Can we roll this out to everyone?” Your task is to show what the current integration actually does, expose what it cannot prove, and agree on the evidence needed next. A passing API call is not customer acceptance or evidence of reduced support workload.

**Outcome:** rehearse discovery, scope negotiation, an integration demonstration, a changed requirement and handover. **Prerequisites:** [API delivery](README.md), its [local serving measurements](serving-under-load.md), and your earlier ML/LLM decision notes. **Effort:** 75–105 minutes total, including 15 minutes replacing the existing P10 stakeholder portion of delivery's independent reflection; net addition 60–90 minutes within phase 4. The new portion is 10 reading, 15 discovery/scope, 20 demonstration, 15 impact-plan drafting and up to 30 repair; the reused 15 minutes completes the plan/change response. Capstone follow-up replaces existing delivery-record/reflection work; it adds no phase-6 hours. **Artifact:** a simulated interaction log, demo evidence, versioned acceptance record and adoption/workflow-impact plan linked to the existing five delivery records.

**Starting state:** use your personal QuickCart API copy and saved packaging/serving evidence. This is the phase-4 ticket API, not the later merchant-support capstone. Keep their artifact IDs, environments and evidence separate. The capstone later reuses your delivery reasoning, not this application's database or test results.

**Before execution:** the only executable step uses the existing Python 3.11/uv loopback runner, with synthetic identity, bounded work and automatic server cleanup. It makes no provider, cloud, customer or external messaging call. For a verbal rehearsal a volunteer may play the customer, taking an estimated 20–40 minutes; none is required or promised. Alone, use the written prompts below and label every customer statement and acceptance as **simulated**. Do not invent observed interviews, deployment acceptance or adoption results.

## 1. Discover and negotiate before demonstrating

Create a private `delivery/customer-interactions.md` beside your delivery records. Use this copyable entry for each stage:

```text
Stage / date / artifact checkpoint:
Customer role and participation: written simulation / volunteer role-play
Question and scenario statement:
Fact / assumption / unresolved decision, with owner:
My proposed scope and trade-off:
Simulated response, revised scope and decision state:
Requirement IDs / acceptance version / evidence:
Exact next action and help used:
```

**Written discovery prompt — simulated support lead:** “We want fewer repeated lookups. If the API triages a ticket, can it also approve a refund and send the customer an answer?” Before opening the example, ask five questions: who uses it; what counts as useful work; where authority comes from; how unsupported cases are handled; who reviews failures and owns operations. Add a baseline question: how often does this workflow occur and how long does it take today?

<details><summary>Worked negotiation — simulated</summary>

The current artifact records a synthetic ticket and mock category. It neither drafts a policy answer nor approves or sends a refund. Propose an internal demonstration of authenticated creation, tenant-safe reads, idempotent replay and bounded triage. The simulated lead agrees to inspect those capabilities and asks for later policy/refund integration. Record that as simulated scope agreement, with actual usefulness, staffing and deployment decisions unresolved. Do not change “mock category returned” into “support issue resolved.”

</details>

Retain the rejected “approve and send now” request and your counterproposal. Link the no-LLM alternative from your earlier selection record. This is a real engineering choice about the requirement, not a promise of a separate career pathway or product.

## 2. Show the integration, including a failure

In PowerShell, from your personal `workbooks/python/quickcart-api` package directory after the delivery setup:

```powershell
uv run python delivery/load_probe.py --output results/customer-demo-01.json
```

Choose a new output name for each run so you preserve earlier evidence. The existing runner creates synthetic tickets through real loopback HTTP, invokes the explicit lab triage route, and exercises overload, duplicate requests, cancellation, failure, timeout and recovery. It starts and stops its own server; do not start another server or expose a remote target. Refer to [serving setup and limits](serving-under-load.md) if the command fails. Reading a previous report is allowed, but record its actual date, source and environment rather than claiming a fresh run.

Walk the simulated lead through three pieces of the report: one useful local completion, one rejection/cancellation/failure, and fresh recovery plus cleanup. Explain the attempt/effect counts and why replay is not a new completion. Show the exact source/configuration and workload: this is a one-process host run, not proof of the packaged container, a provider or the eventual capstone.

**Simulated lead:** “The failures are inconvenient. Hide them and show only successful latency.” Draft your response before opening the reasoning.

<details><summary>Worked response and revised scope</summary>

Keep failures in the acceptance evidence. A low successful p95 cannot describe rejected work, a review queue or useful completion for every submitted ticket. Offer the outcome counts, denominators and recovery evidence together, then negotiate supported load or scope. The simulated acceptance is limited to the stated local triage/control demonstration; broad rollout remains an unresolved release decision. Health alone, a polished demo and hidden failed cases are insufficient.

</details>

Save the report path/hash, artifact checkpoint, exact command, observed result, failed/skipped checks and simulated decision in your interaction log. If the runner fails, label the demo failed and repair the cause using its troubleshooting return point; do not replace a failed run with a fabricated success table. No separate slide presentation is required.

## 3. Carry the conversation into the capstone

At `cap-0-contract`, reuse the [canonical five-record pack](../../assessments/engineering-delivery-artifacts.md) and [worked delivery records](../capstone/merchant-support/delivery-examples.md). In `delivery/discovery.md`, replace the earlier single stakeholder reflection with your question/assumption/owner log. In `delivery/acceptance.md`, use the [versioned UAT exercise](../capstone/merchant-support/customer-acceptance.md) instead of an unstructured acceptance paragraph. UAT means **user acceptance testing**: agreed scenarios checked against observable results in a stated workflow/environment. Local technical checks support it; they do not establish actual user sign-off.

At the independent change, the **simulated finance lead** says: “Above 2000 cents, we need two different current supervisors. The new policy takes effect tomorrow.” Reuse the [changed brief](../capstone/merchant-support/06-independent-delivery.md): update requirement IDs, boundary/date tests, migration/recovery, expected review demand and acceptance version **before** changing code. Keep the old results as v1 evidence; they cannot satisfy the new v2 contract. The current reference's one-approval success must be reported as a v2 failure, not grandfathered as acceptance.

In `delivery/update.md`, give the simulated lead a recommendation, affected scope, evidence gaps and exact next decision. Ask for the effective instant/timezone and eligible approvers; do not invent calendar semantics or delivery dates. At `cap-6-handover`, give the operator the current versioned UAT record and pending conditions, then rehearse one failed check and recovery/cleanup from the existing runbook. Record whether a volunteer or your own fresh session actually attempted the instructions. Neither is real customer adoption or independent program grading.

## 4. Plan adoption and workflow impact

Add the following compact section to `delivery/handover.md`, rather than creating a sixth mandatory record. Complete it during the existing W-DELIVERY-01/P10 stakeholder-reflection allocation; do not repeat the same presentation in the capstone.

| Planning field | What your private record must define |
|---|---|
| Eligible users and tasks | Named role/tenant cohort and supported ticket categories; distinguish eligible, invited and active users |
| Baseline | Current manual workflow, task definition and source of timings/errors; propose a comparable pre-change window |
| Observation window | For example, five comparable working days before and after a bounded rollout; justify mix/volume and note learning effects |
| Useful outcome | A supported, safe answer actually used to finish an eligible task after required review; category assignment or opening the tool is usage only |
| Instrumentation | Allowlisted task/session pseudonym, artifact/version, outcome, time to final reviewed completion, review disposition and queue age; no raw prompts/customer content or credentials |
| Denominators and slices | Active/invited and active/eligible; useful/eligible attempts; reviewed/ready; failures, abstentions, unreviewed and tenant/language/topic slices |
| Review demand/capacity | Ready-answer review, abstention/manual work, approvals and rework in items and minutes; queue growth and oldest-item age |
| Ownership | Support lead owns usefulness/workflow; application on-call owns incidents; designated reviewer owns labels; data owner approves access/retention; names may remain unassigned scenario roles |
| Decision and stop rule | Predeclare unsafe/unauthorized output as a stop; retain existing essential gates, review scope/load and seek explicit release approval |
| Evidence state | Planned/unobserved until actually measured; hypothetical arithmetic and simulated feedback labeled as such |

This is an application measurement plan, not authorization to collect real staff/customer data. Real instrumentation needs approved identity, retention and access controls; the fictional roles above do not implement organizational governance. No adoption benefit is claimed by completing the plan.

**Worked calculation — all numbers hypothetical:** 20 staff are eligible, 10 invited and six active. Activation is 6/10 = 60% of invited staff but 6/20 = 30% of eligible staff. Across 100 eligible attempts, 80 drafts are ready and 20 abstain. Sixty drafts are reviewed; 54 are supported/safe, six have unsupported claims, and 45 are actually used to finish the task. Report review fraction 60/80 = 75%, observed supported/safe quality 54/60 = 90%, and useful completion 45/100 = 45%; 20 drafts remain unreviewed. Do not treat the unreviewed drafts as correct. The six unsupported claims trigger the stated stop rule despite usage.

If every ready draft needs two minutes of review and each abstention three minutes of manual work, demand is `80 × 2 + 20 × 3 = 220 minutes`. At 120 available reviewer minutes the deficit is at least 100 minutes before approvals or repair. The 60 completed reviews already consume those 120 minutes. Two-supervisor approval can add further demand; define its denominator separately. Merely generating drafts faster does not remove this workload.

A six-minute manual baseline minus a 30-second draft time is **not** 5.5 minutes of demonstrated saving: final review, waiting, retries, abstention, rework and changed traffic mix matter. Plan comparable end-to-end timing and useful outcomes; this example has no observed time saving. Small, non-random cohorts cannot establish causal business benefit.

## 5. Independent change, repair and reflection

The **simulated operations lead** now halves review capacity and adds a second language, while keeping the same safety gates. Before opening hints, revise your scope proposal, UAT slice coverage, adoption plan and 150–250-word change update. State what cannot yet be accepted and how the operator should handle the review backlog. Reuse your existing technical failure evidence; do not invent a new live experiment or real feedback.

<details><summary>Hints and self-check</summary>

First recalculate demand against capacity. Then check whether qualified reviewers exist for the added language; an untranslated greeting is not language quality evidence. Narrow supported topics, bound admission or defer rollout rather than waive safety. A complete response names the affected requirement/version, visible failed/pending conditions, owner, workflow-impact measurement and next action. Copying the worked negotiation alone is not independent competence.

</details>

**Repair exercise:** a draft handover says “six users adopted it, all outputs were correct, and the customer approved rollout” while referencing the hypothetical calculation. Mark each unsupported assertion, restore invited/eligible/review denominators, retain the unsafe cases and replace approval with “simulated proposal; rollout not accepted.” Keep your before/after paragraph and explain why no technical check can turn fictional sign-off into real acceptance.

**Completion checkpoint:** show the stage log, negotiated scope, integration demonstration including failure/recovery, revised requirement response, versioned UAT/spec/result links, impact plan and operable handover. Record assistance, actual commands and participation mode. All dialogue and sign-off in this exercise are simulated unless a real separately authorized interaction actually occurred; adoption stays unobserved. Save evidence privately; the runner already closes its local resources, and any container cleanup follows the existing delivery runbook.

**Next:** read [Bounded Bedrock delivery](../../study-guides/aws-bedrock-delivery/README.md), then follow its companion worker lab. Use the [delivery completion checkpoint](README.md#completion-checkpoint) for any needed repair. Revisit this record at [capstone discovery](../capstone/merchant-support/01-discovery-and-acceptance.md), change and handover within their existing allocations.

[Previous: measured serving](serving-under-load.md) · [Phase overview](../../README.md#your-learning-journey)
