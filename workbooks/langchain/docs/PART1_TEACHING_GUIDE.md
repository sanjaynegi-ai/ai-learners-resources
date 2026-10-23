# Part 1 Teaching Guide — Introduction to LangChain (langchain-demo)

**For:** you, the mentor, teaching this live.
**Companion docs:** [`PLAN.md`](./PLAN.md) (overall course design, mentor persona spec, §2 and §4) and [`course_inspiration.md`](./course_inspiration.md) (why each piece was chosen).
**What this is:** a run-of-show for every Part 1 session — what to say, what to build, what to ask, and what "done" looks like — so you can teach the whole of Part 1 from this file alone.

---

## How to use this guide

Each module below has the same seven sections:

1. **Why this module** — the problem-framing question you open with (per `PLAN.md` §2's "ask before telling" rule).
2. **Learning objectives** — what the learner should be able to do by the end.
3. **Step-by-step build** — numbered steps you walk through together, live.
4. **Full code** — the complete file, for your reference and for giving out if a learner falls behind.
5. **Ask the learner** — Socratic prompts to drop in *while* building, not just at the end. Each has a short hint ladder: escalate one level at a time, never jump straight to the answer.
6. **Common mistakes** — what actually goes wrong for beginners here, and the one-line fix.
7. **Quiz + checkpoint** — the closing questions. Answers are in `<details>` blocks — don't open them until the learner has tried.

Keep the voice from `PLAN.md` §2: calm, specific, no hype. Celebrate the thing that changed, not the learner's effort in the abstract.

---

## Before Day 1 — mentor prep checklist

- [ ] Python 3.13 available on the teaching machine (`python --version`).
- [ ] UV installed (`uv --version`; if missing, `curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux, or `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` on Windows).
- [ ] An OpenAI API key, created from the OpenAI developer platform's API keys page. Put a placeholder in your head for how much this will cost — `gpt-4o-mini` and `text-embedding-3-small` are both inexpensive; a full Part 1 session costs cents, not dollars.
- [ ] *(Optional, for the provider-swap aside in Module 1)* Ollama installed from ollama.com, with `ollama pull llama3.2` run once ahead of time — the first pull is a multi-GB download and you don't want to do it live.
- [ ] This guide open next to `PLAN.md` §2 (mentor persona) and §4 (the module table this guide expands).

---

## Module 0 — Environment Setup

### Why this module

> **Ask the learner:** "Before the assistant can say a single word, we need something that runs the same way on your machine as it does on mine. What's gone wrong for you in the past when someone said 'just pip install this'?"

Let them describe a version-mismatch horror story if they have one — it makes the next 15 minutes land.

### Learning objectives

- Learner can explain what `uv.lock` guarantees that a loose `requirements.txt` doesn't.
- Learner has a working UV project with LangChain installed and an API key loaded from `.env`.

### Step-by-step build

1. **Confirm tools.** Run `uv --version` and `python --version` together. If UV is missing, install it now (see prep checklist).
2. **Create the project.**
   ```bash
   uv init part1-langchain-demo
   cd part1-langchain-demo
   ```
   Open the generated `pyproject.toml` together. Point out: no version pins yet, no `uv.lock` yet — both appear after the first `uv add`.
3. **Add dependencies.**
   ```bash
   uv add langchain langchain-openai langchain-core langchain-community langchain-text-splitters langchain-chroma langchain-classic python-dotenv numpy
   ```
   Watch `uv.lock` appear. Open it briefly — don't explain every line, just point out it pins *exact* versions of everything, including transitive dependencies.
4. **Pin the Python version.**
   ```bash
   uv python pin 3.13
   ```
5. **Create `.env.example` and `.env`.**
   ```bash
   touch .env.example .env
   ```
   Put this in `.env.example` (safe to commit):
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
   Copy it to `.env` and have the learner paste their real key into `.env` only. Explain: `.env` never gets committed; `.env.example` is the documentation of what belongs in it.
6. **Add `.env` to `.gitignore`** if the project is git-tracked:
   ```bash
   echo ".env" >> .gitignore
   ```
7. **Create the `langchain_demo/` folder** for all of Part 1's code:
   ```bash
   mkdir langchain_demo
   ```
8. **Sanity check.** Create `langchain_demo/m00_sanity_check.py`:

### Full code

`langchain_demo/m00_sanity_check.py`:
```python
import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Copy .env.example to .env and paste in your key."
    )

print("Environment looks good. Key found, starts with:", api_key[:7] + "...")
```

Run it:
```bash
uv run python langchain_demo/m00_sanity_check.py
```

### Ask the learner

- *"What do you think happens if you run this before creating `.env`?"* — Let them try it and read the error message out loud. This is the error they'll now recognize for the rest of the course instead of a confusing `None` deep inside a LangChain stack trace.
- **Hint ladder** if `uv run` isn't found: (1) "did `uv init` finish without errors?" → (2) "are you inside the `part1-langchain-demo` directory?" → (3) show `cd part1-langchain-demo && uv run python langchain_demo/m00_sanity_check.py`.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `RuntimeError: OPENAI_API_KEY not found` | Key pasted into `.env.example` instead of `.env`, or `.env` not in the project root | Confirm `.env` sits next to `pyproject.toml`; confirm no quotes around the key |
| `ModuleNotFoundError: dotenv` | Ran with system `python` instead of `uv run python` | Always prefix with `uv run` — it's what activates the locked environment without a manual venv |

### Quiz + checkpoint

1. What's the difference between `.env` and `.env.example`?
   <details><summary>Answer</summary>`.env.example` documents which variables are needed, with placeholder values, and is safe to commit. `.env` holds the real secret values and must never be committed.</details>
2. Why does `uv add` modify both `pyproject.toml` and `uv.lock`?
   <details><summary>Answer</summary><code>pyproject.toml</code> records the loose dependency you asked for (e.g. "langchain"); <code>uv.lock</code> pins the exact resolved version of that package and every one of its transitive dependencies, so the next `uv sync` reproduces the identical environment.</details>
3. If a teammate clones this project, what one command gets them an identical environment?
   <details><summary>Answer</summary><code>uv sync</code></details>

**Checkpoint:** learner can run `langchain_demo/m00_sanity_check.py` successfully from a clean terminal, and can state in their own words what `uv.lock` buys them.

---

## Module 1 — The Assistant's First Voice

### Why this module

> **Ask the learner:** "The assistant doesn't exist yet. What's the smallest number of lines of code that makes something talk back to you using a real LLM?"

Let them guess a number before showing it's about 6.

### Learning objectives

- Learner can send a message to an LLM via LangChain and read the response.
- Learner understands that swapping model providers is a one-line change, because LangChain standardizes the interface.

### Step-by-step build

1. Create `langchain_demo/m01_first_voice.py`.
2. Load the API key the same way as Module 0 — point out this pattern will repeat in every file from here on.
3. Construct a `ChatOpenAI` instance.
4. Take a question from the user, call `.invoke()`, print `.content`.
5. Run it, ask the assistant something.
6. *(Optional aside, only if Ollama is installed)* — duplicate the file as `m01b_first_voice_local.py`, swap the model line, run it with no API key at all. This is the entire lesson: same `.invoke()`, same `.content`, different constructor.

### Full code

`langchain_demo/m01_first_voice.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not set. See .env.example.")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)


def main():
    question = input("Ask the assistant something: ")
    response = llm.invoke(question)
    print(response.content)


if __name__ == "__main__":
    main()
```

*(Optional)* `langchain_demo/m01b_first_voice_local.py` — requires Ollama running locally and `uv add ollama`:
```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3.2")


def main():
    question = input("Ask the assistant something (running locally, no API key): ")
    response = llm.invoke(question)
    print(response.content)


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m01_first_voice.py
```

### Ask the learner

- *"What type is `response`? What type is `response.content`?"* Have them print `type(response)` to find out it's an `AIMessage`, not a plain string. **Hint ladder:** (1) "try printing `type(response)` instead of `response.content`" → (2) "it's an object with more than just text on it — what else might it carry?" (model name, token usage) → (3) show `print(response.response_metadata)`.
- *"If you wanted to switch the assistant to run on Mistral instead of GPT-4o-mini, how many lines would change?"* — drive toward "just the constructor line," which is the entire point of the module.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `AuthenticationError` | Key invalid or billing not set up on the OpenAI account | Confirm the key works with a direct `curl` to the OpenAI API, independent of LangChain, to isolate the problem |
| Script hangs with no output | Waiting on `input()` — easy to miss in a terminal that's scrolled | Just type the question and press enter; point this out before it causes confusion |

### Quiz + checkpoint

1. What method actually sends the request to the model — `ChatOpenAI(...)` or `.invoke(...)`?
   <details><summary>Answer</summary><code>.invoke(...)</code>. Constructing <code>ChatOpenAI(...)</code> just configures a client; no network call happens until <code>.invoke()</code>.</details>
2. Why is `response.content` a separate step from `llm.invoke(question)`?
   <details><summary>Answer</summary><code>.invoke()</code> returns a full message object (model, token usage, etc.), not just text — <code>.content</code> pulls out the text portion specifically.</details>

**Checkpoint:** learner can explain, unprompted, why the provider swap only touched one line.

---

## Module 2 — Giving The Assistant Opinions It Can Be Steered On

### Why this module

> **Ask the learner:** "Ask the assistant to explain the history of a country that doesn't exist — make one up. What does it do?"

Let them watch it confidently invent an answer. That failure is the entire motivation for this module.

### Learning objectives

- Learner can build a reusable `PromptTemplate` with variables.
- Learner can write guardrail wording that produces a predictable refusal instead of a hallucination.

### Step-by-step build

1. Create `langchain_demo/m02_prompt_templates.py`.
2. Define a `PromptTemplate` with `topic` and `audience` variables.
3. Add an explicit instruction for what to do when the topic isn't real — and make the required response an *exact string*, not "say you don't know" in the abstract.
4. Format the template and `.invoke()` it.
5. Test with a real topic, then the made-up one from the opening question — confirm the exact-string refusal appears now.

### Full code

`langchain_demo/m02_prompt_templates.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

prompt_template = PromptTemplate(
    input_variables=["topic", "audience"],
    template="""You are a careful research assistant.
Explain the following topic: {topic}
Tailor the explanation for this audience: {audience}

If the topic is not a real, verifiable subject, respond with exactly this sentence
and nothing else: "I don't have reliable information on that."

Otherwise, keep the explanation to 3 short paragraphs.
""",
)


def main():
    topic = input("Topic: ")
    audience = input("Audience (e.g. '10-year-old', 'expert'): ")
    prompt = prompt_template.format(topic=topic, audience=audience)
    response = llm.invoke(prompt)
    print(response.content)


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m02_prompt_templates.py
```

### Ask the learner

- *"Why does the guardrail say 'respond with exactly this sentence' instead of 'say you don't know'?"* **Hint ladder:** (1) "try changing it to the vaguer wording and test the made-up topic again — does it still refuse cleanly?" → (2) "what's easier to detect downstream in your code: an exact string, or 'some kind of refusal'?" → (3) explain that exact-string guardrails are testable with a simple equality check, which matters a lot once you're grading answers automatically (foreshadow Part 2's golden-set scoring).
- *"What happens if `audience` is left blank?"* Try it. Decide together whether that's acceptable or needs a default.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError` on `.format()` | Forgot to pass one of `input_variables` | Match every name in `template="..."` `{}` placeholders to a key passed into `.format()` |
| Guardrail doesn't trigger reliably | Wording is vague ("acknowledge you're not sure") | Make the required output literal and exact, as above |

### Quiz + checkpoint

1. What's the difference between a prompt that *describes* good behavior and one that *forces* it?
   <details><summary>Answer</summary>A description ("try to be accurate") is advice the model can still deviate from under pressure to be helpful; forcing behavior with an exact required string gives the model (and your code) an unambiguous, checkable instruction.</details>
2. `PromptTemplate.format()` returns what type?
   <details><summary>Answer</summary>A plain Python string.</details>

**Checkpoint:** the made-up-country test now reliably produces the exact refusal string, not a confident fabrication.

---

## Module 3 — A Pipeline, Not a Pile of Calls

### Why this module

> **Ask the learner:** "Right now, every new thing the assistant does is its own script. What if the assistant needed to do three things *in a row*, where step 2 needs the output of step 1?"

### Learning objectives

- Learner can compose a chain with the `|` (pipe) operator.
- Learner can explain what actually flows between pipe stages.
- Learner can use `StrOutputParser` to turn a message object into a plain string mid-chain.

### Step-by-step build

1. Create `langchain_demo/m03_chains.py`.
2. Build a two-step "research brief" pipeline: step 1 asks the model for 3 key questions about a topic; step 2 answers them.
3. First, show it *not* working as one chain — run step 1 alone, read the output, manually paste it into step 2's prompt. Painful on purpose.
4. Now chain it for real with `|`, including a `StrOutputParser` and a `lambda` to reshape the dict between steps.
5. Run it end to end with one `.invoke()`.

### Full code

`langchain_demo/m03_chains.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

questions_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""You are a research assistant.
List exactly 3 key questions a newcomer should ask to understand: {topic}
Respond with a numbered list only, no other text.
""",
)

answers_prompt = PromptTemplate(
    input_variables=["questions"],
    template="""You are a research assistant.
Answer each of these questions in 2-3 sentences:
{questions}
""",
)

research_chain = (
    questions_prompt
    | llm
    | StrOutputParser()
    | (lambda questions_text: {"questions": questions_text})
    | answers_prompt
    | llm
)


def main():
    topic = input("Topic: ")
    response = research_chain.invoke({"topic": topic})
    print(response.content)


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m03_chains.py
```

### Ask the learner

- *"`questions_prompt | llm` — what type comes out the other end?"* **Hint ladder:** (1) "is it the same type that came out of Module 1's `.invoke()`?" → (2) "try `print(type(...))` on just that first stage" → (3) state it directly: an `AIMessage`, same as always — the pipe doesn't change what each stage returns, it just feeds it forward.
- *"Why do we need the `lambda` between `StrOutputParser()` and `answers_prompt`?"* **Hint ladder:** (1) "what does `answers_prompt.format()` expect as input — a string, or a dict?" → (2) "what does `StrOutputParser()` hand you — a string, or a dict?" → (3) explain: `PromptTemplate` always expects a dict of variable names to values, so the lambda repackages the bare string into `{"questions": ...}`.
- *"What would happen if you removed `StrOutputParser()` and fed the raw `AIMessage` straight into the lambda?"* Let them try it and see the `.format()` call fail or behave oddly — ties the lesson back concretely.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `TypeError` inside `answers_prompt.format()` | A raw `AIMessage` (not a string) was passed where a dict value was expected | Insert `StrOutputParser()` right after the `llm` call whose text output needs to flow into the next prompt |
| Chain "loses" the original topic by step 2 | The lambda replaced the whole dict instead of merging into it | For this module it's fine (step 2 doesn't need `topic`), but flag that a chain needing *both* old and new variables must merge the dict, not replace it — this is exactly what Module 4 and Part 2 will need |

