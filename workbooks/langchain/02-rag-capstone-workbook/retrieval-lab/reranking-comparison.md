# Optional: rerank only after diagnosing a shortlist miss

QuickCart asks who must approve a damaged-return refund. Lexical search ranks a dashboard above the actual approval rule. The needed passage is present in the shortlist, so changing its order might help. If the passage were absent or its condition had been lost during extraction, reordering could not restore it.

**Outcome:** compare a fixed ranking with a bounded reranking stage and defend a keep/reject decision. **Prerequisites:** [W-RAG-06 retrieval comparison](../06-retrieval.md), [permission-aware candidates](README.md#reference-for-the-next-capability-grounded-rag) and the [knowledge lifecycle](knowledge-lifecycle.md). **Scope:** optional AI-RETRIEVE-01/AI-RAG-01 extension, not required adoption or a learned-model benchmark. **Effort:** 60–90 minutes estimated: 10 reading, 25 guided comparison, 15 failure/repair and 10–40 independent work. **Artifact:** your comparison driver, gain/regression and no-answer reports, diagnosed failure and a decision with latency/cost limitations.

**Starting state:** use your personal retrieval-lab package after the grounded controls. The supplied `reranking.py` is the inspectable control-stage reference; `reranking-cases.json` fixes the synthetic source text and relevance expectations. Build the driver below before comparing with the full CLI output. This uses the existing SQLite store and lexical ranker, not a new framework, provider or project.

**Before running:** Python 3.11, uv and Windows PowerShell; same lockfile, no new dependency, key, paid operation or network request. Temporary files contain only the supplied synthetic documents and are cleaned when closed. Reports contain synthetic source passages; keep your work private. The scorer is an explicitly authored rule, not an embedding model, cross-encoder or prediction of learned-reranker quality.

From repository root:

```powershell
Set-Location workbooks/langchain/02-rag-capstone-workbook/retrieval-lab
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
```

Expect **43 tests**, including eight reranking checks. All following commands start from this package directory. The earlier tests remain; the default grounded application does not enable this optional reranker.

## 1. Freeze the miss and the cases

A first-stage retriever finds a bounded pool. A **reranker** scores that pool against the question and orders it again; it cannot add a missing source. Think of reviewing an interview shortlist: you may change the order, but an omitted applicant cannot be selected. The analogy stops at authority: a scoring model cannot decide permission, publication status or policy validity.

The fixture has four eligible documents: two dashboard/statistics distractors, a supervisor-approval policy and a return-window policy. Three additional high-scoring-looking documents belong to another tenant, are expired or require a supervisor role. Trusted application checks must remove those before any scorer sees content. Relevance labels identify both the expected document and the exact condition that must survive; filename-only success is insufficient.

| Fixed case | Expected evidence | What to diagnose |
|---|---|---|
| `approval-miss`: damaged refund approval | `approval-policy.md`, full supervisor rule | Dashboard ranks first; required source is third in pool of four |
| `window-regression`: return window refund eligibility | `window-policy.md`, 30-day rule | Baseline already retrieves the right evidence |
| `unanswerable-positive`: refund fees | No supporting source | Positive lexical matches still do not support an answer |
| `no-signal`: orbital warranty | No supporting source | Empty pool must not invoke scoring or invent candidates |

**Predict:** should the same rule that promotes supervisor policies help a question about return windows? Write your expectation before inspecting the scorer. Its deliberately overbroad rule adds 10 to a passage containing “require supervisor” whenever the query contains “refund”; other scores are zero. This rule helps one case and harms another. These numbers are authored priorities, not calibrated probabilities or an estimate of a learned model.

## 2. Build the comparison in two increments

Create `exercises/reranking_walk.py` with the skeleton below. Source text and metadata are supplied scaffolding; you build the fixed-case comparison and evidence checks.

```python
import json
from pathlib import Path
import tempfile
from retrieval_lab.grounded import Store
from retrieval_lab.reranking import compare_query, evidence_hit, seed

ROOT = Path(__file__).resolve().parents[1]
fixture = json.loads((ROOT / "reranking-cases.json").read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory() as directory:
    store = Store()
    try:
        seed(store, fixture, directory)
        # Replace pass with the two increments below, indented inside try.
        pass
    finally:
        store.close()
```

First insert this after `seed`, replacing `pass`. Run `uv run python exercises/reranking_walk.py` before proceeding.

```python
case = fixture["cases"][0]
result = compare_query(store, "alice", case["query"], pool_size=4)
assert [row["document"] for row in result["pool"]].index(case["relevant"]) == 2
assert not evidence_hit(result["baseline"], case)
assert evidence_hit(result["reranked"], case)
print("Approval: baseline misses at top 1; authored reranking hits")
```

The first stage already found the source; the miss is its position, not failed ingestion. Now append this second increment inside the same `try` and rerun:

```python
other = fixture["cases"][1]
changed = compare_query(store, "alice", other["query"])
assert evidence_hit(changed["baseline"], other)
assert not evidence_hit(changed["reranked"], other)
short = compare_query(store, "alice", case["query"], pool_size=1)
assert not evidence_hit(short["reranked"], case)
hard = compare_query(store, "alice", fixture["cases"][2]["query"])
assert hard["pool"] and not evidence_hit(hard["reranked"], fixture["cases"][2])
empty = compare_query(store, "alice", fixture["cases"][3]["query"])
assert empty["status"] == "no_candidates"
assert result["reranked"][0] in result["pool"]
print("Window: regression; shortlist loss cannot be repaired; no-answer stays unsupported")
```

Both answerable cases have the same denominator: baseline hits 1/2, reranked hits 1/2. Keep the gain and regression case IDs separately; the unchanged aggregate hides their exchange. The hard no-answer case still returns positive candidates, so answer abstention/validation remains required downstream. This module returns ranked candidates, not a safe final answer or proof of no-answer detection.

## 3. Preserve trust and provenance around scoring

Read `compare_query` in `src/retrieval_lab/reranking.py`. Trace current trusted membership → tenant/role/expiry/revision/hash filtering → lexical pool (1–8 candidates) → recheck before scoring → score validation → recheck before returning. Scores may refer only to the original candidate IDs, exactly once, and must be finite real numbers, not booleans. The returned source text, source hash, section/offsets, chunk ID and publication revision come from the trusted pool; the scorer cannot supply replacement passages.

This preserves the existing local authority/freshness contract. It does not make a document's factual claim true, authenticate a remote caller or provide a distributed consistency guarantee. The tests include invalidation before scoring and revocation during scoring; on those changes both baseline and reranked lists are withheld. A model or malicious document cannot choose a different tenant or reintroduce filtered evidence.

The inherited fixture clock is logical `now=100`, with current source expiry at 1000 and the expired fixture at 99. These checks do not implement calendar policy semantics or prove wall-clock expiry during a remote call. Keep that limit separate from the actual local latency timings below.

**Deliberate failure:** in your personal copy, change only the **last** `if not current():` guard in `compare_query` to `if False:`. Leave the first guard intact. Predict which test detects stale output, then run:

```powershell
uv run python -m unittest discover -s tests -p test_reranking.py -v
```

The revocation-during-scoring test must fail because the revoked response is no longer suppressed. Restore the last guard, rerun the eight tests and then all 43 tests. Keep failed and repaired output; never weaken the permission test to make the exercise pass. If imports/setup fail, return to locked setup; if a shortlist expectation differs, inspect your fixture/source changes before changing expected labels.

`test_shortlist_or_parsing_loss_cannot_be_reconstructed` also simulates a faulty parser that drops the supervisor condition from the indexed payload. The raw source hash still exists, but none of the candidates contain the required condition. Reranking cannot reconstruct it. The changed payload is a deliberate extraction fault, not evidence that the source was legitimately revised. A hash/provenance chain is useful for diagnosis but does not prove faithful parsing.

## 4. Measure the local path and record costs honestly

After your attempt, run the complete comparison to a **new** output path:

```powershell
uv run python -m retrieval_lab.reranking --output results/rerank-comparison-01.json
```

The CLI refuses an existing output. Each case runs 20 times and records nearest-rank p95 (the 19th sorted observation) for the combined local path, baseline selection and additional authored scoring/rechecks where a pool exists. Values are actual local wall-clock measurements and will vary by runtime/host; they are not learned-model latency, a stable benchmark or a real service load test. Do not add the separately sampled p95 values and call their sum the combined p95. Empty-pool cases have no scoring-stage timing.

No paid provider is called, so recorded provider charges are zero; local compute is not priced. Learned reranker latency, token/request billing, hosting and privacy/access eligibility remain **Not measured**. Estimate those separately from official current information only if you later select and run a real candidate under an approved budget. No download or paid evaluation is required here.

The default decision is **reject adoption; retain the optional mechanics exercise**: one gain and one regression provide no net answerable-case benefit, no-answer support is unresolved, and learned quality/operating costs are unknown. The earlier grounded hybrid fixture's success does not need to be rewritten as a miss; this is a separate authored diagnostic corpus. K07 remains optional unless a real requirement, measured relevant-evidence benefit and workload review justify more depth.

## 5. Independent decision under a changed query

Before editing the rule, add a new synthetic approval paraphrase that omits “refund,” a new no-answer question with lexical overlap, and an unrelated-authority passage that must remain filtered. Fix expected evidence/conditions first. In your own scorer, try a narrower policy-selection rule and compare every original and new case, including the window regression. Keep a separate unfamiliar case for a later check and disclose that public teaching cases are development material.

Submit per-case gain/regression and no-answer counts, unchanged source/permission provenance, shortlist/truncation limitations, measured local latency, missing learned cost/quality evidence and a keep/reject decision. A hand-authored rule fitted to these cases cannot establish general relevance. Explain whether improving the first-stage retrieval, parsing or supported question scope would be simpler than another scoring stage.

<details><summary>Hints and self-check</summary>

First ask whether the relevant passage is in the pool and contains the whole condition. Then inspect the question's task, rather than promoting a policy merely because it mentions a supervisor. Keep negative, foreign/stale and no-answer cases in every comparison. Repaired optional mechanics can still lead to rejecting deployment; a more sophisticated score is not acceptance evidence.

</details>

**Completion checkpoint:** your two-step driver, fixed labels/corpus versions, diagnosed baseline miss, gain and regression, no-answer checks, failed/repaired guard, loss demonstration and independent decision. Record runtime, actual command/output and help used. Reference tests/CLI demonstrate controls only; no learner pilot, independent assessment, learned reranker quality or cloud/model evidence is claimed.

Save reports privately. Temporary sources/stores close automatically; no provider or server remains. Do not remove supplied fixtures or another learner's results. **Next:** return to the recommended [grounded-answer route](../07-answer-generation.md); this optional comparison does not replace it or alter its acceptance gates.

[Previous: retrieval comparison](../06-retrieval.md) · [Phase overview](../README.md) · [Course map](../../../../README.md#ordered-capability-map)
