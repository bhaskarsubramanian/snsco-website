import json, glob, os, re, html, subprocess, sys
from seotitle import seo_title
from datetime import date
DRAFTS = '../netlify-verify2/_drafts/' + sys.argv[1]
PUB_BLOG = sys.argv[2]
EXCL = [x['file'] for x in json.load(open('../netlify-verify2/verify/xv_excluded.json', encoding='utf-8'))]
EXCL.append('16-nhai-kurukshetra-expressway-delhi-hc-termination-payment.json')
EXCL.append('05-sc-ibc-section-62-limitation-nclat-pronouncement-certified-copy.json')
SKIPPED = []
EXCL += ['29-hari-dutta-sharma-cholamandalam-vehicle-repossession-sc.json', '05-hotel-alankar-bombay-hc-fssai-suspension-cannot-continue-indefinitely.json', '03-cci-agro-input-dealers-cartel-boycott-agrostar.json']
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
dtxt = lambda iso: '%d %s %s' % (int(iso[8:10]), MONTHS[int(iso[5:7]) - 1], iso[:4])
esc = lambda s: html.escape(s, quote=False)
rd = lambda f: open(f, encoding='utf-8', newline='').read()
def wr(f, s): open(f, 'w', encoding='utf-8', newline='').write(s)

NEWS_TPL = 'legal-news/aptel-piccadily-captive-power-status-26-percent-ownership-rule.html'
T_SLUG = 'aptel-piccadily-captive-power-status-26-percent-ownership-rule'
T_TITLE = "APTEL: Captive Power Status Needs Both 26% Ownership and 51% Self-Consumption, Each Met Independently"
T_DESC = "APTEL upholds denial of captive status to Piccadily after self-consumption fell short of 51%, holding ownership and consumption tests apply separately."
BLOG_TPL = 'blog/mutual-joint-wills-guide.html'

OUTLETS = {'livelaw.in': 'LiveLaw', 'livelawbiz.com': 'LiveLaw Biz', 'barandbench.com': 'Bar and Bench', 'verdictum.in': 'Verdictum',
 'scconline.com': 'SCC Online', 'indiankanoon.org': 'Indian Kanoon', 'taxscan.in': 'Taxscan', 'mondaq.com': 'Mondaq', 'lawbeat.in': 'LawBeat',
 'taxguru.in': 'TaxGuru', 'thelawgist.com': 'The Law Gist', 'business-standard.com': 'Business Standard', 'economictimes.indiatimes.com': 'Economic Times',
 'thehindu.com': 'The Hindu', 'hindustantimes.com': 'Hindustan Times', 'timesofindia.indiatimes.com': 'Times of India', 'indianexpress.com': 'Indian Express',
 'moneycontrol.com': 'Moneycontrol', 'mercomindia.com': 'Mercom India', 'pib.gov.in': 'PIB', 'indialawlive.com': 'India Law Live',
 'lawtrend.in': 'Law Trend', 'lawchakra.in': 'Law Chakra', 'verdictum.in': 'Verdictum', 'rawlaw.in': 'RawLaw', 'ibclaw.in': 'IBC Laws',
 'cyrilamarchandblogs.com': 'Cyril Amarchand Mangaldas blog', 'khaitanco.com': 'Khaitan & Co', 'azbpartners.com': 'AZB & Partners'}
def label(u):
    h = re.sub(r'^www\.', '', re.sub(r'^https?://', '', u).split('/')[0])
    for k, v in OUTLETS.items():
        if h == k or h.endswith('.' + k): return v
    return h
