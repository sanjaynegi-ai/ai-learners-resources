# W-PY-API-01 — A tested HTTP API that keeps its boundaries

**Which guarantees does a web framework give you, and which must your own code and tests still provide?** The Python package you just built now becomes a small local web service. The important part is keeping its rules intact once requests, logins and retries start arriving from outside.

> **Your goal:** Use an API to test input validation, keeping merchants' data apart, safe retries and a time-limited call to a slow service.<br>
> **You need:** The [package checkpoint](../python-bridge/README.md), plus everyday HTTP, bearer-token login and retry ideas from your backend work.<br>
> **Effort:** 20 minutes reading, 60 minutes building and 45 minutes for your own-change task (estimates).<br>
> **You will produce:** Evidence of two failures and their fixes, a tested supervisor-only delete endpoint and a short note on where each rule is enforced. **Status:** Draft; checked locally with a mock classifier, not yet tried with learners.

<details>
<summary>Reference: checkpoint, tested versions and verification record</summary>

> **Unit ID:** W-PY-API-01 · **Capability:** AI-PY-01 · **Checkpoint:** `api-v1` (package version 0.1.0)<br>
> **Audience:** Experienced backend engineers who have finished the [Python bridge](../README.md)<br>
> **Central question:** Which guarantees does a Python web framework give you, and which must your own code and tests still enforce?<br>
> **Your goal:** Build and test an API whose validation, authentication, tenant isolation and idempotency hold even when a client misbehaves.<br>
> **Prerequisites:** [W-PY-BRIDGE-04 package checkpoint](../python-bridge/README.md); HTTP status codes, bearer authentication and idempotent retries from your backend experience<br>
> **Reading / build / independent effort:** 20 / 60 / 45 minutes, estimated; not timed with learners<br>
> **Artifact:** Passing tests, two diagnosed fault drills, a supervisor-only `DELETE` route that passes the acceptance check, and a short boundary note<br>
> **Status:** Draft. The original 19 API tests plus eight serving-extension tests checked offline by the author; local server session checked; no learner pilot, no deployment, no real model<br>
> **Environment:** Windows PowerShell, uv 0.8.3, Python 3.11.13; FastAPI 0.142.1, Pydantic 2.13.5, Starlette 1.7.0, uvicorn 0.54.0; httpx2 2.13.1 for tests. Exact versions are in `uv.lock`

</details>

**QuickCart** is the fictional online shop used across the course. Each merchant's support agents need a small service to create tickets, read them and ask a classifier to put each ticket in a support category. That last step is called **triage**. Each merchant is a separate **tenant**, and one tenant must never see another's tickets. Later units add real model calls and deployment. First, this service must reject bad input, keep tenants apart, handle retries safely within stated limits and put a time limit on slow lookups. The tests show exactly which piece of code enforces each rule.

**Your route:** run the reference, predict and trace each control, try the service locally, diagnose two deliberate faults, then build the own-change endpoint. Keep a private record of each failing and fixed check; the default tests passing does not mean your own-change task is done.

**Why a framework now:** in the bridge you validated input by hand so you could see how it works. Here, Pydantic and FastAPI take care of parsing, routing and the OpenAPI schema, so you can focus on the decisions they cannot make for you. Each framework feature below is matched to something you already wrote by hand in the bridge.

## The service at a glance

This is the project later units build on: [W-ENG-DELIVERY-01](../../delivery/README.md) packages this same service, and AI-AWS-01 deploys a related worker, so you will not need a second application. Both come after the reliability rows on the course map.

| Endpoint | Who can use it | What enforces the rule | Notable failures |
|---|---|---|---|
| `GET /health` | Anyone | — | Only says the service is running; says nothing about the classifier |
| `POST /tickets` | Anyone with a valid token | Strict `TicketIn` model; `Idempotency-Key` header; tenant taken from the token | 401; 409 if a key is reused with a different body or the ID already exists; 422 |
| `GET /tickets/{ticket_id}` | The same tenant only | Tickets stored by `(tenant, ticket_id)` | 404 both for "does not exist" and "belongs to another tenant" |
| `POST /tickets/{ticket_id}/triage` | The same tenant only | Ticket looked up before the classifier is called; `asyncio.timeout`; only allowed categories accepted | 502 for unusable output or a classifier error, 504 for a timeout |

