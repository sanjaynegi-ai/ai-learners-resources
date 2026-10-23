"""Small, single-process guards. Each protects a different resource and causes a different user-visible outcome."""
from dataclasses import dataclass

from .clock import Clock


class CircuitBreaker:
    """Stops calling a dependency that keeps failing, so users get a fast fallback instead of a slow failure.

    closed -> (threshold consecutive failures) -> open -> (cooldown elapses) -> half_open: one probe call
    -> success closes it, failure re-opens it. Process-local: several replicas each keep their own state.
    """

    def __init__(self, clock: Clock, threshold: int = 5, cooldown: float = 5.0) -> None:
        self.clock, self.threshold, self.cooldown = clock, threshold, cooldown
        self.state, self.failures, self.opened_at, self.probe_in_flight = "closed", 0, 0.0, False
        self.times_opened = 0

    def allow(self) -> bool:
        if self.state == "open" and self.clock.now() - self.opened_at >= self.cooldown:
            self.state = "half_open"
        if self.state == "closed":
            return True
        if self.state == "half_open" and not self.probe_in_flight:
            self.probe_in_flight = True
            return True
        return False

    def record_success(self) -> None:
        self.state, self.failures, self.probe_in_flight = "closed", 0, False

    def record_failure(self) -> None:
        self.probe_in_flight = False
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.threshold:
            if self.state != "open":
                self.times_opened += 1
            self.state, self.opened_at = "open", self.clock.now()


@dataclass
class TokenBudget:
    """Spending guard for a batch, tenant or day. Reserve an estimate before calling; settle with actual usage.

    Our own guard, enforced before the call. Provider dashboards and alerts are not hard caps on your bill.
    """
    limit: int
    used: int = 0
    reserved: int = 0

    def reserve(self, estimate: int) -> bool:
        if self.used + self.reserved + estimate > self.limit:
            return False
        self.reserved += estimate
        return True

    def settle(self, estimate: int, actual: int) -> None:
        self.reserved -= estimate
        self.used += actual
