# W-RAG-10 - Diagnose revocation and repair safely

**Can an answer remain eligible after access changes during the request?**

> **Your goal:** Diagnose a revocation race and verify the delivery recheck.<br>
> **You need:** [Evaluation and testing](09-evaluation-and-testing.md) in your personal package.<br>
> **Effort:** Part of the 3-4 hour guided/control estimate in [the brief](00-project-brief.md); record actual effort.<br>
> **You will produce:** Drill output, a removed-recheck regression and an incident note. **Status:** Draft; offline synthetic reference, unpiloted.

Predict which output may still be returned after permissions change, then run:

**Starting state:** retain your personal QuickCart package and W-RAG-09 evidence. The drill uses Python 3.11 via uv, seeds synthetic SQLite state and writes a local report. No paid call, live provider or server is involved. Save earlier reports before rerunning the same output path.

Working directory: your private `retrieval-lab` copy from W-RAG-01. Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run grounded-rag drill --output results/revocation-drill.json
```

Compare the four statuses with your prediction; the worked answer is in **Check your reasoning** below. The repair changes who may access the evidence; it does not undo the revocation to make the original request pass. Inspect citations and retrieved fields: the revoked response must expose neither.

Build a learner checkpoint by temporarily removing the post-provider permission/version recheck in `answer` in `src/retrieval_lab/grounded.py`. Add a test provider that revokes `alice` before returning an otherwise valid quote. The response must not be ready. Observe the failed regression, restore only the deliberate source edit and retain the test. The supplied `test_revocation_during_provider_blocks_response` is an inspectable reference; disclose consulting it.

> [!IMPORTANT]
> Blocking delivery does not retract evidence already seen by a provider. State both the exposure prevented and the remaining race in your incident note.

| Symptom | Cause to investigate | Diagnostic and repair |
|---|---|---|
| Unexpired source not found | Old index revision/hash | Compare documents and chunks; republish valid current index, never bypass freshness |
| Ready after role removal | Cached identity or missing recheck | Resolve current principal before exposure |
| Forbidden document in ranking | Filtering happened after search | Filter authorized set before provider/ranking |
| Correct filename, wrong answer | Unsupported assertion or irrelevant quote | Validate claim support and intent; abstain rather than invent |

Document the incident timeline, affected output surfaces and remaining race limits. Include permission at retrieval, permission at provider submission, the change, delivery decision, and the regression that protects the repair. Keep expected behavior and observed output in separate columns.

## Check your reasoning

Attempt each question before opening its answer.

**Prediction:** What sequence of statuses does the revocation drill produce?

<details>
<summary>Reveal worked reasoning</summary>

**ready, abstained, ready, abstained**: the agent lookup succeeds; the document ACL is changed after retrieval to allow only supervisors, so the agent response is blocked; the supervisor lookup succeeds; deletion then removes the evidence. The drill changes document eligibility, not the user's membership role.

</details>

**Diagnosis:** If you remove the post-provider recheck, which test fails and what kind of bug is it?

<details>
<summary>Reveal worked reasoning</summary>

`test_revocation_during_provider_blocks_response` fails. It is a time-of-check/time-of-use gap: permission was valid at retrieval but not at delivery.

</details>

**Decision:** To make the revoked request pass, someone suggests restoring the agent's access to the document and rerunning. Is that a repair?

<details>
<summary>Reveal worked reasoning</summary>

No. The revocation was correct; the repair is the recheck that blocks delivery. Changing who may access evidence to make a test pass would hide the incident. Record the timeline and keep the regression.

</details>

## Completion checkpoint

**You can now:** show that a revocation blocks delivery after the provider has answered, and diagnose a time-of-check/time-of-use gap.

**Show it:** the drill output, your regression test and an incident note. Cleanup: generated results are removed in W-RAG-13.

**Reflect:** What did the incident show about timing that your earlier tests had not covered?

**Next:** [W-RAG-11 — Specify deletion and delivery limits](11-production-considerations.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
