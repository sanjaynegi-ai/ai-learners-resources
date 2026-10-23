# W-CAP-01.5 — Operate, diagnose and hand over

**Can an operator tell what is safe to run after a failure?**

> **Your goal:** Contain a regression, preserve evidence and hand over a bounded recovery decision.<br>
> **You need:** [Delivery checkpoint](04-delivery.md), current state/configuration and your evaluation records.<br>
> **Effort:** 4 hours for `cap-5-operated`, estimated.<br>
> **You will produce:** An executed local incident, runbook amendment, cost worksheet and operator handover. **Status:** Draft; synthetic reference and independently reviewed delivery are separate.

## Runbook: provider or policy regression

**Starting state:** retain your capstone artifact/configuration, state and report identities. Run the incident CLI from this project's Python 3.11/uv environment, using synthetic isolated incident state. It makes no paid provider call and starts no server. If you already started the application, stop that writer before privileged admin mutations as instructed below.

**Application-oncall** owns detection/containment and the review queue. **Release operator** owns compatible artifact/configuration restoration. **Data owner** decides policy deletion/retention. **Independent reviewer** owns the recovery recommendation. One learner may simulate roles; record that instead of claiming independent review.

1. Detect failed outcomes, coverage loss, stale evidence or unsafe behavior in reports/events. `/health` says only process_alive. In this reference, any failed labelled control or forbidden retrieval halts delivery; do not average a security failure into a quality score.
2. Halt admission and effects. Stop the local server before privileged admin mutations to avoid concurrent multi-process state changes. From the project directory use `uv run --locked python -m merchant_support.admin --state state halt`. Restart to observe the persistent halt; current answers may still abstain without model work, but no model admission or effect proceeds.
3. Preserve versioned report, call reservations, source/config hashes and synthetic action state. Logs contain only allowlisted event fields; there is no general request-body trace. Restricted action/citation state contains synthetic business evidence and must not be exported indiscriminately.
4. Compare deployment/config/provider/data changes. Use a known authorized query and inspect current policy revision, permissions and review status. A missing source is not a provider outage; an old model cannot restore deleted evidence. Halt/review when cause remains unknown.
5. Restore a compatible provider/artifact/configuration; keep current permissions/deletions intact. Use fresh bounded probes in an isolated copy or test state. No automatic resume; the CLI deliberately leaves active halt set.
6. Reviewer checks controls, semantic output, queue/cost impact and unresolved effects. Write a runbook amendment with owner/regression test, actual chronology and next decision. Production resume needs a separately reviewed authorized process; deleting state is not resume.

Run the reproducible local drill from this project directory:

```powershell
uv run --locked python -m merchant_support.incident --out runs/incident-01
```

It changes the provider boundary to a scripted outage, observes failed work, persists halt, restores the offline provider, confirms active admissions remain blocked and probes recovery in separate state. Expected ordered states: ready → failed → budget_or_halt; isolated recovery ready. `incident.json` and `runbook-update.md` are real local execution artifacts describing a synthetic incident, with ordered steps rather than invented wall-clock recovery times. State directories remain for inspection; protect them and close stores before cleanup.

**Pause and decide:** may the on-call reset call reservations after timeout to get a green probe?

<details>
<summary>Compare the recovery decision</summary>

No: remote execution may have happened. Preserve admission history and investigate; a fresh bounded probe needs a distinct approved budget. The local incident uses separate synthetic probe state explicitly, not a reset of the active ledger.

</details>

## Cost and capacity worksheet

Create `delivery/cost.md` from this worked example, labelling every number **hypothetical** until actually measured/priced. Suppose 1000 requests/day, 60% needing generation, 700 input and 120 output tokens per generation, input $1/million and output $4/million. Token charges/day = 600 × (700×$1 +120×$4)/1,000,000 = **$0.708**. A second attempt for 10% of those calls adds about $0.0708 under equal-token assumptions. The reference makes one attempt; this calculation compares a possible change, not observed behavior.

If only 500 requests/day become good ready drafts, model cost/good draft = $0.708/500 = $0.001416, while cost/all requests = $0.000708. This excludes infrastructure, storage, telemetry, backups, failure review and human approval. At 400 reviews/day ×2 min/review × hypothetical $30/hour, review effort costs **$400/day**. Human work can dominate model tokens. Do not quote these prices as current Bedrock rates. For actual evaluation, preserve token usage, use an official model/region price record and disclose unknown usage/ambiguous charges instead of zero-filling.

