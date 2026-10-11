# Chapter 16 — Practice Challenges: Explain, Build, Break, and Defend

> **Study time:** 3–5 hours across several sessions; repeat weak areas before moving on.  
> **Prerequisites:** Core Chapters 00–13 and the [guided integration lab](15-guided-integration-lab.md). Chapter 14, Gradio, Wikipedia, and hosted tracing are optional and are not assessed here.  
> **Central question:** Can you solve a changed problem and produce evidence that your solution works?  
> **Running examples:** Fernwood notes assistant and a small independent studio-policy transfer exercise.

[Previous: Guided Integration](15-guided-integration-lab.md) · [Index](README.md) · [Next: Revision and Assessment](17-revision-and-assessment.md)

## Learning objectives

- Diagnose configuration, contract, retrieval, conversational, and interface failures independently.
- Implement a bounded change in a learner-owned project and verify both success and failure paths.
- Distinguish deterministic evidence from live model-quality observations.
- Transfer the taught pipeline to a small new corpus without relying on Fernwood-specific answers.
- Score your reasoning, implementation, verification, correctness, and trade-offs and identify what to revisit.

## 1. How to use these challenges

Close the worked solution before starting. Predict the outcome, write down the expected evidence, implement in your own learner project, then test. Reveal Hint 1 only if you cannot identify the mechanism; Hint 2 narrows the implementation. Read the solution after your attempt and compare reasoning, not just final prose.

Challenges 1–2 are beginner, 3–5 intermediate, and 6–7 integration/transfer. Each has constraints, deliverables, and observable acceptance criteria. Complete all seven for the full practice route; shorter sessions can tackle one challenge at a time. Use the ten-point rubric in Section 3 for each challenge.

**Working directory:** Your separate learner project, outside this workbook repository. Preserve a baseline copy or use your own version control before deliberately breaking code. Use new evaluation filenames and new snapshot revisions when required; do not delete a working index to disguise a failure. For Challenge 7, use a separate workspace so changes cannot contaminate Fernwood results.

**Verification honesty:** Offline fixtures establish contracts and control flow. They cannot establish semantic retrieval, model understanding, or injection resistance. If you lack a live model, complete deterministic checks and evidence review, label live generation untested, and explain the missing evidence. Do not replace model-quality observations with scripted answers and claim equivalent validation.

### Pause and predict

Your change passes all contract tests and gives a plausible answer with a real source ID. Is the challenge complete?

<details><summary>Reveal the reasoning</summary>

Only if the actual acceptance criteria are met. A real source ID can accompany a false claim; a fixture can pass while a live model fails; and a UI can display an answer while mixing sessions. Inspect the evidence at the boundary the challenge asks you to verify.

</details>

## 2. Challenge set

### Challenge 1 — Reproduce a project without guessing (Beginner, 20–30 minutes)

**Scenario:** A learner says, “The imports worked yesterday, but this terminal fails.” They have a `pyproject.toml`, `uv.lock`, and learner scripts. Their terminal may be in the wrong directory or using a different interpreter.

**Goal:** Establish the project state before making dependency changes.

**Constraints:** Use uv from the learner project root. Do not edit the lockfile, print `.env`, or run a paid call as a diagnostic. Distinguish package import success from provider configuration/service availability.

**Starting checks — PowerShell, learner project root:**

```powershell
Get-Location
uv run python --version
uv sync --locked
uv run python -c "import langchain_core, langchain_openai, langchain_ollama; print('Imports passed')"
```

**Deliverables:** Working directory, Python version, locked-sync/import outcomes, and a short diagnosis naming which facts are still unknown. Identify how you would check hosted configuration or the local service without exposing a key.

**Acceptance:** You can reproduce the documented Python 3.11 environment and import required adapters, or identify the precise failed setup step. You do not describe a successful import as a successful model request. If the starting project does not exist, use Chapter 00 or Chapter 15's setup rather than inventing missing files.

<details><summary>Hint 1 — separate the boundaries</summary>

Directory selection, interpreter/dependency resolution, configuration validation, and service availability are different checks. Start with the first two.

</details>

<details><summary>Hint 2 — narrower check</summary>

Compare your current directory with the location of `pyproject.toml`. Use the project's `uv run` interpreter. Chapter 02's `read_configuration` validates provider/key shape; it does not prove that the provider accepts a key or that Ollama is serving the model.

