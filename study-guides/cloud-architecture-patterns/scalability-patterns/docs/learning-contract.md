# Learning contracts and transfer checks

> **Audience:** Experienced backend engineers extending distributed-systems judgment
> **Status:** Draft companion to chapters 00–13; not an executable project manual
> **Effort:** Use each chapter's reading estimate; add 10–15 minutes for its independent transfer check. Revision/glossary lookup is 20–30 minutes initially, then on demand. These are editorial estimates, not pilot measurements.

Read each chapter's worked explanation and diagrams, predict its failure, then attempt the independent row below before opening the chapter's worked answers. Backend/API/database experience is the entry prerequisite; later chapters use the named earlier conceptual units. No learner is required to read this whole series before building an AI application.

| Chapter / prerequisites | Central question and observable outcome | Learner artifact / acceptance criteria | Independent unfamiliar transfer check |
|---|---|---|---|
| 00 / backend request lifecycle | What is the measured constraint? Explain growth, latency, throughput and saturation without choosing a tool first. | One calculation with units/assumptions and a measurement plan; distinguish nominal capacity from useful throughput. | Demand doubles but p95 stays stable while error rate rises: explain why latency alone is insufficient. |
| 01 / 00 | Where must mutable cart state live? Explain interchangeability while preserving session/business correctness. | State-ownership sketch and failover prediction; do not put mutable payment state in a client token. | A revoked user's cached session remains readable: define the trusted recheck point and residual cache risk. |
| 02 / 00–01 | Which healthy backend should receive work? Explain routing versus state ownership. | Route/health diagram and failure policy; distinguish health detection from guaranteed successful requests. | A healthy API has no database permission: identify why network health alone cannot authorize or validate business work. |
| 03 / 00–02 | When does another replica help? Calculate demand/headroom and scaling delay. | Replica calculation, downstream cap and rollback signal; state assumptions. | Per-instance demand is 250/s, total demand 900/s, database cap 700/s: four replicas cannot achieve 900 useful writes/s; defend admission/fallback rather than another replica. |
| 04 / 00–03 | Does buffering stabilize or postpone failure? Explain backlog and durable acceptance. | Backlog calculation and oldest-age alert with owner; distinguish accepted from completed work. | 120 jobs/min arrive, 100/min complete for 15 min: backlog grows by 300, assuming zero initial backlog and stable rates. Who handles a growing delay when review capacity is only 10/min? |
| 05 / 04 | How many consumers are useful and safe? Explain concurrency, retries, ordering and idempotency. | Worker/provider bound, duplicate-effect reasoning and regression scenario. | Provider cap falls from 100/min to 40/min while workers can do 200/min: bound attempts and queue admission; name the incident owner and recovery signal. |
| 06 / 00, 05 | Which key preserves useful locality? Explain hotspots, ownership and migration. | Shard-key decision, tenant-access boundary and migration/rollback assumptions. | One tenant is 60% of traffic; hashing tenant ID alone cannot divide that tenant's hotspot. Propose a measured alternative and explain ACL propagation. |
| 07 / 06 | What does an incomplete merge mean? Explain deadlines, deduplication and completeness. | Fan-out/merge contract and explicit partial-result policy; separate product discovery from exact totals. | Three shards answer but a fourth times out: explain why an exact financial total must not be labelled successful. |
| 08 / 04–05 | Where does stage responsibility end? Explain immutable artifacts and publish conditions. | Stage/ownership contract, bottleneck calculation and stale-version rejection rule. | Old encoding finishes after a new upload: identify the trusted current-version check before publication and how to audit a rejected artifact. |
| 09 / 01–08 | Can combined patterns preserve invariants? Defend a phased QuickCart design. | ADR, failure timeline, useful business metrics, security/cost assumptions and incident owner. | Notifications succeed while order commit fails: defend transaction/outbox boundaries without claiming exactly-once external effects. |
| 10 / 01–09 | Which smallest change addresses the symptom? Compare alternatives and next constraints. | Decision matrix with an unsuitable alternative and measured trigger to revisit. | Scaling cuts latency but doubles retry charges and review work: include provider failures and human review in cost per useful operation. |
| 11 / 01–10 | Can you defend an unfamiliar constraint? Diagnose, calculate and explain a design. | Attempt the existing public rubric before solutions; preserve failure evidence and repair critical correctness gaps. | Stakeholder changes from approximate search to exact inventory: revise completeness/cost/SLO decisions, then write a short stakeholder update. |
| 12 / attempted 00–11 | Can you retrieve reasoning without rote pattern names? Explain distinctions and formula limits. | Completed recall/numerical checks plus weak-topic repair list; self-score is not certification. | Change a worked example's arrival rate and initial backlog; show how both affect your result. |
| 13 / on-demand reference | Can you use vocabulary precisely? Define a term with a case consequence and a limitation. | Three term/contrast explanations pointing to taught concepts; no new prerequisite is introduced. | Explain why “stateless,” “authorized” and “idempotent” describe different properties of the same request. |

## Worked security and operational reasoning

For chapter 01's revoked session, a cache is like a photocopied permission list: convenient but possibly stale. The analogy does not prove a TTL is safe. The application needs a declared authorization decision point, an accepted staleness policy, invalidation/recheck behavior and a test in which access is revoked between operations. The security owner defines policy; the service owner implements and monitors the check. A diagram cannot prove the control exists.

For chapter 04's queue example, 120 − 100 = 20 jobs/min accumulate; 20 × 15 = 300 jobs. At zero new arrivals, nominal drain time is 300 / 100 = 3 minutes; with arrivals continuing at 120/min, it never drains under these assumptions. Provider costs, retries and human review can impose separate limits. Record queue age and useful completion separately from ingestion success. This is a reasoning exercise, not executed benchmark data.

<details><summary>Reflection and self-check</summary>

For your row, explain the invariant, failure signal, trusted enforcement point, residual limit and owner. Reject any answer that calls denied, stale, partial or merely queued work successful without its declared contract. If you cannot explain what changes when an assumption fails, revisit the chapter before selecting infrastructure. Keep the failed attempt and a revised decision; do not score only presentation quality.

</details>

## Practice connections and boundaries

### Primary source checks

**Reference, AWS documentation, checked 2026-10-14:** [SQS at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html) supports duplicate-delivery/idempotency reasoning; [ALB health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html) explains routing and the all-unhealthy fail-open exception; [Auto Scaling policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html) distinguishes desired/current capacity and warmup; [Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html) supplies operational context. Focus on those named sections, 5–10 minutes each, after the corresponding chapter. Public reading is free; AWS execution needs account/access and can incur charges. These unversioned docs were read, not deployed or tested. Fictional arithmetic is derived from stated assumptions, not AWS benchmarks. If access fails, continue local reasoning and label provider guarantees unverified.

Executable construction belongs in workbooks. The [offline controls exercise](../../../../workbooks/reliability/offline-controls/README.md) tests trusted denial, current grants, deletion, idempotency and cancellation in a synthetic local system; it does not implement every architecture pattern. The [W-LC-16 — LangChain practice route](../../../../workbooks/langchain/01-learning-workbook/16-practice-challenges.md) connects retrieval/evaluation judgments to an independent application change.

Sources and platform-specific guarantees in individual chapters require their source records; these transfer cases use fictional assumptions, not production anecdotes. Analogy limits and contracts here supplement existing narrative, not replace it. [SG-SCALE-00 — Foundations](00-foundations.md) · [Root map](../../../../README.md)
