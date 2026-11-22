"""Search-visibility pass for snsco.in (22 Nov 2026). Idempotent; run from the site worktree.
  python seo_boost.py flatten   # sitemap index -> single flat sitemap.xml (builders append to the flat file)
  python seo_boost.py all       # fonts, share images, related links, latest/cluster blocks, feed, redirects, split sitemaps
  python seo_boost.py <step>    # fonts | og | related | latest | feed | split
Order after a content build: flatten, build, fix_search_index.py, sort_hubs.py, a11y_fix.py, seo_boost.py all, validate_site.py.
BCI Rule 36: every block added here is a plain list of titles of existing educational pages. No calls to action, no claims."""
import glob, re, json, html, os, sys, collections
BS = chr(92)
rd = lambda f: open(f, encoding='utf-8', newline='').read()
def wr(f, s): open(f, 'w', encoding='utf-8', newline='').write(s)
esc = lambda s: html.escape(s, quote=False)
ALL = sorted(f.replace(BS, '/') for f in glob.glob('**/*.html', recursive=True))
TYPE = {'blog': 'blog', 'legal-news': 'news', 'articles': 'article'}
TLABEL = {'blog': 'Guides', 'news': 'Legal News', 'article': 'Articles'}
AREA_PAGE = {'Agricultural Industries': 'agricultural-industries', 'Arbitration & Dispute Resolution': 'arbitration-dispute-resolution', 'Banking & Finance': 'banking-finance',
 'Commercial Litigation': 'commercial-litigation', 'Consumer Protection': 'consumer-protection', 'Corporate Law & M&A': 'corporate-law-ma', 'Employment & Labour': 'employment-labour',
 'Family Law': 'family-law', 'Wills & Succession': 'family-law', 'Food Safety & FSSAI': 'food-safety-fssai', 'IBC & Insolvency': 'ibc-insolvency', 'Infrastructure & PPP': 'infrastructure-ppp',
 'Intellectual Property': 'intellectual-property', 'Power, Energy & Mining': 'power-energy-mining', 'Property & Civil Litigation': 'property-civil-litigation',
 'Real Estate & RERA': 'real-estate-rera', 'Tax Litigation': 'tax-litigation', 'NRI Legal Services': 'nri-cross-border'}
PAGE_AREAS = collections.defaultdict(list)
for a, p in AREA_PAGE.items(): PAGE_AREAS[p].append(a)
PAGE_LABEL = {'family-law': 'Family Law, Wills and Succession', 'nri-cross-border': 'NRI and Cross-Border Matters'}

def load_index():
    idx = json.load(open('assets/search-index.json', encoding='utf-8'))
    return [e for e in idx if e['u'].split('/')[1] in TYPE]

# ---------------------------------------------------------------- fonts
FONT_MARK = '/* SELF-HOSTED FONTS (22 Nov 2026) */'
def step_fonts():
    src = rd('../fonts_face.css')
    rng = {}
    for m in re.finditer(r'/\* (latin(?:-ext)?) \*/\s*@font-face \{(.*?)\}', src, re.S):
        b = m.group(2); fam = re.search(r"font-family: '([^']+)'", b).group(1); st = re.search(r'font-style: (\w+)', b).group(1)
        f = re.search(r'/assets/fonts/(\S+?)\)', b).group(1); ur = re.search(r'unicode-range: ([^;]+);', b).group(1)
        rng[(fam, st, m.group(1))] = (f, ur)
    decl = {('Fraunces', 'normal'): '300 700', ('Fraunces', 'italic'): '300 400', ('Jost', 'normal'): '300 700'}
    css = rd('assets/css/main.css')
    if FONT_MARK not in css:
        out = [FONT_MARK]
        for (fam, st), w in decl.items():
            for sub in ('latin-ext', 'latin'):
                f, ur = rng[(fam, st, sub)]
                out.append("@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;src:url(/assets/fonts/%s) format('woff2');unicode-range:%s;}" % (fam, st, w, f, ur))
        css += '\n' + '\n'.join(out) + '\n'; wr('assets/css/main.css', css)
    pre = ''.join('<link rel="preload" href="/assets/fonts/%s" as="font" type="font/woff2" crossorigin/>\n' % rng[k][0] for k in (('Fraunces', 'normal', 'latin'), ('Jost', 'normal', 'latin')))
    n = 0
    for f in ALL:
        s = rd(f); o = s
        s = re.sub(r'<link[^>]*fonts\.g(?:oogleapis|static)\.com[^>]*>\s*', '', s)
        if 'href="/assets/fonts/' not in s:
            s = re.sub(r'(<link rel="stylesheet" href="/assets/css/main\.css)', lambda m: pre + m.group(1), s, count=1)
        s = s.replace('main.css?v8', 'main.css?v9')
        if s != o: wr(f, s); n += 1
    print('fonts: pages changed', n)

