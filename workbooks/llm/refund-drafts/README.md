# W-LLM-API-01 — Call a model directly, and stay in control of the result

**How do you keep control when a provider returns a slow, incomplete or confidently wrong draft?** QuickCart, our fictional e-commerce platform, needs refund drafts grounded in trusted order facts. This lesson makes the request, bounds and validation visible before introducing a framework.

> **Your goal:** Inspect direct provider requests, validate responses and diagnose failures before comparing prompts.<br>
> **You need:** Complete the linked [LLM foundations](../../../study-guides/llm-foundations/docs/00-how-llms-generate-text.md) and Python prerequisites.<br>
> **Estimated effort:** Reading 25 min; guided walkthrough and runs 60 min; fault drill 20 min; independent extension 45 min; optional live check 20 min. Editorial estimates<br>
> **You will produce:** Bounded call/validation tests, diagnosis records and an independently checked business-rule change.

**Status: Draft.** Detailed starting-state, environment and verification limits remain below.

**Starting state:** this is a separate `api-direct-v1` project, not a file to add to `langchain-learning` or the QuickCart HTTP API. Work in your personal clone/copy, preserve the supplied file tree and lockfile, and keep independent changes and results private. Default reference tests can pass while the independent TODO remains incomplete.

**Your route:** inspect the fixtures and predict outcomes, run offline, trace one request, break and repair a known check, then implement the amount requirement. The optional live run is a separate evidence step, not a prerequisite for practicing control flow.

<details>
<summary>Unit details, prerequisites and verification record</summary>

> **Unit ID:** W-LLM-API-01 · **Capability:** AI-API-01 · **Checkpoint:** `api-direct-v1` (package 0.1.0)<br>
> **Audience:** Experienced backend engineers who have completed the [Python bridge](../../python/README.md) and read [SG-LLM-00](../../../study-guides/llm-foundations/docs/00-how-llms-generate-text.md) and [SG-LLM-01](../../../study-guides/llm-foundations/docs/01-designing-prompts-and-context.md)<br>
> **Central question:** What does your code have to do around a raw model call so that a slow, failing, truncated, refusing or confidently wrong model never reaches a customer as an answer?<br>
> **Effort:** Reading 25 min; guided walkthrough and runs 60 min; fault drill 20 min; independent extension 45 min; optional live check 20 min. Editorial estimates<br>
> **Artifact:** Passing offline tests, a diagnosed fault drill, your amount check passing its acceptance test, and (optionally) a live-check record<br>
> **Status:** Draft. 24 offline tests, six source mutations, the exercise check and the fault drill author-verified. **No live provider call was made by the author**; the OpenAI adapter is verified against official docs and the installed SDK's own types, not a real response<br>
> **Environment:** Windows PowerShell, uv 0.8.3, Python 3.11.13; OpenAI Python SDK 3.22.0, Pydantic 2.13.5 (exact versions in `uv.lock`). Offline by default, with no key and no cost

</details>

QuickCart's agents want first drafts of refund replies (SG-LLM-00's running example). The project exposes a direct SDK adapter and uses a fake provider by default, so you can trace each responsibility without making a paid call:

- looking up facts;
- assembling a delimited request;
- asking for structured output;
- bounding time and attempts;
- telling truncation from refusal from malformed output;
- validating business rules;
- and returning one of three outcomes: `ready`, `needs_agent` or `failed`.

**Intuition:** treat the model like a talented but unreliable remote contractor behind a flaky network. You send a precise work order (the request), you set a deadline, you check the work against your records before it goes out, and you have a plan for when they are late, refuse, or hand back something half-finished. The analogy's limit: a contractor tells you when they are unsure; a model's confidence says nothing about correctness, so your checks must not depend on it.

## How the code is organized

