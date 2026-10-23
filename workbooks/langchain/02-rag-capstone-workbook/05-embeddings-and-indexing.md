# W-RAG-05 - Inspect representation before choosing a store

**What does a vector match demonstrate when the representation is authored rather than learned?**

> **Your goal:** Explain the alias-count representation, cosine and its failure boundaries.<br>
> **You need:** [Chunking](04-chunking.md) and [vector mechanics](../../../study-guides/retrieval-foundations/README.md).<br>
> **Effort:** 5 minutes reading and 10 inspection; estimated within the combined mechanics checkpoint.<br>
> **You will produce:** A cosine calculation, zero-signal observation and versioned failure/repair evidence. **Status:** Draft; offline synthetic reference, unpiloted.

Continue in `retrieval-lab`. Read `toy_tokens()`, `ALIASES` and the vector branch of `rank()` in `src/retrieval_lab/core.py`. The demo substitutes authored synonyms and counts vocabulary occurrences. It exposes the arithmetic; it is not trained semantic retrieval. Its corpus-derived dimensions cannot be reused after changing the corpus without rebuilding.

**QuickCart context:** the fictional shop's policy says refund, while a customer asks for money back. The authored mapping makes this one relationship inspectable. It does not learn how other customers will phrase the request.

**Before running:** use the same personal package and Python 3.11/uv environment as W-RAG-04. Commands use local fixtures and write synthetic reports; no provider account, paid call or server is involved. Preserve the earlier no-signal report if you need a before/after comparison, since the named output can be overwritten.

Predict the three rankings for "money back," then run:

Working directory: `retrieval-lab` (the repository checkpoint or your private copy). Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run retrieval-lab --query "money back"
uv run retrieval-lab --query "zzzzunknown" --output results/no-signal.json
uv run python -m unittest discover -s tests -v
```

The paraphrase becomes `refund refund` through explicit aliases; lexical search has no match. Unknown vocabulary creates a zero query vector and empty results. The cosine test checks (1,1) against (1,0), approximately 0.707, and rejects dimensions/nonfinite values. Returning zero for zero norm is an explicit no-signal policy.

**Break and repair:** Query "cash returned." The representation lacks those aliases. Add a focused test and an explicitly authored mapping in your own copy; bump `TOY_EMBEDDING_VERSION` when behavior changes. Explain why teaching one example proves no general paraphrase capability.

> [!IMPORTANT]
> Version the representation when you change aliases, not just the corpus. A newly passing phrase demonstrates the rule you added; it is not evidence that unseen paraphrases will work.

A learned route already exists in [W-LC-07](../01-learning-workbook/07-embeddings-and-similarity.md). Use that lesson's provider setup and budget. Live embeddings were not run for this checkpoint. Record compatible query/document model revision, preprocessing, dimension, metric and source/chunk hashes. Equal dimensions do not imply compatible spaces; model replacement needs rebuilding and evaluation.


## Check your reasoning

Attempt each question before opening its answer.

**Calculation:** What is the cosine similarity of (1, 1) and (1, 0)?

<details>
<summary>Reveal worked reasoning</summary>

Dot product 1; lengths √2 and 1; cosine = 1/√2 ≈ **0.707**. A zero vector has no direction, so the lab returns no signal instead of dividing by zero.

</details>

**Diagnosis:** Why can a high cosine score still return an obsolete rule?

<details>
<summary>Reveal worked reasoning</summary>

Similarity measures closeness of representation, not authority or freshness. An expired revision can be the closest match. Freshness and permission checks are separate application controls. The lifecycle step after this chapter exercises publication identity and invalidation; W-RAG-07 then applies these controls to answers.

</details>

## Completion checkpoint

**You can now:** explain what an authored-vector match demonstrates, compute a cosine score, and say why similarity is not authority or freshness.

**Show it:** your cosine explanation, zero-signal result, failing phrase test and passing rerun after the versioned mapping change. Cleanup: preserve evidence and follow the [package guidance](retrieval-lab/README.md#troubleshooting-and-cleanup).

**Reflect:** Which retrieval result would you have trusted before this chapter that you now treat as unproven?

**Next:** [build the knowledge-lifecycle driver](retrieval-lab/knowledge-lifecycle.md), then continue to [W-RAG-06 - Retrieval](06-retrieval.md). The lifecycle extension takes 150-195 minutes beyond this chapter's 15-minute representation checkpoint; it reuses this package and replaces a repeated conceptual rebuild discussion with observable publication checks.

[Cleanup/troubleshooting](retrieval-lab/README.md) - [Phase overview](README.md)
