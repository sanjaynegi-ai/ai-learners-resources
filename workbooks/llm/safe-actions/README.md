# W-LLM-ACT-01 — Safe actions: durable intent and idempotent effects

**How do repeated proposals and uncertain external outcomes become a controlled action?**

> **Your goal:** Trace trusted approval, durable intent and idempotent dispatch under explicit assumptions.<br>
> **You need:** [Direct-provider lesson](../refund-drafts/README.md) and [Reliable Drafting](../reliable-drafting/README.md).<br>
> **Effort:** 20 minutes reading, 50 guided, 25 fault drills and 45 independent work; estimated.<br>
> **You will produce:** Message/action traces, repaired faults, an independently tested daily cap and a design note. **Status:** Draft; unpiloted, evidence limits remain explicit.

**Starting point:** QuickCart support actions have consequences, so this separate package uses fake email/credit services and synthetic approval records. Keep its environment and temporary state separate from prior projects. No real email, payment or account mutation is required.

**Study route:** Trace one proposed action through validation, policy, approval, durable recording and dispatch. Predict duplicates and timeout-after-effect behavior, then test the two faults and daily-cap requirement. Distinguish provider calls from unique effects.

<details>
<summary>Reference: unit identity, versions and historical verification</summary>

> **Unit ID:** W-LLM-ACT-01 · **Capability:** AI-RELIABLE-01 (also supports AI-TOOLS-01)<br>
> **Audience:** Experienced backend engineers who have completed [W-LLM-API-01](../refund-drafts/README.md) and [W-LLM-REL-01](../reliable-drafting/README.md)<br>
> **Central question:** A model proposes "send this reply" or "issue this credit". What has to happen in your code so the action is allowed, correct, recorded, and performed once, even when the model repeats itself, the external service times out, or your process crashes?<br>
> **Effort:** Reading 20 min; guided walkthrough 50 min; fault drills 25 min; independent daily cap 45 min. Editorial estimates<br>
> **Artifact:** Your predictions next to the demo output, two diagnosed fault drills, a daily credit cap passing its acceptance check, and a short design note<br>
> **Status:** Draft. 12 tests, 5 source mutations, both drills and the exercise check author-verified; offline fakes only; no learner pilot<br>
> **Environment:** Windows PowerShell, uv 0.8.3, Python 3.11.13; Pydantic 2.13.5 and the standard library's `sqlite3`; no network or cost

</details>

[W-LLM-API-01](../refund-drafts/README.md) only drafted text for a person to send. Here the model proposes **actions with consequences**: emailing a customer, crediting money, escalating a ticket. The [offline controls lab](../../reliability/offline-controls/README.md) showed trusted approval and an idempotent local ledger. Its code notes that real systems "also need provider reconciliation/outbox". This unit builds that part: untrusted tool-call arguments, a durable outbox, and external services that may time out *after* doing the work.

**Intuition:** treat a tool call like an untrusted payment instruction. Check records and authority, durably record intent and use a stable external operation key. The analogy depends on the external system honoring that key for the required retry period. Whether a bad proposal came from a mistake or adversarial input does not change the application's enforcement responsibility.

> [!IMPORTANT]
> The fake services honor idempotency keys. One recorded effect under those assumptions is not a universal exactly-once guarantee: real integrations need an explicit key-retention and reconciliation contract.

## The path of one action

| Step | Where | Trust | What it prevents |
|---|---|---|---|
| 1 Proposal | `boundaries.FakeProposalProvider` | **Untrusted**: tool name and JSON argument text from the model | — |
| 2 Registry | `tools.TOOLS` | Trusted | Tools that do not exist ("refund_everything") |
| 3 Strict arguments | Pydantic `strict=True, extra="forbid"` per tool | Trusted schema | Wrong types; smuggled `approved_by` or `tenant` fields; amounts over the hard limit |
| 4 Role and business rules | `tools.*_check`, tenant-scoped queries | Trusted records | Other tenants' tickets and orders; credits larger than the order |
| 5 Approval rule | `needs_approval`, `executor.approve` | Trusted approvals table | Large credits without a *different* supervisor in the same tenant |
| 6 Durable intent | `store.record_action` in one `BEGIN IMMEDIATE` transaction | Trusted | Lost decisions on crash; duplicates (content-derived idempotency key) |
| 7 Dispatch | `executor.dispatch`, the outbox | Trusted | Double effects on retry: the action key is the external idempotency key |
| 8 External effect | `boundaries.FakeService` | External system | — (it honors idempotency keys, like payment APIs that accept an `Idempotency-Key` header) |

## Setup and verify

From `workbooks/llm/safe-actions`:

