import asyncio
from typing import Protocol, get_args

from .models import Category, Ticket

CATEGORIES: tuple[str, ...] = get_args(Category)


class TriageProvider(Protocol):
    """Stands in for a model or remote classifier. Its output is untrusted data."""

    async def classify(self, ticket: Ticket) -> object: ...


class TriageUnavailable(Exception):
    """The provider failed or returned unusable output; maps to 502."""


class TriageTimedOut(Exception):
    """The provider exceeded the configured bound; maps to 504."""


class MockTriageProvider:
    """Deterministic offline provider for control-flow tests. It says nothing about model quality."""

    async def classify(self, ticket: Ticket) -> object:
        await asyncio.sleep(0)
        for tag in ticket.tags:
            if tag in ("refund", "billing"):
                return "billing"
            if tag in ("shipping", "delivery"):
                return "shipping"
            if tag == "returns":
                return "returns"
        return "other"


async def classify_bounded(provider: TriageProvider, ticket: Ticket, timeout: float) -> Category:
    try:
        async with asyncio.timeout(timeout):
            raw = await provider.classify(ticket)
    except TimeoutError:
        raise TriageTimedOut from None
    except Exception as error:  # Not BaseException: caller cancellation must still propagate.
        raise TriageUnavailable from error
    if not isinstance(raw, str) or raw not in CATEGORIES:
        raise TriageUnavailable
    return raw  # type: ignore[return-value]  # Membership in CATEGORIES was checked above.
