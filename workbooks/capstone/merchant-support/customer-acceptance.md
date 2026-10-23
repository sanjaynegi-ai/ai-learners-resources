# Version the acceptance contract before checking the result

QuickCart's reference can execute a simulated refund after one supervisor approval. Finance now requires two supervisors above 2000 cents. An old passing demonstration cannot establish acceptance of that changed workflow.

**Outcome:** freeze user acceptance testing (UAT) cases, retain results by version and explain a no-acceptance decision. **Prerequisites:** [capstone discovery](01-discovery-and-acceptance.md), [guided application](02-guided-build.md), and the earlier [customer rehearsal](../../delivery/customer-rehearsal.md). **Artifact:** `delivery/acceptance.md` with versioned case/result tables, plus the changed-requirement update and handover links. **Effort:** replace 20 minutes of the existing discovery acceptance discussion and 20 minutes of the existing handover/independent reflection; no additional phase-6 assignment. The independent implementation remains within its existing allocation.

**Starting state:** use `cap-2-approved` reference behavior in your personal merchant-support project, retaining the sibling retrieval package. Earlier `cap-0-contract` work freezes the cases before implementation. The runnable reference is available for comparison; your independent two-approval/calendar change is not supplied here. No real refund, customer message, cloud call or stakeholder acceptance is required or implied.

## 1. Freeze version 1

Copy this contract into `delivery/acceptance.md` **before** checking the local application. Record the exact source/dirty state, fixture and rubric versions, runtime/configuration, decision role, evidence kind and timestamp. Version `quickcart-uat-v1` is a fictional reference contract, not customer approval. Link existing CAP requirement IDs rather than inventing a second assessment rubric.

| Case | Requirement / actor and trigger | Expected observation under v1 | Evidence boundary |
|---|---|---|---|
| UAT-01 | CAP-GROUND-01: merchant-A agent asks `refund` | Ready with reviewed current citation | Curated synthetic answer; not general language quality |
| UAT-02 | CAP-ORDER-01: A requests B's `QC-3002` | Denied without order data | Trusted local identity only |
| UAT-03 | CAP-GROUND-01: unsupported `weather` question | Explicit abstention | No invented answer; manual follow-up not completed |
| UAT-04 | CAP-APPROVE-01: execute 1000 cents before approval | Denied; no simulated effect | Local application transaction only |
| UAT-05 | CAP-IDEM-01: approve by different current supervisor; execute/replay | Done with exactly one stored effect | Local durable effect; no external payment guarantee |
| UAT-06 | CAP-APPROVE-01: supervisor revoked before new action executes | Denied; no additional effect | Execution-time authority recheck |

For every case, create a result row containing: acceptance version, case ID, expected behavior, actual observed behavior, Pass/Fail/Not run, command/report/artifact reference, environment, checker/role, actual versus simulated evidence and unresolved condition. Missing evidence is **Not run**, not Pass. A customer role's “accepted” state is separately **simulated**, **pending**, or **actually confirmed with authorized evidence**. Passing technical rows never fills in that sign-off field.

**Prediction:** if UAT-01 passes, can the team accept all refund-policy questions? Explain before testing. It demonstrates one reviewed fixture, not arbitrary questions, languages, eligibility, model quality or deployment.

## 2. Inspect observable reference results

Execution is optional until the guided application is complete; keep rows Not run beforehand. From your personal `workbooks/capstone/merchant-support` directory in Windows PowerShell, using Python 3.11/uv and the existing lockfile:

```powershell
uv sync --python 3.11 --locked
```

No new dependency is needed. The probe below uses only the offline provider, trusted synthetic tokens and temporary SQLite state, which is closed and removed even on failure. It exercises the application engine directly; it is **not** an HTTP/UI or deployed end-user acceptance test. Separate integration/container/live gates remain in force. Do not substitute real tokens or point it at learner or production state.

Create `delivery/uat_reference_probe.py`. First implement and run the v1 part through its first `finally`; predict each denial/replay result. For that first run, omit the second temporary-directory block and retain the final `print` and `asyncio.run(main())`. Then append the separate v2 part and predict whether the unchanged reference meets the new contract. The full comparison is below so you can inspect it after trying. All returned effect counts come from stored rows, not a hard-coded success message.

