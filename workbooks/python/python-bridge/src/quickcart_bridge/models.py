from dataclasses import dataclass


class InputError(ValueError):
    """A declared synthetic ticket contract failed; messages never echo raw payloads."""


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    amount: int
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.ticket_id, str) or not self.ticket_id.strip() or len(self.ticket_id) > 64:
            raise InputError('Ticket ID must be nonempty text of at most 64 characters')
        if type(self.amount) is not int or not 0 <= self.amount <= 1_000_000:
            raise InputError('Amount must be an integer in synthetic units, 0–1000000')
        if not isinstance(self.tags, tuple) or len(self.tags) > 10:
            raise InputError('Tags must be a tuple with at most ten values')
        if any(not isinstance(tag, str) or not tag.strip() or len(tag) > 40 for tag in self.tags):
            raise InputError('Tags must be nonempty strings of at most 40 characters')


def parse_ticket(payload: object) -> Ticket:
    if not isinstance(payload, dict) or not {'ticket_id', 'amount'} <= payload.keys():
        raise InputError('Ticket object requires ticket_id and amount')
    if payload.keys() - {'ticket_id', 'amount', 'tags'}:
        raise InputError('Unknown ticket fields')
    tags = payload.get('tags', [])
    if not isinstance(tags, list):
        raise InputError('External tags must be a list')
    return Ticket(payload['ticket_id'], payload['amount'], tuple(tags))


def summarize(tickets: list[Ticket]) -> dict[str, object]:
    # One ticket contributes at most once per tag; annotations alone do not enforce this rule.
    tags = sorted({tag for ticket in tickets for tag in ticket.tags})
    return {'count': len(tickets), 'total_units': sum(ticket.amount for ticket in tickets),
            'by_tag': {tag: sum(tag in ticket.tags for ticket in tickets) for tag in tags}}
