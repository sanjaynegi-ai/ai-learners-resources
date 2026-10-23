"""Requirement change: drafts must never claim a refund has been issued when the order says it has not.

From Support Operations, after two complaints:
  * If order.refund_status is not "issued", a reply that says or implies the refund was issued, sent,
    processed, refunded or is on its way must be rejected with the code "claims_refund_issued".
  * Replies for issued refunds are not affected. Holding replies ("an agent will check") must still pass.
  * QuickCart replies in English and German today; cover both. Return [] when there is no problem. Never raise.

Do not open status_claims_reference.py until you have recorded your own attempt.
"""
from refund_drafts.domain import Order
from refund_drafts.schema import DraftOut


def check_status_claims(draft: DraftOut, order: Order) -> list[str]:
    # TODO 1: return [] immediately when the refund really was issued.
    # TODO 2: look for English and German phrases that claim issue or dispatch (case-insensitive).
    # TODO 3: return ["claims_refund_issued"] if any appear.
    raise NotImplementedError("Implement check_status_claims")