### Quiz + checkpoint

1. In `a | b | c`, what is actually happening under the hood?
   <details><summary>Answer</summary>Each stage is a <code>Runnable</code>. The pipe operator wires them so the output of one becomes the input of the next, and LangChain can run the whole composed object with a single <code>.invoke()</code>, <code>.batch()</code>, or <code>.stream()</code> call.</details>
2. Why did we deliberately do the two-step process by hand first, before chaining it?
   <details><summary>Answer</summary>So the chain's behavior is never a black box — the learner has already seen exactly what data moves from step 1 to step 2 and can recognize that the chain automates a process they understand, rather than introducing new magic.</details>

**Checkpoint:** learner can describe, without looking at the code, what object type flows between each `|` stage in `research_chain`.

---

## Module 4 — Giving The Assistant Memory

### Why this module

> **Ask the learner:** "Ask the assistant something, get an answer, then ask a follow-up that only makes sense if it remembers what you just said — like 'what about in French?' Watch what happens."

It will either answer a non-sequitur or ask "what would you like translated?" — either way, the lack of memory is now visibly a problem, not an abstract one.

### Learning objectives

- Learner can use `ChatPromptTemplate` with distinct system/human roles.
- Learner can wire `RunnableWithMessageHistory` so a chain remembers prior turns within one run.
- Learner can state precisely where that memory lives and when it disappears.

