# Part 2 Teaching Guide — The Fernwood Labs Knowledge Assistant

**For:** you, the mentor, teaching this live.
**Companion docs:** [`PLAN.md`](./PLAN.md) (overall course design, mentor persona spec, §2 and §5) and [`course_inspiration.md`](./course_inspiration.md) (why each piece was chosen — every planted bug here traces back to a real bug found there).
**Companion data:** [`sample-corpus/fernwood-labs/`](../sample-corpus/fernwood-labs/) (11 documents) and [`sample-corpus/golden_qna.jsonl`](../sample-corpus/golden_qna.jsonl) (24 questions).
**Prior project:** [`PART1_TEACHING_GUIDE.md`](./PART1_TEACHING_GUIDE.md) — Part 2 assumes everything in it.

---

## How to use this guide

Same seven-section shape as Part 1, per module: **Why this module**, **Learning objectives**, **Step-by-step build**, **Full code**, **Ask the learner**, **Common mistakes**, **Quiz + checkpoint**. Keep the mentor voice from `PLAN.md` §2.

The one addition in Part 2: most modules end with a **Scoreboard entry** — the learner re-runs the golden set through `scripts/eval.py` and records the four RAGAS numbers in their own `SCOREBOARD.md`. Not every module moves accuracy (indexing and caching move latency, not accuracy) — when a module doesn't move the scoreboard, say so explicitly rather than skipping the measurement, so "no change" is a recorded, understood result and not a gap.

---

## Before Day 1 — mentor prep checklist

- [ ] Everything from Part 1's prep checklist (Python 3.11, UV, OpenAI key).
- [ ] Docker Desktop (or an equivalent Docker Engine) installed and running — this project runs Postgres and Redis as containers.
- [ ] A Cohere API key (free tier is enough) for the reranking module — from the Cohere dashboard's API keys page.
- [ ] `sample-corpus/fernwood-labs/` and `sample-corpus/golden_qna.jsonl` exist in the repo root (built alongside `PLAN.md`).
- [ ] This guide open next to `PLAN.md` §5 (the module table this guide expands) and §1.3 (the four planted bugs and their real-world precedent).

---

## Bridge from Part 1 — close the four named gaps

Part 1 ended by naming four gaps in Module 7/8's RAG: no persistence, no reranking, no evaluation, no API. Tell the learner explicitly which Part 2 module closes each one, before module 1 starts:

| Part 1 gap | Closed in |
|---|---|
| No persistence (Chroma rebuilt every run) | Module 2 — pgvector, a real database |
| No API (just a terminal prompt) | Module 3 — FastAPI |
| No evaluation ("it seems to work") | Module 5 — the golden-set scoreboard |
| No reranking (`k=3` was a guess) | Module 9 |

> **Ask the learner:** "Which of those four would break first if Fernwood Labs actually tried to use Part 1's script company-wide?" Whatever they answer, that's where their intuition already points — module order in this guide follows urgency, not just difficulty.

---

## Module 1 — Scaffold

### Why this module

> **Ask the learner:** "Everything in Part 1 lived and died with one Python process. A company knowledge assistant needs to survive a restart and be reachable by more than one person at once. What two pieces of infrastructure does that require, at minimum?"

Drive toward: a database (so data outlives the process) and a web server (so more than one person can ask at once).

### Learning objectives

- Learner has Postgres (with `pgvector`) and Redis running locally via Docker Compose, with correct health-check-gated startup order.
- Learner understands why `init-db/` scripts only run once, against an empty volume.

### Step-by-step build

1. From the repo root:
   ```bash
   uv init part2-fernwood-assistant
   cd part2-fernwood-assistant
   uv add fastapi uvicorn python-dotenv pydantic
   uv python pin 3.11
   ```
2. Edit `pyproject.toml`'s `requires-python` to `>=3.11` if `uv init` set `>=3.12` (same gotcha as Part 1).
3. Create `init-db/init.sql` — just the extension for now:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   ```
4. Create `docker-compose.yml`.
5. Create `.env.example`, copy to `.env`.
6. Bring the infrastructure up and confirm both containers report healthy before moving on.

### Full code

`init-db/init.sql`:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

`docker-compose.yml`:
```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: fernwood-db
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]
      interval: 5s
      timeout: 3s
      retries: 30
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d

  redis:
    image: redis/redis-stack:latest
    container_name: fernwood-redis
    ports:
      - "6379:6379"
      - "8001:8001"
    environment:
      REDIS_ARGS: "--appendonly yes"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
  redis-data:
```

`.env.example`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
OPENAI_API_KEY=sk-your-key-here
DATA_DIR=data
RETRIEVAL_K=5
REDIS_URL=redis://localhost:6379
CO_API_KEY=your-cohere-key-here
```

Bring it up:
```bash
docker compose up -d
docker compose ps   # both should settle to "healthy"
```

