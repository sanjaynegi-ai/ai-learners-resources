"""The tool registry: what the model may propose, the exact arguments each tool accepts, and the trusted checks.

Arguments are untrusted model output. Strict schemas reject wrong types and unknown fields, so arguments
cannot smuggle identity, tenant or approval. Business checks then use trusted records scoped to the caller.
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from .store import Principal, Store

TicketId = Annotated[str, StringConstraints(pattern=r"^T-\d{1,8}$")]
OrderId = Annotated[str, StringConstraints(pattern=r"^QC-\d{1,8}$")]
APPROVAL_THRESHOLD_CENTS = 2000  # Credits above 20.00 need a supervisor's approval
MAX_CREDIT_CENTS = 5000


class StrictArgs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class SendReplyArgs(StrictArgs):
    ticket_id: TicketId
    body: str = Field(min_length=1, max_length=2000)


class GoodwillCreditArgs(StrictArgs):
    order_id: OrderId
    amount_cents: int = Field(gt=0, le=MAX_CREDIT_CENTS)
    reason: str = Field(min_length=1, max_length=200)


class EscalateArgs(StrictArgs):
    ticket_id: TicketId
    note: str = Field(min_length=1, max_length=500)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    args: type[StrictArgs]
    roles: frozenset[str]
    service: str | None                                   # External system that performs the effect, if any
    check: Callable[[Store, Principal, str, StrictArgs], list[str]]
    needs_approval: Callable[[StrictArgs], bool] = lambda args: False


def _same_ticket(store: Store, principal: Principal, ticket_id: str, args) -> list[str]:
    # The tool may only act on the ticket being handled, and only inside the caller's tenant.
    if args.ticket_id != ticket_id:
        return ["ticket_mismatch"]
    return [] if store.ticket(principal.tenant, args.ticket_id) else ["ticket_not_found"]


def _credit_check(store: Store, principal: Principal, ticket_id: str, args: GoodwillCreditArgs) -> list[str]:
    ticket = store.ticket(principal.tenant, ticket_id)
    order = store.order(principal.tenant, args.order_id)
    if ticket is None or order is None:
        return ["order_not_found"]  # Same answer for "absent" and "another tenant's"
    if ticket[1] != args.order_id:
        return ["order_not_on_ticket"]
    return ["amount_exceeds_order_total"] if args.amount_cents > order[1] else []


TOOLS: dict[str, ToolSpec] = {
    "send_customer_reply": ToolSpec("send_customer_reply", SendReplyArgs, frozenset({"agent", "supervisor"}), "email",
                                    _same_ticket),
    "issue_goodwill_credit": ToolSpec("issue_goodwill_credit", GoodwillCreditArgs, frozenset({"agent", "supervisor"}),
                                      "credits", _credit_check,
                                      lambda args: args.amount_cents > APPROVAL_THRESHOLD_CENTS),
    "escalate_to_supervisor": ToolSpec("escalate_to_supervisor", EscalateArgs, frozenset({"agent", "supervisor"}), None,
                                       _same_ticket),
}
