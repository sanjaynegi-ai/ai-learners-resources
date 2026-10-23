# Revision and glossary — retrieve the mechanism, not the slogan

> **Unit:** W-DEFEND-01 / AI-DEFEND-01 · **Effort:** 2 h final revision, selected earlier recall inside existing module time · **Status:** Draft<br>
> **Outcome / artifact:** Explain a term in your own system, predict its failure and link evidence in your practice log. Acceptance: consequence + enforcement + limit, not a memorized definition.

## Retrieval practice

Without looking at code, explain one request and predict where it can fail. Then open the relevant source and correct your account. For each gap, use the precise prerequisite link below rather than rereading every architecture guide. The glossary supports already-taught concepts; it does not introduce a new required syllabus.

| Term | Plain meaning and QuickCart consequence | Retrieve from |
|---|---|---|
| Validation | Check shape and constraints; valid JSON can still promise a nonexistent refund | [Output diagnosis](../llm/refund-drafts/lesson-2-diagnose-and-compare.md) |
| Async cancellation | Stop cooperating local work; a cancelled wait may leave remote inference running | [Reliability guide](../../study-guides/llm-reliability/docs/00-reliable-model-calls.md) |
| Baseline | A defined comparison; a simpler classifier or prompt can outperform added complexity | [ML metrics](../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) |
| Leakage | Evaluation uses information it should not have; a future outcome column makes results misleading | [ML metrics/leakage](../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) |
| Held-out data | Examples withheld from development decisions; public reused examples cannot establish unseen performance | [Evaluation harness](../llm/eval-harness/README.md) |
| Token/context budget | Model input/output units and finite space; including every policy may displace needed evidence | [LLM foundations](../../study-guides/llm-foundations/docs/00-how-llms-generate-text.md) |
| Prompt injection | Untrusted content tries to become instructions; a retrieved note cannot grant another tenant's authority | [Grounding and permissions](../../study-guides/retrieval-foundations/permissions-and-grounding.md) |
| Retrieval recall | Relevant authorized evidence found / relevant authorized evidence expected; no evidence means generation cannot ground an answer | [Retrieval foundations](../../study-guides/retrieval-foundations/README.md) |
| Grounding | Support answer claims with authorized evidence; a syntactically correct citation can still refer to stale data | [Grounding and permissions](../../study-guides/retrieval-foundations/permissions-and-grounding.md) |
| Authentication / authorization | Establish identity / decide permitted action; synthetic token mapping is not production identity | [Ticket API](../python/quickcart-api/README.md) |
| Revocation / freshness | Withdraw authority / require current evidence; recheck after a long provider wait | [Integrated build](../capstone/merchant-support/02-guided-build.md) |
| Logical deletion | Remove query access under a declared contract; SQLite row deletion does not prove secure erasure of backups | [Integrated operations](../capstone/merchant-support/05-operations-and-handover.md) |
| Approval | A trusted, payload-bound decision; an old checkpoint or model statement does not authorize execution | [Stateful orchestration](../langgraph/approval-workflow/README.md) |
| Idempotency | Retry the same business action without a second effect; a new model call ID is not a stable business identity | [Safe actions](../llm/safe-actions/README.md) |
| Outbox | Durable record of an intended side effect for later dispatch; ambiguity still needs downstream idempotency/reconciliation | [Safe actions](../llm/safe-actions/README.md) |
| Interface boundary | Explicit client/server/tool contract; protocol compliance does not grant permission | [Tool interfaces](../../study-guides/tool-interfaces/README.md) |
| Coverage | Ready outcomes / all requests; failed requests must not vanish from the denominator | [LLMOps guide](../../study-guides/application-llmops/README.md) |
| Conditional quality | Correct reviewed ready / reviewed ready; 100% may hide low coverage or missing review | [LLMOps guide](../../study-guides/application-llmops/README.md) |
| Tail latency | A high percentile of response time; fast failures can improve p95 while hurting users | [Operations workbook](../operations/release-watch/README.md) |
| Artifact provenance | Record what code/prompt/model/data/config produced evidence; a hash alone does not prove approval | [Engineering delivery](../delivery/README.md) |
| Rollback | Restore compatible behavior; restoring old data may restore revoked authority or forget effects | [Capstone delivery](../capstone/merchant-support/04-delivery.md) |
| Threat model | Identify assets, boundaries, attackers, controls and residual risk; connect each control to a failure test | [Capstone design](../capstone/merchant-support/design.md) |
| ADR | Record a decision, alternatives and consequences; choosing a graph needs a requirement | [Capstone design](../capstone/merchant-support/design.md) |
| Non-compensable gate | A critical failure cannot be offset by a high score elsewhere; good latency cannot excuse tenant leakage | [Capstone criteria](../../assessments/capstone-evidence.md) |
| Independent ownership | Explain, modify and defend your work with disclosed assistance; copied reference output is insufficient | [Defense route](README.md) |

## Three worked checks

**Predict:** 100 requests, 70 ready, only 35 reviewed, 34 good. What do you know?

<details><summary>Show reasoning</summary>

Coverage 70/100 = 70%; observed conditional quality 34/35 ≈97.1%; review fraction 35/70 =50%. Do not claim 97.1% quality across all 70 ready requests or assume review selection is representative. Record 30 non-ready outcomes by type; acceptance depends on predeclared review/sample criteria.

</details>

**Predict:** The image is restored, but a supervisor was revoked after its database backup. May you restore that backup to “fix” approval?

<details><summary>Show reasoning</summary>

No automatic restoration is justified. Old data can reintroduce authority and forget newer effects. Preserve current security/effect history, use compatible forward repair or a reviewed reconciliation procedure, and halt if recovery cannot be shown safe. A health check alone does not establish recovery.

</details>

**Predict:** AWS returns AccessDeniedException before a response. Is this successful model evaluation with zero cost?

<details><summary>Show reasoning</summary>

It is a failed real-service attempt, with no model response/semantic quality evidence. Preserve the failure, unexecuted cases and unknown billing information. Diagnose the scoped permission rather than broaden IAM or call the result a pass. The current [live-attempt record](../../docs/review-evidence/capstone-live-attempt.json) illustrates this distinction.

</details>

Revision deliverable: choose five weak terms, explain their consequence/enforcement/limit, then answer one changed prediction and verify it in the relevant lab. Reuse [LangChain glossary](../langchain/01-learning-workbook/18-glossary.md) and [scalability revision/glossary](../../study-guides/cloud-architecture-patterns/scalability-patterns/docs/12-quick-revision.md) for fuller definitions; this is a cross-path retrieval aid, not a competing canonical glossary.

[Practice bank](practice-bank.md) · [Route](README.md) · [Repair map](../../assessments/defense-and-remediation.md)
