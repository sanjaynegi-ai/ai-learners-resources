# Fictional QuickCart delivery records — worked examples

**Scope:** Simulated worked records. No actual interview, stakeholder approval, deployment acceptance, staffing promise or independent competency verification occurred. Replace assertions with your actual evidence. The [five-record evidence pack](../../../assessments/engineering-delivery-artifacts.md) remains canonical for the activity.

## 1. `delivery/discovery.md`

“Support agents need an internal way to find applicable merchant policy and prepare a small simulated refund for review. Current lookup and approval workload has not been measured. Scenario facts: two merchants; current tenant/role isolation; all effects simulated. Assumptions to validate: 20 requests/min and 10 reviews/min capacity. Unresolved: real identity provider, applicable policy dates, production retention, authorized model/account/budget and final deployment scope. Support lead owns usefulness/capacity, data/security owners own policy/identity, release owner owns spending/delivery.” Ask the seven concrete questions in chapter 01 rather than recording invented customer answers.

## 2. `delivery/requirements.md`

“Reference-v1 uses CAP-AUTH through CAP-DELIVER in chapter 01. The trigger is an authenticated synthetic support request. It produces a reviewed quote or an explicit abstention/conflict/denial/failure. A read-only order lookup is tenant-scoped. Proposals carry typed cents and evidence; a different current supervisor must approve before an atomic local simulated effect. Negative cases are first-class evidence. Non-goals: real customer messaging/refunds, broad legal-policy interpretation, public internet service, distributed approvals and model training. Real identity/time-effective policy/deployment acceptance remain unresolved.” Link each ID to its actual test/report in your submission.

## 3. `delivery/acceptance.md`

“Simulated exchange: support lead requests answers to every ticket; engineer explains unsupported evidence must abstain. At hypothetical 12 review arrivals/min and 10 service/min, backlog grows 2/min before approval work. Proposed revision: restrict initial topics, measure ready quality and coverage separately, and never waive tenant/execution gates. State: scenario proposal, not confirmed acceptance. Freeze reference controls before runs; retain failures. Do not change expected labels to turn a failing model into a passing release.”

Replace the generic acceptance paragraph with [versioned UAT cases/results](customer-acceptance.md). The local reference can pass v1 controls while failing the v2 two-supervisor rule; retain both results, pending workflow/live evidence and simulated sign-off separately. Reuse the [earlier interaction log](../../delivery/customer-rehearsal.md), rather than repeating a new presentation.

## 4. `delivery/update.md` — worked changed-requirement update

“The new merchant rule changes CAP-APPROVE-01 and policy applicability: refunds above 2000 cents require two distinct current supervisors, and a replacement policy takes effect tomorrow. The reference currently stores one approval and uses a logical fixture clock, so it does not meet either change. Its existing negative tests demonstrate revocation and stale-evidence denial; those controls must remain during migration.

I recommend a versioned approval migration that preserves completed effect identities and blocks incompatible pending actions until the new quorum is met. We also need a trusted calendar clock and effective intervals on policies, with tests at the date and amount boundaries. Deleting an old policy must invalidate retained citations and pending actions without reintroducing access during rollback. Existing passing tests alone cannot verify this changed behavior.

The second approval may increase review demand; staffing and elapsed delivery effort remain uncertain until the changed workflow is measured. No real-model or cloud execution is implied by the current local reference results. Please decide the policy timezone/effective instant, audit-retention rule and acceptable review capacity before a live release is proposed. I will retain the no-release recommendation until the changed integration, migration/recovery, semantic review and deployment evidence are inspected.”

This is a simulated draft for learner analysis, not a sent message or real request awaiting response.

## 5. `delivery/handover.md`

“Operator: application-oncall; reviewer: a separate authorized reviewer, both unassigned scenario roles. Starting artifact: capstone-0.1.0 with source/lock/retrieval/image/config hashes from the actual execution record; working-tree differences must be recorded. Setup and verification are in README/chapter 04, operations/cleanup in chapter 05. The HTTP service uses synthetic fixtures and stays offline; paid inference is a separate explicit CLI with short-lived AWS profile and preflight. No keys belong in this pack.

Reference local checks must be reproduced in the recipient's environment. Healthy `/health` is not evidence of useful work. Inspect evaluation counts, current approval/policy decisions, admission ledger, provider failures and incident halt. Preserve the known artifact/configuration; never restore deleted/revoked access blindly. The incident command records failure, halt, isolated recovery and runbook amendment. A real external effect needs downstream idempotency/reconciliation beyond this local transaction.

Known gaps: real identity/TLS, calendar policy semantics, multiple-worker scaling, production retention/backup verification, real-model human review, final deployment-scope acceptance, independent changed implementation and individual defense. Local packaging and reference results do not authorize release. Costs remain hypothetical until official price and actual usage are reviewed. Stop/clean dedicated containers and volumes only after preserving necessary synthetic evidence.”

Acceptance exercise: ask a reviewer or fresh self-study session to run only from this handover. Record exact attempted commands, failures, skipped/live checks and help. A self-walkthrough is author validation. Explain what decision you could not responsibly make without the unresolved sources.

[Route](README.md) · [Design/threat decisions](design.md) · [Evidence review](07-evidence-and-defense.md)

In the handover, reuse the earlier [adoption/workflow-impact plan](../../delivery/customer-rehearsal.md#4-plan-adoption-and-workflow-impact), update its source/version/owners and retain planned/unobserved status. This replaces the generic stakeholder reflection inside the existing five-record allocation; the hypothetical usage, quality and review-capacity numbers are not business outcomes.
