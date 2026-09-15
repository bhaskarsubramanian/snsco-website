# Research Draft Queue

This branch (`research-draft`) is used ONLY to accumulate verified research candidates
between publish cycles. It is NEVER deployed — Netlify's production webhook only
listens to `main`, and no branch-deploy is configured for this branch.

## Files
- `legal-news-queue.json` — verified candidates for full Legal News articles
- `legal-updates-queue.json` — verified candidates for compact Legal Updates cards
- `blog-queue.json` — evergreen blog guide topics with confirmed factual outline

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
