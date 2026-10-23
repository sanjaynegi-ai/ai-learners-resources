"""Business validation: schema-valid output can still be wrong. Each check returns problem codes, never raises."""
import re
from collections.abc import Callable

from .domain import Order
from .schema import DraftOut

DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
ORDER_ID = re.compile(r"\bQC-\d+\b")
FORBIDDEN_PHRASES = ("guarantee", "approved", "we promise", "full refund")

Check = Callable[[DraftOut, Order], list[str]]


def check_dates(draft: DraftOut, order: Order) -> list[str]:
    allowed = {order.expected_refund_date.isoformat()} if order.expected_refund_date else set()
    problems = []
    if draft.refund_date_used is not None and draft.refund_date_used.isoformat() not in allowed:
        problems.append("refund_date_used_not_in_order")
    if set(DATE.findall(draft.reply_text)) - allowed:
        problems.append("reply_mentions_unknown_date")
    return problems


def check_promises(draft: DraftOut, order: Order) -> list[str]:
    text = draft.reply_text.lower()
    return [f"forbidden_phrase:{phrase}" for phrase in FORBIDDEN_PHRASES if phrase in text]


def check_no_order_id(draft: DraftOut, order: Order) -> list[str]:
    # The agent tool inserts the verified order ID; a model-written ID could be miscopied or another customer's.
    return ["reply_contains_order_id"] if ORDER_ID.search(draft.reply_text) else []


DEFAULT_CHECKS: tuple[Check, ...] = (check_dates, check_promises, check_no_order_id)


def validate(draft: DraftOut, order: Order, checks: tuple[Check, ...] = DEFAULT_CHECKS) -> list[str]:
    return [problem for check in checks for problem in check(draft, order)]
