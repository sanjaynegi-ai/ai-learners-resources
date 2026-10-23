"""A deterministic fake model provider whose failure behavior can be scripted per scenario.

Errors mirror what real providers return: 429 with Retry-After for rate limits; a 429 *without* Retry-After for an
exhausted spend quota, which must not be retried; 5xx-style unavailability. It simulates timing and failures only.
"""
import random
from dataclasses import dataclass

from .clock import Clock


class ProviderError(Exception):
    retryable = True


class RateLimited(ProviderError):
    def __init__(self, retry_after: float) -> None:
        super().__init__(f"rate_limited (retry after {retry_after:g}s)")
        self.retry_after = retry_after


class Unavailable(ProviderError):
    pass


class QuotaExhausted(ProviderError):
    retryable = False  # Like a spend cap: retrying fails until an operator acts.


@dataclass(frozen=True)
class Reply:
    needs_agent: bool  # The model abstained: facts insufficient. Not a failure, not a ready answer.
    tokens: int


@dataclass
class Profile:
    latency: tuple[float, float] = (1.0, 3.0)  # Uniform range, simulated seconds
    max_concurrent: int = 100                  # Provider-side concurrency limit -> RateLimited beyond it
    retry_after: float = 2.0
    outage: tuple[float, float] | None = None  # Simulated-time window in which the provider is broken
    outage_hangs: bool = True                  # Broken calls hang (common in real outages) instead of erroring fast
    quota_tokens: int | None = None            # Provider-side quota; QuotaExhausted once spent
    abstain_every: int = 10                    # Every Nth ticket lacks facts and the model abstains
    tokens_per_call: int = 500


class FakeProvider:
    def __init__(self, clock: Clock, profile: Profile, seed: int = 7) -> None:
        self.clock, self.profile, self.rng = clock, profile, random.Random(seed)
        self.calls = self.rate_limited = self.in_flight = self.peak_in_flight = self.tokens_billed = 0
        self.cancelled_calls = 0

    async def generate(self, ticket_number: int) -> Reply:
        self.calls += 1
        profile = self.profile
        if profile.quota_tokens is not None and self.tokens_billed >= profile.quota_tokens:
            raise QuotaExhausted("quota_exhausted")
        if self.in_flight >= profile.max_concurrent:
            self.rate_limited += 1
            raise RateLimited(profile.retry_after)
        now = self.clock.now()
        if profile.outage and profile.outage[0] <= now < profile.outage[1]:
            if profile.outage_hangs:
                try:
                    await self.clock.sleep(600)  # Only the caller's timeout ends this wait.
                except BaseException:
                    self.cancelled_calls += 1
                    raise
            await self.clock.sleep(0.2)
            raise Unavailable("unavailable")
        self.in_flight += 1
        self.peak_in_flight = max(self.peak_in_flight, self.in_flight)
        latency = self.rng.uniform(*profile.latency)
        try:
            await self.clock.sleep(latency)
        except BaseException:
            self.cancelled_calls += 1
            raise
        finally:
            self.in_flight -= 1
        # Optimistic simplification: a cancelled call here stops and is not billed. A real provider may keep
        # generating, and billing, after your client gives up; do not count cancellation as a guaranteed saving.
        self.tokens_billed += profile.tokens_per_call
        return Reply(needs_agent=ticket_number % profile.abstain_every == 0, tokens=profile.tokens_per_call)