| File | What it does |
|---|---|
| `src/quickcart_api/config.py` | Loads the known users from SHA-256 token hashes and checks settings at start-up |
| `src/quickcart_api/models.py` | `TicketIn` (strict, `extra="forbid"`) and the unchangeable response model `Ticket` |
| `src/quickcart_api/store.py` | In-memory store, organised by tenant, with idempotency records |
| `src/quickcart_api/triage.py` | The classifier interface, a predictable mock classifier and `classify_bounded` |
| `src/quickcart_api/app.py` | Dependencies, routes, the 422 handler that does not repeat input, and the `create_app` factory |
| `tests/test_api.py` | 19 behaviour tests |
| `exercises/check_delete.py`, `delete_reference.py` | The check for your own-change task, and a reference answer you can read |
| `fixtures/` | Made-up users (token hashes only) and sample tickets |
| `requirements-ci.txt` | A pinned export of `uv.lock` for CI, which uses pip. After any lockfile change, regenerate it with `uv export --frozen --no-hashes --no-emit-project -o requirements-ci.txt` |

## Starting state and setup

Copy this folder to your own workspace and work there, because the drills edit source files. The repository copy is the `api-v1` checkpoint. Everything is made up: three public test tokens for two merchants, no real customer data, no network calls except to your local server, and no paid service.

**Before you set up:** the recorded checks used Windows PowerShell, Python 3.11.13 and uv 0.8.3, with every dependency pinned in `uv.lock`. The sync may download packages. You need no model account or cloud resource. The server runs only when you start it below; stop it with Ctrl+C before cleanup.

From **your copy's project root** (the folder containing `pyproject.toml`), in PowerShell, run:

```powershell
uv sync --python 3.11 --locked
uv run python -m unittest discover -s tests -v
```

