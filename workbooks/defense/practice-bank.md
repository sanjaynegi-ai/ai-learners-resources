# Stage defense practice — public prompts, private assessment variants

> **Unit:** W-DEFEND-01 / AI-DEFEND-01 · **Status:** Draft practice bank · **Effort:** Select within each module's existing reflection/independent time; final rehearsal is separately budgeted in the [route](README.md)<br>
> **Artifact:** Prediction, changed artifact/test, diagnosis, decision and drafted stakeholder update. No message is sent. Prerequisites are linked in each stage. These are public exercises, not unseen examination items.

Attempt each selected prompt before consulting the reference. For coding prompts, make the change in a personal copy, add a positive and negative behavior check, and preserve original output. Design answers need requirements, alternatives, enforcement and a residual limit. Stakeholder answers need impact, evidence, uncertainty, recommendation and next decision. Use the [evidence template](evidence-template.md), not a presentation-only checklist.

## P01 — Python and API ownership

Prerequisite/evidence: [Python bridge](../python/README.md), [ticket API](../python/quickcart-api/README.md); AI-ENTRY-01 / AI-PY-01.

- **Code:** Implement the module's supervisor-only deletion extension with strict input and current tenant/role checks.
- **Debug:** A ticket appears missing after switching workers. Identify whether state is in memory, tenant-scoped or durable before “repairing” storage.
- **Design:** Explain which Python differences required practice and which backend skills transferred. Why is code you have run stronger evidence than years of experience?
- **Stakeholder:** Draft an honest setup and progress update with one demonstrated skill, one gap and a targeted return point.

Check: absent and foreign tickets remain indistinguishable, unauthorized deletion fails, and explanation distinguishes local API tests from deployment. Optional Python refreshers do not become an undeclared extra prerequisite month.

## P02 — ML evaluation and leakage

Prerequisite/evidence: [scikit-learn evaluation](../ml/escalation-evaluation/README.md); AI-ML-01.

- **Code:** Change the reviewed threshold under a new review-capacity constraint using validation data, retaining the original test record.
- **Debug:** A future-outcome feature dramatically raises accuracy. Diagnose split/feature leakage rather than celebrate it.
- **Design:** Compare the rule/constant baseline and learned model using confusion counts, subgroup denominators and review cost.
- **Stakeholder:** Explain why an apparently stronger model should not be released while its evaluation is contaminated.

Check: threshold selection does not silently reuse held-out outcomes; the cost/capacity trade-off has units and actual evidence. The optional Orange GUI demo is not a required Python implementation.

## P03 — LLM calls, prompts and context

Prerequisite/evidence: [direct API/diagnosis](../llm/refund-drafts/README.md), [context concepts](../../study-guides/llm-foundations/docs/01-designing-prompts-and-context.md); AI-LLM-01 / AI-API-01 / AI-CALL-01 / AI-VALID-01 / AI-STATE-01.

- **Code:** Implement the module's amount/status-claim check without letting model fields supply trusted order facts.
- **Debug:** A structurally valid reply fabricates a refund date. Find which semantic/business check is missing.
- **Design:** Allocate a finite context budget and explain which evidence is required; defend why adding examples can contaminate evaluation.
- **Stakeholder:** Describe a useful abstention and why prompt wording alone cannot guarantee policy correctness.

Check: preserve separate syntax/schema/business/quality evidence and expected variability. Do not claim a replay fixture is a real provider run.

## P04 — Reliability, safe actions and versioned evaluation

Prerequisite/evidence: [reliability](../llm/reliable-drafting/README.md), [safe actions](../llm/safe-actions/README.md), [evaluation](../llm/eval-harness/README.md); AI-RELIABLE-01 / AI-EVAL-01 / AI-TOOLS-01.

- **Code:** Add the existing independent retry-budget or daily-credit-cap exercise while retaining admission/idempotency history.
- **Debug:** A timed-out action has already applied. Trace reservation, downstream key and reconciliation before retrying.
- **Design:** Explain which limits are per attempt/request/process/global and which costs remain unknown after cancellation.
- **Stakeholder:** Recommend halt/review when a critical gate fails despite improved average quality or latency.

