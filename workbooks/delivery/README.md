# W-ENG-DELIVERY-01 — Deliver the API you can recover

Your API works locally. Can another engineer start the same artifact and recover a broken configuration?

> **Your goal:** Package, check, release and restore the existing QuickCart API.<br>
> **You need:** Complete the [tested ticket API](../python/quickcart-api/README.md).<br>
> **Estimated effort:** 25 minutes reading, 75 guided build/recovery, 45 independent work; first downloads extra. Fits the existing delivery phase, not additional compulsory weeks.<br>
> **You will produce:** Container/configuration identity, compatibility checks, recovery record and cleanup evidence.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Project transition:** return to your personal `workbooks/python/quickcart-api` copy with the completed API evidence. This lesson adds delivery artifacts to that application; it does not package the SDK, MCP or n8n labs. Keep application tests, container checks and configuration recovery as separate evidence.

**Study route:** inspect the runtime assumptions, build and identify the image, verify the bounded local configuration, rehearse failed startup/recovery, then attempt the independent change. The release bundle here is a local artifact; creating it does not publish a release or establish a hosted CI run.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-DELIVER-01 · **Status:** Draft, author-tested locally; GitHub-hosted run and learner pilot pending.<br>
> **Prerequisite:** Complete [W-PY-API-01](../python/quickcart-api/README.md), including its boundary tests. No AI provider or cloud account required.<br>
> **Central question:** Can another engineer run the reviewed artifact, reject a broken delivery, and restore the last compatible state?<br>
> **Effort:** 25 minutes reading, 75 guided build/recovery, 45 independent work; first downloads extra. Fits the existing delivery phase, not additional compulsory weeks.<br>
> **Artifact:** Container ID, reviewed infrastructure diff, schema check, checksummed release bundle, failed-start/repair record and cleanup evidence.

</details>

After this lesson you should be able to separate application correctness from packaging correctness, review a bounded local infrastructure definition, preserve an artifact with its configuration and contract, diagnose startup failure, and explain when rollback would lose state. Acceptance requires all 19 API tests, frozen-schema check, real container smoke, inspected runtime bounds, failed startup, restored smoke, and removal of the dedicated lab containers/network. A copied reference run does not satisfy the independent task.

## Why the passing tests are insufficient

> [!IMPORTANT]
> Restore a compatible image and configuration together. This lab's in-memory tickets and idempotency records are lost when the process is replaced; rolling back an image cannot recover them.

QuickCart's ticket API works in your virtual environment. A colleague receives your source but starts it with missing principals, an incompatible Python, or three workers. The first two fail startup; the third creates three independent in-memory stores. A healthy process can still lose tickets between requests. Packaging must preserve the application's assumptions.

A release is like a sealed equipment kit with an inventory and operating instructions. The analogy stops at mutable state: replacing the kit cannot restore a database or undo a sent payment. Here the API deliberately stores only synthetic tickets in memory, so every replacement loses tickets and idempotency records. **Do not expose this lab to real users.** Durable storage, migrations, authentication operations and real-model quality remain separate outcomes.

Pause and predict: will an old image recover a service whose timeout setting is still zero?

<details>
<summary>Reveal the reasoning</summary>

No. Image rollback without compatible configuration repeats the same startup failure. This lesson preserves and restores both.

</details>

## Exact starting state and supported environment

Use the repository's `api-v1`, package 0.1.0, unchanged application implementation. Packaging/configuration exercises belong in a personal copy of `workbooks/python/quickcart-api`; do not edit the shared reference. All following PowerShell blocks run **from that project directory**, unless explicitly labelled repository root.

Author environment: Windows PowerShell, uv 0.13.1, Python 3.11.13, Docker Desktop 4.93.0 with Linux/amd64 Engine 29.8.1 and Compose 5.5.1. Dockerfile uses Debian Bookworm/Python 3.11.13. CI targets Ubuntu 24.04/Python 3.11.13 and its installed Docker/Compose; that hosted path is pending its first run. Windows containers, ARM, alternate Python and Kubernetes are not verified. Dependencies remain in `uv.lock` and its `requirements-ci.txt` export; install/download access is needed initially. No default paid calls. Docker licensing and GitHub runner/artifact charges depend on your account; review those before organizational use.

Check `docker version` for a Server section and `docker compose version`. Start Docker Desktop with Linux containers if needed. Do not continue after a failed command; check `$LASTEXITCODE` for native commands in PowerShell.

```powershell
uv sync --frozen --python 3.11
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python delivery/check_contract.py
docker build -t quickcart-api:delivery-v1 .
$env:QUICKCART_IMAGE = docker image inspect quickcart-api:delivery-v1 --format '{{.Id}}'
$previousImage = $env:QUICKCART_IMAGE
```

