import copy
import json
from pathlib import Path
import tempfile
import unittest

from watch import Store, artifact, digest, exercise, report, safe_event, traffic


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.manifest = artifact(1200)
        self.rows = traffic(self.manifest)

    def test_metrics_keep_failure_denominator(self):
        result = report(traffic(artifact(500)), artifact(500))
        m = result["metrics"]
        self.assertEqual((m["requests"], m["ready"], m["failed"]), (10, 6, 4))
        self.assertEqual(m["quality"], 1)
        self.assertEqual(m["coverage"], .6)
        self.assertTrue(result["halt"])

    def test_baseline_units_and_slices(self):
        r = report(self.rows, self.manifest)
        self.assertFalse(r["halt"])
        self.assertEqual(r["metrics"]["p95_ms"], 900)
        self.assertAlmostEqual(r["metrics"]["cost_per_good_ready_usd"], .0025)
        self.assertEqual(r["slices"]["slow"]["requests"], 4)

    def test_no_evidence_never_passes(self):
        self.assertTrue(report([], self.manifest)["halt"])
        for r in self.rows:
            r["status"] = "abstained"
        self.assertIsNone(report(self.rows, self.manifest)["metrics"]["quality"])
        self.assertTrue(report(self.rows, self.manifest)["halt"])

    def test_missing_review_halts(self):
        self.rows[0]["reviewed"] = False
        self.assertIn("review_fraction", report(self.rows, self.manifest)["reasons"])

    def test_quality_regression_and_unsafe_gate(self):
        baseline = report(self.rows, self.manifest)
        self.rows[0]["correct"] = False
        self.rows[0]["unsafe"] = True
        reasons = report(self.rows, self.manifest, baseline)["reasons"]
        self.assertTrue({"unsafe", "quality", "quality_regression"}.issubset(reasons))

    def test_cost_latency_gates(self):
        self.rows[0]["latency_ms"] = 2000
        self.rows[0]["cost_usd"] = 1
        self.assertTrue({"cost", "latency"}.issubset(report(self.rows, self.manifest)["reasons"]))

    def test_redaction_drops_nested_unknown_fields(self):
        self.rows[0]["exception"] = {"request": "PRIVATE", "headers": ["SECRET"]}
        encoded = json.dumps(safe_event(self.rows[0]))
        for sentinel in ("PRIVATE", "SECRET", "example.invalid", "authorization", "prompt", "exception"):
            self.assertNotIn(sentinel, encoded)
        self.rows[0]["slice"] = "secret\nforged log"
        with self.assertRaises(ValueError):
            safe_event(self.rows[0])

    def test_invalid_measurements_rejected(self):
        for value in (-1, float("nan"), float("inf"), True, "secret"):
            row = dict(self.rows[0], cost_usd=value)
            with self.assertRaises(ValueError):
                safe_event(row)

    def test_retention_access_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.db"
            s = Store(path)
            s.append(self.rows[0], 100)
            s.append(self.rows[1], 101)
            s.close()
            s = Store(path)
            try:
                with self.assertRaises(PermissionError):
                    s.read("learner")
                self.assertEqual(s.expire(604900), 1)
                self.assertEqual(len(s.read("reviewer")), 1)
                self.assertEqual(s.expire(604901), 1)
            finally:
                s.close()

    def test_baseline_gate_change_rejected(self):
        baseline = copy.deepcopy(report(self.rows, self.manifest))
        baseline["gates_sha256"] = "changed"
        with self.assertRaises(ValueError):
            report(self.rows, self.manifest, baseline)

    def test_config_changes_artifact_identity(self):
        self.assertNotEqual(digest(artifact(1200)), digest(artifact(500)))

    def test_incident_restores_disk_artifact_and_keeps_halt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"incident"
            r = exercise(out)
            self.assertEqual((r["baseline_halt"], r["canary_halt"], r["recovery_halt"]), (False, True, False))
            self.assertEqual(json.loads((out/"active.json").read_text()), artifact(1200))
            self.assertTrue(json.loads((out/"rollout.json").read_text())["halted"])
            self.assertEqual(r["expired_events"], 10)
            self.assertIn("slow", (out/"runbook-update.md").read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                exercise(out)


if __name__ == "__main__":
    unittest.main()