```python
import asyncio
import json
import tempfile
from merchant_support.core import Engine, fixture_paths

async def main():
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        engine = Engine(directory, *fixture_paths())
        try:
            reply = await engine.ask("demo-agent-a", "refund")
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-01",
                         "expected": "ready with citation",
                         "passed": reply["status"] == "ready" and bool(reply["citations"]),
                         "actual": reply["status"]})
            try:
                engine.order("demo-agent-a", "QC-3002")
                denied = False
            except PermissionError:
                denied = True
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-02",
                         "expected": "denied", "passed": denied, "actual": "denied" if denied else "exposed"})
            unsupported = await engine.ask("demo-agent-a", "weather")
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-03",
                         "expected": "abstained", "passed": unsupported["status"] == "abstained",
                         "actual": unsupported["status"]})
            key = engine.propose("demo-agent-a", "QC-3001", 1000, reply["citations"])["action_id"]
            try:
                engine.execute("demo-agent-a", key)
                denied = False
            except PermissionError:
                denied = True
            count = engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-04",
                         "expected": "denied with zero effects", "passed": denied and count == 0,
                         "actual": {"denied": denied, "effects": count}})
            engine.approve("demo-lead-a", key)
            first = engine.execute("demo-agent-a", key)
            replay = engine.execute("demo-agent-a", key)
            count = engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-05",
                         "expected": "done, one effect after replay",
                         "passed": first["status"] == replay["status"] == "done" and count == 1,
                         "actual": {"status": replay["status"], "effects": count}})
            second = engine.propose("demo-agent-a", "QC-3001", 1001, reply["citations"])["action_id"]
            engine.approve("demo-lead-a", second)
            engine.store.revoke("supervisor")
            try:
                engine.execute("demo-agent-a", second)
                denied = False
            except PermissionError:
                denied = True
            count = engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
            rows.append({"version": "quickcart-uat-v1", "case": "UAT-06",
                         "expected": "denied, still one effect", "passed": denied and count == 1,
                         "actual": {"denied": denied, "effects": count}})
        finally:
            engine.close()
    # A fresh, isolated reference store; v2 criteria are checked without changing code.
    with tempfile.TemporaryDirectory() as directory:
        engine = Engine(directory, *fixture_paths())
        try:
            reply = await engine.ask("demo-agent-a", "refund")
            key = engine.propose("demo-agent-a", "QC-3001", 2001, reply["citations"])["action_id"]
            engine.approve("demo-lead-a", key)
            try:
                actual = engine.execute("demo-agent-a", key)["status"]
            except PermissionError:
                actual = "denied"
            rows.append({"version": "quickcart-uat-v2", "case": "UAT-V2-01",
                         "expected": "denied until two current supervisors", "passed": actual == "denied",
                         "actual": actual})
        finally:
            engine.close()
    print(json.dumps({"evidence": "executed local offline reference probe",
                      "customer_signoff": "simulated/pending; no real customer acceptance",
                      "rows": rows}, indent=2))

asyncio.run(main())
```

Run `uv run python delivery/uat_reference_probe.py` and retain the output privately with exact source/runtime/fixture references. Expected reference behavior: six v1 rows pass; the v2 row fails because one approval yields `done` at 2001 cents. A successful script exit means observations were collected, **not** that all acceptance cases passed. The v2 failure is intentional evidence of a missing changed requirement; do not change its expected result to get a green table. Compare your independent implementation later, from the same declared inputs.

## 3. Freeze version 2 before the independent change

Keep v1 and create `quickcart-uat-v2`, linking the [independent brief](06-independent-delivery.md). Carry forward every unchanged tenant, evidence, idempotency and execution-bound case. Add the following cases; do not claim the current reference implements them:

| Case | Changed contract | Reference result before independent implementation |
|---|---|---|
| UAT-V2-01 | 2001 cents with one eligible other supervisor stays blocked | Observably fails in the probe: `done` |
| UAT-V2-02 | Exactly 2000 cents needs one other supervisor; 2001 needs two distinct others | Full two-supervisor boundary/positive test Not run |
| UAT-V2-03 | Revoked/duplicate/foreign/proposer approvals cannot supply quorum | New quorum/migration workflow Not run |
| UAT-V2-04 | Calendar effective instant, future-only/conflicting/deleted policy fail closed under agreed timezone | Calendar workflow Not run; timezone/instant unresolved |
| UAT-V2-05 | Migration preserves completed effects and does not grandfather incompatible pending actions | Independent migration/recovery Not run |

These are versioned result states, not publication labels. In your private results, replace each state only with your actual observation and evidence. Add workflow/user-understanding criteria, qualified language review and declared environment/live scope where applicable; engine checks cannot establish those. Fix implementation and re-execute, retaining failed reports and changed source versions. The simulator and offline reference do not provide final model/deployment acceptance.

**Simulated finance exchange:** the lead asks to mark the one-approval result accepted “just for launch.” Draft a scope/change response identifying CAP-APPROVE-01, policy applicability, migration and review load. Keep no-acceptance for v2, ask the owner for the effective instant/timezone and eligible approver policy, and propose a bounded next verification. Do not invent a release date or real sign-off.

## Completion and handover

Use these UAT/spec/result sections **instead of** the earlier acceptance paragraph and generic stakeholder reflection within the [five-record allocation](../../../assessments/engineering-delivery-artifacts.md). Link current version, failures, pending owner decisions and safe operating boundary from `delivery/update.md` and `delivery/handover.md`. Keep the adoption/workflow-impact plan from the earlier rehearsal in that handover; its numbers remain hypothetical until actually observed.

For an unfamiliar transfer, the merchant reverses one approval while a migrated action is waiting. Add a v3 case before implementing, state the expected authority decision point and evidence needed, and rehearse the response without hints. Explain why a stale UI approval badge and old passing results cannot authorize execution. Use the established independent rubric; no new score or credential is created.

**Show it:** frozen v1/v2 cases, actual/pending result rows, original failed evidence, simulated negotiation, revised requirement response and current handover. Reading or running this public probe is not independent competence or customer acceptance. Temporary state is cleaned automatically; preserve only your private reports and script, and do not remove the course fixtures.

**Next:** complete the [independent change](06-independent-delivery.md) and attach the current acceptance state to the [evidence review](07-evidence-and-defense.md).

[Previous: discovery contract](01-discovery-and-acceptance.md) · [Phase overview](README.md) · [Customer delivery rehearsal](../../delivery/customer-rehearsal.md)