</details>

<details><summary>One reasonable solution and reasoning</summary>

Record `Get-Location`, the `uv run` Python version, and `uv sync --locked` before modifying dependencies. If imports fail after successful locked sync, confirm the imported packages are declared in that project and that the script is being run through uv. If imports pass, move to configuration/service diagnosis under Chapter 00; do not reinstall unrelated packages. Keep any real key in the private learner `.env`. Report hosted/local inference as untested until a deliberate service check succeeds.

</details>

### Challenge 2 — Valid JSON, invalid claim (Beginner, 25–35 minutes)

**Scenario:** The assistant returns this response for the allowance question:

**Illustrative response — data to evaluate, not a runnable file:**

```json
{"status":"answered","answer":"You can claim INR 12000 for each item every month.","source_ids":["FW-EQUIPMENT-001"]}
```

**Goal:** Distinguish schema validation, supplied-source membership, and claim support.

**Constraints:** Use the unchanged shared equipment policy. Do not weaken validation or alter the policy to match the response. Do not rely on a model judge as the only reviewer.

**Deliverables:** A three-column claim / supporting-or-contradicting passage / decision table, a repaired answer, and an explanation of which automated checks could still pass the original response. Use Chapter 09's `parse_response` in your learner copy if you want to confirm membership behavior.

**Acceptance:** The repaired answer preserves currency, cap, calendar-year period, and combined scope. An invented source ID is rejected; a supplied real ID is still checked against the actual passage. Explain what happens if the relevant passage was not retrieved at all.

<details><summary>Hint 1 — inspect qualifications</summary>

The number is only one part of the policy. Period and per-item versus combined scope change the entitlement.

</details>

<details><summary>Hint 2 — compare exact fields</summary>

Chapter 09 validates response shape and supplied IDs. It does not semantically compare “every month” with “per calendar year” or “each item” with “one combined annual limit.”

</details>

<details><summary>One reasonable solution and reasoning</summary>

The amount INR 12000 is present, but the monthly period and separate per-item allowance contradict the passage. A supported repair is “Up to INR 12000 per calendar year, combined across a monitor, keyboard, or ergonomic chair.” Cite the equipment source only when the supplied evidence includes that policy. A valid shape and existing supplied ID can pass programmatic checks while the original answer fails support. If evidence is missing, diagnose retrieval and abstain rather than inserting a remembered answer invisibly.

</details>

### Challenge 3 — Right document, wrong passage (Intermediate, 35–50 minutes)

**Scenario:** A04 asks what to submit for reimbursement and by when. Search returns `FW-EQUIPMENT-001`, yet the selected chunk only describes the allowance limit.

**Goal:** Repair coverage by changing one retrieval variable and measuring the result.

**Constraints:** Keep source text, embedding profile, revision, question, and generation behavior fixed. Compare either chunk setting at fixed k or k at fixed chunk setting. Build any missing snapshot explicitly before querying. Keep the unsupported U03 question in the comparison.

**Starting commands — PowerShell, learner project root with Chapter 13 files:**

```powershell
uv run evaluate_rag.py --setting small --k 3 --output practice-small-k3.jsonl
uv run evaluate_rag.py --setting large --k 3 --output practice-large-k3.jsonl
```

**Deliverables:** Exact selected chunk IDs/text, expected-source hit and passage-support judgments, the changed variable, and a reasoned keep/reject decision. Include one case where the change does not help. Report model generation untested if you only use the fixture.

**Acceptance:** A04's selected evidence includes itemized receipt, People Operations, and 30 calendar days after purchase. U03 still has no supported IP answer. You report both improvements and unchanged/regressing cases, including context-size costs; source presence alone earns no coverage credit.

<details><summary>Hint 1 — choose the failed handoff</summary>

If the required sentence never reaches the answer prompt, changing answer wording is not the first repair.

</details>

<details><summary>Hint 2 — narrower comparison</summary>

Chapter 13's fixture comparison observed required-term coverage 2/3 small versus 3/3 large across A02/A04/A06. Inspect your own rows; do not assume this lexical-fixture observation transfers to a live embedding model.

</details>

<details><summary>One reasonable solution and reasoning</summary>

