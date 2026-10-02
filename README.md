# Book Radar

A hand-picked list of new and upcoming books, published with GitHub Pages at
https://sbarnard310.github.io/book-radar/

## Files
- `index.html`: the website.
- `books.json`: the book list. Edit this to add, change or remove books.
- `add_covers.py`: finds cover images for books that don't have one.
- `.github/workflows/add-covers.yml`: runs `add_covers.py` whenever
  `books.json` changes, and every Monday for covers that appear later.

## Editing the list
`books.json` has one book per line. Change `updated` to today's date
whenever you edit it; the footer shows it. Each book looks like this:

    {"title": "Partita", "author": "Barbara Kingsolver", "genre": "Literary fiction",
     "date": "2026-10-06", "tags": [], "award": "", "note": "", "translatedFrom": "", "cover": ""}

- `date`: `YYYY-MM-DD`, or `YYYY-MM` if only the month is known, or `null`
  for books already out with no date listed. The site moves books from
  "Coming soon" to "Out now" by itself when the date passes.
- `genre`: one of Literary fiction, Fantasy, Romance, Thriller & mystery,
  Historical fiction, Science fiction, Horror, Young adult, Children's,
  Memoir & biography, History & politics, Science & nature.
- `tags`: any of `award`, `easy`, `debut`, `translated`, `bestseller`.
  These drive the Collection filters.
- `award`: prize text shown as a badge, e.g. "Booker Prize 2026 shortlist".
- `note`: one or two sentences shown under the title. Can be empty.
- `translatedFrom`: original language for translated books, else empty.
- `cover`: leave empty. The Add covers workflow fills it in. Books with no
  cover show a coloured placeholder until one is found.

The easiest way to edit is on GitHub: open `books.json`, press the pencil
icon, make your changes and press "Commit changes". The site updates
within a minute or two, and covers follow shortly after.

## Buy links and newsletter
Fill in the CONFIG block near the top of the script in `index.html`:
- `region`: "uk" or "us" (picks Bookshop and Amazon storefronts)
- `bookshopId`: your Bookshop.org affiliate ID
- `amazonTag`: your Amazon Associates tracking ID
- `newsletterUsername`: your Buttondown username, so the signup box works

Until these are filled in, Buy links still work but earn nothing, and the
signup box tells visitors it isn't connected yet. Check each program's
current terms, and keep the disclosure line in the footer.
