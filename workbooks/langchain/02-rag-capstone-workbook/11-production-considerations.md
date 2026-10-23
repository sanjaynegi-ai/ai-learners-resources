# W-RAG-11 - Specify deletion and delivery limits

**Which stored copies does deletion actually reach?**

> **Your goal:** Define deletion surfaces, ownership and delivery limits.<br>
> **You need:** [Revocation diagnosis](10-debugging-and-improvements.md) and its incident evidence.<br>
> **Effort:** Part of the guided/control estimate in [the brief](00-project-brief.md); record actual effort.<br>
> **You will produce:** A deletion inventory with owner, access, retention and verification. **Status:** Draft; offline synthetic reference, unpiloted.

Continue in the personal QuickCart package; this chapter asks for inspection and an operational design, not new cloud resources. Inspect `Store.delete` in `src/retrieval_lab/grounded.py` and the restart regression. A transaction removes chunk rows and clears reviewed payload and metadata fields, retaining the document ID and deletion marker. The restarted database cannot retrieve that document. Seed configuration and original teaching Markdown remain unchanged so the drill can be reproduced. Saved reports may retain previous answers: do not confuse index deletion with erasing every copy.

Write a deletion inventory: authoritative source, parsed/index payload, saved responses, logs/traces, provider retention and backups. State owner, access, retention and verification for each. SQLite row deletion does not guarantee physical page erasure. This reference has no cache invalidation service, provider retention API, backup purge, secure disk erase or legal-retention implementation.

Use one row per surface: **copy/location → owner → readers → retention/deletion trigger → verification → remaining limitation**. Mark surfaces absent from this offline design as absent, rather than claiming a test deleted them. For a hypothetical live provider, record the unresolved retention requirement without inventing an implemented control.

> [!IMPORTANT]
> A successful query returning no rows proves a lookup result. It does not prove secure erasure, backup deletion or removal of a quote from prior reports.

Freshness uses current revision/hash plus expires>now; tests use deterministic integer time. A publisher invalidates an old revision before rebuilding, accepting temporary abstention. ACL changes are read from current metadata and checked before and after mock generation. Single-process tests do not prove distributed consistency or a global deletion SLA.

The reference bounds questions to 500 characters, retrieval to three candidates and reviewed context to 5,000 characters, with one local generation call. It does not impose a wall-clock timeout on arbitrary injected Python callbacks. A live adapter needs the prior deadline/cancellation/budget controls and separately reported usage. Do not attach consequential tools to this reference without explicit trusted authorization.

Operational handoff: preserve code/fixture/report versions, redacted failure IDs, incident ownership, rollback plan and exact teardown. No service remains running; stop any future server you start. Next: W-RAG-12.

## Check your reasoning

Attempt each question before opening its answer.

**Diagnosis:** After `Store.delete` and a restart, a saved report still shows the deleted quote. Is deletion broken?

<details>
<summary>Reveal worked reasoning</summary>

No. Index deletion removed the chunk rows and reviewed claims. The saved report is a separate copy. Your deletion inventory must list it with an owner and a retention rule; index deletion is not erasure of every copy.

</details>

**Decision:** Which listed copy can this reference not delete at all?

<details>
<summary>Reveal worked reasoning</summary>

Provider retention (and backups). The reference has no provider retention API or backup purge, so the inventory records them as outside its control.

</details>

## Completion checkpoint

**You can now:** list every copy deletion must reach and say honestly which ones this reference removes.

**Show it:** your deletion inventory.

**Reflect:** Which copy in your inventory has no clear owner, and who should own it?

**Next:** [W-RAG-12 — Transfer to product recall notices](12-capstone-challenges.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
