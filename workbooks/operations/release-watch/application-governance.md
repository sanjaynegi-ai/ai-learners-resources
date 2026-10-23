# Make ownership and data boundaries inspectable

QuickCart deletes a policy from retrieval, but an earlier refund proposal still contains its citation. Has the data been deleted? Who may inspect the remaining record, and who decides whether it should remain? “We have access controls” does not answer those questions.

**Outcome:** map source/data ownership, readers, retention/deletion, audit access, model/provider approval and incident duties to exercised controls or explicit gaps. **Prerequisites:** this [operations workbook](README.md), its [runbook](runbook.md), and [permissions/grounding](../../../study-guides/retrieval-foundations/permissions-and-grounding.md). **Effort:** 45–75 minutes estimated: 15 reminder reading, 30–45 record creation and up to 15 repair. Optional peer review: 15 minutes, with no reviewer entitlement implied. **Artifact:** one private, versioned application-governance record, later updated in the capstone rather than recreated.

**Starting state:** your personal release-watch copy after its incident exercise, with stable/canary/recovery reports and actual test results. The local operations simulator is separate from the later capstone; it does not hold a production policy corpus or monitor a deployed worker. At this stage, record capstone-specific controls as reference evidence or pending your own execution. Do not copy a seven-day telemetry rule onto every data surface.

**Before execution:** no credentials, paid calls, external messages or deployment are needed. The commands below run existing local synthetic tests. Keep actual owner names, feedback, operational identifiers and approval records outside the public repository; pseudonyms and fictional roles suffice here. Ignored storage is not access control. This is application engineering practice, not legal advice, compliance certification or an organization-wide governance program.

## 1. Build the record before filling in assurances

Create a private `application-governance-v1.md` beside your learning evidence. First copy the identity and responsibility fields below. Keep a short record that an operator can use; link longer decisions and runbooks rather than duplicating them.

```text
Application / source checkpoint / dirty changes / date:
Environment and data: synthetic / live (only if separately authorized)
Record owner and reviewer: fictional role / actual assigned person
Evidence location and exact tested versions:

Source/data owner and publication authority:
Permitted application readers and trusted identity source:
Retention/deletion surfaces, clock and evidence:
Audit readers, writers and storage access:
Model/provider/data-use approval assumptions:
Incident, containment, recovery and resume responsibilities:

For each field: decision/assumption | evidence/test or Gap |
state (local exercised / reference-only / proposed / not implemented) |
role, actual approval state and next action.

Known unresolved release conditions:
Next review trigger / exact next action / help used:
```

**Owner** means the role accountable for a decision, not whoever can edit a file. A data owner decides what may be published, who may read it and what deletion requires; an application publisher implements that decision. A support lead may judge usefulness without authority to approve a provider or retention policy. In this fictional exercise those roles are **proposed/unassigned**, not people who actually approved anything.

Fill the ownership/readers fields first. For every data source, name its synthetic origin, publisher, allowed roles/tenants and trusted identity mechanism. Do not derive permission from model text or assume matching document hashes establish shared access. Record evaluation labels and reviewer feedback as data too, with their own readers and retention assumptions.

**Predict:** a test accepts the string `reviewer` and denies `learner`. Does that prove reviewer-only access in a deployed system?

<details><summary>Reasoning</summary>

No. That tests an interface contract under a trusted local caller. Anyone with direct filesystem/database access can bypass the role parameter. The deployed identity, storage permissions, audit trail and administrative access remain separate controls and evidence gaps.

</details>

## 2. Link decisions to real evidence or explicit gaps

Use this worked mapping as a comparison after your attempt. It is a fictional baseline spanning **two distinct local projects**. Replace reference-only evidence with your own actual commands/results when you run them; never present the whole table as a production approval.

