# Chapter 17 — Revision and Assessment: Explain the Whole Pipeline

> **Study time:** 40–60 minutes revision, then 90–120 minutes assessment.  
> **Prerequisites:** Core Chapters 00–13, [guided integration](15-guided-integration-lab.md), and attempted [practice challenges](16-practice-challenges.md).  
> **Central question:** Can you explain, verify, and defend the assistant without relying on a plausible-looking response?  
> **Running example:** Fernwood team-notes assistant.

[Previous: Practice Challenges](16-practice-challenges.md) · [Index](README.md) · [Next: Glossary](18-glossary.md)

Chapter 14, LangSmith, Gradio, Wikipedia, and live paid services are **not prerequisites for the core assessment**. Complete the deterministic route and label any live checks untested. Optional extensions do not earn replacement credit for missing core evidence.

## Learning objectives

- Recall component responsibilities, data types, and trust/state boundaries.
- Select a simple workflow and distinguish it from agent behavior.
- Use uv and the workbook commands to reproduce and diagnose a learner project.
- Calculate quality measures with clear denominators and identify missing evidence.
- Complete a scored written/practical assessment and turn weak results into a repair plan.

## 1. Reconstruct the mechanism before revising

Without looking below, describe the path from a file to a displayed answer. Name what runs during indexing, what runs for each question, and where conversation history belongs.

<details><summary>Reveal a reference explanation</summary>

Indexing loads UTF-8 sources, preserves metadata, splits text, embeds document chunks, and saves a completed profile-specific snapshot. Querying reopens that snapshot, optionally resolves a follow-up using bounded session history, embeds the resolved question, retrieves passages, formats evidence, prompts a model, parses/validates the response, and displays the answer and sources. Claim support still requires review. The UI caches suitable resources and keeps conversation records per session. Querying does not rebuild the corpus. A clarification can skip retrieval/answering; empty evidence can skip the answer model.

</details>

The main recurring lesson is to inspect each handoff. Correct types do not prove correct meaning; a correct-looking answer does not prove the right evidence, session, or execution path was used.

## 2. Component and type reference

| Component | Input → output | Responsibility / boundary |
|---|---|---|
| Configuration helper | Private environment/configuration → provider settings | Validate setup; never print secrets |
| Chat prompt | Variables/messages → prompt value | Construct messages and distinguish instructions from data |
| Chat model | Messages → `AIMessage` | Generate content or structured tool requests; not execute your Python tools |
| Text extraction/parser | Message blocks/text → text or validated object | Handle output shape; factual support remains separate |
| Runnable composition | One stage's output → next stage's input | Make handoff types compatible; composition does not guarantee meaning |
| Embedding model | Text → numeric vector | Encode representation; consistent document/query configuration required |
| Loader/splitter | Files → `Document` objects → chunks | Preserve source metadata and enough context |
| Vector store/retriever | Query/vector → candidates, optionally scores | Select evidence candidates; proximity is not truth |
| Rewrite stage | Bounded history + latest turn → standalone question/clarification | Preserve intent; history is not policy evidence |
| Answer stage | Question + selected passages → answer contract | Ground claims or abstain; inspect claimed sources |
| Tool boundary | Named request + arguments → result/error | Validate, authorize, bound, execute, correlate results |
| UI | Submission → progress, accepted output, evidence | Own state lifetimes; do not ingest on reruns |
| Evaluation | Fixed cases + captured handoffs → judgments/measures | Separate contract, support, completeness, errors, and missing data |

## 3. Comparisons that prevent common mistakes

| Often confused | First responsibility | Second responsibility | Fernwood example |
|---|---|---|---|
| Prompt vs model | Messages/instructions | Generated response | An evidence-only prompt can still receive an unsupported answer |
| JSON validity vs truth | Shape/field consistency | Claim support | A valid response can say INR 99999 |
| Chat model vs embeddings | Generates responses | Produces vectors | An embedding vector cannot answer a policy question directly |
| Chunk size vs k | How source text is divided | How many candidates are returned | More candidates cannot restore a qualification absent from all selected chunks |
| Source hit vs passage coverage | Expected document appears | Required facts appear in supplied text | Equipment source ID may accompany an unrelated exclusions chunk |
| Retrieved IDs vs supporting citations | Candidate diagnostics | References claimed to support answer facts | Every claimed citation still needs passage-level checking |
| Stored history vs model context | What the application retains | What the current request includes | Old displayed turns may not enter the next prompt |
| Rewrite vs answer | Resolve the user's intent | Supply evidence-based facts | “And its limit?” needs a topic before allowance retrieval |
| Router vs agent | Predetermined path selection | Repeated model-selected steps | Fixed RAG is simpler than an agent for known retrieval/answer steps |
| Tool request vs execution | Model proposes a call | Application runs an allowed function | A greeting or invented “I checked” sentence proves no lookup |
| Validation vs authorization | Inputs satisfy constraints | Caller may perform the operation | Valid integers do not authorize a payment |
| Resource cache vs session state | Reusable server resources | Session-owned records/context | Share the locked store, not all users' histories |
| Streaming vs completion | Provisional output pieces | Normal termination and accepted result | Interrupted JSON/text cannot be saved as a completed answer |
| Graph state vs trace (optional) | Data used by workflow execution | Observations of execution | A trace does not choose the next node or prove truth |