> **Note on architecture:** the FastAPI app itself runs directly on your machine via `uv run python run.py` (added in Module 3), not inside Docker, for the rest of this course — that gives instant reload on every code change. Only Postgres and Redis are containerized. Containerizing the app itself (per `PLAN.md` §7's `uv sync --frozen` Dockerfile) is a good stretch exercise after Module 16, not before.

### Ask the learner

- *"Why does `docker-compose.yml` have `depends_on: condition: service_healthy` instead of just `depends_on: postgres`?"* **Hint ladder:** (1) "if Postgres's container has *started* but is still initializing, is it actually ready to accept connections?" → (2) "what would happen if the app tried to connect during that gap?" → (3) explain: plain `depends_on` only waits for the container process to start, not for the database inside it to be ready to accept connections — `condition: service_healthy` waits for the actual healthcheck to pass.
- *"If you edit `init-db/init.sql` after `docker compose up -d` has already run once, and then restart the containers, does your edit take effect?"* Let them test it. **Hint ladder:** (1) "what does the `pgdata` named volume actually store?" → (2) "do init scripts run every container start, or only once?" → (3) explain: `docker-entrypoint-initdb.d` scripts only run the *first* time a container initializes against an *empty* data volume — once `pgdata` has data in it, `init.sql` is never read again. To apply a schema change, you must `docker compose down -v` (destroying the volume) or apply the SQL manually.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `docker compose ps` never shows "healthy" for postgres | Port 5432 already in use by a local Postgres install | Stop the local Postgres service, or remap the port in `docker-compose.yml` |
| Edited `init.sql` seems to have no effect | Volume already initialized (see above) | `docker compose down -v && docker compose up -d` — **this destroys all data**, fine now, not fine once real data matters |

### Quiz + checkpoint

1. What does `CREATE EXTENSION vector` actually add to the database?
   <details><summary>Answer</summary>The <code>pgvector</code> extension, which adds a <code>vector</code> column type and distance operators (like <code>&lt;=&gt;</code> for cosine distance) so Postgres can store and search embedding vectors natively.</details>
2. If you need to wipe and reapply `init-db/init.sql`, what command actually does that?
   <details><summary>Answer</summary><code>docker compose down -v</code> (the <code>-v</code> removes the named volume) followed by <code>docker compose up -d</code>.</details>

**Checkpoint:** `docker compose ps` shows both services healthy; learner can explain what would go wrong without the healthcheck gate.

---

## Module 2 — Ingest v1

### Why this module

> **Ask the learner:** "We have a database now, but it's empty. What's the smallest ingestion pipeline that gets *one* folder of real documents into it?"

### Learning objectives

- Learner can load, chunk, embed, and store documents in `pgvector` via `langchain-postgres`.
- Learner understands the division of responsibility between the hand-written SQL schema (`init.sql`) and the vector store client (`AsyncPGVectorStore`) — this project commits to **SQL as the source of truth for schema**; the vector store client only ever reads and writes rows in a table that already exists.

### Step-by-step build

1. Copy just the FAQ documents in for now:
   ```bash
   mkdir -p data/faqs
   cp ../sample-corpus/fernwood-labs/faqs/*.md data/faqs/
   ```
2. Add dependencies:
   ```bash
   uv add langchain langchain-core langchain-openai langchain-community langchain-text-splitters langchain-postgres langchain-classic "psycopg[binary,pool]" unstructured markdown
   ```
3. Extend `init-db/init.sql` with the table definition, then **tear down and recreate the volume** so the new script actually runs (per Module 1's gotcha):
   ```sql
   CREATE TABLE IF NOT EXISTS fernwood_chunks (
       langchain_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
       content text,
       embedding vector(1536),
       langchain_metadata jsonb
   );
   ```
   ```bash
   docker compose down -v && docker compose up -d
   ```
4. Create `app/__init__.py` (empty) and `app/utils.py` — the vector store factory. Call `load_dotenv()` at the top, before reading `DATABASE_URL` — without it, `PG_CONN_STR` is `None` and nothing in this module works at all.
5. Create `app/ingest.py` — load the two FAQ files, chunk, embed, store.
6. Run the ingest script directly (not via the API yet — that's Module 3/4) and confirm rows landed in Postgres.

### Full code

`app/utils.py`:
```python
import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.v2.engine import PGEngine
from langchain_postgres.v2.async_vectorstore import AsyncPGVectorStore

# psycopg's async mode cannot run under Windows' default ProactorEventLoop.
# Must be set before any event loop is created -- do it here, at import time,
# since every module that talks to the database imports this one first.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

PG_CONN_STR = os.getenv("DATABASE_URL")
PG_ENGINE = PGEngine.from_connection_string(PG_CONN_STR)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


async def get_vector_store() -> AsyncPGVectorStore:
    return await AsyncPGVectorStore.create(
        engine=PG_ENGINE,
        embedding_service=embeddings,
        table_name="fernwood_chunks",
        metadata_json_column="langchain_metadata",
    )
```

`app/ingest.py`:
```python
import asyncio
import os

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .utils import get_vector_store

DATA_DIR = os.getenv("DATA_DIR", "data")


def _load_faqs():
    docs = []
    faqs_dir = os.path.join(DATA_DIR, "faqs")
    for filename in sorted(os.listdir(faqs_dir)):
        if filename.endswith(".md"):
            docs.extend(UnstructuredMarkdownLoader(os.path.join(faqs_dir, filename)).load())
    return docs


def _chunk(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    return splitter.split_documents(docs)


async def run_ingest():
    docs = _load_faqs()
    chunks = _chunk(docs)
    store = await get_vector_store()
    await store.aadd_documents(chunks)
    print(f"Ingested {len(docs)} documents, {len(chunks)} chunks.")
    return {"documents": len(docs), "chunks": len(chunks)}


if __name__ == "__main__":
    asyncio.run(run_ingest())
```

Run:
```bash
uv run python -m app.ingest
```

Confirm it landed:
```bash
docker compose exec postgres psql -U postgres -c "SELECT count(*) FROM fernwood_chunks;"
```

### Ask the learner

- *"Why does `init.sql` define the table by hand instead of letting `AsyncPGVectorStore` create it automatically?"* **Hint ladder:** (1) "if two different parts of the system could each decide the schema, what happens when they disagree?" → (2) "which one would you want to be the single source of truth — a Python client library's defaults, or a SQL file you can read, review, and migrate deliberately?" → (3) explain: this project makes a deliberate choice — SQL owns the schema, the vector store client is just a reader/writer of an existing table. (This directly fixes an ambiguity the original `company-knowledge-assistant` left unresolved — worth saying so.)
- *"What would happen right now if you ran `uv run python -m app.ingest` twice in a row?"* Have them try it, then count rows again. **Hint ladder:** (1) "did it ask you whether the data already existed?" → (2) "look at the row count before and after the second run" → (3) confirm: it silently doubles everything — flag this out loud as a problem *to be solved properly in Module 13*, not now.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `relation "fernwood_chunks" does not exist` | `init.sql` edited after the volume already initialized | `docker compose down -v && docker compose up -d` |
| `connection refused` on `DATABASE_URL` | Containers not up, or wrong port | `docker compose ps`; confirm `localhost:5432` matches the compose file |
| **(Windows only)** `psycopg.InterfaceError: Psycopg cannot use the 'ProactorEventLoop' to run in async mode` | Windows' default `asyncio` event loop policy is incompatible with psycopg's async driver | Confirm `app/utils.py` sets `asyncio.WindowsSelectorEventLoopPolicy()` at import time, before `load_dotenv()` — this is already in the code above; if you're seeing this, something imported `asyncio` and created a loop before `app.utils` was imported |
| Ingest "succeeds" with 0 chunks | `data/faqs/` empty or `.md` files not copied | Re-check the `cp` command in step 1 |

### Quiz + checkpoint

1. In this project, which component is allowed to change the database schema?
   <details><summary>Answer</summary>Only <code>init-db/init.sql</code>, run by Postgres on container initialization. <code>AsyncPGVectorStore</code> reads and writes rows in the table <code>init.sql</code> already created — it never creates or alters the table itself.</details>
2. What does `RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)` actually control, and have you seen these exact two numbers before?
   <details><summary>Answer</summary>They control how large each chunk is (in characters) and how much consecutive chunks overlap. These are the same values used in the real <code>company-knowledge-assistant</code> project this course is modeled on — Module 6 will test whether they're actually good values, instead of taking them on faith.</details>

**Checkpoint:** `SELECT count(*) FROM fernwood_chunks;` returns a non-zero number matching the FAQ documents' chunk count.

---

## Module 3 — Ask v1

### Why this module

> **Ask the learner:** "Data's in the database. Nothing can ask it a question yet. What's the smallest `/ask` endpoint that retrieves and answers — and actually says 'I don't know' when it should?"

### Learning objectives

- Learner can wire a retriever + grounded prompt into a FastAPI endpoint.
- Learner can verify grounding against the golden set's unanswerable questions, not just vibes.

### Step-by-step build

1. Add `uv add langchain-openai` already present; no new deps needed.
2. Create `app/rag.py` — retriever, grounded prompt, the answer function.
3. Create `app/api.py` — FastAPI app with `POST /ask`.
4. Create `run.py` — a small entrypoint that starts the server. Use this instead of `uv run uvicorn app.api:app --reload` directly: uvicorn's CLI creates its event loop *before* importing the app, which on Windows is too late to apply the `WindowsSelectorEventLoopPolicy` fix from Module 2's `app/utils.py` — setting the policy here, before `uvicorn.run()` is even called, works on every platform.
5. Run the server and test against a question the FAQ docs *can* answer, then one from the golden set's unanswerable trio (`q22`–`q24` in `sample-corpus/golden_qna.jsonl`) to prove grounding actually works before building anything else on top of it.

### Full code

`app/rag.py`:
```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from .utils import get_vector_store

SYSTEM = """You are a grounded company knowledge assistant for Fernwood Labs.
Answer strictly from the provided context. If the answer isn't in the context,
reply with exactly: "I don't know."
Be concise.
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        ("user", "Question:\n{input}\n\nContext:\n{context}"),
    ]
)


async def build_chain():
    store = await get_vector_store()
    retriever = store.as_retriever(search_kwargs={"k": int(os.getenv("RETRIEVAL_K", "5"))})
    llm = ChatOpenAI(model="gpt-4o-mini")
    doc_chain = create_stuff_documents_chain(llm, PROMPT)
    return create_retrieval_chain(retriever, doc_chain)


async def answer(question: str):
    chain = await build_chain()
    result = await chain.ainvoke({"input": question})
    sources = sorted({d.metadata.get("source") for d in result["context"] if d.metadata.get("source")})
    contexts = [d.page_content for d in result["context"]]
    return result["answer"], sources, contexts
```

`app/api.py`:
```python
from fastapi import FastAPI
from pydantic import BaseModel

from .rag import answer

app = FastAPI(title="Fernwood Labs Knowledge Assistant")


class Ask(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/ask")
async def ask(payload: Ask):
    answer_text, sources, contexts = await answer(payload.question)
    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

`run.py`:
```python
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
```

Run:
```bash
uv run python run.py
```

Test (in a second terminal):
```bash
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "Who approves a remote work arrangement?"}'

curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "What is Fernwood Labs parental leave policy?"}'
```

### Ask the learner

- *"The second question has no answer anywhere in the FAQ documents. Did it say 'I don't know,' or did it make something up?"* If it hallucinated, this is a live debugging moment, not a scripted one — walk the grounding prompt line by line with them. **Hint ladder:** (1) "is the system message's instruction unambiguous, or does it leave room for the model to 'be helpful' instead?" → (2) "try making the required refusal string more explicit, the way Part 1 Module 2 did" → (3) tighten the wording until it's reliable.
- *"`sources` is built from a `set` comprehension before being sorted — why not just a list?"* **Hint ladder:** (1) "if two retrieved chunks came from the same file, what would a plain list contain?" → (2) "is that useful to show a user?" → (3) a `set` deduplicates automatically — a user wants to know *which documents* were used, not how many chunks came from each.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ConnectionRefusedError` on first request | Postgres container not actually up | Confirm `docker compose ps` shows both services healthy |
| `OPENAI_API_KEY` not picked up | Running something other than `app/utils.py`'s `load_dotenv()` path — e.g. a fresh script that imports `ChatOpenAI` directly without importing from `app.utils` first | Make sure anything using the API key imports through `app.utils` (or calls `load_dotenv()` itself) before constructing a client |

### Quiz + checkpoint

1. What are the three keys in the JSON `/ask` returns, and where does each one come from?
   <details><summary>Answer</summary><code>answer</code> (the LLM's generated text), <code>sources</code> (deduplicated, sorted filenames from the retrieved chunks' metadata), <code>contexts</code> (the raw text of every retrieved chunk) — all three come out of <code>result["context"]</code> and <code>result["answer"]</code> from <code>create_retrieval_chain</code>'s output.</details>
2. Why test the unanswerable question *before* building anything else on top of this endpoint?
   <details><summary>Answer</summary>Grounding is the foundation every later module (reranking, caching, multi-turn) sits on top of — if "I don't know" doesn't work reliably now, every later module inherits a silent hallucination risk that gets harder to isolate the more is built on top of it.</details>

**Checkpoint:** the parental-leave question reliably returns "I don't know"; the remote-work-approval question returns a correct, grounded answer citing `faqs/remote-work-faq.md`.

---

## Module 4 — Multi-Format Ingest, Categories, and a Planted Bug

### Why this module

> **Ask the learner:** "Right now this assistant only knows about FAQs. Fernwood Labs has policies, handbooks, guides, and announcements too, in `.md`, `.pdf`, and `.docx`. What has to change to ingest all of it?"

### Learning objectives

- Learner can dispatch to different loaders by file extension, with per-file error isolation.
- Learner can attach folder-derived `category` metadata and filter retrieval by it.
- Learner can diagnose a hardcoded-filter bug from a user-facing symptom, not from being told where it is.

### Step-by-step build

1. Copy in the rest of the corpus:
   ```bash
   cp -r ../sample-corpus/fernwood-labs/policies data/
   cp -r ../sample-corpus/fernwood-labs/handbook data/
   cp -r ../sample-corpus/fernwood-labs/guides data/
   cp -r ../sample-corpus/fernwood-labs/announcements data/
   ```
2. Add format dependencies:
   ```bash
   uv add pymupdf "unstructured[docx]"
   ```
3. Add a `category` column, then recreate the volume:
   ```sql
   ALTER TABLE fernwood_chunks ADD COLUMN IF NOT EXISTS category text;
   ```
   ```bash
   docker compose down -v && docker compose up -d
   ```
4. Rewrite `app/ingest.py` to walk every folder, dispatch by extension, tag each document with its parent folder name as `category`, and isolate per-file failures so one bad file doesn't kill the whole run.
5. Update `app/utils.py` to register `category` as a filterable metadata column.
6. Add a background-task `/ingest` endpoint with status polling (ingesting all five folders now takes long enough to want this), and run it.
7. **Before fixing anything**, wire `/ask` with a category *hardcoded* to `"faqs"` — ship it exactly this way and ask a policy question live. Let the "I don't know" land as a surprise, then diagnose and fix it together.

### Full code

`app/ingest.py`:
```python
import asyncio
import glob
import os
import traceback

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .utils import get_vector_store

DATA_DIR = os.getenv("DATA_DIR", "data")

LOADERS = {
    ".md": UnstructuredMarkdownLoader,
    ".pdf": PyMuPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".txt": TextLoader,
}


def _load_docs(base: str = DATA_DIR):
    docs = []
    for path in glob.glob(os.path.join(base, "**", "*"), recursive=True):
        if os.path.isdir(path) or os.path.basename(path).startswith("."):
            continue
        ext = os.path.splitext(path)[1].lower()
        loader_cls = LOADERS.get(ext)
        if loader_cls is None:
            continue
        category = os.path.relpath(path, base).split(os.sep)[0]
        try:
            for doc in loader_cls(path).load():
                doc.metadata["category"] = category
                docs.append(doc)
        except Exception:
            print(f"INGEST ERROR: failed to load {path}")
            traceback.print_exc()
    return docs


def _chunk(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    return splitter.split_documents(docs)


async def run_ingest():
    docs = _load_docs()
    chunks = _chunk(docs)
    store = await get_vector_store()
    await store.aadd_documents(chunks)
    print(f"Ingested {len(docs)} documents, {len(chunks)} chunks across categories.")
    return {"documents": len(docs), "chunks": len(chunks)}


if __name__ == "__main__":
    asyncio.run(run_ingest())
```

`app/utils.py` — add `metadata_columns`:
```python
async def get_vector_store() -> AsyncPGVectorStore:
    return await AsyncPGVectorStore.create(
        engine=PG_ENGINE,
        embedding_service=embeddings,
        table_name="fernwood_chunks",
        metadata_json_column="langchain_metadata",
        metadata_columns=["category"],
    )
```

`app/rag.py` — accept a category filter:
```python
async def build_chain(category: str | None = None):
    store = await get_vector_store()
    search_kwargs = {"k": int(os.getenv("RETRIEVAL_K", "5"))}
    if category:
        search_kwargs["filter"] = {"category": category}
    retriever = store.as_retriever(search_kwargs=search_kwargs)
    llm = ChatOpenAI(model="gpt-4o-mini")
    doc_chain = create_stuff_documents_chain(llm, PROMPT)
    return create_retrieval_chain(retriever, doc_chain)


async def answer(question: str, category: str | None = None):
    chain = await build_chain(category)
    result = await chain.ainvoke({"input": question})
    sources = sorted({d.metadata.get("source") for d in result["context"] if d.metadata.get("source")})
    contexts = [d.page_content for d in result["context"]]
    return result["answer"], sources, contexts
```

`app/api.py` — **ship this version first, bug included**:
```python
import asyncio
import time

from fastapi import FastAPI
from pydantic import BaseModel

from .ingest import run_ingest
from .rag import answer

app = FastAPI(title="Fernwood Labs Knowledge Assistant")

_ingest_lock = asyncio.Lock()
_ingest_task: asyncio.Task | None = None
_ingest_status = {
    "status": "idle",
    "started_at": None,
    "finished_at": None,
    "stats": None,
    "error": None,
}


async def _ingest_job():
    _ingest_status.update(status="running", started_at=time.time(), finished_at=None, stats=None, error=None)
    try:
        stats = await run_ingest()
        _ingest_status.update(status="succeeded", finished_at=time.time(), stats=stats)
    except Exception as e:
        _ingest_status.update(status="failed", finished_at=time.time(), error=str(e))


@app.post("/ingest")
async def kick_off_ingest():
    global _ingest_task
    async with _ingest_lock:
        if _ingest_task and not _ingest_task.done():
            return {"ok": False, "message": "Ingestion already running"}
        _ingest_task = asyncio.create_task(_ingest_job())
    return {"ok": True, "message": "Ingestion started"}


@app.get("/ingest/status")
async def ingest_status():
    return {"ok": True, **_ingest_status}


class Ask(BaseModel):
    question: str


@app.post("/ask")
async def ask(payload: Ask):
    # PLANTED BUG: category is hardcoded. Only faqs/ ever gets searched, no
    # matter what's asked. Ship it exactly like this and let the symptom
    # surface live before looking at this line.
    category = "faqs"
    answer_text, sources, contexts = await answer(payload.question, category=category)
    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

Run ingestion:
```bash
curl -s -X POST localhost:8000/ingest
curl -s localhost:8000/ingest/status   # poll until "status": "succeeded"
```

Now trigger the bug on purpose:
```bash
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "What is the maximum number of PTO days I can carry forward?"}'
```

### Ask the learner

- *"That's a real policy question, and we just ingested the policy documents. Why did it say 'I don't know'?"* This is the heart of the module — let them actually investigate rather than announcing the bug. **Hint ladder:** (1) "check `/ingest/status` — did the policies actually land in the database? Query `fernwood_chunks` directly and check the `category` column." → (2) "now look at what `/ask` actually passes as the category filter — is it related to what was asked at all?" → (3) point at the hardcoded `category = "faqs"` line.
- *"What's the fix — remove the filter entirely, or something more careful?"* **Hint ladder:** (1) "if you remove the filter completely, what happens to Module 3's advantage of being able to narrow a search?" → (2) "where should the category actually come from?" → (3) land on: make it an optional request field, defaulting to `None` (search everything) when the caller doesn't specify one.

Apply the fix:
```python
class Ask(BaseModel):
    question: str
    category: str | None = None


