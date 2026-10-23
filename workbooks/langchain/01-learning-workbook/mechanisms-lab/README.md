# W-LC-MECH-01 — Explain what the abstraction does

> **Capability:** AI-INTEGRATE-01 · **Status:** Draft, offline reference; unpiloted<br>
> **Prerequisites:** [Python bridge](../../../python/README.md), W-LC-02–11 as relevant; [chapter contract review](../lesson-contract.md)<br>
> **Question:** Which responsibility does LangChain remove, and which must your application still enforce?<br>
> **Your goal:** Compare direct code with selected LangChain abstractions and decide which responsibility each one actually takes over.<br>
> **Effort:** 20 min reading, 30 min guided comparison, 15 min diagnosis, 40 min independent extension; estimates within existing integration/practice allocations.<br>
> **Artifact:** Direct/composed comparison, fault evidence, context-budget implementation and a decision note.<br>
> **Runtime:** Windows PowerShell, Python 3.11.13; langchain-core 1.6.10 and Pydantic 2.14.1, exact transitive versions in uv.lock.

## Starting state and setup

The supplied `mechanisms-v1` package contains the complete worked comparison and an unfinished independent extension. It is a small supplemental checkpoint, not a replacement Fernwood application. It uses QuickCart's synthetic carrier example to connect the preceding RAG module; existing Fernwood policies and rubric facts remain unchanged.

From repository root:

```powershell
Set-Location workbooks/langchain/01-learning-workbook/mechanisms-lab
$env:LANGCHAIN_TRACING_V2 = "false"
$env:LANGSMITH_TRACING = "false"
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run lc-mechanisms
```

Expected: nine tests pass; direct_equals_composed is true, session B sees only keyboard, retrieval retains QC-SHIP-01/revision 1, and the authorized tool returns quantity 2. These use **actual LangChain classes with a fixed-response mock**, not inference, provider-native structured output or model-selected tool calls. No provider adapters, credentials, network tools or paid calls are used. LangSmith is a transitive dependency; tracing is disabled and no upload is required. Keep private configuration out of this package.

**Compatibility warning:** This installed version emits a deprecation warning for RunnableWithMessageHistory. The wrapper is a compatibility comparison with the existing W-LC-06 lesson, not the recommended persistence architecture. Learn manual messages/history first; durable orchestration/persistence is covered by [W-GRAPH-01](../../../langgraph/approval-workflow/README.md). Do not hide the warning or treat a wrapper as storage/authentication.

## Inspect one boundary at a time

Open `src/lc_mechanisms/demo.py`. Predict each result before running the tests.

| Lesson | Explicit mechanism | LangChain implementation here | Why use it / what remains yours |
|---|---|---|---|
| W-LC-02 messages | Ordered role/content records; request/response envelope | HumanMessage, SystemMessage, AIMessage | Common message shape; token limits, provider errors and truth remain application/provider concerns |
| W-LC-03 prompts | Fill required variables and preserve roles | ChatPromptTemplate.invoke | Reusable variable composition; formatting is not input validation or authorization |
| W-LC-04 outputs | JSON/schema parsing followed by source/business checks | PydanticOutputParser then supported | Common parser boundary; schema-valid invented claims are still rejected; native provider schemas remain separately untested |
| W-LC-05 composition | Call stages explicitly and pass typed values | RunnableLambda and pipe/invoke/batch | Standard composition; no implicit durable workflow, retries, idempotency or transaction |
| W-LC-06 history | Select a session, append turns, retain a bound | Manual message baseline; optional deprecated history wrapper | Understand actual model inputs; session IDs are not authorization and four retained messages are not a token budget |
| W-LC-08 retrieval | Rank candidates while preserving provenance | BaseRetriever returning Document | Common downstream interface; lexical matching here is not learned semantic retrieval or an ACL |
| W-LC-11 tools | Validate arguments, authorize, then call a function | StructuredTool with strict Pydantic args | Inspectable typed tool interface; trusted role checks happen before invocation, not in model arguments |

`direct()` validates the bounded question and exact fixture evidence, then uses explicit messages, mock call, JSON validation and source validation. Missing or changed fixture evidence stops before the fixed responder, so skipped context cannot silently become a supported answer. `composed()` performs those same boundaries using a prompt/runnable/parser pipeline. Prefer explicit calls while stage boundaries are changing; use common runnable interfaces when several integrations benefit. The framework earns its complexity through reduced integration glue, not improved factual correctness by itself.