### Step-by-step build

1. Create `langchain_demo/m04_memory.py`.
2. Build a `ChatPromptTemplate` with a system message, a `MessagesPlaceholder` for history, and a human message slot.
3. Wrap the `prompt | llm` chain in `RunnableWithMessageHistory`, backed by an in-memory `ChatMessageHistory`.
4. Build a small loop so multiple turns can happen in one run, with a clean exit command (not an uninterruptible infinite loop).
5. Prove memory works: ask something, then a pronoun-dependent follow-up, in the same run.
6. Kill the script and restart it. Ask the follow-up again *first*. Watch it fail — this is deliberate and sets up the "where does memory actually live" question.

### Full code

`langchain_demo/m04_memory.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful research assistant. Keep answers concise."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
history = ChatMessageHistory()

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


def main():
    print("Assistant is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        response = chain_with_history.invoke(
            {"input": user_input},
            {"configurable": {"session_id": "demo-session"}},
        )
        print("Assistant:", response.content)


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m04_memory.py
```

### Ask the learner

- *"Where does `history` actually live right now — disk, a database, RAM?"* **Hint ladder:** (1) "is there any file being written to anywhere in this script?" → (2) "what happens to a Python variable when the process exits?" → (3) state it: it's a plain in-memory Python object, gone the instant the script ends — that's exactly why restarting lost it.
- *"What is `lambda session_id: history` actually for? Why not just pass `history` directly?"* **Hint ladder:** (1) "what if you wanted two different users to have two different histories?" → (2) "`RunnableWithMessageHistory` calls this function with a session_id every time — what could it do differently per session_id that it can't do with a fixed object?" → (3) explain: the lambda is a factory, so a real implementation can look up or create per-session history (this foreshadows Part 2's session-scoped history in Module 11).

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `while True:` loop won't exit | No exit condition checked | Confirm the `"exit"/"quit"` check is before the `.invoke()` call, not after |
| History seems to "leak" between unrelated test runs inside the same session | Same hardcoded `session_id="demo-session"` reused across very different conversations on purpose during testing | Point out this is expected given the fixed id — ask what would change if two different `session_id` values were used |

### Quiz + checkpoint

1. What does `MessagesPlaceholder(variable_name="chat_history")` actually do in the prompt?
   <details><summary>Answer</summary>It reserves a spot in the message list where the full prior conversation history gets inserted at invocation time, so the model sees it as real prior turns rather than as one flattened string.</details>
2. If you restarted the script mid-conversation, what exactly is lost, and why?
   <details><summary>Answer</summary>The entire <code>ChatMessageHistory</code> object, because it only exists in the running process's memory — nothing persisted it to disk or a database.</details>

**Checkpoint:** learner can explain, unprompted, why restarting the script lost the conversation, and can name what would need to change for it to survive a restart (persistent storage — not built yet, just named).

---

## Module 5 — A Sense of Similarity

### Why this module

> **Ask the learner:** "The assistant's memory right now is exact text — it has to literally see the words again. What if we wanted the assistant to find things that *mean* the same thing, even with completely different wording?"

### Learning objectives

- Learner can generate an embedding vector for a piece of text.
- Learner can compute cosine similarity between two vectors by hand.
- Learner can predict, roughly, which of two text pairs will score higher before running the code.

### Step-by-step build

1. Create `langchain_demo/m05_embeddings.py`.
2. Call `OpenAIEmbeddings().embed_query()` on a single string, print its length — establish "it's just a long list of numbers."
3. Write a plain `cosine_similarity` function using `numpy` — no LangChain abstraction here, so the math is visible.
4. Before running, have the learner predict the similarity score for: (a) two near-duplicate sentences, (b) two unrelated sentences, (c) two sentences about the same topic in different words.
5. Run all three pairs, compare predictions to actual scores.

### Full code

`langchain_demo/m05_embeddings.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import numpy as np

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    text1 = input("Text 1: ")
    text2 = input("Text 2: ")
    vector1 = embeddings.embed_query(text1)
    vector2 = embeddings.embed_query(text2)
    print(f"Each vector has {len(vector1)} numbers.")
    print(f"Cosine similarity: {cosine_similarity(vector1, vector2):.4f}")


if __name__ == "__main__":
    main()
```

Run three times:
```bash
uv run python langchain_demo/m05_embeddings.py
```
Suggested pairs:
- "The dog ran across the park." / "A dog sprinted through the park." (expect high, ~0.9+)
- "The dog ran across the park." / "Quarterly revenue grew 12 percent." (expect low, ~0.0–0.2)
- "How do I reset my password?" / "I forgot my login credentials, help." (expect moderately high — same intent, no shared words)

### Ask the learner

- *"Before we run it — which pair do you think scores highest? Which scores lowest? Why?"* Always get a prediction before running; the miss (especially on the "different words, same intent" pair) is the whole lesson.
- *"Is a cosine similarity of 0.4 'kind of similar' or 'basically unrelated'? How would you know without more examples?"* **Hint ladder:** (1) "what did the unrelated pair score?" → (2) "what did the near-duplicate pair score?" → (3) explain there's no universal cutoff — it's always relative to a corpus and needs calibration, which is exactly why Part 2 will tune a `k` and a similarity threshold empirically rather than guessing.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Similarity scores look suspiciously close to 1.0 for everything | Comparing a text to itself, or near-identical strings, by accident | Double check the two inputs actually differ |
| `embed_query` is slow the first call | Normal — first network round trip per process | Not a bug; mention it so it doesn't look broken |

### Quiz + checkpoint

1. What does the *length* of the embedding vector tell you, and what does it *not* tell you?
   <details><summary>Answer</summary>The length (e.g. 1536 numbers for <code>text-embedding-3-small</code>) is fixed by the model and tells you the dimensionality of the space — it says nothing about the content of any particular text.</details>
2. Why did the "forgot my login credentials" pair score high despite sharing almost no words with the password-reset sentence?
   <details><summary>Answer</summary>Embeddings capture semantic meaning, not lexical overlap — the model represents both sentences as being "about the same thing" (account access trouble) even though the vocabulary barely overlaps.</details>

**Checkpoint:** learner correctly predicts the *ranking* (if not the exact number) of all three pairs before the third run.

---

## Module 6 — The Assistant's First Retriever

### Why this module

> **Ask the learner:** "Hand-computing similarity against one other sentence was fine. What if the assistant had a hundred notes and needed to find the 3 most relevant ones to a question? Are you going to write a hundred `cosine_similarity` calls?"

### Learning objectives

- Learner can load a text file as LangChain `Document` objects.
- Learner can split documents into chunks and explain why.
- Learner can build an in-memory vector store and retrieve the top-k matches for a query.

### Step-by-step build

1. Create `langchain_demo/demo_notes.txt` — the assistant's own "notes," a handful of short unrelated-topic paragraphs (given below).
2. Create `langchain_demo/m06_first_retriever.py`.
3. Load the file with `TextLoader`, split with `RecursiveCharacterTextSplitter`, inspect how many chunks came out and roughly what's in each.
4. Build a `Chroma` vector store from the chunks and get a retriever with `k=2`.
5. Ask a question whose answer is clearly in one specific paragraph; confirm the retriever finds it.
6. Ask a question with no answer in the file at all; look at what comes back anyway — retrievers always return *something*, which sets up Module 7's grounding problem.

### Full code

`langchain_demo/demo_notes.txt`:
```text
The Mariana Trench is the deepest known part of the world's oceans, reaching
a depth of about 10,935 meters at its deepest point, called the Challenger Deep.

The Apollo 11 mission landed the first humans on the Moon on July 20, 1969.
Neil Armstrong and Buzz Aldrin walked on the lunar surface while Michael
Collins orbited above in the command module.

Octopuses have three hearts and blue blood. Two hearts pump blood to the
gills, while the third pumps it to the rest of the body. Their blood is
blue because it uses a copper-based protein called hemocyanin instead of
the iron-based hemoglobin found in human blood.

The Great Library of Alexandria, founded in Egypt around the 3rd century BCE,
was one of the largest and most significant libraries of the ancient world,
though its exact collection size and the circumstances of its decline remain
debated among historians.

Honey never spoils if stored properly. Archaeologists have found pots of
honey in ancient Egyptian tombs that were still edible after thousands of
years, thanks to honey's low moisture content and acidic pH.
```

`langchain_demo/m06_first_retriever.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

document = TextLoader("langchain_demo/demo_notes.txt").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(document)
print(f"Loaded 1 document, split into {len(chunks)} chunks.")

db = Chroma.from_documents(chunks, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 2})


def main():
    query = input("Ask about something in demo_notes.txt: ")
    results = retriever.invoke(query)
    for i, doc in enumerate(results, start=1):
        print(f"--- Match {i} ---")
        print(doc.page_content)
        print()


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m06_first_retriever.py
```
Try: "how deep is the ocean" (should hit the Mariana Trench paragraph), then "who was the first president of the United States" (not in the file — watch what comes back anyway).

### Ask the learner

- *"Why did we split the document into chunks instead of embedding the whole file as one vector?"* **Hint ladder:** (1) "if the whole file became one vector, and the file covered 5 unrelated topics, what would that single vector 'mean'?" → (2) "would a query about octopuses be well-matched against a vector that's an average of octopuses, the Moon landing, and a library?" → (3) explain: one vector per chunk lets each topic be found independently; a single whole-document vector blurs everything into a mediocre match for all of it.
- *"You asked about the first U.S. president, which isn't in this file at all — what came back, and was it a good answer?"* Let them see the retriever confidently return the two *least bad* chunks anyway. **Hint ladder:** (1) "did the retriever return nothing, or something?" → (2) "is a vector retriever capable of saying 'nothing here is relevant,' or does it always rank what it has?" → (3) state plainly: a retriever always returns its top-k by *relative* similarity, even if the best match is still bad — nothing here stops a confident wrong answer, which is exactly Module 7's problem.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError` for `demo_notes.txt` | Path mismatch between where the script runs and where the file lives | Run from the `part1-langchain-demo` project root with the path `langchain_demo/demo_notes.txt`, or adjust the path to match your terminal's working directory |
| Only 1 chunk reported | `chunk_size` larger than the whole file | Expected for a short demo file with a large chunk size — confirm by printing each chunk's character count |

### Quiz + checkpoint

1. What does `chunk_overlap=30` actually buy you?
   <details><summary>Answer</summary>It repeats the last 30 characters of one chunk at the start of the next, so a sentence or fact that happens to fall right on a chunk boundary isn't split in a way that destroys its meaning in both halves.</details>
2. Does `retriever.invoke(query)` ever return zero results by default?
   <details><summary>Answer</summary>No — with a plain similarity retriever and a fixed <code>k</code>, it always returns exactly <code>k</code> chunks, ranked by similarity, regardless of whether any of them are actually relevant.</details>

**Checkpoint:** learner can explain why the retriever returned *something* for the off-topic question, and can predict (correctly) that this will cause a problem once an LLM is asked to answer from it.

---

## Module 7 — The Assistant's First Grounded Answer (Minimal RAG)

### Why this module

> **Ask the learner:** "The assistant can now find relevant chunks of text. It still isn't *using* them to answer anything — go back to Module 6's output and try to get the assistant to actually answer your question using only what it found. What's missing?"

### Learning objectives

- Learner can wire a retriever and an LLM together into a single RAG chain.
- Learner can write a grounding instruction that produces a real "I don't know" instead of a fabricated answer.
- Learner can observe the exact failure mode a retriever-only system has (Module 6) now get fixed.

### Step-by-step build

1. Create `langchain_demo/m07_minimal_rag.py`, reusing the same `demo_notes.txt`.
2. Build the same retriever as Module 6.
3. Write a `ChatPromptTemplate` whose system message says to answer **only** from the provided `{context}`, and to say "I don't know" if the answer isn't there.
4. Wire it with `create_stuff_documents_chain` (stuffs retrieved chunks into `{context}`) and `create_retrieval_chain` (connects the retriever to that chain).
5. Ask the same two test questions from Module 6 — the ocean-depth one and the off-topic U.S. president one. Compare the second answer directly against what Module 6 returned.

### Full code

`langchain_demo/m07_minimal_rag.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

document = TextLoader("langchain_demo/demo_notes.txt").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(document)
db = Chroma.from_documents(chunks, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a research assistant.
Answer using only the context below. If the answer isn't in the context,
say exactly: "I don't know."

Context:
{context}
""",
        ),
        ("human", "{input}"),
    ]
)

doc_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, doc_chain)


def main():
    question = input("Ask the assistant about demo_notes.txt: ")
    response = rag_chain.invoke({"input": question})
    print(response["answer"])


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m07_minimal_rag.py
```

### Ask the learner

- *"Compare this answer on the president question to what Module 6 gave you. What actually changed?"* **Hint ladder:** (1) "did the retriever's output change at all?" → (2) "so if the retrieved chunks are identical, what's different?" → (3) point out: the *retrieval* step still returns the same two irrelevant-but-closest chunks — what changed is the prompt instructing the LLM to recognize those chunks don't contain an answer and refuse accordingly. Grounding is a prompting discipline on top of retrieval, not a retrieval feature.
- *"What does `create_stuff_documents_chain` actually 'stuff'?"* **Hint ladder:** (1) "look at the prompt's `{context}` variable — what fills it in?" → (2) "if the retriever returns 3 chunks, how do 3 separate documents become one `{context}` string?" → (3) explain: it concatenates all retrieved chunks' text together and inserts that single block into `{context}` — "stuffing" is the literal, simplest possible way to give an LLM multiple documents at once (and it has a real limit: a huge number of chunks eventually won't fit the context window, which is a reason reranking down to a smaller top-n, coming in Part 2, matters).

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Still invents an answer for the off-topic question | Grounding instruction too soft, or absent from the system message | Confirm the system message literally includes the words "answer using only the context below" and the exact refusal string |
| `KeyError: 'answer'` | Reading the wrong key off the chain's response | `create_retrieval_chain`'s output dict has `"answer"` and `"context"` keys — not `"output"` or `"result"` |

