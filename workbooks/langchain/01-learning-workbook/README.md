# LangChain Learning Workbook

> **Status:** Draft for chapters 00–18 and shared materials. Historical verification is documented below; current publication gates are not established. This declaration is an authoring state, not a completion claim.

> **Audience:** Experienced backend engineers who may be new to AI, Python and LangChain; complete the targeted Python prerequisite check before these labs.
> **Running example:** A fictional Fernwood team-notes assistant.  

Learn to build a small assistant whose behavior you can explain, inspect, test, and improve. You will begin with model calls, add prompts and typed pipelines, introduce conversation history and document retrieval, then combine them into a grounded assistant with a simple interface.

## What you will learn

By the end, you should be able to:

- Create and reproduce a Python project using uv.
- Explain messages, tokens, prompts, models, embeddings, and framework responsibilities.
- Compose chains and validate structured inputs and outputs.
- Keep conversation histories separate and bounded.
- Index documents, preserve sources, and retrieve useful evidence.
- Build basic and conversational RAG and identify unsupported answers.
- Define typed tools and inspect agent execution.
- Build a Streamlit interface and evaluate quality, failures, latency, and usage.
- Explain when LangGraph or LangSmith would help.

## Before you start

You need basic Python: variables, strings, lists, dictionaries, functions, imports, and exceptions. You should be able to save a UTF-8 file, run a terminal command, and navigate directories. No prior LangChain, vector database, Docker, or frontend experience is required.

Use Windows PowerShell and an editor such as VS Code for the primary instructions. Bash alternatives will be labeled when syntax differs. The course baseline is Python 3.11, selected during uv initialization. 

Choose either a hosted OpenAI route with credentials and billing, or a local Ollama route with enough compute for the selected model. Both routes include chat and embeddings through the core RAG lessons. Initial downloads require internet; local compute is not cost-free. Model quality and speed can differ. Exact installation steps will be taught in Chapter 00.

## Where your projects belong

The `mechanisms-lab/` subdirectory is a small executable supplement with its own manifest/lockfile. It is independent of your external `langchain-learning` and `fernwood-notes` projects; do not merge all course dependencies into one environment. Main chapter files still belong in your learner workspace.

This folder contains workbook Markdown and diagrams. Create your working project in a separate directory of your own, outside this repository. The workbook will supply every required file as a labeled snippet; you will not need to run the existing repository sample applications.

The project name is `langchain-learning`. Start with simple scripts in that project root, then add small modules when their imports and purpose have been taught. No packaging or `src/` layout is assumed.

## Recommended study route

Use the [chapter contract review](lesson-contract.md) for starting artifacts, acceptance, cleanup and current verification boundaries. The [W-LC-MECH-01 offline checkpoint](mechanisms-lab/README.md) gives a small pinned, reproducible comparison of actual LangChain messages/prompts/parsers/runnables/history/retrievers/tools with their explicit mechanisms. It supplements chapters 02–11 and existing integration practice; it does not reverify every live or UI route.

1. Complete chapters 00-06 for setup, foundations, prompts, structured output, chains, and history.
2. Complete chapters 07-11 for embeddings, retrieval, RAG, conversational retrieval, and tools.
3. Complete chapters 12-13 for streaming, Streamlit, diagnosis, tests, and evaluation. Gradio is an optional comparison inside Chapter 12.
4. Optionally complete Chapter 14 for a small LangGraph workflow and LangSmith tracing. The chapter includes account-free local inspection.
5. Assemble the assistant in Chapter 15, attempt Chapter 16 independently, and assess yourself with Chapter 17. Use Chapter 18 throughout as a reference.

The optional extension is not required for integration or core assessment. The [separate RAG capstone workbook](../02-rag-capstone-workbook/README.md) is a separate project placed earlier on the course map (AI-RAG-01, before Chapter 09) and reused at AI-RELIABLE-01; it is not an additional requirement of this workbook.

Plan for several sessions per longer chapter, taking breaks between theory and hands-on work. Chapters 00–13 total approximately 18–27 hours; allow another 2–3 hours for integration, 3–5 hours for practice, 2–3 hours for revision/assessment, and 30–45 minutes for a first glossary review. Optional Chapter 14 adds 70–100 minutes. These are editorial planning estimates, not measured beginner completion times; installations, downloads, live evaluation, and repeated exercises take additional time. Keep notes on your predictions, observations, failures, fixes, and unresolved questions.

## Chapter index

- [W-LC-00 — 00 - Environment Setup](00-environment-setup.md)
- [W-LC-01 — 01 - Foundations](01-foundations.md)
- [W-LC-02 — 02 - Models and Messages](02-models-and-messages.md)
- [W-LC-03 — 03 - Prompts](03-prompts.md)
- [W-LC-04 — 04 - Structured Output](04-structured-output.md)
- [W-LC-05 — 05 - Chains and Runnables](05-chains-and-runnables.md)
- [W-LC-06 — 06 - Conversation History](06-conversation-history.md)
- [W-LC-07 — 07 - Embeddings and Similarity](07-embeddings-and-similarity.md)
- [W-LC-08 — 08 - Documents and Retrieval](08-documents-and-retrieval.md)
- [W-LC-09 — 09 - Grounded RAG](09-grounded-rag.md)
- [W-LC-10 — 10 - Conversational RAG](10-conversational-rag.md)
- [W-LC-11 — 11 - Tools and Agents](11-tools-and-agents.md)
- [W-LC-12 — 12 - Streaming and Interfaces](12-streaming-and-interfaces.md)
- [W-LC-13 — 13 - Debugging, Testing, and Evaluation](13-debugging-testing-and-evaluation.md)
- [W-LC-14 — 14 - LangGraph and LangSmith](14-langgraph-and-langsmith.md) (optional)
- [W-LC-15 — 15 - Guided Integration Lab](15-guided-integration-lab.md)
- [W-LC-16 — 16 - Practice Challenges](16-practice-challenges.md)
- [W-LC-17 — 17 - Revision and Assessment](17-revision-and-assessment.md)
- [W-LC-18 — 18 - Glossary](18-glossary.md)

