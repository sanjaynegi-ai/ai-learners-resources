# W-PY-BRIDGE-04 — Package the boundary you tested

**Does your code work because it is packaged correctly, or because your source folder is hiding an import error?** Each notebook explored one Python boundary. This required checkpoint brings them together in one testable project, then checks the package another environment would actually install.

> **Your goal:** Prove your package works when installed from a wheel, not only from its source folder.<br>
> **You need:** The [Python bridge exercises](../README.md) you selected, plus basic functions, imports, exceptions and assertions.<br>
> **Effort:** 60–90 minutes to build and check, plus 30 minutes for your own-change task (estimates).<br>
> **You will produce:** A working command-line tool, evidence of a failure and its fix, and a clean import from an installed wheel.<br>
> **Status:** Draft; tests, tool and wheel install checked locally, not yet tried with learners.

**QuickCart** is our fictional online shop. This project takes its made-up support tickets through validation, limited lookups and a local summary. A **wheel** is a Python package file you can install. The key test is whether that package still works once your source folder can no longer cover up missing files.

## Your route through this checkpoint

1. Look around the supplied project, then run its reference tests and command-line tool.
2. In your own copy, add the validation and concurrency faults described below; record what breaks, then fix it.
3. Build the wheel and check it from outside the source folder.
4. Build and test the priority feature on your own before moving on to the API.

> [!TIP]
> Keep a short evidence log: the command, the folder you ran it from, the real result, any failure and your fix. Tests passing in the source folder and a clean wheel import prove different things, so keep both.

## Inspect the supplied starting state

Make your own copy of this project and keep its folder structure. Keep your changes and results outside the public course repository. You can read all the reference code; `exercises/priority.py` is your own-change task (TODO), and a separate reference answer is provided.

**Starting checkpoint:** the supplied `core-v1` package (version 0.1.0). The own-change task is deliberately unfinished: the reference tests passing does not mean you have done it.

| File | What it does |
|---|---|
| `pyproject.toml`, `uv.lock` | Package details, the supported Python version, the pinned build tool and the exact resolved versions |
| `src/quickcart_bridge/models.py` | The typed, unchangeable ticket, the input parser and the totals |
| `src/quickcart_bridge/batch.py` | Limited async calls to a pretend provider, cleanup and results in input order |
| `src/quickcart_bridge/cli.py` | Reads a local JSON file and prints a summary; this is not a service |
| `fixtures/tickets.json`, `invalid-ticket.json` | Two valid tickets, and one with a deliberate `true` amount |
| `tests/test_bridge.py` | Tests for the rules, concurrency, timeout and cancellation, cleanup after failure, and size limits |
| `exercises/priority.py`, `priority_reference.py` | Your own-change task (selecting and sorting priority tickets) and its separate reference answer |

If the difference between type hints and runtime checks, or how async cleanup works, is still unclear, read the [concepts guide](../../../study-guides/python-engineering-bridge/README.md) before the code. Think of a package like a deployable artefact: importing from your project folder is a weaker test than importing from a freshly installed wheel. The comparison stops there: packaging alone proves nothing about how a service behaves.

## Setup and verify a small coherent path

**Before you run anything:** use Windows PowerShell and Python 3.11. It was tested with Python 3.11.13, uv 0.8.3 and the pinned setuptools 80.9.0 build tool. The project needs no third-party packages to run. The first sync may download the pinned build tools; you need no model key and no paid calls. Keep the lockfile and use this project's own environment, not a shared course-wide one. Nothing starts a server or changes anything outside your folder; cleanup of local files is covered at the end.

From the course repository root in **PowerShell**, run the commands below. If you copied only this project, open a terminal in your copy's root folder instead and skip the `cd` line. Check that `pyproject.toml` and `uv.lock` are in the current folder before you sync.

```powershell
cd workbooks/python/python-bridge
uv sync --python 3.11 --locked
uv run python --version
uv run python -m unittest discover -s tests -v
uv run quickcart-bridge fixtures/tickets.json
```

You should see **8 passing tests**, and a summary with count **2**, total **30 units** and a count of **1** for each tag, with the QC-001 and QC-002 lines in order. These are the expected results for the made-up data; how long the tests take will vary. Compare your real output with these; do not copy them into your log as if you had run them.

Read `models.py` and look at one parser failure before you study `batch.py`. The parser checks the shape and the values; type hints help people calling the code but do not validate anything on their own. The batch code limits the batch size, the number of calls at once and the total time, checks what the provider returns, and waits for any unfinished tasks in a `finally` block. That cleanup relies on the tasks cooperating: it cannot undo something an external system already did, and it does not check tenant permissions.

## Trace the boundaries before editing

Follow one ticket through `models.py` → `batch.py` → `cli.py`. The parser accepts or rejects the incoming data; the async collector limits the provider calls; the command-line tool reports a local result or failure. Each job stays separate, even though the example is small.

**Predict:** if the command-line tool prints a valid total of 30, does that prove the built wheel contains the package and its command?

<details>
<summary>Compare your reasoning</summary>

No. The command may be importing your local source folder. The wheel must be installed and run in a fresh environment outside that folder. Testing how the code behaves and testing the package you ship answer different questions.

</details>

## Deliberate failure, diagnosis and repair

**Predict first:** `invalid-ticket.json` sets one amount to `true`. Will the tool exit with zero or non-zero, and which part rejects it: the type hint, the parser or the totals? Write your answer down before you run it.

From the same project folder, run:

```powershell
uv run quickcart-bridge fixtures/invalid-ticket.json
```

You should see a non-zero exit naming `InputError`, without the raw input being printed. `true` must never count as an amount of one. Now, in your own copy, remove the exact-type amount check in `Ticket.__post_init__`, run the invalid-input unit test and watch it fail. Put the check back and rerun the same test and then the full suite. Keep the before and after evidence; never change the invalid file just to make the test pass.