# ---------------------------------------------------------------- share images
def step_og():
    C = load_index(); byurl = {e['u']: e for e in C}
    cnt = collections.defaultdict(collections.Counter); allc = collections.Counter()
    for f in ALL:
        s = rd(f); m = re.search(r'<meta property="og:image" content="(https://snsco\.in/assets/img/og/[^"]+)"', s)
        if m:
            allc[m.group(1)] += 1; e = byurl.get('/' + f)
            if e: cnt[e['c']][m.group(1)] += 1
    default = allc.most_common(1)[0][0]; n = 0
    for f in ALL:
        if f == '404.html': continue
        s = rd(f); o = s
        e = byurl.get('/' + f)
        if 'og:image' not in s and e:
            img = cnt[e['c']].most_common(1)[0][0] if cnt.get(e['c']) else default
            s = re.sub(r'(<meta property="og:description"[^>]*/>)', lambda m: m.group(1) + '\n<meta property="og:image" content="%s"/>' % img, s, count=1)
        m = re.search(r'<meta property="og:image" content="([^"]+)"', s)
        if m and 'twitter:image' not in s:
            s = re.sub(r'(<meta name="twitter:description"[^>]*/>)', lambda mm: mm.group(1) + '\n<meta name="twitter:image" content="%s"/>' % m.group(1), s, count=1)
            s = s.replace('<meta name="twitter:card" content="summary"/>', '<meta name="twitter:card" content="summary_large_image"/>')
        if s != o: wr(f, s); n += 1
    print('share images: pages changed', n)

# ---------------------------------------------------------------- related links, cluster blocks
STOP = set('india indian guide court high supreme the and for with what how are not can act law rules under from that this when your you who why section legal case hc sc new its has have was were will must may does into over after before between about their there which also than then more most other such these those only both each any'.split())
tok = lambda s: {w for w in re.findall(r'[a-z0-9]{3,}', s.lower()) if w not in STOP}
def short(t, n=78):
    if len(t) <= n: return t
    if ':' in t and 20 <= t.index(':') <= n: return t[:t.index(':')]
    c = t[:n].rsplit(' ', 1)[0].rstrip(' ,;:-')
    return c + '...'
