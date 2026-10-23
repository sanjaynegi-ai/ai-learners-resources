from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from retrieval_lab.core import rank
from retrieval_lab.grounded import answer
from retrieval_lab.lifecycle import LifecycleStore, extract

ROOT = Path(__file__).resolve().parents[1]


def meta(claim="Refund window is 30 days.", **changes):
    result = dict(tenant="A", roles=["support"], expires=1000, topic="refund",
                  claim=claim, value="30")
    return result | changes


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.store = LifecycleStore()
        self.store.db.execute("INSERT INTO members VALUES('alice','A','support',1)")
        self.store.db.commit()
        self.raw = (ROOT / "lifecycle-fixtures" / "returns.md").read_text(encoding="utf-8")
        self.table = (ROOT / "lifecycle-fixtures" / "credits.csv").read_text(encoding="utf-8")

    def tearDown(self):
        self.store.close()

    def publish(self):
        return self.store.publish("returns.md", self.raw, meta())

    def test_table_units_conditions_and_provenance(self):
        chunks = extract("credits.csv", self.table, "refund")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].text, "condition=damaged within 30 days; limit_cents=5000; approval=supervisor required")
        self.assertEqual(chunks[0].section, "CSV record 1")
        self.assertEqual(chunks[0].document, "credits.csv")
        self.assertEqual(len(chunks[0].source_sha256), 64)
        result = self.store.publish("credits.csv", self.table, meta(chunks[0].text))
        self.assertEqual(result["written"], 2)
        self.assertEqual(len(rank(self.store.candidates("alice", 100), "damaged")), 1)

    def test_markdown_condition_survives(self):
        self.publish()
        self.assertIn("Unopened items only", self.store.candidates("alice", 100)[0].text)

    def test_repeat_skips_parser_and_preserves_ids_and_revision(self):
        self.publish()
        before = self.store.candidates("alice", 100)
        with patch("retrieval_lab.lifecycle.extract", side_effect=AssertionError("parsed unchanged source")):
            self.assertEqual(self.publish(), dict(status="unchanged", parsed=0, written=0, revision=1))
        self.assertEqual(before, self.store.candidates("alice", 100))

    def test_update_removes_stale_ids_leaves_unrelated_source(self):
        self.publish()
        self.store.publish("credits.csv", self.table, meta("limit_cents=5000"))
        before = self.store.candidates("alice", 100)
        other = [c for c in before if c.document == "credits.csv"]
        self.store.publish("returns.md", self.raw.replace("30", "14"), meta("Refund window is 14 days.", value="14"))
        after = self.store.candidates("alice", 100)
        self.assertEqual(other, [c for c in after if c.document == "credits.csv"])
        self.assertTrue(set(c.id for c in before if c.document == "returns.md").isdisjoint(c.id for c in after))
        self.assertEqual(self.store.db.execute("SELECT revision FROM documents WHERE id='returns.md'").fetchone()[0], 2)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM chunks WHERE document='returns.md'").fetchone()[0], 1)

    def test_duplicate_alias_quarantined_without_removing_canonical(self):
        self.publish()
        self.assertEqual(self.store.publish("copy.md", self.raw, meta())["status"], "quarantined")
        self.assertEqual([c.document for c in self.store.candidates("alice", 100)], ["returns.md"])
        self.assertEqual(self.store.db.execute("SELECT source,status FROM attempts ORDER BY sequence DESC").fetchone()["source"], "copy.md")

    def test_identical_content_other_tenant_never_merged(self):
        self.publish()
        self.store.publish("foreign.md", self.raw, meta(tenant="B"))
        self.assertEqual([c.document for c in self.store.candidates("alice", 100)], ["returns.md"])

    def test_broken_replacement_quarantines_stale_evidence_then_repairs(self):
        self.publish()
        self.assertEqual(self.store.publish("returns.md", "# Empty", meta())["status"], "quarantined")
        self.assertEqual(self.store.candidates("alice", 100), [])
        self.assertEqual(answer(self.store, "alice", "refund")["status"], "abstained")
        self.assertEqual(self.publish()["revision"], 3)

    def test_invalid_tables_are_rejected(self):
        for raw in ("condition,limit_cents,approval\nx,50\n", "condition,limit_cents,approval\nx,5,yes,extra\n",
                    "condition,limit_cents,approval\nx,$50,yes\n", "condition,limit_cents,approval\n"):
            with self.subTest(raw=raw):
                self.assertEqual(self.store.publish("credits.csv", raw, meta())["status"], "quarantined")

    def test_metadata_change_invalidates_prior_response_and_acl(self):
        self.publish()
        result = answer(self.store, "alice", "refund", after_retrieval=lambda:
                        self.store.publish("returns.md", self.raw, meta(roles=["supervisor"])))
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(self.store.candidates("alice", 100), [])

    def test_rebuild_parses_all_and_omission_deletes(self):
        self.publish()
        self.store.publish("credits.csv", self.table, meta("limit_cents=5000"))
        snapshot = {"returns.md": (self.raw, meta()), "credits.csv": (self.table, meta("limit_cents=5000"))}
        with patch("retrieval_lab.lifecycle.extract", wraps=extract) as parser:
            self.assertEqual(self.store.rebuild(snapshot)["parsed"], 2)
            self.assertEqual(parser.call_count, 2)
        self.assertEqual(self.store.db.execute("SELECT revision FROM documents WHERE id='returns.md'").fetchone()[0], 2)
        self.store.rebuild({"returns.md": (self.raw, meta())})
        self.assertEqual([c.document for c in self.store.candidates("alice", 100)], ["returns.md"])
        result = answer(self.store, "alice", "refund", after_retrieval=lambda:
                        self.store.rebuild({"returns.md": (self.raw, meta())}))
        self.assertEqual(result["status"], "abstained")

    def test_rebuild_failure_preserves_committed_index(self):
        self.publish()
        before = self.store.candidates("alice", 100)
        with self.assertRaises(ValueError):
            self.store.rebuild({f"source{i}.md": (self.raw, meta()) for i in range(101)})
        with self.assertRaises(ValueError):
            self.store.rebuild({"bad.csv": ("bad", meta())})
        self.assertEqual(before, self.store.candidates("alice", 100))

    def test_deletion_survives_restart_and_republish_has_new_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.sqlite"
            store = LifecycleStore(path)
            try:
                store.publish("returns.md", self.raw, meta())
                store.delete("returns.md")
            finally:
                store.close()
            store = LifecycleStore(path)
            try:
                self.assertEqual(store.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 0)
                self.assertEqual(store.publish("returns.md", self.raw, meta())["revision"], 3)
            finally:
                store.close()

    def test_source_id_cannot_escape_and_missing_metadata_cannot_mutate(self):
        self.publish()
        for source, metadata in (("../outside.md", meta()), ("returns.md", {})):
            with self.assertRaises(ValueError):
                self.store.publish(source, self.raw, metadata)
        self.assertEqual(len(self.store.candidates("alice", 100)), 1)

    def test_external_invalidation_cannot_take_unchanged_shortcut(self):
        self.publish()
        self.store.invalidate("returns.md")
        self.assertEqual(self.store.candidates("alice", 100), [])
        self.assertEqual(self.publish()["status"], "published")


if __name__ == "__main__":
    unittest.main()
