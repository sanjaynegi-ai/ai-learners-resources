# W-AGENTS-01 — Inspect a bounded tool loop

A model proposes a tool call. Which application checks still have to happen?

> **Your goal:** Inspect an actual bounded SDK loop and local tracing with a scripted provider.<br>
> **You need:** Read [tool-interface concepts](../../../study-guides/tool-interfaces/README.md) and complete the linked reliability/tool prerequisites.<br>
> **Estimated effort:** 15 min reading, 35 min guided, 15 min fault repair, 30 min independent comparison; estimates.<br>
> **You will produce:** Tool boundary/failure tests, loop evidence and an implementation comparison.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**QuickCart context:** this fictional shop's read-only stock lookup lets you observe model requests, tool entry and returned results separately. The SDK runtime is real; the model's choices are scripted.

**Project route:** use a personal copy of this independent `tool-loop` package, keeping its own lockfile/environment. Inspect trusted context and the registered tool, run the reference, then add the outage test and compare direct execution with orchestration. Do not merge the prior graph or stock-server environment into it.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-INTERFACE-01 | **Status:** Draft offline checkpoint, unpiloted<br>
> **Prerequisites:** [SG-INTERFACE-00](../../../study-guides/tool-interfaces/README.md), Python async/tests and trusted authorization.<br>
> **Question:** Did the tool actually run under trusted authority, or did the model merely request it?<br>
> **Effort:** 15 min reading, 35 min guided, 15 min fault repair, 30 min independent comparison; estimates.<br>
> **Artifact:** Actual SDK-loop result, local trace lifecycle, failure tests and a direct/graph/runner decision.<br>
> **Runtime:** Python 3.11.13, Windows PowerShell, openai-agents 0.23.1; transitive lockfile. No model credentials, inference or paid calls.

</details>

## Starting state and setup

`tool-loop-v1` is a complete worked reference. All data are synthetic QuickCart stock. The actual Agent/Runner invokes a registered function tool, but the custom Model is scripted; it does not contact OpenAI. No multi-agent work or consequential tools are present.

From repository root:

**Execution requirements:** Python 3.11.13, Windows PowerShell, openai-agents 0.23.1; transitive lockfile. No model credentials, inference or paid calls. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/agents-sdk/tool-loop
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run python -m tool_loop.demo
```

Expected: seven tests pass, one trusted tool entry with quantity 2, two scripted model calls and local trace start/end events. The fixed final prose is not credited as successful business execution; inspect trusted_tool_entries. Usage is synthetic zero, not measured provider pricing.

## Build the boundary in your learner copy

Read `src/tool_loop/demo.py`: Principal, lookup, the stock tool, ScriptedModel, LocalTrace and run. Principal comes from the host; quantity is the model-facing argument. The function rejects unauthorized tenant/role and invalid quantity before recording domain entry. Runner owns the call/result loop; max_turns=3 and an asyncio deadline bound it.

Predict what happens if the same valid arguments come from a viewer, and what happens with malformed JSON, a repeated-call model and a sleeping model.

<details><summary>Reveal the expected behavior</summary>

The SDK wraps the viewer's domain failure as UserError, and the entries list stays empty. Malformed JSON, bool quantities and out-of-range values fail the argument boundary. A repeated-call scripted model hits MaxTurnsExceeded. A sleeping model is cancelled by the cooperative deadline. The tests inspect those behaviors separately.

</details>

The custom LocalTrace implements SDK trace/span callbacks and replaces remote exporters before the run. Only lifecycle labels are retained, with sensitive-data tracing disabled. This is actual local SDK tracing, not a hosted trace upload. Processor configuration is process-global: this isolated single-run lab is not a concurrent production tracing design.

**Break and repair:** In a private copy, bypass lookup's role/tenant check. Run the denied tests, record the failure, restore the check and rerun. Do not turn a denial into a fallback success. To inspect a tool failure, call lookup with quantity zero; default tools expose no write operation.

## Independent modification and comparison

Add a synthetic stock-service outage inside `lookup` after authorization but before successful completion. Add a test proving the SDK surfaces failure, no completed lookup is credited, and the local trace remains inspectable without raw context. Keep viewer denial distinct from service failure.

<details>
<summary>After your attempt: failure-accounting hint</summary>

Separate attempted-entry and completed-result counters if your extension needs both. A function may be entered and then fail; a final friendly sentence cannot turn that failure into a completed lookup. Check the messages, trusted audit and result together.

</details>

Compare direct `lookup(Principal(),2)` with the actual runner, and with [W-GRAPH-01](../../langgraph/approval-workflow/README.md). Submit actual outputs, your failure regression and a 150-word decision. The runner helps when a model chooses tools; fixed lookup needs no agent. Durable human approval requires an explicit persistent orchestration design. Framework validation is not authorization.

Acceptance: seven reference tests plus your outage test pass, denied work is not credited, tracing contains no sensitive payloads, and you explain the model mock/real SDK distinction. Disclose assistance and handle an unseen repeated-call/role change.

## Troubleshooting and cleanup

| Symptom | Diagnostic / corrective action |
|---|---|
| UserError from stock | Inspect trusted role/tenant or argument failure; no automatic provider retry |
| MaxTurnsExceeded | Expected loop-bound failure; inspect scripted call count rather than raising the cap |
| TimeoutError | Deadline cancelled the sleeping mock; blocking external code needs separate controls |
| Unexpected trace upload | Ensure LocalTrace replaces remote processors before any run; do not add hosted exporters |

Keep private source/test/evidence copies. Remove only this project's generated .venv/results after verifying the working directory. No server, account or continuing resource remains. Real model choice, latency, quality, usage, hosted tracing, durable resume and production authentication are not tested here.

## Completion checkpoint

**Show it:** your two scripted model-call trace, trusted tool-entry evidence, denied/loop/deadline checks and independent outage regression. Label synthetic usage as synthetic rather than measured zero-cost inference.

**You can now:** explain the actual loop/tool checks and distinguish scripted model/local trace evidence from live behavior. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [exercise the MCP client/server boundary](../../mcp/stock-server/README.md). Use the root capability prerequisites when deciding whether to proceed.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p08--agents-sdk-and-mcp-interfaces) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