## 4. Active-recall flashcards

Answer aloud before revealing each card. Explain one case example; reciting a definition alone is insufficient.

<details><summary>1. What three allowance qualifications must survive paraphrasing?</summary>

INR 12000 maximum, per calendar year, combined across eligible items. “Per item every month” changes the policy even with the same number.

</details>

<details><summary>2. What does lower Chroma cosine distance mean in this workbook?</summary>

Closer vectors under the configured distance metric. It is not an answer-confidence probability or proof of factual support. Do not generalize score direction across different APIs without checking their semantics.

</details>

<details><summary>3. When should a snapshot be rebuilt?</summary>

When source/chunk/embedding configuration changes, following the explicit revision/profile policy. Ordinary questions reopen/query an existing snapshot; they do not silently ingest.

</details>

<details><summary>4. What is the insufficient-evidence contract?</summary>

Status `insufficient_evidence`, answer exactly `I don't have reliable information on that in the provided documents.`, and an empty `source_ids` list. Retrieved candidates can still be displayed separately.

</details>

<details><summary>5. Why can a relevant VPN passage still require abstention?</summary>

It may describe connection steps but omit the server IP. Relevance does not supply an absent fact.

</details>

<details><summary>6. What should a follow-up rewrite avoid?</summary>

Changing topic/qualifiers, answering the question, inventing a premise, or treating prior assistant claims as verified policy. If intent is unclear, ask clarification.

</details>

<details><summary>7. How do you prove a tool attempt in Chapter 11?</summary>

Inspect the structured request, matching tool-result ID/status, and function-entry audit. Function entry can still end in failure; final prose alone proves neither attempt nor success.

</details>

<details><summary>8. Why might clearing UI history leave other records intact?</summary>

It clears current-session display/context only. It does not delete vectors, source files, provider logs, or every server cache.

</details>

<details><summary>9. What does unavailable token usage mean?</summary>

Unknown/not captured, not zero. The evaluation collector's chat usage also excludes embedding usage and does not establish actual billed cost.

</details>

<details><summary>10. Does a passing scripted injection case prove model safety?</summary>

No. The fixture ignores the instruction by construction. A live pass only describes the tested model/context/run; neither establishes universal resistance.

</details>

<details><summary>11. Why keep failed evaluation rows?</summary>

Dropping parser failures/timeouts can make results appear better than the system users experience. Report errors, denominators, unreviewed outcomes, and limits explicitly.

</details>

<details><summary>12. When is exact equality appropriate?</summary>

For IDs, enum statuses, deterministic arithmetic, required schema fields, and the exact abstention contract. Paraphrased policy answers need semantic review preserving facts, scope, negation, and timing.

</details>

## 5. Common traps and repairs

| Trap | Repair question/action |
|---|---|
| “Temperature zero guarantees identical correct answers” | Inspect actual repeated behavior and evidence; temperature is not a correctness proof |
| “A parser repaired it, so the answer is reliable” | Check whether facts were invented or altered; record the original failure |
| “We used the same vector dimensions, so any embedding model works” | Compare exact model/configuration/prefix profile; rebuild when it changes |
| “Raise k until the answer is right” | Compare fixed cases, evidence coverage, context cost, and regressions |
| “A real source ID means a verified citation” | Map each claim to the supplied passage |
| “All visible chat history reaches the model” | Inspect actual prompt inputs and retained bounds |
| “A model said approved, so execute the action” | Use application-owned permission checks before execution |
| “Importing Ollama proves the service/model is available” | Distinguish adapter import, running service, downloaded model, and successful request |
| “Streaming always reduces total latency or cost” | Measure time to first visible text separately from total duration and usage |
| “UI reruns should rebuild the corpus” | Keep ingestion explicit; cache/reopen resources and submit queries separately |
| “All offline tests passed, therefore live quality passed” | Label fixture/control-flow evidence separately from live model judgments |
| “Hosted tracing is local because inference is local” | Check trace-data destination independently of model location |

