# W-LLM-REL-01 — Reliable drafting under failure

**What do reliability controls change when the dependency is slow, limited or unavailable?**

> **Your goal:** Compare mechanisms against customer outcomes and bounded simulated spend.<br>
> **You need:** [Direct-provider lesson](../refund-drafts/README.md) and the [reliability guide](../../../study-guides/llm-reliability/docs/00-reliable-model-calls.md).<br>
> **Effort:** 15 minutes reading, 60 scenarios, 25 fault drills and 45 independent work; estimated.<br>
> **You will produce:** Scenario predictions/results, repaired failures and an independently tested retry budget. **Status:** Draft; unpiloted, evidence limits remain explicit.

**Starting point:** QuickCart's synthetic drafting traffic runs in a separate simulator package. Keep its environment distinct from `refund-drafts`, `langchain-learning` and `fernwood-notes`; no application state is carried over between them.

**Study route:** Predict each scenario, run the deterministic simulation, diagnose the two faults, then implement the retry-budget extension. Simulated timings and token charges teach mechanism behavior, not a real provider's latency or bill.

<details>
<summary>Reference: unit identity, versions and historical verification</summary>

> **Unit ID:** W-LLM-REL-01 · **Capability:** AI-RELIABLE-01<br>
> **Audience:** Experienced backend engineers who have completed [W-LLM-API-01](../refund-drafts/README.md) and read [SG-REL-00](../../../study-guides/llm-reliability/docs/00-reliable-model-calls.md)<br>
> **Central question:** When the model provider slows down, rate-limits, hangs or runs out of quota, what do your reliability mechanisms change for the customer, the agent and the bill?<br>
> **Effort:** Reading 15 min; guided scenarios 60 min; fault drills 25 min; independent retry budget 45 min. Editorial estimates<br>
> **Artifact:** Your predictions next to observed scenario results, two diagnosed fault drills, a retry budget passing its acceptance check, and a short mechanism-settings note<br>
> **Status:** Draft. 16 tests, 5 source mutations, both drills and the exercise check author-verified; no learner pilot<br>
> **Environment:** Windows PowerShell, uv 0.8.3, Python 3.11.13; **standard library only**; no network, provider or cost

</details>

This is a **simulator**. A drafting service with concurrency limits, end-to-end deadlines, jittered retries, a circuit breaker, a token budget and load shedding handles bursts of synthetic tickets against a fake provider. You can make the provider slow, rate-limited, hanging or out of quota. Every run reports what customers and the bill would see.

**Intuition:** this is a load test you can run at your desk in a fraction of a second. Like a load test, it reveals how mechanisms behave under stress. Unlike one, its provider is invented: it teaches **mechanisms and trade-offs, not the latency or failure rates of any real provider**. Real numbers come from measuring your own provider.

## How simulated time works

`clock.py` runs asyncio on a **virtual-time event loop**. When no task can run, it jumps to the next timer instead of waiting. This makes the authored timeout, sleep and cancellation scenarios repeatable without waiting through the simulated outage. It does not reproduce production scheduling, networks or arbitrary operating-system timing. Compare results in the declared environment rather than promising identical behavior on every machine.

| File | Responsibility |
|---|---|
| `clock.py` | Virtual-time loop, `Clock`, `Deadline` |
| `provider.py` | Fake provider: latency range, concurrency limit (429 with Retry-After), hanging outage window, quota (429 without Retry-After), abstentions |
| `guards.py` | `CircuitBreaker` (closed, open, half-open probe) and `TokenBudget` (reserve, then settle) |
| `service.py` | One request to one outcome: admission and shedding, breaker, budget, bounded attempts, jittered backoff, classification |
| `simulate.py` | Seven scenarios and the user-visible report |

## Setup and verify

From `workbooks/llm/reliable-drafting`:

**Before running:** use your personal copy at this package root. Recorded checks used Windows PowerShell, uv 0.8.3 and Python 3.11.13; runtime uses the standard library. Synchronization may download Python/build tooling. Provider behavior, time and charges are simulated; no key, paid request or server is involved. Preserve your independent changes and evidence.

```powershell
uv sync --python 3.11
uv run python -m unittest discover -s tests -v
uv run reliable-drafting --scenario normal
```

**Expected:** `Ran 16 tests ... OK`. `normal` reports ready 54/60, abstained 6/60, fallback 0/60, response-time p95 2.9 s, and 60 provider calls. By design, every tenth ticket lacks the facts and the model abstains.

