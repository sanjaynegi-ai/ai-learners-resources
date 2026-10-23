# Keep retrieved knowledge current

QuickCart changes its return window from 30 days to 14. Uploading the new policy is insufficient if the old passage is still searchable. A failed replacement is worse: the application may confidently keep answering from a superseded policy.

**Outcome:** publish, revise, quarantine and delete synthetic sources, then explain exactly which evidence remains available. **Prerequisites:** [indexing checkpoint](../05-embeddings-and-indexing.md), [retrieval foundations](../../../../study-guides/retrieval-foundations/README.md), and this package's [setup](README.md#exact-starting-checkpoint-and-setup). **Effort:** 150–195 minutes estimated: 20 reading, 15 setup, 75 guided construction, 30 independent and 10–55 diagnosis/repair. **Artifact:** your small publication driver, failure/repair output, independent change-feed implementation and a lifecycle decision record.

**Starting state:** use your personal copy of the existing retrieval-lab package after W-RAG-05. It includes the complete `grounded-v1` reference and the added `lifecycle.py` reference; it does not require an earlier learner-created SQLite file. Keep this isolated from the LangChain framework index. The supplied store, parser and fixtures are scaffolding; you build the publication driver in three increments and then implement a changed change-feed contract independently. The inspectable complete driver is for comparison after your attempt.

**Before execution:** Windows PowerShell, uv and Python 3.11, using the existing lockfile and no new runtime dependencies. Work only with the synthetic fixtures. No network, provider, server or paid resource is used. The walkthrough uses memory and temporary parser files; the persistence test uses a temporary SQLite database. Do not point this exercise at a real knowledge store. SQL inspection below is a trusted local debugging interface, not a public API.

From the repository root in PowerShell:

```powershell
Set-Location workbooks/langchain/02-rag-capstone-workbook/retrieval-lab
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
```

The full reference has **43 tests**, including 14 lifecycle and eight optional-reranking control tests. This verifies supplied reference behavior, not your independent implementation. All following commands start from this package directory.

## 1. Decide what identity means

Think of source identity as an order number and its content hash as a receipt for one version. Editing an order does not create a new order number. The analogy stops at permissions: matching content is not permission to combine two sources.

The trusted publisher assigns a flat source ID such as `returns.md`. Its raw UTF-8 text has a SHA-256 hash. A publication signature also includes reviewed metadata and the parser version. Unchanged signature means no extraction or writes. A content, ACL, claim or parser-version change requires a new publication revision. Markdown chunks include source/hash/location/chunk settings in their IDs; CSV chunks include source/hash/record/parser version. Old chunk IDs are removed when replacing that source. Metadata-only changes may retain chunk IDs while advancing the publication revision; citation validity needs both revision and hash.

| Input event | Declared behavior | What to verify |
|---|---|---|
| Same ID, same content and review metadata | No-op | `parsed=0`, `written=0`, same revision and IDs |
| Same ID, revised content or metadata | Replace this source atomically | New revision; old rows removed; other sources untouched |
| Different ID, same content in same tenant | Quarantine alias for publisher review | No second searchable copy; original unchanged; attempt retains source/hash |
| Same content in different tenants | Separate records | Never infer shared permission from a matching hash |
| Broken extraction or missing reviewed claim | Quarantine replacement and invalidate old evidence | Zero searchable chunks for that source; explicit failure report |
| Explicit delete | Purge indexed payload; retain tombstone/history | No candidates, including after restart |
| Incremental feed omits a source | Leave it alone | Absence is not a delete event |
| Full rebuild omits a source | Delete from current index | Snapshot must be complete and trusted |

These are chosen local policies. Alias quarantine avoids merging provenance or ACLs but requires manual resolution; identical genuinely separate policies in one tenant may be rejected. A production publisher might use reviewed aliases with separate permissions. Revisions remain monotonic through repair, deletion/republish and rebuild, so old evidence cannot become current merely because a counter was reset.

