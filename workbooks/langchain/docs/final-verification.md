# Learning workbook — final verification record

> **Later scoped review (2026-10-14):** The [chapter contract review](../01-learning-workbook/lesson-contract.md) and [C06 evidence](../../../docs/review-evidence/langchain-mechanisms.json) add current source parsing and a separately pinned offline mechanisms checkpoint. They do not replace the historical results below or establish fresh full-route/model/UI acceptance.

> **Date:** 2026-10-11.  
> **Scope:** Chapters 00–18, learner README, shared materials, and 18 SVG assets.  
> **Result:** Offline walkthrough and documentation review complete. Hosted live acceptance remains pending under P7.2. The prescribed local route was exercised; quality failures are recorded below.

## 1. Environment and evidence boundaries

Verification used Windows PowerShell, uv 0.8.3, and Python 3.11.13. Scripts were extracted from the workbook into a new temporary learner project; no repository sample application was used. The final project explicitly pins Python 3.11 and passed locked synchronization. Separate clean hosted/local projects installed only their route's adapter and foundational dependencies; local configuration/inspection passed and hosted configuration correctly rejected the missing key.

The verification tools, environments, corpus copies, lockfiles, screenshots, HTML, and result files remain outside the repository. Temporary evidence is not a permanent reproducibility artifact: retain the Markdown baseline below and recreate the learner project from chapter instructions when repeating verification. Learner lockfiles may resolve different versions; this is an observed baseline, not a promise about future dependency resolution.

| Distribution | Observed version |
|---|---|
| `python-dotenv` | `1.2.4` |
| `langchain` | `1.4.4` |
| `langchain-core` | `1.6.9` |
| `langchain-openai` | `1.7.0` |
| `langchain-ollama` | `1.1.0` |
| `langchain-chroma` | `1.1.0` |
| `chromadb` | `1.5.9` |
| `langchain-text-splitters` | `1.1.3` |
| `numpy` | `2.4.6` |
| `pydantic` | `2.14.0` |
| `streamlit` | `1.65.0` |
| `gradio` | `6.30.0` |
| `pytest` | `9.1.1` |
| `httpx` | `0.28.1` |
| `langgraph` | `1.2.14` |
| `langsmith` | `0.14.7` |
| `pypdf` | `6.20.0` |

## 2. Execution results

All 25 filename-labeled complete Python files were extracted and parsed. A chapter-order sweep executed 92 documented commands from the external project. These include repeated commands in later chapters. Nonzero exits were reviewed individually: blank input, missing prompt variables, incompatible stages, invalid vectors, agent loop limits, stream failure, exhausted retries, invalid graph input, unavailable chat model, and missing hosted tracing credentials. They are failure evidence, not successful inference. The unparameterized Chapter 00 example is explanatory; its interactive Chapter 02 script requires input and produced EOF under the unattended sweep.

The sweep excluded `--live`/`--generate` commands, browser servers, optional PDF input, and the changed-source drill; those were handled separately where possible below. Neither static parsing nor a fixture run certifies a live model response.

