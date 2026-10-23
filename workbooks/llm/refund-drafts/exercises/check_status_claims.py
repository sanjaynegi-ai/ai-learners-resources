"""Acceptance check for the status-claims requirement; run explicitly, it is not part of tests/.

From the refund-drafts directory:
    uv run python exercises/check_status_claims.py              # checks your exercises/status_claims.py
    uv run python exercises/check_status_claims.py --reference  # checks the inspectable reference
"""
import sys

from refund_drafts.compare import ReplayProvider, evaluate, load_recordings
from refund_drafts.config import Settings
from refund_drafts.diagnose import run
from refund_drafts.domain import FIXTURES, load_records
from refund_drafts.schema import DraftOut
from refund_drafts.validate import DEFAULT_CHECKS

if "--reference" in sys.argv:
    from status_claims_reference import check_status_claims
else:
    from status_claims import check_status_claims

orders = load_records(FIXTURES / "eval").orders
issued, pending, pending_de = orders["QC-2001"], orders["QC-2002"], orders["QC-2007"]


def draft(text):
    return DraftOut(reply_text=text, refund_date_used=None, needs_agent=False)


cases = [
    (pending, "Good news: your refund has been issued.", ["claims_refund_issued"]),
    (pending, "Your money is ON ITS WAY.", ["claims_refund_issued"]),
    (pending_de, "Ihre Rückerstattung wurde bereits veranlasst.", ["claims_refund_issued"]),
    (pending_de, "Der Betrag wurde überwiesen.", ["claims_refund_issued"]),
    (pending, "Thank you. An agent is checking your refund and will update you.", []),
    (pending_de, "Ein Mitarbeiter prüft Ihre Rückerstattung und meldet sich.", []),
    (issued, "Your refund was issued and should arrive by 2026-10-20.", []),
]
for order, text, expected in cases:
    got = check_status_claims(draft(text), order)
    assert got == expected, f"{text!r} ({order.refund_status}): expected {expected}, got {got}"

checks = DEFAULT_CHECKS + (check_status_claims,)
diagnosed = {case["case_id"]: diagnosis for case, diagnosis in run(checks)}
assert diagnosed["D-09"].layer == "business" and "claims_refund_issued" in diagnosed["D-09"].codes, diagnosed["D-09"]
assert diagnosed["D-10"].layer == "passed", "Language is out of scope for this check; D-10 still needs human review"

report = evaluate(ReplayProvider(load_recordings()), Settings(), checks)
unsafe_v1, _ = report["refund_reply_v1"]["unsafe_ready"]
assert unsafe_v1 == ["E-09"], f"v1 unsafe ready should drop to ['E-09'], got {unsafe_v1}"
assert report["refund_reply_v1"]["unnecessary_escalation"][0] == ["E-06", "E-08"], "Issued-refund drafts must not be blocked"
print(f"{check_status_claims.__module__}: status-claim checks passed; explain your implementation independently.")
