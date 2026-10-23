import asyncio
import time
import unittest
from dataclasses import replace

from reliable_drafting.clock import Clock, Deadline, run_simulated
from reliable_drafting.guards import CircuitBreaker, TokenBudget
from reliable_drafting.provider import FakeProvider, Profile
from reliable_drafting.service import Config, DraftingService, Outcome
from reliable_drafting.simulate import SCENARIOS, run_scenario


def summary(name, config=None):
    scenario = SCENARIOS[name]
    return run_simulated(run_scenario(name, scenario, config or scenario.config)).summary()


class VirtualTimeTests(unittest.TestCase):
    def test_simulated_minutes_take_milliseconds_and_timeouts_still_fire(self):
        async def scenario():
            clock = Clock()
            await clock.sleep(60)
            try:
                async with clock.timeout(5):
                    await clock.sleep(30)
            except TimeoutError:
                return clock.now()
        started = time.perf_counter()
        self.assertEqual(run_simulated(scenario()), 65.0)
        self.assertLess(time.perf_counter() - started, 1.0)

    def test_runs_are_deterministic(self):
        self.assertEqual(summary("outage"), summary("outage"))


class GuardTests(unittest.TestCase):
    def test_breaker_opens_probes_once_and_closes(self):
        async def scenario():
            clock = Clock()
            breaker = CircuitBreaker(clock, threshold=2, cooldown=5)
            breaker.record_failure(); breaker.record_failure()
            states = [breaker.state, breaker.allow()]
            await clock.sleep(5)
            states += [breaker.allow(), breaker.state, breaker.allow()]  # one probe only
            breaker.record_success()
            return states + [breaker.state, breaker.allow()]
        self.assertEqual(run_simulated(scenario()), ["open", False, True, "half_open", False, "closed", True])

    def test_failed_probe_reopens(self):
        async def scenario():
            clock = Clock()
            breaker = CircuitBreaker(clock, threshold=1, cooldown=1)
            breaker.record_failure()
            await clock.sleep(1)
            breaker.allow(); breaker.record_failure()
            return breaker.state, breaker.times_opened
        self.assertEqual(run_simulated(scenario()), ("open", 2))

    def test_token_budget_reserves_before_and_settles_after(self):
        budget = TokenBudget(limit=1000)
        self.assertTrue(budget.reserve(600))
        self.assertFalse(budget.reserve(600))  # Reservations count, not just settled usage.
        budget.settle(600, 450)
        self.assertEqual((budget.used, budget.reserved), (450, 0))
        self.assertTrue(budget.reserve(500))


class BackoffTests(unittest.TestCase):
    def service(self, **changes):
        return DraftingService(FakeProvider(Clock(), Profile()), Clock(), replace(Config(), **changes))

    def test_retry_after_is_a_minimum_and_jitter_is_added_on_top(self):
        service = self.service()
        delays = [service.backoff(2, retry_after=2.0) for _ in range(200)]
        self.assertTrue(all(2.0 <= d <= 3.0 for d in delays))
        self.assertGreater(len({round(d, 3) for d in delays}), 50)

    def test_full_jitter_and_cap(self):
        service = self.service()
        self.assertTrue(all(0 <= service.backoff(10, None) <= 4.0 for _ in range(200)))
        fixed = self.service(jitter=False)
        self.assertEqual([fixed.backoff(a, None) for a in (1, 2, 3, 4, 5)], [0.5, 1.0, 2.0, 4.0, 4.0])


