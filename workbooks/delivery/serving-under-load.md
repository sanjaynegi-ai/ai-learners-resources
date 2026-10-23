# Measure admission, overload and recovery

QuickCart can answer one ticket at a time in a demo. When eight staff members submit work together, should all eight calls wait, all call the provider, or should some receive a clear rejection? A faster error can improve aggregate latency while useful work disappears. Measure outcomes and capacity before increasing concurrency.

**Outcome:** defend admission and queue settings using real local HTTP observations. **Prerequisites:** the [tested API](../python/quickcart-api/README.md), [delivery lesson](README.md), and [request reliability](../../study-guides/llm-reliability/docs/00-reliable-model-calls.md). **Effort:** 150–210 minutes estimated: 15 reading, 20 setup, 75 guided measurement/repair, 30 independent analysis and 10–70 additional diagnosis. **Artifact:** your measurement driver, separate simulation and HTTP reports, failure/repair evidence and an independently implemented summary with a capacity decision.

**Starting state:** return to your personal `workbooks/python/quickcart-api` copy, with its completed API and delivery evidence. The supplied `serving.py`, `load_app.py`, tests and `delivery/load_probe.py` are measurement scaffolding. Build your report driver in two increments below. Then change the queue guard, diagnose the fault, restore it and independently implement the summary. This extends the same package; no new framework, environment or deployed service is required. Use a full course checkout for the simulator comparison, which reuses the earlier reliability lab's virtual clock.

**Before execution:** Windows PowerShell, Python 3.11 and uv with the existing lockfile. The runner starts its own single-event-loop uvicorn server in a background thread, binds an OS-assigned port on `127.0.0.1`, sends synthetic HTTP requests and stops the server in `finally`. It accepts no target URL. No cloud, paid model, container build or real customer data is used. Do not expose this lab factory on a public address. Dependencies may download during setup. Reports contain synthetic timings and outcomes; keep your learning records private.

From repository root in PowerShell:

```powershell
Set-Location workbooks/python/quickcart-api
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run python delivery/check_contract.py
```

Expect **27 tests**: the original 19 API tests plus eight admission/cancellation tests. The frozen schema check applies to the normal API factory. The separate lab factory adds `/lab/...` routes solely for this exercise. All remaining commands start from this package directory.

## 1. Predict before sending traffic

Admission decides whether a request may consume bounded service capacity. A semaphore limits active work; it does not by itself bound the number of waiting requests. A queue limit makes waiting explicit, and a total deadline must include that wait. Here rejected work returns HTTP 429 with `Retry-After: 1`; the runner records it without automatically retrying.

The default contract is two active operations, two waiting operations, one second from admission attempt through completion, and 250 ms of cooperative synthetic provider work. The maximum runner settings are four active, eight waiting and 16 client threads. The finite overload burst contains `active + queue + 4` requests. At default settings this is eight, not eight requests per second. Creation, cancellation and bounded status polling are counted separately from job submissions.

For an ideal simultaneous eight-request burst, predict four admitted and four rejected. Two admitted requests wait about 250 ms; the last completion is about 500 ms. Ideal steady useful capacity is `2 / 0.25 = 8 operations/s`, assuming identical work with no overhead or failures. It is **not** measured sustained throughput. A bigger queue does not increase that service rate. A request that waits too long can expire without ever starting provider work.

Run the independent burst model on the earlier reliability simulator's virtual clock:

```powershell
uv run python delivery/predict_load.py --output results/load-prediction.json
```

It predicts four completed and four rejected at defaults, with virtual completion times 0.25 and 0.5 seconds. This model uses a semaphore and a count of work in the system, separately from the serving implementation. It omits HTTP, operating-system scheduling, provider variation and the cancellation/failure phases. The original [reliability simulator](../llm/reliable-drafting/README.md) explores retries, rate limits and breaker recovery; this bounded comparison reuses its virtual clock without importing its environment or treating its timings as service measurements.

**Predict:** if six of eight requests are immediately rejected, can a low p95 prove good service?

<details><summary>Reasoning</summary>

No. Report useful completions / all job requests and outcome counts alongside all-outcome and successful latency. Fast rejections can dominate a distribution. With only eight observations, nearest-rank p95 is the eighth sorted observation; it provides little population-level evidence. A two-second stall and a fast error must not be averaged into an unexplained success metric.

</details>

## 2. Build a measurement driver

Create `delivery/learner_load.py` with the following code. Your responsibility is to collect, interpret and verify the measurements; the supplied observer owns the bounded HTTP workload and server lifecycle.

```python
import json
from pathlib import Path
from load_probe import observe

report = observe(concurrency=2, queue_capacity=2)
destination = Path("results/learner-load.json")
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(report["phases"]["overload"])
print(report["cleanup"])
```