The local container has resource limits; the Docker VM, disk/cache, host and developer effort are outside those limits. A future AWS path adds compute, persistent disk, monitoring, network and backup costs. The separate SAM worker's call ledger does not bound this application's total charges. If review arrival exceeds service capacity, stop widening coverage and surface the scope/staffing decision.

## Retention, access and deletion

Seven-day telemetry retention is a teaching assumption, not a legal recommendation. Stop the server and run `uv run --locked python -m merchant_support.admin --state state expire`; inspect the expired count. Reviewers/operators need controlled storage read access; the local CLI assumes filesystem authority and implements no production IAM. Events omit token/user/query/answer/exception text. Restricted SQLite business state is different: it retains approval/action evidence for this exercise, with no claim of secure deletion or an approved real-data retention period.

Stop the server before `admin --state state delete --target refunds-policy.md` or `revoke --target supervisor`; restart and demonstrate policy queries/pending effects fail closed. Queryable chunks disappear and tombstone state survives restart. The original action's restricted audit citation can remain under this declared synthetic contract; neither that row nor an offline backup is a queryable retrieval cache. If a real deletion policy forbids retaining it, redesign with data-owner approval rather than pretending the existing delete call erases it. Do not restore obsolete ACLs from an old release snapshot.

## Worked handover and stakeholder change

[Delivery examples](delivery-examples.md) contain discovery, requirements, acceptance negotiation, changed-requirement update and operator handover. Adapt them to actual evidence rather than copying unsupported claims. Attach your source checkpoint/dirty state, lock/image/config hashes, model/report versions, tests, threat decisions, deployment outputs, failure/recovery/cleanup record, assistance disclosure and known limitations. Draft a message; do not send anything externally for this exercise.

Attach current [versioned UAT results](customer-acceptance.md), simulated/pending customer acceptance, and the reused [workflow-impact plan](../../delivery/customer-rehearsal.md#4-plan-adoption-and-workflow-impact) to handover. Replace the generic stakeholder reflection within the existing allocation. A fresh self-walkthrough, local control pass or hypothetical adoption calculation cannot supply real user acceptance or useful-outcome measurements.

**Troubleshooting**

| Symptom | Likely cause → diagnostic action → repair |
|---|---|
| Python/import fails | Missing sibling dependency or wrong working directory → inspect path/lock → preserve relative layout and sync from project root |
| Requests denied after restart | Current member revoked or policy deleted → inspect privileged state; do not reset DB → obtain appropriate data/security decision |
| `budget_or_halt` | Durable reservation limit/halt → admin status while stopped → reconcile, preserve evidence; do not delete ledger to retry |
| SQLite thread error | Engine created outside API event loop or sync endpoint moved to thread → inspect startup/endpoint model → create in lifespan, keep one event-loop worker |
| Container unhealthy | State mount ownership/import/config → inspect bounded logs and resolved config → restore known artifact; do not run root or broaden host exposure to hide failure |
| Bedrock rejected | Region/model/terms/IAM mismatch → use approved preflight and official errors → keep no-release; never widen IAM to wildcard |
| Evidence output exists | Prior run retained → inspect it → choose a new name; never silently overwrite |

Cleanup: follow [container teardown](04-delivery.md#cleanup). For local generated `runs/incident-01`, resolve it and confirm its parent is your project `runs` directory before recursive removal. No daemon is started by the test/evaluation/incident CLI. Stop the local uvicorn terminal with Ctrl+C. Preserve learner work, and never treat ignored files as confidential storage.

Acceptance: independently explain detection versus cause, preserve actual failed evidence, keep halt after recovery, update the runbook and show exact safe cleanup. Next: [independent changed brief](06-independent-delivery.md), then [evidence/defense](07-evidence-and-defense.md). [Route](README.md)

**Governance handover:** link and update the same private [operations evidence record](../../operations/release-watch/application-governance.md) within the existing handover allocation. Identify actual versus fictional owners/approvals, separate event expiry from retained action/audit/report/backups, and keep provider approval/incident-resume gaps visible. Do not infer organization-wide governance or compliance from the local controls.