@app.post("/ask")
async def ask(payload: Ask):
    answer_text, sources, contexts = await answer(payload.question, category=payload.category)
    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

Re-run the same PTO question (now with no `category` field at all) and confirm it answers correctly.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `/ingest/status` shows `"failed"` with a `.docx` or `.pdf` error | Missing format dependency | Confirm `uv add pymupdf "unstructured[docx]"` succeeded |
| Ingest "succeeds" but some files are silently missing | A loader raised and was caught by the per-file `try/except` | Check the server logs for `INGEST ERROR: failed to load ...` lines — this is the isolation working as intended, not a silent failure; always read the logs after ingesting |
| Category filter still seems to do nothing after the fix | Stale `/ask` process from `--reload` not picking up the edit, or old ingested rows missing `category` from before Module 4's `ALTER TABLE` | Confirm the server restarted; confirm you re-ingested *after* the volume was recreated with the `category` column |

### Quiz + checkpoint

1. Why does `_load_docs` wrap each file's loading in its own `try/except`, instead of one `try/except` around the whole loop?
   <details><summary>Answer</summary>So one malformed or unsupported file doesn't abort ingestion for every other file — each file's failure is isolated and logged, and the run continues.</details>
2. What's the actual difference between Module 4's quick fix and what Module 7 calls "Filtering, properly"?
   <details><summary>Answer</summary>Module 4's fix makes category come from the request instead of being hardcoded — the obvious break is gone. Module 7 goes further: validating the category against the real set of categories, and empirically tuning <code>k</code> rather than guessing — refining a correct-but-unrefined fix into a measured one.</details>

**Checkpoint:** every category's documents are reachable through `/ask` with no `category` field at all; the learner can explain, from the symptom alone, why the hardcoded version failed.

### Scoreboard entry

Not yet — the golden set doesn't exist in this project until Module 5. Note in `SCOREBOARD.md` that this module is "pre-baseline" and move on.

---

## Module 5 — Golden Baseline

### Why this module

> **Ask the learner:** "Every module so far has been judged by 'seems to work.' How would you know, with a number, whether the *next* change you make is actually an improvement?"

### Learning objectives

- Learner can run the golden set against the live API and score it with RAGAS.
- Learner can distinguish "wrong answer" from "correctly refused to answer" in the scoring, rather than conflating them.

### Step-by-step build

1. Bring in the golden set:
   ```bash
   mkdir -p seed
   cp ../sample-corpus/golden_qna.jsonl seed/golden_qna.jsonl
   ```
2. Add dependencies:
   ```bash
   uv add ragas pandas requests
   uv add "langchain-community<0.4"
   ```
   The second line matters: `ragas` unconditionally imports `langchain_community.chat_models.vertexai`, a module that was removed from `langchain-community` 0.4.x. Without pinning below 0.4, importing `ragas` fails with `ModuleNotFoundError: No module named 'langchain_community.chat_models.vertexai'` — a real dependency conflict between two libraries that both move fast, not a mistake in your code.
3. Create `scripts/eval.py` — split the 24 questions into the 21 answerable and 3 unanswerable ones; score the answerable ones with RAGAS, score the unanswerable ones with a simple refusal check.
4. Create `SCOREBOARD.md`.
5. With the server running and fully ingested, run the eval script and record the baseline.

### Full code

`scripts/eval.py`:
```python
import json
import os

import requests
from langchain_openai import ChatOpenAI
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness
from ragas.run_config import RunConfig

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
SEED_PATH = os.getenv(
    "SEED_PATH", os.path.join(os.path.dirname(__file__), "..", "seed", "golden_qna.jsonl")
)


def load_golden_set(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    rows = load_golden_set(SEED_PATH)
    answerable = [r for r in rows if r["answerable"]]
    unanswerable = [r for r in rows if not r["answerable"]]

    samples = []
    for row in answerable:
        resp = requests.post(f"{BASE_URL}/ask", json={"question": row["question"]}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        samples.append(
            SingleTurnSample(
                user_input=row["question"],
                response=data["answer"],
                retrieved_contexts=data["contexts"] or ["(no context retrieved)"],
                reference=row["answer"],
            )
        )

    refusals = 0
    for row in unanswerable:
        resp = requests.post(f"{BASE_URL}/ask", json={"question": row["question"]}, timeout=60)
        resp.raise_for_status()
        if "don't know" in resp.json()["answer"].lower():
            refusals += 1
    print(f"Refusal check: {refusals}/{len(unanswerable)} unanswerable questions correctly got 'I don't know'.\n")

    dataset = EvaluationDataset(samples)
    judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    run_config = RunConfig(max_workers=4, timeout=60)
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=judge_llm,
        run_config=run_config,
    )
    means = result.to_pandas().mean(numeric_only=True).to_dict()
    print(f"RAGAS averages over {len(samples)} answerable questions:")
    for key, value in means.items():
        print(f"  {key}: {value:.3f}")


if __name__ == "__main__":
    main()
```

`SCOREBOARD.md`:
```markdown
# Scoreboard

| Module | Change | faithfulness | answer_relevancy | context_precision | context_recall | refusal rate | notes |
|---|---|---|---|---|---|---|---|
| 5 | Baseline, all 5 categories, k=5, no rerank | | | | | 3/3 | |
```

Run (two terminals — server, then eval):
```bash
uv run python run.py
uv run python scripts/eval.py
```

### Ask the learner