**Read the report like a customer.** `outcomes` uses one denominator, the number of requests. `response_time_s` is how long customers waited for *any* response, fallbacks included. `over_deadline` counts customers who waited past the 8 s promise. `provider` is what the provider saw and billed.

## Guided scenarios: predict, run, explain

For each row, **write your prediction first**, then run the command. All numbers below are the deterministic results of the author's runs.

| # | Command | Predict | Observed |
|---|---|---|---|
| 1 | `--scenario slow --no-breaker` | Provider takes 6–9 s, the promise is 8 s: what do customers get, and when? | All 40 fall back with reason `deadline`, at exactly 8.0 s (p95 8.0, max 8.0, 0/40 over deadline) |
| 2 | `--scenario outage` and `--scenario outage --no-breaker` | Calls hang for 15 s. What does the breaker change? | Breaker on: median wait **0.0 s**, 30 provider calls, 16/90 ready. Off: median **6.1 s**, 98 calls, 53/90 ready |
| 3 | `--scenario outage --breaker-cooldown 2` (then 10) | Does a shorter cooldown recover faster? | 31/90 ready at 2 s, 27/90 at 10 s, against 16/90 at 5 s: not monotonic |
| 4 | `--scenario rate_limited` and `--scenario rate_limited --concurrency 4` | The provider accepts 4 concurrent calls; we allow 12. | At 12: 35 rate-limited responses, 92 calls, p95 7.1 s. At 4: **0** rate-limited, 60 calls, p95 3.0 s |
| 5 | `--scenario budget` | The batch budget covers half the traffic. | 29 calls, 14,500 tokens billed, 31/60 fallback `budget_exhausted` |
| 6 | `--scenario quota` | The provider's quota runs out mid-batch. | 29/60 fallback `quota_exhausted`; 60 calls (one per request: no retries) |
| 7 | `--scenario cancel` | Every third customer leaves after 2 s. | 9/60 cancelled; the provider saw 9 cancelled calls (a test also proves budget reservations are released) |

<details><summary>Explanations</summary>

1. **The deadline is the promise.** Each attempt's timeout is the *remaining* time, so customers get an honest fallback at 8 s rather than a draft at 9 s that nobody is waiting for.
2. **The breaker trades answers for speed and provider protection.** During a hanging outage, every un-broken call wastes a slot and the customer's time. The breaker stops that within a few failures. Its cost is shown in row 3.
3. **Recovery lag depends on timing.** A half-open probe that starts inside the outage hangs for its full attempt timeout and keeps the breaker open after the provider recovers. Cooldowns interact with outage shape, so measure them; do not assume.
4. **Excess concurrency produces 429s, not answers.** The 32 extra calls were all rejections (which count against real rate limits) plus their retries, and customers waited longer. Matching the provider's limit queues work politely instead.
5. **Our code enforces the budget before calling:** reserve 600 tokens, settle to the 500 actually used. The modeled charge stays within this accounting contract. Real currency limits also depend on provider pricing, actual usage and cancellation/retry billing; this run does not establish those.
6. **This 429 has no Retry-After;** retrying cannot succeed until someone acts, so each request falls back after one call.
7. **Cancellation stops waiting and frees slots and budget.** This fake provider stops billing cancelled calls; real providers may not (SG-REL-00, section 6).

</details>

**Note on jitter:** `--no-jitter` exists, but at this simulation's scale its effect is small and mixed. Jitter's benefit, avoiding synchronized retries, grows with the number of clients. Do not read more into one small run.

## Break, diagnose, repair 1: deadlines that are not propagated

```powershell
uv run reliable-drafting --scenario slow --no-breaker --no-deadline-propagation
```

**Observed:** 35/40 customers waited past the 8 s promise; p50 27.7 s, p95 59.1 s, max 60.2 s; 105 provider calls, all cancelled. Every attempt got a fresh 5 s timeout and queue waits had no limit, so customers waited a minute for the same fallback. In `service.py`, find every place `propagate_deadline` is checked and explain what each one bounds: the queue wait, the attempt timeout, and the decision to back off.

## Break, diagnose, repair 2: the breaker that blamed a healthy provider

In `service.py`, find:

```python
error = "timeout" if timeout >= cfg.attempt_timeout_s else "deadline_cut_short"
```

Replace it with `error = "timeout"`, then run:

```powershell
uv run reliable-drafting --scenario normal --concurrency 4
uv run python -m unittest discover -s tests
```

