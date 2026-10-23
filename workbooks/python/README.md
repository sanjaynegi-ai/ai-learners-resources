# Targeted Python bridge

**Which of your engineering habits carry over to Python, and which need a different check?** You do not need to relearn programming. You do need proof that Python's validation, state, cancellation and import behaviour work the way your application assumes.

> **Your goal:** Work through the standard Python units in order, skipping any you already know, then prove the behaviour in a normal packaged project.<br>
> **You need:** [Lesson 1 on the start page](../../START-HERE.md#lesson-1--backend-rules-that-ai-work-depends-on), or its skip check answered, and everyday backend ideas such as validation, exceptions and tests.<br>
> **Effort:** About 2.5–3.25 hours for all four notebook units (less for any you skip), plus 90–120 minutes for the package checkpoint. Setup and repairs vary.<br>
> **You will produce:** Tests that show a failure and its fix, and a check that your installed package works.<br>
> **Status:** Draft; notebooks and package checked locally, not yet tried with learners.

Every learner follows the same units in the same order. Each notebook unit below has a **skip check**: one question about a Python behaviour that often surprises engineers from other languages. If you can answer it *and* explain why, move to the next unit. If not, or if you are unsure, do the unit. Years in another language do not mean you already know how Python behaves, so be honest with yourself; nothing is scored. For each unit you do, read the matching part of the [Python concepts guide](../../study-guides/python-engineering-bridge/README.md), then do its exercise straight away. Work on your own copies. All code and examples use made-up QuickCart data; no model, provider or customer data is involved.

**QuickCart** is our fictional online shop. In this bridge, its support tickets carry amounts and tags that must stay valid as they move from input to batch processing. For example, a total of 30 can only be trusted if invalid inputs were rejected and each ticket was counted once. That gives familiar backend jobs a concrete Python boundary to test.

> [!TIP]
> Keep one private route record: the units you skipped and why, the failure you saw in the units you did, your fix and the recheck. A correct skip-check answer you cannot explain is a reason to do the unit.

## The standard route

**Required for everyone:** the W-PY-BRIDGE-04 package checkpoint and then the W-PY-API-01 project, because later delivery and AWS units build on them. **Skippable:** the four notebook units, if their skip checks are easy for you. **Reference:** guide sections you revisit while explaining a mechanism. The API project has its own time estimate, not included below.

| Order / unit | What to open | What you will show, and effort |
|---|---|---|
| SG-PY-BRIDGE-01 / mechanisms | [Study guide](../../study-guides/python-engineering-bridge/README.md), the section for each unit you do | Explain type hints versus runtime checks, input/state/error boundaries and imports; 45–60 min in total, not repeated for every notebook |
| 1 · W-PY-CONCEPT-01 / first validation | [Validation warm-up](01-validation-concepts.ipynb) | Correct totals, rejected invalid data and an own-change task (a cap); 15 min reading and 30 min practice |
| 2 · W-PY-BRIDGE-01 / typing and validation | [Notebook](02-typing-and-validation.ipynb) | Predict what type hints do at runtime, reject malformed tickets and explain the duplicate-ID rule; 30–45 min |
| 3 · W-PY-BRIDGE-02 / async and exceptions | [Notebook](03-async-and-exceptions.ipynb) | Limit how much runs at once, keep results in order, watch timeout cleanup and explain cancellation; 45–60 min |
| 4 · W-PY-BRIDGE-03 / idioms and behaviour tests | [Notebook](04-tests-and-python-idioms.ipynb) | Count a ticket once even with duplicate tags, handle empty input, and expose and fix a regression; 30–45 min |
| 5 · W-PY-BRIDGE-04 / imports and packaging | [Package checkpoint](python-bridge/README.md) | Run tests and the CLI (including an invalid file), then import the installed wheel outside the source folder; 60–90 min plus a 30 min own-change task |

These times are estimates, not measured learner times. Note setup, experimenting and fixing time as well as reading and building. The package checkpoint's own-change task is part of the assignment; a successful reference run is not the whole job.

## Skip checks

Answer each question in one sentence *before* opening the explained answers below the table. A lucky guess does not count: skip a unit only when your answer and your reasoning are both right.

| Unit | Skip check |
|---|---|
| 1 · W-PY-CONCEPT-01 | Can you write a function that adds up whole-number `amount` values from a list of dictionaries, rejects missing, negative, text and `True`/`False` values with specific errors, and show it working on normal, empty and invalid input? |
| 2 · W-PY-BRIDGE-01 | With `def double(amount: int) -> int: return amount * 2`, what do `double("3")` and `double(True)` return? |
| 3 · W-PY-BRIDGE-02 | What is wrong with `try: return int(row["amount"])` followed by `except Exception: return 0`? And when `await asyncio.wait_for(fetch(), timeout=1)` times out, what happens inside `fetch()`, and what does the caller get on Python 3.11? |
| 4 · W-PY-BRIDGE-03 | `def add_tag(tag, tags=[]): tags.append(tag); return tags`. After `add_tag("a")`, what does the second call `add_tag("b")` return? |
| 5 · W-PY-BRIDGE-04 (required; predict only) | Tests pass from the project folder, but `import quickcart_bridge` fails after you install the wheel in a fresh environment. Name two likely causes. |

<details>
<summary>Explained answers</summary>

1. Decide what valid input looks like before adding anything up. `type(value) is int` stops `True` being accepted as the number 1. Amounts 10 and 20 give 30, and an empty list gives 0. Missing, negative, `True`/`False` and text amounts must be rejected, and tests should assert the valid results and expect a specific exception for invalid input. If you could not write and test this from memory in a few minutes, do the unit.
2. `"33"` and `2`. Python does not enforce type hints when the code runs, `*` repeats a string, and `True` counts as the integer 1. To validate, you need an explicit check such as `type(amount) is int`, or a validation library. Why it matters: a typed signature alone can let `"3"` or `True` reach a refund total.
3. The catch-all turns a missing key (`KeyError`), a typo-level bug and invalid text all into a silent `0`. Catch only the errors you expect (`ValueError` and `TypeError` from the conversion), raise your own domain error with `raise ... from err` so the cause is kept, and let unexpected errors through. For the timeout: normally, `wait_for` asks `fetch()` to cancel. `fetch()` receives `CancelledError` at its next `await` and can clean up in a `finally` block. Once cancellation finishes, the caller gets `TimeoutError` (the built-in exception from Python 3.11). The one-second timeout is not a hard stop: cleanup can take longer, and code that ignores cancellation or blocks the event loop changes the result. Why it matters: corrupt input becomes a believable zero, and a timed-out task may not have stopped its side effects.
4. `["a", "b"]`. The default list is created once, when the function is defined, so every call shares it. Use `tags=None` and create a new list inside the function. Why it matters: state leaks between requests that should be independent.
5. Either the tests imported your source folder rather than the installed package, or the module or its data files were left out of the wheel (because of the folder layout, package discovery or package-data settings). Check by installing the wheel in a fresh environment and importing from a different folder. Why it matters: CI can be green while the package you ship is broken. You still do this unit; the prediction tells you what to look for.

</details>

**Example (illustration only):** type hints and cancellation surprised you, but the validation function and mutable defaults did not. Skip units 1 and 4, do units 2 and 3, then the package checkpoint. Note in your route record why you skipped each one, so you know where to return if a later lab surprises you.

### Open your first unit

Open the first unit whose skip check you could not answer with confidence, and read its guide section as you go. If every notebook skip check was easy, go straight to the [required package checkpoint](python-bridge/README.md). Do not skip that checkpoint or the API project: they test packaging and service boundaries that notebook answers alone cannot prove.

## Notebook workflow and state pitfalls

**Before you run anything:** follow the selected notebook's setup notes; the local reference uses Python 3.11 and any compatible notebook editor works. You need no model keys and no paid API calls. Hosted notebook services have their own account, compute and download requirements, and interactive Colab use has not been tested for this route.

1. **Open your own copy** of the selected `.ipynb` file. Keep your outputs and notes outside the public course files.
2. **Read and predict** before running each exercise. Run the earlier cells in order, make the named change and compare the result with your prediction.
3. **Break and repair** the named behaviour. Keep the failure, restore the rule and run the check again.
4. **Try the own-change task (TODO)** before comparing with the reference. Passing the reference cells does not prove your extension works.
5. **Restart and recheck** from a fresh kernel. A green result from an earlier run is not evidence for your current code.

A notebook keeps variables in memory between cells. For example, if one cell creates `tickets` and a later cell filters it, rerunning only the filter can hide how `tickets` was made. Check cell order and leftover variables before you reinstall packages. Inside a notebook, an event loop is already running, so use top-level `await`; the packaged CLI uses `asyncio.run()` instead, once, at program start.

Clear any sensitive output before sharing, and never put keys in a notebook. The course notebooks start with outputs cleared, so the results you see are your own.

### When a run disagrees with your prediction

| Symptom | Check first | What to do |
|---|---|---|
| A name is undefined, or an old result is still showing | Cell order and kernel state | Restart, run the earlier cells in order and look at the fresh output. |
| An async cell says an event loop is already running | Whether you used the notebook or the CLI pattern | In the notebook, use top-level `await`; keep `asyncio.run()` for the packaged program. |
| A test passes but your own-change task is unfinished | Which behaviour the test actually checks | Run the named extension checks and explain the changed requirement before calling it done. |
| Imports work only inside the project folder | Whether the installed wheel contains the module and its data | Follow the [package checkpoint](python-bridge/README.md) and check from a different folder in a fresh environment. |

When you finish, stop your notebook kernel and follow the package workbook's cleanup steps. Keep the evidence you want and remove only your own temporary files or environments.

## Practice explaining your decisions

During your reflection time, pick one [Python/API practice prompt](../defense/practice-bank.md#p01--python-and-api-ownership). Explain the failure, the change you made and the test that would catch it next time, and note any help you used. This is practice; it does not replace a later independent review.

## Completion and next step

- [ ] Explain why `int` type hints alone do not reject invalid input, and show the explicit checks that do.
- [ ] Show collections being transformed predictably, with no double counting and no shared mutable defaults.
- [ ] Show an expected input failure, an unexpected error passed on unchanged, and async cancellation with cleanup.
- [ ] Make your own change to a requirement, write tests for success and failure, and note any help used.
- [ ] Build and install the package, then check an import from outside the source folder.
- [ ] Note which units you skipped and why, so you can return to them if a later lesson needs them.

**You can now:** show runtime validation and async cleanup working, explain what your tests check and confirm that an installed package works outside its source folder. This applies once the units you did and the package checkpoint are complete.

**Next after the package checkpoint:** build the [QuickCart API](quickcart-api/README.md). It is required before the delivery and deployment units. This bridge gives you its data, async, testing and packaging foundation; it is not an HTTP service or deployment evidence, and running a notebook does not prove a service works.

[Previous: start here](../../START-HERE.md) · [Course map](../../README.md#ordered-capability-map) · [Assessment criteria](../../assessments/README.md)
