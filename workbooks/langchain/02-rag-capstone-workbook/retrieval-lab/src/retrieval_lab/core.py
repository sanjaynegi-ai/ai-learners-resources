import hashlib
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

PARSER_VERSION = "heading-paragraph-v1"
TOKENIZER_VERSION = "ascii-word-hyphen-v1"
TOY_EMBEDDING_VERSION = "authored-alias-counts-v1"
# Hand-authored features for mechanics ONLY, not a trained semantic model.
ALIASES = {"money": "refund", "back": "refund", "reimbursement": "refund",
           "broken": "damaged", "parcel": "shipment", "package": "shipment"}


def tokens(text):
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class Chunk:
    id: str
    document: str
    source_sha256: str
    section: str
    topic: str
    start_word: int
    end_word: int
    text: str


def ingest(directory, *, size=40, overlap=8):
    if type(size) is not int or type(overlap) is not int or size < 1 or not 0 <= overlap < size:
        raise ValueError("Require integer size > overlap >= 0")
    root = Path(directory)
    if not root.is_dir():
        raise ValueError("Corpus directory does not exist")
    paths = sorted(root.iterdir())
    if len(paths) > 100:
        raise ValueError("Lab accepts at most 100 documents")
    if not paths or any(p.suffix != ".md" or not p.is_file() or p.is_symlink() for p in paths):
        raise ValueError("Only plain local Markdown files accepted")
    chunks = []
    for path in paths:
        if path.stat().st_size > 100_000:
            raise ValueError("Document exceeds lab byte bound")
        raw = path.read_text(encoding="utf-8")
        section, lines = "Untitled", []
        sections = []
        for line in raw.splitlines():
            if line.startswith("#"):
                if lines:
                    sections.append((section, " ".join(lines)))
                section, lines = line.lstrip("#").strip(), []
            elif line.strip():
                lines.append(line.strip())
        if lines:
            sections.append((section, " ".join(lines)))
        if not sections:
            raise ValueError(f"Empty document: {path.name}")
        # Offsets are whitespace words WITHIN EACH SECTION, not model tokens or character offsets.
        for section_index, (heading, text) in enumerate(sections):
            if not tokens(text):
                raise ValueError("Section has no searchable text")
            words = text.split()
            for start in range(0, len(words), size - overlap):
                end = min(start + size, len(words))
                identity = f"{path.name}:{sha(raw)}:{section_index}:{start}:{end}:{size}:{overlap}:{PARSER_VERSION}"
                chunks.append(Chunk(sha(identity), path.name, sha(raw), heading, path.stem.split('-')[0],
                                    start, end, " ".join(words[start:end])))
                if end == len(words):
                    break
    return chunks


def cosine(a, b):
    if len(a) != len(b) or not a or any(not math.isfinite(v) for v in (*a, *b)):
        raise ValueError("Finite vectors with identical nonempty dimensions required")
    norm_a, norm_b = math.sqrt(sum(v*v for v in a)), math.sqrt(sum(v*v for v in b))
    if not norm_a or not norm_b:
        return 0.0  # Explicit no-signal policy; no division by zero.
    return sum(x*y for x, y in zip(a, b)) / (norm_a * norm_b)


def toy_tokens(text):
    return [ALIASES.get(t, t) for t in tokens(text)]


def rank(chunks, query, *, mode="lexical", k=3, topic=None):
    if mode not in ("lexical", "vector", "hybrid") or type(k) is not int or k < 1:
        raise ValueError("Invalid retrieval mode or k")
    candidates = [c for c in chunks if topic is None or c.topic == topic]
    if not candidates or not tokens(query):
        return []
    if mode == "hybrid":
        lists = [rank(candidates, query, mode=m, k=len(candidates)) for m in ("lexical", "vector")]
        scores = Counter()
        for results in lists:
            for position, (chunk, _) in enumerate(results, start=1):
                scores[chunk.id] += 1 / (60 + position)
    elif mode == "lexical":
        # BM25 with k1=1.2, b=.75. No stop-word removal, stemming or language detection.
        docs = [Counter(tokens(c.text)) for c in candidates]
        avg = sum(sum(d.values()) for d in docs) / len(docs)
        scores = {}
        for chunk, doc in zip(candidates, docs):
            score = 0.0
            for term in set(tokens(query)):
                df = sum(term in d for d in docs)
                idf = math.log(1 + (len(docs) - df + .5) / (df + .5))
                tf = doc[term]
                score += idf * tf * 2.2 / (tf + 1.2 * (.25 + .75 * sum(doc.values()) / avg))
            scores[chunk.id] = score
    else:
        docs = [Counter(toy_tokens(c.text)) for c in candidates]
        vocabulary = sorted({t for d in docs for t in d})
        q = Counter(toy_tokens(query))
        query_vector = [q[t] for t in vocabulary]
        scores = {c.id: cosine(query_vector, [d[t] for t in vocabulary]) for c, d in zip(candidates, docs)}
    return sorted(((c, scores.get(c.id, 0)) for c in candidates if scores.get(c.id, 0) > 0),
                  key=lambda row: (-row[1], row[0].id))[:k]


def manifest(chunks, size, overlap):
    return {"parser": PARSER_VERSION, "tokenizer": TOKENIZER_VERSION,
            "toy_embedding": TOY_EMBEDDING_VERSION, "size_words": size, "overlap_words": overlap,
            "source_hashes": {c.document: c.source_sha256 for c in chunks},
            "chunks": [asdict(c) for c in chunks]}
