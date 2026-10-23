"""Inspectable reference for the amount check. Consulting it is disclosed assistance, not independent evidence."""
import re

from refund_drafts.domain import Order
from refund_drafts.schema import DraftOut

AMOUNT = re.compile(r"(?<![\d.,-])(\d+)[.,](\d{2})(?![\d-])")


def check_amounts(draft: DraftOut, order: Order) -> list[str]:
    amounts = [float(f"{whole}.{cents}") for whole, cents in AMOUNT.findall(draft.reply_text)]
    if not amounts:
        return []
    problems = []
    if order.refund_status != "issued":
        problems.append("amount_before_refund_issued")
    if any(abs(amount - order.refund_amount) > 0.005 for amount in amounts):
        problems.append("reply_mentions_unknown_amount")
    return problems
