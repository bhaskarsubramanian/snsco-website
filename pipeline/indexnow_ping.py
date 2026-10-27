"""Tell IndexNow search engines (Bing, Yandex, others; not Google) about new or changed pages.
Run AFTER a publish, once the key file is live at https://snsco.in/5848ad5bc75a686d5b90df6716fc14ab.txt.
usage: python indexnow_ping.py <git-ref-before> <git-ref-after>   (URLs of added/changed html pages)
   or: python indexnow_ping.py --urls https://snsco.in/a.html https://snsco.in/b.html
Run from the site worktree (needs git). The key is public by design."""
import sys, json, subprocess, urllib.request
HOST = 'snsco.in'
KEY = '5848ad5bc75a686d5b90df6716fc14ab'
def urls_from_git(a, b):
    out = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=AM', a, b], text=True).split()
    urls = []
    for f in out:
        if not f.endswith('.html') or f.startswith(('_drafts', '404', 'newsletter/thank-you', 'search/')): continue
        p = '/' + f
        if p.endswith('/index.html'): p = p[:-10]
        urls.append('https://%s%s' % (HOST, p))
    return urls
def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--urls': urls = sys.argv[2:]
    elif len(sys.argv) == 3: urls = urls_from_git(sys.argv[1], sys.argv[2])
    else: sys.exit(__doc__)
    urls = urls[:10000]
    if not urls: print('nothing to ping'); return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': 'https://%s/%s.txt' % (HOST, KEY), 'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/IndexNow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=60) as r: print('IndexNow status', r.status, 'urls', len(urls))
main()
