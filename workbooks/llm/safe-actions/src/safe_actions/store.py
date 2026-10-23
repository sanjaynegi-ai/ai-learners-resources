"""Durable state in SQLite: trusted records (orders, tickets), approvals, and actions.

An `actions` row is written in the same transaction as the decision to act. Rows with status `queued` are the
outbox: a dispatcher sends them later, so a crash can never leave "decided" without a record of what to do.
"""
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders(order_id TEXT PRIMARY KEY, tenant TEXT NOT NULL, total_cents INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS tickets(ticket_id TEXT PRIMARY KEY, tenant TEXT NOT NULL, order_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS actions(
    action_key TEXT PRIMARY KEY,           -- idempotency key derived from tenant, ticket, tool and arguments
    tenant TEXT NOT NULL, actor TEXT NOT NULL, ticket_id TEXT NOT NULL, tool TEXT NOT NULL, args TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending_approval', 'queued', 'done', 'failed')),
    attempts INTEGER NOT NULL DEFAULT 0, result TEXT, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS approvals(action_key TEXT NOT NULL, approver TEXT NOT NULL, PRIMARY KEY(action_key, approver));
"""


@dataclass(frozen=True)
class Principal:
    """Established by authentication, never by the model or the request body."""
    user: str
    tenant: str
    role: str  # "agent" or "supervisor"


PRINCIPALS = {
    "agent-a": Principal("agent-a", "shop-a", "agent"),
    "lead-a": Principal("lead-a", "shop-a", "supervisor"),
    "agent-b": Principal("agent-b", "shop-b", "agent"),
}


class Store:
    def __init__(self, path: Path | str) -> None:
        self.db = sqlite3.connect(path, isolation_level=None)  # Explicit transactions below
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def seed(self) -> None:
        with self.transaction():
            self.db.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?)",
                                [("QC-3001", "shop-a", 4500), ("QC-3002", "shop-b", 12000)])
            self.db.executemany("INSERT OR IGNORE INTO tickets VALUES (?, ?, ?)",
                                [("T-31", "shop-a", "QC-3001"), ("T-32", "shop-b", "QC-3002")])

    def transaction(self):
        return _Transaction(self.db)

    # Trusted lookups, always scoped by tenant.
    def ticket(self, tenant: str, ticket_id: str):
        return self.db.execute("SELECT ticket_id, order_id FROM tickets WHERE tenant=? AND ticket_id=?",
                               (tenant, ticket_id)).fetchone()

    def order(self, tenant: str, order_id: str):
        return self.db.execute("SELECT order_id, total_cents FROM orders WHERE tenant=? AND order_id=?",
                               (tenant, order_id)).fetchone()

    def record_action(self, key: str, principal: Principal, ticket_id: str, tool: str, args: dict, status: str) -> str | None:
        """Insert once. Returns None if inserted, or the existing status if this key was already recorded."""
        with self.transaction():
            existing = self.db.execute("SELECT status FROM actions WHERE action_key=?", (key,)).fetchone()
            if existing:
                return existing[0]
            self.db.execute("INSERT INTO actions(action_key, tenant, actor, ticket_id, tool, args, status, created_at) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (key, principal.tenant, principal.user, ticket_id, tool, json.dumps(args, sort_keys=True),
                             status, time.time()))
            return None

    def action(self, key: str):
        row = self.db.execute("SELECT tenant, actor, tool, args, status, attempts, result FROM actions WHERE action_key=?",
                              (key,)).fetchone()
        if row is None:
            return None
        names = ("tenant", "actor", "tool", "args", "status", "attempts", "result")
        return dict(zip(names, row)) | {"args": json.loads(row[3])}

    def queued(self) -> list[str]:
        return [row[0] for row in self.db.execute("SELECT action_key FROM actions WHERE status='queued' ORDER BY created_at")]

    def add_approval(self, key: str, approver: str) -> bool:
        """Record an approval and release the action to the outbox, atomically."""
        with self.transaction():
            row = self.db.execute("SELECT status FROM actions WHERE action_key=?", (key,)).fetchone()
            if row is None or row[0] != "pending_approval":
                return False
            self.db.execute("INSERT OR IGNORE INTO approvals VALUES (?, ?)", (key, approver))
            self.db.execute("UPDATE actions SET status='queued' WHERE action_key=?", (key,))
            return True

    def count_attempt(self, key: str) -> int:
        with self.transaction():
            self.db.execute("UPDATE actions SET attempts = attempts + 1 WHERE action_key=?", (key,))
            return self.db.execute("SELECT attempts FROM actions WHERE action_key=?", (key,)).fetchone()[0]

    def finish(self, key: str, status: str, result: str | None) -> None:
        with self.transaction():
            self.db.execute("UPDATE actions SET status=?, result=? WHERE action_key=?", (status, result, key))


class _Transaction:
    """BEGIN IMMEDIATE takes the write lock up front, so check-then-insert cannot interleave across connections."""

    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db

    def __enter__(self):
        self.db.execute("BEGIN IMMEDIATE")
        return self.db

    def __exit__(self, exc_type, exc, tb):
        self.db.execute("ROLLBACK" if exc_type else "COMMIT")
        return False
