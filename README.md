# Book Radar: setup

1. Create a new GitHub repository and upload everything in this folder,
   keeping the `.github/workflows` path exactly as it is.
2. Optional but recommended: get a free Google Books API key
   (Google Cloud Console > APIs & Services > enable "Books API" > Credentials).
   In your repo go to Settings > Secrets and variables > Actions and add it
   as a secret named GOOGLE_BOOKS_API_KEY.
3. Go to Settings > Pages, set the source to "Deploy from a branch",
   branch "main", folder "/ (root)". Your site appears at
   https://YOUR-USERNAME.github.io/YOUR-REPO/
4. Go to the Actions tab, pick "Update books" and press "Run workflow".
   It creates books.json. After that it runs by itself every day.

Until books.json exists, the site shows the built-in snapshot of 61 titles.

## Buy links and newsletter
Open index.html and fill in the CONFIG block near the top of the script:
- region: "uk" or "us" (picks Bookshop and Amazon storefronts)
- bookshopId: your Bookshop.org affiliate ID. It earns on ISBN links, which
  appear once books.json is live (the built-in snapshot has no ISBNs).
- amazonTag: your Amazon Associates tracking ID. It works on every Buy link.
- newsletterUsername: your Buttondown username, so the signup box works.
Until these are filled in, Buy links still work but earn nothing, and the
signup box tells visitors it isn't connected yet. Check each program's
current terms, and keep the disclosure line in the footer.

## Keeping awards up to date
Edit awards.json by hand when prizes are announced. Title and author must
match what Google Books returns, so check books.json if a badge doesn't show.

## Known limits
Google Books has patchy release dates and genres, so expect some odd entries.
Tune the SUBJECTS and LANGS lists at the top of fetch_books.py.