## Break, diagnose and repair

1. Remove evidence from the prompt input: missing-variable test must reject it before any call.
2. Keep valid JSON/source ID but change the quote: parsing succeeds; supported rejects the unsupported claim.
3. Return a dictionary from the mock stage where the parser expects text/message: the bad-stage test rejects the incompatible handoff.
4. Try quantity=true, quantity=6, or an extra role field: strict tool schema rejects them. A valid request from viewer is denied before the tool.

For an actual fault drill in your learner copy, temporarily replace the supported check with unconditional acceptance. Run the schema/semantic test, observe failure, restore it and rerun all tests. The author clean-copy record also checks that tests catch shared session history. Keep both failed and repaired evidence; do not edit observations to fit expectations.

## Independent transfer: fit whole evidence under a budget

Implement `exercises/context_budget.py`, retaining complete Document objects in original order, deduplicating identical source/revision/content, rejecting conflicting content for the same source/revision, and skipping passages that would exceed a positive integer character budget. Preserve metadata and input objects. Reject bool/zero/negative budgets. This is a character exercise, not a model tokenizer.

```powershell
uv run python exercises/check_context.py
```

The starter stops with NotImplementedError until completed. Then integrate the selector after KeywordRetriever in your learner pipeline, and test that the expected source is retained or explicitly reported as missing under a tight budget. Never silently convert skipped evidence into a supported answer.

<details><summary>Progressive hints and public reasoning aid</summary>

Track a running character total and a dictionary keyed by source/revision. Do not slice page_content, because that can remove a qualification. Deduplicate before counting; inspect a duplicate identity even when the budget is exhausted. The public reference is `context_budget_reference.py`; `uv run python exercises/check_context.py --reference` checks its reasoning. Passing that supplied reference is not independent integration evidence.

</details>

Acceptance: checker passes on your implementation, your integrated pipeline tests exercise skipped and retained evidence, and a 150-word decision explains whether you still need the retriever/runnable abstraction. Disclose assistance and explain a small unseen budget/source change.

## Troubleshooting, limits and cleanup

| Symptom | Diagnostic / corrective action |
|---|---|
| History deprecation warning | Expected at pinned version; use manual baseline and preserve compatibility note |
| Missing package/import | Confirm this working directory and uv.lock, then locked sync |
| Schema parses but assertion fails | Inspect source support; do not weaken the check |
| Failed independent checker | Inspect bounds/duplicate identity; hints are above |

No network inference or server runs. Preserve private evidence, then remove only this checkpoint's generated .venv/results directories from its verified working directory. Restore prior tracing environment settings if appropriate. This checkpoint does not reverify the entire Fernwood integration, Chroma, Streamlit, hosted adapters or model quality. See the [current review](../lesson-contract.md) and historical verification. The [deeper stateful route](../../../langgraph/approval-workflow/README.md) comes later on the course map (AI-GRAPH-01).

## Completion checkpoint

**You can now:** compare explicit message, call and parse code with LangChain prompts, runnables, retrievers and typed tools, and fit whole evidence passages within a context budget.

**Show it:** passing tests and your context-budget implementation.

**Next:** return to [W-LC-15 — Guided Integration Lab](../15-guided-integration-lab.md).

## Official references

Checked 2026-10-14 against official reference/search entries and installed signatures/source. Reference pages may return Markdown unsupported by the browser reader; installed interfaces were executed at the pinned version. All are optional **Reference**, free, Python prerequisite, 5–10 min per relevant section:

- LangChain, [ChatPromptTemplate](https://reference.langchain.com/python/langchain-core/prompts/chat/ChatPromptTemplate), invoke/messages.
- LangChain, [PydanticOutputParser](https://reference.langchain.com/python/langchain-core/output_parsers/pydantic/PydanticOutputParser), parsing boundary.
- LangChain, [RunnableWithMessageHistory](https://reference.langchain.com/python/langchain-core/runnables/history/RunnableWithMessageHistory), session factory; deprecation observed in installed 1.6.10.
- LangChain, [BaseRetriever](https://reference.langchain.com/python/langchain-core/retrievers/BaseRetriever), retrieval contract.
- LangChain, [StructuredTool](https://reference.langchain.com/python/langchain-core/tools/structured/StructuredTool), args_schema/from_function.
