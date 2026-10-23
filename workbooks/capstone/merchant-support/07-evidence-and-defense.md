# W-CAP-01.7 — Evidence review and individual ownership

> **Checkpoint:** `cap-6-reviewed` · **Effort:** 3 h evidence review plus shared 4 h defense/repair reserve · **Question:** What can you prove, and what is still missing?

Use the [existing capstone criteria](../../../assessments/capstone-evidence.md), not a new certification score. Public reference code, a passing pipeline or this document does not establish graduation. Final evidence includes a reproducible repository, real-model evaluation, deployed artifact or verifiable deployment evidence, tests, threat model, decisions, cost sheet, runbook, incident exercise and individual defense. Keep confidential reviewer feedback elsewhere.

## Evidence inventory and critical gates

Create `submission.json` in your personal project. `artifacts` maps each name below to `{"path":"relative/file","sha256":"ACTUAL_SHA256"}`. Required names: discovery, requirements, acceptance, architecture, threat_model, decisions, cost, runbook, incident, handover, evaluation, tests, assistance. Use actual paths/hashes; several design sections may point to one reviewed file if its scope is clear. Generate hashes with `Get-FileHash -Algorithm SHA256`, lowercase them for JSON comparison, and retain failed/obsolete reports.

Add `gates` entries authorization, bounded_execution, secret_review, truthful_evidence, evaluation_failures_visible. Each has `status`, `evidence`, and `reviewer`. Only record pass after the named person actually inspects the cited results. Add `milestones` real_model_review, deployment, individual_defense, independent_transfer, with the same fields. Missing/unexecuted milestones stay `pending`, with an explanation; do not write a fictitious reviewer or deployment ID.

From the project directory:

```powershell
uv run --locked python -m merchant_support.readiness submission.json --root .
```

Exit 2 / `NO_RELEASE` means missing/changed artifacts or undeclared gate/milestone evidence. A fully populated inventory returns `REVIEW_REQUIRED`, **never automatically pass/graduated**. The checker validates required file containment/hash and declaration completeness, not truth, reviewer authority, semantic quality or live infrastructure. Humans must open the evidence and assess the seven dimensions. A string that says “pass” is not proof. Tests ensure synthetic reference evidence cannot silently satisfy missing live/ownership milestones and reject path escapes/stale hashes.

| Essential dimension | Reviewer must inspect |
|---|---|
| Implementation | Clean setup, actual tests, schema/setup/data and acceptance behavior, changes from starting checkpoint |
| Evaluation | Exact dataset/prompt/model/schema/config/label versions, fresh held-out semantics, slices/counts, failed/abstained outcomes; real versus synthetic separated |
| Security | Tenant/role/revocation/deletion, approval and amount boundaries, trusted identity/clock, secrets review; risk limits not hidden |
| Operations | Actual deployment scope/artifact/configuration, resource bounds, safe telemetry/retention, incident halt/recovery and cleanup |
| Architecture judgment | Alternatives, deliberate complexity, single-worker and local-effect boundaries, migration/rollback reasoning |
| Cost | Model/infrastructure/retry/storage/review units and measured versus hypothetical assumptions; unknown cost disclosed |
| Explanation/handover | Individual request walkthrough, fault diagnosis, small unseen modification, stakeholder update and disclosed assistance |

**Non-compensable:** authorization leakage, unbounded execution/action, secret exposure, fabricated evidence and hidden evaluation failures require repair regardless of other strengths. A justified no-release recommendation is valid reasoning within a module; missing final required artifacts remain missing. Nothing here changes earlier chapter scores or establishes credential policy.

## Author-reference delivery audit

The [dated review](../../../docs/c13-implementation-review.md) and [execution record](../../../docs/review-evidence/integrated-capstone.json) separate local deterministic tests, synthetic evaluation, local container deployment, live model and ownership. The reference has authored discovery/design/cost/runbook/handover examples. They are fictional learning assets, not independent stakeholder acceptance or learner submissions. Real-model review, independent changed implementation and individual defense remain pending. The final readiness outcome is therefore **NO_RELEASE**.

The [authorized live attempt](../../../docs/review-evidence/capstone-live-attempt.json) reached AWS but was denied by IAM after one attempted invocation. Seven cases remain unexecuted; a failed service request is not successful real-model evidence. The administrator-reviewed access fix and human semantic review are still prerequisites to advancing that milestone.

Defense prompts: Why validate a quote twice? What does deleting a queryable policy leave in restricted action audit? Why is one process required? What would change for a real external refund? Which denominator hides provider failures? How could old-state restoration reintroduce authority? Explain each with code/evidence and one residual risk. Then modify one selected behavior and rerun its affected positive/negative checks.

Self-study remediation: record failed gate, causal hypothesis, repair, regression output and help used. Reattempt the weak dimension with a different fault, not only the same reference run. A reviewer can verify ownership through explanation plus an unseen modification; self-marked boxes alone cannot.

Next: use the Draft [W-DEFEND-01 defense/revision route](../../defense/README.md) and [targeted reassessment procedure](../../../assessments/defense-and-remediation.md). Public practice is linked throughout the path; actual independent defense and pending live-model delivery gates remain separate. [Independent brief](06-independent-delivery.md) · [Route](README.md)
