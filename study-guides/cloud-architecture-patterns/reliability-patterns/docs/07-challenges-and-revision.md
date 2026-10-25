# 07 — Challenges, revision and glossary

A pattern name is easy to recall. The harder task is explaining why your design will not lose an accepted order or turn a temporary outage into duplicate charges.

> **Unit:** SG-CREL-07 · **Capability:** AI-RELIABLE-01 (Reference).<br>
> **Outcome:** Defend a design under overload, ambiguity and a changed requirement.<br>
> **Prerequisites:** [Foundations through recovery](../README.md).<br>
> **Effort:** 15–25 minutes revision; 90–120 minutes independent practice, estimated.<br>
> **Artifact:** Failure-policy sheet, timeline, architecture sketch, runbook and changed-requirement answer.<br>
> **Central question:** Can you preserve the business invariants when the original assumptions change?

## 1. Select by failure, not by popularity

| If you observe… | Consider first… | Do not confuse it with… |
|---|---|---|
| Demand exceeds a safe rate | Admission and pacing | Autoscaling an unlimited bill |
| Calls stay active too long | Deadline, cancellation and concurrency cap | A rate limit alone |
| A safe operation fails briefly | Bounded retry with jitter | Retrying every error |
| Repeated calls likely fail | Circuit breaker | Repairing the dependency |
| One workload exhausts shared resources | Bulkhead isolation | A separate queue with shared unbounded workers |
| Optional functionality fails | Explicit safe fallback | Pretending the original task succeeded |
| One event repeatedly fails | Quarantine/DLQ and diagnosis | Automatic repair or guaranteed retention |
| Business state commits but publication can fail | Transactional outbox | Exactly-once end-to-end execution |
| External effect is uncertain | Reconciliation and stable identity | A new operation key |

## 2. Challenge A — Protect the sale (35–45 minutes)

The following are hypothetical design inputs. QuickCart receives 180 logical requests/second. Each admitted request needs one provider call; sustainable provider capacity is 120 attempts/second. The product owner reserves 20 attempts/second of headroom. Up to 10 retry attempts/second may be used. The customer deadline is 1,800 ms. Optional recommendations can be omitted; payment confirmation cannot.

**Your tasks:** Calculate the maximum original admission rate under these assumptions. Allocate a deadline across initial work, attempts, waiting and response. Draw required versus optional resource pools. Explain what rejected callers see. Define one behavior test for overload and one for a lost payment response.

<details>
<summary>Hint — identify which traffic consumes capacity</summary>

Both original calls and retries consume provider attempts. Reserve both headroom and retry capacity before setting admission. Do not count fallback as completed payment.

</details>

<details>
<summary>One reasonable worked answer</summary>

120 - 20 - 10 = **90 original calls/second**. At the offered 180 requests/second, at least 90/second need refusal or a separately bounded durable deferral policy. This assumes no other provider traffic and one attempt per original before retries; fan-out changes the calculation.

One budget is 150 ms initial work + two 550 ms attempts + up to 200 ms backoff + 150 ms response = 1,600 ms, leaving 200 ms margin. A second attempt is permitted only when safe and when both individual and shared retry budgets allow it. Capacity and deadline limits apply together.

Reserve checkout capacity separately from recommendations. Refused work receives an explicit unavailable/rate-limited outcome matching the cause; durably deferred work receives a job identity and pending state. Test useful completion, admission counts, active-call ceiling and deadline enforcement. For the lost-response test, commit the simulated effect then lose the response; a repeated intent must not create another effect. A mock result establishes control behavior, not provider guarantees.

</details>

## 3. Challenge B — Recover without shipping twice (35–45 minutes)

A shipping worker created labels before crashing. Two thousand messages are quarantined after a deployment. Some orders were cancelled; some messages are malformed; others reference labels that already exist. The live pipeline consumes 45 jobs/second of a sustainable 60 jobs/second. Keep 5 jobs/second headroom.

**Your tasks:** Partition cases by the evidence required to resolve them. Calculate the nominal replay ceiling and minimum drain time. Define permissions, event identity, retention, ordering checks and stop conditions. Write a concise update for a fictional support lead explaining what is confirmed and what remains unknown.

<details>
<summary>Hint — draining a queue is not the objective</summary>

Begin with possible completed effects and cancellations. “All messages redriven” is weaker evidence than “all accepted obligations reconciled.”

</details>

<details>
<summary>One reasonable worked answer</summary>

Allow at most 60 - 45 - 5 = **10 replay jobs/second**. Processing 2,000 eligible equal-cost jobs would take at least 200 seconds at that rate. Investigation, ineligible messages and retries increase elapsed time.

Reconcile existing labels without recreating them. Route cancelled orders through current-state checks; a cancellation after shipment may require a separate authorized process. Repair malformed data only from verified evidence, preserving the original record. Fix the consumer and test old schemas before redrive. Recheck entity versions so earlier events cannot overwrite later states.

Limit redrive to an authorized operator and a small sample. Stop on duplicate effects, invalid state transitions, rising live latency or budget exhaustion. Record every case's terminal state or named pending owner. Tell support which labels are confirmed, which cancellations are resolved and which cases remain under investigation; do not infer customer acceptance from this simulated exercise.

