"""One customer request -> one user-visible outcome, whatever the provider does.

Outcomes, as the customer and the agent see them:
  ready      a draft is waiting for the agent                      (the only AI success)
  abstained  the model said the facts were insufficient            (agent handles; correct, not a failure)
  fallback   the system could not get a draft in time or budget    (customer gets an acknowledgement; agent handles)
  cancelled  the customer left before we answered                  (nothing to show; stop spending)
"""
import asyncio
import random
from dataclasses import dataclass, field
from typing import Protocol

from .clock import Clock, Deadline
from .guards import CircuitBreaker, TokenBudget
from .provider import FakeProvider, QuotaExhausted, RateLimited, Unavailable

TOKEN_ESTIMATE = 600  # Reserved before each call; settled to actual usage afterwards


class RetryBudget(Protocol):
    def record_request(self) -> None: ...
    def can_retry(self) -> bool: ...


@dataclass
class Config:
    concurrency: int = 8               # Our in-flight limit, sized to the provider's limit
    queue_limit: int = 20              # Waiting requests beyond this get an immediate fallback (load shedding)
    deadline_s: float = 8.0            # What the customer will wait, end to end, including queueing
    attempt_timeout_s: float = 5.0
    max_attempts: int = 3
    base_backoff_s: float = 0.5
    max_backoff_s: float = 4.0
    jitter: bool = True
    breaker: bool = True
    breaker_threshold: int = 5
    breaker_cooldown_s: float = 5.0
    budget_tokens: int | None = None
    propagate_deadline: bool = True    # Fault drill switch: False gives every wait its own fresh timeout


@dataclass
class Outcome:
    ticket: int
    arrived_at: float = 0.0
    status: str = "pending"
    reason: str | None = None
    attempts: int = 0
    queue_wait_s: float = 0.0
    response_time_s: float | None = None
    tokens: int = 0
    errors: list[str] = field(default_factory=list)


class DraftingService:
    def __init__(self, provider: FakeProvider, clock: Clock, config: Config, retry_budget: RetryBudget | None = None,
                 seed: int = 11) -> None:
        self.provider, self.clock, self.config, self.retry_budget = provider, clock, config, retry_budget
        self.slots = asyncio.Semaphore(config.concurrency)
        self.waiting = 0
        self.breaker = CircuitBreaker(clock, config.breaker_threshold, config.breaker_cooldown_s) if config.breaker else None
        self.budget = TokenBudget(config.budget_tokens) if config.budget_tokens else None
        self.rng = random.Random(seed)

    def _finish(self, outcome: Outcome, status: str, reason: str | None = None) -> Outcome:
        outcome.status, outcome.reason = status, reason
        outcome.response_time_s = self.clock.now() - outcome.arrived_at
        return outcome

    def backoff(self, attempt: int, retry_after: float | None) -> float:
        ceiling = min(self.config.max_backoff_s, self.config.base_backoff_s * 2 ** (attempt - 1))
        if retry_after is not None:
            # Retry-After is a minimum. Jitter on top stops every client retrying at the same instant.
            return retry_after + (self.rng.uniform(0, ceiling) if self.config.jitter else 0.0)
        return self.rng.uniform(0, ceiling) if self.config.jitter else ceiling  # "Full jitter"

    async def handle(self, ticket: int, outcome: Outcome) -> Outcome:
        """Fills `outcome` in place so a caller that cancels us can still read what happened."""
        cfg = self.config
        outcome.arrived_at = self.clock.now()
        deadline = Deadline(self.clock, cfg.deadline_s)
        if self.retry_budget:
            self.retry_budget.record_request()
        if self.waiting >= cfg.queue_limit:
            return self._finish(outcome, "fallback", "queue_full")
        self.waiting += 1
        try:
            if cfg.propagate_deadline:
                async with self.clock.timeout(deadline.remaining()):
                    await self.slots.acquire()
            else:
                await self.slots.acquire()
        except TimeoutError:
            return self._finish(outcome, "fallback", "deadline_in_queue")
        finally:
            self.waiting -= 1
        try:
            outcome.queue_wait_s = self.clock.now() - outcome.arrived_at
            return await self._call(ticket, deadline, outcome)
        finally:
            self.slots.release()

    async def _call(self, ticket: int, deadline: Deadline, outcome: Outcome) -> Outcome:
        cfg = self.config
        for attempt in range(1, cfg.max_attempts + 1):
            if self.breaker and not self.breaker.allow():
                return self._finish(outcome, "fallback", "breaker_open")
            if cfg.propagate_deadline and deadline.expired():
                return self._finish(outcome, "fallback", "deadline")
            if self.budget and not self.budget.reserve(TOKEN_ESTIMATE):
                return self._finish(outcome, "fallback", "budget_exhausted")
            outcome.attempts = attempt
            timeout = min(cfg.attempt_timeout_s, deadline.remaining()) if cfg.propagate_deadline else cfg.attempt_timeout_s
            retry_after = None
            try:
                async with self.clock.timeout(timeout):
                    reply = await self.provider.generate(ticket)
            except asyncio.CancelledError:
                self._settle(0)  # Customer left: release the reservation, record nothing as success.
                raise
            except TimeoutError:
                # Only a full attempt timeout says the provider is slow; a timeout cut short by our own
                # nearly-expired deadline says nothing about provider health.
                error = "timeout" if timeout >= cfg.attempt_timeout_s else "deadline_cut_short"
            except RateLimited as exc:  # Backpressure, not ill health: do not trip the breaker.
                error, retry_after = "rate_limited", exc.retry_after
            except Unavailable:
                error = "unavailable"
            except QuotaExhausted:
                self._settle(0)
                return self._finish(outcome, "fallback", "quota_exhausted")  # Retrying cannot help.
            else:
                self._settle(reply.tokens)
                outcome.tokens += reply.tokens
                if self.breaker:
                    self.breaker.record_success()
                return self._finish(outcome, "abstained" if reply.needs_agent else "ready")
            self._settle(0)
            outcome.errors.append(error)
            if self.breaker and error in ("timeout", "unavailable"):
                self.breaker.record_failure()
            if attempt == cfg.max_attempts:
                break
            if self.retry_budget and not self.retry_budget.can_retry():
                return self._finish(outcome, "fallback", "retry_budget_exhausted")
            delay = self.backoff(attempt, retry_after)
            if cfg.propagate_deadline and delay >= deadline.remaining():
                return self._finish(outcome, "fallback", "deadline")
            await self.clock.sleep(delay)
        return self._finish(outcome, "fallback", "attempts_exhausted")

    def _settle(self, actual: int) -> None:
        if self.budget:
            self.budget.settle(TOKEN_ESTIMATE, actual)
