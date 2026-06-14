#!/usr/bin/env python3
"""
to-eat-asu — answer questions from the student-review vector store (M3+).

Pipeline (stages 4-5):
    question
      -> RETRIEVE : embed query, vector search top-k in ChromaDB (+ optional filter)
      -> GATE     : if nothing is close enough, refuse honestly (no LLM call)
      -> GENERATE : Groq llama-3.3-70b answers ONLY from retrieved chunks, cited

Usage:
    python rag.py "vegetarian food near ASU"     # one-shot
    python rag.py                                # interactive loop
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

TOP_K = 5
# Cosine distance above this = no good match -> honest refusal (the "matcha" case).
MAX_DISTANCE = 0.60

SYSTEM_PROMPT = (
    "You are to-eat-asu, a guide to food and dining at and near ASU's Tempe campus. "
    "Answer ONLY using the student reviews and Reddit comments in the CONTEXT below. "
    "Synthesize what students actually say — note agreement and disagreement. "
    "Cite every claim with its source number like [1], [2]. "
    "If the context does not contain enough to answer, say so plainly and do not use "
    "outside knowledge. Never invent places, prices, or hours; for hours, tell the user "
    "to check the official ASU dining hub link. Keep answers concise and practical."
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


def retrieve(col, question, k=TOP_K, where=None):
    res = col.query(query_texts=[question], n_results=k, where=where)
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({"text": doc, "meta": meta, "dist": dist})
    return hits


def build_context(hits):
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[{i}] ({source_tag(h['meta'])})\n{h['text']}")
    return "\n\n".join(blocks)


def answer(question, where=None):
    col = get_collection()
    hits = retrieve(col, question, where=where)

    if not hits or hits[0]["dist"] > MAX_DISTANCE:
        best = hits[0]["dist"] if hits else 1.0
        print(
            f"\nI don't have student data close enough to answer that "
            f"(best match distance {best:.3f} > {MAX_DISTANCE}).\n"
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
        url = h["meta"]["url"]
        print(f"  [{i}] {source_tag(h['meta'])} (dist {h['dist']:.3f}) — {url}")


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