- *"The script splits answerable from unanswerable questions and scores them completely differently. Why not just run all 24 through RAGAS the same way?"* **Hint ladder:** (1) "what would `context_recall` even mean for a question where the correct context is 'none exists'?" → (2) "if you blended a 'correctly refused' answer into the accuracy average, would it look like a win or a loss?" → (3) explain: RAGAS's metrics assume there *is* a correct grounded answer to compare against; for the deliberately unanswerable questions, the thing worth measuring is binary — did it refuse or did it hallucinate — which is a different question than "how good was the answer."
- *"`retrieved_contexts=data["contexts"] or ["(no context retrieved)"]` — why the fallback?"* **Hint ladder:** (1) "what does RAGAS's `context_precision` do if it's handed an empty list?" → (2) "try removing the fallback and see what breaks." → (3) some RAGAS metrics error or produce NaN on an empty context list — the placeholder keeps the pipeline running and should show up as a *bad* score rather than a crash.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ConnectionError` from `requests.post` | Server not running in the other terminal | Start `uv run python run.py` first |
| RAGAS hangs for a long time | `max_workers` too high for your OpenAI rate limit tier | Lower `max_workers` in `RunConfig` |
| Scores look suspiciously perfect | Judge LLM (`gpt-4o-mini`) is lenient on the exact wording used in `sample-corpus/golden_qna.jsonl`'s `answer` fields | Expected at first — this becomes more informative as later modules introduce harder failure modes (reranking bugs, recency conflicts) |

### Quiz + checkpoint

1. Which of the four RAGAS metrics would you expect to move the most from adding reranking (Module 9), and why?
   <details><summary>Answer</summary><code>context_precision</code> most directly — reranking changes which chunks get kept, not whether the model stays faithful to them. (The actual effect gets measured and recorded for real in Module 9 — this is a prediction to check later.)</details>
2. Why record "pre-baseline" in Module 4's row instead of leaving it blank?
   <details><summary>Answer</summary>So the scoreboard's history is honest about what *couldn't* be measured yet, rather than looking like a gap or an oversight later.</details>

**Checkpoint:** `SCOREBOARD.md` has a real baseline row with four numbers and a 3/3 refusal rate (or an honest note if it's not 3/3 yet).

### Scoreboard entry

Baseline recorded. Every module from here either moves a number or explicitly says why it doesn't.

---

## Module 6 — Chunking Experiments

### Why this module

> **Ask the learner:** "`chunk_size=900, chunk_overlap=120` — where did those numbers come from?"

Correct answer: nowhere principled; they were copied from the real `company-knowledge-assistant` project this course is modeled on, which also never tested them. Time to actually test them.

### Learning objectives

- Learner can treat a hyperparameter as an experiment, not a default to trust.
- Learner understands why re-ingesting with a new chunk size requires wiping existing data first (idempotency hasn't been built yet).

### Step-by-step build

1. Pick 2–3 alternative configurations, e.g. `(500, 100)` and `(1400, 200)`.
2. For each configuration: edit `chunk_size`/`chunk_overlap` in `app/ingest.py`, **wipe the database** (`docker compose down -v && docker compose up -d` — call out loud that this is only acceptable because Module 13 hasn't been built yet), re-ingest, re-run `scripts/eval.py`, record the row.
3. Compare all three rows in `SCOREBOARD.md` and pick a winner with a stated reason — not just "the highest number."

### Full code

No new files — just the two changed lines in `app/ingest.py`'s `_chunk` function, run three times:
```python
def _chunk(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # experiment 2
    return splitter.split_documents(docs)
```

`SCOREBOARD.md`, extended:
```markdown
| 6a | chunk_size=500, overlap=100 | | | | | | smaller chunks |
| 6b | chunk_size=1400, overlap=200 | | | | | | larger chunks |
| 6c | chunk_size=900, overlap=120 (reverted) | | | | | | back to baseline config |
```

### Ask the learner

- *"Smaller chunks mean more of them for the same document. What's the tradeoff against larger chunks?"* **Hint ladder:** (1) "if a fact spans two sentences that end up in different small chunks, what happens to a question about it?" → (2) "if a chunk is huge, and only one sentence in it is relevant, what else gets stuffed into the model's context along with that one sentence?" → (3) land on: smaller chunks risk splitting a fact across a boundary; larger chunks risk diluting the relevant sentence with irrelevant surrounding text — both can hurt `context_precision` in different ways.
- *"Why do we have to wipe the whole database between experiments right now?"* **Hint ladder:** (1) "what happens to the old 900/120 chunks if you just re-ingest with 500/100 settings?" → (2) "does the ingestion pipeline know how to remove old chunks for a file before adding new ones?" → (3) not yet — that's exactly Module 13's job. Flag this explicitly as a preview, not a surprise, when it arrives.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Scores barely change between configurations | 900/120 may already be reasonable for this corpus's document lengths (most Fernwood docs are short) | A "no significant difference" result is a valid, recordable finding — don't manufacture a winner that isn't there |
| Forgot to re-ingest after changing chunk size | Old chunks from the previous config are still the only ones in the database | Always: edit code → wipe volume → re-ingest → re-eval, in that order, every time |

### Quiz + checkpoint

1. Why is "wipe the database between every experiment" an acceptable workflow *right now* but clearly wouldn't be once this assistant has real users?
   <details><summary>Answer</summary>Right now there's no real usage to lose and no idempotency problem yet to work around — it's a deliberate shortcut while iterating. Once Module 13 builds proper re-ingestion, this workflow is replaced; it was never meant to be the permanent answer.</details>

**Checkpoint:** three recorded scoreboard rows, a chosen configuration, and a one-sentence reason that isn't just "it scored highest."

### Scoreboard entry

Three experimental rows plus the final chosen configuration, reverted or kept, clearly marked in `SCOREBOARD.md`.

---

## Module 7 — Filtering, Properly

### Why this module

> **Ask the learner:** "Module 4's fix made category filtering *work*. Does that mean it's *good* — is `k=5` actually the right number of chunks to retrieve, for every category, every time?"

### Learning objectives

- Learner can validate a request parameter against a known, finite set instead of trusting arbitrary input.
- Learner can empirically compare retrieval depth (`k`) against the scoreboard rather than guessing.

### Step-by-step build

1. Add a known-categories check to `app/api.py` so an invalid `category` value fails clearly instead of silently returning zero results.
2. Sweep `k` at 3, 5, and 10 (using the chunking configuration Module 6 settled on), re-running `scripts/eval.py` at each value.
3. Record all three in `SCOREBOARD.md`, pick a value, and verify — by asking one question per category — that every one of the five categories is actually reachable.

### Full code

`app/api.py` — add validation:
```python
KNOWN_CATEGORIES = {"policies", "handbook", "guides", "faqs", "announcements"}


class Ask(BaseModel):
    question: str
    category: str | None = None


@app.post("/ask")
async def ask(payload: Ask):
    if payload.category is not None and payload.category not in KNOWN_CATEGORIES:
        return {"error": f"Unknown category '{payload.category}'. Choose from: {sorted(KNOWN_CATEGORIES)}"}
    answer_text, sources, contexts = await answer(payload.question, category=payload.category)
    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

`k` sweep — just change `.env`'s `RETRIEVAL_K` and restart the server between runs:
```env
RETRIEVAL_K=3
```

### Ask the learner

- *"What's the actual tradeoff as `k` goes up?"* **Hint ladder:** (1) "if you retrieve 10 chunks instead of 3, is the model more or less likely to have the right one somewhere in there?" → (2) "but what else is now competing for the model's attention in that stuffed context?" → (3) higher `k` tends to help `context_recall` (the right chunk is more likely present) but can hurt `context_precision` and sometimes `faithfulness` (more irrelevant material for the model to get distracted by or blend answers from).
- *"Why validate `category` against a fixed set instead of just trying the filter and returning empty results for a typo?"* **Hint ladder:** (1) "if someone requests `category: 'polices'` (typo), what would the old behavior silently do?" → (2) "is 'confidently wrong because of a typo' better or worse than 'clearly told you your input was invalid'?" → (3) fail loud and specific beats fail silent and confusing.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| One category's test question still fails | That category's documents didn't actually get chunked/ingested correctly | Query `fernwood_chunks` directly, filter by `category`, confirm row counts per category match expectations |
| `k=10` makes answers noticeably worse | Low-relevance chunks are getting stuffed in and confusing the model | This is itself the lesson — it's also exactly the problem Module 9's reranking exists to solve |

### Quiz + checkpoint

1. Why might `k=10` score *worse* than `k=5` on `context_precision` even though it retrieves strictly more chunks (a superset)?
   <details><summary>Answer</summary><code>context_precision</code> measures what fraction of retrieved chunks were actually relevant — adding more low-relevance chunks on top of the same relevant ones directly lowers that fraction, even though recall (did we get the right one at all) may improve or stay the same.</details>

**Checkpoint:** all five categories verified reachable with real test questions; a `k` value chosen and justified with scoreboard numbers, not intuition.

### Scoreboard entry

Three `k`-sweep rows, with the chosen value flagged as the one carried forward into later modules.

---

## Module 8 — HNSW Index

### Why this module

> **Ask the learner:** "Every retrieval so far has done a brute-force scan over every row in `fernwood_chunks`. That's fine at a few hundred chunks. What happens at a few million?"

### Learning objectives

- Learner can build an approximate nearest-neighbor index and knows it trades perfect recall for speed.
- Learner correctly predicts this module won't move the accuracy scoreboard, and measures latency instead.

### Step-by-step build

1. Create `scripts/create_index.py` using `langchain-postgres`'s `HNSWIndex`.
2. Create `scripts/benchmark_latency.py` — time 10 repeated calls to `/ask` for the same question, before and after the index exists.
3. Run the benchmark, build the index, run the benchmark again, record both numbers — explicitly *not* in the accuracy columns of `SCOREBOARD.md`.

### Full code

`scripts/create_index.py`:
```python
import asyncio

from langchain_postgres.v2.indexes import DistanceStrategy, HNSWIndex

from app.utils import get_vector_store


async def main():
    store = await get_vector_store()
    index = HNSWIndex(
        name="fernwood_chunks_hnsw",
        distance_strategy=DistanceStrategy.COSINE_DISTANCE,
        m=16,
        ef_construction=64,
    )
    await store.aapply_vector_index(index, concurrently=True)
    print("HNSW index created.")


if __name__ == "__main__":
    asyncio.run(main())
```

`scripts/benchmark_latency.py`:
```python
import os
import time

import requests

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
QUESTION = "What is the maximum number of PTO days I can carry forward?"


def main():
    durations = []
    for _ in range(10):
        start = time.perf_counter()
        requests.post(f"{BASE_URL}/ask", json={"question": QUESTION}, timeout=60)
        durations.append(time.perf_counter() - start)
    durations.sort()
    print(f"p50: {durations[4]:.3f}s   p95: {durations[9]:.3f}s   min: {durations[0]:.3f}s")


if __name__ == "__main__":
    main()
```

Run:
```bash
uv run python scripts/benchmark_latency.py        # before
uv run python scripts/create_index.py
uv run python scripts/benchmark_latency.py        # after
```

### Ask the learner

- *"At roughly a few hundred rows, do you expect a measurable latency difference?"* Likely not much — this corpus is intentionally small. **Hint ladder:** (1) "is this index actually about *this* corpus, or about what happens as the corpus grows?" → (2) "what would you expect this comparison to look like at a million rows instead of a few hundred?" → (3) the lesson here is about understanding *why* the index exists and what it trades off, even when this specific demo corpus is too small to show a dramatic number — don't manufacture drama that isn't there.
- *"`m=16, ef_construction=64` — what do these control, roughly?"* **Hint ladder:** (1) "HNSW is building a graph of approximate nearest neighbors — `m` controls how many connections each node keeps" → (2) "`ef_construction` controls how much effort goes into building a *good* graph at index-creation time" → (3) both are a speed/accuracy tradeoff knob — higher values mean slower index builds and queries but better recall; there's no universally correct value, only a measured one for your data and query load.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Benchmark numbers are noisy / inconsistent | Normal — `/ask` round-trips to OpenAI's API, which dominates total latency compared to the local vector search | Note this explicitly: the index primarily matters for *retrieval* latency, which is a small fraction of this endpoint's total time until the corpus is much larger |
| `aapply_vector_index` errors about an existing index | Script run twice | Either drop the index first or treat this as expected and move on |

### Quiz + checkpoint

1. Why does this module not add a new row to `SCOREBOARD.md`'s accuracy columns?
   <details><summary>Answer</summary>An HNSW index changes *how fast* the same (approximately) correct results are found — it is not expected to change the model's faithfulness, relevancy, precision, or recall. Recording a latency-only row keeps the scoreboard honest about what each module actually affects.</details>

**Checkpoint:** index created successfully; learner can state, without being told, why this module doesn't touch the accuracy scoreboard.

### Scoreboard entry

Latency only — p50/p95 before and after, in a separate note, not the accuracy table.

---

## Module 9 — Reranking, and the Recency Bug

### Why this module

> **Ask the learner:** "We're pulling the top-k chunks by vector similarity. Similarity to what, exactly — the question, or a *good answer* to the question? Is that always the same thing?"

### Learning objectives

- Learner can add a reranking stage with `CohereRerank` and `ContextualCompressionRetriever`.
- Learner can diagnose a wrong-recency answer from symptom to root cause, and fix it with a prompting + metadata discipline — not a retrieval trick.

### Step-by-step build

1. Add dependencies:
   ```bash
   uv add langchain-cohere cohere
   ```
2. **Before changing the prompt**, ask the recency question live:
   ```bash
   curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "What is the maximum number of PTO days that can be carried forward to the next year?"}'
   ```
   The two PTO documents (`policies/pto-policy-2024.md`, `policies/pto-policy-2025.md`) are textually similar and both score highly — depending on which happens to rank first in the stuffed context, the answer may come back as 5 days (the superseded figure) instead of 8, or hedge inconsistently between the two. Run it a couple of times if it doesn't fail on the first try; this is a real, not scripted, failure mode.
3. Diagnose: print `contexts` from the response and confirm both PTO chunks are present, with no signal in the prompt about which one is current.
4. Fix in two parts: widen initial retrieval and rerank down to the most relevant few (`CohereRerank`), **and** add an explicit recency rule to the system prompt, since reranking alone doesn't know which policy is "current" — only the prompt can use the `Status: Superseded` / `Status: Current` language already written into the documents.
5. Re-run the same question, confirm 8 is now the reliable answer, and re-run the full eval.

### Full code

`app/rag.py` — rerank + recency rule:
```python
import os

from langchain_cohere import CohereRerank
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from .utils import get_vector_store

SYSTEM = """You are a grounded company knowledge assistant for Fernwood Labs.
Answer strictly from the provided context. If the answer isn't in the context,
reply with exactly: "I don't know."

If multiple context chunks describe the same policy with different values,
prefer the chunk marked "Status: Current" or with the most recent effective
date, and ignore any chunk marked "Status: Superseded". Say which policy
version you used if there's any ambiguity.

Be concise.
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        ("user", "Question:\n{input}\n\nContext:\n{context}"),
    ]
)


async def build_chain(category: str | None = None):
    store = await get_vector_store()
    search_kwargs = {"k": 10}
    if category:
        search_kwargs["filter"] = {"category": category}
    base_retriever = store.as_retriever(search_kwargs=search_kwargs)
    compressor = CohereRerank(model="rerank-v3.5", top_n=3)
    retriever = ContextualCompressionRetriever(base_retriever=base_retriever, base_compressor=compressor)

    llm = ChatOpenAI(model="gpt-4o-mini")
    doc_chain = create_stuff_documents_chain(llm, PROMPT)
    return create_retrieval_chain(retriever, doc_chain)


async def answer(question: str, category: str | None = None):
    chain = await build_chain(category)
    result = await chain.ainvoke({"input": question})
    sources = sorted({d.metadata.get("source") for d in result["context"] if d.metadata.get("source")})
    contexts = [d.page_content for d in result["context"]]
    return result["answer"], sources, contexts
```

Note: `search_kwargs={"k": 10}` here intentionally overrides Module 7's tuned value — retrieve a wider net, then let the reranker narrow it to the best 3. This is a deliberate two-stage retrieval design, worth saying out loud.

### Ask the learner

- *"Why isn't reranking alone enough to fix the recency bug?"* **Hint ladder:** (1) "does `CohereRerank` know anything about calendar dates or which document supersedes which?" → (2) "what is it actually scoring chunks on?" → (3) it scores relevance to the *question*, not recency or correctness — both PTO chunks are highly relevant to a PTO question; only the prompt, reading the `Status:` language already present in the documents, can resolve which one is authoritative.
- *"The documents already said 'Status: Superseded' before this module even started. Why didn't that help on its own?"* **Hint ladder:** (1) "did the Module 3 prompt ever instruct the model to look for or act on that specific word?" → (2) "is text *present* in the context the same as text the model has been told matters?" → (3) the information was always retrievable; nothing told the model it was decision-relevant until this module's prompt rule.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `CohereRerank` raises an auth error | `CO_API_KEY` missing from `.env` or not loaded | Confirm `.env` has a real Cohere key and `load_dotenv()` runs before the client is constructed |
| Recency bug doesn't reproduce on the first try | Vector similarity ranking between the two PTO chunks isn't perfectly deterministic across runs | Try 2–3 times, or temporarily set `k=2` to force both PTO chunks into a tiny context where the ambiguity is unavoidable, to make the demo reliable |
| Fixed prompt still occasionally answers 5 | Both chunks' `Status:` lines got truncated by a chunk boundary (interacts with Module 6's chunk size choice) | Check `contexts` in the response — if the `Status:` line is missing from a chunk, that's a chunking problem, not a prompting one |

