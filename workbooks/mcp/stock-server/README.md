# W-MCP-01 — Inspect the client/server tool boundary

A tool server returns a valid response. Does that make the result trusted?

> **Your goal:** Exercise a real local MCP client/server boundary while retaining application authorization and result validation.<br>
> **You need:** Read [tool-interface concepts](../../../study-guides/tool-interfaces/README.md) and the module prerequisites below.<br>
> **Estimated effort:** 15 min reading, 35 min guided, 20 min diagnosis, 40 min independent extension; estimates.<br>
> **You will produce:** Protocol execution and denied/invalid/unavailable-server evidence, with a defended interface decision.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**QuickCart context:** the fictional shop's stock request now crosses a local process boundary. A valid protocol response still needs host-side checks, and tool discovery does not grant permission.

**Project route:** use a separate personal copy of `stock-server`. Trace launch, initialization, discovery, invocation and result validation; predict denied/error behavior before the drill. Complete the allowlist extension while retaining server-side checks. The SDK tool-loop lab is a comparison, not a hidden dependency that calls this server.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-INTERFACE-01 | **Status:** Draft local checkpoint, unpiloted<br>
> **Prerequisites:** [SG-INTERFACE-00](../../../study-guides/tool-interfaces/README.md), Python async and process basics.<br>
> **Question:** Does discovering a tool authorize its use or make its returned content trustworthy?<br>
> **Effort:** 15 min reading, 35 min guided, 20 min diagnosis, 40 min independent extension; estimates.<br>
> **Artifact:** Actual MCP handshake/discovery/call, denied/failure evidence, hostile-result test and host allowlist extension.<br>
> **Runtime:** Python 3.11.13, Windows PowerShell, mcp 2.3.0; exact transitive lockfile. No model calls, listening network port or external account.

</details>

## Starting checkpoint and commands

`mcp-stock-v1` contains one client and a separate local stdio server process. The host launches only the known repository module under its own interpreter, never a model-provided executable. All stock is synthetic and read-only.

From repository root:

**Execution requirements:** Python 3.11.13, Windows PowerShell, mcp 2.3.0; exact transitive lockfile. No model calls, listening network port or external account. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/mcp/stock-server
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run python -m stock_mcp.client
```

Expected: seven tests pass; client returns QC-42, quantity 2, available true. Deliberate denied/failure cases may log server exception diagnostics to stderr; those are expected rejection evidence. The subprocess closes when the client context exits. Do not run the server alone expecting a printed chat answer: its stdout carries protocol messages.

## Follow the exchange

Read `src/stock_mcp/client.py` and `server.py`. stdio_client launches the known local module; ClientSession initializes, lists tools and calls stock. The server constructs its argument schema and validates a strict integer quantity. The server-owned launch role decides whether the read is permitted. A tool argument cannot change that role. This is a fixed local fixture identity, not HTTP/OAuth authentication or a multi-user service.

The client handles MCP 2.x is_error explicitly and validates the untrusted returned JSON. It rejects extra instruction fields, wrong product, mismatched requested quantity, invalid availability and oversized text. Validation is not proof of a remote service's factual truth. The result text bound applies after SDK decoding; no wire-level memory cap is claimed.

An overall ten-second cooperative timeout and five-second session read timeout bound communication. Unknown tool names are rejected after discovery. The host chooses the pinned server executable/arguments; do not fetch/run arbitrary advertised servers. Adding HTTP would require transport authentication, identity binding, origin/audience considerations and authorization design beyond this stdio lab.

## Predict, fail, diagnose and repair

The tests cover viewer denial, malformed quantities, deliberately failing fault tool, missing executable, unknown purchase tool and hostile result content. They inspect the actual failure category inside asynchronous ExceptionGroups rather than crediting any exception as a correct rejection.

**Predict first:** if the client launches the server with the viewer role, does the stock call return a result, an error result, or an exception in the client? Write it down, then run the drill.

**Fault drill:** In your private copy, change the client launch role to viewer. The normal call must fail with MCP tool rejected/failed. Inspect the stderr diagnostic and error flag; do not parse an error message as a stock answer. Restore the authorized fixture launch and rerun. This restores the intended local fixture, not a production permission grant.

**Independent extension:** Discovery later advertises a purchase tool. Implement a host allowlist containing only stock, even if purchase is discoverable. Add tests that discovery does not expand permission, stock still works, and the unknown/disallowed tool never reaches invocation. Preserve server-side checks: a host allowlist alone cannot authorize another client. Then add a tool-result instruction field and verify result validation rejects it without executing anything.

<details><summary>Hints and worked reasoning, after your attempt</summary>

Calculate the intersection of discovered names and host-approved names, and validate the selected name before `call_tool`. Do not put the allowlist in a prompt or a model-controlled tool argument. Listing stock and purchase yields only stock as callable in this host, and a role-denied stock call still fails at the server.

</details>

Acceptance: reference suite plus your allowlist tests pass, unexpected result fields never enter host policy, and a 150-word note distinguishes protocol, transport, authentication, authorization and business correctness. Explain an unseen new tool or unavailable-server fault and disclose assistance.

## Cleanup and limits

The client context closes the child server; no persistent daemon is launched. Check the working directory, preserve private evidence, and remove only this project's .venv/results when finished. Never add debug print to server stdout. No credentials, paid model, remote server, real purchase, OAuth flow, live agent/MCP adapter or deployment is demonstrated. The separate [Agents SDK lab](../../agents-sdk/tool-loop/README.md) teaches orchestration; joining them is an optional later integration, not proof that MCP itself orchestrates an agent.

## Completion checkpoint

**Show it:** initialization/discovery/call evidence, error-result handling, unavailable-server diagnosis and your host allowlist/hostile-result tests. Record whether each failure occurred before launch, during protocol exchange or after decoding; an arbitrary exception is not enough to prove the intended boundary held.

**You can now:** separate protocol behavior from trusted authorization and validate denied/hostile/unavailable results. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [compare selective visual integration](../../n8n/review-integration/README.md). Use the root capability prerequisites when deciding whether to proceed.

## Stage defense practice

> [!IMPORTANT]
> Protocol/schema validity does not make a tool result trusted or grant permission. Keep authorization and business validation in the application boundary.

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p08--agents-sdk-and-mcp-interfaces) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