Check: denied side effects and unsafe output cannot be averaged away. Version application/prompt/model/schema/data/evaluation/configuration, and show denominator/label limitations.

## P05 — Retrieval, permissions and grounding

Prerequisite/evidence: [guided RAG](../langchain/02-rag-capstone-workbook/README.md); AI-RETRIEVE-01 / AI-RAG-01.

- **Code:** Implement the recall-notice transfer with trusted supplier/time scope and invalidation of changed/deleted evidence.
- **Debug:** Answer generation fails even though retrieval hits the right passage. Separate retrieval and answer failures.
- **Design:** Defend filtering before ranking/provider exposure versus filtering only final citations; name every queryable cache/store.
- **Stakeholder:** Explain what logical deletion removes, what audit data may remain and what secure-erasure claim is unsupported.

Check: inspect candidates as well as answers/traces; stale permissions or retained handles cannot bypass the declared decision point.

## P06 — LangChain abstractions and integration

Prerequisite/evidence: [learning workbook](../langchain/01-learning-workbook/README.md), [actual mechanisms](../langchain/01-learning-workbook/mechanisms-lab/README.md); AI-INTEGRATE-01.

- **Code:** Complete the whole-passage context-budget extension while keeping explicit output validation and bounded history.
- **Debug:** Identify which pipeline stage altered the message or parsing contract; reproduce the fault outside the wrapper.
- **Design:** Compare explicit Python stages with the selected abstraction. What requirement does the abstraction satisfy?
- **Stakeholder:** Communicate a framework upgrade's compatibility/evidence risk without equating newer with better.

Check: chapter 16/17 point rubrics remain unchanged; historical hosted/model-quality failures stay visible. A wrapper does not establish authorization.

## P07 — Stateful orchestration and recovery

Prerequisite/evidence: [durable approval workflow](../langgraph/approval-workflow/README.md); AI-GRAPH-01.

- **Code:** Extend current approval to the module's quorum requirement, preserving restart and effect identity.
- **Debug:** A graph resumes after a crash but approval has been revoked. Locate the execution-time check, not only the checkpoint.
- **Design:** Defend state/checkpoint versus authority/effect ledger separation; compare the sequential implementation.
- **Stakeholder:** Explain why workflow completion is different from approved business completion or a reconciled external effect.

Check: resume payload is not authority, replay cannot double-apply and no graph flag substitutes for trusted business policy.

## P08 — Agents SDK and MCP interfaces

Prerequisite/evidence: [SDK loop](../agents-sdk/tool-loop/README.md), [MCP client/server](../mcp/stock-server/README.md); AI-INTERFACE-01.

- **Code:** Extend a typed read-only tool while rejecting unknown fields, forged identity and hostile result content.
- **Debug:** Separate unavailable server, invalid tool result, denied caller and exhausted execution budget.
- **Design:** Explain actual SDK loop, client/server protocol and application authorization boundaries; state what local tracing cannot prove.
- **Stakeholder:** Compare local protocol/scripted-model evidence with remote authentication and live-model gaps.

Check: schema/protocol validity never grants access. Default practice must not enable paid inference or hosted traces implicitly.

## P09 — Selective n8n integration

Prerequisite/evidence: [review-event integration](../n8n/review-integration/README.md); AI-AUTOMATE-01.

- **Code:** Complete selective retry so a denial stops while an ambiguous retry retains the stable event identity.
- **Debug:** A successful visual workflow appears to have lost an event. Inspect durable admission and actual node contract.
- **Design:** Identify what stays owned by Python and what n8n adds; avoid duplicating the whole application visually.
- **Stakeholder:** State which editor/UI/CLI/runtime route was actually tested and the remaining deployment support boundary.

Check: duplicates do not create a second review, denial is not retryable success, and workflow imports are distinguished from executions.

## P10 — Engineering delivery and compatibility

