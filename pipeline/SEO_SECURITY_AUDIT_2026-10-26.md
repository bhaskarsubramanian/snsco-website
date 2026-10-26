# snsco.in security and SEO audit (26 Oct 2026)

Kept on the pipeline-config branch so it never ships with the website.

## Security (live site, checked with curl)
- HTTPS forced; http and www redirect to https://snsco.in (301).
- Headers present: HSTS (preload), CSP (script hash, no unsafe-inline scripts), X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy.
- /.env, /.git/config, /_drafts/*, /netlify.toml all return 404.
- Newsletter form uses Netlify honeypot; no http:// resources; no target=_blank without rel.
- Fixed (staged): the "I Do Not Agree" disclaimer button used an inline onclick that the CSP blocks, so it did nothing. Now a real link.
- Added (staged): /.well-known/security.txt.

## SEO (staged site, 920 pages)
- Every content page: title, meta description, canonical, one H1, Open Graph and Twitter card, BreadcrumbList; FAQPage on guides; BlogPosting / NewsArticle / Article; LegalService with address on location pages.
- Added (staged): lastmod on all sitemap URLs.
- Open: 800+ titles exceed about 60 characters and are cut in results (the "| S&S Co. Advocates & Solicitors" suffix). Optional trim.
- Open: hero photo is hot-linked from images.unsplash.com on every page (about 1800px). Self-hosting a resized WebP copy would improve load speed; it adds a little Netlify bandwidth.
- Noida: pages exist for Noida and Greater Noida. Four long-form Noida/Gautam Buddh Nagar articles queued (ids M to P in articles.json).

## Needs the owner (cannot be done from the repo)
- Google Business Profile for the Noida office (NAP identical to the site).
- Google Search Console and Bing Webmaster Tools: verify, submit sitemap.
- Any official profiles to add as sameAs in the Organization markup.
- Keep all copy within Bar Council of India Rule 36: no ratings, results claims, "best/top", or solicitation.
