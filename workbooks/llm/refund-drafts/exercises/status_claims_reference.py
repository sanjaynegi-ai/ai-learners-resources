"""Inspectable reference for the status-claims check. Consulting it is disclosed assistance, not independent evidence."""
from refund_drafts.domain import Order
from refund_drafts.schema import DraftOut

CLAIMS = (
    "issued", "has been sent", "was sent", "on its way", "processed", "refunded", "has been paid",
    "veranlasst", "überwiesen", "ausgelöst", "unterwegs", "erstattet", "ausgezahlt",
)


def check_status_claims(draft: DraftOut, order: Order) -> list[str]:
    if order.refund_status == "issued":
        return []
    text = draft.reply_text.lower()
    return ["claims_refund_issued"] if any(phrase in text for phrase in CLAIMS) else []