li = lambda e: '<li><a href="%s">%s</a></li>' % (e['u'], esc(short(e['t'])))
def step_related():
    C = load_index(); byurl = {e['u']: e for e in C}
    T = {e['u']: tok(e['t'] + ' ' + e.get('d', '')) for e in C}
    inb = collections.Counter()
    for f in ALL:
        for h in set(re.findall(r'href="(/[^"#?]*\.html)"', re.sub(r'<div class="toc" data-rl="1">.*?</div>', '', rd(f), flags=re.S))):
            if h != '/' + f: inb[h] += 1
    area = collections.defaultdict(list)
    for e in C: area[e['c']].append(e)
    order = sorted(C, key=lambda e: (inb[e['u']], e['u']))
    picks = {}
    for e in order:
        tiny = [x for a, v in area.items() if len(v) < 12 for x in v]
        pool = [x for x in area[e['c']] + tiny if x['u'] != e['u']]
        pool = list({x['u']: x for x in pool}.values())
        if len(pool) < 12: pool = [x for x in C if x['u'] != e['u']]
        te = T[e['u']]
        def score(x):
            j = len(te & T[x['u']]) / (len(te | T[x['u']]) or 1)
            return 3 * j - 0.08 * inb[x['u']] + (0.002 * (x['dt'] > e['dt']))
        chosen = []
        def take(k, kind=None):
            c = sorted((x for x in pool if x not in chosen and (kind is None or x['k'] == kind)), key=lambda x: (-score(x), x['u']))[:k]
            for x in c: chosen.append(x); inb[x['u']] += 1
        take(2, e['k'])
        for kind in ('blog', 'news', 'article'):
            if kind != e['k']: take(1, kind)
        take(5 - len(chosen))
        picks[e['u']] = chosen
    n = fixed = ugly = 0
    for e in C:
        f = e['u'].lstrip('/'); s = rd(f); o = s
        s = re.sub(r'\s*<div class="toc" data-rl="1">.*?</div>', '', s, flags=re.S)
        blk = '    <div class="toc" data-rl="1">\n      <h4>Related Guides, Articles and News</h4>\n      <ul class="related-list">\n        ' + '\n        '.join(li(x) for x in picks[e['u']]) + '\n      </ul>\n    </div>\n  '
        i = s.rfind('</aside>')
        if i > 0:
            ls = s.rfind('\n', 0, i) + 1
            s = s[:ls] + blk + '  ' + s[i:]
        # correct the practice-area link (build scripts copied the template's)
        pg = AREA_PAGE.get(e['c'])
        pa = ('<li><a href="/practice-areas/%s.html">%s</a></li>' % (pg, esc(PAGE_LABEL.get(pg, e['c'])))) if pg else ''
        s2 = re.sub(r'(<h4>Related Practice Area</h4>\s*<ul class="related-list">)(.*?)(</ul>)', lambda m: m.group(1) + '\n        ' + pa + '<li><a href="/practice-areas/">All Practice Areas</a></li>\n      ' + m.group(3), s, count=1, flags=re.S)
        if s2 != s: fixed += 1
        s = s2
        # in-body "related" anchors whose text is a slugified file name
        def nice(m):
            u = m.group(1); t = byurl.get(u)
            slug = u.rsplit('/', 1)[1][:-5]
            if t and re.sub(r'[^a-z0-9]', '', m.group(2).lower()) == re.sub(r'[^a-z0-9]', '', slug): return '<li><a href="%s">%s</a></li>' % (u, esc(t['t']))
            return m.group(0)
        mi, mj = s.find('<main'), s.find('</main>')
        if mi >= 0 and mj > mi:
            body = re.sub(r'<li><a href="(/(?:articles|blog)/[^"]+\.html)">([^<]*)</a></li>', nice, s[mi:mj]); s = s[:mi] + body + s[mj:]
        if s != o: wr(f, s); n += 1
    print('related: pages changed', n, '| practice-area link corrected on', fixed)

def block(inner):
    return '<!--LIB-->' + inner + '<!--/LIB-->'
def lib_replace(s, new, anchor_re):
    s = re.sub(r'<!--LIB-->.*?<!--/LIB-->\s*', '', s, flags=re.S)
    m = re.search(anchor_re, s)
    if not m: return s, False
    return s[:m.start()] + new + '\n' + s[m.start():], True
def groups(items, top=12):
    out = ''
    for k in ('article', 'blog', 'news'):
        g = sorted((e for e in items if e['k'] == k), key=lambda e: (e['dt'], e['u']), reverse=True)
        if not g: continue
        out += '<h3>%s (%d)</h3>\n<ul class="lib-list">%s</ul>\n' % (TLABEL[k], len(g), ''.join(li(e) for e in g[:top]))
        if len(g) > top: out += '<details class="lib-more"><summary>Show all %d</summary><ul class="lib-list">%s</ul></details>\n' % (len(g), ''.join(li(e) for e in g[top:]))
    return out
LOC = {'bangalore': ('Bengaluru and Karnataka', ['Bengaluru', 'Bangalore', 'Karnataka']), 'faridabad': ('Faridabad and Haryana', ['Faridabad', 'Haryana']),
 'ghaziabad': ('Ghaziabad and Uttar Pradesh', ['Ghaziabad', 'Uttar Pradesh', 'Allahabad High Court']), 'greater-noida': ('Greater Noida and Uttar Pradesh', ['Greater Noida', 'Noida', 'Uttar Pradesh', 'Allahabad High Court']),
 'gurgaon': ('Gurugram and Haryana', ['Gurgaon', 'Gurugram', 'Haryana', 'Punjab and Haryana']), 'howrah': ('Howrah and West Bengal', ['Howrah', 'Calcutta', 'Kolkata', 'West Bengal']),
 'hyderabad': ('Hyderabad and Telangana', ['Hyderabad', 'Telangana']), 'indore': ('Indore and Madhya Pradesh', ['Indore', 'Madhya Pradesh']), 'kochi': ('Kochi and Kerala', ['Kochi', 'Kerala', 'Ernakulam']),
 'kolkata': ('Kolkata and West Bengal', ['Kolkata', 'Calcutta', 'West Bengal']), 'lucknow': ('Lucknow and Uttar Pradesh', ['Lucknow', 'Allahabad High Court', 'Uttar Pradesh']),
 'mumbai': ('Mumbai and Maharashtra', ['Mumbai', 'Bombay', 'Maharashtra']), 'new-delhi': ('Delhi', ['Delhi']), 'noida': ('Noida and Uttar Pradesh', ['Noida', 'Uttar Pradesh', 'Allahabad High Court']),
 'salt-lake': ('Salt Lake and West Bengal', ['Salt Lake', 'Calcutta', 'Kolkata', 'West Bengal'])}