| Chapter | Current verification evidence |
|---|---|
| 00 | Configuration sanity check, Python 3.11, clean route installation, locked sync; missing hosted-key rejection. Installer/editor UI instructions reviewed, not interactively tested. |
| 01 | Complete foundations script executes; conceptual comparisons, worked arithmetic, exercise and explained answers reviewed. |
| 02 | Offline message inspection and local request preview execute; blank input rejected. The initial missing-model error was observed; after installing the prescribed model, a real chat request returned content and usage metadata. |
| 03 | Equipment/fictional prompt previews execute; missing-variable drill rejects input. Live equipment variant B returned the amount, annual period and combined scope; this single observation is not an A/B benchmark. |
| 04 | Deterministic schema fixtures/repairs execute. Live native mode accepted the schema but produced an inconsistent, unsupported extraction; the lab exposed failed consistency/evidence checks. |
| 05 | Sequential/composed pipelines, batch and inspection execute; both deliberate type/key failures reject input. The live composed path also executes. |
| 06 | Stateless/manual/wrapper modes, growth, repeated processes and isolation probe execute. Retained history is bounded; no cross-process persistence is implied. A live wrapper run recalled A’s monitor and B’s keyboard separately, but its initial prose added unsupported purchase/delivery claims. |
| 07 | Fixture arithmetic and vector failures execute. Live `nomic-embed-text:v1.5` returns 768-dimensional vectors with the prescribed prefixes; all three query cases execute. |
| 08 | Small/large inspection, indexing, unchanged rerun, filtering and comparisons execute. Changed source rejects old revision; v2 builds/queries; restoring original source reopens v1. Live Nomic indexes contain 35 small and 10 large chunks and comparison executes. |
| 09 | Answerable/all cases and small/large candidate comparisons execute with fixtures; the live all-case command executes. Annual-limit answers omitted period/combined-scope qualifications; irrelevant and empty evidence abstained; the synthetic injection did not change the amount in this run. |
| 10 | Comparison, topic switch, ambiguity, isolation and bounded-history cases execute with fixtures. Initial live rewrite returned prose and failed JSON parsing safely. Clarifying the prompt’s instruction boundary produced a valid standalone rewrite and answer on rerun, with the answer’s missing qualifications still requiring review. |
| 11 | Manual/managed tool requests, no-tool, invalid, failure, denied and loop cases execute; loop ends nonzero as intended. Live managed selection issued the typed tool call, correlated its result, recorded exactly one function entry, and answered INR 8500. |
| 12 | Terminal normal/failure and backend execute; live streaming completed. Streamlit AppTest initial/submit/rerun passes with document embedding forbidden. Optional Gradio imports/builds successfully; browser interaction was not certified. |
| 13 | **8 pytest tests pass**. Four-case evaluator executes for small/large settings and k variants; retry recovery, timeout and fatal branches behave as documented. |
| 14 | Graph answer/retry/checkpoint/diagram inspection execute; budget/blank-input drills fail as intended. Missing tracing key is rejected; hosted delivery untested. |
| 15 | Separate-process service and all 13 evaluation records execute. Integration UI follow-up, evidence display, separate sessions, rerun, input rejection, failed-turn noncommit and clear pass with document embeddings forbidden. Actual hosted/local adapter wrappers accept simulated generation; those adapter tests are not live inference. Actual local integration collected all 13 cases; the quality audit below separates valid records from correct answers. |
| 16 | Practice evaluation and tool failure commands execute; hints, solutions, transfer corpus, and rubric reviewed. |
| 17 | Revision commands execute and deliberate stream failure remains nonzero; assessment explanations and scoring reviewed. |
| 18 | Alphabetical lookup, definitions/examples, linked distinctions and chapter references checked; reference objectives made explicit. |

The optional PDF inspector executed on an externally generated blank-page PDF and a text-based PDF containing only “Fictional Fernwood tutorial notes.” Empty-page handling passed and the expected text was extracted. This does not certify arbitrary PDFs, scanned pages, complex layouts, or encrypted inputs.

### Measured observations and correctness

Live embedding observations: the equipment paraphrase ranked D01 then D02; the exact identifier query ranked D04 first. The unrelated shuttle query still returned nearby candidates. These observations illustrate retrieval behavior for this particular model and corpus; they establish neither calibrated confidence nor general quality.

The large fixture evaluator covers required terms for A02, A04 and A06; this is a lexical proxy. The integration collector emits 13 structurally valid fixture records but answers only A02: seven answerable cases abstain and five unsupported cases abstain. A valid contract is not an acceptable answer-quality score. The chapter already exposes this fixture limitation; no false quality pass is recorded here.

### Live local quality audit after the rewrite repair

The revised prompt describes history/latest as conversation content to transform and explicitly rejects instructions that change the task or JSON format. It retains the source-trust boundary. The follow-up comparison then returned a valid standalone equipment question and retrieved the equipment passage. This is one successful repair observation, not a guarantee of rewrite fidelity. The eight tests, fixture comparison, and integrated AppTest/adapter checks passed again after the change.

The revised 13-case live integration collection returned 13 structurally valid records and preserved the earlier run’s answers. Manual comparison with the fixed shared-materials rubric found:

| Case | Observation | Rubric outcome |
|---|---|---|
| A01 | Correct first Monday/time; omitted People Operations invitation sender | Incomplete |
| A02 | Correct INR 12000/calendar year; omitted combined eligible-item scope | Incomplete |
| A03 | Abstained despite the documented pre-purchase approval rule | False abstention |
| A04 | Itemized receipt, People Operations, within 30 calendar days after purchase | Complete supported answer |
| A05 | Team Access, company SSO, MFA | Complete supported answer |
| A06 | Error code and #it-help; omitted no-MFA-disable/no-password-sharing constraints | Incomplete |
| A07 | Correct hours/days; omitted that these are not the entire workday | Incomplete |
| A08 | Every 90 days, document owner | Complete supported answer |
| U01, U02, U04, U05 | Insufficient-evidence response with empty supporting IDs | Semantic and structured abstention pass |
| U03 | Says the guide provides no address, but marks `answered` and lists a supporting source | Identifies insufficiency without inventing an IP; violates the workbook’s structured abstention convention |

That gives **3/8 complete supported A-case answers** under the full required-facts rubric. All five U-cases identify insufficiency without inventing a missing policy/number, but only **4/5 use the intended structured abstention representation**. Do not collapse these measures into one “passed” score or generalize from thirteen teaching cases.