### Quiz + checkpoint

1. What are the two keys in the dict returned by `rag_chain.invoke(...)`, and what's in each?
   <details><summary>Answer</summary><code>"answer"</code> holds the LLM's generated text; <code>"context"</code> holds the list of retrieved <code>Document</code> objects that were stuffed into the prompt.</details>
2. If the assistant's answer is wrong, but it did say something *other than* "I don't know" — where would you look first: the retriever, or the prompt?
   <details><summary>Answer</summary>The retriever first — print <code>response["context"]</code> and check whether the retrieved chunks actually contain the answer at all. If they do and the answer is still wrong, then it's a prompting/grounding problem; if they don't, no prompt can fix it — that's a retrieval problem.</details>

**Checkpoint:** the off-topic question now reliably returns "I don't know," and the learner can point to the exact sentence in the prompt responsible for that.

---

## Module 8 — The Assistant Remembers *and* Stays Grounded

### Why this module

> **Ask the learner:** "Ask the assistant something from `demo_notes.txt`, get a grounded answer, then immediately ask a follow-up using a pronoun — like 'how deep is that, exactly' right after asking about the ocean. What happens?"

Module 4 gave the assistant memory but no documents; Module 7 gave the assistant documents but no memory. This module needs both, and the two don't just bolt together — the retrieval step itself needs to understand the follow-up before it can even search.

