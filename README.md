# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The domain I chose is food and dining. **to-eat-asu** is a simple RAG application where students can gather quick opinions on dining and restaurants at and near ASU Tempe. It is tedious to go through reviews every time, especially when you're hangry, and there are almost no official channels to find an opinion you resonate with — Google/Yelp reviews are old or vague, and digging through Reddit to find the answer is hard.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One item per chunk — a single Reddit comment, Google review, or dining-hub venue entry. No fixed character/token window. **305 chunks** total (256 Reddit comments + 24 Google reviews + 25 dining-hub venues).

**Overlap:** None — each item is already self-contained, so there is no mid-idea boundary that overlap would need to protect.

**Preprocessing:** `build_corpus.py` parses the Reddit JSON and reviews CSV, unescapes HTML entities, and drops AutoModerator / deleted / downvoted / pure-reaction / bare-link comments. The dining-hub PDFs were image-only (no text layer), so their venue lists were reconstructed from the web.

**Reasoning:** Chunking was based on how the data is presented — each Reddit comment is one complete idea, and the same holds for each review and each dining-hall venue. The data already arrives as discrete items, which is why each item is its own chunk; a fixed-size window would risk merging unrelated opinions (two different restaurants) into one chunk.
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Embedding model:** all-MiniLM-L6-v2 (sentence-transformers) — local, 384-dim, no API key.

**Top-k:** 5.

**Production tradeoff reflection:**
- If cost needs to be taken to picture, a larger model (OpenAI text embedding-3) for better accuracy on domain, venues, and spatial awareness along with tool calling would be helpful.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
answer only from the provided context, synthesize agreement/disagreement, cite every claim [n], say so if context is
  insufficient (no outside knowledge), don't infer a venue offers an item unless explicitly named, never invent places/prices/hours (hours → official
  link). refer to SYSTEM_PROMPT at rag.py
 - Structural choices: distance gate (>0.60 → refuse before calling the LLM), per-source mixing so context is balanced, temperature=0.2.
**How source attribution is surfaced in the response:**
 each answer lists numbered sources = type + place/subreddit + stars/upvotes + distance + URL; cited at thread/place level, not username
  (privacy).

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What meal plan do students recommend for an incoming freshman? | Lean toward 10/14 over unlimited (mixed dining quality); use the plan for dinner; M&G covers snacks | Synthesized the 10 vs 14 vs unlimited tradeoffs across several students; noted no strong consensus | Relevant | Accurate |
| 2 | What vegetarian food options are there at/near ASU? | Limited; Subway, Choolah, Qdoba/Engrained, some dining-hall options; quality mediocre | Named vegetarian options at Subway/Choolah and dining halls (Barrett, Hassayampa, Pitchforks) with quality caveats | Relevant | Accurate |
| 3 | Where can I get coffee on campus? | Starbucks (multiple), Rosie's, Einstein, + student picks | Returned Starbucks and Rosie's at the MU (surfaced only after adding per-source mixing) | Relevant | Accurate |
| 4 | What do students think of Hassayampa dining hall? | Mixed 1★–5★: food-quality complaints + omelet/vegetarian praise | Balanced summary spanning 1★ complaints to 5★ omelet/sandwich praise (after a routing fix; was one-sided before) | Relevant | Accurate |
| 5 | Where can I get matcha near ASU? | Honest refusal — no matcha in the data | Declined: "I don't have student data on matcha"; did not fabricate | Relevant (gate) | Accurate (refusal) |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "What do students think of Hassayampa dining hall?" (before the fix)

**What the system returned:** A one-sided negative answer — it reported only a single 1★ review ("employees often sit on their phones") and stated there were no other comments, even though the corpus contains 5★ reviews praising the omelet station and vegetarian options.

**Root cause (retrieval stage):** Per-source mixing plus distance ranking pulled in only the one Hassayampa review whose wording best matched the question; the positive reviews ranked lower and were crowded out by Tooker/Reddit chunks, so the LLM never saw them. Generation was faithful — but to a biased context.

**What you would change to fix it (done):** Added place-aware routing — when a query names a known venue, the retriever guarantees that venue's full review spread (praise and complaints) into the context before filling the remaining slots. After the fix, the answer spans 1★ to 5★.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Scoping the domain to three query types and committing to "simple RAG is enough" in planning.md kept tool-calling and live-data features out of scope, and the per-item chunking decision fell directly out of the document shape I described in the plan. That meant the ingestion side matched the spec with very little rework.

**One way your implementation diverged from the spec, and why:** The plan assumed plain dense top-k retrieval, but testing showed it buried the dining-hub venue chunks and produced one-sided place answers, so I added per-source mixing and place-aware routing that weren't in the original spec. I also switched the interface from Gradio to Streamlit, because gradio>=6.9 requires a huggingface-hub version that conflicts with the one sentence-transformers needs.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My chunking strategy and sample files from `documents/`.
- *What it produced:* The per-item parsers (`parse_reddit` / `parse_reviews` / `parse_dininghub`) in `build_index.py` that emit `{text, metadata}`.
- *What I changed or overrode:* I directed structural per-item chunking (not fixed-size) and the cleaning rules, and overrode length-based filtering — short comments like "The Dhaba if you like Indian" are real recommendations, not noise.

**Instance 2**

- *What I gave the AI:* The symptom that the Hassayampa answer was one-sidedly negative.
- *What it produced:* A diagnosis pointing at the retrieval routing, plus a fix that guarantees the full review spread for a named place.
- *What I changed or overrode:* I verified the balanced output myself and confirmed the change didn't regress the out-of-scope refusal (the matcha question still declines).