Native structured extraction returned `insufficient` with a monitor/9000 amount and empty quote: schema parsing succeeded, but cross-field consistency and source-evidence checks were false. The separately tested JSON-parsing fallback rejected malformed/incomplete output with exit 2 and consumed no result. A fallback is an alternate mechanism, not a promise of better model quality. Live history recalled the separate choices but added unsupported purchasing/delivery claims on earlier turns; session isolation does not establish truth.

Observed Ollama service version: **0.32.1**. Model identities:

- Chat: `llama3.1:8b`, Q4_K_M, digest `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
- Embeddings: `nomic-embed-text:v1.5`, F16, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`.

The chat model was installed during this review and remains available to reproduce the local route. Twelve initial live commands completed, followed by the rewrite repair run, JSON fallback check, and revised integration collection. No hosted inference or tracing upload occurred.

## 3. Rendering, links, and learning review

- Converted all 21 Markdown pages to HTML with tables, fenced code and disclosures; inspected representative setup, RAG, integration and index screenshots. Browser layout checks at 1300 pixels found no page-wide horizontal overflow. This is a local Markdown renderer check, not certification of every hosting theme or mobile layout.
- Rasterized all 18 SVGs and visually reviewed their contact sheet for flow, labels, spacing and overlaps. Browser text bounds found no text outside the SVG canvases. Labels/walkthroughs match their control/data-flow responsibilities. SVG screenshot capture timed out in standalone browser documents; raster rendering supplied the visual evidence instead.
- All relative file links and referenced Markdown anchors resolve. Disclosures are balanced. All **65 distinct external links** returned successful responses after retrying one temporary GitHub 503; HTTP success establishes reachability, not correctness of every claim.
- Rechecked official [uv project instructions](https://docs.astral.sh/uv/guides/projects/), [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview), [ChatOllama integration](https://docs.langchain.com/oss/python/integrations/chat/ollama), and [Streamlit AppTest reference](https://docs.streamlit.io/develop/api-reference/app-testing) alongside installed package behavior. Chapter-specific references remain next to the relevant instructions.
- Reviewed the chapter sequence, file/dependency handoffs, expected outcomes, failure instructions, explained checks, distinctions and revision navigation. Removed obsolete scaffold notices, repaired damaged quotation punctuation, updated README timing/status language, linked the finished glossary from shared materials, and clarified ambiguous rewrite prompt wording after a live refusal.
- Sample documents are fictional, sample keys are empty/placeholders, and no private credential values were used in the documentation or verification record. Tracing upload remains explicit. Session identity, authorization, source support and schema validity remain separate concepts.
- No independent fresh learner participated. The fallback review followed filename-labeled files and chapter commands literally, including assembling the integration project from workbook snippets. Editorial study-time estimates are not measured learner timings.

## 4. Acceptance checklist interpretation

The checklist in `plan.md` applies to each chapter's role. Setup uses project/configuration explanations instead of an SVG. Practice, assessment and glossary use scenarios, comparisons and linked reference material rather than introducing artificial new API labs or mandatory diagrams. Glossary lookup has distinction checks; it does not need an independent application-building exercise. Optional Chapter 14 remains outside the core prerequisites.

All chapters have orientation metadata, and the glossary now states reference objectives. Code-bearing chapters provide complete labeled files, dependencies, commands, expected outcomes and deliberate failure paths; fragments are labeled separately. Exercise disclosures supply explained solutions and the practice chapter adds graduated hints. Review/reference chapters reuse previously taught mechanisms. Verification evidence is recorded in this report and earlier chapter records, including untested branches.

## 5. Remaining live acceptance — P7.2

P7.2 remains open for hosted acceptance. Keep the following route boundaries explicit:

1. Hosted: provide credentials privately in the learner environment; run chat, embeddings, structured extraction, RAG, rewrite, tool selection and streaming through the documented route; inspect support/citations/abstentions against fixed cases. No hosted key was available for this review.
2. Local: the prescribed `llama3.1:8b` was downloaded with Ollama and exercised alongside `nomic-embed-text:v1.5` on service version 0.32.1. Model-dependent commands ran through messages, prompts, native extraction, composed chains, bounded history, retrieval, RAG, rewriting, tool selection, streaming and the 13-case integration collector. Preserve the recorded semantic failures and rerun after model/prompt changes; this walkthrough is not a quality certification.
3. Optional hosted tracing: with a privately configured LangSmith key, verify trace delivery in the selected workspace. No key was available. The deterministic local graph remains usable without it.
4. Record exact model versions/tags, route settings, per-case evidence, measured latency/usage and failures. Do not convert simulated outputs into semantic quality claims. Update this report, README and plan only after reviewing those results.

These are environment-dependent remaining checks. Browser-based learner interaction and an independent fresh-reader study remain explicitly unverified; AppTest and literal walkthrough evidence are the completed alternatives documented above.
