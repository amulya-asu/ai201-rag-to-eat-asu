#!/usr/bin/env python3
"""
Build the to-eat-asu document corpus from saved raw files.

Inputs (you collect these into raw/):
    raw/reddit/*.json              saved Reddit thread .json (student voice)
    raw/Reviews - Sheet1.csv       Google dining-hall reviews (Review,Stars,Year,Place)

Outputs (clean text ready for chunking):
    documents/reddit/<slug>.md     one doc per thread (question + comments)
    documents/reviews/<place>.md   one doc per dining hall (its reviews)

No fetching, no keys — just cleans local files. Standard library only.
"""

import csv
import glob
import html
import json
import re
from pathlib import Path

REDDIT_RAW = Path("raw/reddit")
REVIEWS_CSV_CANDIDATES = ["raw/Reviews - Sheet1.csv", "raw/reviews/*.csv", "raw/*.csv"]
OUT_REDDIT = Path("documents/reddit")
OUT_REVIEWS = Path("documents/reviews")

# Reddit comment noise filters.
SKIP_AUTHORS = {"AutoModerator", "[deleted]", ""}
MIN_CHARS = 15
MIN_LETTERS = 12  # below this (URLs/emoji/punctuation removed) = not enough signal
# Whole-comment social pleasantries with no food content — dropped.
PLEASANTRY = re.compile(
    r"^(thanks?( (you|so much|a lot|for .*))?|ty|np|no problem|same( here)?|agreed|"
    r"exactly|this|yep|yup|fr+|ikr+)[.! ]*$",
    re.I,
)

# Canonical dining-hall names (fixes typos / trailing "Dining").
PLACE_CANON = {
    "hassyampa dining": "Hassayampa",
    "hassayampa dining": "Hassayampa",
    "hassayampa": "Hassayampa",
    "barrett dining": "Barrett",
    "barrett": "Barrett",
    "pitchforks": "Pitchforks",
    "memorial union": "Memorial Union",
    "tooker": "Tooker",
}

# Google "structured" boilerplate lines that carry no opinion — dropped.
BOILERPLATE = {
    "seating type", "indoor dining area", "outdoor seating",
    "parking space", "plenty of parking", "difficult to find parking",
    "somewhat difficult to find parking", "parking options",
    "free parking lot", "free street parking", "paid parking lot",
}


# ---------- Reddit ----------

def slug_from_permalink(permalink, fallback):
    m = re.search(r"/comments/([a-z0-9]+)/([^/?#]+)", permalink or "")
    if m:
        return f"{m.group(2)[:40].strip('_')}_{m.group(1)}"
    return fallback


def walk_comments(children, depth=0, out=None):
    if out is None:
        out = []
    for child in children:
        if child.get("kind") != "t1":
            continue
        data = child.get("data", {})
        out.append((depth, data))
        replies = data.get("replies")
        if isinstance(replies, dict):
            walk_comments(replies.get("data", {}).get("children", []), depth + 1, out)
    return out


def clean_reddit_file(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not (isinstance(payload, list) and len(payload) >= 2):
        return None
    post = payload[0]["data"]["children"][0]["data"]
    title = html.unescape(post.get("title", "Untitled").strip())
    selftext = html.unescape((post.get("selftext") or "").strip())
    permalink = "https://www.reddit.com" + post.get("permalink", "")
    sub = post.get("subreddit_name_prefixed", "")
    slug = slug_from_permalink(post.get("permalink"), path.stem)

    lines = [f"# {title}", "", f"Source: {permalink}", f"Type: Reddit thread ({sub})", ""]
    if selftext and selftext not in ("[removed]", "[deleted]"):
        lines += ["## Question / context", selftext, ""]
    lines.append("## Student responses")

    kept = 0
    for depth, c in walk_comments(payload[1].get("data", {}).get("children", [])):
        body = html.unescape((c.get("body") or "").strip())
        author = c.get("author") or ""
        score = c.get("score", 0)
        text_no_url = re.sub(r"https?://\S+", "", body).strip()
        letters = re.sub(r"[^A-Za-z]", "", text_no_url)  # URLs/emoji/punct stripped
        if (author in SKIP_AUTHORS or body in ("[deleted]", "[removed]")
                or len(body) < MIN_CHARS
                or len(letters) < MIN_LETTERS         # rule 1: too little text (e.g. bare link)
                or score < 0                          # rule 2: downvoted
                or PLEASANTRY.match(text_no_url)):    # rule 3: contentless pleasantry
            continue
        body = re.sub(r"\s*\n\s*", " ", body)
        lines.append(f"{'  ' * depth}- (▲{score}) {body}")
        kept += 1
    if kept == 0:
        lines.append("_(no substantive comments)_")
    return slug, "\n".join(lines) + "\n", kept


def build_reddit():
    OUT_REDDIT.mkdir(parents=True, exist_ok=True)
    files = sorted(REDDIT_RAW.glob("*.json"))
    docs, comments = 0, 0
    for path in files:
        try:
            result = clean_reddit_file(path)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {path.name}: {e}")
            continue
        if not result:
            continue
        slug, md, kept = result
        (OUT_REDDIT / f"{slug}.md").write_text(md, encoding="utf-8")
        docs += 1
        comments += kept
    print(f"Reddit:  {docs} docs, {comments} comments kept -> {OUT_REDDIT}/")


# ---------- Reviews ----------

def find_reviews_csv():
    for pat in REVIEWS_CSV_CANDIDATES:
        hits = glob.glob(pat)
        if hits:
            return hits[0]
    return None


def clean_review_text(text):
    kept = []
    for ln in html.unescape(text).splitlines():
        s = ln.strip()
        if not s or s.lower() in BOILERPLATE:
            continue
        kept.append(s)
    return " ".join(kept).strip()


def canon_place(raw):
    return PLACE_CANON.get(raw.strip().lower(), raw.strip())


def build_reviews():
    csv_path = find_reviews_csv()
    if not csv_path:
        print("Reviews: no CSV found (looked for raw/Reviews - Sheet1.csv).")
        return
    OUT_REVIEWS.mkdir(parents=True, exist_ok=True)
    by_place = {}
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = clean_review_text(row.get("Review", ""))
            if not text:
                continue
            place = canon_place(row.get("Place", "Unknown"))
            by_place.setdefault(place, []).append(
                {"text": text, "stars": row.get("Stars", "?"), "year": row.get("Year", "?")}
            )

    total = 0
    for place, reviews in sorted(by_place.items()):
        reviews.sort(key=lambda r: r["stars"])  # low ratings first
        lines = [
            f"# {place} — student reviews (Google)",
            "",
            "Source: Google reviews",
            "Proximity: on-campus",
            f"Place: {place}",
            "",
        ]
        for r in reviews:
            lines.append(f"- [★{r['stars']}, {r['year']}] {r['text']}")
        slug = re.sub(r"[^a-z0-9]+", "_", place.lower()).strip("_")
        (OUT_REVIEWS / f"{slug}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        total += len(reviews)
        print(f"  {place}: {len(reviews)} reviews")
    print(f"Reviews: {total} reviews across {len(by_place)} places -> {OUT_REVIEWS}/")


def main():
    build_reddit()
    build_reviews()
    print("\n[OK] Corpus built. Inspect documents/ before chunking.")


if __name__ == "__main__":
    main()
