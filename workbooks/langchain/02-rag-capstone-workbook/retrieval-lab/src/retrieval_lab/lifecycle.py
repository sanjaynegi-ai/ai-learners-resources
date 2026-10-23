"""Bounded single-writer source publication using the grounded lab's SQLite store.

Metadata is reviewed publisher input, never inferred from source text. No OCR,
remote fetching, background indexing or distributed publication is implemented.
"""
import csv
import io
import json
import re
import tempfile
from dataclasses import asdict
from pathlib import Path

from .core import Chunk, ingest, sha
from .grounded import Store

PARSER = "lifecycle-md-csv-v1"


def extract(source, raw, topic):
    """Retain Markdown conditions and CSV header/value associations and units."""
    if not raw.strip() or len(raw.encode("utf-8")) > 100_000:
        raise ValueError("Empty or oversized source")
    if source.endswith(".md"):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, source).write_text(raw, encoding="utf-8")
            return ingest(directory, size=80, overlap=16)
    if not source.endswith(".csv"):
        raise ValueError("Only Markdown and bounded UTF-8 CSV are supported")
    reader = csv.DictReader(io.StringIO(raw), strict=True)
    headers = ["condition", "limit_cents", "approval"]
    if reader.fieldnames != headers:
        raise ValueError("Require condition,limit_cents,approval columns in order")
    chunks = []
    for line, row in enumerate(reader, 2):
        if (line > 101 or set(row) != set(headers)
                or any(not isinstance(v, str) or not v.strip() for v in row.values())
                or not row["limit_cents"].isdigit()):
            raise ValueError("Invalid or excessive CSV rows")
        text = "; ".join(f"{key}={row[key]}" for key in headers)
        chunks.append(Chunk(sha(f"{source}:{sha(raw)}:{line}:{PARSER}"), source,
                            sha(raw), f"CSV record {line - 1}", topic, 0,
                            len(text.split()), text))
    if not chunks:
        raise ValueError("CSV has no data rows")
    return chunks


