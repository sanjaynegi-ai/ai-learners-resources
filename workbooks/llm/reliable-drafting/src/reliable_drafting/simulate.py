"""Run a traffic scenario and report what customers and the provider bill would see.

    reliable-drafting --scenario outage
    reliable-drafting --scenario outage --no-breaker
    reliable-drafting --scenario all

Simulated, deterministic-seeded traffic against a fake provider: it teaches mechanisms and trade-offs,
not the latency or failure rates of any real provider.
"""
import argparse
import asyncio
import json
import statistics
from collections import Counter
from dataclasses import dataclass, field, replace

from .clock import Clock, run_simulated
from .provider import FakeProvider, Profile
from .service import Config, DraftingService, Outcome


@dataclass(frozen=True)
class Scenario:
    description: str
    requests: int
    arrivals_per_s: float
    profile: Profile = field(default_factory=Profile)
    config: Config = field(default_factory=Config)
    leave_after_s: float | None = None  # Every third customer closes the chat after this long
    leave_every: int = 3


SCENARIOS = {
    "normal": Scenario("Healthy provider, steady traffic", 60, 4.0),
    "slow": Scenario("Provider latency rises to 6-9 s against an 8 s customer deadline", 40, 2.0,
                     Profile(latency=(6.0, 9.0))),
    "outage": Scenario("Provider calls hang from t=5 s to t=20 s", 90, 3.0, Profile(outage=(5.0, 20.0))),
    "rate_limited": Scenario("Provider accepts 4 concurrent calls; we send up to 12", 60, 2.0,
                             Profile(max_concurrent=4), Config(concurrency=12, queue_limit=40)),
    "budget": Scenario("Batch budget covers about half the traffic", 60, 4.0, config=Config(budget_tokens=15_000)),
    "quota": Scenario("Provider quota runs out mid-batch (no Retry-After)", 60, 4.0, Profile(quota_tokens=12_000)),
    "cancel": Scenario("Every third customer leaves after 2 s", 60, 4.0, leave_after_s=2.0),
}


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round(pct / 100 * len(ordered) + 0.5) - 1))]


@dataclass
class Report:
    name: str
    outcomes: list[Outcome]
    provider: FakeProvider
    service: DraftingService

    def summary(self) -> dict:
        n = len(self.outcomes)
        statuses = Counter(o.status for o in self.outcomes)
        reasons = Counter(o.reason for o in self.outcomes if o.status == "fallback")
        answered = [o.response_time_s for o in self.outcomes if o.status != "cancelled" and o.response_time_s is not None]
        ready = [o.response_time_s for o in self.outcomes if o.status == "ready"]
        rnd = lambda value: None if value is None else round(value, 1)
        return {
            "scenario": self.name, "requests": n,
            "outcomes": {s: f"{statuses[s]}/{n}" for s in ("ready", "abstained", "fallback", "cancelled")},
            "fallback_reasons": dict(sorted(reasons.items())),
            "response_time_s": {"p50": rnd(percentile(answered, 50)), "p95": rnd(percentile(answered, 95)),
                                "max": rnd(max(answered) if answered else None),
                                "over_deadline": f"{sum(t > self.service.config.deadline_s + 0.5 for t in answered)}/{len(answered)}"},
            "ready_p95_s": rnd(percentile(ready, 95)),
            "provider": {"calls": self.provider.calls, "rate_limited": self.provider.rate_limited,
                         "peak_in_flight": self.provider.peak_in_flight, "cancelled_calls": self.provider.cancelled_calls,
                         "tokens_billed": self.provider.tokens_billed},
            "breaker_opened": self.service.breaker.times_opened if self.service.breaker else "off",
        }


async def run_scenario(name: str, scenario: Scenario, config: Config | None = None, retry_budget=None,
                       seed: int = 7) -> Report:
    clock = Clock()
    provider = FakeProvider(clock, scenario.profile, seed)
    service = DraftingService(provider, clock, config or scenario.config, retry_budget, seed=seed + 4)
    outcomes, tasks = [], []
    for ticket in range(1, scenario.requests + 1):
        outcome = Outcome(ticket)
        outcomes.append(outcome)
        task = asyncio.create_task(service.handle(ticket, outcome))
        tasks.append(task)
        if scenario.leave_after_s is not None and ticket % scenario.leave_every == 0:
            asyncio.get_running_loop().call_later(scenario.leave_after_s, task.cancel)
        await clock.sleep(1 / scenario.arrivals_per_s)
    for outcome, result in zip(outcomes, await asyncio.gather(*tasks, return_exceptions=True)):
        if isinstance(result, asyncio.CancelledError):
            outcome.status = "cancelled"
    return Report(name, outcomes, provider, service)


def config_from_args(base: Config, args) -> Config:
    changes = {}
    if args.no_breaker:
        changes["breaker"] = False
    if args.no_deadline_propagation:
        changes["propagate_deadline"] = False
    if args.no_jitter:
        changes["jitter"] = False
    if args.concurrency is not None:
        changes["concurrency"] = args.concurrency
    if args.attempts is not None:
        changes["max_attempts"] = args.attempts
    if args.budget is not None:
        changes["budget_tokens"] = args.budget
    if args.breaker_cooldown is not None:
        changes["breaker_cooldown_s"] = args.breaker_cooldown
    return replace(base, **changes)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Simulate reliability mechanisms for model calls (offline)")
    parser.add_argument("--scenario", choices=[*SCENARIOS, "all"], default="normal")
    parser.add_argument("--no-breaker", action="store_true")
    parser.add_argument("--no-deadline-propagation", action="store_true")
    parser.add_argument("--no-jitter", action="store_true")
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--attempts", type=int)
    parser.add_argument("--budget", type=int, help="Token budget for the whole batch")
    parser.add_argument("--breaker-cooldown", type=float, help="Seconds an open breaker waits before probing")
    args = parser.parse_args(argv)
    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    print("Simulated traffic and fake provider: shows mechanisms and trade-offs, not real provider behavior.")
    for name in names:
        scenario = SCENARIOS[name]
        report = run_simulated(run_scenario(name, scenario, config_from_args(scenario.config, args)))
        print(f"\n# {name}: {scenario.description}")
        print(json.dumps(report.summary(), indent=2))


if __name__ == "__main__":
    main()
