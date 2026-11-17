"""Build /articles/ pages (hub + one page per draft) from the blog template. Run in the site worktree.
usage: python build_articles.py <drafts-dir> <publish-date YYYY-MM-DD> [exclude-substring ...]"""
import json, glob, os, re, html, sys
from seotitle import seo_title
DRAFTS = sys.argv[1]; PUB = sys.argv[2]; EXCL = sys.argv[3:]
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
dtxt = lambda iso: '%d %s %s' % (int(iso[8:10]), MONTHS[int(iso[5:7]) - 1], iso[:4])
esc = lambda s: html.escape(s, quote=False)
q = lambda s: html.escape(s, quote=True)
rd = lambda f: open(f, encoding='utf-8', newline='').read()
def wr(f, s): os.makedirs(os.path.dirname(f) or '.', exist_ok=True); open(f, 'w', encoding='utf-8', newline='').write(s)
BLOG_TPL = 'blog/mutual-joint-wills-guide.html'
TPL_SLUG = 'mutual-joint-wills-guide'
PA_PAGE = {'Agricultural Industries': 'agricultural-industries', 'Arbitration & Dispute Resolution': 'arbitration-dispute-resolution', 'Banking & Finance': 'banking-finance',
 'Commercial Litigation': 'commercial-litigation', 'Consumer Protection': 'consumer-protection', 'Corporate Law & M&A': 'corporate-law-ma',
 'Employment & Labour': 'employment-labour', 'Family Law': 'family-law', 'Food Safety & FSSAI': 'food-safety-fssai', 'IBC & Insolvency': 'ibc-insolvency',
 'Infrastructure & PPP': 'infrastructure-ppp', 'Intellectual Property': 'intellectual-property', 'Power, Energy & Mining': 'power-energy-mining',
 'Property & Civil Litigation': 'property-civil-litigation', 'Real Estate & RERA': 'real-estate-rera', 'Tax Litigation': 'tax-litigation'}
