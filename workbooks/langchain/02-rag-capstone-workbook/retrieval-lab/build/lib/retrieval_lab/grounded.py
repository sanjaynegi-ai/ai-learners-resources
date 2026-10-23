"""Curated extractive RAG reference. SQLite is trusted application state, not model input."""
import json
import sqlite3
from dataclasses import asdict

from .core import Chunk, ingest, rank, sha


class Store:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS members(session TEXT PRIMARY KEY, tenant TEXT, role TEXT, active INTEGER);
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, tenant TEXT, roles TEXT, revision INTEGER,
          expires INTEGER, deleted INTEGER, topic TEXT, claim TEXT, value TEXT, hash TEXT);
        CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY, document TEXT, revision INTEGER, payload TEXT);
        """)

    def seed(self, corpus, metadata):
        chunks = ingest(corpus)
        with self.db:
            self.db.execute("DELETE FROM chunks")
            self.db.execute("DELETE FROM documents")
            self.db.execute("DELETE FROM members")
            for session, principal in metadata["members"].items():
                self.db.execute("INSERT INTO members VALUES(?,?,?,1)", (session, *principal))
            for doc, meta in metadata["documents"].items():
                matches = [c for c in chunks if c.document == doc]
                if not matches or not any(meta["claim"] in c.text for c in matches):
                    raise ValueError("Reviewed claim must survive in a source chunk")
                self.db.execute("INSERT INTO documents VALUES(?,?,?,?,?,0,?,?,?,?)",
                                (doc, meta["tenant"], json.dumps(meta["roles"]), 1, meta["expires"],
                                 meta["topic"], meta["claim"], meta["value"], matches[0].source_sha256))
                for chunk in matches:
                    self.db.execute("INSERT INTO chunks VALUES(?,?,1,?)", (chunk.id, doc, json.dumps(asdict(chunk))))

    def principal(self, session):
        row = self.db.execute("SELECT * FROM members WHERE session=? AND active=1", (session,)).fetchone()
        if row is None:
            raise PermissionError("Unknown or revoked local session")
        return row

    def allowed(self, session, document, now):
        principal = self.principal(session)
        row = self.db.execute("SELECT * FROM documents WHERE id=?", (document,)).fetchone()
        return row if (row and not row["deleted"] and row["expires"] > now
                       and row["tenant"] == principal["tenant"]
                       and principal["role"] in json.loads(row["roles"])) else None

    def candidates(self, session, now):
        self.principal(session)  # Fail closed even for an empty corpus.
        result = []
        for row in self.db.execute("SELECT * FROM chunks"):
            document = self.allowed(session, row["document"], now)
            if not document or document["revision"] != row["revision"]:
                continue
            chunk = Chunk(**json.loads(row["payload"]))
            if chunk.source_sha256 == document["hash"]:
                result.append(chunk)
        return result

    def revoke(self, session):
        with self.db:
            self.db.execute("UPDATE members SET active=0 WHERE session=?", (session,))

    def change_acl(self, document, roles):
        with self.db:
            self.db.execute("UPDATE documents SET roles=? WHERE id=?", (json.dumps(roles), document))

    def invalidate(self, document):
        # Publisher marks a new current revision BEFORE replacing its index. Old chunks fail closed.
        with self.db:
            self.db.execute("UPDATE documents SET revision=revision+1 WHERE id=?", (document,))

    def delete(self, document):
        with self.db:
            self.db.execute("DELETE FROM chunks WHERE document=?", (document,))
            self.db.execute("UPDATE documents SET deleted=1, claim='', value='', hash='', tenant='', "
                            "roles='[]', revision=0, expires=0, topic='' WHERE id=?", (document,))

    def close(self):
        self.db.close()


def intent(query):
    """Deliberately small, explicit English route. Not a general semantic intent classifier."""
    return {"refund": "refund", "refund evidence": "refund", "money back": "refund",
            "delay-42": "tracking", "conflict window": "conflict", "injection report": "injection",
            "private review": "private"}.get(query.strip().lower())


def extractive_provider(evidence):
    """Mock generation: quote a reviewed claim, never follow document instructions."""
    first = evidence[0]
    return {"citations": [{"id": first["id"], "quote": first["claim"]}]}


def answer(store, session, query, *, now=100, mode="hybrid", provider=extractive_provider,
           after_retrieval=None, observe_retrieval=None):
    if not isinstance(query, str) or not 0 < len(query.strip()) <= 500:
        raise ValueError("Question must contain 1-500 characters")
    try:
        candidates = store.candidates(session, now)
    except PermissionError:
        return {"status": "denied", "citations": [], "retrieved": []}
    topic = intent(query)
    if topic is None:
        return {"status": "abstained", "citations": [], "retrieved": []}
    eligible = [c for c in candidates if store.allowed(session, c.document, now)["topic"] == topic]
    ranked = rank(eligible, query, mode=mode, k=3)
    evidence = []
    for chunk, _ in ranked:
        doc = store.allowed(session, chunk.document, now)
        if doc["claim"] in chunk.text:
            evidence.append({"id": chunk.id, "document": chunk.document, "revision": doc["revision"],
                             "hash": doc["hash"], "claim": doc["claim"], "value": doc["value"]})
    retrieved = [e["document"] for e in evidence]
    if observe_retrieval:
        # Trusted evaluation instrumentation, separate from the public response contract.
        observe_retrieval(tuple(retrieved))
    if not evidence or sum(len(e["claim"]) for e in evidence) > 5000:
        return {"status": "abstained", "citations": [], "retrieved": retrieved}
    # Curated conflict labels are ingestion-review annotations, NOT general contradiction detection.
    if len({store.allowed(session, c.document, now)["value"] for c in eligible}) > 1:
        return {"status": "conflict", "citations": [], "retrieved": retrieved}
    if after_retrieval:
        after_retrieval()
    try:
        for e in evidence:
            doc = store.allowed(session, e["document"], now)
            if not doc or doc["revision"] != e["revision"] or doc["hash"] != e["hash"]:
                raise ValueError("Evidence changed before generation")
        proposal = provider(evidence)  # Exactly one offline call; no tools or side effects.
        if not isinstance(proposal, dict) or set(proposal) != {"citations"}:
            raise ValueError("Invalid output schema")
        citations = proposal["citations"]
        if not isinstance(citations, list) or not 1 <= len(citations) <= 3:
            raise ValueError("Invalid citations")
        trusted = {e["id"]: e for e in evidence}
        validated = []
        for citation in citations:
            if not isinstance(citation, dict) or set(citation) != {"id", "quote"}:
                raise ValueError("Invalid citation schema")
            e = trusted.get(citation["id"])
            if not e or citation["quote"] != e["claim"]:
                raise ValueError("Unsupported quote")
            doc = store.allowed(session, e["document"], now)
            if not doc or doc["revision"] != e["revision"] or doc["hash"] != e["hash"]:
                raise ValueError("Evidence permission/version changed")
            validated.append({"document": e["document"], "chunk": e["id"], "quote": e["claim"],
                              "revision": e["revision"], "source_sha256": e["hash"]})
        return {"status": "ready", "citations": validated, "retrieved": retrieved}
    except (ValueError, TypeError, KeyError, PermissionError):
        # No stale snippets, IDs or candidate trace returned after a revocation/output failure.
        return {"status": "abstained", "citations": [], "retrieved": []}