### Learning objectives

- Learner can explain why a standalone "question rewriter" step exists before retrieval.
- Learner can explain why the rewriter prompt has no `{context}` while the answering prompt does.
- Learner has a single chain that is both grounded and multi-turn.

### Step-by-step build

1. Create `langchain_demo/m08_history_aware_rag.py`.
2. Build the same retriever as Modules 6–7.
3. Write a **first** prompt whose only job is to rewrite the latest question into a standalone one, using chat history — and explicitly tell it not to answer.
4. Wrap that with `create_history_aware_retriever`.
5. Write a **second** prompt — the same grounded-answering one from Module 7, but now also carrying `MessagesPlaceholder("chat_history")`.
6. Wire both together with `create_retrieval_chain`, then wrap the whole thing in `RunnableWithMessageHistory` (same pattern as Module 4), noting the `output_messages_key="answer"` is required because the chain's output is now a dict, not a bare message.
7. Run the pronoun test from the opening question — confirm it now resolves correctly.

### Full code

`langchain_demo/m08_history_aware_rag.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

document = TextLoader("langchain_demo/demo_notes.txt").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(document)
db = Chroma.from_documents(chunks, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

# Step 1: rewrite the question using history. NO {context} here on purpose —
# this prompt's only job is to produce a standalone question, not an answer.
contextualize_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Rewrite the user's latest question as a standalone question, "
            "using the chat history for any missing context. Do not answer it.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)

# Step 2: answer using retrieved context. {context} appears here, not above.
qa_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a research assistant. Answer using only the context below. If the
answer isn't in the context, say exactly: "I don't know."

Context:
{context}
""",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
qa_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

history = ChatMessageHistory()
chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


def main():
    print("Assistant (with memory + grounding) is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        response = chain_with_history.invoke(
            {"input": user_input},
            {"configurable": {"session_id": "demo-session"}},
        )
        print("Assistant:", response["answer"])


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m08_history_aware_rag.py
```
Test sequence: "Tell me about the ocean trench in demo_notes" → then "how deep is it, exactly?"

