"""Inspectable reference; using it is disclosed assistance, not independent evidence."""
from quickcart_bridge.models import Ticket


def priority_ids(tickets: list[Ticket], threshold: int) -> list[str]:
    if type(threshold) is not int or threshold < 0:
        raise ValueError('Nonnegative integer threshold required')
    return [ticket.ticket_id for ticket in sorted(tickets, key=lambda t: (-t.amount, t.ticket_id))
            if ticket.amount >= threshold]
