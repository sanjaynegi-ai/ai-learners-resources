# SG-RAG-01 — Evidence must still be allowed when it leaves

**If a passage was allowed when search began, can you still return it after access is revoked?**

> **Your goal:** Defend authorization, freshness, citation and deletion boundaries.<br>
> **You need:** [Retrieval foundations](README.md) and the completed retrieval exercises in the [course map](../../README.md#ordered-capability-map).<br>
> **Effort:** 35-45 minutes reading, estimated.<br>
> **You will produce:** A revocation timeline, citation counterexample and deletion test plan. **Status:** Draft; unpiloted.

QuickCart, our fictional e-commerce platform, now needs a policy answer that remains eligible at delivery time. Finding the right text is insufficient if the requester loses access or the source changes.

**Study route:** Trace the three enforcement points, distinguish quote validity from claim support, then design the publication/withdrawal challenge. This guide is conceptual; no paid model or deployed service is required.

<details>
<summary>Reference: unit identity, prerequisites and verification limits</summary>

> **Capability:** AI-RAG-01 / AI-RELIABLE-01 · **Status:** Draft, unpiloted<br>
> **Prerequisite:** [SG-RAG-00](README.md)<br>
> **Effort:** 35–45 minutes, estimated<br>
> **Central question:** If a passage was permitted when search started, may the application still return it after revocation?<br>
> **Outcomes/artifact:** Explain authorization and freshness boundaries, distinguish citation validity from correctness, and defend a deletion/revocation test plan.

</details>

## Start with a race, not a filter

An agent opens a refund ticket. Search finds a policy. Before the draft returns, the agent's role is revoked. A system that checked permissions only while building yesterday's index can disclose the policy today.

Think of a library access card. An old photocopy of the access list cannot prove the card is still valid. The analogy stops at delivery: a returned answer cannot be recalled from someone's memory. Your consistency promise must identify the last authorization check, the source of current identity/permissions and the remaining race before delivery.

**Predict:** Does a model instruction saying “do not reveal tenant B” prevent a tenant A request from receiving tenant B's retrieved passage?

<details><summary>Reasoning</summary>

No. Keep tenant identity in trusted application state and exclude unauthorized evidence before ranking and provider submission. Model behavior cannot restore isolation after sensitive text has crossed that boundary.

</details>

## Three distinct enforcement points

1. Resolve the principal from an authenticated session in trusted application logic. A question, model argument or retrieved page cannot choose the tenant or role.
2. Restrict searchable evidence to currently allowed, current-version, unexpired documents. Store enough provenance to compare index snapshots with authoritative source revisions.
3. Before generation and before response delivery, revalidate identity, document permissions and versions. On revocation or drift, discard evidence and response; do not return stale snippets through diagnostic fields.

The local workbook has synthetic session names and a SQLite principal registry. It teaches these boundaries; it is not a web authentication implementation. Single-process rechecks demonstrate fail-closed behavior at explicit points, not atomic consistency across distributed services. A production design needs a documented consistency model, bounded caches and permission-change propagation. Even a final check cannot retract data already sent to a provider.

## Grounding and citations have different meanings

**Grounding** ties an assertion to evidence. A **citation** identifies where the evidence came from. A real citation can point to a passage that contradicts the answer or never supports its number. Checking a filename or schema is therefore insufficient.

The reference deliberately returns exact reviewed quotes rather than open-ended generated prose. A proposed quote must match an approved claim that actually survived parsing/chunking, and its chunk/document/revision/hash must still match current authorized state. The application builds the final answer from validated citations; the provider cannot supply a separate free-text answer or override identity.

This is a narrow design suitable for a curated policy lookup. It does not solve arbitrary entailment. Review annotations may themselves be wrong; agreement between code and fixtures cannot certify their truth. Free-form generation needs additional factual/semantic review, real-model evaluation, ambiguity handling and abstention. A quote can also be irrelevant to the question, so the demo explicitly limits supported intents instead of pretending to answer everything.

## Treat source instructions as data

A document saying “ignore previous instructions” is still untrusted document content. The mock extractive boundary passes reviewed claims rather than arbitrary document instructions, and rejects invented quotes and unknown citations. It has no tools or external side effects. This reduction in capability is useful: a source injection cannot acquire a refund tool that does not exist.

Do not generalize that result into a claim that a prompt blocks injection. A live provider seeing full passages can behave differently. Test source injection, tool-result injection and direct user instructions separately; keep consequential authorization in application code.

## Freshness, conflict and deletion

> [!IMPORTANT]
> Removing an index row establishes only that deletion surface. Saved answers, traces, source copies and provider-held data require their own retention and deletion evidence.

Freshness requires both current content revision and an explicit expiry policy. A new authoritative revision invalidates old chunks immediately; availability may temporarily fall while a new index is built. Version identity alone does not establish that a policy is still approved. The lab uses deterministic integer time to make expiry boundaries testable.

Two current sources can conflict. A curated claim-value annotation detects the deliberately conflicting fixture and routes it to review. That is not general contradiction detection. For free text, authority rules, source review and human capacity remain design requirements.

Deletion has multiple surfaces: source repository, parsed text, vector/lexical index, metadata, cached context, saved answers, traces, backups and provider retention. The lab removes searchable chunk rows and reviewed payloads and retains an ID-only tombstone. It does not securely erase SQLite pages, repository fixtures, previous reports, backups or provider data. Do not claim complete erasure from a successful SELECT returning no rows. Define each surface's owner, retention, deletion SLA and verification.

## Separate the measurements

Retrieval recall uses relevant **authorized** passages as its denominator. Answer outcome accuracy uses all requests, including abstentions/conflicts/denials; ready-answer quality uses ready responses. Count forbidden retrieval independently as a critical failure. A valid citation does not establish relevance, and a correct abstention is not a completed answer.

If 100 requests produce 60 ready answers, 55 correct ready answers and 40 appropriate abstentions, coverage is 60%, ready quality is 55/60, and correct outcome accuracy is 95/100. Review staffing must cover those 40 abstentions rather than treating them as free successes.

## Practice and reflection

**Pause and diagnose:** a passage was authorized at search time, sent to a provider, and revoked before response delivery. A final recheck blocks the answer. Which exposure did it prevent, and which did it not undo?

<details>
<summary>Compare the boundary</summary>

It prevented response delivery after the revocation was observed. It did not retract the passage already sent to the provider. Recheck before submission as well as delivery, document the remaining race, and define provider retention separately. A successful denial is not proof of atomic distributed consistency.

</details>

In the guided build, which starts at W-RAG-00, chapters [W-RAG-07–13](../../workbooks/langchain/02-rag-capstone-workbook/07-answer-generation.md) exercise these controls. Explain a revocation before provider submission versus one during generation; identify what each test can prevent. Independently design a recall-notice publication/withdrawal rule, where a correct exact match can still be ineligible because it has not been published yet.

Revision: principal means trusted requester identity; ACL means access rules; freshness means current and unexpired evidence; tombstone means a retained deletion marker; grounding means support for assertions. The next constraint is real-model behavior and service delivery, for which this offline control reference supplies no quality or deployment claim.

## Completion checkpoint

**You can now:** name the three enforcement points, explain why a citation can exist without supporting a claim, and list what deletion must reach.

**Show it:** your practice and reflection answers.

**Next:** the [guided RAG build, W-RAG-00](../../workbooks/langchain/02-rag-capstone-workbook/00-project-brief.md).

## Source and scope record

Verified against the repository implementation and tests on 2026-10-14. **Required local reference:** [grounded.py](../../workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/src/retrieval_lab/grounded.py), authorization, quote validation and deletion functions; 20 min, Python/SQLite prerequisite, no paid service. General retrieval sources are in [SG-RAG-00](README.md). No SDK or cloud capability is assumed here.
