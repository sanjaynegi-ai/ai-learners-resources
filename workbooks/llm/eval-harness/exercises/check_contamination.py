"""Acceptance check for the contamination gate; run explicitly, it is not part of tests/.

From the eval-harness directory:
    uv run python exercises/check_contamination.py              # checks your exercises/contamination.py
    uv run python exercises/check_contamination.py --reference  # checks the inspectable reference
"""
import os
import sys
import tempfile

os.environ["EVAL_HARNESS_RESULTS"] = tempfile.mkdtemp(prefix="eval-check-")  # Keep learner registry untouched

from refund_drafts.prompt import load_instructions  # noqa: E402

from eval_harness import dataset  # noqa: E402
from eval_harness.decide import decide  # noqa: E402
from eval_harness.harness import run  # noqa: E402

if "--reference" in sys.argv:
    from contamination_reference import contamination_gate, find_contaminated
else:
    from contamination import contamination_gate, find_contaminated

cases = dataset.load()["cases"]
heldout = [c for c in cases if c["split"] == "heldout"]
toy = [{"case_id": "A", "ticket_text": "Where is my refund for the blue lamp I returned?"},
       {"case_id": "B", "ticket_text": "Ist meine Rückerstattung unterwegs?"},
       {"case_id": "C", "ticket_text": "Completely unrelated question about delivery times"}]
prompt = "Example: where is my REFUND for the blue lamp i returned!!  Example 2: ist meine   Rückerstattung unterwegs?"
assert find_contaminated(prompt, toy) == ["A", "B"], find_contaminated(prompt, toy)
assert find_contaminated("Where is my refund for", toy) == [], "Five shared words are below min_words=6"

v3 = load_instructions("refund_reply_v3")
expected = sorted(c["case_id"] for c in heldout if c["ticket_text"] in v3)
assert find_contaminated(v3, heldout) == expected, (find_contaminated(v3, heldout), expected)
for version in ("refund_reply_v1", "refund_reply_v2"):
    assert find_contaminated(load_instructions(version), cases) == [], f"{version} should be clean"
assert find_contaminated(v3, [c for c in cases if c["split"] == "dev"]) == [], "v3 examples come from held-out only"

baseline, candidate = run("refund_reply_v1", "heldout"), run("refund_reply_v3", "heldout")
report = decide(baseline, candidate, extra_gates=(contamination_gate,))
assert report["decision"] == "NO-RELEASE" and "contamination_gate" in report["failed_gates"], report["failed_gates"]
clean = decide(baseline, run("refund_reply_v2", "heldout"), extra_gates=(contamination_gate,))
assert "contamination_gate" not in clean["failed_gates"], "A clean prompt must pass the contamination gate"
print(f"{find_contaminated.__module__}: contamination checks passed ({len(expected)} contaminated held-out cases "
      "block v3); explain your implementation independently.")