Compare small and large chunks at k=3, preserving all other settings. Read the returned equipment passages to find whether the receipt/deadline sentence is actually supplied. A larger chunk may retain those facts together, but can add unrelated text. A02 already has enough evidence in the large fixture at k=1; raising k need not improve its answer. U03 may return VPN text but still must abstain. Retain the retrieval change only if the broader fixed-case evidence justifies it; the scripted answerer's A04 abstention remains a separate known limitation.

</details>

### Challenge 4 — Two histories, one shared backend (Intermediate, 35–45 minutes)

**Scenario:** Session A discusses equipment reimbursement; session B discusses VPN access. Both ask “And its limit?” A later unrelated exchange evicts A's older topic.

**Goal:** Show isolation, bounded context, and clarification without promoting prior assistant text to policy evidence.

**Constraints:** Reuse Chapter 10 or Chapter 15's actual history-selection path. Do not store histories in a shared cached service. Keep at most two complete pairs for rewriting and test clearing. Distinguish the Chapter 10 ambiguity fixture from Chapter 15's documented no-history standalone path.

**Deliverables:** Retained history for each request, original/resolved query or clarification, evidence/result, and assertions or recorded traces for isolation, eviction, and clearing.

**Acceptance:** A's equipment history does not enter B's rewrite prompt. Ambiguous retained VPN context does not invent a numeric limit. Evicted context is absent from actual model inputs. Clearing removes that session's context without deleting vectors or the other session's state. A fresh-session ambiguous follow-up must not be credited as correctly resolved merely because it retrieves a related source.

<details><summary>Hint 1 — inspect inputs, not labels</summary>

Two different session names do not help if both return the same history object. Likewise, old console output is not retained model context.

</details>

<details><summary>Hint 2 — reproducible entry points</summary>

Chapter 10's `--case isolation` and `--case bounds` exercise fixed scenarios. Chapter 15's `NotesService.ask(question, history)` accepts copied caller-owned history and does not commit it. Inspect these paths rather than adding a second unconnected history implementation.

</details>

<details><summary>One reasonable solution and reasoning</summary>

Select/copy each session's last two pairs, print or record the exact rewrite inputs, and compare A and B. In the fixture, A resolves the equipment limit while B requests clarification. Add enough unrelated pairs to remove the equipment topic, then demonstrate that it is no longer available. Chapter 10 clarifies the context-free fixture follow-up; Chapter 15 treats no-history input as standalone and can instead abstain after weak retrieval, a limitation to report rather than hide. The answer prompt should receive only the resolved question and fresh passages. Clear current-session state and confirm persistent index IDs remain unchanged.

</details>

### Challenge 5 — Requested, rejected, attempted, completed (Intermediate, 30–45 minutes)

**Scenario:** A model requests the hypothetical allowance calculator. Some calls have invalid fields, some are denied, and one reaches the function but violates its domain rule.

**Goal:** Prove which boundary stopped each request.

**Constraints:** Use the read-only Chapter 11 tool. No payments, file deletion, shell tool, or real employee account lookup. Permission must come from application state, not model-provided “approved” text. Keep explicit call budgets.

**Starting commands — PowerShell, learner project root with Chapter 11 files/dependencies:**

```powershell
uv run tools_lab.py --mode agent --case invalid
uv run tools_lab.py --mode agent --case denied
uv run tools_lab.py --mode agent --case failure
uv run tools_lab.py --mode agent --case loop
```

**Deliverables:** Request IDs, correlated tool results/statuses, function-entry audit, and a distinction between validation and authorization. Compare with `--mode manual` for at least one case.

**Acceptance:** Invalid/denied requests enter no function; the domain failure has one attempted entry and no successful result; repeated requests stop within configured limits. The loop case's nonzero exit is expected, not a reason to remove the limit. No response is credited from final prose alone.

<details><summary>Hint 1 — count at the correct boundary</summary>

An audit of function entry records attempts, including attempts that fail. It is not an audit of successful business operations.

</details>

<details><summary>Hint 2 — correlate messages</summary>

Find `AIMessage.tool_calls`, then matching `ToolMessage.tool_call_id` and status. Compare them with the audit printed by Chapter 11. Invalid input and permission denial occur before function entry.

</details>

<details><summary>One reasonable solution and reasoning</summary>