def step_latest():
    C = load_index(); pat = lambda w: re.compile(r'\b' + re.escape(w) + r'\b', re.I)
    # practice-area cluster blocks
    n = 0
    for pg, areas in PAGE_AREAS.items():
        f = 'practice-areas/%s.html' % pg
        if not os.path.exists(f): continue
        items = [e for e in C if e['c'] in areas]
        label = PAGE_LABEL.get(pg, areas[0])
        new = block('<h2 id="library">Guides, Articles and Legal News on %s</h2>\n<p class="lib-note">Educational explainers and summaries of reported rulings, newest first. General information only, not legal advice.</p>\n%s' % (esc(label), groups(items)))
        s, ok = lib_replace(rd(f), new, r'<h2 id="faq">')
        if ok:
            if 'href="#library"' not in s:
                s = re.sub(r'(<div class="toc" aria-label="Table of contents">.*?)(</ol>)', lambda m: m.group(1) + '<li><a href="#library">Guides, Articles and Legal News</a></li>\n      ' + m.group(2), s, count=1, flags=re.S)
            wr(f, s); n += 1
    # location pages
    m_ = 0
    for k, (name, words) in LOC.items():
        f = 'locations/%s.html' % k
        if not os.path.exists(f): continue
        ps = [pat(w) for w in words]
        hit = [e for e in C if any(p.search(e['t'] + ' ' + e.get('d', '')) for p in ps)]
        hit = sorted(hit, key=lambda e: (e['dt'], e['u']), reverse=True)[:10]
        if len(hit) < 1: continue
        new = block('<h2>Recent Rulings and Explainers Relevant to %s</h2>\n<p class="lib-note">Educational pages that discuss courts, laws or matters connected with this region. General information only, not legal advice.</p>\n<ul class="lib-list">%s</ul>' % (esc(name), ''.join(li(e) for e in hit)))
        s, ok = lib_replace(rd(f), new, r'<h2>Frequently Asked Questions')
        if ok: wr(f, s); m_ += 1
    # home page
    s = rd('index.html'); s = re.sub(r'<!--LIB-->.*?<!--/LIB-->\s*', '', s, flags=re.S)
    cols = ''
    for k, href in (('blog', '/blog/'), ('article', '/articles/'), ('news', '/legal-news/')):
        g = sorted((e for e in C if e['k'] == k), key=lambda e: (e['dt'], e['u']), reverse=True)[:6]
        cols += '<div class="lib-col"><h3>Latest %s</h3><ul class="lib-list">%s</ul><a class="lib-all" href="%s">All %s</a></div>' % (TLABEL[k], ''.join(li(e) for e in g), href, TLABEL[k].lower())
    sec = block('<section id="library" class="lib-home"><div class="lib-in"><span class="stag" style="justify-content:center;">Reading</span><h2 class="stitle" style="text-align:center;">Latest <em>Explainers</em> and Rulings</h2><p class="lib-note" style="text-align:center;">Educational guides, long-form articles and summaries of reported rulings. General information only, not legal advice.</p><div class="lib-grid">' + cols + '</div></div></section>')
    i = s.index('<section id="updates">'); j = s.index('</section>', i) + len('</section>')
    s = s[:j] + '\n' + sec + s[j:]; wr('index.html', s)
    css = rd('assets/css/main.css'); mark = '/* LIBRARY BLOCKS (22 Nov 2026) */'
    if mark not in css:
        css += '\n' + mark + '''
.lib-list{list-style:none;margin:0 0 14px;padding:0}
.lib-list li{padding:7px 0;border-bottom:1px solid rgba(20,30,50,.1);line-height:1.5}
.lib-list a{color:var(--gdt);text-decoration:none}
.lib-list a:hover{text-decoration:underline}
.lib-note{font-size:14px;color:#54657d;line-height:1.7;margin:0 0 14px}
.lib-more summary{cursor:pointer;color:var(--gdt);padding:6px 0;font-size:14px}
.lib-home{padding:80px 60px;background:var(--cr)}
.lib-in{max-width:1180px;margin:0 auto}
.lib-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:36px;margin-top:28px}
.lib-col h3{font-size:18px;margin:0 0 10px}
.lib-all{display:inline-block;font-size:14px;color:var(--gdt);margin-top:4px}
@media(max-width:860px){.lib-home{padding:56px 16px}.lib-grid{grid-template-columns:1fr;gap:24px}}
'''
        wr('assets/css/main.css', css)
    print('latest/cluster: practice pages', n, '| location pages', m_, '| home block added')