### Quiz + checkpoint

1. In one sentence: why is a two-stage "retrieve wide, then rerank narrow" design better than just setting `k=3` directly?
   <details><summary>Answer</summary>Pure vector similarity at a small <code>k</code> risks missing the best chunk if it's ranked 4th or 5th by embedding distance alone; retrieving a wider pool and then reranking with a model specifically trained to judge relevance gets a better top-3 than vector similarity alone would have picked.</details>
2. What specifically closed the recency bug — the reranker, the prompt, or both? Defend your answer.
   <details><summary>Answer</summary>Both, but for different reasons: the reranker ensures the most relevant PTO chunks actually make it into the context at all; the prompt rule is what lets the model correctly choose between them once both are present. Removing either one re-opens a path to the wrong answer.</details>

**Checkpoint:** the PTO carryover question reliably answers 8, every time, across several repeated runs; learner can explain why the fix needed two parts.

### Scoreboard entry

Expect `context_precision` to jump the most. Record before/after in `SCOREBOARD.md`; note the recency fix separately, since it's a correctness fix the aggregate RAGAS numbers may or may not fully capture (the judge LLM may already treat superseded-policy answers as "close enough" — call this out as a real limitation of automated scoring, not swept under the rug).

---

## Module 10 — Hybrid Search

### Why this module

> **Ask the learner:** "Ask this assistant about 'WireGuard' or 'Jamf' — exact proper nouns, not concepts. Does pure vector similarity actually excel at exact keyword matches, or does it sometimes blur them with 'similar-sounding' content?"

### Learning objectives

- Learner can combine Postgres full-text search with vector similarity using Reciprocal Rank Fusion (RRF).
- Learner understands when it's appropriate to drop below an ORM/vector-store abstraction to raw SQL.

### Step-by-step build

1. Add dependencies:
   ```bash
   uv add pgvector
   ```
2. Extend `init-db/init.sql` with a generated `tsvector` column and a GIN index, then recreate the volume and re-ingest:
   ```sql
   ALTER TABLE fernwood_chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector
       GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
   CREATE INDEX IF NOT EXISTS fernwood_chunks_tsv_idx ON fernwood_chunks USING GIN (content_tsv);
   ```
3. Create `app/hybrid.py` — a raw-SQL hybrid search function fusing vector rank and text rank with RRF.
4. Wire a new `/ask/hybrid` endpoint (kept separate from `/ask` so you can compare both side by side) that uses it instead of the pure-vector retriever.
5. Test the exact-keyword golden questions (`q10` "WireGuard", `q12` "Jamf", `q13` "Okta") against both endpoints and compare.

### Full code

`app/hybrid.py`:
```python
import os

import psycopg
from pgvector.psycopg import register_vector

from .utils import embeddings


async def hybrid_search(question: str, k: int = 5):
    query_vector = embeddings.embed_query(question)
    async with await psycopg.AsyncConnection.connect(os.getenv("DATABASE_URL")) as conn:
        await register_vector(conn)
        async with conn.cursor() as cur:
            await cur.execute(
                """
                WITH vector_ranked AS (
                    SELECT langchain_id, content, langchain_metadata,
                           row_number() OVER (ORDER BY embedding <=> %(qvec)s) AS rank
                    FROM fernwood_chunks
                    ORDER BY embedding <=> %(qvec)s
                    LIMIT 20
                ),
                text_ranked AS (
                    SELECT langchain_id, content, langchain_metadata,
                           row_number() OVER (
                               ORDER BY ts_rank(content_tsv, websearch_to_tsquery('english', %(question)s)) DESC
                           ) AS rank
                    FROM fernwood_chunks
                    WHERE content_tsv @@ websearch_to_tsquery('english', %(question)s)
                    LIMIT 20
                )
                SELECT
                    COALESCE(v.langchain_id, t.langchain_id) AS id,
                    COALESCE(v.content, t.content) AS content,
                    COALESCE(v.langchain_metadata, t.langchain_metadata) AS metadata,
                    (1.0 / (60 + COALESCE(v.rank, 1000))) + (1.0 / (60 + COALESCE(t.rank, 1000))) AS score
                FROM vector_ranked v
                FULL OUTER JOIN text_ranked t ON v.langchain_id = t.langchain_id
                ORDER BY score DESC
                LIMIT %(k)s;
                """,
                {"qvec": query_vector, "question": question, "k": k},
            )
            rows = await cur.fetchall()
    return rows
```

`app/api.py` — add the comparison endpoint:
```python
from .hybrid import hybrid_search


@app.post("/ask/hybrid")
async def ask_hybrid(payload: Ask):
    rows = await hybrid_search(payload.question, k=5)
    context = "\n\n".join(row[1] for row in rows)
    sources = sorted({row[2].get("source") for row in rows if row[2].get("source")})
    return {"context_preview": context[:800], "sources": sources}
```

### Ask the learner

- *"What does `1.0 / (60 + rank)` actually do, and why `60`?"* **Hint ladder:** (1) "if `rank` is 1 (the best match), what's the score? If `rank` is 20 (barely made the cutoff), what's the score?" → (2) "why might you not want rank 1 vs. rank 2 to make a huge difference, but rank 1 vs. rank 20 to make a big one?" → (3) this is Reciprocal Rank Fusion — it combines two different ranking systems (vector distance, text relevance) into one comparable score using only *rank position*, not the raw incomparable scores from each system; `60` is a conventional smoothing constant from the original RRF paper, not a value you need to derive yourself.
- *"Why raw SQL here instead of another LangChain abstraction?"* **Hint ladder:** (1) "does `AsyncPGVectorStore` know how to combine a `tsvector` query with a vector query in one ranked result?" → (2) "when a library's abstraction doesn't cover what you need, what are your choices?" → (3) sometimes the right call is to drop to the underlying tool (SQL, here) rather than contort an abstraction — recognizing *when* to do that is itself a skill.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `operator does not exist: vector <=> numeric[]` | `register_vector(conn)` not called, so the Python list isn't adapted to the `vector` type | Confirm `await register_vector(conn)` runs before the query on that connection |
| `content_tsv` column empty for documents ingested before this module | `GENERATED ALWAYS AS ... STORED` only computes on insert; existing rows predate the column | Recreate the volume and re-ingest — same gotcha as every schema change so far |

### Quiz + checkpoint

1. For the "Jamf" question specifically, would you predict pure vector search or hybrid search to do better, and why?
   <details><summary>Answer</summary>Hybrid, likely — "Jamf" is a specific proper noun with no real semantic neighbors; full-text search matches it exactly, while vector similarity has to rely on surrounding context words to recognize relevance, which is a weaker signal for this kind of exact-term lookup.</details>

**Checkpoint:** `/ask/hybrid` returns sensible results for at least one exact-keyword golden question where it visibly differs from `/ask`'s pure-vector retrieval.

### Scoreboard entry

Add a hybrid-vs-pure-vector comparison specifically on the keyword-heavy questions (q10, q12, q13) — not necessarily a full RAGAS re-run, since `/ask/hybrid` doesn't go through the LLM answer stage yet in this minimal form.

---

## Module 11 — Multi-Turn

### Why this module

> **Ask the learner:** "Part 1 Module 8 built a history-aware retriever over `demo_notes.txt`. Does any of that exist in this FastAPI service yet?"

### Learning objectives

- Learner can port the Part 1 history-aware pattern into a real API with session-scoped memory.

### Step-by-step build

