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
 The domain I chose is food and dining.to-eat-asu is simple rag application where students can gather quick opinions on dining, restaurants at
  ASU and near ASU, it is tedious to go through reviews every time, especially when you are hangry.There are almost no official channels to find about an opinion  you resonate with, which is why I choose this.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

Sources fall into three tiers: **student voice** (Reddit), **dining-hall reviews** (Google), and **official baseline** (ASU dining hub, used for place names/metadata only).

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/ASU — good food places near campus | Reddit thread | https://www.reddit.com/r/ASU/comments/1m9oy5f/what_are_good_food_places_that_asu_students_have/ |
| 2 | r/ASU — food places on Tempe campus | Reddit thread | https://www.reddit.com/r/ASU/comments/1mvz5dr/what_are_some_food_places_to_eat_on_the_tempe/ |
| 3 | r/ASU — coffee & study spots | Reddit thread | https://www.reddit.com/r/ASU/comments/1lxiglu/good_place_to_get_coffee_and_study/ |
| 4 | r/ASU — vegetarian food quality | Reddit thread | https://www.reddit.com/r/ASU/comments/1r0z9ow/how_is_the_quality_of_food_for_vegetarian_at/ |
| 5 | r/ASU — dining halls with good food | Reddit thread | https://www.reddit.com/r/ASU/comments/1oovggk/do_yall_know_any_dining_halls_with_good_food_or/ |
| 6 | r/ASU — best meal plan | Reddit thread | https://www.reddit.com/r/ASU/comments/1mbriqo/best_meal_plan/ |
| 7 | r/ASU — meal plan for incoming student | Reddit thread | https://www.reddit.com/r/ASU/comments/1eqmtsf/what_meal_plan_would_you_recommend_as_an_incoming/ |
| 8 | r/ASU — cheap lunch near campus | Reddit thread | https://www.reddit.com/r/ASU/comments/1n7qw0f/any_cheap_food_spots_to_have_lunch_in_or_near_the/ |
| 9 | r/ASU — restaurants to explore | Reddit thread | https://www.reddit.com/r/ASU/comments/1nea45i/restaurants_to_explore/ |
| 10 | r/Tempe — lunch or breakfast spots | Reddit thread | https://www.reddit.com/r/Tempe/comments/1loouyy/anywhere_in_tempe_that_serves_lunch_or_breakfast/ |
| 11 | r/Tempe — restaurants with delivery | Reddit thread | https://www.reddit.com/r/Tempe/comments/1nnadb8/tempe_restaurants_with_bakedin_delivery/ |
| 12 | r/Tempe — restaurants to explore | Reddit thread | https://www.reddit.com/r/Tempe/comments/1ne9aj6/restaurants_to_explore/ |
| 13 | r/Tempe — food to try in Tempe | Reddit thread | https://www.reddit.com/r/Tempe/comments/1rjc3op/food_to_try_in_tempe/ |
| 14 | Pitchforks Dining Hall — reviews | Google reviews | Google Maps — Pitchforks Dining Hall, ASU Tempe |
| 15 | Hassayampa Dining Hall — reviews | Google reviews | Google Maps — Hassayampa Dining Hall, ASU Tempe |
| 16 | Tooker House Dining — reviews | Google reviews | Google Maps — Tooker House Dining, ASU Tempe |
| 17 | Barrett (Mark Jacobs) Dining — reviews | Google reviews | Google Maps — Barrett Dining, ASU Tempe |
| 18 | Memorial Union — reviews | Google reviews | Google Maps — Memorial Union, ASU Tempe |
| 19 | ASU dining hub — Restaurants | Official site (metadata) | https://asu.mydininghub.com/en/tempe-campus/locations?cat=Restaurants |
| 20 | ASU dining hub — Convenience | Official site (metadata) | https://asu.mydininghub.com/en/tempe-campus/locations?cat=Convenience |
| 21 | ASU dining hub — Dining Halls | Official site (metadata) | https://asu.mydininghub.com/en/tempe-campus/locations?cat=Dining+Halls |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

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

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

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

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
