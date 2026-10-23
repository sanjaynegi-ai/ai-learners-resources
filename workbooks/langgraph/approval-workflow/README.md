# W-GRAPH-01 — Durable approval and recovery

A workflow resumes after a crash. Is its saved approval still valid?

> **Your goal:** Persist, approve and recover a workflow without trusting stale authority or duplicating a simulated effect.<br>
> **You need:** Read [stateful orchestration](../../../study-guides/stateful-orchestration/README.md) and complete safe-action/Python prerequisites.<br>
> **Estimated effort:** 20 min reading, 50 min guided, 25 min fault diagnosis, 60–90 min independent extension/defense; estimates.<br>
> **You will produce:** Restart/crash evidence, current-approval checks and a defended quorum extension.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Project boundary:** start a personal copy of this independent `approval-workflow` package. Preserve the previous controls/action projects rather than merging their environments. `approval-v1` names the teaching state, not a published Git tag.

**Study route:** inspect start/wait/approve/resume across processes, predict revocation and crash recovery, then integrate the two-approval extension. Its helper checker alone cannot establish durable waiting, migration or replay correctness.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-GRAPH-01 | **Status:** Draft offline reference, unpiloted<br>
> **Prerequisites:** [SG-GRAPH-00](../../../study-guides/stateful-orchestration/README.md), [safe actions](../../llm/safe-actions/README.md), Python packaging/tests. [W-LC-14](../../langchain/01-learning-workbook/14-langgraph-and-langsmith.md) is an optional introduction.<br>
> **Question:** Can you resume after approval or a crash without trusting a resume payload or duplicating an effect?<br>
> **Effort:** 20 min reading, 50 min guided, 25 min fault diagnosis, 60–90 min independent extension/defense; estimates.<br>
> **Artifact:** Saved workflow, CLI snapshots, restart/crash regression evidence, independent quorum integration and a sequential/graph decision.<br>
> **Environment:** Windows PowerShell, uv, Python 3.11.13; LangGraph 1.2.15, checkpoint-sqlite 3.1.2; exact transitive lockfile included. No provider, real payment, external account or continuing cost.

</details>

## Starting checkpoint and setup

`approval-v1` is complete reference code in `src/approval_workflow/workflow.py`, with an unfinished independent exercise. Use a private copy to experiment; preserve existing learner work. The synthetic QuickCart credit is a SQLite effect row, never a real refund. Initial installation needs internet or cached wheels.

From repository root, in PowerShell:

**Execution requirements:** Windows PowerShell, uv, Python 3.11.13; LangGraph 1.2.15, checkpoint-sqlite 3.1.2; exact transitive lockfile included. No provider, real payment, external account or continuing cost. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/langgraph/approval-workflow
$env:LANGSMITH_TRACING = "false"
$env:LANGCHAIN_TRACING_V2 = "false"
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run approval-workflow start --request R1
uv run approval-workflow inspect --request R1
uv run approval-workflow approve --request R1 --person supervisor
uv run approval-workflow resume --request R1
uv run approval-workflow resume --request R1
```

Each CLI command is a separate process. Start stops at the approval node with no effect; after a recorded decision, resume completes. Repeated resume leaves exactly one effect. `inspect` shows saved state, pending nodes and the local effect ledger. Script exit 0 means execution returned; inspect status to distinguish waiting, denied and completed. Ten tests pass, including crash/restart recovery. Use a new request ID or new directory for a new scenario, not deletion of earlier evidence.

## Build by inspecting the boundaries

Read `State`, then `Application.__init__`, `validate`, `approval` and `execute`. Sketch the early denial and validate → approval → execute → END transitions. State stores request ID/status only; request amount/tenant/requester and approval identity come from trusted SQLite application records. The CLI's selectable synthetic identity is not real authentication. A service would need authenticated sessions, tenant-bound thread access and least-privilege operator commands.

`SqliteSaver` persists checkpoints in `results/run/checkpoints.db`. Authority and effect records live in `authority.db`. A checkpoint is not an approval and does not share a transaction with the effect ledger. `approval()` calls interrupt with an inspectable request; resume data is ignored as authority. `execute()` rechecks current requester and approver identity/role/tenant and rejects self approval.

The graph allows at most eight supersteps per invocation by default; the bounded-transition test deliberately sets one. This is not a wall-clock timeout or an approval expiry. Waiting is persistent, not a worker sleeping forever. No unbounded retry loop or live provider is present. Production review expiry and capacity remain design work.

## Predict and run the faults

**Revocation:** Use R2, start, approve, then revoke the supervisor before resume:

```powershell
uv run approval-workflow start --request R2
uv run approval-workflow approve --request R2
uv run approval-workflow revoke --person supervisor
uv run approval-workflow resume --request R2
```

Predict the final status and the number of R2 effects before you run the last command.

<details><summary>Reveal the expected result</summary>

Denied, with no R2 effect: the recorded approval no longer counts once the approver is revoked. Fixture initialization uses INSERT OR IGNORE and cannot restore revoked membership.

</details>
 Diagnose current registry state rather than changing the role check to make the command pass. To rehearse an independent authorized path, use a new isolated `--directory results/another-run`; do not silently repair real revoked authority.

**Forged resume:** The regression test passes a payload claiming approved/supervisor without a recorded decision. It must still deny. The graph's Command is a wake-up, not authorization.

**Crash after commit:** The test sets `crash_after_effect`, resumes, and observes RuntimeError after one committed effect. It closes/reopens the application, revokes the supervisor, and calls recover. Recovery reports the already completed fact and keeps one effect. A late revocation cannot erase an earlier commit. For a manual drill in your private copy, set this fault flag immediately before resume; after the simulated failure, run `approval-workflow recover`. Never rerun submit with a different amount under the same immutable ID.

**Repair and regression:** In your learner copy, temporarily bypass the final current-approval check. Run the forged/revoked tests, observe failure, restore the check and rerun all tests. The author verifier performs this mutation in a temporary copy. Unsupported state, bool/out-of-range amounts, wrong tenants, invalid approvers and immutable-request conflicts are tested separately.

## Compare with the smaller solution

`Application.sequential()` calls the same validate/execute logic with an already recorded approval. Its test demonstrates the same effect/policy semantics without graph orchestration. It cannot itself wait for review across processes; adding that needs an explicit queue/state machine. Submit a 150-word decision choosing sequential code or LangGraph for (a) an immediately authorized lookup and (b) an hours-long supervisor review. Do not claim the framework creates policy or external exactly-once effects.

## Independent extension: two current approvals

Change the brief: credits over 500 need two distinct current same-tenant supervisors, both different from requester. Add a second synthetic supervisor. Implement `exercises/quorum.py`; the records passed into this helper must come from trusted current identity state, never resume/model content.

```powershell
uv run python exercises/check_quorum.py
```

The starter intentionally stops. Then migrate approvals from one-row-per-request to multiple request/approver records, integrate quorum at execution, and test 500 versus 501, duplicate signatures, foreign tenant, requester-as-approver, revocation of either signer, restart before second approval, and crash/replay after the effect commit. Include proposal identity/version so changing an amount cannot reuse old approvals. Preserve completed effects as historical facts; do not issue another effect to repair a graph checkpoint.

<details><summary>Hints and public reasoning</summary>

Use unique request/approver keys; count a set of eligible current IDs rather than rows. Re-read identity at execution. Keep the <=500 path at one approval. The public `quorum_reference.py` and `check_quorum.py --reference` demonstrate counting only; they are not a durable integration solution. Your migration, graph waiting behavior and restart tests are required evidence.

</details>

Acceptance: your checker passes, integrated tests demonstrate the changed threshold and persistence/revocation cases, and you explain the new waiting path plus rollback/migration implications. Disclose AI assistance and defend an unseen revoked-signer change. Public reference execution alone does not prove ownership.

## Troubleshooting, operations and cleanup

| Symptom | Diagnose / repair |
|---|---|
| Still waiting after start | Expected interrupt; record a trusted decision before resume |
| Denied after approve | Inspect current active role/tenant; a recorded decision is not perpetual authority |
| RuntimeError after effect | Inspect durable ledger, then recover the same thread; never create a new action key to retry |
| GraphRecursionError | Inspect saved next/state and topology; bounded execution is working, not permission to disable the cap |
| Wrong saved thread | Verify request/thread identity and storage directory; thread ID is not an access token |

Checkpoint files contain serialized trusted workflow data. Do not load untrusted checkpoint uploads or expose raw SQLite files to users. Local inspect prints synthetic ledger values; production observation must redact sensitive payloads and restrict access. No hosted traces are sent.

This is a single-worker SQLite teaching design. External payments need an outbox, external idempotency keys and reconciliation; distributed claiming, real auth, encryption, approval expiry, backup retention and deployment are not supplied. The simulated crash is a deterministic exception at a chosen boundary, not a power-loss/disk-corruption test.

Close the process before cleanup. Preserve private evidence and verify Get-Location, then remove only generated `results` and `.venv` from this project. Removing results deletes both checkpoint and authority/effect files; it is a fresh fixture start, not recovery or production rollback. Restore previous tracing environment settings if needed. [Course map](../../../README.md)

## Completion checkpoint

**You can now:** explain checkpoint versus authority/effect state and demonstrate bounded restart without a second simulated effect. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** read [Tool Interfaces](../../../study-guides/tool-interfaces/README.md), then compare the SDK loop and MCP boundaries in its linked exercises. Keep current authority, workflow state and protocol transport as separate responsibilities.

## Stage defense practice

> [!IMPORTANT]
> A checkpoint remembers workflow state; it does not confer current authority. Recheck the actor, approver and payload before a consequential effect.

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p07--stateful-orchestration-and-recovery) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