Run `uv run python delivery/learner_load.py`. Confirm the report names the runtime, OS and dependency versions, finite burst size, actual arrival span, observed duration/rate, client timeout, request totals, outcome counts and zero automatic retries. The HTTP run normally matches the four/four prediction at defaults, but retain different observations and diagnose the workload if it does not. Client-side elapsed time includes real networking and scheduling; server queue time covers waiting for admission. Neither measures a real model.

The observer first sends a baseline burst of two requests, then the eight-request overload burst. It next exercises an in-flight duplicate, cancellation of active and queued work, a synthetic provider failure, a deadline timeout, recovery on two fresh tickets and a completed-ticket replay. It waits for active/queued state through real HTTP to coordinate cancellation. Each wait polls at most 60 times over at most three seconds. The complete runner uses fewer than 100 job submissions; the service itself caps recorded valid-ticket job submissions at 100. Each client request has a three-second timeout and no retry. Work phases are finite; reported duration is the observed run duration, not an invented fixed test length.

Interpret the counts carefully: `completed` is a new useful local category update; `replayed` is an already-completed result; `inflight` prevents concurrent duplication; `rejected` is admission refusal; `failed` and `timed_out` are failures; `cancelled` counts explicit application cancellation. For the default scenario, expected job outcomes across all phases are 8 completed, 4 rejected, 4 cancelled, 1 failed, 1 timed out, 1 in-flight conflict and 1 replay: 20 job requests. Polling, fixture creation and cancel commands are additional HTTP requests reported separately. Cancellation commands returning true request cancellation; the original job result and zero remaining capacity establish its completion.

## 3. Turn observations into checks

Append this second increment to your driver, then rerun it:

```python
samples = report["samples"]
counts = {}
for sample in samples:
    outcome = sample["body"]["status"]
    counts[outcome] = counts.get(outcome, 0) + 1
useful = counts.get("completed", 0)
print({"outcomes": counts, "useful": useful, "all_jobs": len(samples),
       "useful_fraction": useful / len(samples)})
stats = report["stats"]
assert stats["active"] == stats["waiting"] == 0
assert stats["max_active"] <= 2 and stats["max_waiting"] <= 2
assert stats["effects"] == useful
assert stats["attempts"] == sum(s["body"]["attempts"] for s in samples)
assert all(s["body"]["status"] == "completed" for s in samples if s["phase"] == "recovery")
```

At the default observed counts, useful fraction is `8 / 20 = 40%` for this deliberately fault-heavy scenario. Overload useful fraction is `4 / 8 = 50%`. These are different denominators; neither is a production success rate. Cancellations and failures are intentional workload probes, not estimates of customer behavior. Replays give users an existing answer but do not count as newly completed work or another effect. Compare `totals.all_client_p95_ms`, `completed_client_p95_ms` and `failed_client_p95_ms`; the one-second timeout is likely to dominate the failure distribution.

Now trace the code path: authenticated tenant and existing ticket → in-flight/completed duplicate guard → bounded admission → FIFO waiting if full → one deadline covering queue and provider → one synthetic category update → permit release in `finally`. Inspect `Admission.acquire/release` in `src/quickcart_api/serving.py`: releasing transfers a permit to a waiter or decrements active capacity. Cancellation must handle both a waiting future and a just-granted future. The tests include those races. `load_app.py` reuses the trusted principal dependency and existing store; a foreign tenant cannot cancel another tenant's task.

This is concurrency admission and backpressure, not a per-client requests-per-second limiter. The base API routes, HTTP connection backlog and arbitrary incoming request bytes are outside this gate. The runner bounds its clients and bodies; the lab is not an internet-facing admission system. No automatic server or client retry is present. A new retry policy would require a bounded retry budget, idempotency and another measurement.

## 4. Break the queue bound and repair it

In your personal `src/quickcart_api/serving.py`, change only the queue comparison from `len(self.waiting) >= self.queue_capacity` to `len(self.waiting) > self.queue_capacity`. Predict the extra admitted waiter. Run:

```powershell
uv run python delivery/load_probe.py --output results/load-fault.json
```

The reference probe should fail its queue-high-water assertion: three waiters fit into a declared two-slot queue. It does not write a passing report after that failure. Inspect the guard, repair `>=`, then run the command again with `--output results/load-repaired.json` and rerun all 27 tests. Preserve the failing command/output and repaired report. Do not increase the declared queue bound merely to make the assertion pass.

**Diagnosis question:** why could testing only final `waiting == 0` miss this defect?

<details><summary>Explained answer</summary>

An oversized queue can eventually drain completely. Final emptiness proves cleanup, not that the bound held during the burst. Check the high-water mark and per-request outcomes as well. Similarly, zero duplicate effects alone does not prove zero duplicate provider calls: compare the attempt count and repeated-ticket results separately.

</details>