1. Add a `session_id` field to the request model.
2. Maintain an in-memory `dict[str, ChatMessageHistory]` keyed by `session_id` (explicitly note: in-memory means it's lost on restart and doesn't scale past one server process — acceptable for this course, not for production; Redis-backed history is the natural next step, left as an exercise).
3. Build the same two-prompt pattern as Part 1 Module 8 — a history-aware rewriter with no `{context}`, and an answering prompt with `{context}` and `MessagesPlaceholder`.
4. Wire `RunnableWithMessageHistory` into `/ask`.

### Full code

`app/rag.py` — add history awareness:
```python
from langchain_core.prompts import MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

_session_histories: dict[str, ChatMessageHistory] = {}


def _get_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _session_histories:
        _session_histories[session_id] = ChatMessageHistory()
    return _session_histories[session_id]


CONTEXTUALIZE_PROMPT = ChatPromptTemplate.from_messages(
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

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        MessagesPlaceholder("chat_history"),
        ("user", "Question:\n{input}\n\nContext:\n{context}"),
    ]
)


async def build_chat_chain(category: str | None = None):
    store = await get_vector_store()
    search_kwargs = {"k": 10}
    if category:
        search_kwargs["filter"] = {"category": category}
    base_retriever = store.as_retriever(search_kwargs=search_kwargs)
    compressor = CohereRerank(model="rerank-v3.5", top_n=3)
    retriever = ContextualCompressionRetriever(base_retriever=base_retriever, base_compressor=compressor)

    llm = ChatOpenAI(model="gpt-4o-mini")
    history_aware_retriever = create_history_aware_retriever(llm, retriever, CONTEXTUALIZE_PROMPT)
    doc_chain = create_stuff_documents_chain(llm, QA_PROMPT)
    rag_chain = create_retrieval_chain(history_aware_retriever, doc_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        _get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


async def answer_with_history(question: str, session_id: str, category: str | None = None):
    chain = await build_chat_chain(category)
    result = await chain.ainvoke(
        {"input": question},
        {"configurable": {"session_id": session_id}},
    )
    sources = sorted({d.metadata.get("source") for d in result["context"] if d.metadata.get("source")})
    contexts = [d.page_content for d in result["context"]]
    return result["answer"], sources, contexts
```

`app/api.py`:
```python
class Ask(BaseModel):
    question: str
    category: str | None = None
    session_id: str = "default"


@app.post("/ask")
async def ask(payload: Ask):
    if payload.category is not None and payload.category not in KNOWN_CATEGORIES:
        return {"error": f"Unknown category '{payload.category}'. Choose from: {sorted(KNOWN_CATEGORIES)}"}
    answer_text, sources, contexts = await answer_with_history(
        payload.question, payload.session_id, category=payload.category
    )
    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

### Ask the learner

- *"Why key the history dict by `session_id` instead of just one global history?"* Same question as Part 1 Module 4 — if the learner remembers, let them answer it themselves this time. **Hint ladder:** (1) "if two different people ask questions at the same time, what should happen?" → (2) "would a single shared history make sense for a multi-user service?" → (3) confirm: each caller's conversation needs to stay isolated.
- *"What happens to every session's history if the server restarts?"* **Hint ladder:** (1) "where does `_session_histories` actually live?" → (2) "is that durable?" → (3) it's gone — exactly the same limitation Part 1 Module 4 had, now at the scale of a whole service instead of one script. Name this as a known, accepted limitation, not a secretly broken feature.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Follow-up question seems to ignore history | Testing with a different `session_id` each time (e.g. the default `"default"` string vs. a typo) | Confirm the exact same `session_id` is sent on every call in the test sequence |
| `KeyError: 'answer'` | `output_messages_key="answer"` dropped during the port from Part 1 | Re-check against Part 1 Module 8's working version |

### Quiz + checkpoint

1. What's the one new parameter in the request model that Part 1 never needed, and why does a real API need it where a single-user script didn't?
   <details><summary>Answer</summary><code>session_id</code> — a single-user terminal script has an implicit "session" (the one process running), but a service handling multiple simultaneous callers needs an explicit way to know whose conversation is whose.</details>

**Checkpoint:** a two-turn conversation with a pronoun-dependent follow-up resolves correctly through the live API, using the same `session_id` both times.

### Scoreboard entry

Not a golden-set accuracy change — add 2–3 multi-turn questions to a small side test file and note pass/fail there instead of forcing them into the single-turn golden set.

---

## Module 12 — Caching, and the Collision Bug

### Why this module

> **Ask the learner:** "If two different questions produce embeddings that are very similar, should they get the same cached answer? What could go wrong if the similarity bar for 'close enough' is set too loose?"

### Learning objectives

- Learner can add a semantic cache and understands the tradeoff its threshold controls.
- Learner can observe, firsthand, a cache returning a wrong answer for a different question — and fix it by tightening, not removing, the cache.

### Step-by-step build

1. Add dependencies:
   ```bash
   uv add langchain-redis redis
   ```
2. Wire `RedisSemanticCache` with a **deliberately loose** threshold first.
3. Ask two genuinely different questions back to back and watch the second one return the first one's cached answer.
4. Tighten the threshold, re-test with the same pair (should no longer collide) and with two paraphrases of the *same* question (should still correctly share a cached answer).

### Full code

`app/utils.py` — add the cache, loose on purpose first:
```python
from langchain_core.globals import set_llm_cache
from langchain_redis import RedisSemanticCache

REDIS_URL = os.getenv("REDIS_URL")

# RedisSemanticCache's constructor eagerly calls embeddings.embed_query() just
# to determine vector dimensions -- so a missing Redis instance, or an invalid
# API key, would otherwise crash the whole app at import time, not just on a
# request. Degrade gracefully instead: no cache beats no app.
try:
    set_llm_cache(
        RedisSemanticCache(
            redis_url=REDIS_URL,
            embeddings=embeddings,
            distance_threshold=0.8,  # PLANTED BUG: far too loose, see below
        )
    )
except Exception as e:
    print(f"WARNING: semantic cache disabled ({e})")
```

This `try/except` is itself worth pointing out: it's exactly the pattern `shopwise` used around its own cache setup, and exactly what `company-knowledge-assistant`'s unconditional `set_llm_cache` call got wrong — the whole app should not go down just because Redis or a key is temporarily unavailable.

Demonstrate the collision:
```bash
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "What is the current annual equipment stipend for remote employees?"}'

curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "What is the domestic per diem rate for meals while traveling?"}'
```
If the threshold is loose enough, the second call returns the first question's cached answer about the equipment stipend — a visibly, confidently wrong response to a completely different question.

Fix — tighten it, and verify empirically rather than guessing a magic number (keep the same `try/except` around it):
```python
set_llm_cache(
    RedisSemanticCache(
        redis_url=REDIS_URL,
        embeddings=embeddings,
        distance_threshold=0.1,  # start tight; loosen only if true paraphrases start missing
    )
)
```

Re-test with the same unrelated pair (should now get two distinct, correct answers), then test two paraphrases of one question:
```bash
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question": "How much is the remote equipment stipend these days?"}'
```
(immediately after asking the original stipend question) — this *should* hit the cache, since it's the same question reworded.

### Ask the learner

- *"What does `distance_threshold` actually measure?"* **Hint ladder:** (1) "is it a similarity score (higher = more alike) or a distance (lower = more alike)?" → (2) "if two questions' embeddings have a distance of 0.05, are they nearly identical or nearly opposite?" → (3) it's a distance — a *lower* threshold means only very close matches are treated as cache hits; `0.8` was so loose that most same-domain business questions ended up "close enough."
- *"Once you fixed it, how did you know `0.1` was right, rather than just a different wrong guess?"* **Hint ladder:** (1) "did you test both a true paraphrase and two genuinely different questions?" → (2) "what would you watch for if `0.1` turns out too tight?" → (3) land on: this is an empirical tuning exercise, not a lookup — too tight means paraphrases stop sharing a cache entry (lower cache hit rate, more cost, but never a wrong answer); too loose risks exactly today's bug. Tight-and-missing-some-hits is the safer direction to err toward.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Cache never seems to hit at all after the fix | Threshold now too tight for this embedding model's actual distance distribution | Loosen gradually while testing only with true paraphrases, never with genuinely different questions |
| Collision doesn't reproduce with this exact question pair | Embedding distances aren't perfectly predictable; try a different pair of same-domain, different-topic questions from the golden set | Any two questions sharing a lot of business-FAQ vocabulary are good candidates |
| The server won't even start after adding this code — fails immediately, before any request | `RedisSemanticCache.__init__` eagerly calls `embeddings.embed_query("test")` to size its vector store, so a missing Redis instance or an invalid key fails at import time | Confirm the `try/except` is in place; a printed `WARNING: semantic cache disabled (...)` at startup, with the server otherwise running, is the correct degraded behavior |

### Quiz + checkpoint

1. Why is "the cache misses more often than it should" a safer failure mode to tune toward than "the cache sometimes returns a wrong answer"?
   <details><summary>Answer</summary>A cache miss costs an extra (correct) LLM call — slower and slightly more expensive, but never wrong. A false cache hit silently returns a plausible-looking wrong answer to the user, with no indication anything went wrong — a much worse failure to ship.</details>

**Checkpoint:** the same unrelated question pair now reliably returns two distinct, correct answers; a true paraphrase reliably still hits the cache.

### Scoreboard entry

Record latency/cost-per-query for a repeated question (cache hit) vs. a novel one (cache miss) — not an accuracy row.

---

## Module 13 — Idempotent Re-Ingest

### Why this module

> **Ask the learner:** "Module 2 flagged this and moved on: what happens if you run `/ingest` twice?"

### Learning objectives

- Learner can make ingestion idempotent per source file using content hashing and delete-by-source.
- Learner can trace a *specific* scoreboard regression back to a duplicate-data root cause, using a named golden question.

### Step-by-step build

1. **Before fixing anything**, run `/ingest` twice in a row (on the already-fixed, already-tuned pipeline from Module 11) and compare row counts.
2. Specifically re-ask `q17` ("What is the current annual home-office equipment stipend...?") after the double-ingest and see whether it's reverted to the stale $500 figure — duplicate copies of `faqs/remote-work-faq.md`'s chunk can crowd out the single `announcements/2025-01-benefits-update.md` chunk from the reranked top-3.
3. Fix: hash each source file's content; before adding a file's chunks, delete any existing rows for that same source path, so re-ingestion always reflects the current file contents exactly once.
4. Re-run `/ingest` twice again, confirm row counts are now stable and `q17` answers correctly both times.

### Full code

`app/ingest.py` — add hashing and delete-by-source:
```python
import asyncio
import glob
import hashlib
import os
import traceback

import psycopg
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .utils import get_vector_store

DATA_DIR = os.getenv("DATA_DIR", "data")

LOADERS = {
    ".md": UnstructuredMarkdownLoader,
    ".pdf": PyMuPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".txt": TextLoader,
}


def _file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _load_docs(base: str = DATA_DIR):
    docs = []
    for path in glob.glob(os.path.join(base, "**", "*"), recursive=True):
        if os.path.isdir(path) or os.path.basename(path).startswith("."):
            continue
        ext = os.path.splitext(path)[1].lower()
        loader_cls = LOADERS.get(ext)
        if loader_cls is None:
            continue
        category = os.path.relpath(path, base).split(os.sep)[0]
        content_hash = _file_hash(path)
        try:
            for doc in loader_cls(path).load():
                doc.metadata["category"] = category
                doc.metadata["content_hash"] = content_hash
                docs.append(doc)
        except Exception:
            print(f"INGEST ERROR: failed to load {path}")
            traceback.print_exc()
    return docs


