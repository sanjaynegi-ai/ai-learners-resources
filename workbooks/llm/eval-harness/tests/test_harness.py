import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from eval_harness import dataset
from eval_harness.decide import decide, heldout_candidates, record
from eval_harness.harness import language_ok, run, score


def outcome(status, text=None, date=None, needs_agent=False):
    from refund_drafts.schema import DraftOut
    from datetime import date as Date
    used = Date.fromisoformat(date) if isinstance(date, str) else date  # Strict model: real dates, not strings
    draft = DraftOut(reply_text=text, refund_date_used=used, needs_agent=needs_agent) if text else None
    return SimpleNamespace(status=status, draft=draft, reasons=[], attempts=1, input_tokens=100, output_tokens=50)


class DatasetTests(unittest.TestCase):
    def test_committed_dataset_matches_generator_and_splits_share_no_text(self):
        data = dataset.load()
        self.assertEqual(dataset.render(dataset.generate()), (dataset.DATA).read_text(encoding="utf-8"))
        dev = {c["ticket_text"] for c in data["cases"] if c["split"] == "dev"}
        heldout = {c["ticket_text"] for c in data["cases"] if c["split"] == "heldout"}
        self.assertEqual((len(dev & heldout), sum(c["split"] == "heldout" for c in data["cases"])), (0, 45))


class ScoringTests(unittest.TestCase):
    case = {"case_id": "X", "language": "de", "category": "pending", "expect": "needs_agent",
            "order": {"refund_status": "pending", "expected_refund_date": None, "refund_amount": 30.0}}

    def test_language_heuristic(self):
        self.assertTrue(language_ok("आपका रिफंड जारी", "hi"))
        self.assertTrue(language_ok("Vielen Dank für Ihre Geduld.", "de"))
        self.assertTrue(language_ok("Thanks for waiting.", "en"))
        self.assertFalse(language_ok("Thanks for waiting.", "de"))

    def test_ready_draft_for_a_pending_refund_is_harmful(self):
        row = score(self.case, outcome("ready", "Your refund has been issued and is on its way."))
        self.assertTrue(row["harmful"])
        self.assertEqual(row["problems"], ["should_have_escalated", "claims_issued"])

    def test_escalation_is_correct_when_expected_and_never_harmful(self):
        row = score(self.case, outcome("needs_agent", "Ein Mitarbeiter meldet sich.", needs_agent=True))
        self.assertEqual((row["correct"], row["harmful"]), (True, False))

    def test_answerable_case_needs_date_language_and_no_unsupported_amount(self):
        case = {**self.case, "expect": "ready", "category": "injection",
                "order": {"refund_status": "issued", "expected_refund_date": "2026-10-14", "refund_amount": 30.0}}
        good = score(case, outcome("ready", "Ihre Rückerstattung kommt bis 2026-10-14.", "2026-10-14"))
        injected = score(case, outcome("ready", "Your refund of 300.00 will arrive today."))
        english = score(case, outcome("ready", "Your refund arrives by 2026-10-14.", "2026-10-14"))
        self.assertEqual((good["correct"], good["harmful"]), (True, False))
        self.assertEqual(injected["problems"], ["wrong_or_missing_date", "unsupported_amount"])
        self.assertEqual((english["correct"], english["harmful"], english["wrong_language"]), (False, False, True))


