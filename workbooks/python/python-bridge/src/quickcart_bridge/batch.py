import asyncio
from collections.abc import Awaitable, Callable
from .models import Ticket


async def collect(tickets: list[Ticket], provider: Callable[[Ticket], Awaitable[str]],
                  *, concurrency: int = 2, deadline: float = 0.5) -> list[str]:
    if type(concurrency) is not int or not 1 <= concurrency <= 10 or len(tickets) > 20:
        raise ValueError('At most 20 tickets and 1–10 concurrent calls')
    if type(deadline) not in (int, float) or not 0 < deadline <= 60:
        raise ValueError('Deadline must be positive and at most 60 seconds')
    semaphore = asyncio.Semaphore(concurrency)

    async def one(ticket: Ticket) -> str:
        async with semaphore:
            value = await provider(ticket)
            if not isinstance(value, str):
                raise TypeError('Provider result must be text')
            return value

    tasks: list[asyncio.Task[str]] = []
    try:
        async with asyncio.timeout(deadline):
            tasks = [asyncio.create_task(one(ticket)) for ticket in tickets]
            return list(await asyncio.gather(*tasks))
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