**Predict:** should an unreadable new policy keep its old policy searchable?

<details><summary>Reasoning</summary>

This lab chooses source-level fail-closed publication: quarantine hides the old source and preserves a failed attempt record. Availability falls, but superseded evidence is not silently served. A failed complete rebuild instead preserves the previous committed snapshot as a whole and reports failure. That boundary does not prove the old snapshot remains business-current; the publisher must halt affected answers if the source of record has already changed.

</details>

## 2. Build the first publication step

Create `exercises/lifecycle_walk.py`. Put the following imports and `main` skeleton in it. The reviewed metadata is supplied by the publisher; do not extract tenant, roles or approval from a document's text.

```python
from pathlib import Path
from retrieval_lab.grounded import answer
from retrieval_lab.lifecycle import LifecycleStore

ROOT = Path(__file__).resolve().parents[1]

def main():
    store = LifecycleStore()
    try:
        # Place each guided increment here, inside try.
        pass
    finally:
        store.close()

if __name__ == "__main__":
    main()
```

Replace `pass` with this first increment. The member is a synthetic trusted local principal; it is not authentication.

```python
store.db.execute("INSERT INTO members VALUES('alice','A','support',1)")
store.db.commit()
raw = (ROOT / "lifecycle-fixtures/returns.md").read_text(encoding="utf-8")
table = (ROOT / "lifecycle-fixtures/credits.csv").read_text(encoding="utf-8")
meta = dict(tenant="A", roles=["support"], expires=1000, topic="refund",
            claim="Refund window is 30 days.", value="30")
credit_meta = meta | {"claim": "limit_cents=5000", "topic": "credit"}
first = store.publish("returns.md", raw, meta)
rows = store.publish("credits.csv", table, credit_meta)
repeated = store.publish("returns.md", raw, meta)
alias = store.publish("copy.md", raw, meta)
assert (first["status"], rows["written"], repeated["parsed"], alias["status"]) == (
    "published", 2, 0, "quarantined")
assert len(store.candidates("alice", 100)) == 3
print("Step 1: 3 chunks; repeat parsed=0; alias quarantined")
```

Run `uv run python exercises/lifecycle_walk.py`. The assertions must pass before continuing. Open both fixture files and compare them to `store.candidates` by temporarily printing each chunk's `document`, `section` and `text` in this synthetic-only driver. The first CSV row must retain `condition=damaged within 30 days; limit_cents=5000; approval=supervisor required`. Five thousand cents is $50, not $5,000. The second row's 1,000-cent limit belongs to late deliveries with `DELAY-42`; mixing columns would change the policy.

The table extractor supports only the declared three-column CSV contract, at most 100 rows and 100,000 bytes. Record numbers identify CSV records, not exact physical lines when fields contain embedded newlines. Markdown uses the existing section/window parser with 80-word windows and 16-word overlap. It preserves this short fixture's exception; it cannot guarantee that all long policy conditions remain together. Both retain raw-source hashes and location labels.

**Check:** why is the credit table assigned `topic=credit` instead of `refund`?

<details><summary>Explained answer</summary>

It describes credit limits, not the refund-window claim. The existing curated answer path treats different values within one topic as conflicting. Misclassifying a table can create a false conflict or misleading evidence; topic and claim review must accompany extraction. The fixed English intent router does not answer arbitrary credit questions. Here the table is inspected with candidates/ranking, not presented as a new general question-answering capability.

</details>

## 3. Revise exactly one source

Append this inside `try`, after step 1. Predict which rows and IDs should change before running it.

```python
old = {c.id for c in store.candidates("alice", 100) if c.document == "returns.md"}
other = [c for c in store.candidates("alice", 100) if c.document == "credits.csv"]
revised = raw.replace("30 days", "14 days")
current_meta = meta | {"claim": "Refund window is 14 days.", "value": "14"}
changed = store.publish("returns.md", revised, current_meta)
now = store.candidates("alice", 100)
assert old.isdisjoint(c.id for c in now)
assert other == [c for c in now if c.document == "credits.csv"]
assert changed["revision"] == 2
assert answer(store, "alice", "refund")["status"] == "ready"
print("Step 2: revision=2; old IDs absent; table unchanged")
```

