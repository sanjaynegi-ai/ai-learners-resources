# 00 — Reliability begins with a promise

QuickCart's checkout returns quickly during an outage. Unfortunately, some responses say “paid” when payment is still unknown. Is that a reliable service?

> **Unit:** SG-CREL-00 · **Capability:** AI-RELIABLE-01 (Reference).<br>
> **Outcome:** Classify failures and define a customer-visible success measure.<br>
> **Prerequisites:** HTTP, transactions and background jobs; [optional refresher](../../scalability-patterns/docs/00-foundations.md).<br>
> **Effort:** 25–35 minutes reading and practice.<br>
> **Artifact:** A failure-policy sheet with explicit success, pending and failure outcomes.<br>
> **Central question:** What must remain true when part of the system fails?

## 1. Intuition: a parcel desk

A parcel desk can accept a package, store it safely, and give you a tracking number even when a delivery van breaks down. That is useful service. Saying “delivered” because the clerk printed a receipt is not.

The analogy separates **acceptance**, **execution** and **completion**. Its limit is that distributed systems can lose responses and deliver the same message more than once. A tracking number needs durable records and duplicate handling behind it.

**Pause and predict:** A payment call times out after one second. Which statement is justified: “payment failed,” “payment succeeded,” or “the caller does not yet know”?

<details>
<summary>Reveal the reasoning</summary>

The caller does not yet know. The request may never have arrived, may still be running, or may have completed before its response was lost. “Unknown” needs a reconciliation path, not a guessed success or a new charge with a new identity.

</details>

## 2. Reliability, resilience and recoverability

**Reliability** means delivering the promised correct behavior under stated conditions over time. **Availability** measures whether service is usable under a declared definition. **Resilience** is the ability to contain a disturbance and continue useful work. **Recoverability** is the ability to restore correct operation and resolve affected data or work after failure.

These overlap, but a healthy process does not prove that yesterday's accepted orders were shipped. A restart can restore availability while leaving recoverability unfinished.

For this guide, QuickCart uses three invariants:

- One logical payment intent must not create two charges.
- Accepted durable work must reach a recorded terminal outcome or a visible pending state with an owner.
- A fallback must preserve authorization and must not invent a business result.

These are fictional design requirements. The guide reasons about them; it does not claim that an implementation already enforces them.

## 3. Classify before choosing a pattern

“User error versus server error” is a useful first clue but an insufficient retry policy. Ask whether repeating the unchanged operation can help, whether it is safe, and whether resources and time remain.

| Observation | What it might mean | Useful response |
|---|---|---|
| Invalid amount or missing field | Request cannot satisfy the contract | Reject with a safe explanation; correct the input |
| Permission denied | Caller is not allowed | Stop; never switch to a more privileged identity |
| Brief connection fault on a read | Temporary transport failure | Consider a bounded retry |
| Sustained overload | Demand exceeds current capacity | Reject, pace or durably defer suitable work |
| Timeout after a payment submission | Outcome ambiguous | Reconcile using the original operation identity |
| Repeated parser failure on one event | Poison message: unchanged processing keeps failing | Quarantine and diagnose |
| Successful model call with an unsupported answer | Semantic failure | Validate, abstain or review; transport success is insufficient |

An HTTP code alone does not reveal whether a side effect occurred. A 503 might be transient or a long outage. A 429 can justify waiting if the budget permits. A successful response can still violate business rules.

Return a stable error category, a safe explanation and a correlation identifier. Keep credentials, raw provider payloads and sensitive stack traces out of customer responses. Internal diagnostics need access and retention controls too.

## 4. Worked example: count useful outcomes

Assume an illustrative ten-minute window with 10,000 eligible checkout attempts: 9,750 confirmed correct completions within the promised time, 150 still pending at that deadline, and 100 rejected due to overload.

For a measure defined as **correct completions within the deadline / eligible attempts**, the result is:

```text
9,750 / 10,000 = 97.5%
Pending = 1.5%; rejected due to overload = 1.0%
```

Do not remove overload rejections from the denominator to improve the number. Define eligibility before measuring; report invalid requests separately. If an asynchronous product promises only durable acceptance within that window, define a separate acceptance measure and a later completion measure. A 202 response is not completion.

A **service-level indicator (SLI)** is the measured quantity. A **service-level objective (SLO)** is its target over a specified window. An **SLA** is an agreement and may include commercial consequences; this guide establishes none. If the hypothetical objective is 99% over these 10,000 attempts, the allowance is 100 unsuccessful attempts. The observed 250 exceed it by 150. That arithmetic does not predict the next window.

## 5. Practice: build the first policy sheet

Write a row for a product image read, a payment submission and a shipping event. Record the invariant, success definition, possible unknown state, retry eligibility, terminal outcome and owner. Start with the payment row: a timeout leaves it pending reconciliation; a new payment identity is not a repair.

**Independent change:** The customer cancels while the payment is pending. Explain why stopping local waiting is different from reversing a charge. Your answer should retain the pending record and name the evidence needed before refunding or confirming cancellation.

## 6. Knowledge checks

1. A dashboard shows 100% HTTP 200 responses because every dependency error becomes an empty response. What should you inspect?
2. Does restoring a backup prove that accepted orders are complete?

<details>
<summary>Show answers and explanations</summary>

1. Inspect customer outcomes, fallback counts, missing required fields and semantic correctness. The transport measure hides failures. An empty recommendation list may be permitted; an empty payment confirmation is not.
2. No. Check the backup's data-loss interval, events after the restore point, external effects and reconciliation. A database can be internally consistent and still disagree with the payment provider.

</details>

**Reflect:** Which metric in a service you know could look healthy while customers still lose work?

**You can now:** classify all three policy-sheet operations and distinguish unknown, pending and successful outcomes. **Next:** decide which requests may enter in [01 — Throttling and rate limiting](01-throttling-and-rate-limiting.md).

[Previous: guide entry](../README.md) · [Guide overview](../README.md) · [Course map](../../../../README.md#ordered-capability-map)