### Ask the learner

- *"Why does the rewriter prompt have no `{context}` variable, while the answering prompt does?"* This is the module's central question — spend real time here. **Hint ladder:** (1) "what does the rewriter need to produce — more text for the user, or a better search query?" → (2) "can you retrieve documents *before* you know what question you're even searching for?" → (3) state plainly: retrieval has to happen *after* the question is understood, so the rewriter runs first and has nothing to do with document content yet; only the second prompt, which runs after retrieval, has anything in `{context}` to work with.
- *"If you skip straight to Module 7's chain but just add chat history to it, with no rewriter step at all, what breaks?"* Have them try it as an experiment — pass the raw pronoun question straight to the retriever with no rewriting. Watch retrieval fail to find the ocean trench chunk because "how deep is it" alone, with no history resolved into the query, barely matches anything. **Hint ladder:** (1) "what text literally gets embedded and searched against?" → (2) "does 'how deep is it' by itself mention oceans, trenches, or anything searchable?" → (3) conclude: memory for the *answering* step isn't enough; the *retrieval* step independently needs the pronoun resolved too, which is exactly what `create_history_aware_retriever` is for.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'answer'` or history seems to store the wrong thing | Forgot `output_messages_key="answer"` on `RunnableWithMessageHistory` | The chain's output is now a dict with `"answer"`/`"context"` keys, not a bare message — this parameter tells the history wrapper which key to actually remember as "what the assistant said" |
| Follow-up question still resolves to the wrong topic | Rewriter prompt accidentally told to answer, or history not actually populated for this session_id | Confirm the rewriter's system message explicitly says "do not answer it"; confirm the same `session_id` is used turn to turn |

