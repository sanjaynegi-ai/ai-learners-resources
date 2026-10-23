"""Behavior checks for the independent feed; no paid calls or files mutated."""
import argparse
import importlib
from retrieval_lab.lifecycle import LifecycleStore


def check(module):
    apply = importlib.import_module(module).apply_events
    store = LifecycleStore()
    try:
        raw = "# Returns\nRefund window is 30 days."
        meta = dict(tenant="A", roles=["support"], expires=1000, topic="refund",
                    claim="Refund window is 30 days.", value="30")
        event = dict(operation="upsert", source="returns.md", raw=raw, metadata=meta)
        assert apply(store, [event])[0]["status"] == "published"
        assert apply(store, [event])[0]["parsed"] == 0
        for bad in ({"operation": "erase", "source": "returns.md"},
                    event | {"metadata": {}}, event | {"source": "../outside.md"},
                    event | {"untrusted": True}):
            try:
                apply(store, [dict(operation="delete", source="returns.md"), bad])
            except ValueError:
                pass
            else:
                raise AssertionError("Malformed batch was accepted")
            assert store.db.execute("SELECT deleted FROM documents WHERE id='returns.md'").fetchone()[0] == 0
        try:
            apply(store, [event] * 21)
        except ValueError:
            pass
        else:
            raise AssertionError("Unbounded batch accepted")
        assert apply(store, []) == []
        assert store.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 1
        assert apply(store, [event | {"raw": "# Empty"}])[0]["status"] == "quarantined"
        assert store.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 0
        assert [r["status"] for r in apply(store, [event, dict(operation="delete", source="returns.md")])] == ["published", "deleted"]
        print("Incremental feed checks passed; independent explanation still required")
    finally:
        store.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    check("lifecycle_events_reference" if args.reference else "lifecycle_events")