def links(urls):
    seen = []; out = []
    for u in urls:
        l = label(u)
        if l in seen: l = l + ' (2)'
        seen.append(l)
        out.append('<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (html.escape(u, quote=True), esc(l)))
    if len(out) == 1: return out[0]
    return ', '.join(out[:-1]) + ' and ' + out[-1]
def short_court(c):
    c = re.sub(r'\s*\(.*?\)', '', c).strip()
    c = c.replace('Supreme Court of India', 'Supreme Court')
    return c[:34]

PA_PAGE = {'Agricultural Industries': 'agricultural-industries', 'Arbitration & Dispute Resolution': 'arbitration-dispute-resolution', 'Banking & Finance': 'banking-finance',
 'Commercial Litigation': 'commercial-litigation', 'Consumer Protection': 'consumer-protection', 'Corporate Law & M&A': 'corporate-law-ma',
 'Employment & Labour': 'employment-labour', 'Family Law': 'family-law', 'Food Safety & FSSAI': 'food-safety-fssai', 'IBC & Insolvency': 'ibc-insolvency',
 'Infrastructure & PPP': 'infrastructure-ppp', 'Intellectual Property': 'intellectual-property', 'Power, Energy & Mining': 'power-energy-mining',
 'Property & Civil Litigation': 'property-civil-litigation', 'Real Estate & RERA': 'real-estate-rera', 'Tax Litigation': 'tax-litigation'}

NORM = {'Power Energy & Mining': 'Power, Energy & Mining', 'NRI Matters': 'NRI Legal Services', 'NRI Legal Services': 'NRI Legal Services'}
news_cards = []; blog_cards = []; sm_new = []; made = {'news': 0, 'blog': 0}
tpl = rd(NEWS_TPL)
for f in sorted(glob.glob(DRAFTS + '/news/*.json')):
    if any(f.replace(chr(92), '/').endswith(x) for x in EXCL): SKIPPED.append(('excluded', f)); continue
    if os.path.exists('legal-news/%s.html' % json.load(open(f, encoding='utf-8'))['slug']): SKIPPED.append(('exists', f)); continue
    d = json.load(open(f, encoding='utf-8')); slug = d['slug']; d['practice_area'] = NORM.get(d['practice_area'], d['practice_area'])
    t = tpl.replace(T_SLUG, slug).replace(T_TITLE, esc(d['title'])).replace(T_DESC, esc(d['meta_description']))
    _st = esc(seo_title(d))
    t = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % _st, t, count=1, flags=re.S)
    t = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")', lambda m: m.group(1) + html.escape(seo_title(d), quote=True) + m.group(2), t)
    t = t.replace('2026-09-17', d['decision_date']).replace('17 September 2026', dtxt(d['decision_date']))
    area = d['practice_area']
    t = t.replace('<span>/</span>Power, Energy &amp; Mining', '<span>/</span>' + esc(area).replace('&', '&amp;') if False else '<span>/</span>' + html.escape(area, quote=False))
    t = t.replace('<span>/</span>Power, Energy & Mining', '<span>/</span>' + esc(area))
    t = re.sub(r'(hero-tag">)Power, Energy (?:&amp;|&) Mining', lambda m: m.group(1) + html.escape(area, quote=False), t)
    mi = t.index('<main class="content-main">'); e = t.index('</main>')
    note = ('<div style="font-size:11.5px;color:var(--mu);letter-spacing:.3px;margin-bottom:28px;padding:14px 16px;background:#f7f5ef;border:1px solid rgba(0,35,70,.08);border-radius:2px;">\n'
            '      <strong>Source:</strong> Originally reported by %s. This article has been independently researched and rewritten in full by S&amp;S Co. Advocates &amp; Solicitors for informational purposes: it is not a reproduction of the original reports. Readers are encouraged to consult the original sources and the underlying judgement directly.\n    </div>') % links(d['sources'])
    body = '\n    '.join('<p>%s</p>' % esc(p) for p in d['body'])
    side = ('<div class="sidebar-card" style="margin-top:32px;">\n      <h4>Why It Matters</h4>\n      <p>%s</p>\n    </div>') % esc(d['why_it_matters'])
    t = t[:mi] + '<main class="content-main">\n    ' + note + '\n    ' + body + '\n    ' + side + '\n  ' + t[e:]
    # newsletter source value
    t = re.sub(r'(<input type="hidden" name="source" value=")[^"]*(")', lambda m: m.group(1) + '/legal-news/' + slug + '.html' + m.group(2), t)
    for bad in ('Piccadily', 'captive'):
        if bad.lower() in (d['title'] + ' ' + ' '.join(d['body'])).lower(): continue
        assert bad not in t[t.index('<title>'):], (slug, bad)
    wr('legal-news/%s.html' % slug, t); made['news'] += 1
    news_cards.append((slug, short_court(d['court']), dtxt(d['decision_date']), d['title'], d['card_summary'], d['card_tip'], d['decision_date']))
    sm_new.append(('legal-news', slug, d['decision_date']))

