# W-CAP-01.4 — Preserve and verify the delivered artifact

**Can another engineer start the preserved artifact and recover compatible configuration?**

> **Your goal:** Verify local delivery while keeping live model review and deployment scope explicit.<br>
> **You need:** [Evaluation](03-evaluation-and-failures.md), the delivery prerequisite and your personal capstone project.<br>
> **Effort:** 4 hours including setup/packaging and separately authorized model review; access/download waits vary.<br>
> **You will produce:** Image/configuration identity, smoke/restart/recovery evidence and labelled live/pending records. **Status:** Draft; synthetic reference and independently reviewed delivery are separate.

The default deployment boundary is a local Linux container bound to loopback. Its synthetic tokens, fixed logical data clock and lack of TLS make it unsuitable for public exposure. This is an inspectable deployment artifact and local deployment exercise, not an AWS-hosted capstone claim. The required AWS competency comes from [W-AWS-01](../../aws/bedrock-worker/README.md); its queue worker is a separate deployment and must not be labelled deployment of this capstone. A final reviewer must explicitly accept the demonstrated deployment scope or require an authorized hosted extension; missing acceptance stays pending.

## Package once and inspect the resolved configuration

**Before the local build:** follow the declared Docker/Linux and Python environment in the [capstone route](README.md). The Docker build uses the course repository root to include the sibling retrieval dependency; subsequent Compose/smoke commands use your capstone project directory. Confirm the named context before executing. Local container processes and volumes require the cleanup below; the separate live-model section has its own account/budget/reviewer prerequisites.

Install Docker Desktop with Linux containers as in the [delivery prerequisite](../../delivery/README.md). From repository root:

```powershell
docker version
docker build -f workbooks/capstone/merchant-support/Dockerfile -t quickcart-capstone:reference-v1 .
Set-Location workbooks/capstone/merchant-support
$env:CAPSTONE_IMAGE = docker image inspect quickcart-capstone:reference-v1 --format '{{.Id}}'
$stableImage = $env:CAPSTONE_IMAGE
docker compose -p skillup-capstone-learner1 config
docker compose -p skillup-capstone-learner1 up -d --wait --wait-timeout 60
uv run --locked python smoke.py
```

Use a unique personal Compose project; the verifier uses another temporary project. Do not continue after a native command fails; check `$LASTEXITCODE`. Expected properties: healthy service, one worker, loopback port 8013, non-root UID 10001, read-only image, state volume, 256 MiB/one CPU/64 PIDs, no extra capabilities, no new privileges and bounded container logs. Inspect actual container configuration, not only YAML:

```powershell
$containerId = docker compose -p skillup-capstone-learner1 ps -q support
docker inspect $containerId
docker compose -p skillup-capstone-learner1 restart support
docker compose -p skillup-capstone-learner1 up -d --wait --wait-timeout 60
uv run --locked python smoke.py
```

The repeated action maps to the same durable effect. The volume preserves approvals, deletions and reservations; do not reset it to hide exhausted budgets. Schema changes require migration/backward-reader tests; reference-v1 has no migration. The root-context Dockerfile copies only the two required source trees, reviewed fixtures and hashed dependency export. Dockerfile-specific ignores exclude credentials/generated state. Verify that your own artifact contains no private files before export. Source is copied directly rather than installed as wheels inside this lab image; dependency export is locked/hashes checked.

## Release and configuration recovery

From the project directory, preserve the actual artifact and compatible configuration in a new `release/reference-01` directory outside public submissions if it contains operational metadata:

```powershell
New-Item -ItemType Directory release/reference-01
docker save $stableImage -o release/reference-01/image.tar
Copy-Item uv.lock,requirements.txt,compose.yaml release/reference-01
docker compose -p skillup-capstone-learner1 config | Set-Content -Encoding utf8 release/reference-01/resolved.yaml
docker image inspect $stableImage | Set-Content -Encoding utf8 release/reference-01/image.json
Get-ChildItem release/reference-01 -File | Get-FileHash -Algorithm SHA256
```

Record source revision/dirty work, retrieval source hashes, image ID/base digest, locked/runtime/tool versions, contract/DB schema, results and reviewer decision. Checksums detect changes, not authorship or approval. Rebuilding under the same tag is not restoration of the same artifact.

Deliberate delivery fault: set `$env:CAPSTONE_IMAGE = 'quickcart-capstone:missing-artifact-exercise'`; run `docker compose -p skillup-capstone-learner1 up -d --pull never` and record the expected nonzero result. Diagnose the missing image rather than widening registry access. Restore `$env:CAPSTONE_IMAGE = $stableImage`, rerun `up --wait` and smoke. This fault may leave the old container serving; report that fact rather than inventing an outage. Also run the provider incident in chapter 05 to demonstrate actual application failure and halt.

