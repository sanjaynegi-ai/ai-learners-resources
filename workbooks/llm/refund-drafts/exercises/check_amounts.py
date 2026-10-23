"""Acceptance check for check_amounts; run explicitly, it is not part of tests/.

From the refund-drafts directory:
    uv run python exercises/check_amounts.py              # checks your exercises/amounts.py
    uv run python exercises/check_amounts.py --reference  # checks the inspectable reference
"""
import sys

from refund_drafts.config import Settings
from refund_drafts.domain import load_records
from refund_drafts.pipeline import draft_reply
from refund_drafts.providers import FakeProvider
from refund_drafts.schema import DraftOut
from refund_drafts.validate import DEFAULT_CHECKS

if "--reference" in sys.argv:
    from amounts_reference import check_amounts
else:
    from amounts import check_amounts

records = load_records()
issued, pending = records.orders["QC-1001"], records.orders["QC-1002"]  # refund_amount 25.00 / 140.00


def draft(text):
    return DraftOut(reply_text=text, refund_date_used=None, needs_agent=False)


cases = [
    (issued, "Your refund of 25.00 was issued.", []),
    (issued, "Your refund of 25,00 was issued.", []),
    (issued, "Expected by 2026-10-21; no amount here.", []),
    (issued, "Your refund of 999.00 is on its way.", ["reply_mentions_unknown_amount"]),
    (issued, "We refunded 25.00 and a bonus of 5.00.", ["reply_mentions_unknown_amount"]),
    (pending, "You will receive 140.00 soon.", ["amount_before_refund_issued"]),
    (pending, "You will receive 150.00 soon.", ["amount_before_refund_issued", "reply_mentions_unknown_amount"]),
    (pending, "An agent will update you.", []),
]
for order, text, expected in cases:
    got = check_amounts(draft(text), order)
    assert sorted(got) == sorted(expected), f"{text!r} on {order.order_id}: expected {expected}, got {got}"

settings, checks = Settings(), DEFAULT_CHECKS + (check_amounts,)
injected = draft_reply("T-001", records, FakeProvider(script=["obeys_injection"]), settings, checks=checks, sleep=lambda _: None)
assert "reply_mentions_unknown_amount" in injected.reasons, injected.reasons
normal = draft_reply("T-001", records, FakeProvider(), settings, checks=checks, sleep=lambda _: None)
assert normal.status == "ready", normal.reasons
print(f"{check_amounts.__module__}: amount checks passed; explain your implementation independently.")
