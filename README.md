# SkillUp — Production AI Engineering for Backend Engineers

You already build reliable backend systems. This course shows you how to build AI features with the same discipline: applications you can **explain, build, test, deploy, fix and defend**. It is written for backend engineers with about five or more years in an object-oriented language. You do not need Python or AI experience to begin: everyone follows the same route, and you skip the opening lessons you already know.

## Start your first session

**Begin with [START-HERE.md](START-HERE.md#lesson-1--backend-rules-that-ai-work-depends-on).** Its first lesson takes 30–45 minutes and covers the backend rules the course builds on; the Python lessons follow. Each opening lesson starts with a short skip check, so you can move past anything you already know. Then follow the course map below in order. You do not need a paid AI account for any of this.

[Start here](START-HERE.md) · [Course map](#ordered-capability-map) · [Study workflow](#study-workflow-and-available-material) · [Assessment and effort](#effort-and-assessment-meaning)

## What you will build

**Meet QuickCart**, a fictional online shop that appears in every module. Customers place orders, and support staff answer policy questions and handle refunds. Because the business stays the same, you can spend your energy on each new engineering problem instead of learning a new domain. All data is made up, so you never need real customer records.

QuickCart wants an internal support assistant. It should find the right policy and draft a reply, without showing staff another customer's data or breaking refund rules. Step by step, you will learn to give the model trusted evidence, check its replies, let it use tools safely, cope with timeouts and retries, record approvals, test releases and recover from incidents. The [guided merchant-support capstone](workbooks/capstone/merchant-support/README.md) brings all of this together, and its [independent brief](workbooks/capstone/merchant-support/06-independent-delivery.md) asks you to change it on your own.

Along the way you will produce:

- **Working code:** typed Python and API projects, answers backed by sources, and tool workflows with clear limits.
- **Evidence you can show:** failure tests, separate checks for search and for answers, versioned reports and cost estimates.
- **A handover another engineer could run:** design decisions, a threat model, a runbook, an incident recovery and a one-to-one defense of your work.

Some labs focus on one idea in a small separate project instead of growing the main application. The [project route](docs/project-learning-route.md) shows which is which. Offline and simulated labs teach the controls; tests against a real model and a real deployment are reported separately.

## Try an engineering prediction

QuickCart's assistant returns perfectly valid JSON and a clear refund explanation, but it used **another customer's order**. Would you accept the result? Which checks are missing? Decide before you open the answer; you do not need any AI background.

<details>
<summary>Compare your reasoning</summary>

Reject it. Valid JSON only proves the reply has the right shape. It says nothing about whether the assistant was allowed to read that order, or whether the refund is correct. Your application must confirm who is asking and what they may see, then check the answer against the right order and policy. This course turns checks like these into code, tests and evidence you can explain.

</details>

## Your learning journey

![Six phases: foundations; reliable calls and state; retrieval, tools and evaluation; orchestration and delivery; AWS and operations; integrated capstone and defense.](docs/diagrams/course-journey.svg)

**How to read the diagram:** follow phases 1–3 along the top row, then phases 4–6 along the bottom row from right to left. Arrows show the order you learn in, not network calls or fixed weeks. Optional extras are left out so the main route is easy to see.

| Phase | Learn and build | Checkpoint you can explain |
|---|---|---|
| 1 — Foundations | Backend rules warm-up, Python and API skills, ML and LLM basics | Why a working program or a fluent answer can still be wrong |
| 2 — Reliable calls and state | Calling a model API, prompts, checking outputs and limiting chat history | What your code must check, and what the provider can get wrong |
| 3 — Retrieval, tools and evaluation | Finding permitted evidence, RAG, safe actions and separate quality checks | Why an answer or action is supported and allowed |
| 4 — Orchestration and delivery | Long-running workflows, SDK and MCP tool interfaces, n8n and packaging | How to resume, retry and release without losing approvals or repeating actions |
| 5 — AWS and operations | One Bedrock deployment path, monitoring, cost and recovery | How to spot a failure, contain it and clean up |
| 6 — Capstone and defense | Guided build, your own changes, handover and fixing gaps | Which claims your evidence supports, and what is still open |

These six phases make up the **six-month Developer program** and the self-study route. The [ten-month Architect foundations](docs/architect-foundations.md) are a separate route; you do not need any advanced extension to finish the Developer path. Use the time estimates to plan, then adjust them to your own pace.

## Prerequisites and setup

The opening lessons teach the skills this course builds on: identity and permissions, retries, input validation, Python, imports, tests and async code. Every learner follows them in the same order; each has a skip check, and you decide what to skip. The [Python route](workbooks/python/README.md) lists its units in order. You do not need any AI knowledge to start.

Set up **one project at a time**, from the folder and lockfile that lesson names. Most examples use Windows PowerShell, uv and Python 3.11; each project lists the versions it was tested with. Anything that needs a provider account, a local model download or a paid call is explained in that lesson, before you run it. Keep your keys and private work out of the course folders.

## Study workflow and available material

Every lesson follows the same rhythm:

1. **Predict:** read the problem and decide what you expect before looking at the answer.
2. **Build and check:** make a small change, run the check and write down what really happened.
3. **Break and repair:** find a deliberate fault, explain why it happens and keep the test that catches it.
4. **Apply and reflect:** try the changed task before opening hints, note any help you used and what is still unclear.

> [!TIP]
> Keep a private learning log: your prediction, the command, what you saw and your explanation. A passing reference run is only the starting point; your own change and reasoning show real progress.

Three labels appear throughout. **Required** work is part of the route. **Optional** work is a refresher or an extra. **Reference** material helps you make a decision without adding another build. Use the map below for order, and the [project route](docs/project-learning-route.md) to avoid repeating overlapping work.

You can now name your first step and the evidence the course will ask you to keep. **Next: [open lesson 1](START-HERE.md#lesson-1--backend-rules-that-ai-work-depends-on), then follow the course map in order.**

## Ordered capability map

Work through the numbered checkpoints in order, reading each explanation and doing its practice together. They are milestones, not fixed weeks. The IDs help you track progress and ask for help: **AI-** IDs are capabilities, **SG-** IDs are study guides and **W-** IDs are workbook units.

**Reading the map:** *Prerequisites* are what to finish first. *Required evidence* is what to save and be ready to explain. A dash means no separate resource is needed. Time estimates cover only the activities named, and some overlap, so do not add them all together. Each module explains its own limits for live models, platforms and deployment.

<details>
<summary>Open the complete ordered capability map — all 22 checkpoints, prerequisites and evidence</summary>

| Order/ID | Capability/topic | Prerequisites | Study guide | Workbook | Estimated effort | Required evidence | Scope |
|---|---|---|---|---|---|---|---|
| 01 / AI-ENTRY-01 | Apply backend trust and retry rules to AI work | Backend programming experience | [Lesson 1 — backend rules](START-HERE.md#lesson-1--backend-rules-that-ai-work-depends-on) | — | 30–45 min; skippable | Written answers to the tenant, retry and valid-but-wrong cases | Skippable warm-up |
| 02 / AI-PY-01 | Bridge Python and build a tested API project | AI-ENTRY-01 | [SG-PY-BRIDGE-01 — Python at an engineering boundary](study-guides/python-engineering-bridge/README.md), section per unit | [Python route notebooks](workbooks/python/README.md) in order, then [W-PY-BRIDGE-04 — package checkpoint](workbooks/python/python-bridge/README.md) and [W-PY-API-01 — tested API](workbooks/python/quickcart-api/README.md) | Guide 45–60 min; notebooks about 2.5–3.25 h in full (each skippable), package 90–120 min, plus about 80 min API reading/build and 45 min independent work | Typed/validated async API, tests and clean setup | Skippable notebooks; required package and API project |
| 03 / AI-ML-01 | Explain ML and evaluate a baseline | AI-PY-01 | [SG-ML-00 — Learning from examples](study-guides/ml-foundations/docs/00-learning-from-examples.md), then [SG-ML-01 — Baselines, metrics and leakage](study-guides/ml-foundations/docs/01-baselines-metrics-and-leakage.md) | [W-ML-EVAL-01 — scikit-learn evaluation and decision](workbooks/ml/escalation-evaluation/README.md); begin [solution selection](workbooks/ml/escalation-evaluation/solution-selection.md), finishing after LLM foundations; optional no-code [W-ML-ORANGE-01 — Orange live demo](workbooks/ml/orange-experiments/README.md) | Guides 60–75 + 75–90 min reading; exercise about 3 h (20 min reading, 60 guided, 45 independent, 60 analysis and decision); selection 85-115 min total across ML/LLM foundations; demo 45–60 min in class | Leakage-aware experiment, metric interpretation and fixed-case solution/no-LLM decision | Synthetic-data experiment |
| 04 / AI-LLM-01 | Explain models/context and configure a learner environment | AI-PY-01; AI-ML-01 for complete foundations | [SG-LLM-00 — How LLMs generate text](study-guides/llm-foundations/docs/00-how-llms-generate-text.md), then [SG-LLM-01 — Designing prompts and context](study-guides/llm-foundations/docs/01-designing-prompts-and-context.md) (framework-free) | [W-LC-00 — Setup](workbooks/langchain/01-learning-workbook/00-environment-setup.md), then [W-LC-01 — foundations](workbooks/langchain/01-learning-workbook/01-foundations.md) | Guides 60–75 + 75–90 min reading; setup varies; foundations 45–60 min reading + 20–30 min exercises | Sanity check, responsibility diagram, explained limits and completed selection record (effort counted in AI-ML-01) | Framework-free concepts and environment setup |
| 05 / AI-API-01 | Implement direct provider API mechanics | AI-LLM-01 | [SG-LLM-00](study-guides/llm-foundations/docs/00-how-llms-generate-text.md) and [SG-LLM-01](study-guides/llm-foundations/docs/01-designing-prompts-and-context.md); concise reminders in the workbook | [W-LLM-API-01 — direct API refund drafts](workbooks/llm/refund-drafts/README.md), then [W-LLM-API-02 — diagnose and compare](workbooks/llm/refund-drafts/lesson-2-diagnose-and-compare.md) | Lesson 1 about 2.5 h; lesson 2 about 2.25 h; optional paid live runs about 50 min | Bounded request, inspected response and fault tests | Offline practice; live calls separately configured |
| 06 / AI-CALL-01 | Inspect model calls and prompt inputs | AI-LLM-01; AI-API-01 for direct-code comparison | Local theory in workbook | [W-LC-02 — Models/messages](workbooks/langchain/01-learning-workbook/02-models-and-messages.md), then [W-LC-03 — prompts](workbooks/langchain/01-learning-workbook/03-prompts.md) | W-LC-02 60–90 min + W-LC-03 50–70 min; provider setup additional | Inspected messages, prompt variation and failure explanation | Hosted access depends on your provider |
| 07 / AI-VALID-01 | Validate outputs and compose stages | AI-CALL-01 | Local theory in workbook | [W-LC-04 — Structured output](workbooks/langchain/01-learning-workbook/04-structured-output.md), then [W-LC-05 — chains](workbooks/langchain/01-learning-workbook/05-chains-and-runnables.md) | W-LC-04 65–90 min + W-LC-05 70–90 min | Schema and evidence checks; diagnosed stage failure | Practice rejecting invalid and unsupported outputs |
| 08 / AI-STATE-01 | Isolate and bound conversation state | AI-VALID-01 | [SG-SCALE-01 — Stateless reasoning](study-guides/cloud-architecture-patterns/scalability-patterns/docs/01-stateless-services.md), preceded by its linked foundations as needed | [W-LC-06 — History](workbooks/langchain/01-learning-workbook/06-conversation-history.md) | SG-SCALE-01 50–70 min (SG-SCALE-00 45–60 min if needed); W-LC-06 70–90 min | Session-isolation probe and retention explanation | Session isolation and bounded history |
| 09 / AI-RETRIEVE-01 | Compare embeddings, chunking and retrieval | AI-PY-01 for offline checkpoint; AI-STATE-01 and model helper for framework route | [SG-RAG-00 - Retrieval foundations](study-guides/retrieval-foundations/README.md) | [W-RAG-03-06 - offline retrieval checkpoint](workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/README.md), then [W-LC-07 — Embeddings](workbooks/langchain/01-learning-workbook/07-embeddings-and-similarity.md), then [W-LC-08 — retrieval](workbooks/langchain/01-learning-workbook/08-documents-and-retrieval.md)  Optional after grounded controls: [bounded reranking](workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/reranking-comparison.md). | Guide 50-65 min; offline checkpoint about 2.25 h plus [knowledge lifecycle](workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/knowledge-lifecycle.md) 150-195 min after W-RAG-05; W-LC-07 70–90 min + W-LC-08 100–130 min; optional live indexing additional  Optional reranking 60-90 min. | Ranking comparison, source metadata, incremental/rebuild and quarantine/deletion checks | Offline mechanics and a separate learned-model route |
| 10 / AI-RAG-01 | Ground answers and resolve follow-ups | AI-RETRIEVE-01 | [SG-RAG-01 - Permissions and grounding](study-guides/retrieval-foundations/permissions-and-grounding.md), then [SG-RAG-02 - RAG evaluation](study-guides/retrieval-foundations/rag-evaluation.md) before W-RAG-09 | [Guided offline RAG build](workbooks/langchain/02-rag-capstone-workbook/README.md), then [W-LC-09 — Grounded RAG](workbooks/langchain/01-learning-workbook/09-grounded-rag.md), then [W-LC-10 — conversational RAG](workbooks/langchain/01-learning-workbook/10-conversational-rag.md) | SG-RAG-01 35-45 min; SG-RAG-02 75-90 min; new guided controls 3-4 h and independent transfer 2-3 h; W-LC-09 90–120 min + W-LC-10 90–120 min | Separate evidence/answer review, ACL/deletion tests and independent recall transfer | Offline reference; model quality evaluated separately |
| 11 / AI-TOOLS-01 | Inspect typed tools and bounded execution | AI-VALID-01, AI-RAG-01 trust context | Local theory in workbook | [W-LC-11 — Tools and agents](workbooks/langchain/01-learning-workbook/11-tools-and-agents.md) | W-LC-11 100–130 min | Invalid/denied/failure/loop checks and authorization explanation | Bounded tool execution |
| 12 / AI-EVAL-01 | Build an interface and diagnose/evaluate behavior | AI-RAG-01, AI-STATE-01 | Local theory in workbook | [W-LC-12 — Interfaces](workbooks/langchain/01-learning-workbook/12-streaming-and-interfaces.md), then [W-LC-13 — testing/evaluation](workbooks/langchain/01-learning-workbook/13-debugging-testing-and-evaluation.md) | W-LC-12 100–130 min + W-LC-13 110–150 min | Repeatable tests, per-case evaluation and failure repair | Repeatable testing and diagnosis |
| 13 / AI-INTEGRATE-01 | Assemble and independently modify the notes assistant | AI-TOOLS-01, AI-EVAL-01; core chapters 00–13 | [Project starting states](workbooks/langchain/docs/project-boundaries.md) | [W-LC-15 — Integration](workbooks/langchain/01-learning-workbook/15-guided-integration-lab.md), [W-LC-16 — practice](workbooks/langchain/01-learning-workbook/16-practice-challenges.md), [W-LC-17 — assessment](workbooks/langchain/01-learning-workbook/17-revision-and-assessment.md) | 2–3 h build + 3–5 h practice + 2–3 h assessment | Independent change, reproducible checks and defended limitations | Independent module practice |
| 14 / AI-RELIABLE-01 | Establish production reliability and permission-aware RAG | AI-API-01, AI-INTEGRATE-01 | [SG-REL-00 — Reliable model calls](study-guides/llm-reliability/docs/00-reliable-model-calls.md); [control boundaries and limits](docs/production-controls-review.md) | [W-LLM-REL-01 — reliable drafting simulator](workbooks/llm/reliable-drafting/README.md); [W-LLM-ACT-01 — safe actions](workbooks/llm/safe-actions/README.md); [offline controls](workbooks/reliability/offline-controls/README.md); [W-LLM-EVAL-01 - versioned evaluation](workbooks/llm/eval-harness/README.md) with [human-review calibration](workbooks/llm/eval-harness/human-review-calibration.md); [Permission-aware RAG reference](workbooks/langchain/02-rag-capstone-workbook/README.md) | SG-REL-00 75–90 min; W-LLM-REL-01 about 2.5 h; W-LLM-ACT-01 about 2.3 h; controls supplement 90 min; evaluation about 2.75 h plus calibration 120-165 min (second reviewer 30-45 min when available); the RAG reference is counted in AI-RAG-01 | Budgets/cancellation/idempotency, tenant ACL/deletion tests and held-out retrieval/answer reports | Offline controls; real-model evidence required for final delivery |
| 15 / AI-GRAPH-01 | Persist, approve and recover stateful workflows | AI-RELIABLE-01 | [SG-GRAPH-00 - Stateful orchestration](study-guides/stateful-orchestration/README.md) | [W-GRAPH-01 - Durable approval/recovery](workbooks/langgraph/approval-workflow/README.md); optional [W-LC-14 introduction](workbooks/langchain/01-learning-workbook/14-langgraph-and-langsmith.md) | Guide 40-55 min; guided/diagnosis about 95 min; independent extension 60-90 min; optional intro 70-100 min | Cross-process checkpoints, current approval/revocation, idempotent crash recovery, quorum transfer and sequential comparison | Local persistence and simulated effects |
| 16 / AI-INTERFACE-01 | Compare Agents SDK and MCP boundaries | AI-TOOLS-01, AI-RELIABLE-01 | [SG-INTERFACE-00 - Tool interfaces](study-guides/tool-interfaces/README.md) | [W-AGENTS-01 - SDK tool loop/local tracing](workbooks/agents-sdk/tool-loop/README.md), then [W-MCP-01 - local client/server](workbooks/mcp/stock-server/README.md) | Guide 40-55 min; SDK about 95 min; MCP about 110 min including independent work | Actual SDK loop/protocol evidence, authorization/result tests, bounded execution and architecture decision | Scripted model and local MCP transport |
| 17 / AI-AUTOMATE-01 | Integrate selectively with n8n | AI-RELIABLE-01 | Local mechanism/trade-off explanation in workbook | [W-N8N-01 - Review-event integration](workbooks/n8n/review-integration/README.md) | About 125 min including independent selective-retry work; installation varies | Native workflow, idempotent retry/denial evidence, ownership and visual-versus-code decision | Local visual integration; UI/Docker checks remain unverified |
| 18 / AI-DELIVER-01 | Package and automate delivery | AI-PY-01 including the [W-PY-API-01 project](workbooks/python/quickcart-api/README.md), AI-RELIABLE-01 | Local concepts in workbook | [W-ENG-DELIVERY-01 — deliver and recover the API](workbooks/delivery/README.md), then [measured serving](workbooks/delivery/serving-under-load.md) and [customer rehearsal](workbooks/delivery/customer-rehearsal.md) | 25 min reading, 75 guided, 45 independent; first downloads extra; serving 150-210 min; customer rehearsal 75-105 min, including 15 min reused from delivery (60-90 min net addition) | Container boundaries, reviewed Compose change, release bundle, failed-start recovery, bounded HTTP load/recovery, simulated acceptance/adoption plan and cleanup | Local containers; hosted CI remains unverified |
| 19 / AI-AWS-01 | Deploy through one AWS/Bedrock path | AI-DELIVER-01 and AI-RELIABLE-01; local workbook prerequisites permit preliminary offline study | [SG-AWS-00 - Bounded Bedrock delivery](study-guides/aws-bedrock-delivery/README.md), plus linked queue/scalability patterns | [W-AWS-01 - Queued Bedrock draft worker](workbooks/aws/bedrock-worker/README.md) | Guide 40-55 min; local 80 min; authorized live route 60-90 min; independent design 45 min; setup varies | IAM/cost review, actual deployment/model/health/teardown evidence or explicit pending record | Offline preparation; cloud deployment remains unverified |
| 20 / AI-OPS-01 | Evaluate releases and recover incidents | AI-AWS-01; AI-RELIABLE-01 for W-LLM-EVAL-01; workbook permits preliminary offline study after evaluation/delivery | [SG-OPS-00 — ML lifecycle and application operations](study-guides/application-llmops/README.md); existing architecture case/comparison as references | [W-OPS-01 — Release monitoring and incident recovery](workbooks/operations/release-watch/README.md), including [application-governance evidence](workbooks/operations/release-watch/application-governance.md) | Guide 40–50 min; workbook 3 h including setup, independent slice gate, defense and repair plus governance 45-75 min | Versioned reports, redacted telemetry, rollout halt, restored artifact, recovery probes, runbook amendment and independent slice regression | Synthetic monitoring and incident exercise |
| 21 / AI-CAP-01 | Deliver an integrated independent capstone | AI-RELIABLE-01 through AI-OPS-01 as applicable to brief | Existing grounding, reliability and operations guides linked at need; [architecture/threat decisions](workbooks/capstone/merchant-support/design.md) | [W-CAP-01 — guided merchant support](workbooks/capstone/merchant-support/README.md), then [W-CAP-02 — independent changed delivery](workbooks/capstone/merchant-support/06-independent-delivery.md) | 24 h guided/evidence + 12 h independent + 4 h defense/repair reserve within phase 6 | Reproducible repository, real-model/deployment evidence, threat model, decisions, costs, incident, handover and individual defense | Local container reference; live review and independent delivery required |
| 22 / AI-DEFEND-01 | Defend ownership and repair essential gaps | AI-CAP-01 for final defense; stage practice follows each local prerequisite | [Revision/glossary](workbooks/defense/revision-and-glossary.md), existing architecture challenges at need | [W-DEFEND-01 — stage practice and individual defense](workbooks/defense/README.md), [seven-dimension repair/reassessment](assessments/defense-and-remediation.md); optional [Architect foundation map](docs/architect-foundations.md) | Final route 11 h including the shared 4 h defense/repair reserve; stage practice replaces existing reflection/independent activity | Individual explanation, reviewer-revealed change, actual tests/diagnosis, seven-dimension evidence and targeted reassessment | Practice available; final defense requires a reviewer |

The [W-LC-18 — glossary](workbooks/langchain/01-learning-workbook/18-glossary.md) and [shared synthetic materials](workbooks/langchain/01-learning-workbook/shared-materials.md) support the available build rows throughout. The [SG-SCALE-12 — scalability revision](study-guides/cloud-architecture-patterns/scalability-patterns/docs/12-quick-revision.md) and [SG-SCALE-13 — glossary](study-guides/cloud-architecture-patterns/scalability-patterns/docs/13-glossary.md) support architectural reasoning. Their reference role does not add new compulsory build projects. Deeper Architect extensions remain separately scoped; the two reference sample-project folders are not map prerequisites or evidence sources for completion.

</details>

## Effort and assessment meaning

Plan for about **12 hours of active study a week for 26 weeks (312 hours)**. That includes preparation, building, testing, the defense and fixing gaps. It is an estimate, not a measured or guaranteed timetable. Some module estimates overlap, so do not count the same work twice. The [six-month workload plan](docs/six-month-course-plan.md) explains the reserve time.

The [public assessment index](assessments/README.md) lists the criteria. Checking your own work, finishing a module and having a reviewer confirm your skills are three different things. Copying a reference solution or AI-generated code does not prove you own the work: explain your decisions, say what help you used and complete the changed tasks. Some failures cannot be made up for by high marks elsewhere: leaking data someone was not allowed to see, letting execution run without limits, exposing secrets or inventing evidence.

Use the [capstone evidence brief](assessments/capstone-evidence.md) to put together your final submission. Offline tests show that your controls behave correctly; a real-model evaluation and accepted deployment evidence are separate requirements. You can practise and check your own work alone, but the final defense and an independent assessment need a reviewer. Access to this repository does not include grading, mentoring or certification; see [learning paths and support](docs/learning-paths-and-support.md).

### Stable unit identifiers

Use this index to find a workbook or reference by its ID. The [chapter index](docs/lesson-id-map.tsv) maps each ID to its lesson file. Note the unit and capability IDs with your work so you can find your way back.

<details>
<summary>Find a study guide or workbook by unit ID</summary>

| Unit IDs | Parent capability / use | Availability |
|---|---|---|
| W-LC-00 through W-LC-18 | Per-chapter AI capability in the ID map; [workbook entry](workbooks/langchain/01-learning-workbook/README.md) and [LangChain landing page](workbooks/langchain/README.md); use chapter-local prerequisites | Chapter 14 is optional |
| W-DEFEND-01 | AI-DEFEND-01: [defense/revision/practice](workbooks/defense/README.md), [repair/reassessment](assessments/defense-and-remediation.md) | Self-study practice and reviewer-led final defense |
| W-CAP-01, W-CAP-02 | AI-CAP-01: [integrated reference](workbooks/capstone/merchant-support/README.md), [independent delivery](workbooks/capstone/merchant-support/06-independent-delivery.md) | Local reference plus independent changed brief |
| SG-OPS-00, W-OPS-01 | AI-OPS-01: [lifecycle/operations](study-guides/application-llmops/README.md), [monitoring and recovery](workbooks/operations/release-watch/README.md) | Synthetic monitoring and recovery |
| SG-AWS-00, W-AWS-01 | AI-AWS-01: [concepts](study-guides/aws-bedrock-delivery/README.md) and [SAM queue worker](workbooks/aws/bedrock-worker/README.md) | Offline preparation; cloud execution requires access and budget |
| W-N8N-01 | AI-AUTOMATE-01: [selective visual integration](workbooks/n8n/review-integration/README.md) with Python-owned schema/identity/idempotency | Local integration with Python-owned controls |
| SG-INTERFACE-00, W-AGENTS-01, W-MCP-01 | AI-INTERFACE-01: [concepts](study-guides/tool-interfaces/README.md), [Agents SDK](workbooks/agents-sdk/tool-loop/README.md) and [MCP](workbooks/mcp/stock-server/README.md) | Scripted SDK model and local MCP server |
| SG-GRAPH-00, W-GRAPH-01 | AI-GRAPH-01: [concepts](study-guides/stateful-orchestration/README.md) and [durable approval workflow](workbooks/langgraph/approval-workflow/README.md) | Local persistence and simulated effects |
| W-LC-MECH-01 | AI-INTEGRATE-01: [selected LangChain mechanisms](workbooks/langchain/01-learning-workbook/mechanisms-lab/README.md), with [chapter contracts](workbooks/langchain/01-learning-workbook/lesson-contract.md) | Focused offline comparison |
| SG-SCALE-00 through SG-SCALE-13 | State, AWS, operations and defense references as mapped | Reference reading at need |
| SG-RAG-00, W-RAG-03 through W-RAG-06 | AI-RETRIEVE-01: [retrieval foundations](study-guides/retrieval-foundations/README.md) and [offline retrieval lab](workbooks/langchain/02-rag-capstone-workbook/retrieval-lab/README.md) | Offline retrieval mechanics |
| W-LLM-EVAL-01 | AI-RELIABLE-01: [versioned evaluation harness](workbooks/llm/eval-harness/README.md), frozen development selection, held-out slices and non-compensable regression gates | Synthetic evaluation; real-model quality assessed separately |
| W-LLM-ACT-01 | AI-RELIABLE-01 and AI-TOOLS-01: [safe actions](workbooks/llm/safe-actions/README.md): strict tool arguments, trusted authorization and approval, durable outbox, idempotent dispatch under ambiguous timeouts and crashes | Simulated tools and services |
| SG-REL-00, W-LLM-REL-01 | AI-RELIABLE-01: [reliability guide](study-guides/llm-reliability/docs/00-reliable-model-calls.md) and [virtual-time drafting simulator](workbooks/llm/reliable-drafting/README.md) | Virtual-time provider simulation |
| SG-LLM-00, SG-LLM-01 | AI-LLM-01: tokens, generation, sampling, context limits, capability limits, prompt and context design, injection | Framework-free concepts |
| SG-ML-00, SG-ML-01 | AI-ML-01: learning, features, splits, overfitting, baselines, metrics and leakage | Conceptual foundations |
| W-LLM-API-01, W-LLM-API-02 | AI-API-01: [direct provider API project](workbooks/llm/refund-drafts/README.md) and its [diagnosis and prompt-comparison lesson](workbooks/llm/refund-drafts/lesson-2-diagnose-and-compare.md) | Offline practice; live calls separately configured |
| W-ML-EVAL-01 | AI-ML-01: [scikit-learn evaluation exercise](workbooks/ml/escalation-evaluation/README.md); required evidence | Synthetic-data evaluation |
| W-ML-ORANGE-01 | AI-ML-01: [Orange live demo](workbooks/ml/orange-experiments/README.md) for non-coding audiences; optional, not required evidence | Optional visual demonstration |
| W-RAG-00 through W-RAG-13, SG-RAG-01, SG-RAG-02 | AI-RAG-01 / AI-RELIABLE-01 / AI-CAP-01: [guided RAG module capstone](workbooks/langchain/02-rag-capstone-workbook/README.md), [permission/grounding concepts](study-guides/retrieval-foundations/permissions-and-grounding.md) and [RAG evaluation concepts](study-guides/retrieval-foundations/rag-evaluation.md) | Offline build; live model and deployment assessed separately |
| W-LC-REF-01 | Overlapping standalone reference route | Reference only |
| W-PY-CONCEPT-01 | AI-PY-01: [output-cleared validation notebook](workbooks/python/01-validation-concepts.ipynb) | Optional notebook; interactive Colab unverified |
| SG-PY-BRIDGE-01, W-PY-BRIDGE-01 through W-PY-BRIDGE-04 | AI-PY-01: [concept guide](study-guides/python-engineering-bridge/README.md), [Python bridge route](workbooks/python/README.md) — three notebooks and the [package checkpoint](workbooks/python/python-bridge/README.md) | Skippable notebooks followed by a required package checkpoint |
| W-PY-API-01 | AI-PY-01: [tested QuickCart ticket API](workbooks/python/quickcart-api/README.md); required before AI-DELIVER-01 and AI-AWS-01 | Required tested API project |
| W-RELIABILITY-01 | AI-RELIABLE-01: [controls lab](workbooks/reliability/offline-controls/README.md) | Offline controls exercise |
| W-ENG-DELIVERY-01 | AI-DELIVER-01: [package, release and recover the API](workbooks/delivery/README.md) | Local delivery; hosted CI remains unverified |
| W-DELIVERY-01 | AI-CAP-01: [delivery records](assessments/engineering-delivery-artifacts.md) | Delivery records to create |
| W-CAP-EVIDENCE-01 | AI-CAP-01 / AI-DEFEND-01: [evidence brief](assessments/capstone-evidence.md) | Submission and review criteria |

</details>