def _chunk(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    return splitter.split_documents(docs)


async def _delete_existing_sources(sources: set[str]):
    if not sources:
        return
    async with await psycopg.AsyncConnection.connect(os.getenv("DATABASE_URL")) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM fernwood_chunks WHERE langchain_metadata->>'source' = ANY(%s)",
                (list(sources),),
            )
        await conn.commit()


async def run_ingest():
    docs = _load_docs()
    chunks = _chunk(docs)

    sources = {d.metadata.get("source") for d in chunks if d.metadata.get("source")}
    await _delete_existing_sources(sources)

    store = await get_vector_store()
    await store.aadd_documents(chunks)
    print(f"Ingested {len(docs)} documents, {len(chunks)} chunks (old versions of these sources removed first).")
    return {"documents": len(docs), "chunks": len(chunks)}


if __name__ == "__main__":
    asyncio.run(run_ingest())
```

Verify idempotency:
```bash
curl -s -X POST localhost:8000/ingest
curl -s localhost:8000/ingest/status
docker compose exec postgres psql -U postgres -c "SELECT count(*) FROM fernwood_chunks;"
curl -s -X POST localhost:8000/ingest
curl -s localhost:8000/ingest/status
docker compose exec postgres psql -U postgres -c "SELECT count(*) FROM fernwood_chunks;"
# row count should be identical after both runs
```

### Ask the learner

- *"Why delete by `source` path rather than by `content_hash`?"* **Hint ladder:** (1) "if a file's *content* changes but its *path* doesn't, which key still correctly identifies 'the current version of this file'?" → (2) "if you keyed on hash instead, what would happen to the old chunks of an edited file?" → (3) `source` identifies "this specific file, whatever its current content is" — exactly the unit you want to fully replace on every re-ingest; `content_hash` is still useful (stored for provenance / future "skip unchanged files" optimization) but isn't the right delete key.
- *"Walk through exactly why `q17` reverted to $500 after the double-ingest — don't just say 'duplicates are bad,' trace the actual mechanism."* **Hint ladder:** (1) "how many copies of the `remote-work-faq.md` chunk exist in the database after a double-ingest?" → (2) "the reranker keeps the top 3 by relevance — if 2 of those 3 slots are now occupied by duplicate copies of the *same* $500 chunk, what got pushed out?" → (3) the single chunk from `2025-01-benefits-update.md` (the $600 update) — crowded out by sheer duplicate volume of an equally-relevant but stale chunk, not because it became less relevant.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ANY(%s)` SQL syntax error | Passed a Python `set` directly instead of a `list` | psycopg needs a list/tuple for `ANY`, not a raw set — convert with `list(sources)` |
| Row count still grows on repeated ingest | `_delete_existing_sources` running against a different `DATABASE_URL` than the one the data was written with (e.g. stale `.env` in a second terminal) | Confirm both ingestion and the delete step share the same environment |

### Quiz + checkpoint

1. If you added a *new* file to `data/policies/` and ran `/ingest` again, what would happen to the existing files' chunks?
   <details><summary>Answer</summary>Nothing — <code>_delete_existing_sources</code> only deletes rows whose <code>source</code> matches a file being re-ingested in *this* run; since every file gets reloaded and rehashed every run in this simple version, every file's old chunks get replaced by fresh ones, and the new file's chunks are simply added since there's nothing to delete for a source that didn't exist before.</details>
2. Name one thing this fix does *not* yet solve, that a production system would need.
   <details><summary>Answer</summary>Any reasonable answer naming a real gap counts — e.g.: it still re-embeds every file on every ingest run (no "skip if `content_hash` unchanged" optimization, even though the hash is already being stored for exactly that purpose); it doesn't handle a file being *deleted* from <code>data/</code> (its old chunks would linger forever, since nothing triggers their removal).</details>

**Checkpoint:** two consecutive `/ingest` calls produce an identical row count; `q17` answers correctly ($600) after both.

### Scoreboard entry

Record the `q17`-specific regression-and-recovery explicitly: wrong ($500) after double-ingest pre-fix, correct ($600) and stable after the fix — a concrete, named example beats an aggregate number here.

---

## Module 14 — Citations and Streaming

### Why this module

> **Ask the learner:** "`sources` right now is just a list of filenames. If a policy question's answer is wrong, how would anyone actually check it against the source?"

### Learning objectives

- Learner can return quote-level citations, not just filenames.
- Learner can stream a response token by token instead of making the user wait for the whole answer.

### Step-by-step build

1. Change the `sources` field to include a short snippet of the actual matching text, not just the filename — applied to `answer_with_history`, the multi-turn chain from Module 11, not an earlier single-turn one.
2. Add a `POST /ask/stream` endpoint. **Deliberately single-turn, no reranking** — streaming through a `RunnableWithMessageHistory`-wrapped chain's `astream_events` correctly is a genuinely harder problem (filtering the right events while history still gets recorded) than this course needs to solve; a simpler, directly-verifiable manual retrieve-then-stream path is the honest choice here. Note this limitation out loud rather than quietly shipping a regression — "streaming + multi-turn + reranking, all three at once" is a good stretch exercise, not a course requirement.

### Full code

`app/rag.py` — richer citations, on top of Module 11's history-aware chain:
```python
async def answer_with_history(question: str, session_id: str, category: str | None = None):
    chain = await build_chat_chain(category)
    result = await chain.ainvoke(
        {"input": question},
        {"configurable": {"session_id": session_id}},
    )
    citations = []
    seen_sources = set()
    for d in result["context"]:
        source = d.metadata.get("source")
        if source and source not in seen_sources:
            seen_sources.add(source)
            citations.append({"source": source, "snippet": d.page_content[:160].strip() + "..."})
    contexts = [d.page_content for d in result["context"]]
    return result["answer"], citations, contexts
```

`app/api.py` — streaming endpoint (single-turn, no rerank, by design — see above):
```python
import os

from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI

from .rag import PROMPT
from .utils import get_vector_store


@app.post("/ask/stream")
async def ask_stream(payload: Ask):
    store = await get_vector_store()
    search_kwargs = {"k": int(os.getenv("RETRIEVAL_K", "5"))}
    if payload.category:
        search_kwargs["filter"] = {"category": payload.category}
    retriever = store.as_retriever(search_kwargs=search_kwargs)
    docs = await retriever.ainvoke(payload.question)
    context = "\n\n".join(d.page_content for d in docs)
    messages = PROMPT.format_messages(input=payload.question, context=context)
    llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

    async def token_stream():
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(token_stream(), media_type="text/plain")
```

