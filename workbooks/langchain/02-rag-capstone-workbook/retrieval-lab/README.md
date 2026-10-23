# Offline retrieval mechanics checkpoint

**Can you explain why a passage was retrieved before adding a learned model?** This small package exposes parsing, chunking and ranking so you can inspect where evidence was lost.

> **Your goal:** Compare lexical, authored-vector and hybrid rankings, then diagnose their limits.<br>
> **You need:** [Retrieval foundations](../../../../study-guides/retrieval-foundations/README.md) and [Python packaging](../../../python/python-bridge/README.md).<br>
> **Effort:** 25 minutes reading, 50 guided, 20 fault repair and 40 independent work; estimated.<br>
> **You will produce:** Source/chunk reports, ranking comparisons and a tested independent retrieval decision. **Status:** Draft; unpiloted, synthetic mechanics only.

QuickCart is our fictional e-commerce platform. These synthetic refund/shipping policies let you contrast a paraphrase such as money back with an exact identifier such as `DELAY-42`. The vector representation is authored for the corpus; it is not learned embeddings or evidence of model quality.

**Project boundary:** use this package separately from your `langchain-learning` project. Keep its own metadata and environment; later framework chapters reuse their own helpers. Follow loading, chunking, representations and retrieval in chapters 03-06 for the detailed mechanics exercises, then return to the course map.

**Before running:** Python 3.11, uv and Windows PowerShell; no third-party runtime dependencies, credentials or paid resources. Work in a personal clone/copy and use only synthetic input. Reports include source text, so keep them private. No server is started. Preserve intended evidence before removing generated artifacts from your own project.

## Exact starting checkpoint and setup

`retrieval-lab-v1` is the mechanics checkpoint; `grounded-v1` completes the offline guided module reference. QuickCart is the default extension domain; Fernwood remains the earlier workbook's separate policy case. These local synthetic policies teach mechanics, not a complete approved business specification.

From repository root in PowerShell:

If you copied only this package, open PowerShell at that personal package root and omit the `Set-Location` line. Confirm `pyproject.toml` and `uv.lock` are present before synchronizing. Keep the reference fault and independent work in your own copy.

```powershell
Set-Location workbooks/langchain/02-rag-capstone-workbook/retrieval-lab
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run retrieval-lab --query "money back"
uv run retrieval-lab --query "DELAY-42" --output results/identifier.json
uv run retrieval-lab --query "zzzzunknown" --output results/no-signal.json
```

Expected for the current full reference: **43 tests pass**; the original mechanics checkpoint had nine. Default mechanics ingestion creates three chunks. `money back` has no lexical hits but positive toy-vector/hybrid hits; the exact code finds the shipping section; the unknown word yields empty rankings. Inspect passage text, not just filenames. Reports contain source text: use only synthetic input. No learned-model quality is demonstrated.

The [author execution record](../../../../docs/review-evidence/retrieval-foundations.json) preserves the observed scenarios, failure/repair results and limitations. Corpus bounds are 100 files and 100,000 bytes per file; the tokenizer is English/ASCII-oriented.

Follow [loading](../03-document-loading.md), [chunking](../04-chunking.md), [representations](../05-embeddings-and-indexing.md), then [retrieval](../06-retrieval.md), staying in this working directory.

## Inspect the implementation

`src/retrieval_lab/core.py` implements a constrained heading parser, section windows, content/configuration IDs, cosine, BM25 and RRF. `cli.py` saves source manifests and rankings. `fixtures/*.md` is the only supported input. `tests/test_retrieval.py` checks boundaries, invalidation, rejected input, exact codes, zero signal, dimensions and topic filtering.

The alias-count representation is **authored and corpus-dependent**, not learned embeddings or cached provider output. It rebuilds on each run; no persistent vector store is supplied. Topic filtering occurs before ranking and changes BM25 statistics; it is not an ACL check.