| File | Responsibility |
|---|---|
| `domain.py` | Synthetic orders, tickets and policies from `fixtures/`; in production, systems of record |
| `prompt.py` + `prompts/refund_reply_v1.txt` | Versioned instructions; the request is built in code; untrusted ticket text is neutralized so it cannot close `<ticket>` |
| `schema.py` | The output contract twice: a strict JSON Schema sent to the provider, and a Pydantic model that re-validates on our side |
| `providers.py` | One small result and error vocabulary; `FakeProvider` (offline, scripted faults) and `OpenAIProvider` (official SDK, Responses API) |
| `validate.py` | Business checks: dates must come from the order; no forbidden promises; no model-written order IDs |
| `pipeline.py` | The bounded loop and every outcome decision |
| `cli.py`, `scripts/live_check.py` | Offline runs; a separately triggered, paid live check |
| `diagnose.py`, `compare.py`, `prompts/refund_reply_v2.txt`, `fixtures/eval`, `fixtures/replay` | Lesson 2: layer-by-layer diagnosis and prompt comparison ([W-LLM-API-02](lesson-2-diagnose-and-compare.md)) |
| `prompts/refund_reply_v3.txt` | A **deliberately contaminated** candidate used by the [evaluation harness](../eval-harness/README.md): its examples are copied from held-out cases. Do not use it as a model prompt |

## Setup and verify (offline)

From `workbooks/llm/refund-drafts` in your clone:

**Execution requirements:** recorded author checks used Windows PowerShell, uv 0.8.3, Python 3.11.13; OpenAI Python SDK 3.22.0, Pydantic 2.13.5 (exact versions in `uv.lock`). Synchronization may download packages. Offline by default, with no key and no provider cost. Keep this working directory and environment for every command below; the only paid step is the optional live check, which has its own conditions. No server is started; preserve evidence before cleaning generated files.

**Predict before running:** inspect the synthetic tickets, orders and policies in `fixtures/`. Which tickets lack facts needed for a ready draft? Which should be rejected before any provider call? Record your reasoning before comparing with the output below.

```powershell
uv sync --python 3.11
uv run python -m unittest discover -s tests -v
uv run refund-drafts --all
```

**Expected:** `Ran 32 tests ... OK` (24 for this lesson; 8 support lesson 2). The `--all` summary ends with `{"provider": "fake", "tickets": 5, "ready": "2/5", "needs_agent": "3/5", "failed": "0/5", "provider_calls": 4}`. No key is needed, and nothing leaves your machine.

<details><summary>Explained answer</summary>

T-002 and T-004 come back `needs_agent` with `model_abstained`: the facts needed for an answer are missing, and the prompt gives the model a safe abstain path. T-005 is `needs_agent` with `order_not_found` and **zero provider calls**: the code refuses to let a model guess about an order it cannot find. That is why 5 tickets cost only 4 calls. T-001 and T-003 are `ready`. The fake provider ignores the language field (T-003 should be German), which is a reminder that **the fake tests control flow, not model quality.**

</details>

## Walkthrough: one call, end to end

Read `pipeline.py` alongside this list.

1. **Look up facts first** (`records.orders`). No order means no call.
2. **Cap untrusted input** (`max_ticket_chars`) before spending tokens on it.
3. **Build the request** (`prompt.build_request`): trusted versioned instructions, then `<order>`, `<policy>` and the neutralized `<ticket>`. The prompt version travels with every outcome.
4. **Call within two bounds:** each attempt gets `min(attempt_timeout, time left)`, and backoff never sleeps past the total deadline. In `OpenAIProvider` the request is:

   ```python
   client.responses.create(model=..., instructions=..., input=...,
       text={"format": {"type": "json_schema", "name": "refund_reply_draft", "strict": True, "schema": JSON_SCHEMA}},
       max_output_tokens=..., store=False, timeout=...)
   ```

   `store=False` keeps ticket text out of provider-side response storage. The client is created with `max_retries=0`. The SDK retries connection errors, 408, 409, 429 and 5xx twice by default; leaving that on under our own three attempts would allow up to nine HTTP requests per draft and blur the deadline.
5. **Classify the result before parsing:**
   - `status == "incomplete"` (for example `max_output_tokens`) goes to an agent without retry, because the same limit would truncate again.
   - A refusal content part goes to an agent.
   - Only then is the output text parsed.

   This order follows OpenAI's structured-outputs guide. It is also why the adapter uses `responses.create` with an explicit schema rather than `responses.parse`, whose helper validates the JSON before you can see that the response was truncated.
