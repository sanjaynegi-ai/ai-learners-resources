# W-CAP-02 — Independent merchant delivery under changed rules

**Can you preserve the invariants when approval, time and order state all change?**

> **Your goal:** Implement a materially different brief and defend the resulting release decision.<br>
> **You need:** The guided baseline and evidence prepared for [review](07-evidence-and-defense.md), with reference use disclosed.<br>
> **Effort:** 12 hours plus the existing shared defense/repair reserve; estimated.<br>
> **You will produce:** Independent migration/code/tests, revised delivery records and before/after reports. **Status:** Draft; synthetic reference and independently reviewed delivery are separate.

Do this before opening the hints. Renaming entities or copying the walkthrough does not demonstrate transfer. Preserve original reference failures/results and disclose assistance. Keep any confidential feedback or unreleased assessment variants outside this public repository.

**Starting checkpoint:** use your own guided baseline, with source/dirty state and evidence inventory recorded. Review the guided evidence with chapter 07 before starting if needed, leaving independent transfer/defense explicitly pending. Return there afterwards with the changed implementation; a preliminary guided review is not final sign-off on this brief.

**Work sequence:** freeze the new applicability/approval contract, plan the schema migration, write boundary tests, implement the change, then evaluate and package it. Preserve the old database and effect history as test inputs in your private workspace. Offline control work requires no real refund or external message; live model/deployment evidence follows the separately authorized delivery route.

## New brief

The merchant needs support for policies with **calendar effective dates** and two distinct supervisor approvals for simulated refunds **above 2000 cents**. Amounts <=2000 still require one different current supervisor. Above the threshold, both supervisors must differ from the proposer and from each other, belong to the same tenant and remain authorized at execution. A supervisor is revoked while a request is waiting. Replace the reference's single-approval schema with an explicit migration; do not silently count duplicate approvals or grandfather unreviewed pending actions.

Add a second synthetic supervisor for merchant A and a supervisor for B through trusted fixture/membership changes. Requests cannot supply their own tenant, role, approval count or effective date. Only the trusted operator sets the business clock; model text cannot choose it. A replacement policy becomes effective tomorrow; the older policy is deleted while an evaluation and pending approval refer to it. Define when queries and actions become stale, what restricted audit data may remain, and how rollback avoids restoring deleted query access. Questions with conflicting or future-only evidence must fail closed under your stated applicability contract.

The read-only order tool must now include the remaining refundable amount from the durable effect ledger, scoped to the caller. An order changes while a proposal is pending. Explain the execution-time source of truth, revalidate remaining amount atomically and preserve idempotency after crash/restart. These changes require materially different state/time/migration reasoning; an extra prompt instruction is insufficient.

Before implementation, carry forward v1 and freeze the [v2 UAT contract](customer-acceptance.md#3-freeze-version-2-before-the-independent-change). Retain the reference's known one-approval failure and new calendar/quorum/migration cases as Fail/Not run until actually exercised. Replace 20 minutes of existing handover/independent reflection with the versioned result/change update; do not add a phase-6 presentation or treat simulated acceptance as real sign-off.

## Required evidence and acceptance fixed before implementation

Submit five revised delivery records, requirement-to-test/evaluation trace, migration/rollback decision, threat model, reviewed cost/queue impact, new runbook amendment, tests and versioned before/after reports. State exact starting revision and dirty changes. Include real-model evaluation and deployment evidence separately from offline tests, preserving final program requirements. Model quality cannot compensate for any trust-boundary failure.

Minimum independent checks:

1. 2000 versus 2001 cent boundary; duplicate/same-person/foreign-tenant/proposer approvals; absent and revoked approvers; no effect while quorum is insufficient.
2. Revocation, amount change, policy expiry/deletion/effective-date change during waiting; stale citations/approval cannot authorize an effect. Show authority decision point precisely.
3. Old DB migrated from reference-v1; pending one-approval actions above threshold remain blocked until new quorum. Done simulated effects stay deduplicated. Demonstrate a compatible backup/migration recovery, preserving deletions and existing effects.
4. Provider timeout/invalid output/cancellation; bounded calls/time/concurrency and spending assumptions remain. Changed rules do not silently reset reservations.
5. Fresh control dataset with development versus held-out separation and applicability/merchant/amount slices; separate retrieval/answer/approval metrics, reviewed labels, denominators and limitations.
6. Package the changed application, preserve actual artifact/configuration, execute smoke/restart/recovery/cleanup in the declared environment, and defend unresolved live deployment/model evidence honestly.

The [existing seven essential dimensions and non-compensable gates](../../../assessments/capstone-evidence.md#submission-and-minimum-criteria) govern this brief without introducing points or credential policy. Use **Demonstrated**, **Needs repair**, or **Not attempted** for each dimension and link actual evidence. Every essential dimension must be demonstrated for the independent brief; security/execution/secrets/evidence failures cannot be averaged away. A self-score is not independent competency verification.

## Staged hints and worked reasoning

<details><summary>Hint 1 — Begin with invariants</summary>

Write the action's business identity, authority decision point and clock source before choosing a framework. Approval records reference authenticated members and immutable action payload/version. Count current distinct eligible members, not historical signature rows.

</details>

<details><summary>Hint 2 — Migration and time applicability</summary>

Store policy effective interval and trusted publication revision separately from chunks. Recheck interval, current ACL and revision before publication/effect. Migration must preserve done effects and existing idempotency identities; do not convert an old single approval into two. Retain a blocked state for pending incompatible actions until a reviewer resolves them.

</details>

<details><summary>Worked decision reasoning, not a copied implementation</summary>

For 2001 cents with two recorded approvals, revoking either supervisor leaves only one eligible approval, so execution must be denied even if the UI says “approved.” When policy evidence is deleted, creating a new model answer does not restore authority for the old action; a new reviewed proposal may be necessary. A database restore from yesterday might restore revoked membership/deleted chunks or forget today's effects. Prefer forward repair/compatible migration with preserved current security/effect records; if that cannot be verified, halt rather than claim successful rollback. The right implementation depends on your stated storage/clock/retention contract and must be tested.

</details>

## Defense and transfer

Explain a changed action end-to-end, write a small validation component without relying on the reference, diagnose an unfamiliar fault, and communicate the release/no-release decision to a simulated support lead. A reviewer should select an unseen change appropriate to the submitted design, such as a different boundary/time or approval eligibility condition; public examples are practice, not secret exam variants. Written/recorded formats are acceptable if they establish the same capability. Disclose AI assistance and demonstrate ownership through explanation and modification, not presentation polish.

Reflection: which original assumption failed first, what did your tests initially miss, and what evidence would change your operating decision? [Evidence review](07-evidence-and-defense.md) · [Route](README.md)

## Completion checkpoint

**You can now:** deliver a materially changed requirement without relying on the reference, diagnose an unfamiliar fault, and communicate a release or no-release decision.

**Show it:** your code, tests, evidence and decision note, with assistance disclosed.

**Next:** add your transfer evidence to the [evidence review](07-evidence-and-defense.md) inventory, then prepare the individual defense in [W-DEFEND-01](../../defense/README.md) (AI-DEFEND-01).
