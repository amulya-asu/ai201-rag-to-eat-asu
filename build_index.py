#!/usr/bin/env python3
"""
Build the to-eat-asu vector store from the cleaned corpus.

Pipeline (stages 1-3 of the RAG diagram):
    documents/*.md
      -> CHUNK   : structural / per-item (1 reddit comment or 1 review = 1 chunk)
      -> EMBED   : all-MiniLM-L6-v2 (sentence-transformers, local, 384-dim)
      -> STORE   : ChromaDB persistent collection at chroma_db/

Each chunk is stored as:
    document  = "[context] opinion text"   (what gets embedded + shown as the source)
    metadata  = {source, place, proximity, stars, score, year, url, title}

Re-running rebuilds the collection from scratch (no duplicates).
Standard library + sentence-transformers + chromadb only.
"""

import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

DOCS_REDDIT = Path("documents/reddit")
DOCS_REVIEWS = Path("documents/reviews")
DOCS_DININGHUB = Path("documents/dininghub")
CHROMA_PATH = "chroma_db"
COLLECTION = "to_eat_asu"
MODEL_NAME = "all-MiniLM-L6-v2"

# Comment line:  "- (▲9) body"  (may be indented for nested replies)
RE_COMMENT = re.compile(r"^\s*-\s*\(▲(-?\d+)\)\s*(.+)$")
# Review line:   "- [★3, 2026] text"
RE_REVIEW = re.compile(r"^\s*-\s*\[★([^,]+),\s*([^\]]+)\]\s*(.+)$")
# Dininghub line: "- Pitchforks (on-campus) — description"  (optional "(unverified)")
RE_VENUE = re.compile(r"^-\s*(.+?)\s*\(([^)]+)\)\s*(?:\(unverified\)\s*)?—\s*(.+)$")


def _header_value(lines, key):
    for ln in lines:
        if ln.startswith(key):
            return ln[len(key):].strip()
    return ""


def parse_reddit(path):
    """One chunk per substantive comment. Embedded text is prefixed with the
    thread title so terse comments ('Take 10...') still carry their topic."""
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    url = _header_value(lines, "Source:")
    sub_raw = _header_value(lines, "Type:")  # "Reddit thread (r/ASU)"
    m = re.search(r"\((r/[^)]+)\)", sub_raw)
    subreddit = m.group(1) if m else ""

    chunks = []
    for ln in lines:
        m = RE_COMMENT.match(ln)
        if not m:
            continue
        score, body = int(m.group(1)), m.group(2).strip()
        chunks.append({
            "document": f"[{title}] {body}",
            "metadata": {
                "source": "reddit", "subreddit": subreddit, "url": url,
                "title": title, "place": "unknown", "proximity": "unknown",
                "stars": -1, "score": score, "year": "unknown",
            },
        })
    return chunks


def parse_reviews(path):
    """One chunk per Google review. Embedded text is prefixed with the place."""
    lines = path.read_text(encoding="utf-8").splitlines()
    place = _header_value(lines, "Place:") or path.stem
    proximity = _header_value(lines, "Proximity:") or "unknown"

    chunks = []
    for ln in lines:
        m = RE_REVIEW.match(ln)
        if not m:
            continue
        stars_raw, year, text = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        try:
            stars = int(stars_raw)
        except ValueError:
            stars = -1
        chunks.append({
            "document": f"[{place}] {text}",
            "metadata": {
                "source": "review", "subreddit": "", "url": "Google reviews",
                "title": place, "place": place, "proximity": proximity,
                "stars": stars, "score": -1, "year": year,
            },
        })
    return chunks


def parse_dininghub(path):
    """One chunk per venue. Official 'what options exist' baseline, used for
    spatial-aware answers. Embedded text is the venue name + description."""
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    category = title.split("—")[-1].split("(")[0].strip() if "—" in title else path.stem
    url = _header_value(lines, "Source:")

    chunks = []
    for ln in lines:
        m = RE_VENUE.match(ln)
        if not m:
            continue
        name, proximity, desc = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        verified = "(unverified)" not in ln
        chunks.append({
            "document": f"[{name}] {desc}",
            "metadata": {
                "source": "dininghub", "subreddit": "", "url": url,
                "title": name, "place": name, "proximity": proximity,
                "stars": -1, "score": -1, "year": "", "category": category,
                "verified": verified,
            },
        })
    return chunks


def collect_chunks():
    chunks = []
    for p in sorted(DOCS_REDDIT.glob("*.md")):
        chunks += parse_reddit(p)
    for p in sorted(DOCS_REVIEWS.glob("*.md")):
        chunks += parse_reviews(p)
    for p in sorted(DOCS_DININGHUB.glob("*.txt")):
        chunks += parse_dininghub(p)
    return chunks


def build():
    chunks = collect_chunks()
    n_reddit = sum(1 for c in chunks if c["metadata"]["source"] == "reddit")
    n_review = sum(1 for c in chunks if c["metadata"]["source"] == "review")
    n_dining = sum(1 for c in chunks if c["metadata"]["source"] == "dininghub")
    print(f"Chunked: {len(chunks)} total  "
          f"({n_reddit} reddit comments, {n_review} reviews, {n_dining} dininghub venues)")

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION)  # fresh rebuild, no dupes
    except Exception:
        pass
    col = client.create_collection(
        COLLECTION, embedding_function=ef, metadata={"hnsw:space": "cosine"}
    )

    col.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=[c["document"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Stored:  {col.count()} vectors in '{COLLECTION}' -> {CHROMA_PATH}/")
    return col


# ---------- verification ----------

def verify(col):
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    print(f"1) Vector count in collection: {col.count()}")

    peek = col.peek(limit=2)
    print("\n2) Sample stored records (id / embedding dim / metadata):")
    for i, cid in enumerate(peek["ids"]):
        dim = len(peek["embeddings"][i])
        print(f"   {cid}: dim={dim}  meta={peek['metadatas'][i]}")
        print(f"      doc: {peek['documents'][i][:80]}...")

    print("\n3) Sample semantic queries (top-3, lower distance = closer):")
    for q in ["vegetarian food near ASU",
              "best meal plan for a freshman",
              "matcha latte"]:
        res = col.query(query_texts=[q], n_results=3)
        print(f"\n   Q: {q!r}")
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            tag = meta["place"] if meta["source"] == "review" else meta["subreddit"]
            print(f"      [{dist:.3f}] ({meta['source']}/{tag}) {doc[:70]}...")

    print("\n4) Metadata filter check (only Hassayampa reviews):")
    res = col.query(
        query_texts=["how is the food"], n_results=3,
        where={"place": "Hassayampa"},
    )
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        print(f"      ({meta['stars']} stars, {meta['year']}) {doc[:70]}...")


if __name__ == "__main__":
    verify(build())
    print("\n[OK] Index built. Re-run anytime to rebuild from documents/.")
