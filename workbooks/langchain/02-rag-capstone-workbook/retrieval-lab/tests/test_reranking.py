from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest

from retrieval_lab.grounded import Store
from retrieval_lab.reranking import authored_scores, compare_query, evidence_hit, run, seed

FIXTURE = json.loads((Path(__file__).resolve().parents[1] / "reranking-cases.json").read_text())


class RerankingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store()
        seed(self.store, FIXTURE, self.temp.name)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_diagnosed_miss_gain_and_regression_remain_separate(self):
        report = run(FIXTURE)
        self.assertEqual((report["baseline_hits"], report["reranked_hits"], report["answerable_n"]), (1, 1, 2))
        self.assertEqual(report["gains"], ["approval-miss"])
        self.assertEqual(report["regressions"], ["window-regression"])
        self.assertIn("REJECT_ADOPTION", report["decision"])
        self.assertEqual(report["cost"]["paid_provider_calls"], 0)

    def test_forbidden_stale_and_restricted_sources_never_reach_scorer(self):
        seen = []
        def scorer(query, chunks):
            seen.extend(c.document for c in chunks)
            return authored_scores(query, chunks)
        result = compare_query(self.store, "alice", "damaged refund approval", scorer=scorer)
        self.assertFalse({"foreign.md", "expired.md", "restricted.md"} & set(seen))
        self.assertEqual(len(seen), 4)
        self.assertEqual(result["reranked"][0]["document"], "approval-policy.md")

    def test_shortlist_or_parsing_loss_cannot_be_reconstructed(self):
        case = FIXTURE["cases"][0]
        result = compare_query(self.store, "alice", case["query"], pool_size=1)
        self.assertFalse(evidence_hit(result["reranked"], case))
        # Deliberately faulty parser payload: raw-source provenance alone cannot prove faithful extraction.
        chunk = next(c for c in self.store.candidates("alice", 100) if c.document == case["relevant"])
        damaged = replace(chunk, text="Damaged return refunds.")
        with self.store.db:
            self.store.db.execute("UPDATE chunks SET payload=? WHERE id=?", (json.dumps(asdict(damaged)), chunk.id))
        result = compare_query(self.store, "alice", case["query"])
        self.assertFalse(evidence_hit(result["reranked"], case))
        self.assertTrue(all(case["required_text"] not in c["text"] for c in result["pool"]))

    def test_no_answer_is_not_confused_with_zero_signal(self):
        hard = compare_query(self.store, "alice", "refund fees")
        self.assertTrue(hard["pool"])
        self.assertFalse(evidence_hit(hard["reranked"], FIXTURE["cases"][2]))
        def never(*args):
            self.fail("No candidate means no scorer call")
        self.assertEqual(compare_query(self.store, "alice", "orbital warranty", scorer=never)["status"], "no_candidates")

    def test_permission_or_revision_changes_before_scoring_block_submission(self):
        def never(*args):
            self.fail("Stale evidence reached scorer")
        result = compare_query(self.store, "alice", "damaged refund approval", scorer=never,
                               before_scoring=lambda: self.store.invalidate("approval-policy.md"))
        self.assertEqual(result, dict(baseline=[], reranked=[], pool=[], status="stale_or_denied"))

    def test_revocation_during_scoring_removes_response(self):
        result = compare_query(self.store, "alice", "damaged refund approval",
                               after_scoring=lambda: self.store.revoke("alice"))
        self.assertEqual(result["status"], "stale_or_denied")
        self.assertEqual(result["pool"], [])

    def test_score_output_cannot_inject_ids_duplicates_or_invalid_numbers(self):
        for invalid in (float("nan"), float("inf"), True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compare_query(self.store, "alice", "damaged refund approval",
                              scorer=lambda q, cs: [(c.id, invalid) for c in cs])
        for duplicate in (False, True):
            def scorer(query, chunks):
                return [(chunks[0].id if duplicate else "foreign-id", 1) for c in chunks]
            with self.assertRaises(ValueError):
                compare_query(self.store, "alice", "damaged refund approval", scorer=scorer)

    def test_provenance_and_bounds(self):
        result = compare_query(self.store, "alice", "damaged refund approval")
        chosen = result["reranked"][0]
        original = next(c for c in result["pool"] if c["id"] == chosen["id"])
        self.assertEqual(chosen, original)
        self.assertEqual(chosen["publication_revision"], 1)
        self.assertEqual(len(chosen["source_sha256"]), 64)
        for size in (0, 9, True):
            with self.assertRaises(ValueError):
                compare_query(self.store, "alice", "refund", pool_size=size)
        with self.assertRaises(PermissionError):
            compare_query(self.store, "unknown", "refund")
        with self.assertRaises(ValueError):
            seed(self.store, {"documents": {"../escape.md": next(iter(FIXTURE["documents"].values()))}}, self.temp.name)
