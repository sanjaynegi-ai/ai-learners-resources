"""Privileged local operator interface. Filesystem access is the authority boundary."""
import argparse
import json
import time

from .core import Engine, fixture_paths


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state", required=True)
    p.add_argument("command", choices=("halt", "revoke", "delete", "expire", "status"))
    p.add_argument("--target", choices=("alice", "supervisor", "bob", "refunds-policy.md"))
    args = p.parse_args()
    engine = Engine(args.state, *fixture_paths())
    try:
        if args.command == "halt":
            engine.halt()
        elif args.command == "revoke":
            if args.target not in ("alice", "supervisor", "bob"):
                p.error("choose a member target")
            engine.store.revoke(args.target)
        elif args.command == "delete":
            if args.target != "refunds-policy.md":
                p.error("choose the disposable refund policy")
            engine.store.delete(args.target)
        elif args.command == "expire":
            print(json.dumps({"expired": engine.expire_telemetry(time.time())}))
        else:
            print(json.dumps({"halted": bool(engine.store.db.execute("SELECT halted FROM controls").fetchone()[0]),
                "calls": engine.store.db.execute("SELECT COUNT(*) FROM calls").fetchone()[0],
                "effects": engine.store.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]}))
    finally:
        engine.close()
