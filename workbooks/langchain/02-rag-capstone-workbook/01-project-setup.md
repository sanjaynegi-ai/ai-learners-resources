# W-RAG-01 - Create your reproducible workspace

**Can another engineer reproduce the results without inheriting old state?**

> **Your goal:** Create an inspectable private workspace while preserving previous work.<br>
> **You need:** [Project brief](00-project-brief.md), Python 3.11 and uv.<br>
> **Effort:** Setup is part of the 3-4 hour guided/control estimate in the brief; downloads and repairs vary.<br>
> **You will produce:** A private workspace, 21 passing reference tests, one cited answer and source/version evidence. **Status:** Draft; offline reference, unpiloted.

**Starting state:** the repository provides `retrieval-lab-v1` for mechanics and `grounded-v1` for security/answering in one evolving package. These names describe teaching checkpoints, not claimed release tags. If you already have a personal copy, inspect it and preserve its independent changes before deciding whether you need a fresh reproduction.

**Before running:** Windows PowerShell, Python 3.11 via uv and the supplied lockfile. Runtime uses the standard library; initial Python/build-tool downloads may require internet. No key, paid model, server or cloud resource is needed. The commands create a temporary personal copy and result files. Temporary storage can be cleaned by your system: retain important learner work and evidence in a durable private location before ending the session.

For a fresh private copy, from the **course repository root** in PowerShell:

```powershell
if (Test-Path -LiteralPath $env:TEMP/quickcart-rag-learner) { throw "Choose a new destination; preserve existing work" }
New-Item -ItemType Directory -Path $env:TEMP/quickcart-rag-learner
Push-Location workbooks/langchain/02-rag-capstone-workbook/retrieval-lab
Copy-Item -LiteralPath pyproject.toml,uv.lock,src,fixtures,secure-fixtures,security-metadata.json,tests,exercises -Destination $env:TEMP/quickcart-rag-learner -Recurse
Pop-Location
Set-Location $env:TEMP/quickcart-rag-learner
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
uv run grounded-rag ask --query "money back" --output results/answer.json
```

Choose a different destination if that directory exists; do not overwrite prior evidence. The explicit source inventory excludes generated .venv/results directories. Virtual environments must not be relocated and reused.

Expected: 21 reference tests pass. The answer is ready with a source-backed citation. No .env is required; fixture session names alice/bob/supervisor are synthetic local identities, not web credentials. Dependency manifest and lockfile live here; runtime uses the standard library. Initial build tooling/Python download may need internet. Author environment: Windows PowerShell, uv, Python 3.11.13.

Keep code beside instructions and record the source checkout/version, Python version, commands, working directory and reported document/chunk hashes. A copied reference is a worked example; independent competence requires your own changes, diagnosis and defense.

## Verify the workspace you actually ran

Open `results/answer.json` in this copy. Check its status and citation identity/revision/hash, and locate the corresponding synthetic source. Do not substitute the expected 21-test transcript for your actual output. Passing tests establish this reference's local behavior; they do not authenticate fixture users or establish live-model quality.

| Symptom | Check and next action |
|---|---|
| Destination already exists | Inspect prior work; choose a fresh path consistently or resume the existing copy. |
| Missing copy source | Confirm the repository root and explicit file inventory; do not silently omit fixtures or tests. |
| CLI cannot find security metadata | Confirm the current directory contains `security-metadata.json` and `secure-fixtures/`. |
| Test count differs | Record the source revision and inspect the collected tests before comparing with this checkpoint. |

## Check your reasoning

Attempt each question before opening its answer.

**Diagnosis:** You rerun the setup into the same `TEMP` folder after an earlier attempt. What does the first line do, and why does that protect your evidence?

<details>
<summary>Reveal worked reasoning</summary>

It throws because the destination exists. Reproduction must not overwrite the earlier results and notes you will compare against; choose a new destination instead.

</details>

**Decision:** Why does the copy list name source files explicitly instead of copying the whole folder?

<details>
<summary>Reveal worked reasoning</summary>

It excludes generated `.venv` and `results` directories. A virtual environment cannot be relocated safely, and copying old results would mix earlier evidence into the new run.

</details>

## Completion checkpoint

**You can now:** reproduce the reference in a fresh private workspace without disturbing earlier work.

**Show it:** 21 passing tests, `results/answer.json` with a ready status and citation, and recorded source hashes. Cleanup comes at the end of the module in W-RAG-13; nothing keeps running.

**Reflect:** What would another engineer need, beyond your commands, to trust that your 21 passing tests came from this workspace?

**Next:** [W-RAG-02 — Trace the trust boundaries](02-architecture.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
