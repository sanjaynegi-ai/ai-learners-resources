# Chapter 00 — Environment Setup

> **This chapter:** Create and verify a learner-owned Python environment, then prepare your model route.  
> **Estimated study time:** 60–90 minutes, plus installation and model-download time.  
> **Prerequisites:** PowerShell, an editor, and internet access for installation or Python downloads.  
> **Central question:** How do we make sure our application runs with the intended Python and dependencies?  
  

[Workbook index](README.md) · [Next chapter: Foundations](01-foundations.md)

## Learning objectives for this section

- Explain the different roles of uv, the Python interpreter, project metadata, a lockfile, and a virtual environment.
- Install uv or verify an existing installation.
- Locate a Python 3.11 interpreter and inspect the interpreter used by an explicitly selected command.
- Explain why `uv run` is preferable to guessing which global Python will execute a lab.

## 1. Intuition: a recipe and a prepared kitchen

Imagine sharing a recipe with a friend. Naming the ingredients is useful, but a successful repeat also depends on their versions and the equipment used. Your working kitchen is not the same thing as your written recipe.

For our Fernwood assistant, the Python interpreter is the equipment that executes the program. Project metadata declares what the application requires. A lockfile records the resolved package versions. A virtual environment is the project's prepared working environment. uv manages these pieces and launches commands with the appropriate environment.

The analogy has limits: package compatibility and operating-system differences still matter. A lockfile does not guarantee identical model answers, available credentials, or working network services.

### Pause and predict

Your terminal's `python` command reports Python 3.13, but the workbook uses 3.11. Must you uninstall 3.13?

<details><summary>Reveal the reasoning</summary>

No. Multiple Python versions can coexist. uv can locate or download a suitable interpreter and use it explicitly. The important question is which interpreter executes this project, not which one happens to be first on the terminal's PATH.

</details>

## 2. What each component does

| Component | Responsibility | What it does not do |
|---|---|---|
| Python interpreter | Executes Python code; this workbook selects 3.11 | Installing Python does not install every library |
| uv | Manages Python selection, dependencies, project environments, and command execution | It is not a language model or application framework |
| `pyproject.toml` | Declares project metadata, Python compatibility, and direct dependency requirements | It is not a complete record of every installed transitive version |
| `.python-version` | Records the preferred interpreter selection for the directory | It does not itself install Python or replace compatibility metadata |
| `uv.lock` | Records resolved package versions and related resolution information | It contains no API credentials and does not freeze external services |
| `.venv/` | Holds the project's installed interpreter environment and libraries | It is not the portable source of truth to copy into Git |

**Direct dependency:** A library your application intentionally needs. **Transitive dependency:** A library required by another dependency. The resolver finds versions that satisfy the declared constraints together.

The eventual project workflow is: read project requirements → resolve or reuse the lockfile → synchronize the environment → run the command. uv creates or updates project artifacts as needed; merely installing uv does not create a workbook project or lockfile. Project creation is the next section, not a step to repeat here. [uv project workflow](https://docs.astral.sh/uv/guides/projects/)

Normally commit `pyproject.toml`, `uv.lock`, and the project's `.python-version`; do not commit `.venv/` or secrets. A virtual environment isolates libraries, but it is not a security sandbox: code still has the permissions of the user running it.

## 3. Install or verify uv

**Working directory:** Any directory. These commands do not create the learner project.

In PowerShell, check whether uv is already available:

```powershell
uv --version
```

If it displays a version, skip installation. If PowerShell cannot find the command, install uv using one of the following alternatives, then open a fresh terminal.

**Option A — Windows Package Manager, if available:**

```powershell
winget install --id=astral-sh.uv -e
```

**Option B — Astral's official standalone installer:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Choose one method. The standalone command downloads and executes Astral's installer; its execution-policy setting applies to the launched PowerShell process. See the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/) for inspection instructions and other platforms. Updating later should use the installation method you chose.

In the fresh PowerShell terminal:

```powershell
uv --version
Get-Command uv
```

**Expected behavior:** A uv version and the path of its executable appear. The exact version and path vary. This confirms command discovery, not that the application or its dependencies are installed.

## 4. Inspect interpreter selection without creating a project

**Working directory:** Any ordinary personal directory outside another uv project. No learner files are required yet.

