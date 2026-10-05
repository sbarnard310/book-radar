# Book Radar: notes for Claude

A hand-picked list of new and upcoming books, live at https://sbarnard310.github.io/book-radar/ (GitHub repo sbarnard310/book-radar). The owner is non-technical: give numbered steps with exact button names, and do the technical work for them. README.md explains the files and every field in books.json; keep it in step when fields change.

This site is separate from The Starred Bill (in /Users/sambarnard/starred-bill). Don't mix their files, notes or to-do lists.

## How it's built
- `index.html` is the whole website: layout, styles and script in one file. It loads `books.json` in the browser and sorts books into "Coming soon" and "Out now" by date. The CONFIG block near the top of the script holds the shop region, Bookshop.org and Amazon affiliate IDs and the Buttondown newsletter username (empty until the owner signs up).
- `books.json` is the list (`updated`, `sources`, `books`), one book per line. It's hand-picked: the owner edits it on GitHub (pencil icon › Commit changes) or asks Claude.
- `add_covers.py` finds missing covers (Apple Books search, then Open Library). The `Add covers` workflow (`.github/workflows/add-covers.yml`) runs it whenever books.json changes, every Monday, or by hand from the Actions tab, and commits the covers itself. So run `git pull --rebase` before starting work and before every push.
- Visitors' wishlists are kept in their own browser (localStorage). There are no accounts and no visit statistics yet.
- Publishing: GitHub Pages serves the `main` branch as it is (no build step). Commit and push to `main`; the site updates in a minute or two. The `gh` CLI is at `/usr/local/bin/gh` (add it to PATH).

## Working on it
- Preview: the "site" entry in `.claude/launch.json` serves this folder on port 8766, viewed in the browser pane at http://localhost:8766. (Port 8799 is The Starred Bill's, 8765 another site's.)
- Check changes in light and dark mode and at phone width (no sideways scroll).
- Commit messages: a short imperative subject.
- Before this folder existed, the site was worked on in a temporary scratch folder (Claude's scratch-workspaces, "scratch-2026-10-02-4c5fd6"). Everything from it was copied here on 5 Oct 2026, and this folder is the one to use.

## Chats
Book Radar's chats are filed in the Code tab sidebar under sections starting "Book Radar · ". Start new chats with this folder (book-radar) as the working folder.
