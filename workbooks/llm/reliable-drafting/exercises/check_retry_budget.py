"""Acceptance check for RetryBudget; run explicitly, it is not part of tests/.

From the reliable-drafting directory:
    uv run python exercises/check_retry_budget.py              # checks your exercises/retry_budget.py
    uv run python exercises/check_retry_budget.py --reference  # checks the inspectable reference
"""
import sys

from reliable_drafting.clock import run_simulated
from reliable_drafting.simulate import SCENARIOS, run_scenario

if "--reference" in sys.argv:
    from retry_budget_reference import RetryBudget
else:
    from retry_budget import RetryBudget

for bad in ({"ratio": 0}, {"ratio": 1.5}, {"minimum": -1}):
    try:
        RetryBudget(**bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"RetryBudget({bad}) must raise ValueError")

budget = RetryBudget(ratio=0.5, minimum=1)
assert budget.can_retry() and not budget.can_retry(), "With no requests, only `minimum` retries are allowed"
for _ in range(10):
    budget.record_request()
assert sum(budget.can_retry() for _ in range(10)) == 4, "ratio 0.5 of 10 requests allows 5 retries in total (1 used)"

scenario = SCENARIOS["rate_limited"]
without = run_simulated(run_scenario("rate_limited", scenario)).summary()
with_budget = run_simulated(run_scenario("rate_limited", scenario, retry_budget=RetryBudget(0.1, 3))).summary()
assert with_budget["provider"]["calls"] < without["provider"]["calls"] - 15, (without["provider"], with_budget["provider"])
assert "retry_budget_exhausted" in with_budget["fallback_reasons"], with_budget["fallback_reasons"]
normal = run_simulated(run_scenario("normal", SCENARIOS["normal"], retry_budget=RetryBudget(0.1, 3))).summary()
assert normal["outcomes"]["ready"] == "54/60", "A healthy provider needs no retries; the budget must not change outcomes"
print(f"{RetryBudget.__module__}: retry budget checks passed "
      f"(provider calls {without['provider']['calls']} -> {with_budget['provider']['calls']}); "
      "explain your implementation independently.")
