# W-N8N-01 — Integrate a review event without duplicating the application

A visual workflow retries an ambiguous review event. Will it create the review twice?

> **Your goal:** Integrate selectively while Python owns schema, identity and durable event admission.<br>
> **You need:** [W-LLM-ACT-01 — safe actions](../../llm/safe-actions/README.md) (idempotent effects) and a tested Python API such as [W-PY-API-01](../../python/quickcart-api/README.md).<br>
> **Estimated effort:** 20 min reading, 40 min guided, 20 min diagnosis, 45 min independent change; installation/download time varies. Editorial estimates within existing integration allocation.<br>
> **You will produce:** Native workflow execution, idempotent retry/denial evidence and a selective-retry extension.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Project route:** start a personal copy of this independent review-integration lab. Python owns the review contract and ledger; n8n routes the synthetic event. Verify Python first, then run the imported workflows in an isolated n8n profile, then attempt selective retry. The editor walkthrough is additional evidence; CLI execution does not certify its appearance.

**Local port check:** this service and the earlier QuickCart API examples both use port 8765. Stop your own earlier lab server before starting this one, then verify the expected service. Do not terminate an unrelated process just to free the port.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-AUTOMATE-01 | **Status:** Draft; actual CLI workflows and five Python tests verified, unpiloted; editor/UI not inspected<br>
> **Prerequisites:** Python API/tests and [idempotent safe actions](../../llm/safe-actions/README.md)<br>
> **Question:** When an integration retries after a lost response, does it create another review?<br>
> **Effort:** 20 min reading, 40 min guided, 20 min diagnosis, 45 min independent change; installation/download time varies. Editorial estimates within existing integration allocation.<br>
> **Artifact:** Imported visual workflow, HTTP/event evidence, failure/repair note and visual-versus-code decision.<br>
> **Environment:** Windows PowerShell, Python 3.11, Node 24.18.0, n8n 2.43.5. Synthetic local data only; no AI model, messaging, payment, external automation account or paid operation.

</details>

## Why this integration exists

QuickCart needs an operator-visible bridge from a support event to a Python-owned review service. n8n supplies visual wiring and connector/execution inspection. Python owns schema validation, trusted tenant binding, idempotency and admission. Rebuilding RAG, authorization or model evaluation inside n8n would add a second application to maintain without a demonstrated requirement.

Think of a delivery conveyor: routing a parcel is different from deciding its contents or authorizing a refund. A successful HTTP response means the review record was accepted, not that a person reviewed it or a customer received an answer. The routing function here is deliberately synthetic keyword logic, not an AI classifier.

**Predict:** Python commits an event, then returns 503. Should the retry use a new event ID?

<details><summary>Reveal the reasoning after the drill</summary>

No. A stable tenant/event identity must describe the same immutable event, so the committed review is reused rather than created twice.

</details>

## Exact starting checkpoint

`review-integration-v1` contains:

| File | Responsibility |
|---|---|
| `review_service.py` | Loopback HTTP service, strict bounded input, synthetic trusted key-to-tenant binding and SQLite review/attempt records |
| `create_workflows.py` | Builds native n8n Manual Trigger → Set → HTTP Request JSON, with two tries and a fixed event identity |
| `workflows/happy.json`, `retry.json`, `denied.json` | Inspectable importable workflows; no external credentials or active triggers |
| `test_service.py` | Duplicate/restart, identity, malformed input, key conflict and ambiguous-failure tests |
| `package.json` | Pins n8n; keep a successful npm-generated package-lock.json with learner evidence |
| `.env.example` | Optional editor configuration placeholders; not real/deployable secrets |

Do not use reference-only sample applications. Preserve learner changes before regenerating workflow JSON.

## Setup and verify Python first

From repository root, PowerShell:

