# LangChain Learning Workbook

> **Audience:** Python learners new to LangChain.  
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

This folder contains workbook Markdown and diagrams. Create your working project in a separate directory of your own, outside this repository. The workbook will supply every required file as a labeled snippet; you will not need to run the existing repository sample applications.

The planned project name is `langchain-learning`. Start with simple scripts in that project root, then add small modules when their imports and purpose have been taught. No packaging or `src/` layout is assumed.

## Recommended study route

1. Complete chapters 00-06 for setup, foundations, prompts, structured output, chains, and history.
2. Complete chapters 07-11 for embeddings, retrieval, RAG, conversational retrieval, and tools.
3. Complete chapters 12-13 for streaming, Streamlit, diagnosis, tests, and evaluation. Gradio is an optional comparison inside Chapter 12.
4. Optionally complete Chapter 14 for a small LangGraph workflow and LangSmith tracing. An account-free inspection alternative will be supplied.
5. Assemble the assistant in Chapter 15, attempt Chapter 16 independently, and assess yourself with Chapter 17. Use Chapter 18 throughout as a reference.

The optional extension is not required for integration or core assessment. The [separate RAG capstone workbook](../02-rag-capstone-workbook/README.md) is the next project, not an additional requirement here.

Plan for one chapter per study session, taking breaks between theory and hands-on work. Chapter-specific estimates will be added after walkthroughs; current scaffolds do not justify a total duration claim. Keep notes on your predictions, observations, failures, fixes, and unresolved questions.

## Chapter index

- [00 - Environment Setup](00-environment-setup.md)
- [01 - Foundations](01-foundations.md)
- [02 - Models and Messages](02-models-and-messages.md)
- [03 - Prompts](03-prompts.md)
- [04 - Structured Output](04-structured-output.md)
- [05 - Chains and Runnables](05-chains-and-runnables.md)
- [06 - Conversation History](06-conversation-history.md)
- [07 - Embeddings and Similarity](07-embeddings-and-similarity.md)
- [08 - Documents and Retrieval](08-documents-and-retrieval.md)
- [09 - Grounded RAG](09-grounded-rag.md)
- [10 - Conversational RAG](10-conversational-rag.md)
- [11 - Tools and Agents](11-tools-and-agents.md)
- [12 - Streaming and Interfaces](12-streaming-and-interfaces.md)
- [13 - Debugging, Testing, and Evaluation](13-debugging-testing-and-evaluation.md)
- [14 - LangGraph and LangSmith](14-langgraph-and-langsmith.md) (optional)
- [15 - Guided Integration Lab](15-guided-integration-lab.md)
- [16 - Practice Challenges](16-practice-challenges.md)
- [17 - Revision and Assessment](17-revision-and-assessment.md)
- [18 - Glossary](18-glossary.md)

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

## How lessons will work

Each lesson will connect an everyday analogy and concrete failure to theory, a diagram walkthrough, guided construction, verification, troubleshooting, exercises, explained quizzes, and revision. Copying output is not the goal: explain the mechanism and test an independent variation.