## 6. uv and diagnostic command reference

Commands operate in your **learner project**, never inside the workbook documentation folder. Initialization runs from its parent; all other examples assume the project root and the named chapter files/dependencies already exist. Dependency changes intentionally update project metadata/lock state; do not perform them while trying to reproduce a frozen baseline without recording the change.

| Purpose | PowerShell command | Recall |
|---|---|---|
| Create the workbook project | `uv init --no-package --python 3.11 --vcs none langchain-learning` | Then `cd langchain-learning` |
| Declare a runtime dependency | `uv add streamlit` | Records it in the learner project |
| Declare test tooling | `uv add --dev pytest` | Development group |
| Reproduce/check locked environment | `uv sync --locked` | Fails when the lock needs updating rather than silently changing it |
| Check interpreter | `uv run python --version` | Uses the project environment |
| Run against a checked lock | `uv run --locked notes_service.py` | Do not silently re-resolve a changed baseline |
| Run offline contracts | `uv run pytest -q test_workbook.py` | Requires Chapter 13's test file |

This is a short project-workflow reference, not a full uv command catalog. Compare the declared Python requirement, `pyproject.toml`, `uv.lock`, provider/model settings, and actual versions when reproducing someone else's result. A lockfile does not supply credentials, model downloads, source files, or an existing vector snapshot. See the official [locking/syncing](https://docs.astral.sh/uv/concepts/projects/sync/) and [dependency management](https://docs.astral.sh/uv/concepts/projects/dependencies/) references.

**Targeted checks — PowerShell, learner project root:**

```powershell
uv run retrieval_lab.py inspect --setting large
uv run retrieval_lab.py query --setting large --k 3 --question "What is the annual home-office reimbursement limit?"
uv run rag_lab.py --case unsupported
uv run conversation_rag_lab.py --case isolation
uv run tools_lab.py --mode agent --case denied
uv run terminal_stream.py --fail
```

