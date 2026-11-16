"""Browser-tab / og title helper: use the draft's seo_title (<=60 chars) if present, else shorten the title safely."""
def seo_title(d, limit=60):
    t = (d.get('seo_title') or '').strip()
    if t and len(t) <= limit: return t
    t = d['title'].strip()
    if len(t) <= limit: return t
    head = t.split(':')[0].strip()
    if 20 <= len(head) <= limit: return head
    cut = t[:limit + 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
    return cut
