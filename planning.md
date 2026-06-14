# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
 The domain I chose is food and dining. to-eat-asu is a simple rag application where students can gather quick opinions on dining, restaurants at
  ASU and near ASU, it is tedious to go through reviews every time, especially when you are hangry.There are almost no official channels to find  an opinion  you resonate with, with the fact that each google/yelp reviews are old or very vague, and going through reddit to find it is hard.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/ASU — good food places near campus | Student opinions on where to eat near ASU Tempe | https://www.reddit.com/r/ASU/comments/1m9oy5f/what_are_good_food_places_that_asu_students_have/ |
| 2 | r/ASU — vegetarian food quality | Vegetarian/vegan perspective on dining | https://www.reddit.com/r/ASU/comments/1r0z9ow/how_is_the_quality_of_food_for_vegetarian_at/ |
| 3 | r/ASU — best meal plan | Meal-plan tradeoffs (7 / 10 / 14 / unlimited) | https://www.reddit.com/r/ASU/comments/1mbriqo/best_meal_plan/ |
| 4 | r/ASU — coffee & study spots | Coffee/cafe recommendations | https://www.reddit.com/r/ASU/comments/1lxiglu/good_place_to_get_coffee_and_study/ |
| 5 | r/ASU — cheap lunch near campus | Budget food spots in/near campus | https://www.reddit.com/r/ASU/comments/1n7qw0f/any_cheap_food_spots_to_have_lunch_in_or_near_the/ |
| 6 | r/Tempe — lunch or breakfast spots | Off-campus / walkable Tempe options | https://www.reddit.com/r/Tempe/comments/1loouyy/anywhere_in_tempe_that_serves_lunch_or_breakfast/ |
| 7 | r/Tempe — food to try in Tempe | Broader Tempe restaurant recommendations | https://www.reddit.com/r/Tempe/comments/1rjc3op/food_to_try_in_tempe/ |
| 8 | Google reviews — ASU dining halls | Student star-reviews for Pitchforks, Hassayampa, Tooker, Barrett, Memorial Union | Google Maps (5 venues) |
| 9 | ASU dining hub — Dining Halls & Restaurants | Official on-campus venue lists (names, cuisine) | https://asu.mydininghub.com/en/tempe-campus/locations?cat=Dining+Halls |
| 10 | ASU dining hub — Convenience / P.O.D. Markets | Official convenience-market list | https://asu.mydininghub.com/en/tempe-campus/locations?cat=Convenience |

> The full 21-source list (all 13 Reddit threads, 5 Google review sets, 3 dining-hub pages) is in `README.md` → Document Sources.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** One item per chunk — a single Reddit comment, Google review, or dining-hub venue entry. No fixed character/token window. **307 chunks** total across all documents.

**Overlap:** None.

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 (sentence-transformers) — local, 384-dim, no API key.

**Top-k:** 5.

**Production tradeoff reflection:**
- Could swap to a larger/hosted model (bge-large, OpenAI text-embedding-3, Cohere) for better accuracy on domain slang / venue names.
  - Weigh: accuracy on domain text vs latency vs cost vs privacy (local keeps review text off third-party servers) vs context length (irrelevant here).
  - Multilingual would matter only if reviews weren't English-only.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | |What meal plan do students recommend for an incoming freshman, and why? |lean to 10 or 14 over unlimited (dining food quality is
  mixed); use the plan for dinner (priciest meal); M&G/meal-exchange covers snacks. (opinion synthesis — verified, dist 0.18)
| 2 |"What vegetarian food options are there at/near ASU, and are they good?" | |
| 3 | "Where can I get coffee on campus?"| Starbucks (multiple incl. MU), Rosie's at the MU, Einstein Bros, plus student study-spot picks.
  (options/spatial — good test for the #2+#3 routing)|
| 4 | "What do students think of Hassayampa dining hall?"| mixed-to-negative — food quality/feeling sick, coffee out, staff on phones; some
  praise the morning omelet crew + a veg-friendly 5★. (place-specific) |mixed-to-negative — food quality/feeling sick, coffee out, staff on phones; some
  praise the morning omelet crew + a veg-friendly 5★. (place-specific)
| 5 | "Where can I get matcha near ASU?"| honest refusal — system says it lacks student data on matcha, does not fabricate. (out-of-scope,
  distance-gate — verified refuses at 0.6+) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.Minority sources buried in a flat vector pool 

2.Out-of-scope questions inviting hallucination

3. Noisy / low-signal document

4. Context-prefix dilutes topical precision


---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
to-eat-asu — RAG pipeline

 ┌─ INGESTION ─────────────────────────────────────────────────┐
 │ raw/reddit/*.json   ─┐                                       │
 │ raw/Reviews.csv      ─┼─► build_corpus.py / process_dininghub│
 │ raw/dininghub/*.pdf  ─┘   (+ web sub-agent fallback)         │
 │              → documents/{reddit, reviews, dininghub}/       │
 └─────────────────────────────┬───────────────────────────────┘
                               ▼
   ① CHUNK    build_index.py — 1 comment | 1 review | 1 venue = 1 chunk
              (structural, no overlap)  →  { text, metadata }
              307 chunks  (258 reddit + 24 reviews + 25 dininghub)
                               ▼
   ② EMBED    sentence-transformers · all-MiniLM-L6-v2  →  384-dim vector
                               ▼
   ③ STORE    ChromaDB (cosine, persistent)  →  chroma_db/   [gitignored]
              record = vector + text + metadata
 ──────────────────────────────────────────────────────────────
   query time  (rag.py)
                               ▼
   ④ RETRIEVE embed query → top-k = 5 nearest  (+ optional metadata filter)
              distance gate: best > 0.60 → honest refusal (no LLM call)
                               ▼
   ⑤ GENERATE Groq · llama-3.3-70b-versatile
              answer ONLY from retrieved chunks + cite [n] sources
                               ▼
                        grounded answer + source list
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     Claude Code
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
 M3 Ingestion/chunking: give Claude the Chunking section + sample documents/ files → implement the per-item parsers (parse_reddit / parse_reviews /
  parse_dininghub) in build_index.py emitting {text, metadata}. Verify: chunk count = 307 + peek records.
  - M4 Embedding/retrieval: give Claude the Retrieval section → wire all-MiniLM-L6-v2 + ChromaDB persistent collection + retrieve() with top-k=5,
  metadata filter, query routing/per-source mixing. Verify: sample queries + distances.
  - M5 Generation/interface: give Claude the grounding rules → implement the Groq call in rag.py (system prompt: answer-only-from-context + [n] citations
  + distance-gate refusal) + CLI/Gradio. Verify: run the 5 eval questions.
**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
