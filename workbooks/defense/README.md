# W-DEFEND-01 — Explain, modify, repair and defend your system

> **Capability:** AI-DEFEND-01 · **Audience:** Experienced backend engineers on the Developer path<br>
> **Status:** Draft public practice/assessment route, unpiloted; no certification policy<br>
> **Central question:** Can you show ownership when a requirement or failure changes, rather than repeat the reference solution?<br>
> **Prerequisites:** Use the stage-local resources below throughout study; final defense follows your [independent capstone](../capstone/merchant-support/06-independent-delivery.md) and its [evidence inventory](../capstone/merchant-support/07-evidence-and-defense.md)<br>
> **Outcomes:** Explain mechanisms and evidence limits, implement a small change, diagnose a fault, justify design/cost/security decisions, and communicate a safe handover<br>
> **Artifact:** Stage practice log, final individual explanation/modification record, seven-dimension review and targeted repair/reassessment record<br>
> **Acceptance:** Observable evidence in every essential dimension and no unresolved critical gate; self-review is distinct from independently verified competency<br>
> **Effort:** Stage prompts replace existing module reflection/independent-practice time. Final phase-6 route: revision 2 h, integrated rehearsal 3 h, defense/feedback 2 h, initial repair 2 h and reassessment 2 h = 11 h, including the already-budgeted C13 4 h shared reserve; unpiloted estimates<br>
> **Environment:** Your selected module's declared runtime/lockfile and synthetic fixtures; no new package, paid calls, deployment or external message is required by this route<br>
> **Last reviewed:** 2026-10-15; author navigation/content checks, not a learner defense or grading calibration

## 1. Begin with a prediction, not a presentation

QuickCart's refund assistant returns a correct answer, yet the new release loses useful work. You can recite its architecture and run all tests. Can you identify which denominator hides the problem, modify the relevant check, and explain the consequence to support?

Treat a defense like a code review that follows a changed requirement into behavior. The analogy has a limit: a prepared code review may show what a team produced, while individual ownership needs evidence that **you** can explain and change it. Fluent vocabulary or AI-generated code is not that evidence. Conversely, uncertainty honestly bounded by a good diagnostic plan is stronger than an unsupported claim.

Pause: if a public reference passes every test, what remains unknown about the learner?

<details><summary>Reveal the reasoning</summary>