## Shared reference materials

The [Fernwood documents, evaluation cases, and lab notebook](shared-materials.md) are ready for reuse across the chapters. Create the document files in your own project only when the relevant lab instructs you. The shared page also defines evidence, citation, and abstention scoring; it is a reference rather than an additional required chapter.

## Prerequisite self-check

Try each question before expanding its explanation. If several are unfamiliar, review those Python or terminal concepts before starting the labs.

### 1. Functions

What does `def greet(name): return "Hello " + name` produce when called with `greet("Mira")`? Does it print anything by itself?

<details><summary>Show answer</summary>

It returns the string `Hello Mira`. Returning is not printing: use `print(greet("Mira"))` to display it. Labs use functions to return results for later stages.

</details>

### 2. Dictionaries

Given `record = {"source": "handbook.txt"}`, what do `record["source"]` and `record.get("page", "unknown")` return?

<details><summary>Show answer</summary>

They return `handbook.txt` and `unknown`. Direct indexing requires the key; `.get()` can supply a default. Retrieval metadata uses dictionaries.

</details>

### 3. Imports

Why might `from dotenv import load_dotenv` fail even after a package was installed elsewhere on your machine?

<details><summary>Show answer</summary>

The script may use a different Python environment. Installing globally does not install into every project. Use the project's uv commands and select its interpreter in your editor. Package distribution names and Python import names can differ.

</details>

### 4. Exceptions

What happens when `int("hello")` executes, and how could a program display a helpful message instead of crashing?

<details><summary>Show answer</summary>

It raises `ValueError`. Catch that specific exception around the conversion and explain the expected input. Avoid hiding unrelated failures under a broad catch.

</details>

### 5. Terminal navigation

From your personal projects directory, what does `cd langchain-learning` change? Why does it matter before running a relative filename?

<details><summary>Show answer</summary>

It changes the terminal's working directory. Relative paths are resolved from that directory. Use `Get-Location` in PowerShell to check where you are. Do not assume the editor's active file determines the terminal directory.

</details>

### 6. Files

What does `Path("notes.txt").read_text(encoding="utf-8")` need before it can succeed?

<details><summary>Show answer</summary>

Import `Path` from `pathlib`, create the file at the expected location, and ensure it contains readable UTF-8 text. A missing file raises `FileNotFoundError`. The explicit encoding avoids platform-dependent text decoding.

</details>

## How lessons work

Use the [readiness route](../../../START-HERE.md), [starting-state table](../docs/project-boundaries.md) and [learning-design review](../../../docs/learning-design-audit.md) to choose prerequisites and record evidence. Fernwood's fictional policy notes teach grounding and abstention; preserve source IDs and the combined annual equipment limit in shared materials. Reference/sample corpora are not interchangeable inputs. New engineering extensions use QuickCart unless another domain has an explained benefit.

Each lesson connects an everyday analogy and concrete failure to theory, a diagram walkthrough, guided construction, verification, troubleshooting, exercises, explained quizzes, and revision. Copying output is not the goal: explain the mechanism and test an independent variation.



## Verification baseline and limitations

**Current scoped review: 2026-10-14.** [C06 execution evidence](../../../docs/review-evidence/langchain-mechanisms.json) records 19 chapter contracts, 25 parsed complete Python blocks and a fresh-copy `mechanisms-lab` run: nine tests pass and three injected faults are caught. The independent context-budget reference passes; the starter intentionally stops until implemented. The pinned supplement uses core 1.6.10/Pydantic 2.14.1 and documents the history-wrapper deprecation. Parsing does not execute the main chapter applications, and this review does not repair or reclassify historical live quality failures. Hosted inference, tracing, main UI and an independent learner walkthrough remain untested in this review.

**Last verification: 2026-10-11.** The external Windows/PowerShell walkthrough used uv 0.8.3 and Python 3.11.13. The baseline includes LangChain 1.4.4, core 1.6.9, OpenAI adapter 1.7.0, Ollama adapter 1.1.0, Chroma adapter 1.1.0, Pydantic 2.14.0, and Streamlit 1.65.0. Keep your own `uv.lock`; independently resolved environments can differ. The [verification record](../docs/final-verification.md) lists all tested versions and chapter evidence.

Offline labs, eight automated tests, session/rerun checks, Markdown rendering, and SVG review passed. The prescribed local `llama3.1:8b` chat model and Nomic embeddings were exercised, including native extraction, RAG, tools, streaming and integration. These runs exposed incomplete answers and a schema-valid extraction that failed evidence checks; a rewrite prompt ambiguity was repaired. Hosted inference remains unverified because credentials were unavailable. Hosted tracing delivery, interactive editor setup, and an independent beginner walkthrough were also not performed. Fixture results teach mechanics and failure inspection; they do not certify live model quality.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p06--langchain-abstractions-and-integration) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.

External links in every chapter, including setup pages in W-LC-00 to W-LC-02, are classified and access-checked in the [W-LC source record](source-record.md).