# ---------------------------------------------------------------- feed
def step_feed():
    C = sorted(load_index(), key=lambda e: (e['dt'], e['u']), reverse=True)[:60]
    upd = max(e['dt'] for e in C)
    ent = ''.join('<entry><title>%s</title><link href="https://snsco.in%s"/><id>https://snsco.in%s</id><updated>%sT00:00:00+05:30</updated><category term="%s"/><summary>%s</summary></entry>\n' % (
        html.escape(e['t']), e['u'], e['u'], e['dt'], html.escape(e['c']), html.escape(e.get('d', ''))) for e in C)
    wr('feed.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>S&amp;S Co. Advocates &amp; Solicitors: legal explainers, articles and news</title><subtitle>Educational legal information. Not legal advice.</subtitle><link href="https://snsco.in/feed.xml" rel="self"/><link href="https://snsco.in/"/><id>https://snsco.in/</id><updated>%sT00:00:00+05:30</updated><author><name>S&amp;S Co. Advocates &amp; Solicitors</name></author>\n%s</feed>\n' % (upd, ent))
    tag = '<link rel="alternate" type="application/atom+xml" title="S&amp;S Co. legal explainers and news" href="/feed.xml"/>\n'
    n = 0
    for f in ('index.html', 'blog/index.html', 'legal-news/index.html', 'articles/index.html'):
        s = rd(f)
        if 'application/atom+xml' not in s:
            s = re.sub(r'(<link rel="stylesheet" href="/assets/css/main\.css)', lambda m: tag + m.group(1), s, count=1); wr(f, s); n += 1
    print('feed: entries', len(C), '| pages tagged', n)

# ---------------------------------------------------------------- sitemaps
SECT = [('sitemap-guides.xml', 'blog'), ('sitemap-news.xml', 'legal-news'), ('sitemap-articles.xml', 'articles')]
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
def step_flatten():
    s = rd('sitemap.xml')
    if '<sitemapindex' not in s: print('flatten: already flat'); return
    ents = []
    for fn in ['sitemap-pages.xml'] + [x[0] for x in SECT]:
        if os.path.exists(fn): ents += re.findall(r'<url>.*?</url>', rd(fn), re.S)
    wr('sitemap.xml', HEAD + '\n'.join('  ' + e for e in ents) + '\n</urlset>\n')
    for fn in ['sitemap-pages.xml'] + [x[0] for x in SECT]:
        if os.path.exists(fn): os.remove(fn)
    print('flatten: restored', len(ents), 'urls into sitemap.xml')
def step_split():
    s = rd('sitemap.xml')
    if '<sitemapindex' in s: print('split: already an index'); return
    ents = re.findall(r'<url>.*?</url>', s, re.S); buckets = collections.defaultdict(list)
    for e in ents:
        loc = re.search(r'<loc>https://snsco\.in/([^<]*)</loc>', e).group(1)
        top = loc.split('/')[0] if '/' in loc else ''
        fn = next((a for a, b in SECT if b == top), 'sitemap-pages.xml'); buckets[fn].append(e)
    idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for fn in ['sitemap-pages.xml'] + [a for a, b in SECT]:
        es = buckets[fn]; lm = max(re.search(r'<lastmod>([^<]*)', e).group(1) for e in es)
        wr(fn, HEAD + '\n'.join('  ' + e for e in es) + '\n</urlset>\n')
        idx += '  <sitemap><loc>https://snsco.in/%s</loc><lastmod>%s</lastmod></sitemap>\n' % (fn, lm)
    wr('sitemap.xml', idx + '</sitemapindex>\n'); print('split:', {k: len(v) for k, v in buckets.items()})

STEPS = {'fonts': step_fonts, 'og': step_og, 'related': step_related, 'latest': step_latest, 'feed': step_feed, 'flatten': step_flatten, 'split': step_split}
if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if a == 'all':
        for k in ('flatten', 'fonts', 'og', 'related', 'latest', 'feed'): STEPS[k]()
        import subprocess; subprocess.run([sys.executable, 'gen_redirects.py'], check=True)
        STEPS['split']()
    else: STEPS[a]()
