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

<!-- webhook fix verification test: 2026-09-16T15:19:31Z -->