</details>

## 4. Transfer task — The fallback is a model (20–30 minutes)

QuickCart's support assistant must draft a response within three seconds. The primary model is unavailable. A second provider is responsive but has different privacy approval, answer quality and token pricing. Human review can handle only ten cases/minute; forty cases/minute need help.

Decide whether to use the second provider, an approved template, bounded review or an explicit refusal. State what evidence would change your decision. Include data access, current approvals, evaluation, deadline, cost and review backlog. Keep this task independent: attempt it before revealing the criteria.

<details>
<summary>Review criteria</summary>

Do not send data to an unapproved provider just to improve uptime. A fast answer needs quality and privacy evidence. A template must be appropriate to the task and labelled as reduced service where relevant. At forty incoming and ten reviewed cases/minute, the review backlog grows by thirty cases/minute unless admission or routing changes. Set a queue/age bound and truthful waiting expectations. State which controls were only designed and which would need implementation, real-model evaluation and organizational approval.

</details>

## 5. Self-check, not certification

For each dimension, assign **0** if missing, **1** if plausible but with unstated assumptions, and **2** if justified with a trace, calculation or concrete verification plan:

- Failure diagnosis and customer-visible contract.
- Capacity, time and retry calculations with units.
- Effect safety, authorization and durable state.
- Recovery ownership, replay and useful-outcome evidence.
- Alternatives, costs and changed-requirement reasoning.

Use the ten-point total to locate weaknesses, not to certify readiness. **Critical repair gates:** any duplicate consequential effect, authorization bypass, unbounded execution, silent loss of accepted work or invented evidence requires repair regardless of total. A paper design does not prove implementation. A public worked answer does not prove independent competence.

## 6. Quick revision and mixed quiz

Keep these distinctions close: rate versus concurrency; timeout versus remote cancellation; retry versus reconciliation; breaker versus bulkhead; DLQ versus repair; restoration versus resolved obligations.

1. **Calculation:** Three layers each permit two total attempts. Maximum leaf calls?
2. **Diagnosis:** DLQ depth falls, but unresolved orders do not. What could explain it?
3. **Decision:** A permission check fails. Should you try a more privileged fallback?
4. **Prediction:** Breaker cooldown ends on 100 replicas simultaneously. What risk remains?
5. **Transfer:** Backup recovery loses the deduplication ledger but preserves the queue. Is replay safe?

<details>
<summary>Answers with explanations</summary>

1. Up to eight under nested retry behavior: 2 × 2 × 2. One shared budget can lower that bound.
2. Expiration, removal without completion, redrive into another backlog or wrong acknowledgement can reduce depth. Reconcile business IDs rather than treating queue depth as success.
3. No. Availability does not override authorization.
4. A synchronized recovery surge. Jitter cooldowns and bound representative probes and subsequent traffic.
5. Not automatically. Reconstruct or reconcile effect identities and fence unsafe writes; the queue does not prove the effects have not already occurred.

</details>

## 7. Glossary

| Term | Plain meaning and QuickCart consequence |
|---|---|
| Backoff / jitter | Increasing waits / randomized waits; reduce synchronized retry traffic |
| Backpressure | Downstream pressure changes upstream admission or pace; prevents unlimited import backlog |
| Bulkhead | Resource partition; slow recommendations cannot take checkout's reserved slots |
| Circuit breaker | Health-based call gate; stops repeated image calls during an outage |
| Compensation | New action addressing a completed effect; refund is not erasing the original charge |
| Deadline | End-to-end time bound; includes queueing and all attempts |
| DLQ / quarantine | Holding destination for unresolved messages; still needs ownership and resolution |
| Idempotency | Repetition preserves one intended effect; same payment intent does not create two charges |
| Inbox / outbox | Durable processed-event record / transactionally recorded publish intent |
| Reconciliation | Compare trusted records to resolve unknown state; check whether a charge already exists |
| Redrive / replay | Reintroduce retained work for processing; current preconditions still apply |
| Retry budget | Bound on extra attempts; protects capacity across requests |
| RPO / RTO | Data-loss interval target / service restoration time target |
| SLI / SLO | Measured service indicator / target for it over a defined window |
| Visibility timeout | Temporary message hiding after delivery; not exactly-once effect protection |

**Reflection:** Which extra pattern did you choose not to add, and what measured change would justify it?

**You can now:** produce a defended reliability design with bounded work, explicit unknown states and a recovery owner. **Next course action:** return to [AI-RELIABLE-01 in the course map](../../../../README.md#ordered-capability-map) and continue the workbook assigned there. For optional implementation practice, [offline controls](../../../../workbooks/reliability/offline-controls/README.md) exercises selected mechanisms; it does not implement every pattern in this guide. [Measured serving practice](../../../../workbooks/delivery/serving-under-load.md) must be followed through its actual project instructions and evidence boundaries.

[Previous](06-recovery-and-case-study.md) · [Guide overview](../README.md) · [Sources](sources.md)
