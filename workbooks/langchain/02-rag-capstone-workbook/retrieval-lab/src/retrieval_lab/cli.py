import argparse
import json
from pathlib import Path
from .core import ingest, manifest, rank


def main():
    parser = argparse.ArgumentParser(description="Synthetic offline retrieval mechanics; no learned embeddings")
    parser.add_argument("--corpus", type=Path, default=Path("fixtures"))
    parser.add_argument("--query", default="money back")
    parser.add_argument("--size", type=int, default=40)
    parser.add_argument("--overlap", type=int, default=8)
    parser.add_argument("--topic")
    parser.add_argument("--output", type=Path, default=Path("results/retrieval.json"))
    args = parser.parse_args()
    try:
        if args.output.resolve().is_relative_to(args.corpus.resolve()):
            raise ValueError("Write results outside the input corpus")
        chunks = ingest(args.corpus, size=args.size, overlap=args.overlap)
        report = manifest(chunks, args.size, args.overlap)
        report.update(query=args.query, topic=args.topic, evidence_kind="offline-authored-feature-demo",
                      rankings={m: [{"id": c.id, "document": c.document, "section": c.section,
                                     "score": s, "text": c.text} for c, s in rank(chunks, args.query, mode=m, topic=args.topic)]
                                for m in ("lexical", "vector", "hybrid")})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"chunks": len(chunks), "ranked_documents": {
            m: [r["document"] for r in rows] for m, rows in report["rankings"].items()}}, indent=2))
    except (ValueError, OSError, UnicodeError) as error:
        parser.exit(2, f"Ingestion/retrieval failed: {error}\n")


if __name__ == "__main__":
    main()