6. **Validate twice:** `DraftOut` (schema: types, required fields, no extras, real dates), then `validate.py` (business: is this date *this order's* date?).
7. **Decide:**
   - **Retry** transient errors and malformed output while budget remains.
   - **Fail immediately** on permanent errors (401, 400, 404).
   - Otherwise return `ready`, or `needs_agent` with reason codes.

   A `ready` outcome may still list recovered events, such as `["rate_limit"]`, so you can see what happened.

**Pause and predict:** with `--fault timeout --fault timeout --fault timeout` on T-001, what are the status, attempts and reasons? With `--fault auth_error`, how many calls?

<details><summary>Answer</summary>

Three timeouts exhaust `max_attempts=3`: `failed` with reasons `["timeout", "timeout", "timeout", "attempts_exhausted"]`, after real backoff sleeps of 1 s and 2 s. `auth_error` is permanent: `failed` after exactly 1 call, because retrying with the same bad key only burns rate limit. Run both and check. Scripted faults are listed in `providers.FAULTS`.

</details>

## Break, diagnose, repair: the fabricated date

Run:

```powershell
uv run refund-drafts --ticket T-001 --fault fabricated_date
```

**Observed:** `needs_agent` with `refund_date_used_not_in_order` and `reply_mentions_unknown_date`. The draft says "3 business days, by 2026-10-17", while the order says 2026-10-21. The JSON was perfectly valid.

Now, in `validate.py`, remove `check_dates` from `DEFAULT_CHECKS` and run the same command.

**Observed:** status **`ready`**, reasons `[]`, the same fabricated sentence. A schema-valid, confident and wrong promise is now cleared to send. Run the tests: `test_schema_valid_but_wrong_output_is_caught_by_business_checks` fails.

**Diagnose:** structured output guarantees shape, not truth. **Repair:** restore `check_dates`, rerun the command and the tests, and record before and after.

> [!IMPORTANT]
> `ready` means this draft passed the implemented checks. Pattern-based checks can miss unsupported phrasing; it is not a guarantee of policy correctness, language quality or safe automatic sending. Keep that limitation in your evidence note.

**Second drill, on bounds:** change `max_retries=0` to `max_retries=2` in `make_openai_client`. `test_client_is_built_with_sdk_retries_disabled` fails. Explain in two sentences what would have happened to your deadline and your provider bill under a rate-limit storm, then restore it.

## Independent extension: amounts

Support Operations reports a draft that said "your refund of 999.00 is approved". `check_promises` caught the word *approved*, but not the amount. Implement `check_amounts` in `exercises/amounts.py`, following the requirement in its docstring:
- two-decimal amounts must equal the order's `refund_amount`;
- no amounts at all before the refund is issued;
- dates are not amounts.

Write two cases of your own first, then:

```powershell
uv run python exercises/check_amounts.py
```

**Expected:** `amounts: amount checks passed...`. The untouched starter raises `NotImplementedError`. `--reference` runs `amounts_reference.py`; read it only after recording your attempt. The check also runs the full pipeline with your function added, proving an injected "999.00" is caught and a normal draft is still `ready`.

<details><summary>Progressive hints</summary>

1. A regular expression with digits, a `.` or `,` and exactly two digits finds the amounts. Make sure the `21` in `2026-10-21` cannot match.
2. Compare as numbers with a small tolerance, not as strings: `25.00` and `25,00` are the same amount.
3. Return *all* problems that apply; an unissued refund with a wrong amount has two.

</details>

<details><summary>Worked reasoning</summary>

Amounts, like dates, are facts the model has no authority over. The order record is the authority, so the check compares every amount the model wrote against it and treats any amount before issue as premature. This is not a complete defense: "nine hundred ninety-nine" or "€999" without decimals passes this simple check. Name that limitation, and decide whether the safer design is to have your template insert the amount and forbid the model from writing one at all.

</details>

## Optional: the live check (paid)

Mocks test control flow; a real-model run supplies a separate observation. Before choosing this optional route, confirm account/model access, set a spending budget and execution window, and identify who will review every draft. The default run allows up to 15 calls (5 tickets × 3 attempts), each limited to 400 output tokens. Input tokens and retries also cost money; output-token and call-count limits are not a currency spending cap.

```powershell
$env:REFUND_DRAFTS_PROVIDER = "openai"
$env:OPENAI_MODEL = "<a model your account can use>"
# Set OPENAI_API_KEY privately in this terminal; do not type it into files you commit.
uv run python scripts/live_check.py --confirm-paid-calls
```

There is deliberately no default model: names and availability change, so pick one from your provider account. The script refuses to run without `--confirm-paid-calls`. It writes `results/live-<timestamp>.json` with each outcome, the model the API reported, token usage and the prompt version.

**Acceptance properties, not exact text:**
- every outcome is `ready`, `needs_agent` or `failed` with reason codes;
- T-005 makes no call;
- T-004 is not `ready`;
- every `ready` draft states only the order's date;
- T-003 is in German.

Read every draft yourself. Report live results separately from offline tests, as live observations on a stated model and date. **The author has not run this check.**

**Reflect:** which outcome would you have shipped as "success" before this unit: a truncated reply, a refusal, or a schema-valid draft with the wrong date? Where in your current systems does a dependency's well-formed response get trusted without a business check?

## Completion evidence

- [ ] `uv run python -m unittest discover -s tests -v` shows 32 passing tests on your restored copy.
- [ ] The fabricated-date drill: before and after output, diagnosis, repair; and your two-sentence answer for the retries drill.
- [ ] `exercises/check_amounts.py` passes on **your** implementation, with your own cases. Disclose any use of the reference.
- [ ] A note of about 150 words: which outcome does each fault produce, and why is `needs_agent` not a success?
- [ ] Optional: a live-check JSON file with your own review of each draft, labelled as live, with model and date.

## Troubleshooting

| Symptom | Likely cause | Diagnostic and repair |
|---|---|---|
| `Configuration error: Set OPENAI_MODEL...` | The live route was chosen without a model | Set `OPENAI_MODEL`, or unset `REFUND_DRAFTS_PROVIDER` to stay offline. |
| `Configuration error: OPENAI_API_KEY is not set` | The key is missing in this terminal | Set it privately, and never echo or commit it. |
| Live outcomes are all `failed` with `http_401` | Invalid key or no API access | Check the account; a permanent error is correctly not retried. |
| Live outcomes include `http_404` or `http_400` | Unknown model name, or a model without structured-output support | Choose a model your account lists that supports JSON-schema structured outputs. |
| Many `needs_agent` with `incomplete:max_output_tokens` | The output budget is too small for the model, including reasoning tokens | Raise `REFUND_DRAFTS_MAX_OUTPUT_TOKENS` deliberately, and note the cost. |
| A run takes about 3 s with `--fault timeout` | Real backoff sleeps (1 s, then 2 s) | Expected. Tests inject a fake clock instead. |
| `ModuleNotFoundError: amounts` | Run from the wrong directory | Run from `workbooks/llm/refund-drafts` with `uv run`. |

## Cleanup, limits and next step

Preserve your result records and independent evidence first. Remove generated `results/` and `.venv` only from your own project after checking the resolved paths, and unset `OPENAI_API_KEY` in shared terminals. This project provisions no servers or cloud resources; live requests incur provider charges, so review actual usage in your account after the run.

**Limitations:**
- One provider adapter. An Ollama or Bedrock adapter would implement the same `Provider` protocol.
- Synchronous calls only.
- The fake provider cannot judge language, tone or helpfulness.
- Business checks are pattern-based and can be evaded by spelled-out numbers.
- No persistence, idempotency or audit trail for drafts. AI-RELIABLE-01 adds those concerns.

**Sources:** [OpenAI: Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) (strict JSON Schema; check `incomplete` status and refusals before reading output); [OpenAI Python SDK README](https://github.com/openai/openai-python) (timeouts, `max_retries`, default retry conditions, error classes); [OpenAI: Migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses) (the `text.format` shape). Behavior was also confirmed against the installed SDK 3.22.0's types and source. Recorded in the [source ledger](../../../docs/source-ledger.md). All records are synthetic.

## Completion checkpoint

**You can now:** distinguish syntax, schema and business failures and explain the bounded request/response contract. Support that explanation with this module's actual acceptance checks and disclose any unexecuted route.

**Next:** [diagnose and compare prompts](lesson-2-diagnose-and-compare.md). Use the root capability prerequisites when deciding whether to proceed.

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p03--llm-calls-prompts-and-context) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.
