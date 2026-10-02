"""
Book Radar cover finder.

Fills in "cover" for every book in books.json that doesn't have one yet.
Tries Apple Books first (the earliest English-language edition, which is
the original rather than a translation), then Open Library. Books it can't
find keep an empty cover and get another try next run. Standard library only.

    python add_covers.py
"""
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "BookRadar/1.0 (cover lookup)"}
# Apple Books subtitles that still mean "the same book".
SAME_BOOK = r" (a novel|a thriller|a memoir|a shadowhunters novel|book \d+)$"


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s)).strip()


def get_json(url):
    for wait in (5, 20, None):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError) as err:
            if wait is None:
                print(f"  giving up on {url[:80]}: {err}", file=sys.stderr)
                return {}
            time.sleep(wait)


def looks_english(text):
    words = re.findall(r"[a-z]+", re.sub("<[^>]+>", " ", text or "").lower())
    return sum(w in ("the", "and", "of", "her", "his", "to", "is", "with") for w in words) >= 6


def apple_cover(title, author, last):
    short = norm(title.split(":")[0])
    for country in ("us", "gb"):
        q = urllib.parse.urlencode({"term": f"{title.split(':')[0]} {author}",
                                    "entity": "ebook", "limit": 50, "country": country})
        results = get_json("https://itunes.apple.com/search?" + q).get("results", [])
        time.sleep(3)  # Apple allows about 20 searches a minute
        matches = [r for r in results
                   if last in norm(r.get("artistName", ""))
                   and (norm(r.get("trackName", "")) == short
                        or re.match(re.escape(short) + SAME_BOOK, norm(r.get("trackName", ""))))
                   and looks_english(r.get("description"))
                   and r.get("releaseDate", "") >= "2024"]
        if matches:
            first = min(matches, key=lambda r: r["releaseDate"])
            return re.sub(r"/\d+x\d+bb\.jpg$", "/300x300bb.jpg", first["artworkUrl100"])
    return ""


def openlibrary_cover(title, author, last):
    q = urllib.parse.urlencode({"title": title, "author": last, "limit": 20,
                                "fields": "title,author_name,cover_i"})
    docs = get_json("https://openlibrary.org/search.json?" + q).get("docs", [])
    time.sleep(1)
    for d in docs:
        if (norm(d.get("title", "")) == norm(title) and d.get("cover_i")
                and any(last in norm(a) for a in d.get("author_name", []))):
            return f"https://covers.openlibrary.org/b/id/{d['cover_i']}-M.jpg"
    return ""


def save(data, path="books.json"):
    # One book per line keeps the file easy to read, edit and diff.
    head = "".join(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n"
                   for k, v in data.items() if k != "books")
    books = ",\n".join("  " + json.dumps(b, ensure_ascii=False) for b in data["books"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("{\n" + head + ' "books": [\n' + books + "\n ]\n}\n")


if __name__ == "__main__":
    with open("books.json", encoding="utf-8") as f:
        data = json.load(f)
    missing = [b for b in data["books"] if not b.get("cover")]
    print(f"{len(missing)} books need a cover")
    found = 0
    for b in missing:
        last = norm(b["author"]).split()[-1]
        b["cover"] = (apple_cover(b["title"], b["author"], last)
                      or openlibrary_cover(b["title"], b["author"], last))
        found += bool(b["cover"])
        print(f"  {'found' if b['cover'] else 'none yet'}: {b['title']} by {b['author']}")
    save(data)
    print(f"Added {found} covers")