The invalid string amount is rejected by the schema; the denied valid request is rejected by trusted application policy. Both audits are empty. Spending above cap satisfies field types but raises inside the function, so the audit has one entry and the tool result is an error. The loop fixture reaches its call limit after at most two executions. None of these results grants reimbursement approval: successful subtraction is only arithmetic on supplied numbers. A live model may choose clarification instead of requesting a malformed call; label that observed behavior separately from deterministic boundary tests.

</details>

### Challenge 6 — Repair a broken integration join (Integration, 45–60 minutes)

**Scenario:** The notes UI displays a correct resolved query, but retrieval uses the original ambiguous follow-up. An error during another request also leaves a misleading partial turn in displayed history.

**Goal:** Fix the joins and verify state/resource lifetimes.

**Constraints:** Work in a separate copy of the Chapter 15 learner project. Keep ingestion outside UI requests. Validate complete output before committing state. Do not add LangGraph, LangSmith, external tools, or a new dataset as prerequisites. Preserve safe error handling.

**Deliverables:** Before/after request trace, the exact value passed to the backend, state before/after a failed request, index IDs across a restart, and UI evidence for clearing/isolation. If browser execution is unavailable, provide an automated UI test where possible and label visual behavior unverified.

**Acceptance:** Full allowance question → follow-up retrieves with the resolved query. Failures save neither partial history nor display records. Two independent sessions do not share conversation data; clearing one removes both its display and rewrite context. Repeated submissions never invoke document embedding or indexing. The existing snapshot remains queryable in a separate process.

<details><summary>Hint 1 — trace the data, not just the display</summary>

Showing `resolved.question` in a widget does not prove that it was passed to `Backend.answer`.

</details>

<details><summary>Hint 2 — locate the commit boundary</summary>

Chapter 15 assigns `query = resolved.question`, returns a validated record, computes `next_history`, then updates both session lists only in the successful `else` branch. Use that order. Cache resources, not records.

</details>

<details><summary>One reasonable solution and reasoning</summary>

Restore the resolved query as the backend argument and verify the exact input with a spy/trace. Stage the returned record and updated history before assigning either session field. Inject a controlled backend exception and check both state lists remain unchanged and the user sees a generic error. Rerun successful requests, clear one session, and reopen the persisted store in another process. This repairs glue/state behavior; it does not establish live semantic retrieval or injection safety. Report those limits separately.

</details>

### Challenge 7 — Transfer to a tiny studio corpus (Integration/transfer, 60–90 minutes)

**Scenario:** You need to answer two studio-room questions instead of Fernwood employment-policy questions. Reusing an unchanged prompt or fixture could accidentally return the Fernwood allowance.

**Goal:** Transfer loading, metadata, persistent retrieval, evidence formatting, and evaluation to a small new domain. This is a bounded two-document exercise, not another capstone.

**Starting state:** Create a **new** learner directory using Chapter 15's initialization/dependency/file-order instructions. Keep the original Fernwood project intact. Do not place the new documents inside the old corpus or reuse its snapshot. Replace the new project's knowledge contents with exactly the two UTF-8 files below.

**Configuration/data — `knowledge/room-booking.txt`**

```text
Source ID: ST-ROOM-001
Title: Fictional Studio Room Booking
Effective date: 2026-01-01
Status: Current

Section: Booking duration
One room booking may last at most two hours. This limit applies to each booking, not to total weekly use.

Section: Changes
To change a booking, email the studio coordinator at least one working day before the booked start time.
```

**Configuration/data — `knowledge/studio-access.txt`**

```text
Source ID: ST-ACCESS-001
Title: Fictional Studio Access
Effective date: 2026-01-01
Status: Current

Section: Entry
Use your assigned access card to enter during your booked time. Do not lend your access card to another person.

Section: Boundary
This note does not specify replacement-card fees or weekend opening hours.
```

**Constraints:** Keep source IDs/metadata and query-time evidence display. Adapt the copied loader's `FILES` list to these two filenames and replace Fernwood-specific prompt wording. Build a fresh snapshot in this new root. If using a new revision name, update every backend selection consistently; otherwise a fresh-root v1 is acceptable. Keep generation fixture and live routes explicitly labeled. Do not use Wikipedia or invented studio facts to fill missing policy.

**Required cases:**

