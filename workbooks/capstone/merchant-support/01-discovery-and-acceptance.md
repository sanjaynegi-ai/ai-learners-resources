# W-CAP-01.1 — Discover the problem and freeze acceptance

**What useful work should this system support, and which evidence would show it is safe to proceed?** Freeze the scenario contract before optimizing prompts or running a release evaluation.

> **Your goal:** Separate scenario facts, assumptions and open decisions, then map requirements to checks.<br>
> **You need:** The [capstone route](README.md) and its prerequisite evidence.<br>
> **Effort:** 2 hours, estimated within the guided capstone allocation.<br>
> **You will produce:** Delivery records begun and a versioned requirement/acceptance map. **Status:** Draft fictional scenario; no stakeholder approval is implied.

**Starting state:** work in your personal capstone copy at `cap-0-contract`. No provider request, deployment or external stakeholder message is needed. Create the named Markdown records below and preserve their versions alongside later reports. Use synthetic identities, orders and policies only.

QuickCart's two fictional merchants need internal support agents to find shipping/refund evidence and prepare an eligible refund for approval. The desired result is supported internal work with clear refusal paths. A fluent chat demonstration cannot establish that the right merchant saw the right policy or that a revoked supervisor cannot authorize a queued effect.

Think of the application as a controlled case file: the agent finds evidence, proposes an action, and a different authorized person reviews it. The analogy stops at authority: a paper signature may be historical evidence; this scenario requires **current** authority at execution. The application must recheck, rather than trust that the approver was authorized yesterday.

## Scenario facts, assumptions and questions

Create `delivery/discovery.md` in your personal project, using this labelled worked example. These are fictional requirements, not a record of real interviews.

| Question / decision role | Scenario answer or unresolved choice | Engineering consequence |
|---|---|---|
| Support lead: what is useful? | **Scenario fact:** exact reviewed policy excerpts and an order total, for internal review only | Curated extractive answers suffice; free-form policy advice is outside scope |
| Security owner: who establishes identity? | **Assumption:** local synthetic bearer mapping → trusted membership; **unresolved:** real identity provider | No model/request tenant field; no production authentication claim |
| Finance reviewer: what may execute? | **Scenario fact:** simulated local refunds, <=5000 cents and <=remaining order total, one other current supervisor | All refunds need approval even when policy text says otherwise |
| Support manager: review capacity? | **Assumption:** 10 reviews/min at 20 requests/min; **unresolved:** actual staffing | Abstention/approval counts affect feasibility; measure backlog before scaling |
| Operations owner: when is stale data denied? | **Scenario fact:** recheck before answer publication and inside effect transaction | Deletion/revision change invalidates retained citations/approvals |
| Data owner: what does deletion mean? | **Scenario fact:** remove queryable chunks and deny pending effect; **unresolved:** retention of restricted audit/backups | Logical deletion is not secure erase; never restore revoked/deleted access blindly |
| Release owner: what may be called live? | **Unresolved:** sandbox/account/region/model/budget/window and cleanup owner | Default offline; final model/deployment evidence remains required |

The synthetic memberships A/B and claims come from the earlier RAG fixture. Its tenant-B claim says review can be bypassed; that is untrusted business content and cannot change the application's approval rule. The reference corpus is a curated teaching corpus, not an approved commercial refund policy. Dates use the inherited logical data clock `now=100`, expiry `1000`. Do not confuse these with real calendar validity; calendar/effective-date interpretation is a changed requirement in the independent task.

## Contract fixed before evaluation

> [!IMPORTANT]
> A scenario fact is supplied teaching input; an assumption is a claim to validate; an unresolved choice needs an owner and evidence. Do not convert an illustrative negotiation into stakeholder approval or silently relax an essential gate.

Create `delivery/requirements.md` and `delivery/acceptance.md`. Freeze the following reference-v1 contract before running reports. A stakeholder may negotiate scope, not waive trust boundaries or hide failed evidence. Keep criteria versions with reports.

