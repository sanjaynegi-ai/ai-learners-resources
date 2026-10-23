# W-AWS-01 — Package, review and deliver a Bedrock queue worker

A queued support job fails after its paid attempt is reserved. What is safe to retry?

> **Your goal:** Package and review one bounded Bedrock queue worker, then distinguish local checks from authorized live delivery.<br>
> **You need:** Read [bounded Bedrock delivery](../../../study-guides/aws-bedrock-delivery/README.md) and the linked Python/AWS prerequisites.<br>
> **Estimated effort:** 80 min local; 60–90 min authorized live route; 45 min independent work. Setup/DLQ waits vary; unpiloted estimates.<br>
> **You will produce:** Reviewed package/IAM/cost records, failure/recovery checks and explicit deployment/teardown evidence.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Project route:** use a personal copy of this independent queue-worker package, retaining its lockfile, infrastructure template and synthetic event fixtures. It is not the container from the QuickCart API delivery lesson. Run offline tests/lint/build first; treat live preflight, deployment, inference review and teardown as separate evidence stages.

**Study focus:** trace a job that never starts, one that completes and one whose inference outcome is ambiguous. Keep the original reservation and status for reconciliation. Complete the live preflight below before any paid execution.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Capability:** AI-AWS-01 | **Status:** Draft; offline tests/lint/build only. Live deployment/teardown pending authorization and budget.<br>
> **Prerequisites:** [SG-AWS-00](../../../study-guides/aws-bedrock-delivery/README.md), Python tests and AWS IAM/queue basics.<br>
> **Question:** Can you reproduce a bounded deployment and distinguish a draft, a failed attempt and a safely deleted environment?<br>
> **Effort:** 20 min reading, 60 min local work, 60–90 min authorized deployment/health/teardown, 45 min independent recovery design; installation and DLQ waits vary. Editorial estimates within AWS delivery allocation.<br>
> **Artifact:** Built package/template, IAM/cost review, local results, deployment/recovery/teardown submission or explicitly pending live evidence.<br>
> **Runtime:** Windows PowerShell, uv, Python 3.11.13, Boto3 1.43.113; SAM CLI 1.169.0, cfn-lint 1.57.2. No paid calls in default checks.

</details>

## Starting checkpoint and local verification

`bedrock-worker-v1` provides `src/bedrock_worker/app.py`, `template.json`, tests, pinned SDK lockfile and vendoring requirements. No AWS account or credentials are needed for local tests. Fake credentials exist only inside Stubber tests and are never sent.

From repository root:

**Execution requirements:** Windows PowerShell, uv, Python 3.11.13, Boto3 1.43.113; SAM CLI 1.169.0, cfn-lint 1.57.2. No paid calls in default checks. Keep the following working directory and supported environment; review paid/safety conditions before any live step.

```powershell
Set-Location workbooks/aws/bedrock-worker
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run --no-project --with cfn-lint==1.57.2 cfn-lint template.json
$env:SAM_CLI_TELEMETRY = "0"
uv run --no-project --python 3.11 --with aws-sam-cli==1.169.0 --with pip sam build --template-file template.json --build-dir .aws-sam/build
```

Expected: ten tests pass, infrastructure lint returns 0 and SAM produces `.aws-sam/build/template.yaml`. Adding pip is necessary because uv environments need not include it; the first author build exposed that failure. No Docker is required for this pure-Python build. SAM local emulation, live IAM and Lambda were not run. A build is packaging evidence, not a deployment.

## Inspect code and resources

Read parse → process → DynamoStore.reserve → generate → complete. Schema, identity and budget come before inference. The body cannot choose tenant/model/storage. A DynamoDB transaction reserves one attempt and the immutable hash. An ambiguous result never gets an automatic second paid attempt. Structured logs omit ticket/draft text.

`template.json` creates a queue/DLQ, on-demand DynamoDB table, one Lambda, scoped execution role, seven-day log group, partial-batch event mapping, failure metric and alarm. Mapping processing defaults false. IAM resources are exact queue/table/model/log group; deployment/producer permissions are separate and must be reviewed. The model parameter accepts only this lab's single-region foundation-model route; it does not broaden permission to inference profiles.

Pause: why does a failed job log matter if Lambda Errors stays zero?

<details><summary>Reveal the reasoning</summary>

Partial-batch failures can be returned from an otherwise successful invocation, so Lambda Errors can stay at zero while jobs fail. Inspect the job-failed metric and the DLQ too.

</details>

## Live preflight: complete before any paid operation

> [!WARNING]
> The commands in the live route can incur AWS charges. Complete the approved account, region, model, call/token budget, time window and cleanup-owner preflight before enabling processing; local tests and budget alerts do not authorize or cap total spending.

