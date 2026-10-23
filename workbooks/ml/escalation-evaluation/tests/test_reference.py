import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from escalation_eval import report
from escalation_eval.data import DataContractError, Splits, check_features, check_splits, load_tickets, time_split
from escalation_eval.metrics import Counts, Rate
from escalation_eval.models import build_logistic, fit_logistic, model_scores, rule_scores
from escalation_eval.thresholds import choose_threshold


class MetricsTests(unittest.TestCase):
    def test_counts_partition_and_rates_keep_denominators(self):
        counts = Counts.from_arrays([1, 1, 0, 0, 1], [1, 0, 1, 0, 0])
        self.assertEqual((counts.tp, counts.fp, counts.fn, counts.tn, counts.total), (1, 1, 2, 1, 5))
        self.assertEqual((counts.recall().numerator, counts.recall().denominator), (1, 3))
        self.assertEqual(counts.cost(40, 4), 2 * 40 + 1 * 4)

    def test_zero_denominator_is_undefined_not_zero(self):
        precision = Counts.from_arrays([1, 0], [0, 0]).precision()
        self.assertIsNone(precision.value)
        self.assertIsNone(precision.interval())
        self.assertIn("n/a", str(precision))

    def test_wilson_interval_is_bounded_and_narrows_with_n(self):
        small, large = Rate(7, 10).interval(), Rate(700, 1000).interval()
        self.assertTrue(0 <= small[0] < 0.7 < small[1] <= 1)
        self.assertLess(large[1] - large[0], small[1] - small[0])
        self.assertEqual(Rate(0, 20).interval()[0], 0.0)

    def test_mismatched_lengths_are_rejected(self):
        with self.assertRaises(ValueError):
            Counts.from_arrays([1, 0], [1])


class ThresholdTests(unittest.TestCase):
    scores = np.array([0.9, 0.8, 0.7, 0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01])
    actual = np.array([1, 1, 0, 1, 0, 0, 0, 0, 0, 0])

    def test_chooses_lowest_cost_within_capacity(self):
        choice = choose_threshold(self.scores, self.actual, capacity=0.4, fn_cost=40, fp_cost=4)
        self.assertEqual((choice.threshold, choice.counts.tp, choice.counts.flags), (0.4, 3, 4))
        self.assertEqual(choice.cost, 4)

    def test_never_exceeds_capacity_even_when_cheaper(self):
        choice = choose_threshold(self.scores, self.actual, capacity=0.2, fn_cost=40, fp_cost=4)
        self.assertLessEqual(choice.counts.flags, 2)
        self.assertEqual(choice.counts.tp, 2)

    def test_tiny_capacity_flags_nothing_and_bad_inputs_fail(self):
        self.assertEqual(choose_threshold(self.scores, self.actual, capacity=0.05, fn_cost=40, fp_cost=4).counts.flags, 0)
        for kwargs in ({"capacity": 0}, {"capacity": 1.5}, {"capacity": 0.1, "fn_cost": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                choose_threshold(self.scores, self.actual, **{"fn_cost": 40, "fp_cost": 4, **kwargs})


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = load_tickets()
        cls.splits = time_split(cls.frame)

    def test_dataset_matches_documented_contract(self):
        self.assertEqual((len(self.frame), int(self.frame["y"].sum())), (12000, 993))
        self.assertEqual(tuple(len(part) for part in (self.splits.train, self.splits.validation, self.splits.test)),
                         (8000, 2000, 2000))

    def test_forbidden_features_are_refused(self):
        for features in (("amount", "assigned_queue"), ("amount", "customer_id"), ("month",)):
            with self.subTest(features=features), self.assertRaises(DataContractError):
                check_features(features)
        with self.assertRaises(DataContractError):
            build_logistic(("amount", "tag", "assigned_queue"))

    def test_split_guards_catch_time_and_customer_leaks(self):
        train, validation, test = self.splits.train, self.splits.validation, self.splits.test
        with self.assertRaises(DataContractError):
            check_splits(Splits(pd.concat([train, test]), validation, test))  # future months in training
        shared = test.assign(customer_id=[train["customer_id"].iloc[0]] + list(test["customer_id"].iloc[1:]))
        with self.assertRaises(DataContractError):
            check_splits(Splits(train, validation, shared))
        shuffled = self.frame.sample(frac=1, random_state=0)
        with self.assertRaises(DataContractError):
            check_splits(Splits(shuffled.iloc[:8000], shuffled.iloc[8000:10000], shuffled.iloc[10000:]))

    def test_rule_baseline_and_model_are_deterministic(self):
        self.assertEqual(int(rule_scores(self.splits.validation).sum()), 126)
        first = model_scores(fit_logistic(self.splits.train), self.splits.validation)
        second = model_scores(fit_logistic(self.splits.train), self.splits.validation)
        np.testing.assert_allclose(first, second)


class ReportTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.results = Path(directory.name)
        original = report.RESULTS
        report.RESULTS = self.results
        self.addCleanup(setattr, report, "RESULTS", original)

    def run_report(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            report.main(list(args))
        return output.getvalue()

    def test_test_stage_requires_a_frozen_validation_configuration(self):
        with self.assertRaises(SystemExit) as raised:
            self.run_report("--stage", "test")
        self.assertIn("never chosen on test", str(raised.exception))

    def test_threshold_is_chosen_on_validation_and_respects_capacity(self):
        output = self.run_report("--stage", "validation")
        frozen = json.loads((self.results / "frozen.json").read_text())
        self.assertIn("chosen on validation", output)
        self.assertAlmostEqual(frozen["capacity"], 0.10)
        self.assertRegex(output, r"\(chosen on validation\) flags 9\.\d% \(1\d\d/2000")

    def test_rescoring_test_after_changing_configuration_is_refused(self):
        self.run_report("--stage", "validation")
        self.run_report("--stage", "test")
        self.run_report("--stage", "test")  # Same frozen configuration: allowed.
        self.run_report("--stage", "validation", "--capacity", "0.08")
        with self.assertRaises(SystemExit) as raised:
            self.run_report("--stage", "test")
        self.assertIn("already scored", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