### Quiz + checkpoint

1. Why are there two separate prompts in this module instead of one combined prompt?
   <details><summary>Answer</summary>They run at two different points in the pipeline, with two different jobs: the rewriter runs before retrieval and only needs to produce a standalone question; the answerer runs after retrieval and needs the retrieved context to produce a grounded answer. Combining them would require retrieval to happen before the question is even understood, which is backwards.</details>
2. What does `output_messages_key="answer"` actually control?
   <details><summary>Answer</summary>It tells <code>RunnableWithMessageHistory</code> which key of the chain's dict output represents "the assistant's reply" to be recorded into chat history — without it, the wrapper wouldn't know whether to store the whole dict, the context, or the answer as what the assistant "said."</details>

**Checkpoint:** the pronoun-dependent follow-up now retrieves correctly, and the learner can explain why that required a *second* rewriting step, not just adding history to Module 7's existing chain.

---

## Module 9 (Optional) — The Assistant Learns to Use Tools

### Why this module

> **Ask the learner:** "The assistant can only ever answer from documents you hand it. What happens if you ask something the answer to which isn't in any document you have — but *is* out there on the internet or in an encyclopedia?"

This module is a stretch goal — teach it if time and interest allow; skipping it does not block Part 2.

### Learning objectives

- Learner can give an LLM-based agent access to an external tool.
- Learner can distinguish "the model retrieved a document chunk" from "the model called a tool and got a result back."

