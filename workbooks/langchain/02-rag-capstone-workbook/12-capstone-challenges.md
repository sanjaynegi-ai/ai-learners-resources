# W-RAG-12 - Transfer to product recall notices

**Can an exact SKU match identify a notice that must not yet be returned?**

> **Your goal:** Transfer the policy design to supplier-scoped recall notices.<br>
> **You need:** [Deletion and delivery limits](11-production-considerations.md) and the guided reference evidence.<br>
> **Effort:** 2-3 hours independent transfer, estimated in [the brief](00-project-brief.md).<br>
> **You will produce:** Independent code/tests/reports, a threat model, deletion inventory and trade-off note. **Status:** Draft; offline synthetic reference, unpiloted.

Build an independent recall-notice lookup for QuickCart suppliers. This changes evidence format, identity scope and time applicability; copying the policy solution is insufficient. Use synthetic CSV rows with SKU, supplier, published_at, withdrawn_at and notice text. Support exact SKU retrieval, supplier isolation, current publication/withdrawal rules, cited row/version and abstention when no notice is effective. Treat notice text as untrusted and recheck eligibility before output.

**Before implementing:** preserve the policy reference and work in your personal Python 3.11/uv package. Write a short access/time contract and expected outcomes first. Use only synthetic suppliers/notices; the extension needs no paid provider, server or real product-recall publication. Save generated evidence separately from source fixtures.

Implement your CSV parser and row provenance in new files beside your private project; keep the policy reference intact. Reject duplicate SKU/version keys, malformed timestamps and missing supplier identity rather than silently coercing. A customer-facing public view may see only published notices, while suppliers see only their own allowed records. Define this access policy in trusted logic, not CSV text or model arguments.

The timestamp contract is [published_at, withdrawn_at): publication instant included; withdrawal instant excluded; None means no withdrawal. Nonnegative integer timestamps only, reject bool and withdrawal before publication. Implement exercises/recall_policy.py, then run:

Working directory: your private `retrieval-lab` copy from W-RAG-01. Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run python exercises/check_recall.py
```

The starter intentionally raises NotImplementedError. Public reasoning aid:

```powershell
uv run python exercises/check_recall.py --reference
```

Acceptance also requires integration tests: exact SKU across two suppliers, future notice, withdrawal during retrieval, unknown SKU, conflicting active revisions, injected notice instructions and deletion after a prior successful response. Report retrieval recall and answer correctness separately; merely passing the policy checker is insufficient. Preserve your independently written expectations before tuning.

<details>
<summary>After your attempt: progressive hints and boundary reasoning</summary>

Parse rows first, scope by trusted identity, time-filter, then exact-match rank. A correct SKU match can still be ineligible. The time rule is `published_at <= now` and (`withdrawn_at is None` or `now < withdrawn_at`), followed by eligibility rechecking at delivery. Keep parser, permission and time failures distinguishable in your tests.

</details>

> [!IMPORTANT]
> Passing `check_recall.py` establishes the eligibility helper's tested behavior. It does not establish CSV fidelity, supplier isolation, safe delivery or deletion; submit the integration evidence as well.

Submit code, tests, actual reports, threat model, deletion inventory and a 300-word trade-off note; disclose assistance. Explain one alternative you rejected and which unfamiliar requirement would make you revisit it.

## Check your reasoning

Attempt each question before opening its answer.

**Calculation:** A notice has `published_at = 100` and `withdrawn_at = 200`. Is it eligible at `now = 100`, `150` and `200`?

<details>
<summary>Reveal worked reasoning</summary>

Yes at 100 (publication instant included), yes at 150, **no** at 200 (withdrawal instant excluded). The window is `[published_at, withdrawn_at)`.

</details>

**Decision:** The exact SKU matches but belongs to another supplier. Return it?

<details>
<summary>Reveal worked reasoning</summary>

No. Scope by trusted identity before ranking. A correct SKU match can still be ineligible; returning a notice from another supplier is forbidden evidence exposure, a critical gate in W-RAG-13.

</details>

## Completion checkpoint

**You can now:** build a recall-notice lookup with supplier isolation and publication-window rules, without copying the policy solution.

**Show it:** your code, tests, reports, threat model, deletion inventory and trade-off note, with assistance disclosed. Cleanup: generated results are removed in W-RAG-13.

**Reflect:** Which part of the policy solution did you have to rethink for recall notices rather than reuse?

**Next:** [W-RAG-13 — Defend the build and clean up](13-revision-and-assessment.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