Prerequisite/evidence: [delivery](../delivery/README.md); AI-DELIVER-01.

- **Code:** Make the existing optional-priority/schema change with consumer compatibility checks and preserved artifacts.
- **Debug:** An old image still fails under a bad timeout configuration. Compare image, config and data separately.
- **Design:** Explain why more workers break in-memory assumptions and what must become durable/shared before scaling.
- **Stakeholder:** Use 15 minutes of this existing reflection allocation for the [customer rehearsal and impact plan](../delivery/customer-rehearsal.md), replacing the separate stakeholder paragraph. Retain the release/no-release recommendation, actual hosted versus local evidence, rollback consequences and simulated acceptance state inside that record; do not add another presentation.

Check: restore the recorded artifact/configuration, not just a tag; cleanup is scoped to your dedicated resources.

## P11 — AWS/Bedrock delivery

Prerequisite/evidence: [bounded queue worker](../aws/bedrock-worker/README.md); AI-AWS-01.

- **Code:** Implement the workbook's approved-second-attempt design with a new attempt identity and remaining budget, using offline tests first.
- **Debug:** Distinguish queue backlog, mapping disabled, model-access denial, budget exhaustion and ambiguous reserved attempt.
- **Design:** Review exact IAM/resource/call/token bounds, redrive/reconciliation and teardown residuals without widening permission to fix a symptom.
- **Stakeholder:** Report a denied live attempt as denied, not model-quality evidence; state the administrator decision and next bounded verification.

Check: no cloud/model call is required for this public rehearsal. Only separately authorized/budgeted runs may produce live evidence; budget alerts are not guaranteed spending caps.

## P12 — Application LLMOps and incident ownership

Prerequisite/evidence: [release monitoring](../operations/release-watch/README.md); AI-OPS-01.

- **Code:** Add the independent slow-slice regression gate, including missing/undersized slice handling.
- **Debug:** Quality stays 100% and p95 improves after timeout reduction. Explain coverage/failure/review denominators.
- **Design:** Defend safe telemetry fields, retention/access assumptions, regression threshold and review queue capacity.
- **Stakeholder:** Draft containment/recovery update with owner, impact, uncertainty and next decision; keep rollout halted until reviewed.

Check: preserve failed and recovery reports; logical expiry, local role strings and probe recovery do not establish production IAM/erasure/live quality.

## P13 — Independent integrated delivery

Prerequisite/evidence: [changed merchant brief](../capstone/merchant-support/06-independent-delivery.md); AI-CAP-01.

- **Code:** Implement threshold-based current quorum and calendar-effective policy/migration with boundary and restart checks.
- **Debug:** A previously approved action fails after policy deletion or approver revocation. Distinguish correct denial from a regression.
- **Design:** Explain whether rollback would restore deleted authority or forget effects; defend forward repair or a no-release decision.
- **Stakeholder:** Update discovery/requirements/acceptance/handover with scope, review/cost workload and actual missing milestones.

Check: [seven-dimension evidence review](../capstone/merchant-support/07-evidence-and-defense.md), real-model/deployment separation, assistance disclosure and independent changed implementation. A public reference cannot supply these ownership claims.

## P14 — Final individual defense

Prerequisite/evidence: [assessment procedure](../../assessments/defense-and-remediation.md#individual-defense-procedure); AI-DEFEND-01.

Explain one complete request, then make the reviewer's revealed small change, diagnose an unfamiliar failure, defend an alternative and draft a stakeholder decision. The reviewer must choose a task different from rehearsed public prompts and record it privately when revealed. No unreleased variant is supplied here. A solo public rehearsal remains self-assessment, even if all tests pass.

Acceptance is the existing essential-dimension evidence with critical gates intact; time/format is a planning accommodation, not a score for accent or speaking speed. Return to the specific [repair route](../../assessments/defense-and-remediation.md#repair-and-reassessment-map) when evidence is weak.

[Revision](revision-and-glossary.md) · [Evidence template](evidence-template.md) · [Route](README.md)
