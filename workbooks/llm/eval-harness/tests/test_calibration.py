import copy
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import unittest

from eval_harness.calibration import compare, validate_review
from eval_harness.core import load
from eval_harness.harness import score
from refund_drafts.schema import DraftOut

ROOT = Path(__file__).resolve().parents[1] / "calibration"


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.packet = load(ROOT / "sample.json")
        self.rubric = load(ROOT / "rubric-v1.json")
        self.a, self.b = load(ROOT / "demo-a.json"), load(ROOT / "demo-b.json")
        self.adjudication = load(ROOT / "demo-adjudication.json")

    def report(self, adjudication=None):
        return compare(self.packet, self.rubric, self.a, self.b, adjudication)

    def test_authored_demo_preserves_disagreement_and_never_becomes_human_evidence(self):
        before = copy.deepcopy(self.a)
        result = self.report(self.adjudication)
        self.assertEqual(result["mode"], "authored_demo")
        self.assertFalse(result["independent_evidence_complete"])
        self.assertEqual(result["critical_cases"], ["CAL-02", "CAL-04", "CAL-06"])
        self.assertEqual(result["disagreements"], {"CAL-04": ["support", "task", "safety"], "CAL-07": ["language"]})
        self.assertEqual(result["agreement"]["safety"], dict(matches=7, comparable=8, total=8, fraction=.875))
        self.assertEqual(self.a, before)
        self.assertEqual(result["original_passes"][0]["labels"]["CAL-04"]["scores"]["safety"], 1)

    def test_one_person_two_rounds_is_self_calibration(self):
        for review in (self.a, self.b):
            review["reviewer"].update(id="same-human", kind="human", blind_to_other_pass=True)
        self.assertEqual(self.report()["mode"], "self_calibration")

    def test_declared_distinct_people_still_need_blind_passes_and_resolution(self):
        for review in (self.a, self.b):
            review["reviewer"]["kind"] = "human"
        self.assertEqual(self.report()["mode"], "non_independent")
        for review in (self.a, self.b):
            review["reviewer"]["blind_to_other_pass"] = True
        result = self.report()
        self.assertEqual(result["mode"], "independent_human_attested")
        self.assertFalse(result["independent_evidence_complete"])

    def test_uncertainty_is_excluded_from_agreement_and_remains_unresolved(self):
        self.a["labels"]["CAL-08"]["scores"]["language"] = None
        report = self.report()
        self.assertEqual(report["agreement"]["language"]["comparable"], 7)
        self.assertIn("CAL-08", report["unresolved"])

    def test_changed_rubric_or_packet_requires_new_passes(self):
        with self.assertRaises(ValueError):
            compare(self.packet, load(ROOT / "rubric-v2.json"), self.a, self.b)
        self.packet["cases"][0]["response"]["text"] += " changed"
        with self.assertRaises(ValueError):
            self.report()

    def test_coercion_missing_cases_and_unqualified_language_rejected(self):
        for invalid in (True, "1", 2):
            with self.subTest(value=invalid):
                bad = copy.deepcopy(self.a)
                bad["labels"]["CAL-01"]["scores"]["safety"] = invalid
                with self.assertRaises(ValueError):
                    validate_review(bad, self.packet, self.rubric)
        del self.a["labels"]["CAL-01"]
        with self.assertRaises(ValueError):
            self.report()
        self.a = load(ROOT / "demo-a.json")
        self.a["reviewer"]["languages"] = ["en"]
        with self.assertRaises(ValueError):
            self.report()

    def test_adjudication_cannot_erase_unresolved_cases_or_change_input_hashes(self):
        del self.adjudication["resolutions"]["CAL-07"]
        with self.assertRaises(ValueError):
            self.report(self.adjudication)
        self.adjudication = load(ROOT / "demo-adjudication.json")
        self.adjudication["first_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            self.report(self.adjudication)

    def test_integer_dollar_failure_becomes_narrow_scoring_regression(self):
        fixture = load(ROOT / "regression-integer-dollar.json")
        case = next(c for c in self.packet["cases"] if c["id"] == fixture["origin"])
        source = dict(case_id=case["origin"], language=case["language"], category=case["category"],
                      expect=case["expected_outcome"], order=case["facts"])
        response = fixture["observed_response"]
        draft = DraftOut(reply_text=response["text"], refund_date_used=date.fromisoformat(response["refund_date_used"]), needs_agent=False)
        outcome = SimpleNamespace(status="ready", draft=draft, reasons=[], attempts=1, input_tokens=0, output_tokens=0)
        result = score(source, outcome)
        self.assertTrue(result["harmful"])
        self.assertIn(fixture["expected_problem"], result["problems"])
        good = response["text"].replace("$5000", "$40")
        outcome.draft = draft.model_copy(update={"reply_text": good})
        self.assertFalse(score(source, outcome)["harmful"])

    def test_language_marker_heuristic_is_not_a_semantic_language_review(self):
        from eval_harness.harness import language_ok
        case = self.packet["cases"][6]
        self.assertTrue(language_ok(case["response"]["text"], "de"))
        self.assertEqual(self.b["labels"][case["id"]]["scores"]["language"], 0)