Test streaming:
```bash
curl -N -X POST localhost:8000/ask/stream -H "Content-Type: application/json" \
  -d '{"question": "What travel booking platform do employees use?"}'
```
(`-N` disables curl's output buffering so you see tokens arrive incrementally, not all at once.)

### Ask the learner

- *"Why does `/ask/stream` retrieve manually instead of reusing `create_retrieval_chain` like everything else?"* **Hint ladder:** (1) "if you called `.astream()` on the full retrieval chain, what would actually come out token by token — just the answer, or the whole chain's internal structure too?" → (2) "would you need to filter that stream to find just the answer tokens?" → (3) `create_retrieval_chain` bundles retrieval and generation into one object whose streaming output mixes both; retrieving manually first, then calling `llm.astream()` on just the final prompt, sidesteps needing to filter anything — the tradeoff is giving up this endpoint's history-awareness and reranking, which is why it's flagged as a known simplification, not a final design.
- *"Would the citation snippet change if Module 6's chunk size changed?"* **Hint ladder:** (1) "what's `d.page_content[:160]` actually slicing?" → (2) "if chunks were twice as long, would the first 160 characters of a chunk still reliably contain the relevant sentence?" → (3) not necessarily — a cruder "first N characters" snippet is a simplification worth naming as one; a better version would locate the most relevant *sentence* within the chunk, not just truncate from the start (a good stretch exercise).
- *"Would the citation snippet change if Module 6's chunk size changed?"* **Hint ladder:** (1) "what's `d.page_content[:160]` actually slicing?" → (2) "if chunks were twice as long, would the first 160 characters of a chunk still reliably contain the relevant sentence?" → (3) not necessarily — a cruder "first N characters" snippet is a simplification worth naming as one; a better version would locate the most relevant *sentence* within the chunk, not just truncate from the start (a good stretch exercise).

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `curl` shows the whole answer at once anyway | Output still buffered somewhere (missing `-N`, or a proxy/terminal buffering) | Use `curl -N`; test directly against `localhost`, not through an intermediate proxy |
| Streaming endpoint returns the answer with no category filter applied | `payload.category` validated in `/ask` but that check wasn't copied into `/ask/stream` | Add the same `KNOWN_CATEGORIES` check here, or factor it into a shared helper |

### Quiz + checkpoint

1. What's the practical difference, from a user's perspective, between `/ask` and `/ask/stream`?
   <details><summary>Answer</summary><code>/ask</code> makes the caller wait for the entire answer to finish generating before anything is returned; <code>/ask/stream</code> returns the first tokens as soon as the model produces them, so a UI can render the answer incrementally, which feels dramatically faster for long answers even though total generation time is the same.</details>

**Checkpoint:** a streamed response visibly arrives in pieces via `curl -N`; citations now include a readable snippet, not just a bare filename.

### Scoreboard entry

Not an accuracy change — note citation quality as a qualitative spot-check (are the snippets actually the relevant sentence?) rather than a RAGAS number.

---

## Module 15 — Observability

### Why this module

> **Ask the learner:** "If a user says 'the assistant gave me a weird answer yesterday at 3pm,' what do you currently have to go investigate that?"

Nothing — there's no trace, no log, no cost record. That's the gap this module closes.

### Learning objectives

- Learner can enable LangSmith tracing for every chain run.
- Learner can log latency and approximate token cost per request.

### Step-by-step build

1. Add LangSmith env vars to `.env` (requires a free LangSmith account):
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-key-here
   LANGCHAIN_PROJECT=fernwood-labs-assistant
   ```
2. Re-run any `/ask` call and open the LangSmith dashboard — find the trace, click into the retrieval step and the LLM step separately.
3. Add simple per-request timing and token-usage logging in `app/api.py`.

### Full code

`app/api.py` — timing and usage logging:
```python
import time


@app.post("/ask")
async def ask(payload: Ask):
    if payload.category is not None and payload.category not in KNOWN_CATEGORIES:
        return {"error": f"Unknown category '{payload.category}'. Choose from: {sorted(KNOWN_CATEGORIES)}"}

    start = time.perf_counter()
    answer_text, sources, contexts = await answer_with_history(
        payload.question, payload.session_id, category=payload.category
    )
    elapsed = time.perf_counter() - start
    print(f"[timing] /ask took {elapsed:.2f}s for question: {payload.question[:60]!r}")

    return {"answer": answer_text, "sources": sources, "contexts": contexts}
```

Token usage (inspect what the LLM actually reports, rather than guessing):
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("test")
print(response.usage_metadata)
# {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}
```

### Ask the learner

- *"Open a trace in LangSmith for a reranked, multi-turn question. How many distinct steps does it show?"* Let them actually count — history rewriting, retrieval, reranking, document stuffing, final generation. **Hint ladder:** (1) "is this the same number of steps you'd have guessed, just reading the Python code?" → (2) "which step took the longest?" → (3) tracing makes the chain's real internal shape visible in a way reading source code alone doesn't — especially useful once a bug report comes in days later and the exact inputs need to be reconstructed.
- *"Why log token usage at all, if OpenAI already shows a usage dashboard?"* **Hint ladder:** (1) "does OpenAI's dashboard tell you *which specific user question* was expensive?" → (2) "what would you need to answer 'why did our bill spike last Tuesday'?" → (3) per-request, per-question logs let you correlate cost with specific behavior (a particular question pattern, a particular category, a reranking call) — the provider's aggregate dashboard can't do that.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| No traces appear in LangSmith | `LANGCHAIN_TRACING_V2` not actually loaded (missing `load_dotenv()` somewhere, or set after the chain modules were already imported) | Confirm env vars are set *before* any LangChain imports happen — set them at the very top of `app/api.py` or in the shell environment, not deep inside a function |
| `usage_metadata` is `None` | Some model/provider combinations don't populate it the same way, or streaming responses need usage requested explicitly | Check against a plain non-streaming `.invoke()` call first to confirm the baseline works |

### Quiz + checkpoint

1. What's one question a LangSmith trace can answer that your own `print()` statements can't, without a lot of extra manual work?
   <details><summary>Answer</summary>Any reasonable answer: e.g. exactly what prompt text (with all variables filled in) was actually sent to the model at each step, including the rewritten standalone question from the history-aware retriever — reconstructing that from scattered print statements across multiple files is far more effort than reading one trace.</details>

**Checkpoint:** a real trace is visible in the LangSmith dashboard for a request made during this session; per-request timing is visible in the server logs.

### Scoreboard entry

Add a cost/latency note to `SCOREBOARD.md`, separate from the accuracy columns — this module is about visibility, not accuracy.

---

## Module 16 — UI Polish

### Why this module

> **Ask the learner:** "Would you hand `curl` commands to a non-technical coworker at Fernwood Labs and ask them to test this?"

### Learning objectives

- Learner can serve a minimal dependency-free chat UI from the same FastAPI app.

### Step-by-step build

1. Create `app/static/index.html` — a plain HTML/JS chat page with an "Ingest Data" button and status pill, calling the existing `/ingest`, `/ingest/status`, and `/ask` endpoints.
2. Mount it as static files in `app/api.py`.

### Full code

`app/static/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Fernwood Labs Knowledge Assistant</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; }
    textarea, input { width: 100%; box-sizing: border-box; padding: .5rem; }
    button { padding: .5rem 1rem; margin-top: .5rem; }
    .answer { white-space: pre-wrap; background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
    .pill { padding: .2rem .6rem; border-radius: 999px; font-size: .8rem; }
    .pill-idle { background: #e5e7eb; }
    .pill-running { background: #fde68a; }
    .pill-succeeded { background: #bbf7d0; }
    .pill-failed { background: #fecaca; }
  </style>
</head>
<body>
  <h1>Fernwood Labs Knowledge Assistant</h1>
  <p>
    <span id="ingestStatus" class="pill pill-idle">idle</span>
    <button id="ingestBtn">Ingest Data</button>
  </p>
  <textarea id="question" rows="3" placeholder="Ask a question about Fernwood Labs..."></textarea>
  <button id="askBtn">Ask</button>
  <div id="answer" class="answer" style="display:none;"></div>

  <script>
    const ingestBtn = document.getElementById("ingestBtn");
    const ingestStatus = document.getElementById("ingestStatus");
    const askBtn = document.getElementById("askBtn");
    const questionEl = document.getElementById("question");
    const answerEl = document.getElementById("answer");

    async function pollIngestStatus() {
      const res = await fetch("/ingest/status");
      const data = await res.json();
      ingestStatus.textContent = data.status;
      ingestStatus.className = "pill pill-" + data.status;
      if (data.status === "running") setTimeout(pollIngestStatus, 1500);
    }

    ingestBtn.addEventListener("click", async () => {
      await fetch("/ingest", { method: "POST" });
      pollIngestStatus();
    });

    askBtn.addEventListener("click", async () => {
      const question = questionEl.value.trim();
      if (!question) return;
      answerEl.style.display = "block";
      answerEl.textContent = "Thinking...";
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      answerEl.textContent = data.answer + "\n\nSources: " + JSON.stringify(data.sources, null, 2);
    });

    pollIngestStatus();
  </script>
</body>
</html>
```

`app/api.py` — mount static files and serve the page:
```python
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root_page():
    return FileResponse(static_dir / "index.html")
```

### Ask the learner

- *"This page polls `/ingest/status` every 1.5 seconds while ingestion is running. What would happen without that polling loop?"* **Hint ladder:** (1) "ingestion for the full corpus might take tens of seconds — does the browser wait for one long request, or ask repeatedly?" → (2) "which approach lets the user see progress rather than a frozen page?" → (3) polling a status endpoint is a simple, robust pattern for long-running background work — the alternative (one giant blocking request) would time out or just look frozen.

### Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `404` on `/static/...` | `static_dir` path doesn't match where `index.html` actually lives | Confirm `app/static/index.html` exists relative to `app/api.py`'s own file location |
| Page loads but buttons do nothing | Browser console has a JS error (often a typo in an element id) | Open browser dev tools and check the console before assuming the backend is at fault |

### Quiz + checkpoint

1. Why does this module intentionally avoid a frontend framework?
   <details><summary>Answer</summary>A dependency-free static page keeps the course focused on the backend/RAG concepts being taught — introducing a frontend build toolchain here would be a distraction from this course's actual subject matter, not a necessary part of it.</details>

**Checkpoint:** a non-technical user could open this page, click "Ingest Data," wait for the status pill to turn green, and ask a real question — with no terminal involved.

---

## Module 17 — Capstone

### Why this module

> **Ask the learner:** "Pick a direction: make the assistant smarter about *when it's wrong* (corrective RAG), or make it incapable of ever stating a number it didn't look up in a system of record (structured hydration). Which failure mode worries you more for a real company deployment?"

This module is intentionally more open than the rest — guide, don't hand over a finished solution.

### Option A — LangGraph Corrective RAG

**Idea:** after retrieval, have a small grading step judge whether the retrieved context actually looks sufficient to answer the question. If not, rewrite the query and retrieve again (once), before falling back to "I don't know."

```bash
uv add langgraph
```

Skeleton to build out together, not a finished solution:
```python
from typing import TypedDict

from langgraph.graph import END, StateGraph


class RagState(TypedDict):
    question: str
    context: list
    answer: str
    retry_count: int


async def retrieve_node(state: RagState) -> RagState:
    # reuse the Module 9 retriever
    ...


async def grade_node(state: RagState) -> RagState:
    # ask a small, cheap LLM call: "is this context sufficient to answer
    # the question? yes/no" -- store the verdict in state
    ...


def should_retry(state: RagState) -> str:
    if state.get("graded_sufficient") or state["retry_count"] >= 1:
        return "answer"
    return "rewrite_and_retrieve"


async def rewrite_and_retrieve_node(state: RagState) -> RagState:
    # rewrite the question to be more specific/different, retrieve again,
    # increment retry_count
    ...


async def answer_node(state: RagState) -> RagState:
    # same grounded stuff-documents answering as every prior module
    ...


graph = StateGraph(RagState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("grade", grade_node)
graph.add_node("rewrite_and_retrieve", rewrite_and_retrieve_node)
graph.add_node("answer", answer_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "grade")
graph.add_conditional_edges("grade", should_retry, {"answer": "answer", "rewrite_and_retrieve": "rewrite_and_retrieve"})
graph.add_edge("rewrite_and_retrieve", "grade")
graph.add_edge("answer", END)

corrective_rag = graph.compile()
```

**Ask the learner**, while building this out: *"What stops this from retrying forever on a genuinely unanswerable question?"* → the `retry_count` check inside `should_retry` — make sure they add it before testing, and test specifically against `q22`–`q24` to confirm it still correctly gives up and says "I don't know" rather than looping.

### Option B — Structured Hydration (the Shopwise Pattern)

**Idea:** some facts shouldn't come from an LLM's paraphrase of a document chunk at all — they should come from a system of record. Add a small employee directory as structured data, and make "who is X's manager" answered by SQL, never by the LLM guessing from prose.

1. Create `data/team-directory.csv` (not part of the main document corpus — a separate structured source):
   ```csv
   name,title,department,manager,start_date
   Priya Shah,Engineering Manager,Edge AI,Dana Oyelaran,2023-02-01
   Marcus Webb,Senior Engineer,Edge AI,Priya Shah,2023-03-15
   ...
   ```
2. Load it into a real SQL table (`team_directory`), separate from `fernwood_chunks`.
3. Also embed a short text version of each row ("Priya Shah is an Engineering Manager in Edge AI, reporting to Dana Oyelaran.") into `fernwood_chunks` with `category="directory"` so it's *findable* by the retriever — but the final answer for a directory question is assembled from the SQL row, the same way `shopwise`'s product search hydrates prices from a `products` table rather than letting the LLM state them.
4. In `/ask`, detect directory-style questions (simplest version: if retrieved context includes a chunk with `category="directory"`, look up the named person's row in `team_directory` and build the answer from the SQL row's fields directly, with the LLM only used to phrase the sentence — never to state the manager's name itself).

**Ask the learner**, while building this: *"Why go to the trouble of also embedding a text version of each row, if the real answer comes from SQL?"* → the retriever's job is finding *which* row is relevant to a given question; the SQL table's job is being the authoritative source for what that row actually says. Losing either piece breaks the pattern.

### Capstone demo day

Whichever option is chosen, end with:
1. A walk through `SCOREBOARD.md` as a story — baseline, then what each module moved and why — not a slide deck.
2. One live question that exercises the recency rule (Module 9).
3. One live question that correctly returns "I don't know" (the original Module 3 guarantee, still holding after 16 more modules of changes).
4. For Option A: one question that triggers a retry and recovers. For Option B: one directory question where the name/title comes from SQL, not the LLM's phrasing.

### Quiz + checkpoint

1. Why does Option B still bother retrieving a chunk at all, instead of just running every question against the SQL table directly?
   <details><summary>Answer</summary>The retriever's job is figuring out *which* row (or whether any row) is relevant to an arbitrary natural-language question — SQL alone has no way to match "who does Marcus report to" to the right table row without some retrieval step first; the two are solving different problems.</details>
2. In Option A, what's the actual difference between this and just always retrieving with a larger `k`?
   <details><summary>Answer</summary>A larger fixed <code>k</code> retrieves more every time, regardless of whether the first attempt was already sufficient — it's a constant cost increase. Corrective RAG only pays the cost of a second retrieval attempt when the first one is actually judged insufficient, and it changes the *query*, not just the quantity, on retry.</details>

**Checkpoint:** a working, demoable capstone; a complete `SCOREBOARD.md` telling the whole story from Module 5's baseline forward.
