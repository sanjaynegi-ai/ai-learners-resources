# W-RAG-07 - Generate only a verifiable quote

**Can a real citation ID still carry an invented claim?**

> **Your goal:** Validate exact reviewed quotes and handle missing or conflicting evidence.<br>
> **You need:** [Retrieval comparison](06-retrieval.md), earlier mechanics and [permissions/grounding](../../../study-guides/retrieval-foundations/permissions-and-grounding.md).<br>
> **Effort:** Part of the 3-4 hour guided/control estimate in [the brief](00-project-brief.md); record actual effort.<br>
> **You will produce:** Ready/abstained/conflict reports and an invented-quote regression test. **Status:** Draft; offline synthetic reference, unpiloted.

Continue in your private `retrieval-lab` copy from W-RAG-01. QuickCart's policy lookup now moves from ranking to a validated answer. Read `extractive_provider` and `answer` in `src/retrieval_lab/grounded.py`. This boundary is a mock generator over curated evidence, not an LLM. It proposes citation IDs and quotes only; the application constructs the returned answer from validated values. Free text, unknown fields, invented IDs and changed quotes are rejected.

**Before running:** keep the package's Python 3.11/uv environment and trusted synthetic seed files. Each CLI invocation seeds a fresh in-memory database and writes a result file; these commands do not demonstrate persistent user state. No paid provider or service is involved. Predict `ready`, `abstained` or `conflict` for each query before executing, then inspect the citations rather than only the status.

Working directory: your private `retrieval-lab` copy from W-RAG-01. Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run grounded-rag ask --query "refund evidence" --output results/refund.json
uv run grounded-rag ask --query "refund amount" --output results/missing.json
uv run grounded-rag ask --query "conflict window" --output results/conflict.json
```

Compare your prediction with the actual citation, document revision and hash. The supported intent allowlist deliberately rejects other questions; a plausible generic quote is insufficient evidence for an unknown numeric limit.

Build/repair step: in your learner copy, temporarily replace the exact quote equality check with a check only that the ID exists. Add a provider in a test returning an invented quote against a valid ID. Observe the test failure, restore exact equality and rerun all tests. This is meaningful output validation, not simply JSON parsing. Keep the regression test.

> [!IMPORTANT]
> Exact equality proves that the returned quote matches the reviewed value. It does not prove the review annotation is correct or that an arbitrary quote answers the question. Keep supported-intent scope and curator review explicit.

Reviewed claim extraction reduces source injection exposure: arbitrary source instructions are not passed through as directives. It does not establish general prompt-injection immunity or semantic correctness of curators. Live provider quality, latency, billing and cancellation are separate evidence; reuse prior reliable-calls work before adding an adapter. Next: W-RAG-08.

## Check your reasoning

Attempt each question before opening its answer.

**Prediction:** What status does each of the three commands return?

<details>
<summary>Reveal worked reasoning</summary>

`refund evidence` → **ready**; `refund amount` → **abstained** (no supported evidence for a numeric limit); `conflict window` → **conflict** (annotated conflicting sources are not resolved by picking one).

</details>

**Diagnosis:** Why is checking only that a cited ID exists not enough?

<details>
<summary>Reveal worked reasoning</summary>

A real ID paired with an invented quote would pass. Exact quote equality ties the claim to the evidence; the build-and-repair step shows the regression test catching it.

</details>

**Decision:** A colleague proposes accepting a quote when it is at least 90% similar to the source text. Do you agree?

<details>
<summary>Reveal worked reasoning</summary>

No. Near matches allow small edits that change meaning, such as removing "not" or changing a number. Exact equality is a simple, testable invariant; if the source wording must change, re-review the claim instead of loosening the check.

</details>

## Completion checkpoint

**You can now:** return only exact, validated quotes, and abstain or report a conflict otherwise.

**Show it:** the three result files and your invented-quote regression test. Cleanup: nothing keeps running; generated results are removed in W-RAG-13.

**Reflect:** Which check in the answer path would you least want to remove, and why?

**Next:** [W-RAG-08 — Expose status honestly](08-user-interface.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
