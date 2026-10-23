# LangChain chapter contract and current verification

> **Review:** 2026-10-14 | **Tasks:** C06-01 through C06-03 | **Status:** Draft

This companion completes shared starting-state, artifact, acceptance, cleanup and verification guidance without rewriting the substantial Fernwood lessons. Existing chapter outcomes, predictions, diagrams, worked examples, failure/repair instructions, exercises/hints, quizzes, source links and estimates remain authoritative. The audit reviewed all 19 numbered chapters; the glossary and assessment adapt the build sequence to their reference/assessment roles.

The current repeatable path is the [pinned mechanisms checkpoint](mechanisms-lab/README.md), a focused supplement for selected abstractions. The old full learner-project walkthrough is the [2026-10-11 historical record](../docs/final-verification.md), not a fresh blanket pass. Current static parsing and a new offline checkpoint cannot certify old hosted/local model outputs, Chroma, UI behavior or every optional dependency.

## Shared execution and evidence contract

For a main chapter, work in your own external langchain-learning project, except Chapter 15's separate empty fernwood-notes project and Chapter 14's explicitly optional setup. Use the [starting-state table](../docs/project-boundaries.md) and exact chapter file labels before copying code. Retain prerequisite files; these are named instructional checkpoints, not release tags. Do not run reference-only sample applications.

Each row below defines the learner artifact and minimum acceptance; each chapter supplies the detailed prediction, implementation, failure, repair and independent exercise. Record actual environment/lockfile, selected route, exact working directory, commands, observed outputs and independent change. Use the existing chapter hints/rubrics; changing words in a copied answer is not independent practice.

For model behavior, distinguish mock wiring, live inference, retrieval quality and supported-answer quality. Chapter 04's schema success did not establish correct extraction; Chapters 09/15 historically missed required qualifications. Preserve those as failures until a new full-rubric live comparison actually repairs them. A prompt edit or mock response is insufficient. No fresh hosted model or tracing upload occurred in C06.

## Lesson-specific records

### W-LC-00

