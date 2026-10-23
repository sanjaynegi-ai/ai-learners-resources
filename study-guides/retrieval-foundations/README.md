# SG-RAG-00 — From a document to useful evidence

**What must survive between the original policy and the passage shown to a model?**

> **Your goal:** Explain parsing loss, choose chunk boundaries and justify a retrieval method.<br>
> **You need:** The [Python bridge](../../workbooks/python/README.md) and [models/context guide](../llm-foundations/docs/00-how-llms-generate-text.md).<br>
> **Effort:** 50-65 minutes reading, estimated.<br>
> **You will produce:** A worked retrieval score, diagnosed evidence loss and a chunking decision. **Status:** Draft; unpiloted.

QuickCart is our fictional e-commerce platform. Its customers ask about damaged deliveries and refunds; retrieval must preserve the policy conditions that make an answer applicable.

**Study route:** Follow the source through parsing, chunking, metadata and ranking. Work the cosine/RRF examples before the transfer challenge. No installation, account or paid call is needed to read this guide.

<details>
<summary>Reference: unit identity, prerequisites and verification limits</summary>

> **Capability:** AI-RETRIEVE-01 · **Status:** Draft, unpiloted<br>
> **Prerequisites:** [Python bridge](../../workbooks/python/README.md); [models/context](../llm-foundations/docs/00-how-llms-generate-text.md)<br>
> **Study effort:** 50–65 minutes, estimated<br>
> **Central question:** What must survive between the original policy and the passage shown to a model?<br>
> **Outcomes:** Explain parsing loss, choose chunk boundaries, compare retrieval methods and specify provenance.<br>
> **Artifact:** A retrieval decision with a worked score, diagnosed failure and justified chunking choice.

</details>

## A policy miss before a model call

QuickCart's customer asks for “money back” after a damaged delivery. The policy says “refund,” while the order identifier is essential. Keyword search may miss the paraphrase. A semantic retriever may find general policy but miss an exact carrier code. Returning a high score does not establish an answer.

Retrieval-augmented generation (RAG) supplies selected external evidence to a model before generating a response. This guide covers evidence selection. Adding documents does not establish authority, authorization, truth or successful completion.

Think of a librarian selecting passages before you write. This separates search from writing, but the analogy has limits: a librarian can interpret authority and contradictions. An index requires explicit application policy and evaluation.

**Predict:** A chunk says “refund permitted,” but the exception is in another chunk. Can a better embedding repair this?

<details><summary>Reasoning</summary>

Not reliably. Ranking cannot reverse arbitrary information loss. Keep a rule and its exception together where possible, or deliberately retrieve surrounding context.

</details>

## Ingestion must preserve meaning

**Ingestion** transforms approved sources into searchable representations. **Parsing** extracts text and structure. A Markdown heading, PDF table, scan and HTML menu need different decisions. Nonempty extracted text is not proof of faithful extraction.

Imagine a table with columns for condition, credit limit and approval. Reading columns instead of rows can attach a limit to the wrong condition. Preserve associations and units; compare representative extractions with originals. OCR may misread numbers, and repeated headers may dominate ranking. Never silently discard failed sources and report a complete corpus.

Record accepted/rejected sources, rejection reasons, content hashes, parser/configuration versions and extraction counts. Decide whether a rejection blocks publication or visibly quarantines one source. The small lab fails the whole corpus on unsupported input; a larger pipeline might publish an explicitly incomplete index.

## Chunk boundaries determine the evidence unit

A **chunk** is the indexed passage selected by retrieval. Prefer meaningful structure: a question with its answer, a heading's paragraphs, or a table with its headers. Split unusually long sections using bounded windows. Fixed windows are repeatable but can separate exceptions from rules. Structure-aware parsing costs more work and still needs limits.

**Overlap** repeats boundary text. With 100 whitespace words, window 40 and overlap 10, starts are 0, 30 and 60: three chunks cover the text. Stored lengths total 120 words, a 20% repetition overhead. Independent section boundaries can change this count. Words, bytes, characters and model tokens are different units; a word limit is not a provider token limit.

Large chunks preserve context but mix topics and consume prompt budget. Small chunks target precisely but fragment meaning. Overlap can recover conditions while increasing duplicate context, storage and indexing work. Choose against actual questions and inspect passages instead of asserting one universally optimal size.

## Metadata connects results to their source

> [!IMPORTANT]
> A result needs traceable source identity and revision, not just a plausible passage. Preserve the metadata needed to diagnose a miss before evaluating the generated answer.

An **index** optimizes search; it is not the source of record. A lexical index tracks terms/documents; a vector index stores numeric representations and search structures. Exhaustive comparison suits small corpora. Approximate nearest-neighbor search trades some recall for scale and requires measurement.

Retain document and chunk IDs, section/location, content hash, parser/chunker versions and relevant metadata. Topic labels aid filtering. Security metadata and trusted permission checks are separate: a client-selected topic is not authorization. A filename does not establish freshness or implement deletion.

Content/configuration-derived IDs make rebuild changes visible. A document-hash strategy may invalidate every passage when one paragraph changes; that is a deliberate choice, not an incremental-update algorithm. Real publication needs atomic index switching, tombstones and removal of old entries. The [knowledge-lifecycle exercise](../../workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/knowledge-lifecycle.md) tests source-level incremental replacement, table provenance, duplicate quarantine, failed extraction and logical deletion in the existing SQLite lab. Its local transactional boundary does not implement distributed publication or erase caches/backups.

## Compare three retrieval mechanisms