btpl = rd(BLOG_TPL)
made = []
files = [f for f in sorted(glob.glob(DRAFTS + '/*.json')) if not any(x in f for x in EXCL)]
for f in files:
    d = json.load(open(f, encoding='utf-8')); slug = d['slug']; area = d['practice_area']; page = PA_PAGE.get(area)
    AUTH = d.get('authors') or [{'name': d['author'], 'role': d['author_role']}]
    url = 'https://snsco.in/articles/%s.html' % slug
    head_end = btpl.index('<script type="application/ld+json">')
    head = btpl[:head_end]
    head = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % esc(seo_title(d)), head, flags=re.S)
    for pat in (r'(<meta name="description" content=")[^"]*(")', r'(<meta property="og:description" content=")[^"]*(")', r'(<meta name="twitter:description" content=")[^"]*(")'):
        head = re.sub(pat, lambda m: m.group(1) + q(d['meta_description']) + m.group(2), head)
    head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")', lambda m: m.group(1) + q(seo_title(d)) + m.group(2), head)
    head = head.replace('/blog/' + TPL_SLUG, '/articles/' + slug).replace(TPL_SLUG, slug).replace('2026-09-30', PUB)
    head = re.sub(r'<meta property="og:image"[^>]*>\n?', '', head).replace('summary_large_image', 'summary')
    faq = [{"@type": "Question", "name": x['q'], "acceptedAnswer": {"@type": "Answer", "text": x['a']}} for x in d['faqs']]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://snsco.in/"},
            {"@type": "ListItem", "position": 2, "name": "Articles", "item": "https://snsco.in/articles/"},
            {"@type": "ListItem", "position": 3, "name": d['title'], "item": url}]},
        {"@type": "Article", "headline": d['title'], "description": d['meta_description'], "datePublished": PUB, "dateModified": PUB,
         "author": [{"@type": "Person", "name": a['name'], "jobTitle": re.sub(r",? *S&S Co\..*$", "", a['role']).strip(), "worksFor": {"@id": "https://snsco.in/#organization"}} for a in AUTH],
         "publisher": {"@id": "https://snsco.in/#organization"}, "mainEntityOfPage": url, "articleSection": area},
        {"@type": "FAQPage", "mainEntity": faq}]}
    ld_s = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>'
    after = btpl[btpl.index('</script>', head_end) + len('</script>'):]
    after = re.sub(r'(<div class="breadcrumb"[^>]*>\s*<a href="/">Home</a><span>/</span>)<a href="/blog/">Blog</a><span>/</span>.*?(\s*</div>)',
                   lambda m: m.group(1) + '<a href="/articles/">Articles</a><span>/</span>' + esc(area) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(hero-tag">).*?(</span>)', lambda m: m.group(1) + 'Article · ' + esc(area) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<h1 class="h1">).*?(</h1>)', lambda m: m.group(1) + esc(d['title']) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<p class="hdesc">).*?(</p>)', lambda m: m.group(1) + esc(d['subtitle']) + m.group(2), after, count=1, flags=re.S)
    mi = after.index('<main class="content-main">'); e = after.index('</main>')
    def _nm(a): return '<strong style="color:var(--nv);">%s</strong>, %s' % (esc(a['name']), esc(a['role']))
    by_html = ' and '.join(_nm(a) for a in AUTH)
    byline = ('<p style="font-size:12px;color:var(--mu);letter-spacing:.4px;margin-bottom:6px;line-height:1.7;">By %s</p>'
              '<p style="font-size:11px;color:var(--mu);letter-spacing:.5px;margin-bottom:26px;">Published %s · Law stated as on %s · Informational content, not legal advice: see our <a href="/#contact">disclaimer</a></p>'
              % (by_html, dtxt(PUB), dtxt(d['as_on_date'])))
    parts = [byline, '<p style="font-size:17px;line-height:1.7;color:var(--nv);font-weight:400;margin-bottom:26px;">%s</p>' % esc(d['standfirst'])]
    kp = ''.join('<li>%s</li>' % esc(x) for x in d['key_points'])
    parts.append('<div style="background:#f7f5ef;border:1px solid rgba(0,35,70,.08);border-left:3px solid var(--gd);padding:18px 22px;margin-bottom:30px;">'
                 '<h4 style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--gd);margin-bottom:10px;">Key points</h4>'
                 '<ul style="padding-left:18px;font-size:14px;line-height:1.8;color:#4a5568;">%s</ul></div>' % kp)
    toc = ''.join('<li><a href="#s%d">%s</a></li>' % (i, esc(s['heading'])) for i, s in enumerate(d['sections'], 1))
    parts.append('<div role="navigation" aria-label="In this article" style="margin-bottom:34px;"><h4 style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--mu);margin-bottom:8px;">In this article</h4>'
                 '<ol style="padding-left:20px;font-size:13.5px;line-height:1.9;">%s</ol></div>' % toc)
    for i, s in enumerate(d['sections'], 1):
        parts.append('<h2 id="s%d">%s</h2>' % (i, esc(s['heading'])))
        for p in s['paragraphs']: parts.append('<p>%s</p>' % esc(p))
    for p in d['conclusion']: parts.append('<p>%s</p>' % esc(p))
    parts.append('<h2>Frequently Asked Questions</h2>')
    for x in d['faqs']: parts.append('<div class="faq-item">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>' % (esc(x['q']), esc(x['a'])))
    parts.append('<h2>References &amp; Further Reading</h2>')
    parts.append('<p style="font-size:12.5px;color:var(--mu);">The provisions, rulings and official documents below were relied on for this article, which states the law as on %s. The position can change with amendments, rules and later decisions, so check the current text before acting on any of it.</p>' % dtxt(d['as_on_date']))
    parts.append('<ol style="font-size:12.5px;line-height:2;color:#4a5568;font-weight:300;padding-left:20px;margin-bottom:20px;">')
    for i, r in enumerate(d['references'], 1): parts.append('  <li id="ref-%d">%s</li>' % (i, esc(r)))
    parts.append('</ol>')
    if d.get('related_pages'):
        parts.append('<h2>Related reading on this site</h2><ul style="font-size:14px;line-height:2;padding-left:20px;">' + ''.join('<li><a href="%s">%s</a></li>' % (q(p), esc(os.path.basename(p)[:-5].replace('-', ' ').capitalize())) for p in d['related_pages']) + '</ul>')
    main = '<main class="content-main">\n    ' + '\n    '.join(parts) + '\n  '
    after = after[:mi] + main + after[e:]
    rel = '<li><a href="/practice-areas/%s.html">%s</a></li>' % (page, esc(area)) if page else ''
    after = re.sub(r'(<h4>Related Practice Area</h4>\s*<ul class="related-list">)\s*.*?(\s*<li><a href="/practice-areas/">All Practice Areas</a></li>)', lambda m: m.group(1) + ('\n        ' + rel if rel else '') + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<h4>More From the Blog</h4>\s*<ul class="related-list">).*?(\s*<li><a href="/blog/">All Articles</a></li>)', lambda m: m.group(1).replace('More From the Blog', 'More Articles') + '\n        <li><a href="/articles/">All Articles</a></li>', after, count=1, flags=re.S)
    after = re.sub(r'(<input type="hidden" name="source" value=")[^"]*(")', lambda m: m.group(1) + '/articles/' + slug + '.html' + m.group(2), after)
    t = head + ld_s + after
    assert '—' not in t[t.index('<main'):t.index('</main>')], slug
    wr('articles/%s.html' % slug, t)
    made.append((slug, area, d['title'], d['meta_description'], d['as_on_date'], d))

# ---- hub ----
h = rd('blog/index.html')
h = re.sub(r'<title>.*?</title>', '<title>Legal Articles | S&amp;S Co. Advocates &amp; Solicitors</title>', h, count=1, flags=re.S)
dsc = 'Long-form legal analysis by the partners and team of S&S Co. on contemporary Indian legal issues in arbitration, insolvency, data protection, intellectual property, criminal law, real estate and succession.'
for pat in (r'(<meta name="description" content=")[^"]*(")', r'(<meta property="og:description" content=")[^"]*(")', r'(<meta name="twitter:description" content=")[^"]*(")'):
    h = re.sub(pat, lambda m: m.group(1) + q(dsc) + m.group(2), h)
h = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")', lambda m: m.group(1) + 'Articles | S&amp;S Co.' + m.group(2), h)
h = h.replace('https://snsco.in/blog/', 'https://snsco.in/articles/')
h = re.sub(r'(<div class="breadcrumb"[^>]*>\s*<a href="/">Home</a><span>/</span>)Blog', lambda m: m.group(1) + 'Articles', h, count=1)
h = h.replace('<span class="hero-tag">Legal Insights</span>', '<span class="hero-tag">Long-form analysis</span>')
h = re.sub(r'<h1 class="h1">.*?</h1>', '<h1 class="h1">The S&amp;S Co. <em>Articles</em></h1>', h, count=1, flags=re.S)
h = re.sub(r'<p class="hdesc">.*?</p>', '<p class="hdesc">Long-form analysis of contemporary Indian legal issues by the partners and team of S&amp;S Co. Each article names its authors, states the law as on its date and lists its sources.</p>', h, count=1, flags=re.S)
cards = []
for slug, area, title, desc, asd, d in sorted(made, key=lambda x: x[4], reverse=True):
    cards.append('      <a class="prc" href="/articles/%s.html" style="text-align:left;">\n        <span class="pr-num">%s</span>\n        <span class="pr-icon">\U0001F4D6</span>\n        <h3 class="pr-name">%s</h3>\n        <p class="pr-desc">%s</p>\n        <span class="pr-link">Read the article →</span>\n      </a>' % (slug, esc(area), esc(title), esc(d['standfirst'])))
i = h.index('<div class="pr-con">') + len('<div class="pr-con">')
j = h.index('</section>', i)
h = h[:i] + '\n    <div class="pr-grid blog-grid">\n' + '\n'.join(cards) + '\n    </div>\n  </div>\n' + h[j:]
h = re.sub(r'<script[^>]*listing\.js[^>]*></script>\s*', '', h)
h = re.sub(r'<link[^>]*listing\.css[^>]*>\s*', '', h)
h = re.sub(r'(<input type="hidden" name="source" value=")[^"]*(")', lambda m: m.group(1) + '/articles/' + m.group(2), h)
h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: m.group(0).replace('/blog/', '/articles/').replace('"name": "Blog"', '"name": "Articles"'), h, flags=re.S)
wr('articles/index.html', h)
# ---- sitemap ----
sm = rd('sitemap.xml')
ref = re.search(r'<url><loc>https://snsco\.in/blog/[a-z0-9-]+\.html</loc>[^\n]*</url>', sm).group(0)
def add(loc, lm):
    global sm
    if loc in sm: return
    new = re.sub(r'<loc>[^<]*</loc>', '<loc>%s</loc>' % loc, ref); new = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>%s</lastmod>' % lm, new)
    k = sm.index('</urlset>'); sm = sm[:k] + '  ' + new + '\n' + sm[k:]
add('https://snsco.in/articles/', PUB)
for slug, *_ in made: add('https://snsco.in/articles/%s.html' % slug, PUB)
wr('sitemap.xml', sm)
# ---- search index ----
idx = json.load(open('assets/search-index.json', encoding='utf-8'))
idx = [e for e in idx if not e['u'].startswith('/articles/')]
for slug, area, title, desc, asd, d in made:
    body = ' '.join(p for s in d['sections'] for p in s['paragraphs'])
    idx.append({'u': '/articles/%s.html' % slug, 't': title, 'd': desc, 'c': area, 'k': 'article', 'dt': PUB, 's': body[:220]})
json.dump(idx, open('assets/search-index.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, separators=(',', ':'))
print('articles built', len(made))