Expected: 19 tests pass and the v1 contract check passes; build exits zero and returns an image SHA-256 ID. Output varies with download/cache state. Record actual commands, versions, source revision (and dirty-tree status) and image ID in a private log. Do not invent an immutable course release tag; none is issued here.

The Dockerfile builds wheels in a separate stage, installs the application and its locked runtime dependencies without network in the final stage, and runs as UID 10001. Test dependencies may be downloaded into the build wheel directory but are not installed unless the runtime dependency graph requires them. `.dockerignore` admits only packaging inputs and the public synthetic principal hashes. Build tools and private environment files are not runtime inputs. Record the resolved base digest; periodic security updates require a new reviewed base, build and smoke run. A fixed Python version alone does not guarantee vulnerability safety or bit-for-bit rebuilds.

## Small infrastructure-as-code exercise: inspect before applying

`compose.yaml` is our local declarative infrastructure: one container and one project network, no volumes, no AWS resources. This is sufficient to learn desired configuration, review and teardown without spending on cloud provisioning. The [AWS SAM exercise](../aws/bedrock-worker/README.md) later applies those habits to IAM and paid resources.

```powershell
docker compose config
docker compose config --format json | Set-Content -Encoding utf8 reviewed-compose.json
docker compose up -d --wait --wait-timeout 60
uv run --frozen python delivery/smoke.py
$containerId = docker compose ps -q api
docker inspect $containerId
```

Before `up`, review the rendered image ID, loopback-only port 18000, one process/worker, 256 MiB RAM, 0.5 CPU, 64 PIDs, dropped capabilities, read-only filesystem, no privilege escalation, no restart loop and two 1 MiB log files. No host credentials, Docker socket or host directories are mounted. `pull_policy: never` prevents deployment silently selecting a remote replacement. `config` is a render/validation operation, **not a complete infrastructure plan** and not proof that limits are enforced. Inspect the running container's `HostConfig` and `Config.User` to establish that evidence.

Walk through the request flow: loopback port 18000 forwards to uvicorn on container port 8000; trusted application code loads synthetic principals and enforces tenant scope before calling the mock provider. The smoke script sends only synthetic requests and verifies health, 401, cross-tenant 404, strict schema 422, idempotency and mock triage. The health check alone establishes only liveness. Synthetic credentials are public teaching values and cannot protect a real service.

Now change only `mem_limit` to `192m` in your copy. Render again, compare with the saved JSON using `Compare-Object` on the file lines, explain the smaller memory margin and review the unchanged port/identity/image. Apply, rerun smoke, and inspect `HostConfig.Memory` for 201326592 bytes. Restore 256m, apply and inspect again. A reviewed source diff plus resolved configuration plus runtime inspection is the evidence; a successful parser alone is insufficient. CPU/RAM/PID limits constrain this container, not total Docker VM or build-cache disk consumption. One worker is essential until shared durable state exists.

## Contract and release bundle

`delivery/openapi-v1.json` freezes the current public API. `delivery/check_contract.py` compares the generated schema exactly: it is deliberately conservative and may reject harmless descriptive changes. It does not prove behavioral or data compatibility; the existing tests cover those boundaries. Review the cause before updating the baseline.

| Change | Decision and rollback consequence |
|---|---|
| Timeout within `(0,10]` seconds | Boot-compatible; changed latency needs measurement and smoke. Preserve old value. |
| Rename/remove principals path or change principal fields | Startup incompatibility; coordinate config with image. Never put real tokens in the bundle. |
| Require a new ticket field or change amount units | Consumer incompatibility; reject until consumers/versioning and schema baseline are explicitly reviewed. |
| Introduce persistence or change stored schema | Old binaries may not read new data. Require migration/backward-reader tests and a recovery plan before rollout. This lab has no database migration. |

In your copy, add a required field to `TicketIn` in `src/quickcart_api/models.py`. Run the schema checker and existing tests: delivery must fail. Restore the source and rerun. Do not repair by blindly regenerating the baseline. A schema change is a design decision, not a snapshot-maintenance chore.

Create an inspectable bundle:

```powershell
New-Item -ItemType Directory -Force release | Out-Null
uv build --wheel --out-dir release
Copy-Item uv.lock,requirements-ci.txt,compose.yaml,delivery/openapi-v1.json release
docker compose config | Set-Content -Encoding utf8 release/compose-resolved.yaml
docker image inspect $previousImage | Set-Content -Encoding utf8 release/image-inspect.json
docker save $previousImage -o release/image.tar
Get-ChildItem release -File | Get-FileHash -Algorithm SHA256 | Format-Table -AutoSize | Out-String -Width 300 | Set-Content release/SHA256SUMS.txt
```

