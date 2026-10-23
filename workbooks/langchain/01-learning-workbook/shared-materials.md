# Shared Learning Materials — Fernwood Notes Assistant

> **Purpose:** A reusable fictional corpus, fixed evaluation cases, and lab notebook for the learning workbook. These are reference materials, not an extra required chapter.

Fernwood Labs is fictional. These rules are invented for learning and do not describe real employment policies. No external dataset or existing repository sample application is required.

## 1. Create the learner documents when instructed

In the documents-and-retrieval chapter, create a `knowledge` directory inside your own `langchain-learning` project and save the five files below as UTF-8 text. Do not create them inside the workbook repository. Earlier prompt lessons may use individual passages directly.

Keep the source ID, effective date, and section labels in each file. Later loading code will preserve the filename and extract the source ID into metadata. Dates are contextual information; this initial corpus deliberately has no superseded or conflicting versions.

### File: `knowledge/team-handbook.txt`

```text
Source ID: FW-HANDBOOK-001
Title: Fernwood Team Handbook
Effective date: 2026-01-01
Status: Current

Section: Onboarding
New team members attend orientation on their first Monday at 09:30 India Standard Time. The People Operations team sends the invitation.

Section: Help channels
For onboarding questions, contact People Operations through the fictional channel #people-help. For laptop or VPN problems, use #it-help. Do not send passwords or access tokens in either channel.

Section: Handbook boundary
This handbook describes onboarding and help channels only. It does not define compensation, retirement benefits, or parental leave.
```

### File: `knowledge/equipment-policy.txt`

```text
Source ID: FW-EQUIPMENT-001
Title: Fernwood Equipment Policy
Effective date: 2026-01-01
Status: Current

Section: Home-office allowance
Each employee may request reimbursement of up to INR 12000 per calendar year for a monitor, keyboard, or ergonomic chair. This is one combined annual limit, not a separate limit for each item.

Section: Approval and evidence
Obtain manager approval before purchasing. Submit the itemized receipt to People Operations within 30 calendar days after purchase. Approval does not remove the receipt requirement.

Section: Exclusions
Personal phones and gaming consoles are not eligible under this policy. This document does not define company-laptop replacement intervals.
```

### File: `knowledge/vpn-guide.txt`

```text
Source ID: FW-VPN-001
Title: Fernwood VPN Setup Guide
Effective date: 2026-01-01
Status: Current

Section: Prerequisites
Use a company-managed laptop. Request VPN access through #it-help before attempting connection. A personal laptop is not an approved device for this exercise.

Section: Connection steps
Open the fictional Fernwood Connect application. Select the profile named Team Access. Sign in using company single sign-on and approve the multi-factor authentication request.

Section: Troubleshooting
If sign-in succeeds but the connection fails, record the error code and contact #it-help. Never disable multi-factor authentication or share a password to work around a connection failure. No VPN server address is provided in this guide.
```

### File: `knowledge/remote-work-faq.txt`

```text
Source ID: FW-REMOTE-001
Title: Fernwood Remote Work FAQ
Effective date: 2026-01-01
Status: Current

Section: Shared collaboration hours
The team's shared collaboration hours are 14:00 to 16:00 India Standard Time, Monday through Thursday. These are collaboration hours, not a statement of the entire working day.

Section: Meeting changes
If you cannot attend a scheduled meeting, notify the organizer before it starts and provide a short written update. Do not infer a leave entitlement from this meeting rule.

Section: Location changes
Discuss a temporary working-location change with your manager before making arrangements. This FAQ does not specify countries where cross-border work is permitted.
```

### File: `knowledge/documentation-guide.txt`

```text
Source ID: FW-DOCS-001
Title: Fernwood Documentation Guide
Effective date: 2026-01-01
Status: Current

Section: Note structure
Every internal procedure note should include a title, owner, effective date, prerequisites, numbered steps, and a verification check.

Section: Review cycle
The document owner reviews each procedure note every 90 days. A review checks whether the steps and verification result are still accurate.

Section: Sensitive information
Use fictional examples when preparing a public tutorial. Never include real API keys, passwords, customer records, or private employee information. This guide does not define a company-wide retention period.
```

## 2. Fixed evaluation cases

Use these same cases before and after a change. Answerable cases require all listed facts and supporting evidence. Matching prose word-for-word is unnecessary. Unsupported cases require abstention, not a plausible guess. Explicit statements that a policy is absent support abstention, not an invented benefit or rule.

