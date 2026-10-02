"""
Book Radar data pipeline.

Pulls recent and upcoming books from the Google Books API, merges in a
hand-curated awards file, and writes books.json for the website to read.
Standard library only. Run it on a schedule (daily is plenty).

    python fetch_books.py                 # uses GOOGLE_BOOKS_API_KEY if set
    GOOGLE_BOOKS_API_KEY=xxx python fetch_books.py

awards.json (you maintain this) looks like:
    [{"title": "Taiwan Travelogue", "author": "Yáng Shuāng-zǐ",
      "award": "International Booker 2026 winner"}]
"""
import json
import os
import time
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date

API = "https://www.googleapis.com/books/v1/volumes"
KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")  # optional, raises your quota

# Google Books subject searches. Add or remove to change coverage.
SUBJECTS = {
    "Literary fiction": "subject:literary",
    "Fantasy": "subject:fantasy",
    "Romance": "subject:romance",
    "Thriller & mystery": "subject:thriller OR subject:mystery",
    "Historical fiction": "subject:historical fiction",
    "Science fiction": "subject:science fiction",
    "Horror": "subject:horror",
    "Young adult": "subject:young adult fiction",
    "Memoir & biography": "subject:biography",
    "History & politics": "subject:history OR subject:political science",
    "Science & nature": "subject:science OR subject:nature",
}
# Languages to request. Each is a separate pass, which is how you widen
# coverage beyond English.
LANGS = ["en", "es", "fr", "de", "pt"]
EASY_GENRES = {"Romance", "Thriller & mystery"}
NONFICTION = {"Memoir & biography", "History & politics", "Science & nature"}
# Refuse to replace books.json with a suspiciously small result.
MIN_BOOKS = 50


def get(params):
    if KEY:
        params["key"] = KEY
    url = f"{API}?{urllib.parse.urlencode(params)}"
    # Google Books answers bursts with 429/503; back off and retry.
    for wait in (2, 5, 15, None):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 503) or wait is None:
                raise
            time.sleep(wait)


def normalise(item, genre):
    v = item.get("volumeInfo", {})
    published = v.get("publishedDate", "")
    # Google returns YYYY, YYYY-MM or YYYY-MM-DD. Keep month precision as-is.
    if len(published) not in (7, 10):
        return None
    pages = v.get("pageCount") or 0
    cover = (v.get("imageLinks") or {}).get("thumbnail", "").replace("http://", "https://")
    return {
        "t": v.get("title", "").strip(),
        "a": ", ".join(v.get("authors", [])) or "Unknown",
        "g": genre,
        "d": published,
        "lang": v.get("language", ""),
        "pages": pages,
        "n": (v.get("description") or "")[:200],
        "isbn": next((i["identifier"] for i in v.get("industryIdentifiers", [])
                      if i["type"] == "ISBN_13"), ""),
        # Easy read is a rule of thumb, not a reading level.
        "easy": genre in EASY_GENRES or (0 < pages <= 250),
        "type": "Nonfiction" if genre in NONFICTION else "Fiction",
        "cover": cover,
        # Many new or upcoming books have no ratings yet; 0 means none.
        "rating": v.get("averageRating") or 0,
        "ratings": v.get("ratingsCount") or 0,
    }


def fetch_all():
    year = date.today().year
    seen, books = set(), []
    stats, years = Counter(), Counter()
    for lang in LANGS:
        for genre, q in SUBJECTS.items():
            for start in (0, 40):  # two pages of 40 per query
                try:
                    data = get({
                        "q": q, "orderBy": "newest", "printType": "books",
                        "langRestrict": lang, "maxResults": 40, "startIndex": start,
                    })
                except (urllib.error.URLError, TimeoutError) as err:
                    print(f"Skipping {genre}/{lang}/{start}: {err}", file=sys.stderr)
                    stats["failed requests"] += 1
                    continue
                items = data.get("items", [])
                stats["items returned"] += len(items)
                for item in items:
                    years[(item.get("volumeInfo", {}).get("publishedDate") or "none")[:4]] += 1
                    b = normalise(item, genre)
                    if not b or not b["t"]:
                        stats["dropped: year-only or missing date"] += 1
                        continue
                    # Keep this year and next, which covers "coming soon".
                    if not b["d"][:4] in (str(year), str(year + 1)):
                        stats["dropped: outside this year and next"] += 1
                        continue
                    key = (b["t"].lower(), b["a"].lower())
                    if key in seen:
                        stats["dropped: duplicate"] += 1
                        continue
                    seen.add(key)
                    books.append(b)
                    stats["kept"] += 1
                time.sleep(1)  # be polite to the API
    for k, v in stats.items():
        print(f"{k}: {v}")
    print("Publication years returned:", ", ".join(f"{y} x{n}" for y, n in years.most_common(12)))
    return books


def merge_awards(books, path="awards.json"):
    if not os.path.exists(path):
        return books
    with open(path, encoding="utf-8") as f:
        awards = {(a["title"].lower(), a["author"].lower()): a["award"]
                  for a in json.load(f)}
    for b in books:
        award = awards.get((b["t"].lower(), b["a"].lower()))
        if award:
            b["award"] = award
    return books


if __name__ == "__main__":
    books = merge_awards(fetch_all())
    if len(books) < MIN_BOOKS:
        # Don't overwrite the last good books.json with a near-empty result.
        sys.exit(f"Only {len(books)} books fetched (minimum {MIN_BOOKS}); keeping the existing books.json")
    books.sort(key=lambda b: b["d"])
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump({"updated": date.today().isoformat(), "books": books},
                  f, ensure_ascii=False, indent=1)
    print(f"Wrote {len(books)} books to books.json")
