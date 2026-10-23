import asyncio
import hashlib
import json
from pathlib import Path
import sqlite3
import time

from retrieval_lab.grounded import Store, answer, extractive_provider

VERSION = "capstone-0.1.0"
TOKENS = {"demo-agent-a": "alice", "demo-lead-a": "supervisor", "demo-agent-b": "bob"}
ORDERS = {"QC-3001": ("A", 4500), "QC-3002": ("B", 12000)}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class OfflineProvider:
    kind = "synthetic"
    model = "extractive-v1"

    async def generate(self, evidence):
        return extractive_provider(evidence)


class Engine:
    def __init__(self, directory, corpus, metadata, provider=None, timeout=2.0, maximum_calls=20):
        if type(timeout) not in (int, float) or not 0 < timeout <= 15:
            raise ValueError("invalid timeout")
        if type(maximum_calls) is not int or not 1 <= maximum_calls <= 100:
            raise ValueError("invalid call budget")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.store = Store(self.directory / "support.sqlite")
        if not self.store.db.execute("SELECT COUNT(*) FROM members").fetchone()[0]:
            self.store.seed(corpus, metadata)
        self.store.db.executescript("""
        CREATE TABLE IF NOT EXISTS calls(id INTEGER PRIMARY KEY, at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, actor TEXT NOT NULL,
          order_id TEXT NOT NULL, amount INTEGER NOT NULL, evidence TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS approvals(action TEXT PRIMARY KEY, member TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS effects(action TEXT PRIMARY KEY, amount INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS telemetry(at REAL NOT NULL, status TEXT NOT NULL, latency_ms REAL NOT NULL,
          calls INTEGER NOT NULL, kind TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS controls(id INTEGER PRIMARY KEY CHECK(id=1), halted INTEGER NOT NULL);
        INSERT OR IGNORE INTO controls VALUES(1,0);
        """)
        self.provider = provider or OfflineProvider()
        self.timeout = timeout
        self.maximum_calls = maximum_calls
        self.slots = asyncio.Semaphore(2)

    def close(self):
        self.store.close()

    def session(self, token):
        session = TOKENS.get(token)
        if not session:
            raise PermissionError("denied")
        self.store.principal(session)
        return session

    def reserve(self):
        with self.store.db:
            halted = self.store.db.execute("SELECT halted FROM controls WHERE id=1").fetchone()[0]
            count = self.store.db.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
            if halted or count >= self.maximum_calls:
                return False
            self.store.db.execute("INSERT INTO calls(at) VALUES(?)", (time.time(),))
        return True  # Single event-loop process; no await between check and insert.

    def current(self, session, citations):
        for c in citations:
            doc = self.store.allowed(session, c["document"], 100)
            if not doc or doc["revision"] != c["revision"] or doc["hash"] != c["source_sha256"]:
                return False
        return bool(citations)

    async def ask(self, token, query, *, observe_retrieval=None):
        start = time.monotonic()
        calls = 0
        result = {"status": "failed", "citations": [], "retrieved": []}
        try:
            session = self.session(token)
            if self.slots.locked():
                result["status"] = "busy"
                return result
            async with self.slots:
                captured = []

                def capture(evidence):
                    captured.extend(evidence)
                    return extractive_provider(evidence)

                initial = answer(self.store, session, query, now=100, provider=capture,
                                 observe_retrieval=observe_retrieval)
                if initial["status"] != "ready":
                    result = initial
                    return result
                if not self.reserve():
                    result["status"] = "budget_or_halt"
                    return result
                calls = 1
                remaining = self.timeout - (time.monotonic()-start)
                if remaining <= 0:
                    raise TimeoutError()
                proposal = await asyncio.wait_for(self.provider.generate(captured), remaining)
                if not self.current(session, initial["citations"]):
                    result["status"] = "abstained"
                    return result
                result = answer(self.store, session, query, now=100, provider=lambda evidence: proposal)
                return result
        except PermissionError:
            result["status"] = "denied"
            return result
        except (TimeoutError, ValueError, TypeError, KeyError, RuntimeError):
            return result
        finally:
            # Allowlist only: no raw body, auth, query, answer, tool result or exception text.
            with self.store.db:
                self.store.db.execute("INSERT INTO telemetry VALUES(?,?,?,?,?)",
                    (time.time(), result["status"], (time.monotonic()-start)*1000, calls, self.provider.kind))

    def order(self, token, order_id):
        session = self.session(token)
        principal = self.store.principal(session)
        item = ORDERS.get(order_id)
        if not item or item[0] != principal["tenant"]:
            raise PermissionError("order unavailable")
        return {"order_id": order_id, "total_cents": item[1]}

    def propose(self, token, order_id, amount, citations):
        session = self.session(token)
        order = self.order(token, order_id)
        if type(amount) is not int or not 0 < amount <= min(5000, order["total_cents"]):
            raise ValueError("invalid amount")
        # Only the reviewed refund-policy topic can support a refund proposal.
        if not self.current(session, citations) or any(
                self.store.allowed(session, c["document"], 100)["topic"] != "refund" for c in citations):
            raise PermissionError("refund evidence unavailable")
        for c in citations:
            doc = self.store.allowed(session, c["document"], 100)
            if c["quote"] != doc["claim"]:
                raise PermissionError("unsupported claim")
        tenant = self.store.principal(session)["tenant"]
        payload = {"tenant": tenant, "order": order_id, "amount_cents": amount, "evidence": citations}
        key = digest(payload)
        with self.store.db:
            self.store.db.execute("INSERT OR IGNORE INTO actions VALUES(?,?,?,?,?,?,?)",
                (key, tenant, session, order_id, amount, json.dumps(citations, sort_keys=True), "pending"))
        return {"action_id": key, "status": self.action(token, key)["status"]}

    def action(self, token, key):
        tenant = self.store.principal(self.session(token))["tenant"]
        row = self.store.db.execute("SELECT * FROM actions WHERE id=? AND tenant=?", (key, tenant)).fetchone()
        if not row:
            raise PermissionError("action unavailable")
        return dict(row)

    def approve(self, token, key):
        session = self.session(token)
        p = self.store.principal(session)
        action = self.action(token, key)
        if p["role"] != "supervisor" or session == action["actor"] or action["status"] != "pending":
            raise PermissionError("approval denied")
        with self.store.db:
            self.store.db.execute("INSERT OR IGNORE INTO approvals VALUES(?,?)", (key, session))
        return {"status": "approval_recorded"}

    def execute(self, token, key, *, crash_before_commit=False):
        action = self.action(token, key)
        # One transaction contains authorization recheck, simulated local effect and completion.
        self.store.db.execute("BEGIN IMMEDIATE")
        try:
            if self.store.db.execute("SELECT halted FROM controls WHERE id=1").fetchone()[0]:
                raise PermissionError("rollout halted")
            actor = self.store.principal(action["actor"])
            approval = self.store.db.execute("SELECT member FROM approvals WHERE action=?", (key,)).fetchone()
            approver = self.store.principal(approval[0]) if approval else None
            if (not approver or approver["role"] != "supervisor" or approver["tenant"] != action["tenant"]
                    or approver["session"] == action["actor"] or actor["tenant"] != action["tenant"]
                    or not self.current(action["actor"], json.loads(action["evidence"]))):
                raise PermissionError("current authority/evidence denied")
            applied = self.store.db.execute("SELECT 1 FROM effects WHERE action=?", (key,)).fetchone()
            spent = self.store.db.execute("SELECT COALESCE(SUM(e.amount),0) FROM effects e JOIN actions a "
                "ON a.id=e.action WHERE a.tenant=? AND a.order_id=?", (action["tenant"], action["order_id"])).fetchone()[0]
            if not applied and spent+action["amount"] > ORDERS[action["order_id"]][1]:
                raise PermissionError("aggregate order limit")
            self.store.db.execute("INSERT OR IGNORE INTO effects VALUES(?,?)", (key, action["amount"]))
            if crash_before_commit:
                raise RuntimeError("simulated crash before commit")
            self.store.db.execute("UPDATE actions SET status='done' WHERE id=?", (key,))
            self.store.db.commit()
            return {"status": "done", "effect_count": 1}
        except BaseException:
            self.store.db.rollback()
            raise

    def halt(self):
        with self.store.db:
            self.store.db.execute("UPDATE controls SET halted=1 WHERE id=1")

    def expire_telemetry(self, now):
        with self.store.db:
            return self.store.db.execute("DELETE FROM telemetry WHERE at <= ?", (now-604800,)).rowcount


def fixture_paths():
    # Installed retrieval package and fixtures are supplied together by the root-context Docker build.
    import os
    root = Path(os.environ.get("CAPSTONE_RETRIEVAL", "../../langchain/02-rag-capstone-workbook/retrieval-lab"))
    return root / "secure-fixtures", json.loads((root/"security-metadata.json").read_text(encoding="utf-8"))