### Step-by-step build

1. Create `langchain_demo/m09_tools.py`.
2. Load a single tool (Wikipedia) with `load_tools`.
3. Build an agent with `create_agent`, giving it a system prompt describing when to use the tool.
4. Ask it something it couldn't know confidently on its own and that Wikipedia covers well; inspect the final message.

### Full code

`langchain_demo/m09_tools.py`:
```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
tools = load_tools(["wikipedia"])

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a research assistant. Use the wikipedia tool when you need facts you "
        "don't already know confidently. Give one clear final answer."
    ),
)


def main():
    task = input("Ask the assistant anything (it can use Wikipedia now): ")
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python langchain_demo/m09_tools.py
```

### Ask the learner

- *"How is this different from Module 7's retriever? Both of them 'go get information' before answering."* **Hint ladder:** (1) "who decided what to search for and when — your code, or the model?" → (2) "in Module 7, retrieval happens on every single question, no matter what. Here?" → (3) explain: a retriever is unconditional and deterministic — it always runs; a tool call is a *decision* the model makes at inference time about whether it needs help, and what to ask the tool for.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Agent never calls the tool | System prompt doesn't make clear when to use it, or the question is something the model is already confident about | Ask something more obscure, or sharpen the system prompt |
| Slow / multiple tool calls | Normal for ReAct-style agents — they may search, read, and re-search | Not a bug; mention this is why agents are more expensive and slower than a fixed retriever |

### Quiz + checkpoint

1. What decides whether the Wikipedia tool gets called at all — your code, or the model?
   <details><summary>Answer</summary>The model, at inference time, based on the system prompt and the question — this is the fundamental difference from a retriever, which runs unconditionally every time.</details>

**Checkpoint:** learner can articulate, in one sentence, the difference between retrieval and tool use.

---

## Bridge to Part 2 — name the gaps out loud

Before starting Part 2, say this explicitly, and have the learner confirm each point against Module 7/8's code:

1. **No persistence.** Every run rebuilds the Chroma index from scratch — kill the script and the vector store is gone.
2. **No reranking.** `k=3` is a guess; nothing measures whether those 3 chunks were actually the best 3.
3. **No evaluation.** "It seems to work" has been the only quality signal so far — there's no number anywhere.
4. **No API, no UI beyond a terminal prompt.** Nothing here is a service another program could call.

> **Ask the learner:** "If you had to turn Module 8's script into something a whole company could actually rely on, which of these four gaps would break first?"

Whatever they answer, tell them: that's Part 2's first module.
