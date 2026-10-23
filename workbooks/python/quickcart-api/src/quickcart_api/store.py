import hashlib
import threading

from .models import Category, Ticket, TicketIn


class DuplicateTicket(Exception):
    """The tenant already has this ticket_id under a different idempotency key."""


class IdempotencyConflict(Exception):
    """The idempotency key was reused with a different request body."""


class TicketGone(Exception):
    """The idempotency key refers to a ticket that has since been deleted."""


class TicketStore:
    """In-memory, single-process store. Every key starts with the tenant from trusted identity.

    The lock guards each check-then-write. The critical sections contain no ``await``, so async
    handlers in one event loop cannot interleave inside them; the lock also covers sync handlers
    run in a thread pool. It does NOT coordinate several worker processes or survive a restart:
    a real service needs a database unique constraint on (tenant, idempotency key).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tickets: dict[tuple[str, str], Ticket] = {}
        self._idempotency: dict[tuple[str, str], tuple[str, str]] = {}

    def create(self, tenant: str, key: str, request: TicketIn) -> tuple[Ticket, bool]:
        """Return (ticket, created). A replay with the same key and body returns the original."""
        fingerprint = hashlib.sha256(request.model_dump_json().encode("utf-8")).hexdigest()
        with self._lock:
            prior = self._idempotency.get((tenant, key))
            if prior is not None:
                prior_fingerprint, ticket_id = prior
                if prior_fingerprint != fingerprint:
                    raise IdempotencyConflict
                existing = self._tickets.get((tenant, ticket_id))
                if existing is None:
                    raise TicketGone
                return existing, False
            if (tenant, request.ticket_id) in self._tickets:
                raise DuplicateTicket
            ticket = Ticket(ticket_id=request.ticket_id, amount=request.amount, tags=tuple(request.tags))
            self._tickets[(tenant, ticket.ticket_id)] = ticket
            self._idempotency[(tenant, key)] = (fingerprint, ticket.ticket_id)
            return ticket, True

    def get(self, tenant: str, ticket_id: str) -> Ticket | None:
        with self._lock:
            return self._tickets.get((tenant, ticket_id))

    def set_category(self, tenant: str, ticket_id: str, category: Category) -> Ticket | None:
        with self._lock:
            current = self._tickets.get((tenant, ticket_id))
            if current is None:
                return None
            updated = current.model_copy(update={"status": "triaged", "category": category})
            self._tickets[(tenant, ticket_id)] = updated
            return updated

    def delete(self, tenant: str, ticket_id: str) -> bool:
        """Remove a tenant's ticket; return False when it does not exist for that tenant."""
        with self._lock:
            return self._tickets.pop((tenant, ticket_id), None) is not None

    def count(self, tenant: str) -> int:
        with self._lock:
            return sum(1 for owner, _ in self._tickets if owner == tenant)