| Record field | Proposed role / decision | Exercised or reference evidence | Remaining gap / approval state |
|---|---|---|---|
| Source/data ownership | Data owner approves synthetic policy revision; publisher maintains provenance and reviewed claims | [Capstone discovery](../../capstone/merchant-support/01-discovery-and-acceptance.md) and [retrieval source lifecycle](../../langchain/02-rag-capstone-workbook/retrieval-lab/knowledge-lifecycle.md) define fixture origin/revisions | No actual commercial source owner or publication approval; proposed roles only |
| Application readers | Same-tenant current members with allowed roles; application establishes scope | [Capstone integration tests](../../capstone/merchant-support/tests/test_integration.py): `test_tenant_candidates_citations_and_order`, `test_no_execution_without_current_approval` | Local bearer fixture/membership, not production authentication; storage operators can bypass application controls |
| Retention/deletion | On-call expires events at seven days; data owner decides all other surfaces separately | [Operations tests](test_watch.py): `test_retention_access_and_restart`; capstone `test_delete_during_provider_and_restart`, `test_telemetry_no_sensitive_strings_and_expiry` | Logical deletion only; source files, retained audit citations, reports, backups, provider copies and physical erasure need distinct decisions |
| Audit/data access | Reviewer may inspect sanitized events; app writes approved fields; operator controls storage | Operations `test_redaction_drops_nested_unknown_fields`, `test_retention_access_and_restart` | No deployed principal verification, IAM, encrypted audit store, reader-access auditing or tamper resistance implemented |
| Model/provider approval | Default uses synthetic provider; release/data owner must approve any live model/data/account/budget combination | [Capstone ADR-04](../../capstone/merchant-support/design.md#decision-records) separates live evaluation; `test_durable_budget_and_halt` exercises local admission/halt | A model ID, SDK permission or successful call is not organizational/model/data-use approval. Actual approval and live evidence remain pending |
| Incident responsibility | Application-oncall contains; release engineer restores compatible configuration; independent reviewer decides resume | [Runbook](runbook.md), operations `test_incident_restores_disk_artifact_and_keeps_halt`, capstone `test_durable_budget_and_halt` | Fictional/unassigned duties, no actual rota or response commitment; local halt file is not deployed traffic routing |

The capstone tests can demonstrate local enforcement, not assignment of real authority. Owner names and approval state must remain separate from test status. A passed test is not a signed approval; a signed approval is not a passed control test. `Gap` is a useful result when it has an owner, consequence and next action.

From your personal `workbooks/operations/release-watch` directory in Windows PowerShell, using the workbook's supported Python 3.13.1 environment:

```powershell
python -m unittest -v test_watch.WatchTests.test_redaction_drops_nested_unknown_fields test_watch.WatchTests.test_retention_access_and_restart test_watch.WatchTests.test_incident_restores_disk_artifact_and_keeps_halt
```

Expect three passing local tests. They use temporary state and synthetic events, open no server and call no model. Save the exact command, runtime, result and skipped checks; attach them to the relevant record rows. Use the existing workbook setup/troubleshooting if imports fail. Do not label an unexecuted OS/runtime as supported.

Later, from your personal `workbooks/capstone/merchant-support` directory after capstone setup, preserving its sibling retrieval package:

```powershell
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -p test_integration.py -v
```

The current reference has 17 integration tests, all offline; SDK checks are stubbed and child cleanup is exercised without network. Read actual output rather than copying a pass. This capstone execution is a later evidence update, not a prerequisite to finish the phase-5 record. Full readiness, live quality, deployment scope and individual defense remain separate requirements. These are existing behavior tests; no new tests are needed merely to assert that a prose field exists.

## 3. Trace deletion through every surface

Append this compact surface inventory to the same record. A versioned citation or hash helps trace a record but does not delete it or establish permission.

| Surface | Current local teaching contract | What the record must still decide |
|---|---|---|
| Source fixtures and current retrieval index | Synthetic source files remain; capstone deletion removes queryable chunks and leaves tombstone state | Who owns original sources/copies and may publish/rebuild; ensure rebuild/rollback cannot restore deleted access |
| Operational event rows | Watch expiry uses trusted logical seconds, `at <= now - 604800`; capstone telemetry uses its application clock | Clock/retention owner, exact boundary and verification; SQL row expiry does not prove secure physical erasure |
| Actions, approvals, effects and audit citations | Capstone keeps restricted SQLite business history, including proposal evidence | No approved real-data retention period; authorize readers and reconcile retention/deletion with the data owner, without silently erasing idempotency evidence |
| Reports, evaluation labels and reviewer notes | Saved evidence is separate from the live index/event rows | Readers, retention/disposal, exports and private feedback; expiring events does not expire reports |
| Backups, caches, database pages and restored snapshots | No production disposal or restore-control implementation is claimed | Owners, restore test, current revocation/deletion state and residual-copy disposal |
| Provider prompts, logs/traces and remote copies | Default exercise exports no data to a live provider | Before any live route: approve fields/model/region/retention assumptions and verify provider-specific controls; local cancellation or deletion cannot prove remote erasure |

For example, the operations test appends events at logical times 100 and 101. At `now=604900`, the cutoff is 100, so exactly the first event expires. At 604901 the second expires. Those are seconds, not dates or a legal retention recommendation. The capstone's seven-day telemetry expiry is a separate method; retaining action history is deliberate under a synthetic contract, not proof that real deletion obligations are satisfied.

**Repair exercise:** someone writes “all customer data and logs are deleted after seven days; reviewer access is enforced; the provider is approved.” Mark each overclaim and replace it with the precise exercised boundary, residual surfaces, fictional owner and unresolved approval. Keep the before/after paragraph. Do not remove useful controls merely because organizational decisions are pending.

## 4. Transfer the record into the capstone

The capstone [design/threat decisions](../../capstone/merchant-support/design.md) should point to your existing private record and update its version with actual sources, identities, approval ledger, live-route assumptions and evidence. Reuse the [customer handover](../../delivery/customer-rehearsal.md) owner/impact section. Do not create a second competing governance document or a new compulsory organization-wide framework.

**Independent change:** a policy owner requests deletion while a pending approval and exported evaluation report still cite it, and a restore from yesterday is proposed. Before opening hints, update the surface inventory, permitted readers, retention assumptions, incident decision and release conditions. State what you can deny/delete now and what still needs a data-owner decision. Require an explicit check that current revocations/deletions survive recovery; old passing results do not establish it.

<details><summary>Progressive hints and self-check</summary>

First distinguish query access from restricted audit history. Then inspect saved reports/copies and pending action validity. A restore that resurrects access or loses effect identities is unsafe even if health checks pass. Preserve permitted synthetic evidence and use the known halt/manual-review path while unresolved decisions are escalated to fictional responsible roles. A complete record identifies each surface, exercised check or gap, approval state and exact next action. A legal/compliance claim cannot be substituted for missing implementation evidence.

</details>

## Completion and next step

Show your private versioned record with all six governance fields, surface inventory, exact test/report references, actual versus reference-only status, fictional versus actually assigned roles, failed/untested boundaries and independent changed-case response. A peer may review it for 15 minutes if available; solo review remains self-assessment, with no independent grading or actual approval implied. Record help used and one unresolved condition that would block a real release.

If a row only names an owner, add its decision/evidence/gap. If a row only links a test, add scope and responsibility. If expiry is described as universal deletion, return to the surface inventory. If a claim depends on live provider or deployment behavior, keep it pending and use the separately authorized route. Do not execute paid operations to fill a planning record.

Save your evidence privately; tests clean their temporary databases. No new service, account or continuing cost was created. Preserve the original incident records, and use the existing [cleanup instructions](README.md#7-troubleshooting-cleanup-and-next-constraint) for any separately generated local runs.

**Next:** [connect these controls in the integrated capstone](../../capstone/merchant-support/README.md), updating this same record during design and handover. Return to the [operations checkpoint](README.md#completion-checkpoint) if a local check still needs repair.

[Previous: operations runbook](runbook.md) · [Phase overview: course map](../../../README.md#ordered-capability-map)