**Observed:** the provider is perfectly healthy, yet `breaker_opened` is 1 and 10 customers get `breaker_open` fallbacks (ready falls from 34/60 to 32/60). Two tests fail, including `test_timeout_cut_short_by_own_deadline_does_not_trip_breaker`. **Diagnosis:** requests that queued for a long time start their attempt with little time left; when that short attempt times out, it is *our* deadline expiring, not the provider failing. Counting it as a failure trips the breaker under ordinary load. Restore the line and rerun both commands.

## Independent exercise: a retry budget

Per-request attempt limits still let every request retry at once. Implement `RetryBudget` in `exercises/retry_budget.py`, following its docstring: retries may not exceed a `ratio` of requests seen so far, with a small `minimum`. The service calls `record_request()` for each request and `can_retry()` before each retry.

Write a test of your own first, then run:

```powershell
uv run python exercises/check_retry_budget.py
```

**Expected:** `retry_budget: retry budget checks passed (provider calls 92 -> 66)...`. On the untouched starter it raises `NotImplementedError`; `--reference` runs `retry_budget_reference.py`. The check also confirms the budget changes nothing for a healthy provider.

<details><summary>Progressive hints</summary>

1. Two counters and one comparison are enough: `retries < max(minimum, ratio * requests)`.
2. Count a retry only when you allow it.
3. Validate the arguments in `__init__`, and let a quiet service still retry `minimum` times.

</details>

<details><summary>Worked reasoning</summary>

In the rate-limited scenario, a 10% budget cut provider calls from 92 to 66, and p95 wait from 7.1 s to 4.2 s, but ready drafts fell from 52 to 47. It is a policy choice: during real incidents, retries are the main source of extra load, and a budget converts some would-be answers into fast fallbacks to protect everyone else. In the hanging-outage scenario the budget barely matters, because deadlines run out before retries happen. Name in your note which incident shape your budget is for.

</details>

## Completion evidence

- [ ] `uv run python -m unittest discover -s tests -v` shows 16 passing tests on your restored copy.
- [ ] Your predictions for scenarios 1–7 beside the observed results, with one-sentence explanations.
- [ ] Both drills: the command output, your diagnosis and the passing rerun after repair.
- [ ] `exercises/check_retry_budget.py` passes on **your** `RetryBudget`, with your own test. Disclose any use of the reference.
- [ ] A settings note of about 200 words for QuickCart's sale (SG-REL-00, section 13): concurrency, attempt timeout, attempts, retry budget, breaker and budget, each with the user-visible trade-off you accepted.

**Reflect:** which mechanism's cost surprised you most: fewer answers, longer waits or more provider calls? What would you measure in production before choosing its setting?

## Troubleshooting

| Symptom | Likely cause | Diagnostic and repair |
|---|---|---|
| `RuntimeError: Simulation deadlock` | Code awaits something that never completes and no timer is scheduled | Look for an `await` without a timeout, or a lock that is never released, in your change. |
| Numbers differ from the tables | Code, scenario or seed changed | Results are deterministic; `git diff` shows what differs. |
| A test hangs | A `CancelledError` was swallowed | Re-raise `CancelledError`; never catch `BaseException` around awaits. |
| `ModuleNotFoundError: retry_budget` | Run from the wrong directory | Run from `workbooks/llm/reliable-drafting` with `uv run`. |

## Limits and next step

Cleanup: the simulator runs in virtual time with no network, server or provider, so nothing keeps running. When finished, remove your personal `.venv` after checking its resolved path.

The provider, latencies and failure windows are invented, and the simulator runs one process. Real breakers and budgets are per process unless their state is shared. Real providers may keep billing cancelled work. Real rate limits also count tokens per minute, which this simulator models only through concurrency. Use the simulator to learn the mechanisms, then measure your provider.

**You can now:** predict and then measure what deadlines, retries, concurrency limits, a breaker and a token budget change for customers and the bill, and diagnose a breaker tripped by your own deadline. **Show it:** your scenario predictions, both drills and your settings note.

**Next:** [W-LLM-ACT-01 — safe actions](../safe-actions/README.md) puts these mechanisms behind fault-injectable provider boundaries, adds trusted authorization for tool arguments, and makes side effects durable and idempotent. The [offline controls lab](../../reliability/offline-controls/README.md) is a shorter supplement on the same controls. Return to the [course map](../../../README.md#ordered-capability-map).

**Sources:** See [SG-REL-00](../../../study-guides/llm-reliability/docs/00-reliable-model-calls.md) and the [source ledger](../../../docs/source-ledger.md); asyncio's `Runner(loop_factory=...)` and `asyncio.timeout` from the [Python 3.11 asyncio documentation](https://docs.python.org/3.11/library/asyncio-runner.html).
