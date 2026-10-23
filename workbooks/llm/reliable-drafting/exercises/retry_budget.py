"""Independent exercise: a process-wide retry budget.

Per-request limits (max_attempts) still allow a fleet of requests to triple provider load during an outage.
A retry budget caps retries across all requests: retries may not exceed `ratio` of requests seen so far,
with a small `minimum` so a quiet service can still retry a few times.

Contract (used by DraftingService through two calls):
  * record_request() is called once per incoming request.
  * can_retry() is called before each retry; return True and count the retry if it is within budget,
    otherwise return False (the service then falls back with reason "retry_budget_exhausted").
  * Reject ratio outside (0, 1] or a negative minimum with ValueError.

Do not open retry_budget_reference.py until you have recorded your own attempt.
"""


class RetryBudget:
    def __init__(self, ratio: float = 0.1, minimum: int = 3) -> None:
        # TODO 1: validate arguments; store them; start counters for requests and retries at zero.
        raise NotImplementedError("Implement RetryBudget.__init__")

    def record_request(self) -> None:
        # TODO 2: count one request.
        raise NotImplementedError

    def can_retry(self) -> bool:
        # TODO 3: allow while retries < max(minimum, ratio * requests); count each allowed retry.
        raise NotImplementedError