class LifecycleStore(Store):
    def __init__(self, path=":memory:"):
        super().__init__(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS publications(
          source TEXT PRIMARY KEY, signature TEXT, parser TEXT, state TEXT);
        CREATE TABLE IF NOT EXISTS attempts(
          sequence INTEGER PRIMARY KEY, source TEXT, source_hash TEXT,
          status TEXT, reason TEXT);
        """)

    def publish(self, source, raw, metadata, *, force=False):
        # A source ID is one flat filename, scoped here by a trusted single publisher.
        if not isinstance(source, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}", source):
            raise ValueError("Require a flat lowercase source ID")
        if not isinstance(raw, str):
            raise ValueError("Require decoded UTF-8 source text")
        required = {"tenant", "roles", "expires", "topic", "claim", "value"}
        if (not isinstance(metadata, dict) or set(metadata) != required or not isinstance(metadata["roles"], list)
                or not metadata["roles"] or any(not isinstance(r, str) or not r for r in metadata["roles"])
                or type(metadata["expires"]) is not int
                or any(not isinstance(metadata[k], str) or not metadata[k]
                       for k in ("tenant", "topic", "claim", "value"))):
            raise ValueError("Require complete trusted review metadata")
        signature = sha(json.dumps([sha(raw), metadata, PARSER], sort_keys=True))
        old = self.db.execute("SELECT * FROM documents WHERE id=?", (source,)).fetchone()
        publication = self.db.execute("SELECT * FROM publications WHERE source=?", (source,)).fetchone()
        current = old and not old["deleted"] and self.db.execute(
            "SELECT 1 FROM chunks WHERE document=? AND revision=?", (source, old["revision"])).fetchone()
        if current and publication and publication["state"] == "active" and publication["signature"] == signature and not force:
            return {"status": "unchanged", "parsed": 0, "written": 0, "revision": old["revision"]}
        revision = (old["revision"] if old else 0) + 1
        try:
            # Duplicate aliases are quarantined, never merged across ACLs or tenants.
            duplicate = self.db.execute(
                "SELECT id FROM documents WHERE id!=? AND hash=? AND deleted=0 AND tenant=?",
                (source, sha(raw), metadata["tenant"])).fetchone()
            if duplicate:
                raise ValueError("Duplicate content under another source ID; publisher must resolve alias")
            chunks = extract(source, raw, metadata["topic"])
            if not any(metadata["claim"] in c.text for c in chunks):
                raise ValueError("Reviewed claim did not survive extraction")
        except (ValueError, UnicodeError, csv.Error, OSError):
            # Deliberately fail closed: a broken replacement makes the old version unavailable.
            with self.db:
                self.db.execute("DELETE FROM chunks WHERE document=?", (source,))
                self.db.execute("UPDATE documents SET revision=?, deleted=1, claim='', value='', hash='' WHERE id=?",
                                (revision, source))
                self.db.execute("INSERT OR REPLACE INTO publications VALUES(?,?,?,?)",
                                (source, signature, PARSER, "quarantined"))
                self.db.execute("INSERT INTO attempts(source,source_hash,status,reason) VALUES(?,?,?,?)",
                                (source, sha(raw), "quarantined", "extraction-or-duplicate-review-required"))
            return {"status": "quarantined", "parsed": 1, "written": 0, "revision": revision}
        with self.db:
            self.db.execute("DELETE FROM chunks WHERE document=?", (source,))
            self.db.execute("INSERT OR REPLACE INTO documents VALUES(?,?,?,?,?,0,?,?,?,?)",
                            (source, metadata["tenant"], json.dumps(metadata["roles"]), revision,
                             metadata["expires"], metadata["topic"], metadata["claim"], metadata["value"], sha(raw)))
            for chunk in chunks:
                self.db.execute("INSERT INTO chunks VALUES(?,?,?,?)",
                                (chunk.id, source, revision, json.dumps(asdict(chunk))))
            self.db.execute("INSERT OR REPLACE INTO publications VALUES(?,?,?,?)",
                            (source, signature, PARSER, "active"))
            self.db.execute("INSERT INTO attempts(source,source_hash,status,reason) VALUES(?,?,?,?)",
                            (source, sha(raw), "published", "reviewed-source"))
        return {"status": "published", "parsed": 1, "written": len(chunks), "revision": revision}

    def delete(self, document):
        # An explicit tombstone prevents a deleted source's old signature skipping republish.
        with self.db:
            self.db.execute("DELETE FROM chunks WHERE document=?", (document,))
            self.db.execute("UPDATE documents SET deleted=1, revision=revision+1, claim='', value='', hash='', tenant='', roles='[]', expires=0, topic='' WHERE id=?", (document,))
            self.db.execute("UPDATE publications SET state='deleted', signature='' WHERE source=?", (document,))
            self.db.execute("INSERT INTO attempts(source,source_hash,status,reason) VALUES(?,'','deleted','publisher-delete')",
                            (document,))

    def rebuild(self, snapshot):
        """Re-extract every source from a complete trusted snapshot, atomically.

        Unlike publish, omission means deletion. Reject the rebuild as a whole
        if any source fails, leaving the previous committed snapshot available.
        """
        if not isinstance(snapshot, dict) or len(snapshot) > 100:
            raise ValueError("Require complete snapshot of at most 100 sources")
        self.db.execute("SAVEPOINT rebuild")
        try:
            # publish uses connection contexts (which commit), so use a separate staging DB.
            staging = LifecycleStore()
            try:
                reports = [staging.publish(source, raw, meta) for source, (raw, meta) in snapshot.items()]
                if any(r["status"] != "published" for r in reports):
                    raise ValueError("Rebuild rejected; repair snapshot before retry")
                self.db.execute("DELETE FROM chunks")
                for row in self.db.execute("SELECT id FROM documents").fetchall():
                    if row["id"] not in snapshot:
                        self.db.execute("UPDATE documents SET deleted=1, revision=revision+1, claim='', value='', hash='' WHERE id=?", (row["id"],))
                        self.db.execute("UPDATE publications SET state='deleted', signature='' WHERE source=?", (row["id"],))
                for row in staging.db.execute("SELECT * FROM documents"):
                    old = self.db.execute("SELECT revision FROM documents WHERE id=?", (row["id"],)).fetchone()
                    revision = (old[0] if old else 0) + 1
                    values = list(row)
                    values[3] = revision
                    self.db.execute("INSERT OR REPLACE INTO documents VALUES(?,?,?,?,?,?,?,?,?,?)", values)
                    for chunk in staging.db.execute("SELECT * FROM chunks WHERE document=?", (row["id"],)):
                        self.db.execute("INSERT INTO chunks VALUES(?,?,?,?)", (chunk["id"], chunk["document"], revision, chunk["payload"]))
                for row in staging.db.execute("SELECT * FROM publications"):
                    self.db.execute("INSERT OR REPLACE INTO publications VALUES(?,?,?,?)", tuple(row))
                for row in staging.db.execute("SELECT * FROM attempts"):
                    self.db.execute("INSERT INTO attempts(source,source_hash,status,reason) VALUES(?,?,?,?)", tuple(row)[1:])
            finally:
                staging.close()
            self.db.execute("RELEASE rebuild")
            return {"parsed": len(snapshot), "written": sum(r["written"] for r in reports)}
        except BaseException:
            self.db.execute("ROLLBACK TO rebuild")
            self.db.execute("RELEASE rebuild")
            raise