**Before running:** use your personal package copy in PowerShell with Python 3.11 via uv. Recorded checks used uv 0.8.3, Python 3.11.13 and locked Pydantic 2.13.5. Synchronization may download dependencies. Demo/tests use temporary SQLite databases and fake services: no real email, credit or account operation occurs. Their temporary state is cleaned automatically; preserve your source and evidence separately.

```powershell
uv sync --python 3.11
uv run python -m unittest discover -s tests -v
uv run safe-actions
```

**Expected:** `Ran 12 tests ... OK`. The demo's last two lines read `Real-world effects: 1 email sent, 2 credits issued (email service saw 3 calls, credit service 3).` and `Every recorded action happened exactly once, despite a timeout after applying, an error and a crash.`

## Walkthrough: predict, then read the demo

**Before running the demo, predict the outcome of each proposal in part 1.** Then run it, and read the matching code.

**Part 1, proposals (observed):**
- Normal reply: `queued`.
- The same reply proposed again with a new `call_id`: `duplicate ['already_queued']`.
- Unknown tool: `rejected ['unknown_tool']`.
- Arguments with `approved_by` and `tenant` added: `rejected`, both fields `extra_forbidden`.
- Amount sent as the string `"1500"`: `rejected ['invalid_argument:amount_cents:int_type']`.
- A credit on another tenant's order: `rejected ['order_not_found']`.
- Another tenant's agent acting on this ticket: `rejected ['ticket_not_found']`.
- A provider timeout followed by a valid proposal: `queued`.
- A 30.00 credit: `pending_approval`.

<details><summary>Why each one</summary>

- **Duplicate:** the idempotency key is a hash of tenant, ticket, tool and *canonical arguments*, not the provider's `call_id`. A model asked twice, or a retried request, proposes the same action with a new `call_id`. Content-derived keys recognize it.
- **Smuggled fields:** the arguments are model output. If the schema ignored unknown fields, a successful prompt injection could not grant approval *here*, because approval comes from the approvals table, but it would hide the attempt. Forbidding extras makes the attempt visible and rejected.
- **Tenant:** every lookup is scoped by the authenticated principal's tenant. "Not found" is the same answer for "absent" and "belongs to someone else".
- **Approval:** credits over 20.00 wait in `pending_approval` and are not in the outbox until a *different* supervisor of the *same* tenant approves.

</details>

**Part 2, approval (observed):** the requester approving their own credit returns `False`; supervisor `lead-a` approving it returns `True`.

**Part 3, dispatch under failure (observed):**
- First pass: `done=1, retry_later=2`. The email timed out *after* being sent; the second credit got a 503.
- Second pass: crashes after the email service applied the reply, before the database recorded it.
- After a restart (only the database survives), the third pass finishes both: `done=2`.
- Result: **1 email and 2 credits**. The email service saw 3 calls for one effect.

<details><summary>Why it is exactly once</summary>

The action row is written **before** any effect, in the same transaction as the decision, so a crash before dispatch loses nothing. The dispatcher sends the **same action key** as the external idempotency key every time. When the email service timed out after applying, our retry carried the same key, and the service returned the original result without sending again. When we crashed after the effect, the row was still `queued`, so the restarted dispatcher sent it again, harmlessly. This is **at-least-once delivery plus idempotent receivers = effectively once**. It depends on the external service honoring keys; for one that does not, you need reconciliation (read back its state) instead.

</details>

## Break, diagnose, repair 1: the idempotency key from the wrong field

In `executor.py`, change the key line to include the provider's call ID:

```python
key = idempotency_key(principal.tenant, ticket_id, spec.name, {**payload, "call": proposal.call_id})
```

Run the demo and the tests. **Observed:** the repeated reply is now `queued`, not `duplicate`, and the summary reads **2 email sent**: the customer receives the same message twice. The demo's own verdict *still* says "exactly once", because the duplicate is now a separate, legitimate-looking recorded action, so your consistency checks cannot see it. `test_duplicate_proposals_with_new_call_ids_record_one_action` fails. Restore the line and rerun.

## Break, diagnose, repair 2: marking done before doing

In `dispatch`, add `store.finish(key, "done", "assumed")` just before the `try:` that calls the service. Run the demo and the tests. **Observed:** only **1 credit** is issued instead of 2, and the demo prints `MISMATCH`. The 503 on the large credit left a row already marked `done`, so it was never retried: the effect was silently lost. Four dispatch tests fail. **Diagnosis:** record intent before the effect, and completion only after it. Restore and rerun.

## Independent exercise: a daily credit cap

