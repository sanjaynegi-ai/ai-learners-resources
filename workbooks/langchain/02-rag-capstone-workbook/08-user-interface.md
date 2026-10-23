# W-RAG-08 - Expose status honestly at the CLI

**Does the interface show whether a request answered, abstained or was denied?**

> **Your goal:** Display domain outcomes honestly and clear stale answer state.<br>
> **You need:** [Validated quotes](07-answer-generation.md) and the personal package from W-RAG-01.<br>
> **Effort:** Part of the 3-4 hour guided/control estimate in [the brief](00-project-brief.md); record actual effort.<br>
> **You will produce:** Three status reports and a tested display adapter for ready and non-ready transitions. **Status:** Draft; offline synthetic reference, unpiloted.

QuickCart's support agent needs to distinguish a usable quote from a request that could not be answered. The provided interface is a CLI, not a web app. No HTTP authentication, browser rendering or deployment is claimed. Continue in your existing personal package; no new UI framework is needed.

**Before running:** these local Python 3.11/uv commands use synthetic session names, seed a fresh database per invocation and save reports under `results/`. No paid calls or server is involved. Predict which request yields a quote and which must not. A fixture session name is not a deployed login mechanism.

Working directory: your private `retrieval-lab` copy from W-RAG-01. Runtime: Python 3.11 via uv in PowerShell.

```powershell
uv run grounded-rag ask --session alice --query "private review" --output results/role-denied.json
uv run grounded-rag ask --session supervisor --query "private review" --output results/allowed.json
uv run grounded-rag ask --session unknown --query "refund" --output results/unknown.json
```

Valid users without eligible evidence receive abstained, the supervisor receives ready, and an unknown session receives denied. None of the non-ready outputs contains a citation. Script exit 0 means the CLI executed; inspect the domain status to know whether it answered. A no-release or denial is not disguised as task completion.

Implement an independent small display adapter in your private workspace: ready shows quote plus provenance; abstained/conflict routes to a review explanation; denied shows no document names or snippets. Preserve machine-readable JSON as the underlying contract. Add tests that non-ready states cannot accidentally show an old answer left in UI state.

Use a new `display_adapter.py` beside the package metadata and `tests/test_display_adapter.py` for your own checks. Keep the reference CLI unchanged. Exercise transitions, not just isolated payloads: `ready → denied`, `ready → abstained`, and `ready → conflict`. Each must clear the prior quote/provenance before showing the new state; verify that a subsequent valid answer can display normally.

> [!IMPORTANT]
> Clear stale content before rendering the new outcome. A correct denial message does not protect data if the previous answer remains visible beside it.

Output paths must be within results. Reports contain synthetic source quotes; real content would require controlled retention and access. Do not log raw questions/claims in production by default. The CLI's selectable fixture identity is deliberately unsuitable as a web login mechanism. Next: W-RAG-09.

## Check your reasoning

Attempt each question before opening its answer.

**Diagnosis:** The CLI exits 0 for the unknown session. Did the request succeed?

<details>
<summary>Reveal worked reasoning</summary>

No. Exit 0 means the program ran. The domain status is **denied**. Always read the status field; treating a clean exit as success hides denials and abstentions.

</details>

**Decision:** Why must a non-ready state clear the previously displayed answer?

<details>
<summary>Reveal worked reasoning</summary>

Otherwise the screen still shows an old quote after a denial or revocation, which is a leak through UI state. The independent adapter tests make this explicit.

</details>

## Completion checkpoint

**You can now:** make every interface state say whether the system answered, abstained or denied.

**Show it:** the three status results and your adapter tests. Cleanup: nothing keeps running; generated results are removed in W-RAG-13.

**Reflect:** Where else besides the screen could an old answer survive a denial?

**Next:** [W-RAG-09 — Measure retrieval separately from answers](09-evaluation-and-testing.md).

[Workbook index](README.md) | [Course map](../../../README.md) | [Reference setup](retrieval-lab/README.md)