- **Lesson:** [00-environment-setup](00-environment-setup.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** No project -> Python 3.11 project.
- **Final artifact:** sanity_check.py, .env.example, local lockfile.
- **Acceptance/failure evidence:** Interpreter/configuration check; missing hosted key remains a denial, not inference.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-01

- **Lesson:** [01-foundations](01-foundations.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Configured environment.
- **Final artifact:** foundations_lab.py and responsibility explanation.
- **Acceptance/failure evidence:** Token/cost assumptions and model versus application ownership.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-02

- **Lesson:** [02-models-and-messages](02-models-and-messages.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Configuration plus selected adapter.
- **Final artifact:** first_call.py, inspect_message.py.
- **Acceptance/failure evidence:** Inspect role/content and envelope; blank input rejects.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-03

- **Lesson:** [03-prompts](03-prompts.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Chapter 02 files.
- **Final artifact:** prompt_lab.py.
- **Acceptance/failure evidence:** Missing variables reject; compare full instructions without claiming truth.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-04

- **Lesson:** [04-structured-output](04-structured-output.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Prompt/message baseline.
- **Final artifact:** structured_output_lab.py.
- **Acceptance/failure evidence:** Malformed JSON rejects; supported-source and cross-field checks remain separate.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-05

- **Lesson:** [05-chains-and-runnables](05-chains-and-runnables.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Message and structured-output files.
- **Final artifact:** chain_lab.py.
- **Acceptance/failure evidence:** Explicit/composed stage agreement; wrong type/key faults reject.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-06

- **Lesson:** [06-conversation-history](06-conversation-history.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Chapter 05 project, in-memory session scope.
- **Final artifact:** history_lab.py.
- **Acceptance/failure evidence:** A/B isolation, retention, clearing and restart limits; legacy wrapper note applies.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-07

- **Lesson:** [07-embeddings-and-similarity](07-embeddings-and-similarity.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** History/message baseline.
- **Final artifact:** embedding_lab.py.
- **Acceptance/failure evidence:** Manual cosine, zero/mismatched vectors and exact-ID baseline.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-08

- **Lesson:** [08-documents-and-retrieval](08-documents-and-retrieval.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Embedding helper plus shared synthetic corpus.
- **Final artifact:** retrieval_lab.py, optional pdf_inspect.py.
- **Acceptance/failure evidence:** Inspect/index/reopen and stale revision rejection; source and passage completeness.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-09

- **Lesson:** [09-grounded-rag](09-grounded-rag.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Current selected retrieval snapshot.
- **Final artifact:** rag_lab.py.
- **Acceptance/failure evidence:** Unsupported/empty evidence abstains; assess full facts, not source ID alone.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-10

- **Lesson:** [10-conversational-rag](10-conversational-rag.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** History and RAG files.
- **Final artifact:** conversation_rag_lab.py.
- **Acceptance/failure evidence:** Rewrite fidelity, topic switch, ambiguity and isolated histories.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-11

- **Lesson:** [11-tools-and-agents](11-tools-and-agents.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Model helper and typed-output baseline.
- **Final artifact:** tools_lab.py.
- **Acceptance/failure evidence:** Denied/invalid requests never enter function; count attempted/completed separately.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** New selected-primitives supplement verified; the full chapter route retains historical verification limits.

### W-LC-12

- **Lesson:** [12-streaming-and-interfaces](12-streaming-and-interfaces.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Complete Chapter 09 files.
- **Final artifact:** terminal_stream.py, interface_backend.py, streamlit_app.py.
- **Acceptance/failure evidence:** Failed stream/turn does not commit; UI reruns do not reindex; stop servers.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-13

- **Lesson:** [13-debugging-testing-and-evaluation](13-debugging-testing-and-evaluation.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Retrieval/RAG/conversation files.
- **Final artifact:** test_workbook.py, evaluate_rag.py, retry_lab.py.
- **Acceptance/failure evidence:** Explicit denominators, required-facts review, exhausted-retry failure.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-14

- **Lesson:** [14-langgraph-and-langsmith](14-langgraph-and-langsmith.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Optional independent local graph setup.
- **Final artifact:** graph_lab.py.
- **Acceptance/failure evidence:** Local graph invalid input; hosted traces require separate evidence.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-15

- **Lesson:** [15-guided-integration-lab](15-guided-integration-lab.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Empty separate fernwood-notes directory.
- **Final artifact:** notes_service.py, notes_app.py, integration_check.py.
- **Acceptance/failure evidence:** All join/UI/fixture records inspected; fixture answering limitations retained.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-16

- **Lesson:** [16-practice-challenges](16-practice-challenges.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Core plus attempted integration.
- **Final artifact:** Seven independent challenge artifacts and existing ten-point rubric.
- **Acceptance/failure evidence:** Changed evidence/permissions/faults require tests and explained ownership.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-17

- **Lesson:** [17-revision-and-assessment](17-revision-and-assessment.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** Integration plus independent attempts.
- **Final artifact:** Existing twenty-point assessment and repair plan.
- **Acceptance/failure evidence:** No fabricated execution or high-total compensation for failed critical gates.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

### W-LC-18

- **Lesson:** [18-glossary](18-glossary.md); prerequisites and reading/build estimates are in its opening metadata.
- **Starting state:** No prerequisite for lookup.
- **Final artifact:** Definitions/distinctions and linked example explanation.
- **Acceptance/failure evidence:** Reference role: explain and trace a term; no new application build required.
- **Independent work:** Complete the chapter exercise/challenge before revealing its worked reasoning; the glossary instead asks you to trace a new term to an example.
- **Current execution boundary:** Current source/contract reviewed; full runtime/UI/live route was not rerun for C06.

## Cleanup, cost and retention

For every chapter, preserve learner source, lockfile and private evidence before removing generated artifacts. Verify Get-Location is the intended learner project. Stop Streamlit/Gradio with Ctrl+C; inspect/unload local models using Chapter 00's commands. Unloading is not deleting model downloads. Remove only a chapter-generated index/profile after confirming its path and preserving any needed reproducibility evidence. A missing index is repaired by the explicit matching profile/revision build, not a UI rerun.

Do not delete another learner's workspace or silently reset .env/history. Clear only the intended in-memory session during history exercises. Keep private keys and raw private traces out of public submissions. Local mode consumes compute; hosted chat/embedding calls can incur charges even when an answer is rejected. No paid call is required by the new checkpoint. Record live calls/usage separately and bound them using the earlier reliability guidance.

## Current limitations and decisions

The pinned 1.6.10 core emits a RunnableWithMessageHistory deprecation warning. W-LC-06 keeps manual history first and treats the wrapper as a legacy compatibility comparison. Do not add a graph framework merely to silence a warning; C07 teaches persistence after the requirement exists. Existing dynamic-install main lessons remain Draft and need their own route-specific lockfile; the new supplement's lockfile does not pin the entire Fernwood application.

Known historical quality failures remain visible: incomplete annual-limit scope/period, false abstention, inconsistent structured extraction, and U03's wrong structured-abstention status. The old integration fixture answered only A02; its contract records are not full quality success. Current complete source blocks are parsed, not replayed as live evidence. An independent learner walkthrough, hosted inference/tracing, actual UI verification and a fresh full-quality benchmark remain unperformed here.

Return to [workbook navigation](README.md) or [root course map](../../../README.md). No Ready for pilot or Published promotion follows from this audit.

External links in every chapter, including setup pages in W-LC-00 to W-LC-02, are classified and access-checked in the [W-LC source record](source-record.md).
