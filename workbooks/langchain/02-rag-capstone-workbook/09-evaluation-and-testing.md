# W-RAG-09 - Measure evidence retrieval separately from answers

**Did the system retrieve eligible evidence, return a correct outcome, or merely produce JSON?**

> **Your goal:** Report retrieval and answer behavior separately with explicit denominators.<br>
> **You need:** [Interface outcomes](08-user-interface.md), [evaluation fundamentals](../../../study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) and [SG-RAG-02 — RAG evaluation](../../../study-guides/retrieval-foundations/rag-evaluation.md).<br>
> **Effort:** Part of the 3-4 hour guided/control estimate in [the brief](00-project-brief.md); record actual effort.<br>
> **You will produce:** An evaluation report, baseline comparison and an independent irrelevant-source test. **Status:** Draft; offline synthetic reference, unpiloted.

QuickCart's reference can retrieve the right policy and still reject a proposed answer. This lesson keeps those observations separate so a successful safety check does not look like a retrieval failure, or a good retrieval score like a completed answer.

**Starting state:** continue the personal package from W-RAG-08 with Python 3.11 via uv. No later evaluation harness is required for this offline exercise. Read `CASES` and `comparison` in `src/retrieval_lab/evaluation.py` first, and write the expected status and relevant authorized source for each case before inspecting results. The commands write a synthetic report and run tests; no provider, paid call or server is involved.

Working directory: your private `retrieval-lab` copy from W-RAG-01. Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run grounded-rag evaluate --output results/evaluation.json
uv run python -m unittest discover -s tests -v
```

Read CASES and comparison in src/retrieval_lab/evaluation.py before inspecting results. Fourteen versioned synthetic cases cover exact/paraphrase/identifier queries, irrelevant and missing facts, conflicts, source/output injection, role/tenant failures, unknown sessions, stale revisions, expiry and deletion. Fixture/case hashes identify the comparison. These public cases are development/control tests, not a confidential held-out benchmark.

**Observer boundary:** here the retrieval observer records ranked evidence whose reviewed claim survived chunking and eligibility checks. It does not audit every intermediate candidate or all possible data flows. Zero forbidden retrieval applies to those recorded observations and tested cases, not an exhaustive security guarantee.

Retrieval reports hits_at_3/relevant_passages and forbidden_retrieval_count. Relevant passages mean expected authorized documents in this curated fixture. Answer reports correct outcomes/all cases, coverage ready/all cases and quality correct ready/all ready. Correct abstention counts as a correct outcome but not a delivered answer. Overlap or repeated passage hits are deduplicated by document here; this is document recall, not fine-grained chunk recall.

Observed reference result: lexical document hits are 7/8 (87.5%), authored hybrid 8/8 (100%), and forbidden retrieval is zero for both. Hybrid correct outcomes are 14/14; five are ready, so coverage is 5/14 and ready quality 5/5. The rejected injected output still has a retrieval hit: the trusted observer measures retrieval independently from the returned answer. These counts demonstrate controls on curated fixtures, not general model quality.

Compare lexical baseline against hybrid. The money-back case justifies the authored feature change for this fixture. Source injection and invalid proposals test control behavior, not real-model resistance. Keep the baseline, report regressions and treat forbidden retrieval as a non-compensable failure. Do not let an aggregate hide permission failures.

Independent test: add an authorized but irrelevant positive-match source in your own fixture copy, write expectations before modifying retrieval, and inspect whether intent and reviewed-claim scope still justify the output. A ready answer with a real but irrelevant citation must fail your answer criterion. Preserve the baseline report and record fixture/case hashes for the changed experiment. The [versioned evaluation harness](../../llm/eval-harness/README.md) is later reference for frozen development/held-out administration, not a prerequisite to finish this lesson.

> [!IMPORTANT]
> A high correct-outcome rate can include many abstentions. Report coverage and ready-answer quality alongside it, and keep any forbidden retrieval visible as a critical failure.

## Check your reasoning

Attempt each question before opening its answer.

**Calculation:** In the reference hybrid run, what are the coverage and ready-quality figures?

<details>
<summary>Reveal worked reasoning</summary>

Coverage = 5 ready / 14 cases ≈ **35.7%**. Ready quality = 5 correct / 5 ready = **100%**. Correct outcomes = 14/14, because a correct abstention counts as a correct outcome but not as a delivered answer.

</details>

**Diagnosis:** Why does a rejected injected output still count as a retrieval hit?

<details>
<summary>Reveal worked reasoning</summary>

The trusted observer measures retrieval independently of what is returned. Retrieval found the right evidence; the answer stage correctly refused the injected output. Merging the two would hide which stage worked.

</details>

## Completion checkpoint

**You can now:** report retrieval and answer quality separately, with denominators, and treat forbidden retrieval as non-compensable.

**Show it:** your evaluation report and independent irrelevant-source test. Cleanup: generated results are removed in W-RAG-13.

**Reflect:** Which single number from your report would mislead a manager on its own, and what must sit beside it?

**Next:** [W-RAG-10 — Diagnose revocation](10-debugging-and-improvements.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
