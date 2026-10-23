# Reliable Model Calls: What the Customer Experiences

**When a provider slows down or fails, what changes for the customer, support agent and bill?**

> **Your goal:** Choose reliability controls and predict their user-visible trade-offs.<br>
> **You need:** [LLM generation](../../llm-foundations/docs/00-how-llms-generate-text.md), a direct-provider call and [async cleanup](../../../workbooks/python/03-async-and-exceptions.ipynb).<br>
> **Effort:** 75-90 minutes reading, estimated.<br>
> **You will produce:** Prediction answers and a defended reliability design, followed by simulator observations. **Status:** Draft; unpiloted, evidence limits remain explicit.

**Starting point:** QuickCart is the fictional e-commerce platform used across the course. Its refund-draft service now faces sale traffic and provider faults. This is a conceptual guide: no installation, account or paid call is needed to study it.

**Study route:** Trace deadlines, retries, cancellation, concurrency, budgets and fallback from the customer's experience. Attempt the calculations before revealing answers, then test the mechanism choices in the separate drafting simulator.

<details>
<summary>Reference: unit identity, versions and historical verification</summary>

> **Unit ID:** SG-REL-00 · **Capability:** AI-RELIABLE-01 · [Course map](../../../README.md#ordered-capability-map)
> **Series status:** Draft. Conceptual chapter; worked figures come from cited sources or from the deterministic simulator in [W-LLM-REL-01](../../../workbooks/llm/reliable-drafting/README.md). No learner pilot.
> **Chapter 00 · Self-study guide · Estimated study time: 75–90 minutes**
>
> **Audience:** Experienced backend engineers who have built a direct model call (W-LLM-API-01).
>
> **Prerequisites:** [SG-LLM-00](../../llm-foundations/docs/00-how-llms-generate-text.md) (latency, truncation, cost per token); [W-PY-BRIDGE-02](../../../workbooks/python/03-async-and-exceptions.ipynb) (asyncio timeouts and cancellation). The [queue-based load-levelling chapter](../../cloud-architecture-patterns/scalability-patterns/docs/04-queue-based-load-leveling.md) is useful background.
>
> **Running example:** QuickCart's refund-draft service during a sale, while the model provider slows down, rate-limits and briefly fails.
>
> **Central question:** When the model provider misbehaves, what does each reliability mechanism change for the customer, the support agent and the bill?
>
> **Outcome:** Choose and size retries, deadlines, cancellation, concurrency limits, budgets, fallbacks and abstention for a model call, predicting each one's user-visible effect and its cost.
>
> **Evidence:** Your answers to the prediction prompts, knowledge checks and design challenge, then the simulator runs in W-LLM-REL-01.

</details>

> [!TIP]
> For each mechanism, predict four things: response received, waiting time, dependency work and human follow-up. Faster fallback is not the same outcome as a successful draft.

## Learning objectives

By the end of this chapter, you should be able to:

- Decide which provider errors to retry, compute retry amplification, and explain jitter and retry budgets.
- Propagate one end-to-end deadline through queueing, attempts and backoff.
- Make cancellation stop work and release reservations, and say what it does not save.
- Size concurrency from provider limits with Little's law, and shed load early.
- Enforce token and money budgets before calls, not after the bill.
- Distinguish ready, abstained, fallback and cancelled outcomes, and report them separately.
- Explain a circuit breaker's benefit and its recovery-lag cost.

## 1. Start with intuition: a restaurant at rush hour

A kitchen during a rush runs into every problem in this chapter:

- **Retries:** a waiter resends an order the kitchen lost. If every waiter resends every slow order, the kitchen drowns.
- **Deadlines:** a customer will wait about 20 minutes. A dish served at 40 minutes is worth nothing, however good.
- **Cancellation:** when a customer leaves, the kitchen should stop cooking for them.
- **Concurrency:** there are six burners. Taking a seventh order at once does not cook it faster.
- **Budget:** there are ingredients for 200 covers today.
- **Fallback:** "the kitchen is backed up; here is bread while you wait, or we can take your order later."
- **Abstention:** "we cannot make that dish." That is a correct answer, not a failure.

**Where the analogy stops:**
- A model provider bills by the token, and may keep "cooking", and billing, after you stop waiting.
- Its rate limits are enforced by someone else.
- A fluent but wrong dish looks exactly like a right one, so section 7 matters as much as speed.

## 2. The QuickCart problem

During a sale, the refund-draft service from W-LLM-API-01 handles several tickets a second. On the day:

- the provider's latency rises from 2 s to 7 s;
- then it returns 429 rate-limit errors;
- then, for 15 minutes, calls simply hang.

Customers see spinners for a minute, agents get nothing, and the bill shows three times the usual call count. Nothing was "down" in our code. Every symptom came from how our code waited, retried and admitted work.

**Pause and predict:** which symptom does each mechanism in section 1 prevent, and which might it make worse?

## 3. Mechanisms and what the user sees

| Mechanism | Protects | User-visible effect when it acts | Metric to watch |
|---|---|---|---|
| **Retry** (bounded, jittered) | Success rate against transient errors | A brief extra wait, then an answer | Retries per request; share of 429/5xx |
| **Deadline** (end to end) | The customer's time | A fallback *on time* instead of a late answer | Response-time p95 and max against the promise |
| **Cancellation** | Capacity and money | Nothing: the customer left | Cancelled calls; work done after cancel |
| **Concurrency limit** | The provider and your rate limits | Queueing, then answers in order | In-flight calls; 429 rate; queue wait |
| **Load shedding** | Everyone already admitted | An immediate fallback for the overflow | Shed count; queue depth |
| **Budget** (tokens or money) | The bill | Fallbacks once the budget is spent | Budget used against limit; budget fallbacks |
| **Circuit breaker** | Customers and the provider during an outage | An instant fallback instead of a long hang | Breaker state; time to recover |
| **Fallback** | The customer relationship | An honest acknowledgement; an agent takes over | Fallback rate by reason |
| **Abstention** | Correctness | "An agent will confirm": the model lacked facts | Abstention rate; whether it was justified |

## 4. Retries: only the right errors, only at one layer, never in lockstep

**Retry only what can succeed next time:**

| Retry with backoff | Do not retry |
|---|---|
| Timeouts and connection failures | 400 bad request, 401/403 auth, 404 unknown model |
| 429 **with** a Retry-After header | 429 meaning an exhausted spend quota: Anthropic documents a spend-cap 429 with **no** `retry-after`, where retries fail until access resumes |
| 5xx and "overloaded" responses | Output that failed validation for the same deterministic reason |

**Amplification multiplies quietly.** Google's SRE book gives an example in which three layers each make 4 attempts, so "a single user action may create 64 attempts (4^3)" ([Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)). Recall from W-LLM-API-01 that the OpenAI SDK retries twice by default. If the browser makes up to 3 attempts (it retries twice), your service makes 3 attempts, and the SDK makes 3 per attempt, one click can become **3 × 3 × 3 = 27 provider calls**, during exactly the incident when the provider is struggling. Retry at **one** layer, and disable the others.

**Backoff and jitter.** Wait longer after each failure (exponential backoff), and randomize the wait (jitter) so that thousands of clients do not retry at the same instant. In the common "full jitter" form, the wait is a random value between zero and `min(cap, base × 2^attempt)`. Marc Brooker's analysis found jittered backoff clearly better than plain exponential backoff, and recommends it as standard practice for remote clients ([AWS Architecture Blog, 2015](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)).

**Retry-After is a minimum.** OpenAI's guidance is to treat the header's value as a minimum, use exponential backoff when it is absent, add random jitter, and cap both attempts and total retry time. It also notes that "unsuccessful requests contribute to your per-minute limit" ([OpenAI: Rate limits](https://developers.openai.com/api/docs/guides/rate-limits)). Waiting *exactly* Retry-After seconds, with no jitter, makes every rate-limited client return at the same moment.

**Retry budgets** cap retries across the whole process, for example "retries may not exceed 10% of requests". A per-request limit then cannot triple fleet-wide load during an incident. The SRE book recommends a server-wide retry budget ("If the retry budget is exceeded, don't retry; just fail the request"). In the simulator's rate-limited scenario, a 10% budget cut provider calls from 92 to 66 and the p95 response time from 7.1 s to 4.2 s, at the cost of 6 more fallbacks out of 60 (ready drafts fell from 52 to 47). That is a trade-off you choose deliberately.

## 5. Deadlines: one promise, propagated

![Two timelines against an 8-second customer deadline. With propagation, after 1.2 s queueing, a failed first attempt and a 0.8 s wait, the second attempt gets only the 3.0 s remaining, and the fallback is shown at 8.0 s. Without propagation, the second attempt gets a fresh 5 s timeout and the fallback arrives at 10.0 s, 2 s late.](../diagrams/01-deadline-timeline.svg)

**Diagram walkthrough:** Time runs left to right and the amber line is the promise made to the customer. Both rows have the same queue wait, first attempt and backoff. In the top row, the deadline was created once, at the edge, and every later wait asks how much time is left. Attempt 2 gets 3.0 s, not its usual 5 s, and the customer gets an honest fallback exactly on time. In the bottom row, each step uses its own fixed timeout, so the same failure reaches the customer 2 s late. The invariant: **time spent queueing and backing off belongs to the customer's budget.** The figure omits how the fallback is rendered and what happens to the late provider work.

"Rather than inventing a deadline when sending RPCs to backends, servers should employ deadline propagation," as the SRE book puts it. In the simulator's slow-provider scenario, with the breaker off, propagation kept every response within the 8 s promise. Without it, 35 of 40 customers waited longer, and the p95 reached 59 s.

**Sizing an attempt timeout:** set it from the provider's measured latency percentiles for your request size, not from a round number. Then check what your deadline leaves for retries. With an 8 s promise and a 5 s attempt timeout, a retry after a *timeout* has at most about 3 s left, which is rarely enough. Retries mostly help with fast failures such as 429s and 503s. Know which kind you are paying for.

## 6. Cancellation: stop work for people who left

When a customer closes the chat, or an upstream deadline fires, cancel the in-flight work. In asyncio that means letting `CancelledError` propagate rather than catching it (W-PY-BRIDGE-02), releasing any budget reservation, and not counting the request as an answer.

Be precise about what cancellation saves. It frees your concurrency slot and stops *your* waiting. Whether the provider stops generating, and stops billing, depends on the provider and the transport; do not assume it does. The simulator optimistically assumes a cancelled call is not billed, and it says so in its code.

## 7. Concurrency, overload and load shedding

**Little's law** relates in-flight work to arrivals and latency: *in flight = arrival rate × average time in the system*. QuickCart receives 2 drafts a second, and each takes about 2 s, so about **4 calls are in flight**. If the provider allows 4 concurrent calls, you are at the edge. If latency doubles to 4 s, you need 8, and the provider will reject the excess with 429s.

What to do about it:

- **Match your concurrency limit to the provider's.** Excess calls do not go faster; they come back as 429s that still count against your rate limit. In the simulator, a provider accepting 4 concurrent calls received 35 rate-limited responses (92 calls for 60 requests) when our limit was 12. With our limit at 4: zero 429s, 60 calls, and a p95 response time of 3.0 s instead of 7.1 s.
- **Queue a little, shed early.** A request that waits longer than its deadline in a queue was never going to be answered on time. The SRE book favors small queues, so a server rejects early instead of letting latency grow. Give overflow requests an immediate fallback ("queue full"): fast and honest beats slow and late.
- **Know the provider's units.** Providers limit requests per minute *and* tokens per minute (and sometimes per day). Anthropic documents that limits use a token bucket and can be enforced over short intervals, so a burst can hit a per-minute limit ([Anthropic: Rate limits](https://platform.claude.com/docs/en/api/rate-limits)).

## 8. Budgets: decide the spend before the call

Every call costs input tokens plus output tokens. Bound both:

- **Per request:** a cap on input size, and `max_output_tokens`.
- **Per batch, tenant or day:** a token or money budget in *your* code. **Reserve** an estimate before calling and **settle** to actual usage afterwards. Reservations count against the budget, so concurrent requests cannot overspend it together.

When the budget is spent, give a clear fallback and an alert. A provider's dashboard alerts and spend limits are a backstop, not your control: alerts are not hard caps, and a provider spend cap stops *all* your traffic at once.

In the simulator's budget scenario, a 15,000-token batch budget let 29 calls through, billed 14,500 tokens, and returned 31 "budget exhausted" fallbacks. The bill stayed exactly where it was promised.

## 9. Ready, abstained, fallback, cancelled: count them honestly

![A request passes four gates: admission (queue limit, budget), circuit breaker, a bounded call with jittered retries, then classification of the answer. The first three gates can lead to a fallback with a stated reason; the last leads to ready or abstained. A customer leaving at any point cancels work and releases reservations.](../diagrams/02-outcome-gates.svg)

**Diagram walkthrough:** Follow a request down the gates. Each of the first three can stop it with a **fallback**: a fast, honest acknowledgement to the customer, with the ticket handed to an agent, and a recorded reason. A request that gets through is classified as **ready** (a draft for the agent) or **abstained** (the model said it lacked the facts). The dashed note applies at every step: a customer who leaves turns the request into **cancelled**. The invariant: **only ready counts as an AI success**, and every outcome is reported over the same denominator of requests.

Why the distinction matters:

- A fallback is not a success with a different label. If 30% of requests fall back, the AI feature is mostly not working, whatever the error rate says.
- Abstention is often *correct* (SG-LLM-01), but it still lands on an agent. Count it, and check whether it was justified.
- Fallbacks need **human capacity**. A fallback that promises "an agent will reply within the hour" has to be backed by agents. When the drafting service falls back to people during an outage, check that the people can absorb it.
- **Fallback content must be honest.** Never fall back to a canned "your refund is on its way": that is a fabricated answer by another route.

## 10. Circuit breakers: fail fast, at the cost of recovery lag

A circuit breaker counts consecutive failures. Past a threshold it **opens**: calls fail immediately without touching the provider. After a cooldown it lets one **probe** through, and closes again if the probe succeeds ([Martin Fowler: CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html)).

In the simulator's outage scenario, where calls hang for 15 s, the breaker brought the median customer wait from 6.1 s to 0.0 s and cut provider calls from 98 to 30. **But** it answered fewer requests (16 against 53 ready out of 90), because a probe sent during the outage hung for its full timeout and kept the breaker open after the provider had recovered. Trying cooldowns of 2, 5 and 10 s gave 31, 16 and 27 ready: not even monotonic. Breaker settings interact with outage timing, so measure them against realistic failure patterns rather than trusting defaults.

Two practical cautions:

- **Count the right failures.** A timeout cut short by the request's own nearly-expired deadline says nothing about provider health. If you count it, a healthy but busy provider will trip your breaker. The workbook fixes exactly this bug.
- **Breakers and budgets are per process.** Ten replicas keep ten breakers and ten budgets unless you share the state. Decide whether that is acceptable.

### Common misconceptions

| Misconception | Correction |
|---|---|
| "More retries means more reliability." | Retries multiply load during the very incidents they react to; bound them, jitter them, budget them. |
| "Each call has a timeout, so we have a deadline." | Without propagation, timeouts add up; the customer's wait is the sum. |
| "A 429 always means wait and retry." | A spend-cap 429 without Retry-After will not succeed until someone acts. |
| "Higher concurrency means higher throughput." | Past the provider's limit you get 429s, not answers. |
| "A fallback is a successful response." | It is a graceful failure; report it separately. |
| "Cancelling the request saves the money." | It frees your capacity; provider billing for in-flight work depends on the provider. |
| "The provider's spend alert protects our budget." | Alerts notify; your code must enforce the budget before calling. |

## 11. Production concerns

- **Observe the outcomes the user sees:** counts of ready, abstained, fallback (by reason) and cancelled; response-time p50, p95 and max against the promise; 429 rate; breaker state; budget used.
- **Alert on change, not just failure.** A rising fallback share or p95 is an incident even when no request errors.
- **Choose numbers from data:** attempt timeouts from latency percentiles, concurrency from provider limits and Little's law, budgets from expected volume. Revisit them when the model, prompt length or traffic changes.
- **Ownership:** someone owns the budget numbers, the fallback wording and the agent capacity behind it.
- **Test failure on purpose:** fake slow, rate-limited, hanging and quota-exhausted providers in CI, as the workbook does.

## 12. Knowledge checks

**1.** The browser retries twice, your API makes 3 attempts, and the SDK keeps its default of 2 retries. During an outage, how many provider calls can one click cause, and what do you change?

<details>
<summary>Show answer and explanation</summary>

3 × 3 × 3 = **27**. Keep retries at one layer, your service, with a deadline and a retry budget. Set the SDK's `max_retries=0` (as in W-LLM-API-01) and make the browser retry only on explicit "try again later" responses.

</details>

**2.** Arrivals are 5 requests a second, and average model latency is 3 s. The provider allows 10 concurrent calls. What happens, and what are your options?

<details>
<summary>Show answer and explanation</summary>

Little's law: 5 × 3 = **15 in flight** needed, but only 10 are allowed, so you are overloaded by about 50%. The queue grows without bound unless you act. Options: shed overflow early with a fallback; reduce latency (shorter outputs, a faster model); request higher limits; or move non-urgent work to a batch queue. Raising your own concurrency to 15 only produces 429s.

</details>

**3.** Your promise is 6 s; the provider's p99 latency is 5 s; your attempt timeout is 5 s. Is a retry after a timeout ever useful?

<details>
<summary>Show answer and explanation</summary>

Barely. A timed-out first attempt leaves at most about 1 s, minus backoff, for a second one that typically needs more. Retries here only make sense for fast failures (429, 503). Either accept one attempt plus a fallback for timeouts, or lower latency so a retry fits.

</details>

**4.** Out of 1,000 requests yesterday: 610 ready, 90 abstained, 260 fallback (200 breaker open, 60 deadline) and 40 cancelled. A manager says "96% handled successfully". What do you report instead?

<details>
<summary>Show answer and explanation</summary>

AI drafts ready: **610/1,000 (61%)**. Abstained 90/1,000; fallback 260/1,000, mostly the breaker (an outage); cancelled 40/1,000. "Handled" merges a graceful failure with success. The useful story is that an outage turned a quarter of requests into agent work, so check whether agents had the capacity.

</details>

## 13. Design challenge: refund drafts for the sale

Next week's sale is forecast at 6 drafts per second at peak. Measured provider latency for your prompt is about 2 s on average, with a p99 of 4 s. Your provider tier allows 16 concurrent requests and 300,000 tokens per minute; a draft uses about 900 tokens. The customer is promised a response within 8 s. Finance allows 2 million tokens for the sale day. Agents can absorb at most 15% of tickets.

**Your tasks:**

1. Check the concurrency and tokens-per-minute limits against peak load.
2. Choose the attempt timeout, number of attempts, retry rules and budget mechanism.
3. Decide what happens when (a) the provider slows to 6 s, and (b) the day's budget runs out at 3 p.m.
4. Name the three numbers you would put on the dashboard.

<details>
<summary>Show one reasonable solution</summary>

1. **Concurrency:** 6/s × 2 s = 12 in flight, within 16, so set our limit to about 14, leaving headroom. **Tokens:** 6/s × 60 × 900 = 324,000 tokens a minute, **over** the 300,000 limit. Either shorten outputs (about 830 tokens a draft fits) or request a higher tier. Otherwise expect 429s at peak whatever the concurrency.
2. Attempt timeout about 4.5 s (just above p99); deadline 8 s propagated; at most 2 attempts, retrying only on 429 or 5xx with jittered backoff, Retry-After as a minimum, and a 10% retry budget; SDK retries off. Reserve 1,000 tokens per call and settle to actual.
3. (a) At 6 s latency, 6/s needs 36 in flight, so most requests would wait past 8 s. Shed early with fallbacks, and let the breaker open on repeated full timeouts. The fallback share will exceed 15% of agent capacity, so warn support, and consider pausing drafts for low-value ticket types. (b) Budget exhausted means "budget" fallbacks for the rest of the day. 2 million tokens at 900 per draft is about 2,200 drafts, far below a peak-day volume. That is a planning conversation with Finance *before* the sale, not a 3 p.m. surprise.
4. Ready share and fallback share by reason; response-time p95 against 8 s; tokens used against the day's budget (with 429 rate as a close fourth).

</details>

## 14. Revision and transition

| Question | Short answer |
|---|---|
| Which errors deserve a retry? | Transient ones: timeouts, connection errors, 429 with Retry-After, 5xx. Not 4xx or spend caps. |
| Where should retries happen? | At one layer, with jittered backoff, a deadline and a retry budget. |
| What is deadline propagation? | One end-to-end deadline whose remaining time bounds every queue wait, attempt and backoff. |
| How do you size concurrency? | Little's law against the provider's limits; shed overflow early. |
| When is the budget enforced? | Before each call, by reserving an estimate, then settling to actual usage. |
| What counts as success? | Ready only; abstained, fallback and cancelled are reported separately. |

**Glossary:** *transient error, retry amplification, exponential backoff, jitter, Retry-After, retry budget, deadline propagation, cancellation, concurrency limit, Little's law, load shedding, token budget, reservation, circuit breaker, half-open probe, fallback, abstention.* Each is defined in sections 3–10 above.

**Reflect:** in a service you run today, add up the worst-case wait a user can experience across every timeout and retry in the call path. Is it the number you promised?

**You can now:** decide which errors to retry, propagate one deadline through every wait, size a queue with Little's law, and report fallbacks separately from success. **Show it:** your answer to the section 13 design challenge.

**Next:** run every scenario in this chapter and change the mechanisms yourself in [W-LLM-REL-01 — Reliable drafting under failure](../../../workbooks/llm/reliable-drafting/README.md). Return to the [course map](../../../README.md#ordered-capability-map).

**Sources:** Google SRE Book, ["Addressing Cascading Failures"](https://sre.google/sre-book/addressing-cascading-failures/) (deadline propagation, retry amplification and budgets, load shedding, small queues); M. Brooker, ["Exponential Backoff And Jitter"](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), AWS Architecture Blog, 2015; [OpenAI: Rate limits](https://developers.openai.com/api/docs/guides/rate-limits) (Retry-After as a minimum, jitter, failed requests count); [Anthropic: Rate limits](https://platform.claude.com/docs/en/api/rate-limits) (RPM/ITPM/OTPM, token bucket, 429 with `retry-after`, spend-cap 429 without it); M. Fowler, ["CircuitBreaker"](https://martinfowler.com/bliki/CircuitBreaker.html). Simulator figures are from W-LLM-REL-01's deterministic scenarios. Records are in the [source ledger](../../../docs/source-ledger.md).

**Later measured checkpoint:** [serving under load](../../../workbooks/delivery/serving-under-load.md) in phase 4 exercises actual loopback HTTP admission, bounded queueing, cancellation and recovery. Keep its measurements separate from the companion simulator's virtual timings; no additional phase-3 lab is required here.
