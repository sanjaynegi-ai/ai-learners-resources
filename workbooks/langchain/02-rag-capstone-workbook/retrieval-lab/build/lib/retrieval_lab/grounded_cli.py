import argparse
import json
from pathlib import Path
from .evaluation import comparison
from .grounded import Store, answer


def main():
    parser = argparse.ArgumentParser(description="Local curated RAG reference; no credentials or network")
    parser.add_argument("command", choices=("ask", "evaluate", "drill"))
    parser.add_argument("--query", default="money back")
    parser.add_argument("--session", default="alice", help="Local synthetic fixture identity; not a web authentication token")
    parser.add_argument("--output", type=Path, default=Path("results/grounded.json"))
    args = parser.parse_args()
    root = Path.cwd()
    if not (root / "security-metadata.json").is_file():
        parser.exit(2, "Run from the retrieval-lab working directory\n")
    if not args.output.resolve().is_relative_to((root / "results").resolve()):
        parser.exit(2, "Output must be within this lab's results directory\n")
    if args.command == "evaluate":
        report = comparison(root)
    else:
        store = Store()
        try:
            store.seed(root / "secure-fixtures", json.loads((root / "security-metadata.json").read_text()))
            if args.command == "drill":
                before = answer(store, "alice", "refund")
                stale = answer(store, "alice", "refund", after_retrieval=lambda: store.change_acl("refunds-policy.md", ["supervisor"]))
                repaired = answer(store, "supervisor", "refund")
                store.delete("refunds-policy.md")
                deleted = answer(store, "supervisor", "refund")
                report = {"before": before, "revoked_during_request": stale,
                          "authorized_repair": repaired, "after_delete": deleted}
            else:
                report = answer(store, args.session, args.query)
        finally:
            store.close()
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
