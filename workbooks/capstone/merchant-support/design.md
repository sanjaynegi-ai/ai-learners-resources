# Reference architecture, threat model and decisions

**Status:** Draft scenario design, not production security approval. Requirement IDs are defined in [chapter 01](01-discovery-and-acceptance.md). Read the [diagram and walkthrough](02-guided-build.md#1-trace-the-boundaries-before-changing-them).

## Decision records

**ADR-01 — Curated extractive RAG rather than free-form support chat.** CAP-GROUND-01 needs attributable reviewed policy excerpts. Reuse the earlier permission-aware package, including authored hybrid retrieval. A search UI is simpler and remains a viable alternative if generation adds no benefit; the provider boundary lets learners evaluate exact-claim selection and failure behavior. Curated topic routes/claim labels are narrow and require publisher review; this is unsuitable for general conversational policy interpretation. The reference does not prove learned embedding quality or general contradiction detection.

**ADR-02 — Explicit tools and one local process.** CAP-ORDER/APPROVE needs trusted records and a short approval path. Use a read-only tenant-scoped order function and an explicitly operator-requested simulated refund, not an autonomous tool loop. SQLite/one event loop gives clear transaction boundaries. A durable outbox with idempotent downstream service is required for real remote effects; graph orchestration could become useful for long-running distributed approvals. This reference adds neither gratuitously.

**ADR-03 — Persist policy state, approvals and admission.** CAP-IDEM/BOUND requires restart evidence. Seed only a new empty membership store; do not reseed on restart. Hash canonical action payload and preserve an aggregate order-total check. Explicit consequence: identical intended separate refunds need a redesigned trusted event identity. Multi-process/replica scaling requires atomic shared budget and concurrency control; one worker is a design constraint, not an optimization left to deployment defaults.

**ADR-04 — Isolate live evaluation from service defaults.** Real Bedrock evaluation needs budget/account/model review, whereas default tests must be free. The service always stays offline. A separate CLI requires paid-call acknowledgement and model ID, invokes one bounded SDK call in a killable child, stores usage when available and marks output unreviewed. Provider outputs remain untrusted even in live mode. A deadline bounds local waiting; it cannot guarantee cancellation of provider work or charges.

**ADR-05 — Local container deployment with honest boundary.** One digest-pinned Linux image, loopback port and named state volume make packaging/restart reproducible. Production IdP/TLS, operational IAM, hosted deployment, state backup/restore and representative live semantic evidence remain additional work. The earlier AWS SAM deployment demonstrates AWS competencies separately; it does not automatically deploy this application. Final reviewer acceptance of deployment scope is explicit and pending until actual evidence is reviewed.

## Threat model

Assets: merchant policy content, restricted order totals, membership/approvals, simulated effect ledger, provider budget and evidence integrity. Trust boundaries: caller→API, trusted membership→retrieval, evidence→provider, provider→validator, actor/approver→effect transaction, operator→state files, artifact/evaluation→reviewer. Raw caller text, document text, provider responses and tool results are untrusted. Filesystem/database administrators are trusted in this local model; it does not resist a hostile host.

| Threat / requirement | Control and test | Residual risk / owner |
|---|---|---|
| Tenant or role leakage / AUTH | Trusted membership filters candidates before provider; tenant order checks; HTTP/isolation tests | Synthetic public tokens; real IdP/TLS/rate limit required. Security owner |
| Revoked authority between retrieval/action / APPROVE | Publication recheck plus current actor/approver/policy in effect transaction; revoke/delete/revision tests | Fixed logical clock; real time-effective data is independent work. Data/security owners |
| Prompt injection or fabricated quote / GROUND | Only reviewed claims sent, exact schema/quote validation; invalid-output/injection tests | Curated claims can be wrong; no free-form injection robustness claim. Publisher/reviewer |
| Forged approval/amount / ACT | Strict body forbids extra identity fields; cents/order/current supervisor checks | Local actor role model only; no real monetary integration. Application owner |
| Duplicate effect / IDEM | Durable content key and atomic local effect/completion; crash/restart test | No remote exactly-once guarantee, explicit event identity limitation. Release/operator |
| Budget/time/concurrency exhaustion / BOUND | One call, two slots, deadline, durable reservations, bounded body/context/output; cancellation/budget tests | One-process assumption; remote costs may continue; rate/host limits still needed. Application/cloud owner |
| Sensitive telemetry export / TRACE | Event fields constructed explicitly; non-echoing HTTP validation; expiry test | Business SQLite/backup access needs protection; logical deletion only. Data owner |
| False graduation / EVAL | Distinct synthetic/live/unreviewed/deployment records and readiness NO_RELEASE | Declarations/hashes cannot verify truth or individual ownership. Assessor |

Unacceptable release conditions: authorization leak, unbounded operation, secret exposure, hidden evaluation failures or fabricated evidence. Do not use illustrative mitigations to call these passed. The [evidence chapter](07-evidence-and-defense.md) maps verification and pending milestones.

[Route](README.md) · [Cost/operations](05-operations-and-handover.md)

## Application-governance evidence

Update and link the private [record begun in operations](../../operations/release-watch/application-governance.md) from your existing threat/design and handover records; do not create a second competing governance policy. This update uses existing capstone design/handover effort, with no new phase-6 assignment. Replace reference-only checks with actual evidence where executed, preserving source/reader scope, clock/retention, deletion surfaces, audit readers, provider/data-use approvals and incident/resume duties.

The local reference retains action/approval/effect history and audit citations separately from seven-day telemetry and deleted retrieval chunks. Direct storage readers are trusted; real identity/IAM, audit integrity, backup/export disposal and actual model/provider/data approvals are unresolved. Fictional owner roles are not signed approvals or legal compliance. A live model call or local container pass cannot close those gaps; retain them in the release decision and reuse the customer-delivery plan's unobserved impact state.