For transport recovery, `docker load -i release/reference-01/image.tar`, verify the loaded ID, restore recorded configuration and rerun smoke. Do not restore a stale DB backup that re-enables revoked users or deleted policies. Stop writers and use SQLite's backup API for a consistent snapshot; a copied live `.sqlite` file is not a verified recovery plan. A database restore requires review of all deletions/effects since the snapshot. A payment service would additionally need external reconciliation; this project has local simulated effects only.

## Real-model evidence: separate paid step

The first author live attempt on 2026-10-15 was authorized separately and **denied by IAM**; no model response was obtained. [Follow-up evidence](../../../docs/review-evidence/capstone-live-attempt.json) records one attempted call and seven unexecuted cases. Before any new call, obtain the approved sandbox account/profile, region, exact eligible Bedrock model, IAM scope, model terms/access, maximum calls/output tokens, price source/date, active time window, reviewer and cleanup owner. Use the [AWS preflight](../../aws/bedrock-worker/README.md#live-preflight-complete-before-any-paid-operation) to verify account/region/access. No marketplace subscription, cloud deployment or spending is authorized merely by running local tests.

From this project directory with an approved short-lived profile and region already configured, run only the approved split/model:

```powershell
uv run --locked python -m merchant_support.evaluate --split heldout --live --confirm-paid-calls --model REPLACE_APPROVED_MODEL_ID --out runs/live-heldout-01.json
```

Reference held-out has at most five provider calls, each with 256 requested output tokens, one SDK attempt and a 12-second local deadline. Development adds at most two calls if separately approved. No automatic reruns. Prompt/context is bounded; token counts still depend on model tokenizer and actual service usage. Local deadline kills/reaps the child process; remote work and charges may continue. Budget alerts do not guarantee spending caps. Evaluation uses a fresh local DB per case to isolate cases; this bypasses a persistent global budget across CLI invocations, so the explicit run/call budget and operator oversight remain essential.

Preserve real per-case usage and failures. The report kind is `real-model-unreviewed`, and semantic review remains pending. A human must inspect each actual answer against expected authorized policy and usefulness; retain reviewer/date/labels/disagreements and exact evaluation/code/model/configuration hashes. These public narrow controls alone cannot establish broad semantic competence: add representative independently reviewed fresh cases under a fixed label policy, disjoint from prompt development. Report latency, coverage, abstention, failure and estimated costs using approved current prices, plus uncertainty and human capacity. Never label the synthetic provider results as real-model evidence.

On access/configuration rejection, the CLI now halts at the first `AccessDeniedException`, `ValidationException` or `ResourceNotFoundException`; unexecuted cases remain explicit rather than being scored as passes. Each call clears prior token usage, so an unsuccessful request cannot inherit a previous call's accounting. Child errors export only bounded service categories, never exception strings containing account/user/request data.

For the recorded in-region Nova Micro denial, [the example IAM statement](bedrock-invoke-policy.example.json) limits `bedrock:InvokeModel` to that one foundation-model ARN. It is **a review artifact, not an applied account change**. An authorized IAM administrator must inspect the principal, SCPs/boundaries/explicit denies and model access before applying any appropriate change. `ListFoundationModels` is not required for this known-model invocation and is not granted by the example. Do not broaden to wildcard inference or silently choose a cross-region model. The [official model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html) identifies the model/region/API; the [Converse API reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) identifies the InvokeModel permission. No IAM changes were made by this task.

## Cleanup

Stop producers and preserve needed synthetic evidence, then from the project directory:

```powershell
docker compose -p skillup-capstone-learner1 down
docker ps -a --filter label=com.docker.compose.project=skillup-capstone-learner1
docker volume ls --filter label=com.docker.compose.project=skillup-capstone-learner1
```

`down` preserves the state volume. If the dedicated personal exercise state is disposable, inspect the exact project/volume name, then run `docker compose -p skillup-capstone-learner1 down --volumes` and verify that project's containers/network/volume are gone. This intentionally destroys synthetic actions/approvals/deletions/budget history; never do it to bypass a live ledger. Preserve release artifacts needed by active learners. Avoid global prune commands. No AWS resources are created by the real-model CLI; any resources from the separate AWS workbook require its own teardown and residual-cost checks. Local build images/cache consume disk until deliberately removed.

Next: [operations/handover](05-operations-and-handover.md). [Route](README.md) · [Sources and versions](sources.md)
