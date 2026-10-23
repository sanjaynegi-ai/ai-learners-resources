"""Inspectable reference for the retry budget. Consulting it is disclosed assistance, not independent evidence."""


class RetryBudget:
    def __init__(self, ratio: float = 0.1, minimum: int = 3) -> None:
        if not 0 < ratio <= 1 or minimum < 0:
            raise ValueError("ratio must be in (0, 1] and minimum must be non-negative")
        self.ratio, self.minimum = ratio, minimum
        self.requests = self.retries = 0

    def record_request(self) -> None:
        self.requests += 1

    def can_retry(self) -> bool:
        if self.retries < max(self.minimum, self.ratio * self.requests):
            self.retries += 1
            return True
        return False