class ScenarioTests(unittest.TestCase):
    def test_normal_traffic_answers_everyone_within_deadline(self):
        result = summary("normal")
        self.assertEqual(result["outcomes"], {"ready": "54/60", "abstained": "6/60", "fallback": "0/60", "cancelled": "0/60"})
        self.assertEqual(result["response_time_s"]["over_deadline"], "0/60")

    def test_deadline_propagation_bounds_what_customers_wait(self):
        base = SCENARIOS["slow"].config
        bounded = summary("slow", replace(base, breaker=False))
        unbounded = summary("slow", replace(base, breaker=False, propagate_deadline=False))
        self.assertLessEqual(bounded["response_time_s"]["max"], 8.0)
        self.assertEqual(unbounded["response_time_s"]["over_deadline"], "35/40")
        self.assertGreater(unbounded["provider"]["calls"], bounded["provider"]["calls"])

    def test_breaker_fails_fast_and_protects_the_provider_during_an_outage(self):
        on = summary("outage")
        off = summary("outage", replace(SCENARIOS["outage"].config, breaker=False))
        self.assertEqual((on["response_time_s"]["p50"], off["response_time_s"]["p50"]), (0.0, 6.1))
        self.assertEqual((on["provider"]["calls"], off["provider"]["calls"]), (30, 98))
        self.assertGreater(on["fallback_reasons"]["breaker_open"], 0)

    def test_matching_provider_concurrency_removes_rate_limiting(self):
        over = summary("rate_limited")
        matched = summary("rate_limited", replace(SCENARIOS["rate_limited"].config, concurrency=4))
        self.assertEqual((over["provider"]["rate_limited"], matched["provider"]["rate_limited"]), (35, 0))
        self.assertLess(matched["response_time_s"]["p95"], over["response_time_s"]["p95"])

    def test_budget_and_quota_fall_back_without_retrying(self):
        budget = summary("budget")
        self.assertEqual(budget["fallback_reasons"], {"budget_exhausted": 31})
        self.assertLessEqual(budget["provider"]["tokens_billed"], 15_000)
        quota = summary("quota")
        self.assertEqual(quota["fallback_reasons"], {"quota_exhausted": 29})
        self.assertEqual(quota["provider"]["calls"], 60)  # One call per request: a spent quota is not retried.

    def test_cancelled_customers_stop_provider_work(self):
        result = summary("cancel")
        self.assertEqual(result["outcomes"]["cancelled"], "9/60")
        self.assertEqual(result["provider"]["cancelled_calls"], 9)

    def test_cancellation_releases_budget_reservations(self):
        scenario = replace(SCENARIOS["cancel"], config=Config(budget_tokens=100_000))
        report = run_simulated(run_scenario("cancel", scenario))
        self.assertEqual(report.service.budget.reserved, 0)
        self.assertEqual(report.service.budget.used, report.provider.tokens_billed)

    def test_time_spent_queueing_counts_against_the_deadline(self):
        async def scenario():
            clock = Clock()
            provider = FakeProvider(clock, Profile(latency=(3.0, 3.0)))
            service = DraftingService(provider, clock, Config(concurrency=1, deadline_s=4.0, breaker=False))
            outcomes = [Outcome(n) for n in (1, 2, 3)]
            await asyncio.gather(*(service.handle(o.ticket, o) for o in outcomes))
            return [(o.status, o.reason, round(o.response_time_s, 1)) for o in outcomes]
        first, second, third = run_simulated(scenario())
        self.assertEqual(first, ("ready", None, 3.0))
        self.assertEqual(third, ("fallback", "deadline_in_queue", 4.0))  # Not "answered" at 6+ seconds.
        self.assertLessEqual(second[2], 4.0)

    def test_timeout_cut_short_by_own_deadline_does_not_trip_breaker(self):
        async def scenario():
            clock = Clock()
            provider = FakeProvider(clock, Profile(latency=(3.0, 3.0)))
            service = DraftingService(provider, clock, Config(deadline_s=1.0, breaker_threshold=1))
            outcome = await service.handle(1, Outcome(1))
            return outcome.errors, service.breaker.state
        errors, state = run_simulated(scenario())
        self.assertEqual((errors, state), (["deadline_cut_short"], "closed"))


if __name__ == "__main__":
    unittest.main()