These are offline diagnostic entry points, not a sequential installation recipe. The last command deliberately exits nonzero after partial output. Query commands require completed matching snapshots; do not create one implicitly inside a UI request. Use [Chapter 15's file-order table](15-guided-integration-lab.md) if a file is missing.

## 7. Final assessment — core route only

Complete Part A without opening its answers. Then complete Part B in your learner workspace before revealing the practical solution. Record elapsed time, help used, evidence locations, and verification scope. You may consult official documentation during implementation, but record changes you make and why.

**Total: 20 points.** Part A has five questions worth two points each. Part B uses the Chapter 16 ten-point rubric. Do not add flashcard/practice scores to this total; they serve revision, not extra assessment credit.

### Part A — five written cases (10 points, 25–35 minutes)

#### A1 — Trace types and contracts (2 points)

You compose a prompt, chat model, and JSON parser. The model returns a valid answer claiming a separate INR 12000 monthly allowance for each item. Describe the three handoff types and explain why a valid parsed result can still fail.

<details><summary>Answer, reasoning, and marking</summary>

Prompt variables/messages become a prompt value, the chat model returns an `AIMessage`, and text extraction/JSON validation yields the expected structured object. Award 1 point for tracing these boundaries without treating a raw message as an already validated dictionary. Award 1 point for explaining the period/combined-scope contradiction and the need to compare claims with supplied policy text. JSON validity or a supplied source ID cannot establish support. Revisit Chapters 02–05 and 09 if either point is missing.

</details>

#### A2 — Diagnose a retrieval miss (2 points)

An equipment source ID is returned for A04, but the selected passage lacks the receipt deadline. What evidence do you inspect, and what controlled comparison could test a repair without hiding unsupported U03 behavior?

<details><summary>Answer, reasoning, and marking</summary>

Award 1 point for inspecting exact chunks/metadata and the itemized-receipt/People Operations/30-calendar-days-after-purchase facts rather than crediting the source ID alone. Award 1 point for a one-variable comparison such as small versus large at fixed k, retaining U03 and reporting both gains and non-improvements/regressions. Preserve source/profile/revision consistency and do not put the missing answer into an undocumented prompt workaround. Revisit Chapters 07–09 and 13.

</details>

#### A3 — Resolve history without leaking it (2 points)

Two users discuss different topics and ask “And its limit?” What enters rewriting, what enters answering, and what happens when the relevant older topic is evicted?

<details><summary>Answer, reasoning, and marking</summary>

Award 1 point for selecting each user's own bounded history plus latest turn for rewriting, with ambiguity handled explicitly. Award 1 point for sending only the resolved question and fresh passages to this workbook's answer stage and explaining that evicted context cannot be assumed available. Prior assistant text is not verified policy. A session ID alone does not authenticate ownership. Revisit Chapters 06, 10, and 15; note Chapter 15's documented no-history standalone limitation rather than claiming it always clarifies.

</details>

#### A4 — Separate execution boundaries (2 points)

One tool request has a string amount, one has valid amounts but permission is denied, and one has spending above cap. State whether each enters the function and explain what establishes that conclusion.

<details><summary>Answer, reasoning, and marking</summary>

The invalid string fails schema validation and the denied request fails application authorization, both before function entry. Spending above cap passes field validation but raises a domain error after one function-entry audit. Award 1 point for all three paths and 1 point for correlated request/result IDs, result statuses, and audit evidence, distinguishing attempt from successful completion. Final prose and model-written “approved” text prove neither execution nor permission. Revisit Chapter 11.

</details>

#### A5 — Calculate and qualify results (2 points)

In a ten-case run, six cases are answerable and four unsupported. Five answerable cases receive answers: four complete supported answers and one unsupported answer. One answerable case abstains. All four unsupported cases abstain. Calculate complete-supported task success across all cases, unsupported abstention rate, and false-abstention rate. Every row has unavailable usage: what may you conclude about cost?

<details><summary>Answer, reasoning, and marking</summary>

Complete-supported task success is `(4 correct supported answers + 4 correct unsupported abstentions) / 10 = 8/10 = 80%`. Unsupported abstention is `4/4 = 100%`; false abstention is `1/6`, approximately 16.7%. Award 1 point for correct numerators/denominators and all three measures. Award 1 point for saying unavailable usage is unknown, not zero, with no justified token-cost estimate from those rows. The three rates describe different behavior; 100% unsupported abstention alone hides failures on answerable cases. These sample counts do not establish general reliability. Revisit Chapter 13.

</details>

### Part B — defend a working assistant (10 points, 60–90 minutes)

Use the Chapter 15 learner project or recreate it from the complete-snippet map. Do not import repository sample applications. Keep the fictional sources unchanged and use an existing completed fixture snapshot unless you intentionally create a new revision. No paid/model service is required.

**Tasks and evidence:**

1. Record project/Python/lock/profile/revision state and run the two-turn allowance CLI demo. Explain original question, resolved query, evidence, and answer.
2. Run `integration_check.py` to a **new** output filename and inspect all thirteen rows. Record the fixture's false abstentions and unsupported-case results; manually check the allowance amount, period, scope, and citation.
3. Verify history isolation and clearing using two independent sessions or a deterministic service/UI test. Demonstrate invalid-input rejection and a controlled failure that commits no partial turn.
4. Verify that repeated query/UI interactions do not ingest/re-embed documents and that the saved snapshot reopens after a process restart. Distinguish persisted index state from temporary conversation state.
5. Propose one bounded change, define its expected observable result, and compare it with the baseline. Report a non-improving outcome if that is what the evidence shows; do not loosen the policy/golden cases to manufacture success.

**Submission:** A project tree and configuration summary without secrets; command/test results; a per-case review table; a before/after failure or change trace; and a short trade-off statement. Label deterministic, simulated-provider, live, manual-review, browser-unverified, and untested evidence accurately. If live services are available, include their results as a separate appendix; they do not replace core contract/isolation checks or automatically add points.

**Scoring:** Apply the [five-category rubric in Chapter 16](16-practice-challenges.md#3-ten-point-self-study-rubric): understanding 2, implementation 2, verification 2, failure/correctness 2, trade-offs 2. Give verification credit for repeatable positive and negative evidence, not a screenshot of fluent prose. If you cannot run an interactive browser, automated UI checks plus an explicit visual-verification limitation can establish the deterministic scope; do not claim visual behavior passed.

<details><summary>One reasonable practical solution and marking guidance</summary>

Reproduce the project with uv and identify the matched fixture large/v1 snapshot. The two-turn demo resolves the fixed allowance follow-up and supplies the equipment passage. Collect all thirteen cases independently: the fixture answers A02, falsely abstains on seven answerable questions, and abstains on all five unsupported questions. Report those limitations rather than calling thirteen valid contracts thirteen correct answers.

Keep the service cached but pass copied bounded history per session. Verify A's topic never enters B's rewrite input; clearing A removes its display/history and preserves the index. Inject a controlled service failure and assert both successful-state lists remain unchanged. Prohibit document embedding during queries and reopen the snapshot in another process. For a controlled change, compare k with a case already covered: the same supported answer with more context is a non-improvement, not a success to exaggerate.

Award rubric points only for supplied evidence and reasoning. A supported allowance answer alone cannot earn isolation, persistence, or failure-handling credit. A live run is not required, but unrun live checks must remain labeled untested. A correct explanation of limitations is part of the result.

</details>

## 8. Scorecard and targeted repair

Copy this table into your learner notes before revealing solutions:

| Item | Maximum | Your score | Evidence / repair action |
|---|---|---|---|
| A1 — Types and contracts | 2 | | |
| A2 — Retrieval coverage | 2 | | |
| A3 — Context and isolation | 2 | | |
| A4 — Tool boundaries | 2 | | |
| A5 — Measures and missing data | 2 | | |
| B — Understanding | 2 | | |
| B — Implementation | 2 | | |
| B — Verification | 2 | | |
| B — Failure/correctness | 2 | | |
| B — Trade-offs | 2 | | |
| **Total** | **20** | | |

**Interpretation:** 16–20 indicates readiness for independent transfer within the verified scope; 10–15 calls for targeted repairs; 0–9 calls for revisiting prerequisites and rebuilding one boundary at a time. This is self-study guidance, not certification. Any unresolved history leakage, fabricated policy, ignored authorization denial, or hidden evaluation failure must be repaired regardless of total score.

| Weak item/category | Revisit | Practice retry |
|---|---|---|
| A1 / conceptual types | [02 messages](02-models-and-messages.md), [03 prompts](03-prompts.md), [04 schema](04-structured-output.md), [05 composition](05-chains-and-runnables.md) | Chapter 16 Challenge 2; trace actual input/output types |
| A2 / retrieval diagnosis | [07 embeddings](07-embeddings-and-similarity.md), [08 retrieval](08-documents-and-retrieval.md), [09 grounding](09-grounded-rag.md) | Challenge 3; compare exact passages, not just source IDs |
| A3 / history correctness | [06 history](06-conversation-history.md), [10 rewriting](10-conversational-rag.md) | Challenge 4; isolation/eviction/clear traces |
| A4 / permission or execution | [11 tools](11-tools-and-agents.md) | Challenge 5; correlate messages and audit |
| A5 / quantitative judgment | [13 evaluation](13-debugging-testing-and-evaluation.md) | Recalculate case counts; Challenge 3 controlled comparison |
| B implementation / environment | [00 setup](00-environment-setup.md), [15 integration](15-guided-integration-lab.md) | Challenge 1, then rebuild the integration file-order map |
| B verification / state lifecycle | [12 interfaces](12-streaming-and-interfaces.md), [13 evaluation](13-debugging-testing-and-evaluation.md) | Challenge 6; prove no partial commits or query-time ingestion |
| B failure/correctness | [09 grounding](09-grounded-rag.md), [11 tools](11-tools-and-agents.md), [15 integration](15-guided-integration-lab.md) | Challenges 2, 5, and 6; target the actual failed boundary |
| B trade-offs / transfer | [08 retrieval](08-documents-and-retrieval.md), [13 evaluation](13-debugging-testing-and-evaluation.md) | Challenge 7; new documents, missing facts, and explicit costs/limits |

For each weak item, choose one repair and rerun the original criterion. Record original score, repair, changed evidence, new score, and help used. Do not silently replace the failed attempt. A high average with one broken trust/state boundary is a reason for focused practice, not a reason to ignore it.

## 9. Completion and next step

- [ ] I can reconstruct indexing and querying and explain every major boundary.
- [ ] I attempted recall/assessment before reading the explained answers.
- [ ] I completed the core practical route with appropriately labeled evidence.
- [ ] I reported false abstentions, unsupported answers, errors, and unavailable usage honestly.
- [ ] I mapped weak items to specific chapter/exercise retries and rechecked a repair.
- [ ] I can state what remains unverified before moving to a larger project.

Use the [glossary](18-glossary.md) to revisit terminology, then the [separate RAG capstone](../02-rag-capstone-workbook/README.md) for a larger independent project. Optional framework/tracing knowledge can enrich that work, but it does not replace the core reasoning and evidence assessed here.

## References  

- [Shared materials](shared-materials.md): policy facts, fixed questions, and abstention contract.
- [Practice challenges and rubric](16-practice-challenges.md): graduated exercises and repair evidence.
- [Evaluation](13-debugging-testing-and-evaluation.md) and [integration](15-guided-integration-lab.md): commands, measurement limits, and actual fixture outcomes.
- [uv locking/syncing](https://docs.astral.sh/uv/concepts/projects/sync/) and [dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/): project workflow reference.


