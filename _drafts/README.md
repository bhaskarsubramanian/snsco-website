# Research Draft Queue

This branch (`research-draft`) is used ONLY to accumulate verified research candidates
between publish cycles. It is NEVER deployed — Netlify's production webhook only
listens to `main`, and no branch-deploy is configured for this branch.

## Files
- `legal-news-queue.json` — verified candidates for full Legal News articles
- `legal-updates-queue.json` — verified candidates for compact Legal Updates cards
- `blog-queue.json` — evergreen blog guide topics with confirmed factual outline
- `practice-areas/` — DRAFT practice-area page(s) not yet added to the live 15-area
  set on `main`. Each file is a fully rendered page ready to be moved into the live
  `practice-areas/` directory (and wired into its nav/footer/sitemap/index listings,
  the same way `family-law.html` was) on a future publish cycle. As of 2026-09-28
  this holds two drafts: `wills-estate-planning-succession.html` and
  `nri-legal-services.html`, requested ahead of the news/updates/blog queue items
  for those two areas so publishing can add all three (practice page + articles)
  together. Their internal links to specific blog/legal-news article pages will
  only resolve once those queued items are actually built — check the queue for
  matching ids before publishing.

## Workflow
- **Daily curation routine** (runs ~3am IST daily): researches, verifies (2+ independent
  sources per item, no invented citations/facts), de-duplicates against what's already
  published on `main` AND what's already queued here, appends new verified items to
  these files, commits and pushes to `research-draft` ONLY.
- **Publish routine** (runs every 3 days, ~2am IST): reads these queue files, picks
  enough verified items to reach the 10-per-section target, builds the actual site
  pages on `main`, pushes `main` (the one deploy), then removes the consumed items
  from these queue files and pushes the drained queue back to `research-draft`.

Never write directly to any live site file (legal-news/, legal-updates/index.html,
blog/, sitemap.xml) from this branch — only touch files inside `_drafts/`.

## Open feedback for the publish routine / site owner (2026-10-10)

Raised by the site owner in chat; logged here rather than acted on directly, since
both items require touching files outside `_drafts/` (and the newsletter item
touches `main`'s shared header/nav template), which is outside this routine's
remit:

1. **Article prose should not read as LLM-written.** When the publish routine
   drafts full article text from a queue item's `holding_summary` /
   `why_it_matters` / `key_points`, review the prose for grammar, punctuation and
   generic AI phrasing (e.g. em-dash overuse, "it's important to note",
   "landscape", "robust", stock transition phrases) before pushing to `main`.
   The queue notes themselves are research summaries, not final copy, and
   weren't written to be published verbatim.
2. **Newsletter subscription should be more prominent.** Currently it's a
   mid-page band on the homepage (`#newsletter`) plus a footer link to
   `/newsletter/` — the site owner wants it more visible, e.g. a persistent
   nav-bar tab, not just a scroll-down section. This means editing the shared
   header/nav partial used across every page on `main`, so it belongs to
   whichever session/routine next works on `main`'s templates, not to a
   research-draft-only session.

<!-- webhook fix verification test: 2026-09-16T15:19:31Z -->
