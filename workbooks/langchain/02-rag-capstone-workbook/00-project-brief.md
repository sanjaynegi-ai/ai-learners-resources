# W-RAG-00 - A grounded policy lookup with revocation

**What may this policy lookup answer, and when must it withhold an answer?**

> **Your goal:** Define supported scope and failure behavior before changing the reference.<br>
> **You need:** [Retrieval foundations](../../../study-guides/retrieval-foundations/README.md), [permissions/grounding](../../../study-guides/retrieval-foundations/permissions-and-grounding.md), Python packaging and readiness evidence.<br>
> **Effort:** Scope work is part of the 3-4 hour guided/control estimate below; no separate lesson timing is validated.<br>
> **You will produce:** A one-page scope note covering supported, abstained, conflicting, denied and deleted-evidence cases. **Status:** Draft; offline reference, unpiloted.

**QuickCart** is the fictional e-commerce platform used across the course. Its support agents need applicable policy evidence while each merchant's records remain isolated. Build the provided curated, extractive RAG reference and defend its failure behavior. The final artifact is a local Python package and CLI, SQLite-backed authority/index state, cited quotes, separate retrieval/answer reports, regression tests, incident exercise and independent recall-notice extension. It is a module capstone, not program graduation or a deployed service.

**Your route:** define scope here, establish the workspace in W-RAG-01, trace authority in W-RAG-02, then inspect evidence mechanics before adding answer validation. If you already completed W-RAG-03–06 in the retrieval capability, revisit their acceptance evidence rather than repeating the whole checkpoint. Continue with W-RAG-07 after confirming that evidence is still valid for your current copy.

> [!IMPORTANT]
> This reference returns reviewed quotes for a narrow set of supported intents. A working offline pipeline does not establish general question answering, real-model quality or readiness to deploy.

Acceptance: supported lookup returns only an authorized current reviewed quote with document/chunk/revision/hash; unknown questions abstain; conflicts do not pick a convenient source; denied or revoked requests leak no snippets; deletion removes current index payloads and survives restart; held-out model quality is never inferred from mocks.

The worked reference uses a small explicit English intent route and authored feature vectors. Learn mechanisms here, then use the earlier learned-embedding route for a separately budgeted experiment. A live model adapter and deployment remain outside this module's offline completion claim. No actual payments, emails or cloud operations occur.

Total new guided/control work is estimated at 3–4 hours, plus the earlier 2.25-hour retrieval checkpoint, 85–110 minutes conceptual reading and a 2–3-hour independent transfer. Count the earlier reading/checkpoint once if you already completed them. These are editorial estimates, not observed learner times or additional compulsory months; reconcile them with the six-month budget.

## Define acceptance before running

Write one row per case in your scope note: question/requester, applicable source, expected outcome, forbidden disclosure and the check you will use. For example, a missing refund limit should abstain without inventing a number; a denied requester must receive no policy snippet. Keep current response outcomes (`ready`, `abstained`, `conflict`, `denied`) separate from events such as deletion that may cause a non-ready response.

## Check your reasoning

Attempt each question before opening its answer.

**Decision:** A supervisor asks for a refund limit that no document states. Which outcome should the reference return, and why is a plausible generic quote not enough?

<details>
<summary>Reveal worked reasoning</summary>

It should **abstain**. The acceptance rule says unknown questions abstain, and a quote is only evidence if it supports the specific claim. A general refund sentence does not establish a numeric limit. Tempting misconception: "any citation is better than none." An unsupported citation makes a wrong answer look verified.

</details>

**Prediction:** A policy document's access list changes to supervisors only after an agent's request has retrieved it but before the answer is delivered. Which outcome do you expect, and what must the response not contain?

<details>
<summary>Reveal worked reasoning</summary>

A non-ready status with no citation, document name or snippet. The W-RAG-10 drill shows **abstained** when the document's eligibility changes during the request; an unknown session is **denied**. The acceptance rule is that denied or revoked requests leak no snippets, because even a document title can disclose information.

</details>

## Completion checkpoint

**You can now:** state what the reference answers and how it responds to missing evidence, conflict, denied access and deleted sources.

**Show it:** your scope note.

**Reflect:** Which of the four non-ready outcomes would a stakeholder most likely mistake for a bug, and how will you explain it?

**Next:** [W-RAG-01 — Create your reproducible workspace](01-project-setup.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