For the async fault, replace the semaphore that limits concurrent calls with unlimited calls in your own copy, and watch the concurrency test fail. Then put the limit back. Making the pretend delay shorter is not a fix, because the rule is about how many calls run at once. Never treat a `CancelledError` as a successful empty result.

## Build and independently inspect the wheel

From this project's folder:

```powershell
uv build --python 3.11 --wheel
```

The wheel is written to the ignored `dist/` folder; nothing is uploaded. To check the supplied project with a clean install, open a terminal at the **course repository root** (the folder that contains `tools/`) and run:

```powershell
uv run --no-project --python 3.11 python tools/verify_python_bridge_project.py
```

This tool builds a wheel in a fresh temporary folder, creates a separate Python 3.11 environment, installs the wheel there, imports it from outside the source folder and runs the valid and invalid examples. It reports what actually happened, then deletes its temporary environment; it never publishes anything.

**What this check covers:** the tool checks the project in the course repository. If your changes are in a separate copy, use the manual steps below on the wheel you built there; the reference passing its check says nothing about your changed package. Replace the example paths with your own interpreter and wheel paths.

### Verify your own wheel outside its source tree

In a new PowerShell terminal, start from a **new, empty folder outside the course repository**. Replace the two example paths with your chosen folder and the exact wheel your build just produced; do not use an old file.

```powershell
Set-Location C:/your-private-workspace/bridge-wheel-check
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe C:/your-project/dist/quickcart_python_bridge-0.1.0-py3-none-any.whl
.venv/Scripts/python.exe -c "import quickcart_bridge; print(quickcart_bridge.__file__)"
```

Use the real wheel filename that `uv build` printed; it may differ from the example above. The printed import path must point inside this fresh environment, not your source folder. Then run `.venv/Scripts/quickcart-bridge.exe` with the full path to your valid file, and again with your invalid file. You should get the same summary as before and a non-zero rejection. Check `$LASTEXITCODE` after each command and stop if anything fails unexpectedly. Do not copy a reference result into your own evidence log.

**Predict:** your tests pass in the source folder, but importing the installed wheel fails. Should you change the input file, add your project folder to the import path, or inspect the built package?

<details>
<summary>Explain the decision</summary>

Inspect the built package and its metadata, fix the problem, then repeat the clean-install check. Adding your project folder to the import path hides the missing content, and changing the input data does nothing for packaging. The goal is an installed package that works without your source folder.

</details>

## Independent transfer, hints and self-check

**Your own-change task:** implement `priority_ids` in `exercises/priority.py`. Reject a threshold that is `True`/`False`, text or negative. Select tickets whose amount is at least the threshold, sort them by amount from highest to lowest and then by ticket ID for ties, and do not change the input. Write tests for normal, empty, tie, exactly-at-threshold and invalid cases before you look at `priority_reference.py`. Explain any test failures and say whether you used the reference or AI help.

From **your project folder**, once you have implemented it, run its separate check:

```powershell
uv run python exercises/check_priority.py
```

To pass: highest amount first, IDs in order for ties, tickets exactly at the threshold included, the input unchanged and invalid thresholds rejected. If you have not touched the stub yet, it raises `NotImplementedError`; that is expected, and the default reference tests do not cover this task.

**Then the requirement changes:** duplicate ticket IDs must be rejected before any provider call, and the batch must tell apart "one ticket's provider call failed" from "the caller cancelled". Decide where the whole-batch check belongs and how the counts in your results change. Do not quietly drop duplicates, and do not report a fallback as a success.

<details><summary>Hints and reasoning, in order</summary>

For the priority sort, use a key of (negative amount, ID). Check the threshold separately from checking each ticket. Track the IDs you have seen before any work starts, so a duplicate cannot trigger an unnecessary call. Expected provider errors can become clear per-ticket status records, but a cancellation should be passed on, and unfinished tasks still need to be waited for. A batch where every item is valid can still break a whole-batch or business rule.

</details>

**Reflect:** which import or packaging mistake would have stayed hidden if you had only run the tests from the source folder?

## Troubleshooting, cleanup and next step

| Symptom | Likely cause | What to check and do |
|---|---|---|
| The package import fails | Wrong interpreter, project not synced, or files missing from the wheel | Check `uv run python --version`, your current folder and the package metadata; compare with the clean-wheel check. |
| The `quickcart-bridge` command is missing | The command is not installed in this environment | Sync this project, or install its wheel into the environment you are using. |
| A notebook says the event loop is already running | CLI start-up code was pasted into a running notebook | Use top-level `await` in the notebook; keep `asyncio.run` for the command-line program. |
| Work keeps running after a timeout | Cancel-and-wait cleanup was removed, or the provider ignores cancellation | Look at the cleanup tests and the note about providers that do not cooperate. |
| Tag counts are wrong | Counting mentions instead of tickets | Rerun the duplicate-tag test and restore the rule of counting each ticket once. |

Nothing keeps running and nothing costs money. Keep your source code, lockfile and own-change evidence. You can delete the generated `.venv`, `build`, `dist` and `*.egg-info` folders from **your own copy**, after checking the paths really are inside that project. Never delete course files or anyone else's work. The verification tool cleans up its own temporary folder automatically.

**You can now:** show that your package imports and runs from a wheel in a fresh environment, and catch a `true`-amount bug and an unlimited-concurrency bug with tests. **Show it:** your test runs, the fault-and-fix evidence and the clean-install check, plus `priority_ids` passing its check.

**Next:** build the tested [W-PY-API-01 QuickCart API](../quickcart-api/README.md). This command-line tool is not a deployed API, so do not describe it as one. [Workbook index](../README.md) · [Course map](../../../README.md)