**Expected:** `Ran 27 tests ... OK` (19 API and eight later serving-extension tests); the timing will vary. `uv sync` installs the runtime dependencies plus the `dev` group (`httpx2`, which Starlette's test client needs), all at the locked versions, and `--locked` stops it if the lockfile is out of date. `pyproject.toml` also sets `exclude-newer`, so any future re-resolve only picks releases published before 2026-09-30.

The made-up bearer tokens are listed below. `fixtures/synthetic-principals.json` stores only their SHA-256 hashes, but these public strings **really do log you in to this teaching service**. They are deliberately shared test tokens and must never be used for a real identity system.

> [!IMPORTANT]
> Use these public tokens only with this made-up lab, running on `127.0.0.1`. Hashing a published token does not make it secret. Keep real keys, passwords and customer data out of the project.

| Token | Tenant | Role |
|---|---|---|
| `synthetic-token-merchant-a-agent` | merchant-a | agent |
| `synthetic-token-merchant-a-supervisor` | merchant-a | supervisor |
| `synthetic-token-merchant-b-agent` | merchant-b | agent |

## Predict before reading the code

Write down your answers first.

1. A client sends `{"ticket_id": "QC-1001", "amount": true}`. A plain Pydantic `int` field without strict mode: is it accepted or rejected? What about `"amount": "25"`?
2. The client adds `"tenant": "merchant-b"` to the body. With Pydantic's default settings, what happens to that field?
3. Does FastAPI's built-in 422 error response include the value the client sent?
4. A mobile client times out and retries `POST /tickets` with the same `Idempotency-Key`. Eight retries arrive at once. How many tickets should exist?
5. Agent B asks for agent A's ticket. Should the answer be 403 or 404?

<details><summary>Explained answers</summary>

1. Both are **accepted** in Pydantic's default relaxed mode: `true` becomes `1` and `"25"` becomes `25`. The author checked this with the locked versions. `TicketIn` uses `strict=True`, so both are rejected.
2. It is **silently ignored** by default (`extra="ignore"`), so a client bug, or an attempt to set fields it should not, goes unnoticed. `extra="forbid"` turns it into a 422. Either way, the tenant must come from the token, never from the body.
3. **Yes:** each error includes an `input` field holding the value that was sent. That can copy secrets or personal data into responses and client logs. `validation_error` in `app.py` returns only `loc`, `msg` and `type`.
4. **One.** The first request gets 201 and the rest get 200 with the same body. The same key with a *different* body gets 409, not a silent overwrite.
5. **404**, exactly the same as for a ticket that does not exist, so tenant B cannot find out which IDs tenant A uses.

</details>

## Walk through the mechanisms

**Identity comes from trusted code.** `current_principal` reads the `Authorization: Bearer` header through FastAPI's `HTTPBearer(auto_error=False)`, hashes the token and looks it up in the users loaded at start-up. A missing, malformed or unknown token gets 401 with a `WWW-Authenticate: Bearer` header. Routes receive a `Principal(tenant, role)`, and nothing in the body or URL can change it. These are test tokens, not a real login system: they never expire and cannot be rotated or revoked. A real service would check signed tokens or sessions issued by its identity provider.

**The input rules are strict.** `TicketIn` checks types without converting them, rejects unknown fields, and limits lengths and formats. `Ticket` is a separate, unchangeable response model, so stored records cannot be altered by accident and the tenant is never sent back to clients. This is the bridge's `parse_ticket` written as a schema, and it also produces the OpenAPI page at `/docs`.

**Errors do not repeat the input.** `validation_error` replaces FastAPI's default handler. It keeps where the problem is and why, which is all a client needs to fix the request, and drops the value that was sent.

**Retries are safe, within one process.** `TicketStore.create` takes a fingerprint of the validated body and records `(tenant, Idempotency-Key) → (fingerprint, ticket_id)`. The "check, then write" step runs under a lock and contains no `await`, so concurrent async requests in one event loop cannot interleave inside it. The concurrency test sends eight retries at the same moment and expects exactly one ticket. **Limit:** this memory disappears when the process restarts and is not shared between worker processes. A production service needs a database unique constraint on `(tenant, idempotency key)` and a rule for how long keys are kept.

**The slow external call has a time limit, and its answer is not trusted.** `triage_ticket` checks that the ticket belongs to the caller's tenant *before* calling the classifier, so a missing or foreign ticket costs nothing. `classify_bounded` wraps the call in `asyncio.timeout`. A timeout becomes 504, and any classifier `Exception` becomes 502 without exposing its message. Because it catches `Exception`, not `BaseException`, a client cancelling its request still cancels the work. The result must be one of the four allowed categories; anything else, including `"BILLING"` or a sentence, is a 502 and the ticket stays `open`. A ticket that is already triaged is returned without calling the classifier again. Every later model call in the course follows this same shape.

**Bad configuration stops start-up.** `create_app_from_env` refuses to start without `QUICKCART_PRINCIPALS_FILE`, or with a timeout that is not a finite number above 0 and up to 10 seconds. A half-configured service that starts and then fails every request is much harder to diagnose than one that refuses to start.

## Run the service

**Terminal 1**, from your project folder:

```powershell
$env:QUICKCART_PRINCIPALS_FILE = "fixtures/synthetic-principals.json"
uv run uvicorn quickcart_api.app:create_app_from_env --factory --host 127.0.0.1 --port 8765
```

**Terminal 2**, also opened in your project folder. The last request is supposed to fail, because merchant B is asking for merchant A's ticket. Keep that refusal as evidence; it does not mean your setup is broken:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/health
$headers = @{ Authorization = 'Bearer synthetic-token-merchant-a-agent'; 'Idempotency-Key' = 'demo-key-0001' }
$body = '{"ticket_id": "QC-1001", "amount": 25, "tags": ["refund"]}'
Invoke-WebRequest http://127.0.0.1:8765/tickets -Method Post -Headers $headers -Body $body -ContentType 'application/json' -UseBasicParsing | Select-Object StatusCode, Content
Invoke-WebRequest http://127.0.0.1:8765/tickets -Method Post -Headers $headers -Body $body -ContentType 'application/json' -UseBasicParsing | Select-Object StatusCode, Content
Invoke-RestMethod http://127.0.0.1:8765/tickets/QC-1001/triage -Method Post -Headers @{ Authorization = 'Bearer synthetic-token-merchant-a-agent' }
Invoke-RestMethod http://127.0.0.1:8765/tickets/QC-1001 -Headers @{ Authorization = 'Bearer synthetic-token-merchant-b-agent' }
```

**What the author saw on 2026-10-14:** `{"status":"ok"}`; then `201` followed by `200` with the identical body `{"ticket_id":"QC-1001","amount":25,"tags":["refund"],"status":"open","category":null}`; triage returned `"status":"triaged","category":"billing"`; merchant B's request failed with `404 {"detail":"Ticket not found"}`. Sending `"amount": true` returned `422 {"detail":[{"loc":["body","amount"],"msg":"Input should be a valid integer","type":"int_type"}]}`. The mock classifier always gives the same answer; a real model would not. Record your own responses rather than copying these.

Open `http://127.0.0.1:8765/docs` to see the generated OpenAPI page. Stop the server with **Ctrl+C** in terminal 1. If you forget the environment variable, start-up stops with `ConfigError: QUICKCART_PRINCIPALS_FILE is not set; see .env.example`.

uvicorn's access log records the method, path and status code. That means ticket IDs appear in it, but request bodies and headers do not. Treat even that log as operational data that needs a retention rule.

## Break, diagnose, repair 1: the error response leaks input

In `create_app`, comment out the line `app.add_exception_handler(RequestValidationError, validation_error)`. Predict which test will fail, then run:

```powershell
uv run python -m unittest tests.test_api.ValidationTests -v
```

**What you should see:** only `test_validation_errors_do_not_echo_submitted_values` fails. FastAPI's default handler puts the test's marker string inside each error's `input` field. Every other validation test still passes, because the status code is still 422. A test suite that only checked status codes would never notice this leak. Put the line back and rerun that test class, then the full suite.

## Break, diagnose, repair 2: tenant scope lost in a lookup

In `TicketStore.get`, replace the `return` line with this lookup, which ignores the tenant:

```python
return next((t for (owner, tid), t in self._tickets.items() if tid == ticket_id), None)
```

Predict what will fail, then run the full suite. **What you should see:** `test_other_tenant_gets_404_and_ids_are_tenant_scoped` and `test_unknown_or_foreign_ticket_never_reaches_provider` fail. Merchant B can now read merchant A's ticket, *and* trigger classifier calls on it. The bug lives in one helper, not in any route, which is why isolation tests must go through the API instead of trusting each handler. Restore the original line and rerun.

For each drill, keep the failing output, your diagnosis and the passing rerun. Never overwrite the evidence of the failure.

## Independent exercise: supervisor-only delete

Merchants need to remove tickets created by mistake. Add `DELETE /tickets/{ticket_id}` to `router` in `src/quickcart_api/app.py`:

- Only a `supervisor` may delete. An `agent` gets **403**, whether or not the ticket exists.
- A supervisor can delete only their own tenant's tickets. Another tenant's ticket, or a missing one, gets **404**.
- Success is **204** with an empty body. Deleting the same ticket again returns 404.
- An invalid ticket ID gets 422, and a missing token gets 401.
- Replaying the original create request's `Idempotency-Key` must not bring the ticket back. A create with a new key may recreate the same ID.

Write at least two tests of your own in `tests/` first, and watch them fail. Then build the endpoint and run:

```powershell
uv run python exercises/check_delete.py
```

**Expected once you have built it:** `Ran 6 tests ... OK`. On the untouched project all 6 fail, so the default tests passing can never be mistaken for your result. `uv run python exercises/check_delete.py --reference` shows the same check passing against `exercises/delete_reference.py`. Only read that file after you have recorded your own attempt, and say so if you do.

<details><summary>Hints, one at a time</summary>

1. Reuse `TicketIdPath`, `PrincipalDep` and `StoreDep`. `TicketStore.delete` already exists and tells you whether anything was removed.
2. Choose the order of the role check and the lookup on purpose. Which order would let an agent find out whether an ID exists?
3. For an empty 204 response, return `Response(status_code=204)` and declare `status_code=204` on the route.
4. The idempotency replay rule is already handled by the store's `TicketGone` path. Write a test that proves it, rather than rebuilding it.

</details>

<details><summary>Worked reasoning</summary>

Permission has two separate parts: *what* the caller may do (their role) and *which* records they may touch (their tenant). Checking the role first means an agent gets the same 403 for every ID, so the endpoint gives nothing away. The tenant comes only from the token, so a supervisor cannot reach another merchant's data even by guessing IDs, and the 404 they get looks exactly like "missing". Deleting has real consequences: a real system would also record who deleted what and when, and think about soft deletes and how long data must be kept. The exercise leaves these out on purpose, so mention them in your boundary note.

</details>

### Transfer challenge without hints

Add `GET /tickets?status=open&limit=20`, which lists the caller's own tenant's tickets. `limit` must be a whole number from 1 to 50 (default 20), and results must always come back in the same order. Write the tests yourself, including one that proves merchant B's tickets never appear in merchant A's list. Explain one way a list endpoint could leak data that the single-ticket endpoint cannot.

## Completion evidence

- [ ] `uv run python -m unittest discover -s tests -v` shows the 27 reference tests plus your own, all passing, on your restored copy.
- [ ] Both drills: the failing output, your diagnosis and the passing rerun.
- [ ] `exercises/check_delete.py` passes on **your** endpoint, with your own tests. Say whether you used the reference.
- [ ] The local server session from "Run the service", with responses you recorded yourself.
- [ ] A boundary note of about 200 words. For identity, tenant scope, input validation, idempotency and the classifier call, say where each is enforced, which test proves it, and what this in-memory, single-process version cannot guarantee in production.

This is evidence for checking your own work. Having your skills independently confirmed needs you to explain your work and make an unseen change, as described in the [capstone evidence brief](../../../assessments/capstone-evidence.md).

## Troubleshooting

| Symptom | Likely cause | What to check and do |
|---|---|---|
| `RuntimeError: The starlette.testclient module requires the httpx2 package` | The `dev` group was not installed | Run `uv sync` (it includes `dev` by default). Do not swap in plain `httpx`: Starlette 1.7 deprecates it for the test client. |
| `ConfigError: QUICKCART_PRINCIPALS_FILE is not set` when starting uvicorn | The variable was set in a different terminal, or not at all | Set it in the server's own terminal, as shown. The path is relative to the folder you start from. |
| Every request returns 401 | The `Bearer ` prefix is missing, or the token has a typo | Compare with the token table. The server only knows the hashes, so it cannot tell you which character is wrong. |
| `[Errno 10048]` or "address already in use" on port 8765 | An earlier server is still running | Stop it with Ctrl+C in its terminal, or choose another `--port`. |
| A test passes on its own but fails in the full run | Tests are sharing state | Each test must build its own app with `create_app`; never reuse a module-level app or store. |
| A triage test hangs | The timeout was removed, or the classifier swallows cancellation | Restore `asyncio.timeout` in `classify_bounded`, and look for `except BaseException` or a bare `except:` around an `await`. |

## Stage defense practice

Use the [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p01--python-and-api-ownership) to practise coding, debugging, design and writing a short update for a stakeholder. Pick from them during this module's reflection and own-change time; you do not need to do every prompt. Note your prediction, the checks you actually ran, any help used and what your evidence cannot show. Practising with public prompts or the reference is different from the final review, where a reviewer chooses an unseen change.

## Cleanup and limits

Stop the server with Ctrl+C. Inside your copy you can delete `.venv` and any `build` or `*.egg-info` folders, which `.gitignore` already ignores. Keep your tests, your own-change work and your evidence. Nothing runs in the background, there are no cloud resources and nothing keeps costing money.

**Limits:** in-memory storage, a single process, test tokens that never expire, a predictable mock classifier, no rate limiting, no structured logging or tracing, no container and no deployment. These are deliberate. The delivery unit (AI-DELIVER-01) adds packaging and CI, and AI-AWS-01 adds deployment. Real model calls start in the direct-API lessons (AI-API-01), whose answer quality has to be evaluated separately. Mock tests prove the control flow, not the quality of a model.

**Required before the deployment lessons:** AI-DELIVER-01 and AI-AWS-01 build on this project, or on your own version that passes the same tests. Finish the completion evidence above first.

**Sources:** the FastAPI documentation on [testing](https://fastapi.tiangolo.com/tutorial/testing/), [testing dependencies](https://fastapi.tiangolo.com/advanced/testing-dependencies/) and [handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/), and Pydantic's [strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/) and [model configuration](https://docs.pydantic.dev/latest/api/config/) pages, recorded in the [source ledger](../../../docs/source-ledger.md).

## Completion checkpoint

**You can now:** show where identity, tenant scope, strict validation, idempotency and the time-limited classifier call are each enforced, and prove each one with a test that fails when that control is removed.

**Show it:** the completion evidence above.

**Next:** continue the course map with AI-ML-01: [SG-ML-00 — How models learn from examples](../../../study-guides/ml-foundations/docs/00-learning-from-examples.md).

[Previous: Python bridge route](../README.md) · [Package checkpoint](../python-bridge/README.md) · [Course map](../../../README.md)

The later delivery route adds [measured serving under load](../../delivery/serving-under-load.md) using an explicit lab factory in this package. Its extra routes and admission controls are absent from the normal API factory; complete that exercise in phase 4, after reliability and packaging.