**Lexical retrieval** scores terms. BM25 accounts for term discrimination, repeated-term saturation and passage length. It is an inspectable baseline for identifiers and specialized vocabulary. Tokenization and language support matter: splitting `DELAY-42` incorrectly can lose the useful exact match.

**Vector retrieval** maps passages and questions into a compatible numeric space and compares similarity. Learned embeddings may bridge paraphrases; similarity does not prove truth or current policy applicability. Record model revision, dimension, preprocessing, normalization and metric. Use the intended compatible query/document interfaces. Equal dimensions do not make two models compatible; changing models requires rebuilding and evaluation.

Cosine is dot product divided by vector lengths. For (1,1) and (1,0), it is 1/√2 ≈ 0.707. That teaches geometry, not calibrated relevance probability. A zero vector has no direction: explicitly reject it or return no signal. Never divide silently by zero or mix dimensions.

**Hybrid retrieval** combines rankings. Lexical and cosine scores have different scales. Reciprocal rank fusion (RRF) adds 1/(c + rank) for each list containing a passage. The lab uses c=60 and rank one first. A passage ranked first and second scores 1/61 + 1/62 ≈ 0.0325; one present only at rank one scores about 0.0164. List depth, tie handling and settings affect results. Fusion cannot recover evidence absent from every list.

| Requirement | Starting choice | Evidence that could justify more complexity |
|---|---|---|
| Exact codes | Lexical baseline | Measured paraphrase misses |
| Meaning-preserving paraphrases | Compatible learned vectors | Identifier failures or unacceptable cost |
| Both | Compare hybrid against each baseline | Complementary retrieval benefit exceeding added latency/complexity |
| Small corpus | Exhaustive search | Measured latency/memory constraint |

A positive score is not an acceptance threshold. Include no-answer queries. The toy lab returns no candidates for zero signal; positive irrelevant matches still require relevance evaluation and downstream abstention.

## Failure, cost and ownership

Parsing, chunking, embedding and retrieval fail separately. Observe accepted/rejected sources, chunk counts, empty vectors, retrieval latency, candidate counts and stage versions. Avoid logging private source text and questions by default; define diagnostic access and retention.

Embedding spend grows with tokens and rebuilds; prompt spend grows with selected context. Raw vector bytes ≈ documents × chunks/document × dimensions × bytes/coordinate. With 1,000 documents, 10 chunks each, 768 dimensions and four-byte coordinates, that is 30,720,000 bytes, about 30.7 MB, before metadata/index/replicas. This is arithmetic, not a vendor price estimate.

The ingestion owner defines supported formats, failure handling and rebuild/rollback procedures. Retrieval engineers preserve metadata and measure relevant evidence separately from generated-answer quality. A plausible answer can conceal bad retrieval; a good passage can still produce a bad answer.

## Practice and reflection

Complete [W-RAG-03–06](../../workbooks/langchain/02-rag-capstone-workbook/03-document-loading.md). Explain which parsing loss is most dangerous, which metadata diagnoses it, which query favors lexical search, and what observed result would justify learned vectors.

Independent challenge: a multilingual policy table contains a numeric limit, currency and exception footnote. Specify extraction checks, boundaries, exact-match handling and a rejection rule.

<details>
<summary>After your attempt: hint and worked reasoning</summary>

Preserve row/footnote meaning before choosing a database. A defensible answer validates units against the source, keeps conditions together, tests actual languages and refuses to generalize from an English toy demo.

</details>

**Check your calculation:** a passage ranks second in one list and is absent from the other. With RRF constant 60, what is its score, and does that prove it answers the question?

<details>
<summary>Compare the calculation and interpretation</summary>

Its score is 1/(60 + 2), approximately 0.0161. This records its ranking contribution, not answerability, permission or a probability of correctness. Inspect the passage and evaluate relevant-evidence coverage separately.

</details>

Revision: parsing preserves meaning; chunking defines the evidence unit; metadata preserves provenance; embeddings represent text; retrieval ranks candidates; fusion combines lists. None replaces permission checks. Next unresolved constraint: whether the requester may see the passage and whether it is current.

## Completion checkpoint

**You can now:** explain what extraction and chunking can lose, explain what BM25 rewards, work through cosine and RRF on a small example, and justify lexical, vector or hybrid retrieval for a stated corpus.

**Show it:** your practice and reflection answers.

**Next:** open the [offline retrieval checkpoint](../../workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/README.md) for its exact starting state and setup, then follow its chapters 03–06.

## Sources

Checked 2026-10-14. Core explanation above is sufficient; these resources are optional, free and require basic vectors/ranked lists.

- **Recommended:** Manning, Raghavan and Schütze, [Queries as vectors](https://nlp.stanford.edu/IR-book/html/htmledition/queries-as-vectors-1.html), Introduction to Information Retrieval, vector-scoring section; 15 min; stable textbook.
- **Reference:** Same authors, [Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html), term-frequency/length-normalization section; 15 min. The lab uses a positive smoothed IDF variant `log(1 + (N-df+0.5)/(df+0.5))` and distinct query terms; it does not implement every BM25 variant.
- **Reference:** Cormack, Clarke and Buettcher, [Reciprocal Rank Fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf), SIGIR 2009, method section; 15 min; author-hosted original paper. No universal superiority is claimed.

[Course map](../../README.md) · [Existing learned-embedding workbook](../../workbooks/langchain/01-learning-workbook/07-embeddings-and-similarity.md)

**Optional comparison:** [reranking a diagnosed miss](../../workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/reranking-comparison.md) reorders only current permitted candidates and reports a gain, regression and missing-evidence failure. It cannot restore an extracted condition or candidate absent from the shortlist. The scorer is authored, not learned-quality evidence; take it only after the required grounded controls.
