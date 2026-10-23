import hashlib
from pathlib import Path
import tempfile
import unittest

from merchant_support.readiness import ARTIFACTS, GATES, MILESTONES, check


class Readiness(unittest.TestCase):
    def test_reference_cannot_graduate_without_external_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"evidence.txt"
            p.write_text("synthetic reference")
            item = {"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            manifest = {"artifacts": {name: item for name in ARTIFACTS},
                        "gates": {name: {"status": "pass", "evidence": "test log", "reviewer": "author"} for name in GATES}}
            r = check(tmp, manifest)
            self.assertEqual(r["decision"], "NO_RELEASE")
            self.assertEqual(len(r["reasons"]), len(MILESTONES))
            p.write_text("changed")
            self.assertIn("artifact_changed:tests", check(tmp, manifest)["reasons"])

    def test_path_escape_and_empty_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"artifacts": {"tests": {"path": "../outside", "sha256": "fake"}},
                        "gates": {"authorization": {"status": "pass"}}}
            r = check(tmp, manifest)
            self.assertIn("artifact_missing_or_outside:tests", r["reasons"])
            self.assertIn("gate_not_demonstrated:authorization", r["reasons"])


if __name__ == "__main__":
    unittest.main()
