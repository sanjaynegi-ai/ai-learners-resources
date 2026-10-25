# 00 — A release is a controlled change

QuickCart installs a new recommendation model but keeps the feature disabled. Has it deployed? Has it released? If the model is enabled for 5% of merchants, what should the team measure before increasing exposure?

> **Unit:** SG-DEP-00 · **Capability:** AI-DELIVER-01 (Reference).<br>
> **Outcome:** Separate deployment, release, experimentation and recovery; identify a release completely.<br>
> **Prerequisites:** HTTP services and transactions; [optional reliability refresher](../../reliability-patterns/docs/00-foundations.md).<br>
> **Effort:** 25–35 minutes.<br>
> **Artifact:** A release record and customer-visible acceptance contract.<br>
> **Central question:** What changes, who encounters it, and how will we know it works?

## 1. Intuition: a restaurant changes its menu

Installing a new oven is different from offering a new dish. Letting one table try the dish is different from measuring whether customers prefer it. Practising what happens when an oven stops is a fourth activity.

The analogy separates installation, exposure, comparison and resilience. Its limit is shared state: software versions may read the same records and compete for the same resources even when customers see different experiences.

**Predict:** A feature is disabled, but its new startup routine performs an expensive database migration. Is customer impact impossible?

<details>
<summary>Reveal the reasoning</summary>

No. The disabled feature may still affect startup, migrations, scheduled jobs, memory or shared dependencies. Feature exposure and deployment impact are different boundaries.

</details>

## 2. Vocabulary that prevents confused decisions

**Deployment** puts an identified artifact and configuration into an environment. **Release** makes behavior available to intended users. **Rollout** controls how that availability expands. A **canary** evaluates a change under limited exposure before wider rollout. An **A/B experiment** compares variants to estimate their effect on an outcome. **Chaos engineering** tests a resilience hypothesis through a controlled disturbance.

These can be combined. A team might deploy a binary using a rolling update, enable a feature with a flag for a canary cohort, and later run a product experiment. A fault-injection experiment is a separate decision, not an automatic deployment step.

**Continuous integration** builds and checks changes frequently. **Continuous delivery** keeps validated changes ready for release; **continuous deployment** automatically promotes qualifying changes into production under a policy. None means “skip evidence.” A maintenance-window replacement remains a reasonable alternative when a service can tolerate downtime and a more complex strategy adds little value.

## 3. Identify more than the source commit

QuickCart's release record should identify the application artifact digest, configuration, database/event schema, feature rules and dependencies. For an AI application, also record prompt, model/provider identifier, execution limits, retrieval/index version, evaluation dataset and scoring policy. A model alias can change behind a stable name; record what the provider exposes and what cannot be pinned or restored.

Promote the same verified artifact between environments where possible. Rebuilding from the same source with different dependencies can produce a different artifact. A digest identifies bytes; it does not itself prove approval, provenance or correctness. Restrict who can change the artifact, configuration and traffic policy, and audit those decisions without logging secrets.

## 4. Health has several meanings

A process may be alive but unable to serve. A **startup check** asks whether initialization has finished. **Readiness** asks whether this instance should receive work now. **Liveness** asks whether restarting a stuck process might help. A dependency outage does not necessarily justify restarting every caller; that can amplify failure.

A **smoke test** is a small check of an essential path after deployment. It does not replace workload testing, authorization checks or business-outcome evaluation. QuickCart's “get product” probe cannot prove payment idempotency. A model returning valid JSON cannot prove it retrieved the right merchant's policy.

## 5. Worked acceptance contract

Suppose a fictional ten-minute release window contains 20,000 eligible order submissions. Of these, 19,840 complete correctly within the promised time, 100 remain pending and 60 fail. Useful on-time completion is 19,840 / 20,000 = **99.2%**. Returning 200 for a fallback does not change that count unless the product contract explicitly accepts it as equivalent completion.

Define eligibility, time window, success and denominators before observing the candidate. Report admission rejections, fallback and pending work separately. For a draft-generation service, transport completion and answer-quality acceptance need separate measures because human labels may arrive later.

Record four decisions: **promote** when evidence meets the gate; **hold** when evidence is insufficient; **stop exposure** when the gate fails; **recover** the compatible system and reconcile affected work. “No errors visible” is not enough if telemetry is missing.

## 6. Practice and quiz

**Guided task:** Write a release record for QuickCart's recommendation change. Include one artifact identity, one data dependency, a success measure and a fallback. **Independent change:** the model provider cannot restore the previous model. Explain the safe recovery options instead of promising model rollback.

1. Is deploying a disabled feature always harmless?
2. Does the same source commit guarantee the same runtime behavior?

<details>
<summary>Show answers and explanations</summary>

1. No. Startup and shared-resource effects can occur before exposure.
2. No. Dependencies, configuration, data and provider behavior can differ. For the changed task, consider an already evaluated available alternative, an approved deterministic response, or abstention with bounded review. Preserve data permissions and report reduced functionality honestly.

</details>

**Reflect:** Which part of a release in your own service is currently unnamed or unversioned?

**You can now:** identify the change and distinguish process health from useful service. **Next:** [01 — Rolling deployment](01-rolling-deployment.md) asks whether a partially updated fleet can carry the workload.

[Previous: entry](../README.md) · [Guide overview](../README.md) · [Course map](../../../../README.md#ordered-capability-map)