| ID | Question | Expected support/outcome |
|---|---|---|
| T01 | How long may one room booking last? | At most two hours per booking; not a weekly total; ST-ROOM-001 |
| T02 | How do I change a booking, and how early must I ask? | Email studio coordinator at least one working day before booked start; ST-ROOM-001 |
| T03 | May I lend my access card to someone else? | No; ST-ACCESS-001 |
| T04 | How much does a replacement access card cost? | Insufficient evidence; no fee supplied |
| T05 | What time does the studio open on Sunday? | Insufficient evidence; no weekend schedule supplied |

**Deliverables:** Adapted file/import/configuration map, source metadata/chunk inspection, explicit index/query commands, five-case evidence table, and one deliberately irrelevant-passage test. Use Chapter 09's answer contract, with the same exact abstention sentence and empty supporting IDs for unsupported cases.

**Acceptance:** No Fernwood fact, source ID, or old snapshot appears in answers. T01–T03 each have the required source passage supplied; T04/T05 abstain. Invalid/unknown citations are rejected. An access-card passage cannot justify a booking-change deadline. If offline only, verify retrieval/contract checks and draft human-reviewed answers; mark live generation untested. A newly scripted studio responder is plumbing evidence only.

<details><summary>Hint 1 — identify domain assumptions</summary>

The source filename list, prompt wording, fixed-case fixture, and evaluation questions are all domain-specific. A reusable model/store wrapper alone does not remove those assumptions.

</details>

<details><summary>Hint 2 — narrower adaptation map</summary>

In the new project, change `retrieval_lab.FILES` to the two studio filenames, retain its source-ID/date extraction, and inspect chunks before indexing. Replace Chapter 09's system prompt domain and its fixture cases rather than silently using the Fernwood responder. Replace the evaluation case list/golden expectations too. Use a separate root so the profile-derived store path cannot open your Fernwood snapshot by accident.

</details>

<details><summary>One reasonable solution and reasoning</summary>

Create the two sources in a fresh learner root and adapt the loader and prompt together. Index once, then reopen/query without document embedding. For each case record the actual supplied text: T01 needs the two-hour/per-booking qualification; T02 needs email recipient, one working day, and the booked start reference; T03 needs the no-lending rule. T04/T05 have explicit topic boundaries but no answer values, so abstain. Supply only access evidence for T02 as a negative test: a related studio source cannot support a booking-change deadline. Retain the answer schema and membership check, but perform claim review independently. The fixture can be rewritten for these five fixed cases only if it remains labeled scripted. Designing a broader product, production permissions, and richer retrieval belongs to the separate capstone.

</details>

## 3. Ten-point self-study rubric

Score **each challenge** independently, from 0–2 in each category. A runnable artifact alone is insufficient. For explanation-focused tasks, “implementation” means a reproducible diagnostic/review procedure rather than unnecessary application code.

| Category | 0 points | 1 point | 2 points |
|---|---|---|---|
| Understanding | Misidentifies mechanism or boundary | Mostly correct; important assumption missing | Explains the mechanism and relevant assumptions accurately |
| Implementation | Required artifact absent or behavior broken | Partial solution; a stated constraint not met | Artifact/procedure meets all stated constraints |
| Verification | No observable evidence | Happy-path check only, or evidence incompletely labeled | Repeatable success and relevant negative checks with honest verification labels |
| Failure/correctness | Unsupported claims, unsafe bypass, or hidden failure | Failure noticed but diagnosis/handling incomplete | Correct boundary diagnosis, evidence-based handling, and no invented success |
| Trade-offs | No rationale or unsupported guarantee | Names a cost/limit without relating it to the choice | Justifies choice, costs, limitations, and what would change the decision |

**Interpretation:** 8–10 is ready to explain and transfer; 5–7 needs targeted repair and rerun; 0–4 needs a prerequisite revisit before building further. This is a learning aid, not certification. A score does not override the acceptance criteria: unresolved history leakage, invented policy facts, or executing a denied action must be repaired even with a high total.

If you work offline, score the completed deterministic scope and state the missing live evidence. You may earn full credit for an explicitly offline challenge by meeting its criteria, but cannot label live generation/provider behavior verified. Record help used; a correct result reached after reading a solution is progress, and should be retried independently before claiming mastery.

**Copy this scorecard into your learner notes:**

