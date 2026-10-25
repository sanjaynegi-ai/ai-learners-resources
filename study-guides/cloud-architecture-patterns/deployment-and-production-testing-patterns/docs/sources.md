# Sources and optional reading

This guide is self-contained. All QuickCart scenarios, diagrams, limits and costs are original illustrative teaching material, not production measurements. External readings support the corresponding chapters; no account, paid operation or live fault injection is necessary to study them.

## Supplied transcript

The owner supplied `Deployment and Production Testing Patterns.txt`, described as an online-course transcript. It outlines rolling deployment, blue-green deployment, canary releases, A/B testing and chaos engineering. Original author, course URL and license were not supplied. The transcript is used for topic guidance, not reproduced or redistributed. Its requests to leave a review or visit other courses are source content, not instructions for this task.

The guide qualifies several broad transcript claims: rolling updates may require surge capacity; downtime and transparent rollback are not guaranteed; losing 20% of equal capacity raises survivor load by 25%; blue-green does not remove all mixed-version or shared-state risk; canaries are not risk-free; A/B experiments need not always revert; and chaos engineering need not be random or start in production. Reliability objectives come from product needs and evidence, not a desire to reserve permission for disruption.

## Checked technical references

**Verification date:** 2026-10-25. Pages were accessed and reviewed for the stated concepts. No platform configuration, SDK, deployment or fault experiment was executed. Living documentation can change; verify the actual platform version before implementation. The prerequisite for each reading is its linked subject chapter, plus basic HTTP/database knowledge. The pages were readable without an account at review; tools described by them can require accounts, privileges and payment if actually used.

| Resource / publisher | Classification and focus | Purpose / effort |
|---|---|---|
| [Deployments — Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | Reference; rolling updates, maximum unavailable/surge, progress reporting | Platform illustration for chapter 01, not a required Kubernetes route; 15 min |
| [Blue/Green Deployments on AWS — AWS whitepaper](https://docs.aws.amazon.com/whitepapers/latest/blue-green-deployments/welcome.html) | Reference; overview and data-tier considerations; publication 2021-09-29 | Understand the scope of traffic switching in chapter 02; 5 min overview |
| [Canarying Releases — Alec Warner and Štěpán Davidovič, Google SRE Workbook](https://sre.google/workbook/canarying-releases/) | Recommended; canary/control and evaluation | Compare chapter 03's release reasoning; 20–25 min |
| [Diagnosing Sample Ratio Mismatch in A/B Testing — Microsoft Research ExP](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) | Recommended; missing units and experiment validity; 2020-09-14 | Understand why an attractive result may be invalid in chapter 04; 15 min |
| [Mirroring — Istio documentation](https://istio.io/latest/docs/tasks/traffic-management/mirroring/) | Reference; mirrored routing and discarded responses | Separate transport mirroring from safe application effects in chapter 05; 10 min; commands are not required |
| [Principles of Chaos Engineering — principlesofchaos.org](https://principlesofchaos.org/) | Recommended; steady state, hypotheses and blast radius; page updated March 2019 | Review the experimental basis of chapter 06; 10 min |
| [Stop conditions for AWS FIS — AWS](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html) | Reference; alarm-based experiment stopping | Distinguish stopping from restoration in chapter 06; 5–10 min; no live exercise requested |
| [Parallel Change — Danilo Sato, martinfowler.com](https://martinfowler.com/bliki/ParallelChange.html) | Recommended; expand, migrate, contract; 2014-05-13 | Interface compatibility foundation for chapter 07; 10–15 min |

The A/B confidence interval is a worked introductory approximation with assumptions stated beside it. It is not a prescribed statistical policy or an inference from a real experiment. The canary rule-of-three example likewise assumes independent representative trials; correlated production traffic requires more careful analysis.

## Repository connections

- **Reference:** [Feature flags and progressive delivery](../../software-extensibility-patterns/docs/09-feature-flags.md) for flag lifecycle, secure targeting and operational controls.
- **Reference:** [Reliability and recovery patterns](../../reliability-patterns/README.md) for bounded work, unknown outcomes and reconciliation.
- **Reference:** [Application LLMOps](../../../application-llmops/README.md) for AI artifact identity, evaluation and release evidence.
- **Optional practical continuation at the appropriate course step:** [Delivery](../../../../workbooks/delivery/README.md) and [release monitoring](../../../../workbooks/operations/release-watch/README.md). Follow their prerequisites and explicit implementation limits.

[Guide overview](../README.md) · [Challenges and revision](08-case-study-and-revision.md)