## 5. Independent capacity decision

Support asks for fewer rejected requests but refuses a longer one-second deadline. First implement `summarize` in `exercises/load_summary.py` from its docstring, without importing the reference. Use `uv run python exercises/check_load_summary.py` and add checks for a sample with no useful completions and for a single useful result. The checker initially raises `NotImplementedError`. Explained comparison code is in `load_summary_reference.py`; disclose reference use after attempting the task.

Compare two bounded choices on the same synthetic workload:

```powershell
uv run python delivery/predict_load.py --concurrency 1 --queue 2 --output results/prediction-one-worker.json
uv run python delivery/load_probe.py --concurrency 1 --queue 2 --output results/load-one-worker.json
uv run python delivery/load_probe.py --concurrency 2 --queue 0 --output results/load-no-waiting.json
```

Explain the changed burst size: the runner always offers `active + queue + 4`, so these runs test each configuration's saturation boundary rather than identical offered traffic. Do not claim a controlled throughput comparison from those different bursts. Your independent driver must also compare a fixed eight-request burst across the chosen configurations, by adapting the supplied burst helper in your personal `delivery/load_probe.py` to hold `count=8` for the overload phase while retaining its 16-thread, local-target and deadline limits. Preserve both configuration and workload in each report, and compare useful completions, rejections, queue waits, failures and cleanup under that unchanged offered load. The default runner's prediction field assumes its original burst size; update or separately label that prediction when changing the workload.

Defend a keep/reject decision with measured denominators and missing evidence. More waiting cannot increase provider capacity, and a long queue may turn rejections into deadline failures. No configuration in this exercise establishes real provider rate limits, cost, tenant fairness or a service-level objective. Name what measurement would change your decision.

<details><summary>Progressive hints and scoring guidance</summary>

First separate offered work from admitted work. Next compare useful completion and failure counts before p95. Finally inspect attempts/effects and queue high-water/cleanup. A complete self-assessment requires: correct denominator and nearest-rank calculation; fixed-load comparison; deliberate repair; capacity limits held; duplicate/retry accounting; recovery and limitations. A passing reference checker is mechanics evidence, not independent analysis or grading.

</details>

## Troubleshooting, cleanup and completion

| Symptom | Diagnose | Repair and return point |
|---|---|---|
| Missing package/import | Confirm package directory, locked uv environment and full checkout for prediction | Rerun setup; return to step 1 |
| No rejection in burst | Inspect actual arrival span versus work duration and host load | Restore finite synchronized burst; retain the failed observation; return to step 2 |
| Queue high-water exceeds bound | Inspect comparison and configuration | Restore guard, rerun fault/repair then all tests; return to step 4 |
| Recovery stalls | Inspect active/waiting after cancellation, including granted-permit race | Compare release/cleanup with reference and regression tests; return to step 3 |
| Client error or startup failure | Confirm owned server started and inspect local runtime errors | Do not label the run passed; restore environment and rerun step 2 |
| More attempts than expected | Inspect duplicate guard, custom retries and outcome counters | Restore single attempt; add a duplicate regression; return to step 3 |

The runner stops its server thread and closes the listening socket even when a scenario assertion fails. If shutdown fails it raises rather than reporting cleanup success. No persistent service or paid resource remains. Save private evidence before removing only your own generated `results` files; keep course fixtures intact. A client disconnect is **not** the explicit cancellation endpoint: this lab does not detect disconnects or claim remote provider cancellation. Cooperative mock sleep cancellation is exercised. In-memory ticket/idempotency state does not survive restart, and category updates are local effects; consequential external effects need durable idempotency and reconciliation.

**Show it:** predictions beside HTTP observations, your two-step driver, failure/repair, independent summary and fixed-load comparison, queue/latency/outcome denominators, duplicate attempt/effect accounting, recovery and shutdown evidence. Record help used and unexecuted platforms. No learner pilot, model quality, Docker throughput or cloud delivery is implied by an author run.

**Next:** complete the [customer integration rehearsal](customer-rehearsal.md), carrying your measured failure/recovery evidence into the demonstration. The unresolved constraint is provider/deployment behavior under a representative workload, which requires separate authorized evidence.

[Previous: packaging and recovery](README.md) · [Phase overview: course phase 4](../../README.md#your-learning-journey)

**Reference sources:** [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) (trusted dependency reuse; optional 5 min; Python/FastAPI prerequisite; free, no account) and [uvicorn official server source](https://github.com/Kludex/uvicorn/blob/main/uvicorn/server.py) (`Server.run(sockets=...)` and thread signal handling; optional 5 min; async/server prerequisite; free). Checked 2026-10-18 against official pages/source and installed uvicorn 0.54.0. The uvicorn website timed out; its official source was accessible. Runtime versions remain in this package lockfile. No external reading is required to complete the exercise.