Check for a Python 3.11 interpreter:

```powershell
uv python find 3.11
```

If no matching interpreter is installed, install it, then repeat the lookup:

```powershell
uv python install 3.11
uv python find 3.11
```

Now inspect the interpreter actually used by an explicit invocation:

```powershell
uv run --no-project --python 3.11 python -c "import sys; print(sys.version.split()[0]); print(sys.executable)"
```

**Expected behavior:** The first line begins with `3.11.`; the second is the selected Python executable path. A diagnostic about no project may appear with some uv versions and does not invalidate those checks. `--no-project` makes this an isolated interpreter-selection demonstration rather than running a surrounding project. It does not create the planned learner project or establish its dependency environment.

**Explain the command:** `--python 3.11` requests the interpreter family; `python -c` executes the quoted Python expression; `sys.executable` reports the executable used by this process. The Python standard library supplies `sys`, so no LangChain package or provider account is needed.

Record the version and executable in your lab notebook. Do not copy another person's absolute path into your own configuration.

## 5. Understand `uv run` inside a project

Once the next section creates the learner project, run lab commands from its root. There, uv normally checks the lockfile and synchronizes the project environment before launching a command. Manual activation is unnecessary. This can create or update environment/lock artifacts; it is not always a read-only operation. [uv command execution](https://docs.astral.sh/uv/concepts/projects/run/)

**Illustrative fragment — future project command, not a step to run yet:**

```powershell
uv run python first_call.py
```

This means “run this script using the project's environment.” The file does not exist yet. In project labs, omit the demonstration's `--no-project` flag so the project's dependencies are available.

An editor can still point to another interpreter. Later setup will align VS Code with the project's `.venv`; the explicit command above establishes the terminal-side mental model first.

## 6. Troubleshooting and independent check

| Symptom | Diagnostic check | Next action |
|---|---|---|
| `uv` is not recognized | Open a fresh terminal and run `Get-Command uv` | Follow the chosen installer's PATH guidance |
| No Python 3.11 found | Run `uv python find 3.11` | Install with `uv python install 3.11` |
| Python download fails | Read the network/proxy error | Restore access or use an approved existing 3.11 installation; do not change the course version silently |
| Global `python` and uv show different versions | Inspect the explicit invocation's `sys.executable` | Use uv's selected interpreter for the workbook |

**Independent exercise:** Without changing system defaults, show that uv can locate and run Python 3.11. Record the version, path, and why no `.venv` has been required for this standard-library demonstration.

<details><summary>Hint and solution reasoning</summary>

Use `uv python find 3.11`, followed by the explicit `uv run --no-project --python 3.11` inspection command. This task needs only an interpreter and its standard library. A dependency-bearing project will need its own managed environment in the following setup steps.

</details>

## 7. Knowledge checks and revision

### Q1. Which should travel with the project: `uv.lock` or `.venv/`?

<details><summary>Show answer and explanation</summary>

Commit the lockfile. Recreate the environment locally from project metadata and the lock rather than copying machine-specific installed files. Python/OS compatibility still needs validation.

</details>

### Q2. Does installing uv also install LangChain?

<details><summary>Show answer and explanation</summary>

No. uv is the manager. The application declares and installs LangChain dependencies separately when the relevant lesson needs them.

</details>

### Q3. Why inspect `sys.executable` rather than trust the terminal prompt?

<details><summary>Show answer and explanation</summary>

It reports the executable that actually runs the process. Shell defaults and editor selections may differ from the interpreter uv chooses.

</details>

| Remember | Meaning |
|---|---|
| Metadata | Declared requirements |
| Lockfile | Resolved dependency versions |
| Virtual environment | Local installed environment |
| `uv run` | Execute using the selected/project environment |

## 8. Create your learner project with Python 3.11

**Goal:** Create a simple application project with the intended interpreter selected before dependencies are resolved.

**Starting state:** uv is available, the previous interpreter check succeeded, and you have chosen a personal projects directory outside this repository. No API key or LangChain dependency is needed yet. Do not run these commands inside the workbook folder or another uv workspace.

### Step 1 ? Check your location and target name

Open PowerShell in your chosen personal projects directory, then run:

```powershell
Get-Location
Test-Path -LiteralPath ./langchain-learning
```

The second command should return `False`. If it returns `True`, inspect the existing directory before proceeding. If it is your project from an earlier attempt, continue there rather than initializing again. Otherwise choose a different unused project name and adjust subsequent paths consistently; do not delete personal work to follow the lesson.

### Step 2 ? Initialize once

**Working directory:** Your personal projects directory, the parent of the new project.

```powershell
uv init --no-package --python 3.11 --vcs none langchain-learning
cd langchain-learning
```

- `--python 3.11` selects the course interpreter family during creation.
- `--no-package` creates a simple script-based application without a package build system. This keeps packaging and a `src/` layout out of the beginner setup. uv defaults vary by release, so we select this behavior explicitly.
- `--vcs none` avoids initializing Git automatically. Version-control setup and ignore rules will be introduced separately.
- `langchain-learning` is the new directory and project name.

Project creation writes metadata and starter files; it is not a model call and does not install LangChain. See [uv project creation](https://docs.astral.sh/uv/concepts/projects/init/).

### Step 3 ? Inspect what was generated

**Working directory:** The new `langchain-learning` project root.

```powershell
Get-ChildItem -Force
Get-Content -LiteralPath ./pyproject.toml
Get-Content -LiteralPath ./.python-version
```

The simple application layout should include:

```text
langchain-learning/
  .python-version
  main.py
  pyproject.toml
  README.md
```

The generated `main.py` is a starter script, and `README.md` is the learner project's own description. Neither is the workbook file you are reading. With this initialization command alone, `.venv/` and `uv.lock` are not expected yet; later project execution or dependency management creates them as needed. Additional generated details may vary with uv releases.

**Illustrative fragment ? generated metadata to inspect, not a file replacement:**

```toml
[project]
name = "langchain-learning"
requires-python = ">=3.11"
dependencies = []
```

Your actual file also contains fields such as version, description, and readme. Leave them in place. An empty dependency list is correct at this stage.

The `.python-version` file should contain:

```text
3.11
```

### Step 4 ? Distinguish compatibility from selection

| Setting | Question it answers | Meaning here |
|---|---|---|
| `requires-python = ">=3.11"` in `pyproject.toml` | Which interpreter versions does the project declare compatible? | Python 3.11 and newer satisfy this declared lower bound |
| `3.11` in `.python-version` | Which interpreter should uv prefer for this directory? | Select a Python 3.11 patch release |

A compatibility declaration is not proof that every future Python version has been tested. Our course verification baseline remains 3.11. The generated lower bound also does not mean ?use exactly 3.11.? The directory's version-selection file guides that choice. See [uv Python version selection](https://docs.astral.sh/uv/concepts/python-versions/).

For example, changing only `.python-version` to `3.10` would request an interpreter that does not satisfy `>=3.11`. Changing only `requires-python` to `>=3.12` would make the existing 3.11 selection incompatible. Do not make either change in your working project; this is a reasoning exercise.

A family selection such as `3.11` permits different 3.11 patch releases on different machines. Record the actual patch version when validating later labs. The lockfile records dependency resolution; it does not replace interpreter selection.

### Checkpoint and failure reasoning

Confirm all four points before moving on:

- Your terminal is inside the learner project, not this workbook repository.
- `pyproject.toml` declares `requires-python = ">=3.11"`.
- `.python-version` contains `3.11`.
- `dependencies = []` is still empty; no application packages have been added.

| Symptom | Likely cause | Action |
|---|---|---|
| Initialization reports an existing project | The target already contains project metadata | Continue the existing intended project; do not initialize twice |
| `Get-Content` cannot find metadata | Terminal is in the wrong directory or initialization failed | Check `Get-Location` and the initialization output |
| A packaged `src/` layout appears | The explicit layout option was omitted | Check the command used; do not blindly remove generated files |
| Python selection conflicts with compatibility metadata | One setting was changed independently | Restore the documented 3.11 selection and `>=3.11` lower bound |

**Independent exercise:** Explain why a project can declare `>=3.11` while this workbook tests only 3.11. Then identify which file requests the interpreter family. Do not edit either setting to perform this exercise.

<details><summary>Show answer and explanation</summary>

The declared compatibility range and the tested environment answer different questions. The lower bound allows newer versions in principle; it does not certify their dependency behavior. `.python-version` requests the preferred 3.11 interpreter family for these lessons. Later verification records the actual patch version and dependency versions used.

</details>

## 9. Add only the dependency needed now

**Working directory:** Your learner-owned `langchain-learning` project root from Section 8.

Our first lab checks configuration, not model responses. It needs one external package: `python-dotenv`, which reads a local `.env` file.

```powershell
uv add python-dotenv
uv run python -c "from dotenv import load_dotenv; print('python-dotenv import OK')"
```

The second command prints `python-dotenv import OK`. The first updates project dependencies, resolves the lockfile, and installs the environment. You should now see `uv.lock` and `.venv/`. The resolved version may vary; a dependency requirement and a locked exact version are different things.

The package distribution is `python-dotenv`, while its import is `dotenv`. The `os`, `pathlib`, and `sys` modules used below are in Python's standard library and require no installation.

| Capability introduced later | Dependency introduced at that lesson |
|---|---|
| Hosted chat and embeddings | OpenAI provider integration |
| Local chat and embeddings | Ollama provider integration |
| Prompts and composition | Core interfaces used by the examples |
| Manual similarity | NumPy |
| Chunking and persistence | Text splitters and Chroma integration |
| Interfaces, tests, optional graphs/traces | Respective tools |

This is an installation schedule, not an instruction to install the table now. If resolution fails, read the network or compatibility error before continuing. A global installation elsewhere does not install the dependency into this project.

## 10. Create configuration and ignore files

**Working directory:** Your learner project root. Create these files in your own project, not in the workbook repository.

Use your editor to create the files below as UTF-8 text. Alternatively, create empty files with PowerShell first:

```powershell
New-Item -ItemType File -Path .env.example, .gitignore
```

If a file already exists, inspect and edit it rather than overwriting it blindly.

**Complete configuration file — `.env.example`:**

```dotenv
MODEL_PROVIDER=local
OPENAI_API_KEY=
```

`MODEL_PROVIDER` is our application's convention, not a uv setting. It accepts `local` or `openai`. The local default lets this check run without credentials. The blank key documents a field, not a usable credential.

**Complete ignore file — `.gitignore`:**

```gitignore
# Private configuration; keep the safe example shareable
.env
.env.*
!.env.example

# Generated environments and Python caches
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/

# Generated local indexes and logs
chroma_store/
chroma_store_*/
*.log
```

When using Git, commit metadata, lockfile, source, and sample configuration; exclude private configuration and generated environments. Ignore rules do not remove credentials already tracked by Git. If a credential was committed, remove it from tracked content and rotate it.

Check whether your private file exists:

```powershell
Test-Path -LiteralPath ./.env
```

Only if the result is `False`, create it:

```powershell
Copy-Item -LiteralPath ./.env.example -Destination ./.env
```

Keep `MODEL_PROVIDER=local` for the first successful run. Hosted-route learners later set `MODEL_PROVIDER=openai` and enter their key privately in `.env` using the editor. Never put credentials in the example, a terminal command, a screenshot, or a log.

The script below explicitly loads `.env`; the file does not configure every process automatically. Existing environment variables take precedence with `override=False`. See [python-dotenv documentation](https://bbc2.github.io/python-dotenv/).

## 11. Align the editor and verify configuration

### Step 1 — Select the project interpreter

Open the learner project folder in VS Code and install Microsoft's Python extension if needed. Press **Ctrl+Shift+P**, choose **Python: Select Interpreter**, and select the interpreter under this project's `.venv`.

If it is not listed, choose **Enter interpreter path** and select `.venv\Scripts\python.exe` on Windows. The macOS/Linux equivalent is `.venv/bin/python`. Extension labels can change; check the selected executable path. See [VS Code Python environments](https://code.visualstudio.com/docs/python/environments).

Editor selection and terminal location are separate. In an integrated PowerShell terminal, with the learner project as working directory:

```powershell
Get-Location
uv run python -c "import sys; print(sys.executable)"
```

The location should be the project root and the executable should be inside its `.venv`. Continue using `uv run`; manual activation is unnecessary.

### Step 2 — Create the sanity check

**Complete runnable file — `sanity_check.py`:** Create this file in your project root after installing `python-dotenv` and creating the configuration above.

```python
import os
from pathlib import Path
import sys

from dotenv import load_dotenv


def main():
    project_root = Path(__file__).resolve().parent
    load_dotenv(project_root / ".env", override=False)

    provider = os.getenv("MODEL_PROVIDER", "").strip().lower()
    if provider not in {"local", "openai"}:
        raise SystemExit(
            "Set MODEL_PROVIDER to local or openai in your project .env "
            "or environment."
        )

    if provider == "openai" and not os.getenv("OPENAI_API_KEY", "").strip():
        raise SystemExit(
            "OPENAI_API_KEY is missing. Set it privately for the hosted "
            "route, or select MODEL_PROVIDER=local."
        )

    print(f"Python: {sys.version.split()[0]}")
    print(f"Interpreter: {sys.executable}")
    print(f"Provider: {provider}")
    print("Configuration check passed; no model request was made.")


if __name__ == "__main__":
    main()
```

`Path(__file__)` anchors configuration to the script's directory. `SystemExit` stops with an actionable message and nonzero exit code. The key is checked for presence but never printed, including prefixes. This does not validate credentials or billing. Local mode does not verify Ollama; that is a later task.

### Step 3 — Synchronize without updating the lockfile

**Working directory:** Learner project root, after `uv add` generated `uv.lock`.

```powershell
uv sync --locked
uv run --locked python sanity_check.py
```

`--locked` fails if the lockfile is missing or needs updating rather than silently resolving a new one. Synchronizing may change installed packages; it is not read-only. The subsequent locked run keeps that same check. See [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).

**Expected local output** (path and patch version vary):

```text
Python: 3.11.x
Interpreter: <your project>\.venv\Scripts\python.exe
Provider: local
Configuration check passed; no model request was made.
```

### Failure drill and troubleshooting

Temporarily set `MODEL_PROVIDER=invalid` in your private `.env`, rerun, and read the error. Restore `local`, rerun, and confirm success. A shell variable takes precedence: check its presence with `Test-Path Env:MODEL_PROVIDER` if the file change seems ignored. Do not display the whole environment or key values. Use a fresh terminal without that override for the drill.

| Symptom | First check | Repair |
|---|---|---|
| Cannot import `dotenv` | Project and execution command | Run locked sync and the documented uv command |
| Missing or invalid provider | File location and shell override presence | Set `local` or `openai` in the intended configuration |
| Missing hosted key | Private configuration | Supply the key privately or select local mode |
| Editor errors but terminal succeeds | Selected interpreter | Select this project's `.venv` |
| Stale-lock error | Metadata changed after locking | Review the change; deliberately run `uv lock` if intended, then repeat locked sync |

Do not use `--frozen` merely to bypass an unexplained mismatch.

**Independent exercise:** Record the command, interpreter path, selected provider, and failure-drill outcome. Explain what passed and what remains untested.

<details><summary>Show expected reasoning</summary>

The environment can import dotenv and basic configuration satisfies the application's shape requirements. The check does not establish valid credentials, active billing, a running local model, or correct AI responses. Lockfile compatibility is checked, but external services are not frozen.

</details>

**Question:** Why might global Python fail to import a package that `uv run` can import?

<details><summary>Show answer</summary>

The package is installed in the project environment, not necessarily the global interpreter's environment. Align editor and execution with the project interpreter.

</details>

**Question:** Should `.env.example` contain a real key to simplify setup?

<details><summary>Show answer</summary>

No. It documents safe defaults and variable names. Each learner supplies credentials privately; this local configuration check needs no key.

</details>

## 12. Record the dependency baseline

**Verified on 2026-10-10:** The setup lab was executed in an external temporary project, not in this documentation folder.

| Component | Actual verified value | Scope |
|---|---|---|
| Operating system / shell | Windows / PowerShell | Command execution |
| uv | 0.8.3 | Initialization, dependency addition, locked sync/run |
| Python | CPython 3.11.13 | Project interpreter |
| Direct runtime dependency | `python-dotenv==1.2.4` | Import and configuration checks |
| Other third-party runtime packages | None needed by this lab | LangChain integrations are introduced later |
| Ollama client | 0.32.1 | Client command available; server unavailable |

The initializer used the temporary name `explicit-layout`; your project's name is `langchain-learning`. The same explicit initialization options and interpreter family apply. Newer uv releases may produce different auxiliary files, which is why this chapter selects `--no-package` explicitly.

### Why your lockfile may differ

`uv add python-dotenv` resolves a version available and compatible when you run it. Two learners initializing independently on different days can resolve different releases. Each learner's `uv.lock` then records their own resolved graph. A declared requirement such as `python-dotenv>=1.2.4` does not mean every future run upgrades it: uv normally reuses an existing compatible lockfile.

To reproduce the author's direct dependency choice deliberately, use this **optional alternative to the earlier unpinned addition** in your own project:

```powershell
uv add "python-dotenv==1.2.4"
uv sync --locked
```

This pins the direct dependency; it is not a general substitute for sharing and retaining an entire lockfile when a project has transitive dependencies. Do not replace an existing working environment just because its version differs. Investigate a failure and record the difference first. No lockfile or executable project is shipped inside this workbook.

**Working directory:** Learner project root. Record actual versions without displaying configuration values:

```powershell
uv --version
uv run --locked python -c "import sys; from importlib.metadata import version; print(sys.version.split()[0]); print('python-dotenv=' + version('python-dotenv'))"
```

Keep the output, OS/shell, date, and test result in your lab notebook. Your uv version need not equal the author's older installation; if behavior differs, consult the official documentation and record it. `uv sync --locked` detects stale resolution metadata, not differences in model behavior or external services.

## 13. Prepare a local model route

Hosted-route learners should read the distinction between configuration and service health, then use the hosted checklist below. They do not need to download local models. Local-route learners complete the following steps before attempting local model calls in Chapter 02.

### Step 1 — Install and start Ollama

Install the Windows application from [Ollama's official download page](https://ollama.com/download/windows), following the [Windows setup instructions](https://docs.ollama.com/windows). Open Ollama from the Start menu, then open a fresh PowerShell terminal.

**Working directory:** Any directory; Ollama stores models separately from your Python project.

```powershell
ollama --version
Invoke-RestMethod -Uri http://localhost:11434/api/tags -TimeoutSec 10
```

The first command verifies the client. The second checks the local server and lists installed models. An empty model list is a healthy server with no downloaded models; a connection error means the server is unavailable. A client version alone is not proof of service health. See the [model-list endpoint](https://docs.ollama.com/api/tags).

If the application is installed but no server runs, launch the application. For a CLI-only setup, run `ollama serve` in a separate terminal and leave it open. Do not start another server when the application already serves port 11434; an address-in-use error usually means you should check the existing instance.

### Step 2 — Download the two different model types

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text:v1.5
ollama list
```

Use these exact tags in later configuration. `llama3.1:8b` generates text; `nomic-embed-text:v1.5` generates vectors. They are not interchangeable. Record model details with:

```powershell
ollama show llama3.1:8b
ollama show nomic-embed-text:v1.5
```

The library lists approximately 4.9 GB for the chat model and 274 MB for this embedding model. Downloads are not total runtime memory requirements. Allow additional disk space for Ollama, caches, and indexes. Actual RAM/VRAM needs depend on model format, context size, concurrent requests, and hardware; there is no universal guarantee from the download size. Review the [chat model](https://ollama.com/library/llama3.1) and [embedding model](https://ollama.com/library/nomic-embed-text) pages before downloading.

If downloads fail, check connectivity, disk space, and the exact tag. If inference exhausts memory or is unusably slow, reduce competing workloads or use the hosted route. Changing to a smaller model is a separate experiment: record the change and recheck its feature support and quality rather than assuming identical results.

### Step 3 — Check generation independently of LangChain

**Working directory:** Any directory, with Ollama running and the chat model downloaded.  

_This is PowerShell code, not Python code. Run the following code directly on Powershell._
```powershell
$chatBody = @{
    model = "llama3.1:8b"
    prompt = "Explain in one sentence what a Python virtual environment does."
    stream = $false
    options = @{ num_predict = 80 }
} | ConvertTo-Json -Depth 4

$chatResult = Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate -ContentType "application/json" -Body $chatBody -TimeoutSec 180
$chatResult.response
$chatResult.done
```

Expect nonempty explanatory text and `True` for completion. The wording varies. First use can take longer while the model loads. The 180-second timeout is a diagnostic limit, not a promised response time. Do not treat a timeout as proof that the model can never run. See [Ollama generation](https://docs.ollama.com/api/generate).

### Step 4 — Check embeddings independently

```powershell
$embeddingBody = @{
    model = "nomic-embed-text:v1.5"
    input = "Fernwood procedure notes include a verification check."
} | ConvertTo-Json

$embeddingResult = Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/embed -ContentType "application/json" -Body $embeddingBody -TimeoutSec 180
$embeddingResult.embeddings.Count
$embeddingResult.embeddings[0].Count
```

Expect one vector and a positive vector length. This checks response structure, not retrieval quality; avoid copying every vector number into your notebook. See [Ollama embedding generation](https://docs.ollama.com/api/embed).

Keep `MODEL_PROVIDER=local` in your private `.env`. No local provider integration package is installed in this chapter; Chapter 02 introduces the adapter when it is first used. A successful direct service check isolates model/service issues from Python integration issues.

Use `ollama ps` to inspect loaded models. `ollama stop llama3.1:8b` unloads that model; it does not delete the download. Closing the server/application makes local inference unavailable until restarted.

### Hosted-route preparation

In your private `.env`, set `MODEL_PROVIDER=openai` and supply your own key. Rerun the sanity check without displaying the key. Confirm you have access to the chosen model and understand your provider account's billing and usage limits. Actual authentication and model access are verified by the first hosted call in Chapter 02; this chapter's presence check is intentionally insufficient to certify them.

Do not paste a credential into a command to diagnose it. Use the provider's account controls to inspect or replace credentials and review usage. Keep an eye on charges when later exercises repeat model or embedding calls. The local route needs no hosted key, but still consumes local resources.

## 14. Diagnose by failure boundary

| Failure class | Typical evidence | Useful next action |
|---|---|---|
| Configuration missing | Sanity check names a missing provider/key | Correct the private file or intended environment override |
| Authentication rejected | A later hosted API request explicitly rejects credentials | Check the correct account/key; never expose the key in logs |
| Billing, quota, or rate limit | Provider error identifies quota, payment, or request limits | Read the error details; distinguish account funding from temporary throttling |
| Network/service unavailable | Download failure, connection refused, timeout | Separate internet access from local server health; check endpoint and service state |
| Model not installed | Local API reports unknown/missing model | Verify `ollama list` and pull the exact tag |
| Hardware/resource limit | Memory allocation error, severe swapping, model-load failure | Inspect resource usage; reduce workload or choose a suitable route |
| Python integration failure | Import error while direct service checks work | Check project environment and install only the adapter required by that lesson |

An HTTP status by itself is not always the full diagnosis. Quota and request-rate errors can share a status; use the provider's structured error message. Do not solve a resource or billing problem with unbounded retries.

**Production perspective:** Keep the local inference endpoint on its intended local interface. Private files and local models do not automatically make an application secure: prompts, logs, traces, and tools create additional data boundaries. Use fictional content from this workbook for testing.

### Final knowledge checks

**Q1. The configuration script passes, but the hosted API rejects the first request. Is the script wrong?**

<details><summary>Show answer</summary>

Not necessarily. It checked presence and allowed provider values, not credential validity, model access, billing, or connectivity. Diagnose the actual API error at its boundary.

</details>

**Q2. `/api/tags` returns an empty list. Is the server down?**

<details><summary>Show answer</summary>

No. A successful list response establishes server reachability. Download the required models before running generation or embeddings.

</details>

**Q3. Two learners followed `uv add python-dotenv` but have different versions. What should they compare?**

<details><summary>Show answer</summary>

Compare initialization date, requirements, interpreter compatibility, and each lockfile. Independent resolutions can differ. Retain a working lockfile and record actual versions; use the documented exact direct pin only when intentionally reproducing that choice.

</details>



The environment is ready for the next learning problem: what do messages, models, and frameworks actually do? Continue to [Foundations](01-foundations.md), then [Models and Messages](02-models-and-messages.md). Those chapter files are still scaffolds until their implementation phases are completed.

