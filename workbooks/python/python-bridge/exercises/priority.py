"""Independent checkpoint. Do not import the reference solution before attempting it."""
from quickcart_bridge.models import Ticket


def priority_ids(tickets: list[Ticket], threshold: int) -> list[str]:
    # TODO: reject bool/noninteger/negative thresholds.
    # TODO: select amounts >= threshold; sort descending amount, then ascending ID.
    # TODO: do not mutate the input list or count a duplicated tag as another ticket.
    raise NotImplementedError('Implement the independent requirement')
