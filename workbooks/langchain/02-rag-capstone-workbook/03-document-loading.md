# W-RAG-03 - Preserve evidence during loading

**Did extraction preserve the policy, or merely return nonempty text?**

> **Your goal:** Inspect source fidelity and diagnose an unsupported or empty source.<br>
> **You need:** [Retrieval foundations](../../../study-guides/retrieval-foundations/README.md) and the [checkpoint setup](retrieval-lab/README.md).<br>
> **Effort:** 10 minutes reading and 15 inspection, estimated within the combined mechanics checkpoint.<br>
> **You will produce:** A source-to-manifest comparison and rejected-source failure/repair evidence. **Status:** Draft; offline reference, unpiloted.

Start at the supplied `retrieval-lab-v1` mechanics checkpoint, either directly from its setup or in the personal package created in W-RAG-01. The larger guided build is not needed for this exercise. If you completed it earlier, compare your saved evidence with the current source/configuration and recheck only what changed. Stay in that same package for all commands; do not switch to the separate `langchain-learning` environment.

QuickCart's synthetic policy has evidence requirements as well as a refund topic. Your acceptance check is whether those conditions survive extraction, not merely whether the loader returns text. No paid calls or services are involved; outputs contain source passages, so use only synthetic input and preserve your own evidence before cleanup.

Predict whether a heading-only document should be accepted. Read `ingest()` in `src/retrieval_lab/core.py`: the parser accepts bounded UTF-8 Markdown in a flat directory, retains headings as section metadata and collapses blank lines. It does not support general Markdown, PDF, OCR, HTML or tables. A heading inside a code fence would be misread; supporting that requires a proper parser.

Working directory: `retrieval-lab` (the repository checkpoint or your private copy). Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run retrieval-lab --query "damaged shipment"
uv run python -m unittest discover -s tests -v
```

Compare `fixtures/refunds-policy.md` with `results/retrieval.json`: the photo, identifier and packaging conditions must survive. Explain why document ID, section, source hash and within-section word offsets help investigate a disputed result. They do not establish authority or permissions.

**Break and repair:** Create `fixtures/unsupported.txt` with harmless synthetic text. The command must exit 2 rather than silently omit it. Diagnose the allowlist, remove that exact test file and rerun both commands. A real unsupported document needs an approved parser and extraction checks, not a renamed extension. Regression tests already cover unsupported and empty input.

**Independent check:** In a separate personal corpus, create a heading-only Markdown document and verify rejection. Use the CLI's `--corpus` argument to select that directory and keep `--output` outside it. Add a meaningful paragraph and verify acceptance. Record both exits; explain what you would inspect before supporting a policy table.

<details>
<summary>After your attempt: inspection hint</summary>

Compare source meaning with the manifest, not just text length. Nonempty output is insufficient if row associations, numeric units or an exception are lost. Never place a generated report inside the input corpus; the CLI rejects that boundary.

</details>

## Check your reasoning

Attempt each question before opening its answer.

**Prediction:** Should a heading-only Markdown document be accepted?

<details>
<summary>Reveal worked reasoning</summary>

No. It contains nothing that can be cited, so the loader rejects it. Rejecting it makes the gap visible instead of silently shrinking the corpus.

</details>

**Decision:** Why is a loud failure (exit 2) for `unsupported.txt` better than silently skipping it?

<details>
<summary>Reveal worked reasoning</summary>

A skipped source quietly removes policies. Later, an abstention looks like "no policy exists" when the real cause is an ingestion failure. Exit 2 points straight at the cause.

</details>

## Completion checkpoint

**You can now:** show that loading preserved a policy's conditions and provenance, and that an unsupported source fails loudly.

**Show it:** your source-to-manifest comparison and the diagnosed rejection. Cleanup: remove the test file you created; see the lab README for the rest.

**Reflect:** What would change in your inspection if the next policy arrived as a table or a PDF?

**Next:** [W-RAG-04 — Defend a chunk boundary](04-chunking.md).

[Cleanup/troubleshooting](retrieval-lab/README.md) - [Next: W-RAG-04](04-chunking.md) - [Course map](../../../README.md)