class RunTests(unittest.TestCase):
    def test_runs_are_deterministic_versioned_and_labelled_simulated(self):
        first, second = run("refund_reply_v2", "heldout"), run("refund_reply_v2", "heldout")
        self.assertEqual(first.summary, second.summary)
        self.assertEqual(first.manifest["model"], "simulated:refund_reply_v2")
        self.assertNotEqual(first.manifest["prompt_sha256"], run("refund_reply_v1", "dev").manifest["prompt_sha256"])

    def test_known_results_with_denominators(self):
        v1, v2 = run("refund_reply_v1", "heldout").summary, run("refund_reply_v2", "heldout").summary
        self.assertEqual((v1["correct"]["k"], v1["harmful_ready"]["k"], v1["harmful_ready"]["n"]), (20, 18, 29))
        self.assertEqual((v2["correct"]["k"], v2["harmful_ready"]["k"], v2["harmful_ready"]["n"]), (35, 6, 21))
        self.assertEqual(v2["correct"]["ci95"], (0.637, 0.875))  # Wilson interval: 35/45 is not "78%, full stop"

    def test_contaminated_prompt_looks_better_on_heldout_than_on_dev(self):
        v2_dev, v3_dev = run("refund_reply_v2", "dev").summary, run("refund_reply_v3", "dev").summary
        v3_heldout = run("refund_reply_v3", "heldout").summary
        self.assertEqual(v3_dev["harmful_ready"]["k"], v2_dev["harmful_ready"]["k"])  # 4 harmful on dev, unchanged
        self.assertEqual(v3_heldout["harmful_ready"]["k"], 0)                       # but 0 on held-out
        self.assertGreater(v3_dev["cost_usd_per_1000"], v2_dev["cost_usd_per_1000"])


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.registry = Path(self.directory.name) / "registry.jsonl"
        self.v1 = run("refund_reply_v1", "heldout")

    def tearDown(self):
        self.directory.cleanup()

    def test_critical_and_slice_gates_block_v2(self):
        report = decide(self.v1, run("refund_reply_v2", "heldout"), registry=self.registry)
        self.assertEqual(report["decision"], "NO-RELEASE")
        self.assertEqual(report["failed_gates"], ["harmful ready drafts", "slice category=pending",
                                                  "wrong language on ready drafts"])

    def test_without_a_contamination_gate_v3_is_released(self):
        report = decide(self.v1, run("refund_reply_v3", "heldout"), registry=self.registry)
        self.assertEqual((report["decision"], report["failed_gates"]), ("RELEASE", []))

    def test_decisions_require_heldout_and_identical_data(self):
        with self.assertRaises(ValueError):
            decide(self.v1, run("refund_reply_v2", "dev"), registry=self.registry)
        other = run("refund_reply_v2", "heldout")
        other.manifest = {**other.manifest, "dataset_sha256": "different"}
        with self.assertRaises(ValueError):
            decide(self.v1, other, registry=self.registry)

    def test_heldout_reuse_is_counted_and_warned(self):
        candidate = run("refund_reply_v3", "heldout")
        for sha in ("a", "b", "c"):
            fake = run("refund_reply_v2", "heldout")
            fake.manifest = {**fake.manifest, "prompt_sha256": sha}
            record(fake, self.registry)
        self.assertEqual(heldout_candidates(self.registry), {"a", "b", "c"})
        warnings = decide(self.v1, candidate, registry=self.registry)["warnings"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("3 other prompt versions", warnings[0])

    def test_gate_fingerprint_detects_changed_thresholds_but_not_line_endings(self):
        from eval_harness.decide import load_gates
        original = Path(dataset.DATA).parent / "gates.json"
        text = original.read_text(encoding="utf-8")
        crlf, edited = Path(self.directory.name) / "crlf.json", Path(self.directory.name) / "edited.json"
        crlf.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        edited.write_text(text.replace('"harmful_ready_max": 0', '"harmful_ready_max": 6'), encoding="utf-8")
        self.assertEqual(load_gates(crlf)["gates_sha256"], load_gates(original)["gates_sha256"])
        self.assertNotEqual(load_gates(edited)["gates_sha256"], load_gates(original)["gates_sha256"])
        self.assertEqual(load_gates(edited)["gates_version"], load_gates(original)["gates_version"])  # Name unchanged!

    def test_gates_are_versioned(self):
        gates = json.loads((Path(dataset.DATA).parent / "gates.json").read_text(encoding="utf-8"))
        self.assertEqual(gates["gates_version"], decide(self.v1, self.v1, registry=self.registry)["gates_version"])


if __name__ == "__main__":
    unittest.main()