Run the same command again; the in-memory store starts fresh each time, so steps 1 and 2 rerun in order. Publication parses just one source, and the unrelated table retains its stored chunks. This is **source-level incremental replacement**, not paragraph-level diffing or incremental embedding. No embeddings are learned or recomputed here. SQLite commits the source record and replacement chunks together. One trusted writer and small local datasets are assumed.

Open `src/retrieval_lab/lifecycle.py`: follow `signature` → no-op check → extraction → reviewed-claim check → transaction. Then follow the inherited `Store.candidates` checks in `grounded.py`: current membership, tenant/role, expiry, revision and hash must agree before ranking. Changing the ACL advances publication; response-time rechecks also protect an answer retrieved just before the change. An old report file is not updated by these checks.

## 4. Fail, repair, rebuild and delete

Append the following increment and rerun your driver:

```python
failed = store.publish("returns.md", "# Empty", current_meta)
assert failed["status"] == "quarantined"
assert not any(c.document == "returns.md" for c in store.candidates("alice", 100))
repaired = store.publish("returns.md", revised, current_meta)
assert repaired["revision"] == 4
snapshot = {"returns.md": (revised, current_meta), "credits.csv": (table, credit_meta)}
rebuilt = store.rebuild(snapshot)
assert rebuilt == {"parsed": 2, "written": 3}
store.delete("returns.md")
assert all(c.document != "returns.md" for c in store.candidates("alice", 100))
print("Step 3: failed replacement hidden; repaired revision=4; rebuild parsed=2; deleted")
```

Revision 3 records failed replacement; repair becomes revision 4. A full rebuild parses both sources even if unchanged, writes three chunks and advances revisions. It stages extraction separately, then swaps the SQLite rows inside a savepoint; it rejects the entire rebuild if a source fails. It does not make a distributed index switch atomic. Compare the incremental `parsed=1` revision to rebuild `parsed=2`: these are observed parser-operation counts, not performance benchmarks.

Compare your driver with `exercises/lifecycle_walk_reference.py` only after attempting all steps. The reference produces the same three output lines. Run the targeted regressions:

```powershell
uv run python -m unittest discover -s tests -p test_lifecycle.py -v
```

Expect 14 passing reference tests. They check raw row/header associations, no-op parser avoidance, stale-ID removal, unrelated-source preservation, duplicate policy, failed replacement, ACL changes, rebuild failure/omission, external invalidation and deletion across database restart. Save your own driver output separately from these reference results.

**Deliberate fault:** in your driver change `current_meta` to retain `claim="Refund window is 30 days."` while the revised source says 14. Predict the result, then run it. The step-2 `revision` assertion passes, but `answer(...)["status"] == "ready"` fails: the reviewed claim no longer survives extraction, so publication quarantines. Print `changed` to diagnose the failure. Repair the claim and rerun all three steps; retain the failure and passing output. Add an assertion that `changed["status"] == "published"` to keep this failure near its cause.

## 5. Independent change: consume an incremental feed

QuickCart's publisher now sends a bounded list of explicit upsert/delete events instead of a complete snapshot. Implement `apply_events` in `exercises/lifecycle_events.py` without importing the reference. Its docstring defines exact shapes, bounds and behavior. Malformed event shape must reject the whole batch **before** writes; valid-shaped but unextractable content quarantines just that source. Event order matters. Omitted sources remain present.

```powershell
uv run python exercises/check_lifecycle.py
```

The starter intentionally raises `NotImplementedError`. Your implementation must pass, and you must add a test where a feed changes one source while another remains unchanged. Also test upsert → delete → upsert with a fresh revision and a revised ACL. Explain why passing a feed to `rebuild` would delete unrelated sources. This explanation and your extra tests distinguish independent work from a reference run.