**Execution requirements:** Windows PowerShell, Python 3.11, Node 24.18.0, n8n 2.43.5. Synthetic local data only; no AI model, messaging, payment, external automation account or paid operation. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/n8n/review-integration
uv run --no-project --python 3.11 python --version
uv run --no-project --python 3.11 python -m unittest test_service -v
uv run --no-project --python 3.11 python review_service.py
```

These commands explicitly select Python 3.11; do not infer the interpreter from your editor. Five tests pass. The server binds **127.0.0.1:8765**; Ctrl+C stops it. It uses `results/reviews.db`. In another terminal at the same directory:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/health
node --version
npm.cmd ci --no-audit --no-fund
```

Wait for installation to finish before running n8n; partially installed files are not a usable runtime. No global npm installation is needed. The framework has a large dependency tree and may emit peer/deprecation warnings; preserve the actual install outcome. A successful install and lockfile do not certify every dependency or a supported production platform.

The committed lockfile pins the tested graph. `allowScripts` approves only `sqlite3@5.1.7`, whose native prebuilt-install/rebuild script was inspected and used for the CLI database. Do not blanket-approve unrelated install scripts. If your npm reports SQLite as pending, inspect that exact package script, run `npm.cmd approve-scripts sqlite3`, then `npm.cmd rebuild sqlite3`; preserve any platform-specific build failure. The author install took about seven minutes; this is an observation, not a learner timing promise.

Set an isolated n8n profile for this lab, avoiding any personal instance database:

```powershell
$env:N8N_USER_FOLDER = Join-Path (Get-Location) "results/n8n-profile"
$env:N8N_DIAGNOSTICS_ENABLED = "false"
$env:N8N_PERSONALIZATION_ENABLED = "false"
$env:N8N_VERSION_NOTIFICATIONS_ENABLED = "false"
node node_modules/n8n/bin/n8n --version
node node_modules/n8n/bin/n8n import:workflow --input=workflows/happy.json
node node_modules/n8n/bin/n8n execute --id=reviewE1
```

The pinned CLI rejects the old execute --file flag: import first and use ID. The commands mutate only your isolated local workflow database. No workflow is published, no webhook is exposed, and no external messages are sent. n8n's admin CLI is not an authenticated tenant API.

**Author execution:** [Actual n8n CLI evidence](../../../docs/review-evidence/n8n-runtime.json) records import/execution of all three workflows in a new temporary profile on Node 24.18.0/n8n 2.43.5. Happy and retry paths succeed, RETRY1 has two attempts and one review, denied execution exits 1, and the final ledger has two reviews. Docker's engine was unavailable; no Docker or editor/UI verification is claimed. The verifier closes the loopback server and removes its isolated databases after recording results.

For the visual walkthrough, start the local editor with `node node_modules/n8n/bin/n8n start` using the same isolated profile and loopback listen address from `.env.example`. Complete any local owner setup, import the JSON and inspect the three nodes. This editor/UI path requires separate manual verification; a CLI or contract replay is not evidence of an inspected UI. Do not publish the workflow or expose it through a public tunnel.

## Inspect the visual handoffs

Follow Manual synthetic event → Synthetic envelope → Python review boundary. The Set node creates event_id, ticket_id and text. HTTP Request sends JSON to a fixed loopback URL with the public synthetic header `X-Lab-Key: synthetic-lab-A`.

This key is an intentionally public lab fixture, not production authentication. Tenant comes from the server-owned mapping and cannot be selected by payload text. Unknown fields (including a smuggled tenant), invalid sizes and conflicting payloads under an existing event key are rejected. A production connector needs real credential storage, identity/tenant binding, least privilege, network/TLS controls and key rotation; none is implied by this local demo.

The HTTP node waits up to 1,500 ms for its configured response stage, attempts at most twice, waits 500 ms between attempts and has a workflow execution timeout of 15 seconds. These are distinct controls, not a guaranteed end-to-end deadline for every failure mode. Generic Retry On Fail can also repeat a permanent 403 once; the denied fixture demonstrates that waste without accepting a review. Selective transient retry is the independent extension.

## Failure, repair and regression

Import `workflows/retry.json` and execute ID `reviewRETRY1`. The service deliberately commits first and returns 503 only on its first RETRY1 attempt. The second request uses the same event ID/payload and gets an accepted duplicate. Verify one review record for RETRY1 and two attempts. Reexecuting the workflow must not create another review.

