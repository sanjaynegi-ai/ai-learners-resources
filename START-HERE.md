# Start here

> **Your goal:** Begin the one standard route every learner follows, and skip only the early lessons you already know.<br>
> **You need:** Backend programming experience, a personal folder to work in and made-up test data. No AI or Python knowledge is needed.<br>
> **Effort:** Lesson 1 below takes 30–45 minutes; you can skip it if its skip check is easy for you.<br>
> **You will produce:** Short written answers to three backend cases and the exact lesson you will open next.

This page starts the [Developer learning route](README.md#ordered-capability-map). You do not need to install an AI framework or open a paid model account to begin.

**Meet QuickCart**, the fictional online shop used throughout the course. Customers place orders, and support staff answer policy questions and handle refunds. The same orders, policies and support tickets appear in every lesson, so you can focus on the engineering. All examples use made-up data; you never need real customer records.

## One route for everyone

There is no placement test and no menu of routes. **Every learner follows the same ordered route**, from the first lesson below to the capstone and defense. The first lessons cover the backend and Python skills the rest of the course builds on, so nothing later assumes knowledge you were never shown.

Each of these opening lessons starts with a short **skip check**. If you can answer it confidently *and* explain why, move on to the next lesson. If you are unsure, do the lesson; they are short. Skipping is your decision, and nothing is scored. If a later lesson trips you up, come back to the one you skipped.

> [!TIP]
> Start offline. The opening lessons and the Python route need no paid model account. You choose a model provider later, in the lesson that uses it.

## Lesson 1 — Backend rules that AI work depends on

**Skip check:** can you already explain (1) why the tenant a request may read must come from the logged-in identity and never from a field in the request, (2) how a stored idempotency key stops a retried refund from paying twice, and (3) why a reply in valid JSON can still be wrong? If yes, go to [lesson 2](#lesson-2-onward--the-python-route).

You already know these ideas from backend work. AI features make them more important, because a model will happily produce a convincing answer from data it should never have seen, or repeat an action it cannot tell has already happened. This lesson names the three rules that come back in almost every later module.

For each case, write your answer in your personal folder *before* opening the explanation. Keep your first answer even if it turns out wrong; it shows you what changed.

### Case 1 — Whose data is this?

QuickCart serves two fictional merchants, `shop-a` and `shop-b`. Each is a separate **tenant**: one tenant's request must never reach another tenant's records. A request arrives saying `tenant=shop-b`, but the logged-in user belongs to shop-a. What should the system read or do, where is that decision made, and what test would prove the request is refused?

<details>
<summary>Compare your reasoning</summary>

The logged-in identity decides the tenant and the permissions, not a field the caller sends. The application looks up what that identity may see *before* it searches or reads anything, so documents from shop-b are never retrieved. Neither the user nor the model can widen that access. A test sets up a shop-a user, sends `tenant=shop-b` and checks that no shop-b record is read and the request is refused.

A common unsafe answer filters the model's reply afterwards. By then the forbidden documents have already been read and may have shaped the answer.

</details>

### Case 2 — A refund retried after a timeout

A client asks for a pretend refund. The refund goes through, but the reply is lost and the client times out, then retries. How do you stop the customer being paid twice? What should happen if the retry carries different data?

<details>
<summary>Compare your reasoning</summary>

A timeout does not prove the refund failed: it may have gone through just before the reply was lost. Store an **idempotency key** with the operation and its request data. A retry with the same key and the same data returns the earlier result instead of paying again; the same key with *different* data is rejected. Keep the record somewhere that survives a restart, not only in memory. A fresh request ID on each retry does not solve this. One limit remains: you still need to check with the real payment provider, because your record cannot see what happened on their side.

</details>

### Case 3 — Valid JSON, wrong answer

The assistant returns perfectly valid JSON that cites a real policy ID, but it states the wrong refund allowance. What passed, what failed, and what check would catch the mistake?

<details>
<summary>Compare your reasoning</summary>

The format and schema checks passed: the reply has the right shape. The claim failed: it does not match the policy. Valid JSON proves shape, not truth. A separate check compares the stated allowance with the policy and order facts this user is allowed to see. Fluent wording and valid structure are not evidence that an answer is correct.

</details>

**You can now:** explain where access decisions belong, why retried actions need a stored key and why output checks must include business correctness. Later lessons turn each rule into code and tests: [W-LLM-ACT-01 — safe actions](workbooks/llm/safe-actions/README.md), the [offline controls lab](workbooks/reliability/offline-controls/README.md) and the [permission-aware RAG build](workbooks/langchain/02-rag-capstone-workbook/README.md).

## Lesson 2 onward — the Python route

Next comes the [Python route](workbooks/python/README.md). Every learner works through the same units in the same order. The route page gives each notebook unit its own skip check, so a learner who already knows Python's validation, async or packaging behaviour can move straight on.

| Order | Unit | Skippable? |
|---|---|---|
| 2 | [W-PY-CONCEPT-01 — validation warm-up](workbooks/python/01-validation-concepts.ipynb) | Yes, if its skip check is easy for you |
| 3 | [W-PY-BRIDGE-01 — typing and validation](workbooks/python/02-typing-and-validation.ipynb) | Yes, if its skip check is easy for you |
| 4 | [W-PY-BRIDGE-02 — async and exceptions](workbooks/python/03-async-and-exceptions.ipynb) | Yes, if its skip check is easy for you |
| 5 | [W-PY-BRIDGE-03 — idioms and behaviour tests](workbooks/python/04-tests-and-python-idioms.ipynb) | Yes, if its skip check is easy for you |
| 6 | [W-PY-BRIDGE-04 — package checkpoint](workbooks/python/python-bridge/README.md) | No: later delivery work builds on it |
| 7 | [W-PY-API-01 — tested QuickCart API](workbooks/python/quickcart-api/README.md) | No: later delivery and AWS work builds on it |

The [Python concepts guide](study-guides/python-engineering-bridge/README.md) explains why each behaviour matters; read the matching section when you reach a unit. After the API project, carry on down the [course map](README.md#ordered-capability-map) in order.

## Set up only the lesson you are on

**Set up only the project you are about to study.** Each workbook names its working folder, Python version, dependencies and the commands that check your setup. Many labs use Windows PowerShell, uv and Python 3.11; follow each project's own instructions rather than installing everything at once.

1. **Choose your working space:** keep your notes and any private feedback outside the course repository. For project builds, follow the workbook's instructions for making a personal copy, and keep its folder layout. Never put keys or passwords in shared files.
2. **Check before you change code:** run the project's setup check, note the result and decide which files you will create or change. If the check fails, use the workbook's troubleshooting section first.

**Study guides explain why; workbooks show you what to build and how to check it.** Read each linked explanation when you reach its task, not all guides up front. The [project learning route](docs/project-learning-route.md) shows which projects grow over time and which are small standalone labs. Follow the [course map](README.md#ordered-capability-map), not folder names or alphabetical order; reference-only examples are not extra required projects.

You choose a model provider later, in the lesson that needs one. Hosted models need an account, access and a budget; local models need downloads and capable hardware. Offline fixtures let you practise control flow and failures without paying for model calls, but they cannot tell you how good a real model's answers are. Package downloads may still need internet access. Always read the cost and cleanup notes before starting a provider or cloud exercise.

## Study, verify and resume

You can work through the explanations, guided practice and self-checks on your own. The [learning paths and support guide](docs/learning-paths-and-support.md) explains what the repository gives you and what needs an instructor or reviewer.

Use this loop for every lesson:

1. **Predict:** read the problem and the related guide. Write down what you expect, and why, before running the example.
2. **Build and check:** make the workbook change, run its check and compare what happened with your prediction.
3. **Break and repair:** add the fault the lesson describes, work out why it fails and confirm your fix with a test that would catch it again.
4. **Apply it:** try the changed task before opening hints or solutions, and explain which assumption changed.
5. **Leave a return point:** note the commands, real outputs, assumptions, versions, help used and your next open question in your private log.

> [!IMPORTANT]
> Running the reference code successfully is only a starting point. Real progress means your own change, a failure you diagnosed and an explanation of the result. Keep offline checks separate from real-model quality and deployment evidence.

Use the [public assessment index](assessments/README.md) to compare your work with the criteria. Self-checks help you find gaps; having your skills independently confirmed needs a reviewer who looks at your work and your explanation. Access to this repository does not include grading, mentoring or certification.

### Leave yourself a useful return point

Copy this short record into your private notes. Note skipped lessons too, so you know where to return if something later feels unfamiliar. The filled rows are examples, not results you should claim.

| Lesson / task | What happened | Next action |
|---|---|---|
| W-PY-BRIDGE-02 | Skipped: skip check answered and explained without help. | Return here if cancellation surprises me in a later lab. |
| W-PY-BRIDGE-01 | Normal and empty cases passed; `True` was wrongly accepted as an amount. Used a hint about Python types. | Fix the type check, add a test that rejects `True`, then repeat with new input. |
| Your current task | Record the command, result, where the evidence is and any help used. | Name one fix or the exact next lesson. |

**Resume check:** your tests passed last week, but today you changed the input format. Can you carry on using last week's results?

<details>
<summary>Compare your reasoning</summary>

No. Last week's results describe last week's code and inputs. Confirm the starting state, rerun the affected checks for both valid and invalid input, and record the new result. A failure and its fix are worth more than a checklist that just says "done".

</details>

## Troubleshoot by symptom

| Symptom | Likely cause | What to check, then do |
|---|---|---|
| Command or import not found | Wrong shell or environment, or a missing dependency | Check the terminal's working folder and the selected Python interpreter, then rerun your workbook's setup checks. The file open in your editor does not set the terminal's folder. |
| A later lesson assumes something you skipped | The skip check looked easier than the lesson | Go back to the skipped unit, do its exercise, then return to where you were. |
| Hosted model call fails | Missing key, no access or a service problem | Look at the error type (with secrets hidden) and follow the relevant model chapter. Never print or share keys. Record that the call did not complete, and do not keep retrying a paid call before you know why it failed. |
| Local model call hangs | The model is still loading, or the machine lacks resources | Review the setup's hardware and download notes and the [model timeout guidance](workbooks/langchain/01-learning-workbook/02-models-and-messages.md). Record the fault instead of treating it as an answer. |
| A RAG answer looks right but is not supported | The search missed the right passage, or the model made something up | Check the retrieved passages separately from the answer, using the [retrieval](workbooks/langchain/01-learning-workbook/08-documents-and-retrieval.md), [grounding](workbooks/langchain/01-learning-workbook/09-grounded-rag.md) and [debugging](workbooks/langchain/01-learning-workbook/13-debugging-testing-and-evaluation.md) chapters. |
| Unsure which code state a lesson expects | A skipped prerequisite or mixed-up projects | Check the starting-state table and restore only your own last good checkpoint; never overwrite other work. |

Follow each lab's cleanup steps. Stop local servers when you finish and keep only the data and index files you mean to keep. Keep local practice results separate from any later real-model or deployment checks.

**You can now:** explain the three backend rules the course builds on and name the lesson you will open next. **Next:** open the [Python route](workbooks/python/README.md) and start with its first unit, or skip it if its skip check is easy for you.

[Previous: course overview](README.md) · [Course map](README.md#ordered-capability-map)