<details><summary>Hint 1</summary>

Validate every event into the allowed contract first. Do not delete as you validate: a bad later event must not leave earlier changes applied.

</details>

<details><summary>Hint 2 and reference comparison</summary>

Use two passes: shape/type/source-ID validation, then ordered calls to `publish` or `delete`. Preserve the returned quarantine report; never count it as a successful publication. Compare to `exercises/lifecycle_events_reference.py` after your attempt. `uv run python exercises/check_lifecycle.py --reference` verifies only that supplied comparison.

</details>

## 6. State the remaining boundaries

These controls guarantee current local candidate selection within the tested single-writer SQLite process. They do not erase the original source files, answer caches, generated exports, logs, database free pages, backups or provider copies. The `attempts` table retains source IDs/hashes and outcomes indefinitely in this small lab; hashes and names can themselves be sensitive. Define owner, retention and deletion for every real surface. Logical SQL deletion is not physical secure erasure or a compliance claim.

Roles and tenants are trusted local metadata, not remote authentication. No untrusted caller may invoke publisher SQL or choose its own permissions. Recheck authorization at use time; rebuilding cannot repair a stale membership service. Failed/quarantined sources and pending reviews need an owner and capacity, not automatic retry loops. Recovery from a stale complete snapshot requires publication judgment, not merely a successful rebuild.

The CSV example is not PDF/table OCR, nested spreadsheet parsing or arbitrary Markdown-table extraction. UTF-8 is accepted, but the existing ranker's ASCII tokenizer and English intent router do not establish multilingual retrieval. Mixed-script text can retain non-English passages that remain unsearchable; a Markdown section with no ASCII-searchable tokens is rejected. Test representative languages, merged cells, missing units and long cross-section exceptions before adopting a parser; unsupported inputs must stay visibly rejected. No live-model quality or deployed knowledge platform is demonstrated.

| Symptom | Diagnose | Repair and exact return point |
|---|---|---|
| `ModuleNotFoundError` | Check package directory, `pyproject.toml`, and active uv environment | Rerun locked setup, then step 1 |
| `quarantined` after revision | Compare reviewed claim to extracted source; inspect newest `attempts` status | Correct trusted review or source, rerun step 3; do not weaken claim validation |
| Unexpected conflict | Compare source topic/value metadata, not just ranking | Restore distinct reviewed topics, rerun step 2 |
| Old evidence in a saved report | Compare report revision/hash with current database | Regenerate privately; inspect other cache/export surfaces; return to step 3 |
| Feed deleted an unrelated source | Check whether adapter used snapshot rebuild | Use explicit events, add omitted-source regression, rerun independent checker |
| Same content keeps quarantining | Inspect alias identity, tenant and canonical source | Publisher resolves alias; do not silently merge permissions; return to step 1 |

## Completion checkpoint

Show your incrementally built driver, predictions, three output lines, failed claim/repair, targeted test result, independent feed with extra tests and a short decision record. The record must explain source/chunk identity, no-op versus source replacement versus full rebuild, duplicate policy, fail-closed behavior, provenance/units, persisted logical deletion and remaining surfaces. Note help/reference use. A reference-suite pass alone establishes neither independent competence nor production ingestion readiness.

Save evidence privately. The driver leaves no persistent service or resource to clean up; discard only your own optional generated databases after preserving evidence and checking their paths. Keep the source fixtures and course reference intact.

**Reflect:** what must happen outside this database when a policy owner deletes a source? **Next:** continue to [W-RAG-06 — Retrieval](../06-retrieval.md), carrying your identity and lifecycle decision into ranking and later permission-aware answers.

[Previous: W-RAG-05 — Indexing](../05-embeddings-and-indexing.md) · [Phase overview: retrieval route](../README.md) · [Course map](../../../../README.md#ordered-capability-map)