Keep the bundle outside the public repo. Record source revision, dirty changes, configuration, image ID/base digest, Python/tool versions, schema version, test/smoke results and reviewer in a release note beside it. Hashes detect accidental alteration; they are not signatures or evidence that a malicious artifact is trustworthy. Verify hashes after transport, `docker load -i release/image.tar`, inspect the loaded ID against the recorded ID, and use that ID rather than rebuilding for rollback. Wheel timestamps may vary; preserve the tested artifact rather than promising identical rebuild bytes.

## Failed delivery, diagnosis and repair

Save the good image/configuration before beginning. Our deliberate failure uses an invalid timeout without altering application code:

```powershell
$env:QUICKCART_TRIAGE_TIMEOUT_SECONDS = '0'
docker compose up -d --wait --wait-timeout 30
docker compose ps -a
docker compose logs --no-color
```

Expected acceptance property: startup fails, `up --wait` exits nonzero and logs identify `ConfigError`. Diagnose configuration first: the setting must be a finite number in `(0,10]`. Restarting the same image with the same bad configuration cannot repair it. Never log real tokens while investigating.

Restore the reviewed artifact **and** configuration:

```powershell
$env:QUICKCART_IMAGE = $previousImage
Remove-Item Env:QUICKCART_TRIAGE_TIMEOUT_SECONDS
docker compose config
docker compose up -d --wait --wait-timeout 60
uv run --frozen python delivery/smoke.py
```

The reference restoration returns timeout to the known default 0.5. For a real prior release, restore its recorded value explicitly. Expect smoke success; all pre-replacement in-memory tickets are gone. This exercise validates configuration recovery and artifact selection, not zero-downtime deployment, durable data recovery or rollback across a database migration. Record detection, error, hypothesis, change, actual recovery time and lost synthetic state. Release owner decides stop/rollback; application owner confirms contract; infrastructure owner checks cleanup. Here you perform all three roles explicitly.

## Scoped CI without paid defaults

The repository's [QuickCart workflow](../../.github/workflows/quickcart-delivery.yml) runs only for project/workbook/workflow pull-request changes or manual dispatch. Read permission, pinned actions, Ubuntu 24.04, one job and a 15-minute timeout bound the job. It installs locked dependencies, runs 19 tests and the schema check, builds a wheel/container, applies Compose, performs HTTP smoke, saves the tested image and checksums, always attempts teardown, then uploads a successful release bundle for seven days. It does not push images, deploy AWS or call a model. Dependency downloads and Docker Hub access remain network requirements.

Run from repository root for equivalent local verification:

```powershell
python tools/verify_engineering_delivery.py
```

The verifier uses a dedicated project name, checks runtime limits, forces startup failure, restores configuration, saves/loads the image archive, builds a wheel and removes its containers/network. It writes the actual local [verification record](../../docs/review-evidence/engineering-delivery.json). The hosted workflow additionally tests the runner environment and artifact upload; attach its URL/result after an authorized push/run. A local pass is not a fabricated GitHub CI result. No push or remote workflow run occurred during authoring.

## Independent transfer task and self-check

An Operations engineer proposes two replicas and a mandatory `priority` field to accelerate ticket handling. Produce a review rejecting unsafe rollout, then implement a compatible optional priority field **in your personal copy**, with a stable default for old clients. Preserve tenant isolation, strict validation of unknown fields and the mock-only provider. Add a meaningful old-client request test and a new-field validation test. Explain exactly why two replicas remain unsafe with this store.

Submit the schema diff, intentional baseline update reasoning, new passing tests, container smoke and release record; repeat the invalid-config drill and show restoration. Acceptance: old request still works, invalid priority fails, unknown tenant remains forbidden, and no multiworker deployment is claimed. Explain what durable idempotency and shared storage would have to guarantee before replica expansion.

<details><summary>Progressive hints and worked reasoning — open after attempting</summary>

First inspect `TicketIn` and the immutable response `Ticket`; adding only an input field may silently discard it in `TicketStore`. Trace input → stored representation → response before changing the contract. Second choose a bounded allowlist with a default rather than a required field. Third keep the existing store's tenant key and replay semantics: repeated key with a different priority must not silently mutate the ticket. A schema snapshot can identify a shape change but cannot verify those behaviors. Add tests that would fail if priority were discarded or idempotency ignored it. A compatible forward change still needs an old-reader decision: rolling back may lose the new field, and this lab already loses all memory on restart. Document that limitation rather than calling it production-safe.