Their own implementation, explanation, independent transfer and judgment. A reference is teaching material; [C13's denied live attempt](../../docs/review-evidence/capstone-live-attempt.json) also shows why an attempted service call is not successful model evaluation. Do not repair an evidence gap by changing its label.

</details>

## 2. Practice throughout the path

At each existing stage, select its entry in the [practice bank](practice-bank.md). Before opening worked reasoning, write a prediction, make or sketch the small change in your personal project, run the relevant existing check and record what happened. Then explain the mechanism and send **no actual message**: draft the stakeholder update in your learning log. Use synthetic fixtures and preserve the original failed result.

Each bank entry has coding, debugging, design and stakeholder prompts. They are public practice, not secret assessment variants. Spend about 10–15 minutes on the stage's explanation/design/communication within its existing reflection time; practical changes use the module's existing independent exercise allocation, commonly 30–60 minutes. Select prompts that expose a gap rather than completing every bank prompt as extra compulsory work. Existing module estimates remain authoritative until the overall workload pilot reconciles them.

Start with [revision and glossary](revision-and-glossary.md) to locate an explanation you cannot yet give, rather than rereading every guide. The [remediation map](../../assessments/defense-and-remediation.md) directs you to existing labs; it does not prescribe repeating the entire course.

## 3. Integrated rehearsal — three hours

Use your capstone checkpoint and record dirty changes, runtime/lock, data/model/configuration versions, actual model/deployment evidence and assistance. If the independent project is not ready, rehearse on the disclosed public reference and label it practice only.

Allocate 30 minutes to tracing one request from identity through retrieval and provider validation to approval/effect; 60 minutes to a small code change with positive and negative checks; 45 minutes to a different fault diagnosis/repair; and 45 minutes to design, cost and stakeholder handover. Capture actual output and explain what you did without outsourcing the entire reasoning to a generated answer. No paid rerun is needed just to rehearse a boundary control.

Public rehearsal example: change the default provider reservation limit in a personal copy of [merchant support](../capstone/merchant-support/README.md), add a boundary test, then demonstrate that existing reservations still count after restart. Separately diagnose a revoked approver or stale policy. A quick configuration change must not silently reset durable admissions. The final unseen task must differ from the rehearsed example.

<details><summary>Hints and worked reasoning</summary>

First identify whether the bound is request-local, process-local or durable. Then distinguish changing a configured maximum from clearing history. A valid new limit may immediately deny requests if existing usage exceeds it; this is not automatically a defect. Explain the administrative decision needed for a new budget period. Retain the original history and use a separately identified authorized period if your changed design supports one. Compare local test evidence with the absent live-model/production guarantees.

</details>

## 4. Final individual defense and unseen modification

Use the [assessment procedure](../../assessments/defense-and-remediation.md#individual-defense-procedure). A reviewer inspects the real artifacts first, then selects a small change **after** the learner's baseline explanation. The change must target the submitted system, be achievable with its offline fixtures, and require a positive and negative check. The reviewer records the exact revealed task, help permitted/used, outcome and limitations in the private evidence record. Never publish unreleased variants or confidential feedback here.

A 75-minute defense plus 45-minute evidence/feedback review fits the two-hour planning allowance. This is a planning assumption, not a speed-based competency gate. Written, recorded or live formats may demonstrate the same technical evidence; accommodate the format without changing the competency. A solo learner can simulate selection and mark self-assessment, but cannot claim an independent unseen assessment.

Do not make final defense contingent on solving a surprise paid/cloud setup issue. Unavailable live evidence stays a separate missing milestone. A no-release recommendation may demonstrate good judgment while graduation delivery evidence remains incomplete. No pass is awarded for fluent presentation over failed authorization, execution bounds, secrets or truthful evidence.

## 5. Repair, reassess and hand off

Create your private record using [the template](evidence-template.md). Each essential dimension is **Demonstrated**, **Needs repair** or **Not attempted**, with direct evidence. These reuse the existing capstone meanings; they do not replace earlier point-based workbook rubrics. Retain the original failure, diagnose the gap, repair the smallest cause, rerun affected regression checks, and attempt a changed task. A familiar rerun alone cannot establish transfer.

Troubleshooting: if you can describe architecture but cannot locate enforcement, trace one failing request to its exact check; if checks pass but evidence is missing, regenerate the missing artifact rather than fabricate it; if setup blocks the task, preserve the symptom and return to the specific setup checkpoint; if the allotted repair reserve is insufficient, record remaining work and surface the workload decision. Do not silently add compulsory weeks or weaken gates.

No new service is started by these documents. Stop/clean only resources created in the selected lab using its exact cleanup procedure; retain sanitized evidence and keep confidential records outside public storage. No real customer data or messages are needed.

**You can now:** explain your own system end to end, make a reviewer-chosen change under observation, and repair a weak dimension with a changed reassessment. **Show it:** your defense record and any repair evidence.

**Next:** if any dimension is **Needs repair**, follow the [remediation map](../../assessments/defense-and-remediation.md) and reassess. This completes the Developer path. *Optional:* the [reusable Architect foundations](../../docs/architect-foundations.md) show what this evidence supports and which deeper topics remain selective/proposed. That map does not certify Architect readiness or add months to the Developer path.

Sources: repository-local [assessment contract](../../assessments/capstone-evidence.md), [style requirements](../../docs/study-guide-style.md) and linked module artifacts reviewed 2026-10-15. No new SDK/price claims or required external readings. [Course map](../../README.md) · [Assessment index](../../assessments/README.md)