Import `workflows/denied.json` and execute ID `reviewDENIED1`. The wrong header produces 403, no accepted review and a failed execution. Inspect the HTTP error, not merely whether a node displayed output. Repair by restoring the intended public fixture header in a copy; do not weaken server authorization or invent a new event ID to bypass a conflict.

The default success fixture uses E1. Reusing E1 with changed text produces 409; a legitimate changed event requires its own immutable identity and source record, not an ad hoc retry key. Inspect test_key_payload_conflict before changing this rule.

Run the [HTTP contract verifier](../../../tools/verify_n8n_contract.py) from repository root with `uv run --no-project --python 3.11 python tools/verify_n8n_contract.py`. It consumes the same workflow settings and exercises real loopback HTTP, but is **not n8n runtime execution**. The [evidence record](../../../docs/review-evidence/n8n-contract.json) distinguishes those boundaries. Keep failed and repaired outputs; never fabricate a UI or n8n execution from this Python replay.

## Independent requirement and decision

Change the retry policy: retry only a transient 503, at most once; a 400/403/409 must fail immediately. Keep the same event ID across retries. Build an explicit status/condition branch or Python-owned retry endpoint rather than treating every error as transient. Add acceptance evidence showing 503→200 and one review, 403 with one request and zero reviews, and unchanged 409 conflict behavior. Inspect the exact node result shape before writing expressions.

<details><summary>Hints and worked reasoning, after your attempt</summary>

A generic Retry On Fail setting does not express your policy. Inspect status codes without crediting non-2xx as success, then gate the retry. The worked design preserves idempotency and bounds while moving eligibility into an explicit tested branch.

</details>

Your exported JSON, actual runtime trace or disclosed unavailable-runtime record, tests and a 200-word decision are the artifact.

Compare a Python function/queue consumer with n8n. Visual integration earns its place when operators need connector visibility and controlled workflow changes. Python remains preferable for core authorization, nuanced retry policy, tests and model-quality evaluation. Assign owners for payload/schema versions, credentials, failed executions, review staffing, backups and dependency updates. n8n's own version is not a version of your business contract.

## Troubleshooting, retention and cleanup

| Symptom | Diagnose / repair |
|---|---|
| Connection refused | Confirm Python health endpoint and URL/port; Docker localhost is a different network context |
| 403 | Inspect intended fixture header; never retry indefinitely or log real credentials |
| 409 | Same key with changed payload; inspect event provenance |
| Import/runtime fails | Preserve exact Node/n8n/install error; Python replay is not a runtime pass |
| Workflow starts but no review completes | Distinguish accepted queue record from completed human work |

Execution records may contain event bodies. This lab uses synthetic input, disables successful execution retention and keeps failed runs for diagnosis. Production access/retention/pruning need explicit review; n8n execution history is another stored-data surface.

Stop both Python and optional n8n editor with Ctrl+C. Preserve private evidence and verify your lab working directory before removing generated results or node_modules. Removing results destroys the SQLite review ledger and n8n profile; it is a fixture reset, not incident recovery. There are no cloud resources or ongoing paid operations. Local compute/download/storage still cost resources.

## Official sources

Checked 2026-10-14. Optional **Reference**, free, 10 min each, HTTP/Node prerequisite: n8n [npm installation](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-npm.md), [server CLI](https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line.md), [HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest), timeout/retry configuration. No vendor workflow or external repository script is copied/executed as a lesson. Core instructions above are self-contained.

## Completion checkpoint

**Show it:** the isolated workflow/profile identity, Python ledger entries and attempts for happy/retry/denied cases, plus your selective-retry tests. Label CLI and editor observations separately. An accepted review event is pending human work, not a reviewed outcome or a customer response.

**You can now:** explain workflow versus application ownership and show idempotent retry/denial evidence. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [package and recover the API artifact](../../delivery/README.md). Use the root capability prerequisites when deciding whether to proceed.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p09--selective-n8n-integration) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
