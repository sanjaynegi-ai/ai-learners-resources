# W-RAG-04 - Defend a chunk boundary

**Does the selected passage retain the condition as well as the rule?**

> **Your goal:** Choose an evidence-preserving chunk boundary and test it.<br>
> **You need:** [Document loading](03-document-loading.md) in the same personal package.<br>
> **Effort:** 5 minutes reading and 15 experiment, estimated within the combined mechanics checkpoint.<br>
> **You will produce:** Compared manifests, a boundary diagnosis and your own regression assertion. **Status:** Draft; offline reference, unpiloted.

Continue in `retrieval-lab` at the same checkpoint. `ingest()` in `src/retrieval_lab/core.py` windows each heading section independently. Default 40 words and overlap 8 preserve all three fixture sections as three chunks. These are whitespace words, not provider tokens or original character offsets.

**Before running:** retain W-RAG-03's personal source copy and use its Python 3.11/uv environment. The three commands below save separate synthetic manifests; no embedding provider or paid service is called. Keep the original fixture for comparison and make the independent change only in your own copy.

Predict whether a smaller window helps, then run:

Working directory: `retrieval-lab` (the repository checkpoint or your private copy). Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run retrieval-lab --query "damaged shipment" --output results/default.json
uv run retrieval-lab --query "damaged shipment" --size 8 --overlap 0 --output results/small.json
uv run retrieval-lab --query "damaged shipment" --size 16 --overlap 4 --output results/overlap.json
```

Inspect passage text. With size 8, the opening damaged-shipment chunk loses part of the evidence requirement. This is the deliberate failure: retrieval can find the right opening words but incomplete instructions. Repair by retaining the complete short section or selecting a measured window/neighbor expansion that preserves its condition. Overlap alone offers no universal guarantee.

Compare offsets, repeated words and IDs. Source/configuration-derived IDs change with window settings. This lab rebuilds in memory and saves snapshots; it does not implement incremental indexing or deletion.

**Independent change:** In your own fixture copy, add a synthetic rule and exception across a window boundary. Add `tests/test_boundaries.py` showing that the selected chunking retrieves both together. Do not assert only chunk count: acceptance concerns evidence meaning. Run the full tests after repair and record which query benefited.

<details>
<summary>After your attempt: boundary-test hint</summary>

Compare full-section retention against a small window. Assert that the passage actually retrieved for your chosen query contains both the rule and exception; a different chunk containing the missing condition is not enough by itself. Explain the additional context-budget cost and what your test does not generalize to.

</details>

## Check your reasoning

Attempt each question before opening its answer.

**Prediction:** Does `--size 8 --overlap 0` improve the damaged-shipment result?

<details>
<summary>Reveal worked reasoning</summary>

No. It still finds the opening words, but the chunk loses part of the evidence requirement. Smaller windows can cut a rule away from its condition. Repair by keeping the full short section or a measured neighbor expansion.

</details>

**Calculation:** With size 16 and overlap 4, how many new words does each window add after the first?

<details>
<summary>Reveal worked reasoning</summary>

16 − 4 = **12** new words per window. Overlap only repeats 4 words, so a condition more than 4 words away from its rule can still be split. Overlap is not a guarantee.

</details>

## Completion checkpoint

**You can now:** choose a chunk boundary that keeps a rule with its condition, and defend it with a test.

**Show it:** compared manifests and your boundary regression test. Cleanup: see the lab README.

**Reflect:** What did keeping the condition with its rule cost in context budget, and when would that trade stop being worth it?

**Next:** [W-RAG-05 — Inspect representation](05-embeddings-and-indexing.md).

[Cleanup/troubleshooting](retrieval-lab/README.md) - [Next: W-RAG-05](05-embeddings-and-indexing.md)
