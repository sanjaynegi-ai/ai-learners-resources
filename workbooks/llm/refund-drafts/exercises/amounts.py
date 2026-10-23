"""Independent extension: stop drafts from stating amounts the order record does not support.

Requirement from Support Operations:
  * Any money amount written with two decimals (25.00, 999.00, or 60,50 with a decimal comma) must equal the
    order's refund_amount; otherwise report "reply_mentions_unknown_amount".
  * If the refund has not been issued (refund_status != "issued"), any such amount is premature; report
    "amount_before_refund_issued".
  * Dates such as 2026-10-21 are not amounts. Return [] when there is no problem. Never raise.

Do not open amounts_reference.py until you have recorded your own attempt.
"""
from refund_drafts.domain import Order
from refund_drafts.schema import DraftOut


def check_amounts(draft: DraftOut, order: Order) -> list[str]:
    # TODO 1: find every two-decimal amount in draft.reply_text (accept "." or "," as the decimal mark).
    # TODO 2: if any are present and order.refund_status != "issued", report "amount_before_refund_issued".
    # TODO 3: report "reply_mentions_unknown_amount" if any amount differs from order.refund_amount.
    raise NotImplementedError("Implement check_amounts")
