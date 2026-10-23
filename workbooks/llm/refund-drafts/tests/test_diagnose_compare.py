import contextlib
import io
import unittest

from refund_drafts import compare
from refund_drafts.compare import ReplayProvider, evaluate, load_recordings
from refund_drafts.config import Settings
from refund_drafts.diagnose import diagnose, run
from refund_drafts.domain import FIXTURES, load_records
from refund_drafts.prompt import load_instructions


class DiagnoseTests(unittest.TestCase):
    def test_every_case_is_caught_at_its_expected_layer(self):
        for case, diagnosis in run():
            with self.subTest(case=case["case_id"]):
                self.assertEqual(diagnosis.layer, case["expected_layer"])

    def test_layers_are_checked_in_order_syntax_schema_business(self):
        order = load_records(FIXTURES / "eval").orders["QC-2001"]
        self.assertEqual(diagnose("not json", order).layer, "syntax")
        self.assertEqual(diagnose('{"reply_text": "Hi"}', order).layer, "schema")
        wrong = '{"reply_text": "By 2026-01-01.", "refund_date_used": "2026-01-01", "needs_agent": false}'
        self.assertEqual(diagnose(wrong, order).layer, "business")

    def test_passing_every_check_is_reported_as_passed_not_correct(self):
        passed = [case["case_id"] for case, diagnosis in run() if diagnosis.layer == "passed"]
        self.assertEqual(passed, ["D-09", "D-10"])


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.report = evaluate(ReplayProvider(load_recordings()), Settings())

    def test_replay_metrics_have_explicit_denominators(self):
        v1, v2 = self.report["refund_reply_v1"], self.report["refund_reply_v2"]
        self.assertEqual((v1["matches_expected"], v2["matches_expected"]), ((5, 10), (6, 10)))
        self.assertEqual(v1["unsafe_ready"], (["E-02", "E-07", "E-09"], 4))
        self.assertEqual(v2["unsafe_ready"], (["E-09"], 4))
        self.assertEqual(v2["unnecessary_escalation"], (["E-06", "E-10"], 6))
        self.assertEqual(v2["failed"], (["E-04"], 10))

    def test_code_fenced_json_is_malformed_and_retried_until_budget(self):
        self.assertEqual(self.report["refund_reply_v2"]["outcomes"]["E-04"]["reasons"],
                         ["malformed_output"] * 3 + ["attempts_exhausted"])

    def test_versions_use_different_instructions(self):
        self.assertNotEqual(load_instructions("refund_reply_v1"), load_instructions("refund_reply_v2"))
        self.assertIn("refund_status is not", load_instructions("refund_reply_v2"))

    def test_replay_output_is_labelled_and_live_requires_confirmation(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            compare.main([])
        self.assertTrue(output.getvalue().startswith("REPLAY OF SYNTHETIC RECORDINGS"))
        with self.assertRaises(SystemExit) as raised:
            compare.main(["--live"])
        self.assertIn("paid API calls", str(raised.exception))

    def test_recordings_are_marked_synthetic(self):
        for version, recordings in load_recordings().items():
            self.assertIn("SYNTHETIC", recordings["_note"], version)


if __name__ == "__main__":
    unittest.main()
