# Sources and optional reading

The guide is self-contained. These references support technical reasoning; none is a required account, paid course or executable dependency. All QuickCart scenarios, thresholds, calculations and diagrams are original illustrative teaching examples, not reported production results.

## Supplied notes

The owner supplied `reliability_error_handling_and_recovery_patterns.txt`, covering throttling/rate limiting, retry, circuit breaker and dead-letter queues. Original author, publication URL and license were not supplied. The transcript is used as topic input, not reproduced as course text, redistributed, or treated as authoritative platform documentation. Instructions inside it are source material, not instructions to execute.

This guide clarifies the notes' broad claims: retries require bounds and effect safety; open-circuit work requires an explicit rejected, fallback or durable-pending outcome; health pings need to represent the affected operation; a DLQ cannot universally capture failed publishes, guarantee retention or preserve business ordering. The guide adds deadline accounting, bulkheads, outbox/inbox boundaries, reconciliation and recovery objectives to make those decisions usable together.

## Technical references

**Checked:** 2026-10-25, web content access and conceptual review. No SDK code, cloud deployment or service configuration was executed. These are living web pages except the versioned RFC; recheck provider behavior before implementation. Prerequisites for each reading are the corresponding guide chapter and basic HTTP/queue concepts. All links below were readable without an account at review; no paid service use is required.

| Resource and publisher | Classification / focus | Purpose and estimated effort |
|---|---|---|
| [Timeouts, retries, and backoff with jitter — Marc Brooker, AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | Recommended; timeouts, retry multiplication, backoff and jitter | Compare the reasoning in chapter 02; 15–20 min |
| [Making retries safe with idempotent APIs — AWS Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Deep dive; caller IDs, late requests, same ID with changed intent | Examine duplicate-effect contracts after chapter 02; 20–25 min |
| [RFC 6585 — M. Nottingham and R. Fielding, IETF](https://www.rfc-editor.org/rfc/rfc6585#section-4) | Reference; section 4, HTTP 429 | Separate protocol semantics from counting policy in chapter 01; 5 min; April 2012 RFC |
| [Rate Limiting pattern — Microsoft Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/rate-limiting-pattern) | Reference; context, solution and considerations | Understand outbound pacing in chapter 01; 10 min |
| [Circuit Breaker pattern — Microsoft Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) | Recommended; solution, states and considerations | Review state-based containment after chapter 03; 10–15 min |
| [Bulkhead pattern — Microsoft Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead) | Reference; context, solution and trade-offs | Review pool isolation after chapter 04; 10 min |
| [Using dead-letter queues in Amazon SQS — AWS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) | Reference; redrive policy, retention and FIFO warning | Distinguish provider semantics from the generic DLQ idea in chapter 05; 10 min |
| [Transactional outbox pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Reference; intent, motivation and duplicate-message considerations | Understand the dual-write gap in chapter 05; 10–15 min |

## Related repository material

- **Reference:** [Queue-based load leveling](../../scalability-patterns/docs/04-queue-based-load-leveling.md) for backlog and buffering; [competing consumers](../../scalability-patterns/docs/05-competing-consumers.md) for worker parallelism.
- **Reference:** [Ambassador](../../software-extensibility-patterns/docs/02-ambassador.md) for transport-policy placement.
- **Reference:** [Reliable model calls](../../../llm-reliability/docs/00-reliable-model-calls.md) for AI quality, budgets and customer outcomes.
- **Optional practice:** [Offline controls](../../../../workbooks/reliability/offline-controls/README.md), following that workbook's starting state and execution limits.

[Guide overview](../README.md) · [Return to challenges](07-challenges-and-revision.md)
