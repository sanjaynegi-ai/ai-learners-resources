# SG-GRAPH-00 — Resume the work without repeating its effect

A saved workflow can remember a decision without proving that it is still allowed.

> **Your goal:** Explain durable state, approval, replay and recovery before choosing orchestration.<br>
> **You need:** [SG-REL-00 — reliable model calls](../llm-reliability/docs/00-reliable-model-calls.md) and [SG-RAG-01 — permissions and grounding](../retrieval-foundations/permissions-and-grounding.md); the outbox pattern from [W-LLM-ACT-01](../../workbooks/llm/safe-actions/README.md) helps.<br>
> **Estimated effort:** 40–55 min, estimated<br>
> **You will produce:** A state/authority/effect explanation and a justified sequential-versus-graph decision.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**QuickCart context:** a fictional support credit waits for supervisor review and may resume after a worker failure. Distinguish saved progress, current permission and the durable effect before selecting a framework.

**Study route:** trace the crash scenario, explain checkpoints versus authority, then compare direct sequential execution with a durable wait. No runtime setup or paid call is needed for this guide; implementation belongs in the next workbook.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-GRAPH-01 | **Status:** Draft, unpiloted<br>
> **Prerequisites:** [reliability](../llm-reliability/docs/00-reliable-model-calls.md), [trusted evidence/authority](../retrieval-foundations/permissions-and-grounding.md)<br>
> **Effort:** 40–55 min, estimated<br>
> **Question:** After a worker crashes, which facts are durable and which steps may run again?<br>
> **Outcomes/artifact:** Explain state versus authority versus effects, trace an interrupt/recovery, and defend the simplest suitable orchestration.

</details>

## The failure that motivates a graph

QuickCart queues a synthetic credit for review. A supervisor approves, the worker records the credit, then crashes before recording its graph completion. Retrying the node blindly may duplicate the credit. Refusing all retries may strand completed work.

A workflow is an explicit set of steps and allowed transitions. A stateful workflow retains enough progress to continue after waiting or failure. Think of a parcel tracking ledger: the next depot needs to know where the parcel reached. The analogy has a limit: recording arrival does not itself perform delivery, and a missing tracking update does not prove delivery failed.

**Predict:** If a saved graph says execution is pending but the effect ledger already contains the credit, should recovery issue another credit?

<details><summary>Reasoning</summary>

No. Reconcile against the durable effect identity. A checkpoint and a side effect may commit at different times. The application must recognize replay and report the existing committed fact.

</details>

## State, checkpoints and authority

**State** is the data passed between nodes; a node returns updates and an edge selects the next step. TypedDict documents fields but does not enforce runtime policy. Validate external inputs and read consequential facts from trusted storage. In the reference, graph state contains request_id/status; amount, tenant and current approvals are application records.

A **checkpoint** stores workflow progress. A thread ID selects a saved workflow; it is not an authentication credential. Restrict checkpoint access and treat serialized state as trusted service data, never an arbitrary uploaded artifact. Persist only necessary fields, with access/retention assumptions.

An **interrupt** pauses for external input. Resume wakes the workflow; it does not authorize a credit. Read the decision and the approver's current role/tenant from application authority. An approval recorded yesterday can be revoked before execution today.

Code before an interrupt may run again on resume. Keep that region free of non-idempotent effects. Here it only reads the request and constructs a review payload. Do not catch a graph interrupt with a generic exception handler and accidentally turn it into a successful answer.

## Recovery is a replay problem

There are two SQLite files: checkpoints and authoritative request/approval/effect records. They are deliberately not one distributed transaction. Inside the authority database, the synthetic effect row and completed request update share a transaction. A unique request key makes a repeated insert harmless, and recovery checks for an already recorded effect before applying anything.

For example, credit R1 commits at time t1; the process fails before checkpoint t2. On restart, LangGraph retries execution, but the ledger already has R1. The final graph reports completed and the effect count remains one. If the supervisor was revoked after t1, that does not undo the existing effect or turn it into an unperformed denial. Reconciliation must distinguish already completed work from authorization for a new effect.

Real external payments cannot join this local transaction. They require an external idempotency contract, durable outbox/reconciliation and ambiguity handling, as taught in the safe-actions workbook. This simulated ledger is not proof of exactly-once external delivery.

## Bound execution and observe facts

The reference graph has validate → approval → execute, plus an early-denial edge. A recursion limit bounds supersteps per invocation; it is neither a wall-clock timeout nor a spending cap. Waiting for approval consumes no continuously running worker here, but may last indefinitely. A production approval queue needs expiry, ownership and review capacity.

Inspect saved state, pending node names and effect counts. Do not infer success from a node trace alone. Keep request IDs, node/status/error categories and version identities in controlled logs; avoid retaining secrets or unnecessary customer content in checkpoints/traces. The local CLI uses synthetic identities and no hosted tracing.

## When sequential code is enough

If inputs and a trusted approval are already available, call validate then execute directly. The reference sequential function uses the same policy and effect ledger. It is smaller and easier to inspect. A graph earns its complexity when waiting/resumption, explicit branches and saved progress reduce application glue.

A sequential service could implement its own durable queue/state machine; that remains a legitimate alternative, not a claim that persistence requires LangGraph. Conversely, a graph does not automatically supply authentication, policy, external idempotency or operational ownership.

## Practice and reflection

> [!TIP]
> Draw three separate records: workflow progress, current authority and completed effect. Then mark which one changes at approval, revocation and crash recovery.

**Pause and diagnose:** the effect ledger says completed but the workflow checkpoint still points to execution. Which fact should recovery inspect before trying another effect?

<details>
<summary>Compare your reasoning</summary>

Inspect the authoritative committed effect under the same immutable request identity. A stale checkpoint is not evidence that the effect failed. Reconcile progress with the completed fact; a new action key would turn a retry into another effect. This local reference does not make an external service part of the SQLite transaction.

</details>

Complete [W-GRAPH-01](../../workbooks/langgraph/approval-workflow/README.md). Predict every fault before running it. Independently change approval from one supervisor to two distinct current same-tenant supervisors, then revoke one after approval and before execution. A duplicate signature must not count twice. Explain the schema and recovery impact, not just a boolean helper.

Revision: state tracks progress; authority grants permission; checkpoints save workflow progress; interrupts wait; idempotency identifies repeated effects; reconciliation resolves conflicting progress/effect records. Next constraint: live model/tool boundaries and deployment, which are not established by this local graph.

## Sources

Checked 2026-10-14; official APIs executed at versions in the workbook manifest. **Reference**, optional, free, Python prerequisite, 10 min each: LangChain [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), pause/resume and restarted-node sections; [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), checkpoints and local SQLite development backend. Core explanations above are self-contained. No source examples are copied as a complete application.

## Completion checkpoint

**You can now:** explain current approval, durable replay and effect reconciliation before choosing a graph. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [build the durable approval workflow](../../workbooks/langgraph/approval-workflow/README.md). Use the root capability prerequisites when deciding whether to proceed.