| ID | Trigger, behavior and failure | Trusted enforcement / evidence |
|---|---|---|
| CAP-AUTH-01 | A request uses only current caller-tenant/role policy candidates; unknown/revoked identity denied | Membership and `Store.candidates` before ranking; isolation/revocation tests |
| CAP-GROUND-01 | Known topic returns exact reviewed quote/citation; missing/conflicting/invalid evidence produces distinct abstention/conflict | Existing `answer` plus integration publication recheck; evaluation and deletion tests |
| CAP-ORDER-01 | Typed order lookup returns only caller-tenant order; absent and foreign both denied | Trusted `Engine.order`, no model-selected tenant; negative HTTP test |
| CAP-ACT-01 | Proposal amount is integer cents, >0, <=5000 and <=order total, supported by refund-policy evidence | Strict API plus business checks; forged quote/amount tests |
| CAP-APPROVE-01 | Different current same-tenant supervisor approves; current proposer, approver and evidence checked at execution | `approve` and transaction `execute`; revoked approver/changed revision tests |
| CAP-IDEM-01 | Same tenant/order/amount/evidence payload maps to one action/effect across crash/restart; aggregate effects cannot exceed order total | SQLite key + one atomic local effect/completion transaction; restart/order-total tests |
| CAP-BOUND-01 | At most two provider operations concurrently, one attempt per answered request, 2 s local provider deadline and 20 durable reservations/state | Admission, wait_for, call ledger, subprocess cleanup; deadline/budget/concurrency tests |
| CAP-TRACE-01 | Events contain only time/status/latency/call count/kind, expire logically after seven days | Projection by construction and `expire_telemetry`; privacy/expiry tests |
| CAP-EVAL-01 | Reference controls: development 4/4 and held-out 8/8 expected outcomes, zero forbidden retrieval, reviewed quotes exact | Versioned evaluation; public tiny dataset is not unseen production evaluation |
| CAP-OPS-01 | Provider failure halts model admission and effects; recovery probe and amendment recorded, no automatic resume | Incident CLI, persisted halt, operator runbook |
| CAP-DELIVER-01 | Preserved artifact/configuration starts, HTTP checks pass, state survives restart and cleanup is verified | Container build/config/inspect/smoke/restart evidence; separate live evidence gate |

The chosen operational targets are pedagogical. They do not imply representative quality, production latency, a universal refund limit or a certification threshold. Live semantic criteria must be fixed with human-reviewed labels and realistic slices before evaluation. Keep unsafe/forbidden behavior at zero; uncertainty does not justify averaging it away.

**Pause and predict:** If every unanswerable request goes to review and arrivals exceed review capacity, has abstention solved the problem?

<details><summary>Show worked acceptance negotiation</summary>

No. At 20 requests/min and 60% review routing, demand is 12 reviews/min. Capacity 10/min yields +2 queued reviews/min before approvals. This is an illustrative steady-rate calculation, not measured capacity. A simulated support lead requests higher coverage; the engineer proposes narrower supported topics and a bounded queue while measuring human capacity. The revised proposal remains **simulated/unconfirmed**, not accepted business approval. Do not make the model guess to shrink the queue.

</details>

Before the contract review, freeze [versioned UAT cases](customer-acceptance.md) in `delivery/acceptance.md`. Use 20 minutes of this existing two-hour discovery allocation, replacing the generic acceptance discussion; actual result rows wait until the application exists. Reuse the phase-4 simulated interaction log and distinguish technical checks from customer sign-off.

## Review the contract before building

Check your discovery, requirement and acceptance records together:

- Every scenario fact is labelled, and each assumption/open choice has an owner and validation question.
- Each stable requirement ID identifies a trigger, expected behavior, failure case, trusted enforcement and inspectable evidence.
- Human-review demand uses stated arrivals and routing rates; approval work is included rather than treated as free capacity.
- Revisit your [phase-1 selection record](../../ml/escalation-evaluation/solution-selection.md) against this capstone contract: update the deterministic, traditional-ML, LLM and RAG comparison, separate orchestration from model choice, defend a no-LLM alternative and retain pending model measurements. Replace the earlier single-alternative discussion within the existing two-hour allocation; do not repeat the phase-1 exercise or weaken the frozen capstone controls.
- Model, deployment and independent-ownership gates remain visible even when local control checks can pass.

**You can now:** defend the bounded problem and map its requirements to evidence before implementation. **Show it:** your versioned discovery, requirements and acceptance records, with fictional decisions and unresolved choices labelled honestly.

**Next:** [guided implementation](02-guided-build.md), using this frozen contract. Return to the [capstone route](README.md) for checkpoint and effort boundaries.