> [!IMPORTANT]
> A successful paraphrase lookup here demonstrates the authored mapping and ranking pipeline. It does not establish general semantic retrieval, authorization or live-model quality.

Acceptance: submit actual reports, source/version evidence, fault diagnosis and the W-RAG-06 independent tests/decision. Unchanged reference tests alone do not demonstrate independent competence.

## Reference for the next capability: grounded RAG

The following extension belongs to the later permissions/grounding route. Read it after mechanics; these commands are not prerequisites for comparing retrieval rankings. Run only after the setup above, from this package root.

The same package now also supplies `grounded-v1`; use [W-RAG-00–13](../README.md) for the complete guided offline route. `grounded.py` adds a trusted SQLite principal/document registry, permission filtering before ranking/provider submission, freshness checks, reviewed claim/citation validation and logical index deletion. `evaluation.py` compares lexical/hybrid retrieval separately from answer outcomes over 14 synthetic cases. Local time is fixed at 100 in CLI scenarios; fixture expiry is 1000.

From this directory, after syncing:

```powershell
uv run grounded-rag ask --query "money back" --output results/answer.json
uv run grounded-rag evaluate --output results/evaluation.json
uv run grounded-rag drill --output results/revocation-drill.json
uv run python exercises/check_recall.py --reference
```

The current reference suite has 43 tests (including 14 lifecycle and eight optional-reranking control tests); the historical nine-test count describes the mechanics checkpoint only. The full independent recall starter intentionally stops until implemented. Fixture identities and metadata are trusted local seed inputs, not production authentication. Every CLI invocation uses a fresh in-memory database; persisted deletion is separately tested with a temporary file. Saved reports and original fixtures are not erased by index deletion. No arbitrary-source entailment, learned embeddings, live model or deployment is claimed.

## Publish knowledge changes

After W-RAG-05, build the [knowledge-lifecycle driver](knowledge-lifecycle.md) before W-RAG-06. It adds 150-195 minutes within phase 3: source-level incremental Markdown/CSV publication, duplicate quarantine, revision invalidation, failed extraction, complete rebuild and persisted logical deletion. Use the same package and lockfile; keep the walkthrough separate from the framework index. Supplied reference correctness, your guided driver and your independent change-feed evidence are distinct.

## Optional reranking comparison

After the grounded permission controls, try the [bounded reranking comparison](reranking-comparison.md) only if you want to diagnose a first-stage ranking miss. It takes 60-90 optional minutes in the same package. The authored scorer fixes one fixture case but regresses another; it does not establish learned-reranker quality or justify compulsory adoption. Default grounded application behavior stays unchanged.

## Troubleshooting and cleanup

| Symptom | Likely cause | Diagnostic action |
|---|---|---|
| Exit 2 | Unsupported/empty input or invalid overlap | Inspect corpus and size/overlap before retrying |
| Missing condition | Parsing loss or window boundary | Compare original section with manifest offsets/text |
| Paraphrase absent | Authored features lack the mapping | Add a diagnostic case; do not claim general semantics |
| Changed ranking after filtering | Candidate set/statistics changed | Inspect filtered documents |
| Stale report | Saved snapshot from an old run | Rerun and compare source/configuration hashes |

Preserve private evidence, then remove generated `results` and `.venv` only from your own package after checking their resolved paths. No continuing costs or services. The later grounded reference adds permissions/freshness/deletion; live-model and deployed delivery evidence remain separate. [Course map](../../../../README.md).


## Completion checkpoint

**You can now:** inspect which source/chunk reached each ranking and explain the limits of the authored representation.

**Show it:** your three query reports, a diagnosed failure with its repaired rerun, and the independent W-RAG-06 checks/decision. Default tests alone do not complete the independent work.

**Next:** [W-LC-07 - Embeddings and Similarity](../../01-learning-workbook/07-embeddings-and-similarity.md). Keep this package for the later grounded build; do not transfer its environment or reports into the framework index.