Live execution requires an explicitly approved sandbox account, region, profile, model ID, artifact bucket/prefix, maximum jobs, token/cost budget, time window and cleanup owner. This authoring task supplied none, so no live calls/deployment were made. Required program deployment competence is not satisfied by this pending record.

Install AWS CLI v2 and use an approved short-lived IAM/SSO profile; do not commit access keys. SAM is invoked at the pinned version through uv above. Confirm the chosen model supports Converse and on-demand inference in the selected region and that account/provider terms/access are already approved. Do not trigger unreviewed marketplace subscription or switch to a wildcard IAM policy to repair access.

Prepare local parameters using your approved values:

```powershell
$Profile = "REPLACE_APPROVED_PROFILE"
$Region = "REPLACE_APPROVED_REGION"
$Account = "REPLACE_12_DIGIT_ACCOUNT"
$Stack = "skillup-bedrock-learner1"
$ModelId = "REPLACE_ELIGIBLE_FOUNDATION_MODEL_ID"
$ArtifactBucket = "REPLACE_DEDICATED_APPROVED_ARTIFACT_BUCKET"
aws sts get-caller-identity --profile $Profile --region $Region
```

Compare the returned account with the approved account before proceeding. The artifact bucket must already be approved, belong to the intended account and support the chosen region. CloudFormation creation, S3 packaging, Lambda/SQS/DynamoDB/logs/metrics/alarms and Bedrock may incur charges; free-tier availability is not assumed. Ten reservations and 128 requested output tokens do not cap total AWS charges. Budget alerts are not guaranteed spending caps.

## One deployment path: reviewed SAM change set

These commands are **live, paid and unexecuted by the author**. From this project directory, after preflight:

```powershell
uv run --no-project --python 3.11 --with aws-sam-cli==1.169.0 --with pip sam deploy --template-file .aws-sam/build/template.yaml --stack-name $Stack --profile $Profile --region $Region --s3-bucket $ArtifactBucket --s3-prefix $Stack --capabilities CAPABILITY_IAM --parameter-overrides ModelId=$ModelId EnableProcessing=false --no-execute-changeset
aws cloudformation describe-change-set --stack-name $Stack --change-set-name REPLACE_REVIEWED_CHANGESET --profile $Profile --region $Region
```

Use the actual change-set name printed by SAM. Review resources/IAM and the disabled mapping; do not paste a sample ID. Only after the authorized review, execute that exact change set and wait:

```powershell
aws cloudformation execute-change-set --stack-name $Stack --change-set-name REPLACE_REVIEWED_CHANGESET --profile $Profile --region $Region
aws cloudformation wait stack-create-complete --stack-name $Stack --profile $Profile --region $Region
aws cloudformation describe-stacks --stack-name $Stack --profile $Profile --region $Region
```

For an update, use the update waiter and review replacement/data-loss implications. Record outputs QueueUrl, TableName, FunctionName and MappingId; keep them private with the approved account/region. A CREATE_COMPLETE stack is not healthy inference.

## Health, one-job smoke test and observability

Verify the function runtime/configuration, disabled mapping, queue redrive/visibility, scoped role and table before enabling. Set variables from actual stack outputs. Enabling admits paid work:

```powershell
aws lambda update-event-source-mapping --uuid $MappingId --enabled --profile $Profile --region $Region
aws sqs send-message --queue-url $QueueUrl --message-body file://job.json --profile $Profile --region $Region
aws dynamodb get-item --table-name $TableName --key file://job-key.json --consistent-read --profile $Profile --region $Region
```

Create `job-key.json` as `{"id":{"S":"A#J1"}}` beside your private evidence (a supplied fixture also exists). Poll with bounded intervals; do not send another event to fix a delayed result. Expect DRAFT_FOR_REVIEW only after a completed, bounded model response is stored. REVIEW_REQUIRED means ambiguous/failed work needing reconciliation. Read the actual draft for quality; status/schema success is not semantic acceptance.

Send the same unchanged job once more under the approved request budget and verify no new model attempt. Inspect BUDGET calls, queue oldest age/depth, DLQ, Lambda duration/throttles and the custom failed-job alarm. The alarm has no notification actions; no emails/messages are sent by the lab. Protect logs/results and enforce seven-day retention assumptions. Do not publish raw real tickets or credentials.

## Failure diagnosis and independent recovery

Local tests simulate malformed/tenant-smuggled input, identity conflict, ambiguous timeout, admission exhaustion and partial-batch failure. The Bedrock/DynamoDB SDK contracts and teardown sequence use Stubber: they validate calls without contacting AWS. In a private local copy, bypass the prior-job guard and observe duplicate-call tests fail; restore it and rerun.