btpl = rd(BLOG_TPL)
for f in sorted(glob.glob(DRAFTS + '/blog/*.json')):
    if any(f.replace(chr(92), '/').endswith(x) for x in EXCL): SKIPPED.append(('excluded', f)); continue
    if os.path.exists('blog/%s.html' % json.load(open(f, encoding='utf-8'))['slug']): SKIPPED.append(('exists', f)); continue
    d = json.load(open(f, encoding='utf-8')); slug = d['slug']; d['practice_area'] = NORM.get(d['practice_area'], d['practice_area']); area = d['practice_area']
    page = PA_PAGE.get(area)
    head_end = btpl.index('<script type="application/ld+json">')
    head = btpl[:head_end]
    # head replacements
    head = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % esc(seo_title(d)), head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(d['meta_description'], quote=True) + m.group(2), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(d['meta_description'], quote=True) + m.group(2), head)
    head = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(d['meta_description'], quote=True) + m.group(2), head)
    head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")', lambda m: m.group(1) + html.escape(seo_title(d), quote=True) + m.group(2), head)
    head = head.replace('mutual-joint-wills-guide', slug).replace('2026-09-30', PUB_BLOG)
    head = re.sub(r'<meta property="og:image"[^>]*>\n?', '', head)
    head = head.replace('summary_large_image', 'summary')
    faq = [{"@type": "Question", "name": q['q'], "acceptedAnswer": {"@type": "Answer", "text": q['a']}} for q in d['faqs']]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://snsco.in/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://snsco.in/blog/"},
            {"@type": "ListItem", "position": 3, "name": d['title'], "item": "https://snsco.in/blog/%s.html" % slug}]},
        {"@type": "BlogPosting", "headline": d['title'], "description": d['meta_description'], "datePublished": PUB_BLOG,
         "author": {"@type": "Organization", "name": "S&S Co. Advocates & Solicitors"}, "publisher": {"@id": "https://snsco.in/#organization"},
         "mainEntityOfPage": "https://snsco.in/blog/%s.html" % slug},
        {"@type": "FAQPage", "mainEntity": faq}]}
    ld_s = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>'
    after = btpl[btpl.index('</script>', head_end) + len('</script>'):]
    # hero + main
    after = re.sub(r'(<div class="breadcrumb"[^>]*>\s*<a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span>).*?(\s*</div>)', lambda m: m.group(1) + esc(area) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(hero-tag">).*?(</span>)', lambda m: m.group(1) + esc(area) + ' · ' + dtxt(PUB_BLOG) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<h1 class="h1">).*?(</h1>)', lambda m: m.group(1) + esc(d['title']) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<p class="hdesc">).*?(</p>)', lambda m: m.group(1) + esc(d['meta_description']) + m.group(2), after, count=1, flags=re.S)
    mi = after.index('<main class="content-main">'); e = after.index('</main>')
    byline = '<p style="font-size:11px;color:var(--mu);letter-spacing:.5px;margin-bottom:28px;">By S&amp;S Co. Advocates &amp; Solicitors · Published %s · Informational content, not legal advice: see our <a href="/#contact">disclaimer</a></p>' % dtxt(PUB_BLOG)
    parts = [byline, '']
    for p in d['intro']: parts.append('<p>%s</p>' % esc(p))
    for s in d['sections']:
        parts.append('')
        parts.append('<h2>%s</h2>' % esc(s['heading']))
        for p in s['paragraphs']: parts.append('<p>%s</p>' % esc(p))
    parts.append('')
    parts.append('<h2>Frequently Asked Questions</h2>')
    for q in d['faqs']:
        parts.append('<div class="faq-item">\n      <h3>%s</h3>\n      <p>%s</p>\n    </div>' % (esc(q['q']), esc(q['a'])))
    parts.append('<h2>References &amp; Further Reading</h2>')
    parts.append('<p style="font-size:12.5px;color:var(--mu);">The provisions and rulings below were relied on for this guide. The position can change with amendments and later decisions, so check the current text and the latest case law before acting on any of it.</p>')
    parts.append('<ol style="font-size:12.5px;line-height:2;color:#4a5568;font-weight:300;padding-left:20px;margin-bottom:20px;">')
    for i, r in enumerate(d['references'], 1): parts.append('  <li id="ref-%d">%s</li>' % (i, esc(r)))
    parts.append('</ol>')
    main = '<main class="content-main">\n    ' + '\n    '.join(parts) + '\n  '
    after = after[:mi] + main + after[e:]
    # related practice area link
    rel = '<li><a href="/practice-areas/%s.html">%s</a></li>' % (PA_PAGE[area], esc(area)) if area in PA_PAGE else ''
    after = re.sub(r'(<h4>Related Practice Area</h4>\s*<ul class="related-list">)\s*.*?(\s*<li><a href="/practice-areas/">All Practice Areas</a></li>)', lambda m: m.group(1) + ('\n        ' + rel if rel else '') + m.group(2), after, count=1, flags=re.S)
    # more from blog: leave generic All Articles only
    after = re.sub(r'(<h4>More From the Blog</h4>\s*<ul class="related-list">).*?(\s*<li><a href="/blog/">All Articles</a></li>)', lambda m: m.group(1) + m.group(2), after, count=1, flags=re.S)
    after = re.sub(r'(<input type="hidden" name="source" value=")[^"]*(")', lambda m: m.group(1) + '/blog/' + slug + '.html' + m.group(2), after)
    t = head + ld_s + after
    seg = t[t.index('<main'):t.index('</main>')]
    assert '—' not in seg, slug
    wr('blog/%s.html' % slug, t); made['blog'] += 1
    blog_cards.append((slug, area, d['title'], d['meta_description']))
    sm_new.append(('blog', slug, PUB_BLOG))

# hubs
NL = chr(10)
nc = []
for slug, badge, dt, title, summ, tip, iso in news_cards:
    nc.append('      <a class="uc" href="/legal-news/%s.html" style="display:block;text-decoration:none;color:inherit;">' % slug + NL
        + '        <div class="uc-bar"></div>' + NL
        + '        <div class="uc-meta"><span class="uc-badge">%s</span><span class="uc-date">%s</span></div>' % (esc(badge), dt) + NL
        + '        <h4 class="uc-title">%s</h4>' % esc(title) + NL
        + '        <p class="uc-body">%s</p>' % esc(summ) + NL
        + '        <div class="uc-tip"><span>Why It Matters:</span> %s</div>' % esc(tip) + NL
        + '      </a>')
bc = []
for slug, area, title, desc in blog_cards:
    bc.append('      <a class="prc" href="/blog/%s.html" style="text-align:left;">' % slug + NL
        + '        <span class="pr-num">%s</span>' % dtxt(PUB_BLOG) + NL
        + '        <span class="pr-icon">\U0001F4F0</span>' + NL
        + '        <h3 class="pr-name">%s</h3>' % esc(title) + NL
        + '        <p class="pr-desc">%s</p>' % esc(desc) + NL
        + '        <span class="pr-link">Read More \u2192</span>' + NL
        + '      </a>')
hh = rd('legal-news/index.html')
kk = hh.rindex('</a>', 0, hh.index('</main>')) + 4
wr('legal-news/index.html', hh[:kk] + NL + NL.join(nc) + hh[kk:])
bh = rd('blog/index.html')
ii = bh.index('id="lfgrid"'); ii = bh.index('>', ii) + 1
wr('blog/index.html', bh[:ii] + NL + NL.join(bc) + bh[ii:])
sm = rd('sitemap.xml')
ref = re.search(r'<url><loc>https://snsco\.in/blog/[a-z0-9-]+\.html</loc>[^\n]*</url>', sm).group(0)
for sec, slug, iso in sm_new:
    new = re.sub(r'https://snsco\.in/[a-z-]+/[a-z0-9-]+\.html', 'https://snsco.in/%s/%s.html' % (sec, slug), ref)
    new = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>%s</lastmod>' % iso, new)
    k = sm.index('</urlset>'); sm = sm[:k] + '  ' + new + '\n' + sm[k:]
wr('sitemap.xml', sm)
print(made, 'skipped', SKIPPED)
