"""Complete comparison for the three-step lifecycle walk; inspect after attempting."""
from pathlib import Path
from retrieval_lab.grounded import answer
from retrieval_lab.lifecycle import LifecycleStore

ROOT = Path(__file__).resolve().parents[1]


def main():
    store = LifecycleStore()
    try:
        store.db.execute("INSERT INTO members VALUES('alice','A','support',1)")
        store.db.commit()
        raw = (ROOT / "lifecycle-fixtures/returns.md").read_text(encoding="utf-8")
        table = (ROOT / "lifecycle-fixtures/credits.csv").read_text(encoding="utf-8")
        meta = dict(tenant="A", roles=["support"], expires=1000, topic="refund",
                    claim="Refund window is 30 days.", value="30")
        first = store.publish("returns.md", raw, meta)
        rows = store.publish("credits.csv", table, meta | {"claim": "limit_cents=5000", "topic": "credit"})
        repeated = store.publish("returns.md", raw, meta)
        alias = store.publish("copy.md", raw, meta)
        assert (first["status"], rows["written"], repeated["parsed"], alias["status"]) == (
            "published", 2, 0, "quarantined")
        assert len(store.candidates("alice", 100)) == 3
        print("Step 1: 3 chunks; repeat parsed=0; alias quarantined")

        old = {c.id for c in store.candidates("alice", 100) if c.document == "returns.md"}
        other = [c for c in store.candidates("alice", 100) if c.document == "credits.csv"]
        revised = raw.replace("30 days", "14 days")
        current_meta = meta | {"claim": "Refund window is 14 days.", "value": "14"}
        changed = store.publish("returns.md", revised, current_meta)
        now = store.candidates("alice", 100)
        assert old.isdisjoint(c.id for c in now)
        assert other == [c for c in now if c.document == "credits.csv"]
        assert changed["revision"] == 2
        assert answer(store, "alice", "refund")["status"] == "ready"
        print("Step 2: revision=2; old IDs absent; table unchanged")

        failed = store.publish("returns.md", "# Empty", current_meta)
        assert failed["status"] == "quarantined"
        assert not any(c.document == "returns.md" for c in store.candidates("alice", 100))
        repaired = store.publish("returns.md", revised, current_meta)
        assert repaired["revision"] == 4
        snapshot = {"returns.md": (revised, current_meta),
                    "credits.csv": (table, meta | {"claim": "limit_cents=5000", "topic": "credit"})}
        rebuilt = store.rebuild(snapshot)
        assert rebuilt == {"parsed": 2, "written": 3}
        store.delete("returns.md")
        assert all(c.document != "returns.md" for c in store.candidates("alice", 100))
        print("Step 3: failed replacement hidden; repaired revision=4; rebuild parsed=2; deleted")
    finally:
        store.close()


if __name__ == "__main__":
    main()