| ID | Question | Answerable | Expected facts or behavior | Required source and section | Why it exists |
|---|---|---|---|---|---|
| A01 | When is orientation, and who sends the invitation? | Yes | First Monday, 09:30 IST; People Operations | FW-HANDBOOK-001 / Onboarding | Multiple facts in one passage |
| A02 | What is the annual home-office reimbursement limit? | Yes | INR 12000 per calendar year; combined across eligible items | FW-EQUIPMENT-001 / Home-office allowance | Preserve amount, currency, period, scope |
| A03 | Can I buy a monitor first and request approval afterward? | Yes | No; manager approval is required before purchase | FW-EQUIPMENT-001 / Approval and evidence | Distinguish approval timing |
| A04 | What do I submit for equipment reimbursement, and by when? | Yes | Itemized receipt to People Operations within 30 calendar days after purchase | FW-EQUIPMENT-001 / Approval and evidence | Evidence and deadline |
| A05 | Which VPN profile do I select, and how do I authenticate? | Yes | Team Access; company SSO plus MFA | FW-VPN-001 / Connection steps | Exact identifier and sequence |
| A06 | What should I do if VPN sign-in succeeds but connection fails? | Yes | Record error code; contact #it-help; do not disable MFA or share passwords | FW-VPN-001 / Troubleshooting | Safe troubleshooting |
| A07 | What are the shared collaboration hours? | Yes | 14:00–16:00 IST, Monday–Thursday; not the entire workday | FW-REMOTE-001 / Shared collaboration hours | Time, days, qualification |
| A08 | How often are procedure notes reviewed, and by whom? | Yes | Every 90 days by the document owner | FW-DOCS-001 / Review cycle | Clear source attribution |
| U01 | How many weeks of paid parental leave does Fernwood provide? | No | Abstain; no entitlement or duration supplied | None; handbook explicitly excludes the topic | Avoid invented HR policy |
| U02 | What percentage does Fernwood contribute to retirement accounts? | No | Abstain; no contribution percentage supplied | None | Unsupported numeric answer |
| U03 | What is the VPN server's IP address? | No | Abstain; no address supplied | None; VPN guide explicitly omits it | Nearest document is not the answer |
| U04 | Can I work from France for six months? | No | Explain permitted countries/duration are unspecified; manager discussion alone is not authorization | None; remote FAQ does not supply the rule | Related evidence is insufficient |
| U05 | How many years must every company document be retained? | No | Abstain; no retention duration supplied | None; documentation guide excludes this policy | Do not confuse review with retention |

### Scoring rules

- **Retrieval hit:** For each A-case, did the retrieved chunks contain the required source section? Record hits divided by eight. A matching filename without the required passage is not a hit.
- **Supported-answer pass:** All required facts are correct and supported; no material unsupported additions. Record passes divided by eight.
- **Citation pass:** Displayed source identifiers exist and the cited passages support the claims. Retrieved source lists alone do not establish a pass.
- **Abstention pass:** For each U-case, the answer identifies insufficient evidence without inventing the missing rule or number. Record passes divided by five.
- **Operational observations:** Record latency and available usage separately. Do not invent local token counts or combine milliseconds with seconds.

These small denominators make this a teaching diagnostic, not a general quality benchmark. Preserve failed cases and record configuration changes rather than editing expected answers to fit a model.

## 3. Abstention and evidence contract

Use the sentence **“I don't have reliable information on that in the provided documents.”** as the target plain-text abstention response for document-grounded tasks. A prompt requests this behavior; it cannot guarantee compliance or factual correctness. Score meaning and unsupported claims separately from exact formatting.

When structured output has been taught, use status values `answered` and `insufficient_evidence`, with `answer` and `source_ids` fields. An insufficient-evidence result has the abstention sentence and an empty supporting-source list. Retrieved candidates may be shown separately as diagnostics and must not be labeled supporting citations.

Schema validation checks shape and allowed values. It does not verify that `answered` is justified or that listed sources support the answer. Chapters must implement evidence checks at an appropriate learning level and explain their limits.

## 4. Lab notebook

Copy this table into a notebook or a learner-owned Markdown file. Never record API keys or private documents.

| Run / case | Input | Prediction | Observed output | Evidence | Failure | Fix / changed variable | Remaining limitation |
|---|---|---|---|---|---|---|---|
| Example A02 | Annual allowance? | Correct combined annual limit | Amount correct, period omitted | Equipment allowance passage | Incomplete answer | Ask prompt to preserve amount, currency, period; rerun | One passing example is not general reliability |
| Your run | | | | | | | |

For comparisons, also record date, provider/model, prompt revision, embedding model, chunk settings, retrieval k, index version, latency units, and relevant package versions. Keep the question set fixed and change one variable at a time.

## 5. Vocabulary used consistently

| Term | Workbook meaning | Common confusion to avoid |
|---|---|---|
| Chat model | Generates a response from supplied messages | It does not automatically remember earlier calls |
| Embedding model | Maps text to vectors for comparison | It does not generate the assistant's answer |
| Prompt template | Instructions/message structure with named variables | A template is not an enforcement or truth system |
| Chain | Explicit composition of processing stages | Composition alone is not autonomous planning |
| Agent | Model-directed tool selection within application controls | A tool request is not authorization |
| History | Prior messages supplied or stored by the application | Stored history is not model training |
| Chunk | Retrievable portion of a document | Character count is not necessarily token count |
| Retriever | Selects candidate documents/passages | A selected candidate may be irrelevant |
| RAG | Retrieval followed by evidence-informed generation | Retrieval does not guarantee grounded output |
| Citation | Attribution that identifies supporting evidence | A list of retrieved filenames is not claim verification |
| Groundedness | Whether claims are supported by supplied evidence | Evidence can itself be wrong outside the exercise |
| Abstention | Declining a substantive answer when evidence is insufficient | It is not proof the topic has no real-world answer |

Return to the [chapter index](README.md). Use the [W-LC-18 — full glossary](18-glossary.md) for definitions and chapter links.
