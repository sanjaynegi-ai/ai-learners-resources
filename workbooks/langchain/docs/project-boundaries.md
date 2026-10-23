# Learner project boundaries and starting states

> **Reviewed:** 2026-10-14
> **Scope:** Documentation-defined learner projects; static starting-state review, not a fresh execution claim

The learning workbook is documentation. Learners create projects outside this repository. Each independent project owns its dependencies, configuration, lockfile, fixtures and generated results. Retain earlier files unless a chapter explicitly instructs a change. Chapter instructions provide exact file contents and commands; the table identifies the state to resume from, without inventing Git release tags.

## Learning project: `langchain-learning`

Use the [workbook README](../01-learning-workbook/README.md) for prerequisites and [W-LC-00 — Chapter 00](../01-learning-workbook/00-environment-setup.md) for setup. Named checkpoints below mean completed chapter instructions, not published tags. Save your own checkpoint after verification. Python 3.11 and route-specific configuration are established in Chapter 00; later dependency additions follow their own chapter commands.

| Lesson | Starting state | Files or responsibility introduced |
|---|---|---|
| 00 | Personal project parent directory; no existing learner project required | New `langchain-learning`, uv metadata/lock state, private configuration and `sanity_check.py` |
| 01 | Verified Chapter 00 project | `foundations_lab.py` |
| 02 | Chapter 00 configuration and Chapter 01 concepts | `first_call.py`, reused by subsequent labs |
| 03 | Chapter 02's complete `first_call.py` and dependencies | Parameterized prompt lab; retain model configuration boundary |
| 04 | Chapters 02–03 complete | `structured_output_lab.py` beside `first_call.py` |
| 05 | Chapters 03–04 complete; Chapter 02 model helper unchanged | `chain_lab.py` |
| 06 | Chapter 05 complete and Chapter 02 helper present | `history_lab.py` |
| 07 | Chapter 06 concepts and Chapter 02 configuration helper | `embedding_lab.py`; offline vectors distinguished from live vectors |
| 08 | Chapter 07 `embedding_lab.py`, Chapter 02 helper and prescribed synthetic files | `retrieval_lab.py`, persistent profile/revision snapshots; optional PDF inspector |
| 09 | Chapter 08 files and the explicitly indexed matching profile/revision | `rag_lab.py` and output/evidence contract |
| 10 | Chapter 09 RAG contract plus earlier history concepts | `conversation_rag_lab.py` |
| 11 | Chapters 02/04 files and schema concepts; chapters 09–10 trust context | `tools_lab.py`; bounded/denied/failure cases |
| 12 | Chapter 09 complete files and chapter 06 state concepts | `terminal_stream.py`, `interface_backend.py`, `streamlit_app.py`; optional `gradio_app.py` |
| 13 | Complete chapters 08–10 files and prior project environment | `test_workbook.py`, `evaluate_rag.py`, `retry_lab.py`; tests are created in the learner project |
| 14 (optional) | Python functions/dictionaries and chapters 05/13 | `graph_lab.py`; optional tracing configuration; not required for integration |

Before a query, use the chapter's index command for the selected profile/revision. Do not reuse live and fixture indexes interchangeably or rebuild an index in a UI rerun merely to repair a setup mistake. Follow each chapter's expected acceptance properties and failure checks before treating its checkpoint as complete.

## Integration project: `fernwood-notes`

[W-LC-15 — Chapter 15](../01-learning-workbook/15-guided-integration-lab.md) deliberately starts from an **empty, separate learner directory** after core chapters 00–13. It assembles the taught components using explicit source-chapter file instructions, creates `notes_service.py`, `notes_app.py` and `integration_check.py`, and indexes its own prescribed corpus/profile. Chapter 14 is optional. This clean assembly tests reproducibility and component joins; it is not a complete application copy at every lesson.

Chapter 16 starts from the completed Chapter 15 project and its checks for independent variations. Chapter 17 requires core chapters, integration and attempted practice; it specifies evidence rather than a new application copy. Chapter 18 and shared materials are references. Retain your own lockfile and redact configuration; live evaluation remains separately reported.

## Other routes and duplication decisions

- The [single-file guide](../00_LangChain_Learning_Guide.md) overlaps model/prompt/history/RAG topics. It is a separate reference route; do not mix its snippets or environment assumptions silently into workbook checkpoints. Consolidation or retirement requires a later focused content decision.
- The [RAG capstone workbook](../02-rag-capstone-workbook/README.md) contains scaffolds. Its runtime, dependencies, exact starting project and reference implementation are not yet specified; do not infer them from a sample application.
- `part1-langchain-demo/` and `part2-fernwood-assistant/` are reference-only by owner direction. Exclude them from course implementation, maintenance, verification and completion gates. They may inform explanations; their manifests, tags and tests do not establish learner readiness or course delivery evidence. Do not modify them.
- Synthetic sources exist in shared-material instructions and `sample-corpus/`. Their actual reuse/semantic equivalence across future modules has not been established. Retain them locally; no shared package or `shared-assets/` directory is introduced merely to enforce a layout.

No application is moved or duplicated by this document. Keep future runnable starter/reference code near its workbook, with one environment per independent project and explicit checkpoints. This section 4 audit establishes boundaries; dependency compatibility, source correctness and fresh runtime execution remain later verification tasks.

[Learner entry](../../../START-HERE.md) · [Workbook index](../01-learning-workbook/README.md)