For an authorized cloud drill, an invalid bounded synthetic message should reach the DLQ after the configured receives; this can take multiple visibility periods. Inspect DLQ/review state before redrive. Do not remove job rows to enable another paid attempt. For model-access denial, verify region/model/terms/IAM; do not broaden to Resource=*.

Independent brief: design an operator-approved second attempt for REVIEW_REQUIRED, with a new versioned attempt identity, retained prior evidence and a remaining global budget reservation. Test rejection without approval, budget exhaustion, duplicate approval/redrive, crash after second reservation and changed payload. Keep ambiguous outcomes out of the successful-draft denominator. Hints: separate job from attempt; do not turn a reset counter into permission. Public reasoning is the existing conservative one-attempt policy and the [safe-actions](../../llm/safe-actions/README.md) durable record pattern; your changed integration needs its own tests and defense.

## Teardown and recovery evidence

Stop producers, disable mapping and export the needed synthetic job/DLQ/metric evidence before deletion. The tested cleanup function verifies account/name, disables polling, waits for Disabled, allows 35 seconds for in-flight work, deletes the dedicated stack and waits for disappearance. It is tested with actual SDK Stubbers, **not a live cloud deletion**.

After authorized review of data destruction:

```powershell
uv run python -m bedrock_worker.teardown --stack $Stack --account $Account --profile $Profile --region $Region --execute
aws cloudformation describe-stacks --stack-name $Stack --profile $Profile --region $Region
```

Expected live postcondition: the stack no longer exists; independently verify queue/DLQ/table/function/log group/metric filter/alarm removal. A delete failure is unresolved, not passed. This removes application data. It does not delete the packaging bucket/prefix: inspect the dedicated `$Stack/` artifact prefix and remove only those approved objects using the owner's storage procedure, then verify residual storage/costs. Never recursively empty a shared bucket to satisfy teardown. Preserve artifacts needed by active releases.

For an approved, dedicated artifact prefix, first validate and inspect the exact target. These are live storage operations, unexecuted by the author:

```powershell
if ($Stack -notmatch '^skillup-bedrock-[a-z0-9-]{1,24}$') { throw "Unexpected stack prefix" }
aws s3 ls "s3://$ArtifactBucket/$Stack/" --recursive --profile $Profile --region $Region
```

After the owner confirms those exact objects are disposable: `aws s3 rm "s3://$ArtifactBucket/$Stack/" --recursive --profile $Profile --region $Region`, followed by the same listing. A versioned bucket can retain noncurrent versions/delete markers; inventory and remove them through the approved version-retention procedure or record them as unresolved residuals. Do not claim an empty current-object listing proves complete erasure or zero storage cost.

Submit account/region (privately), source/lock/template hashes, change-set/IAM/cost review, model/version/config, actual deployment outputs, one-job/duplicate/failure evidence, quality review, metric/DLQ observation, reconciliation decision and teardown/residual inventory. Disclose assistance and distinguish local mocks from real-model and deployment evidence. No certification policy is created.

## Troubleshooting and local cleanup

| Symptom | Diagnostic / repair |
|---|---|
| SAM cannot find pip | Use the explicit Python 3.11 SAM invocation with --with pip |
| Jobs accumulate | Check mapping enabled/state, role queue permissions, throttles and oldest age |
| REVIEW_REQUIRED repeats | Attempt reserved before ambiguous failure; reconcile rather than rerun paid work |
| Transaction denied/throttled | Check scoped Get/Put/Update permissions, budget row and DynamoDB response; no inference after failed admission |
| Delete stalls | Inspect mapping state, in-flight work, CloudFormation events and actual residual resources |

Preserve private evidence, then remove only local `.venv`, `.aws-sam` and generated results from this verified project directory. No local daemon is started. Cloud cleanup remains mandatory after any live run; local folder deletion does not remove AWS resources.

[Course map](../../../README.md). Official SAM installation reference: [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html), optional free Reference, 10 min, AWS/Windows prerequisite; checked 2026-10-14. Core AWS sources and reasoning are in SG-AWS-00.

## Completion checkpoint

**Show it:** your offline test/lint/build outputs and reviewed IAM/resource assumptions. If the live route ran, add the actual account/region/model/configuration, job result, human review and verified teardown record. Otherwise mark those stages pending; local packaging is not substitute deployment or model-quality evidence.

**You can now:** separate local packaging, authorized deployment/model evidence, ambiguous attempts and verified teardown. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [SG-OPS-00 — ML lifecycle and application operations](../../../study-guides/application-llmops/README.md), then [W-OPS-01 — release monitoring and incident recovery](../../operations/release-watch/README.md) (AI-OPS-01). Check the root-map prerequisites before you start.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p11--awsbedrock-delivery) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
