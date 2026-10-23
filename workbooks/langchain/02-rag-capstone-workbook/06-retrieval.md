# W-RAG-06 - Compare lexical, vector and hybrid candidates

**Which added retrieval complexity fixes a miss you actually observed?**

> **Your goal:** Compare lexical, vector and hybrid results and defend a bounded decision.<br>
> **You need:** [Representation mechanics](05-embeddings-and-indexing.md) in the same personal package.<br>
> **Effort:** 5 minutes reading, 10 comparison and 40 independent work; estimated within the combined checkpoint.<br>
> **You will produce:** Three ranking reports, transfer tests and a 200-word retrieval decision. **Status:** Draft; offline synthetic reference, unpiloted.

Continue in `retrieval-lab`. The lexical branch uses BM25 with k1=1.2 and b=0.75; the authored-vector branch uses cosine. Hybrid uses reciprocal rank fusion with c=60 and one-based ranks. Only positive-score candidates participate; ties break by chunk ID. Scores are not interchangeable probabilities.

**Starting state:** keep W-RAG-05's personal package, source copy and representation version. Use Python 3.11 via uv; the following commands are offline and save separate reports. QuickCart's exact carrier code and refund paraphrase test different requirements, so decide the expected passage before inspecting rank positions.

Predict the identifier and paraphrase behavior:

Working directory: `retrieval-lab` (the repository checkpoint or your private copy). Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run retrieval-lab --query "DELAY-42" --output results/code.json
uv run retrieval-lab --query "money back" --output results/paraphrase.json
uv run retrieval-lab --query "refund" --topic refunds --output results/topic.json
```

Inspect actual passages. Topic selection precedes scoring and changes lexical document frequencies. It is caller-supplied metadata, not identity or permission enforcement. Do not expose this reference as a secure multi-tenant service.

> [!TIP]
> Beside each result, record the required condition that survived retrieval. A filename hit can look successful while the returned passage omits the policy exception.

**Break and diagnose:** Query "cash returned": fusion cannot invent a relationship missing from every representation. Repair the authored demo as in W-RAG-05 or propose a separately evaluated learned experiment. Add a regression test for zero signal. Query "refund" too: a shipping disclaimer mentioning refunds may still be insufficient evidence for a refund decision.

**Independent transfer:** In a separate synthetic corpus copy, add a new carrier code and support phrase absent from `ALIASES`. Write expectations before changing features. Add `tests/test_transfer.py`: exact code retrieves the right section; the explicitly authored mapping recovers the phrase; an unknown/no-signal query returns no fabricated result. Include a condition at a chunk boundary. Compare all methods and submit reports, tests, source/representation versions and a 200-word decision explaining whether hybrid earns its complexity.

<details><summary>Progressive hints and worked reasoning</summary>

Start with lexical retrieval for the exact code. Inspect tokenization and the alias map for the phrase. Version the authored change and preserve the no-answer test. Manually calculate 1/(60+rank) for fused candidates. A defensible result may retain lexical search for this tiny corpus. Filename-only hits do not prove the required condition was retrieved.

</details>

Run all tests after repair. No learned-model quality or general retrieval benchmark is established. Continue with [W-RAG-07](07-answer-generation.md) for permission-aware extractive answers, then W-RAG-09 for separate retrieval/answer evaluation.

**Decision check:** if lexical search retrieves every required exact-code passage and hybrid adds no relevant evidence, what would justify keeping hybrid?

<details>
<summary>Compare your reasoning</summary>

Not the extra score or the more sophisticated name. Keep the simpler baseline unless measured paraphrase coverage or another requirement justifies the additional representation and fusion behavior. State the tested corpus and queries; the decision may change with new evidence.

</details>

## Completion checkpoint

**You can now:** compare lexical, vector and hybrid rankings on one corpus and decide whether hybrid earns its complexity.

**Show it:** three ranking reports, your transfer tests and the 200-word decision. Cleanup: see the lab README.

**Reflect:** What evidence would make you change your hybrid decision for a larger corpus?

**Next:** [W-RAG-07 — Generate only a verifiable quote](07-answer-generation.md).

[Cleanup/troubleshooting](retrieval-lab/README.md) - [Course map](../../../README.md)

[Previous: knowledge lifecycle](retrieval-lab/knowledge-lifecycle.md) - [Phase overview](README.md)

**Optional after the grounded controls:** [rerank a diagnosed shortlist miss](retrieval-lab/reranking-comparison.md), 60-90 minutes. Compare per-case gain/regression and local overhead before deciding; the authored simulation is not learned-model quality evidence. Continue to W-RAG-07 first on the recommended route.
