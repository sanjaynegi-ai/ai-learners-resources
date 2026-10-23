"""Assemble the model request in code: trusted instructions, looked-up data, delimited untrusted text."""
from dataclasses import dataclass
from importlib import resources

from .domain import Order, Ticket

PROMPT_VERSION = "refund_reply_v1"


@dataclass(frozen=True)
class ModelRequest:
    instructions: str  # Trusted: versioned file reviewed like code.
    input_text: str    # Supplied data plus the untrusted ticket, each in its own delimited block.
    prompt_version: str
    ticket_id: str = ""  # Metadata for logging and replay; never sent to the provider.


def load_instructions(version: str = PROMPT_VERSION) -> str:
    return resources.files("refund_drafts").joinpath("prompts", f"{version}.txt").read_text(encoding="utf-8")


def neutralize(text: str) -> str:
    """Untrusted text must not be able to close our delimiters, e.g. by writing </ticket>."""
    return text.replace("<", "&lt;").replace(">", "&gt;")


def build_request(order: Order, policy: str, ticket: Ticket, version: str = PROMPT_VERSION) -> ModelRequest:
    date_text = order.expected_refund_date.isoformat() if order.expected_refund_date else "unknown"
    input_text = (
        f"<order>payment_method: {order.payment_method}; refund_status: {order.refund_status}; "
        f"expected_refund_date: {date_text}; refund_amount: {order.refund_amount:.2f}; "
        f"language: {order.language}</order>\n"
        f"<policy>{policy}</policy>\n"
        f"<ticket>{neutralize(ticket.text)}</ticket>"
    )
    return ModelRequest(load_instructions(version), input_text, version, ticket.ticket_id)
