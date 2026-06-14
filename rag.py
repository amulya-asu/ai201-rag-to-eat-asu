#!/usr/bin/env python3
"""
to-eat-asu — answer questions from the student-review vector store (M3+).

Pipeline (stages 4-5):
    question
      -> RETRIEVE : per-source vector search + place routing + upvote tie-break,
                    merged with a per-source cap so no single source dominates
      -> GATE     : if nothing is close enough, refuse honestly (no LLM call)
      -> GENERATE : Groq llama-3.3-70b answers ONLY from retrieved chunks, cited

Why per-source mixing: a single flat top-k let the 258 conversational Reddit
chunks crowd out the 25 factual dining-hub venue chunks (e.g. "Starbucks"
ranked 7th for a coffee query). Querying each source pool and capping how many
each contributes guarantees venues/reviews get a seat.

Usage:
    python rag.py "where can I get coffee on campus?"   # one-shot
    python rag.py                                        # interactive loop
"""

import os
import sys

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

sys.stdout.reconfigure(encoding="utf-8")  # let Windows console print ★ / emoji

CHROMA_PATH = "chroma_db"
COLLECTION = "to_eat_asu"
MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

TOP_K = 6                 # chunks sent to the LLM
PER_SOURCE_FETCH = 8      # candidates pulled from each source pool
SOURCE_CAP = 3            # max chunks any one source may contribute to the final set
MAX_DISTANCE = 0.60       # best match beyond this -> honest refusal (the "matcha" case)
UPVOTE_MAX_BONUS = 0.03   # tiny nudge: high-upvote Reddit comments win ties

# Query mentions one of these -> also pull that place's reviews (routing).
KNOWN_PLACES = {
    "hassayampa": "Hassayampa", "pitchforks": "Pitchforks", "barrett": "Barrett",
    "tooker": "Tooker", "memorial union": "Memorial Union", " mu ": "Memorial Union",
}

SYSTEM_PROMPT = (
    "You are to-eat-asu, a guide to food and dining at and near ASU's Tempe campus. "
    "Answer ONLY using the student reviews, Reddit comments, and official venue entries "
    "in the CONTEXT below. Synthesize what students actually say — note agreement and "
    "disagreement. Cite every claim with its source number like [1], [2]. "
    "If the context does not contain enough to answer, say so plainly and do not use "
    "outside knowledge. Do NOT infer or assume a venue offers a specific dish or drink "
    "unless a source explicitly names that item; if the user asks about something none "
    "of the sources mention (e.g. a specific beverage), say you don't have student data "
    "on it rather than guessing. Never invent places, prices, or hours; for hours, tell "
    "the user to check the official ASU dining hub link. Keep answers concise and practical."
)


def get_collection():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION, embedding_function=ef)


def source_tag(meta):
    if meta["source"] == "review":
        stars = meta["stars"]
        star_txt = f"{stars}★" if stars >= 0 else "n/a"
        return f"{meta['place']} Google review, {star_txt}"
    if meta["source"] == "dininghub":
        return f"ASU dining hub: {meta['place']} ({meta.get('category', '')})"
    return f"{meta['subreddit']} comment, ▲{meta['score']}"


def _upvote_bonus(meta):
    """High-upvote Reddit comments get a small rank nudge (tie-breaker, not override)."""
    if meta["source"] == "reddit" and meta.get("score", 0) > 0:
        return min(meta["score"], 20) / 20 * UPVOTE_MAX_BONUS
    return 0.0


def retrieve(col, question, k=TOP_K):
    """Per-source retrieval + place routing, merged with a per-source cap.

    Returns (hits, ok). ok=False means nothing cleared the distance gate.
    Each hit = {text, meta, dist, rank}; rank = dist - upvote bonus (lower = better).
    """
    cand = {}

    def add(res):
        for cid, doc, meta, dist in zip(
            res["ids"][0], res["documents"][0],
            res["metadatas"][0], res["distances"][0],
        ):
            if cid not in cand:
                cand[cid] = {"text": doc, "meta": meta, "dist": dist,
                             "rank": dist - _upvote_bonus(meta)}

    # #3 per-source mixing: query each source pool separately
    for src in ("reddit", "review", "dininghub"):
        add(col.query(query_texts=[question], n_results=PER_SOURCE_FETCH,
                      where={"source": src}))

    # #2 routing: if the question names a known place, pull that place's chunks too
    q_pad = f" {question.lower()} "
    for key, place in KNOWN_PLACES.items():
        if key in q_pad:
            add(col.query(query_texts=[question], n_results=4, where={"place": place}))
            break

    ranked = sorted(cand.values(), key=lambda c: c["rank"])
    if not ranked or ranked[0]["dist"] > MAX_DISTANCE:
        return ranked[:1], False  # distance gate -> refuse

    # merge with per-source cap so no single source dominates the final set
    final, counts = [], {}
    for c in ranked:
        src = c["meta"]["source"]
        if counts.get(src, 0) >= SOURCE_CAP:
            continue
        final.append(c)
        counts[src] = counts.get(src, 0) + 1
        if len(final) >= k:
            break
    return final, True


def build_context(hits):
    return "\n\n".join(
        f"[{i}] ({source_tag(h['meta'])})\n{h['text']}" for i, h in enumerate(hits, 1)
    )


def answer(question):
    col = get_collection()
    hits, ok = retrieve(col, question)

    if not ok:
        best = hits[0]["dist"] if hits else 1.0
        print(
            f"\nI don't have student data close enough to answer that "
            f"(best match {best:.3f} > {MAX_DISTANCE}).\n"
            "Try a different food/dining question about ASU Tempe."
        )
        return

    context = build_context(hits)
    load_dotenv()
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
        ],
    )
    print("\n" + resp.choices[0].message.content.strip())

    print("\nSources:")
    for i, h in enumerate(hits, 1):
        print(f"  [{i}] {source_tag(h['meta'])} (dist {h['dist']:.3f}) — {h['meta']['url']}")


def main():
    if len(sys.argv) > 1:
        answer(" ".join(sys.argv[1:]))
        return
    print("to-eat-asu — ask about ASU Tempe food/dining (Ctrl+C to quit)")
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q:
            answer(q)


if __name__ == "__main__":
    main()