| Challenge | Understanding /2 | Implementation /2 | Verification /2 | Failure/correctness /2 | Trade-offs /2 | Total /10 | Evidence and next action |
|---|---|---|---|---|---|---|---|
| 1 — Reproduce setup | | | | | | | |
| 2 — Claim support | | | | | | | |
| 3 — Passage coverage | | | | | | | |
| 4 — History boundaries | | | | | | | |
| 5 — Tool execution | | | | | | | |
| 6 — Integration joins | | | | | | | |
| 7 — Studio transfer | | | | | | | |

All seven total at most 70 points; average challenge score is total divided by seven, out of ten. If you attempt fewer, report which ones and the denominator rather than presenting a full-route score. Recheck acceptance criteria and the weakest category even when the average looks strong.

## 4. Turn weaknesses into a repair plan

| Observed weakness | Revisit | Retry evidence |
|---|---|---|
| Cannot reproduce environment/imports | [00 setup](00-environment-setup.md), [02 models](02-models-and-messages.md) | Challenge 1 directory/interpreter/lock/configuration boundary record |
| Confuses JSON validity with truth | [04 structured output](04-structured-output.md), [09 grounding](09-grounded-rag.md) | Challenge 2 claim-support table and unknown-ID rejection |
| Treats nearest document as an answer | [07 embeddings](07-embeddings-and-similarity.md), [08 retrieval](08-documents-and-retrieval.md) | Challenge 3 exact passages and unchanged unsupported-case behavior |
| Mixes sessions or assumes unlimited memory | [06 history](06-conversation-history.md), [10 conversational RAG](10-conversational-rag.md) | Challenge 4 isolated inputs, eviction, clearing |
| Treats tool request as permission/execution | [11 tools](11-tools-and-agents.md) | Challenge 5 correlated messages and audit counts |
| UI reruns rebuild or corrupt state | [12 interfaces](12-streaming-and-interfaces.md), [15 integration](15-guided-integration-lab.md) | Challenge 6 no-ingestion/no-partial-commit checks |
| Cannot judge whether a change helped | [13 evaluation](13-debugging-testing-and-evaluation.md) | Challenge 3 one-variable comparison with a non-improving case |
| Hard-codes Fernwood assumptions | [03 prompts](03-prompts.md), [08 retrieval](08-documents-and-retrieval.md), [15 integration](15-guided-integration-lab.md) | Challenge 7 new-domain cases and no stale policy/source IDs |

Choose one repair, define the expected changed observation, and rerun the same case. Preserve failed evidence alongside the fixed result. If a change does not improve the relevant criterion, record that outcome and revise the diagnosis instead of adding unrelated complexity.

## 5. Knowledge checks

<details><summary>1. Can a non-improving experiment still be successful learning?</summary>

Yes. A controlled comparison that shows no benefit can justify retaining a simpler configuration. Report the evidence and limits rather than manufacturing an improvement.

</details>

<details><summary>2. Why use new documents for transfer?</summary>

They reveal hidden assumptions in prompts, fixtures, filenames, snapshots, and golden cases. Repeating the same policy answer does not show that you can adapt the pipeline.

</details>

<details><summary>3. What should you do when live services are unavailable?</summary>

Complete contract/control-flow/retrieval-fixture checks, review passages manually, and label live model behavior untested. Do not claim a scripted answer demonstrates live quality.

</details>

## 6. Revision and next step

- [ ] I attempted the challenges before revealing solutions and recorded help used.
- [ ] I produced artifacts and negative-path evidence, not just plausible answers.
- [ ] I can defend state ownership, evidence support, and execution permission separately.
- [ ] I transferred the pipeline to new documents without leaking old policy assumptions.
- [ ] I scored each attempt, identified weak categories, and reran a targeted repair.
- [ ] I distinguished deterministic, simulated-provider, live, and untested results.

Continue to [Revision and Assessment](17-revision-and-assessment.md) to consolidate the core material. For a larger independent project, use the separate [RAG capstone](../02-rag-capstone-workbook/README.md); the tiny studio transfer here is deliberately limited to two documents and five questions.

## References  

- [Shared Fernwood cases](shared-materials.md): fixed corpus and policy expectations for Challenges 2–6.
- [Chapter 13](13-debugging-testing-and-evaluation.md): comparisons, metrics, offline tests, and safe diagnosis.
- [Chapter 15](15-guided-integration-lab.md): complete learner-project creation order and integration contracts.