Finance limits goodwill credits to 60.00 per tenant per day. Implement `check_daily_cap` in `exercises/daily_cap.py`, following its docstring, and pass it to `propose_and_record(..., extra_checks=(check_daily_cap,))`. The trap is in the requirement: a *replay* of an already-recorded credit must still come back as `duplicate`, not be rejected by the cap.

```powershell
uv run python exercises/check_daily_cap.py
```

**Expected:** `daily_cap: daily cap checks passed...`. The untouched starter raises `NotImplementedError`; `--reference` runs the inspectable reference.

<details><summary>Progressive hints</summary>

1. Return early for other tools.
2. Compute the idempotency key the executor would compute; if `store.action(key)` exists, this is a replay, so return `[]`.
3. `json_extract(args, '$.amount_cents')` sums amounts in SQLite; count every status, because a `failed` credit may still have been applied.

</details>

<details><summary>Worked reasoning, and the race you should name</summary>

The cap is a business invariant across many requests, so it reads trusted, durable state, never the model's arguments beyond the requested amount. Replays must not count, or a harmless retry would be wrongly rejected. **Name the remaining race in your note:** the check runs *before* `record_action` opens its transaction. Two simultaneous requests could each see 50.00 spent and each add 10.00. The fix is to run the check and the insert inside the same `BEGIN IMMEDIATE` transaction, or to keep a per-tenant, per-day total row updated in that transaction. Explain which you would choose and why.

</details>

## Completion evidence

- [ ] `uv run python -m unittest discover -s tests -v` shows 12 passing tests on your restored copy.
- [ ] Your predictions for part 1 beside the observed decisions.
- [ ] Both drills: output, diagnosis, repair; for drill 1, explain why your own verdict line did not catch the duplicate.
- [ ] `exercises/check_daily_cap.py` passes on **your** implementation; disclose any use of the reference.
- [ ] A design note of about 200 words: for a new tool `cancel_order`, list its argument schema, business checks, approval rule, idempotency key fields, and what the dispatcher does when the order system times out.

**Reflect:** which side effect in a system you work on today has no idempotency key? What would a timeout after applying do to it?

## Troubleshooting

| Symptom | Likely cause | Diagnostic and repair |
|---|---|---|
| `PermissionError: [WinError 32]` deleting a temp folder | A test or script left the SQLite file open | Close the `Store` in `finally` or `tearDown`; Windows cannot delete open files. |
| `database is locked` | Two connections writing at once in your own experiment | Keep transactions short; `BEGIN IMMEDIATE` waits for the lock up front. |
| A duplicate proposal is queued twice | The key includes something that changes per proposal | Derive keys from tenant, ticket, tool and canonical arguments only. |
| An action stays `queued` forever | The service keeps failing below `max_attempts` across passes, or no dispatcher runs | Check `attempts`; after 3, the action becomes `failed` with `needs_reconciliation`. |

## Limits and next step

Cleanup: the demo and tests create their SQLite databases in temporary directories that are removed automatically, and nothing keeps running. Remove your personal `.venv` when finished, after checking its resolved path.

The services are fakes that honor idempotency keys perfectly. Real ones keep keys only for a limited time, may not support them at all, and may need read-back reconciliation; check each API's documentation. There is one dispatcher process; several dispatchers would need row claiming (`UPDATE ... WHERE status='queued'` with ownership) to avoid sending in parallel. The proposal provider is a fake; a real tool-calling adapter would map provider tool-call output into the same `ToolCall` shape, following the provider-boundary pattern in W-LLM-API-01. Approvals here are table rows; real ones need authenticated approvers and an audit trail.

**You can now:** take an untrusted tool call through registry, strict arguments, tenant-scoped business rules and approval to a durable, idempotent effect, and explain why a timeout after applying causes no second effect. **Show it:** both drills, your daily cap and the design note.

**Next:** [W-RELIABILITY-01 — offline controls](../../reliability/offline-controls/README.md), the next unit in the course map's AI-RELIABLE-01 row, tests tenant isolation, current grants and a local ledger at the trust boundary. [W-LLM-EVAL-01 — versioned evaluation](../eval-harness/README.md) follows it. Return to the [course map](../../../README.md#ordered-capability-map).

**Sources:** SQLite [`BEGIN IMMEDIATE` transactions](https://www.sqlite.org/lang_transaction.html) and [JSON functions](https://www.sqlite.org/json1.html); Pydantic [strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/) and `extra="forbid"`; the idempotency and outbox reasoning builds on [SG-REL-00](../../../study-guides/llm-reliability/docs/00-reliable-model-calls.md) and the [offline controls lab](../../reliability/offline-controls/README.md). Recorded in the [source ledger](../../../docs/source-ledger.md). All data is synthetic.