</details>

Self-assessment: explain the image/config/schema relationship (2), inspect actual bounds and justify one worker (2), diagnose and recover with honest state-loss evidence (2), preserve/check release artifacts (2), and implement/test the unfamiliar compatibility change (2). Require at least one point in every dimension, with tenant isolation, no paid default calls and truthful evidence as non-compensable gates. This is module self-assessment, not a new certification policy. Disclose AI assistance and demonstrate ownership by explaining a small unseen config or schema change.

## Troubleshooting, cleanup and next step

| Symptom | Likely cause | Diagnostic action |
|---|---|---|
| Docker client present, no Server | Engine stopped/wrong container mode | Start Desktop in Linux mode; rerun version. |
| Required image variable error | Missing image selection | Set the reviewed local ID; render `compose config`. |
| Port 18000 already allocated | Another local process/lab | Identify it before changing anything; stop only your own prior lab or review a port change. |
| Container exits immediately | Invalid startup config | Read logs and rendered env; restore config, then image if needed. |
| Schema check fails after library update | Changed generated contract | Review diff/consumer impact; do not auto-accept. |
| Tickets disappear after apply | In-memory store recreated | Expected limitation; never use this for persistent business data. |
| Download/build failure | Registry/network/version availability | Inspect exact failing stage; do not loosen lock to hide failure. |

```powershell
docker compose down --remove-orphans --timeout 10
docker compose ps -a
docker network ls --filter label=com.docker.compose.project=quickcart-delivery-lab
Remove-Item Env:QUICKCART_IMAGE
```

Expect no project containers/network. No volumes/cloud resources were created. Images, release archives, downloaded packages and build cache still occupy local disk; retain the last reviewed image until recovery work is finished. If desired, remove only your exact lab tag with `docker image rm quickcart-api:delivery-v1`; other tags/build cache can retain layers. Do not use global prune commands on a shared machine. Delete only the reviewed personal release directory when its evidence is no longer needed. CI artifacts expire after seven days; archive necessary evidence privately before then.

[Previous on the course map: W-N8N-01](../n8n/review-integration/README.md) · [Course map](../../README.md) · [API project being packaged](../python/quickcart-api/README.md)

## Reference sources

Checked 2026-10-14; public free documentation, no account for reading. These are Reference, not additional compulsory readings. Prerequisite: this lesson's packaging/configuration concepts. Local execution is recorded separately from documentation access.

| Official title/author | Exact focus and purpose | Effort/version boundary |
|---|---|---|
| [Multi-stage builds — Docker](https://docs.docker.com/build/building/multi-stage/) | Use multi-stage builds; separates build inputs from runtime artifact | 5 min; Dockerfile syntax used here |
| [Define services in Docker Compose — Docker](https://docs.docker.com/reference/compose-file/services/) | `mem_limit`, `cpus`, `pids_limit`, `read_only`, `ports`, `pull_policy`; review local bounds | 10 min selectively; tested Compose 5.5.1 |
| [Store and share data — GitHub](https://docs.github.com/en/actions/tutorials/store-and-share-data) | Upload/retention and artifact validation; distinguish preserved output from a rebuild | 5 min; upload-artifact v4 commit resolved through official GitHub API during authoring |

## Measure service overload

Before the completion checkpoint, follow [serving under load](serving-under-load.md) in the same QuickCart API package. It adds 150-210 minutes within phase 4 and produces real loopback HTTP admission, queue, cancellation and recovery measurements, reported separately from virtual-time predictions. The supplied lab uses a cooperative synthetic provider; it does not measure the container or a hosted model.

## Rehearse customer delivery

Follow the [customer integration rehearsal](customer-rehearsal.md): negotiate bounded scope, show a failed and successful integration path, and draft an adoption/workflow-impact plan. Total 75-105 minutes includes 15 minutes replacing the existing P10 stakeholder reflection; net addition 60-90 minutes within phase 4. Carry the same record into capstone discovery/change/handover without repeating a presentation. All customer dialogue/acceptance is simulated and adoption unobserved.

## Completion checkpoint

**You can now:** identify the preserved artifact/configuration, reproduce compatibility checks and recover the declared local service. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** complete [measured serving](serving-under-load.md), then the customer rehearsal linked from it. After saving both records, read [SG-AWS-00 — Bounded Bedrock delivery](../../study-guides/aws-bedrock-delivery/README.md), then follow its companion worker lab. The guide introduces identity, admission and cleanup decisions before any separately authorized paid deployment.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../defense/practice-bank.md#p10--engineering-delivery-and-compatibility) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
