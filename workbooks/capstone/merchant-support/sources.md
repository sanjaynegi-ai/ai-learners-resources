# Source and version record

Checked 2026-10-15 by accessing the official pages below; access is not proof of live integration. All are **Reference**, free web reading, no required external homework. Core instructions are self-contained. Initial SDK/package downloads require internet; AWS runtime calls require approved account/access/billing. No third-party code or diagrams copied. The earlier repository modules are reused with local attribution in README/design.

| Resource / author | Exact focus and purpose | Optional effort / prerequisite / compatibility |
|---|---|---|
| [Converse API — AWS](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) | `messages`, `system`, `inferenceConfig`, `stopReason`, response `usage`, InvokeModel permission; verify adapter request/response shape | 10 min; AWS/SDK prerequisite; Boto3 1.43.113 pinned in lock; model/region support still separately checked before live use |
| [Lifespan Events — FastAPI](https://fastapi.tiangolo.com/advanced/events/) | Async lifespan creation/cleanup of request-owned resources; avoid cross-thread SQLite test setup | 5 min; async API prerequisite; FastAPI 0.142.1 locally tested |
| [Use Compose in production — Docker](https://docs.docker.com/compose/how-tos/production/) | Single-host deployment/configuration model and environment differences; local Compose is not a hosted-service acceptance claim | 5 min; earlier delivery prerequisite; Engine 29.8.1/Compose 5.5.1 Linux/amd64 locally checked |
| [Nova Micro model card — AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html) | Model ID, Converse and in-region us-east-1 support for the separately authorized live attempt | 5 min; AWS prerequisite; accessed 2026-10-15; actual account invocation denied by IAM, not model-quality evidence |

The [operations guide source ledger](../../../study-guides/application-llmops/README.md#sources-and-maintenance) covers incident/telemetry principles, and the [retrieval workbook](../../langchain/02-rag-capstone-workbook/README.md) explains the reused curated RAG contract. The [AWS guide](../../../study-guides/aws-bedrock-delivery/README.md) covers approved account/IAM/resource reasoning. Price values in this module are explicitly hypothetical, not source-derived current provider prices.

Maintenance owner: repository maintainer until assigned. Weekly broken-lab corrections, monthly dependency/source/model-support checks, quarterly outcome/workload review. Preserve cohort locks and artifact references; do not silently swap provider/model or loosen gates. No global style change was needed: canonical workbook, evidence and diagram rules already cover this module.

[Route](README.md)
