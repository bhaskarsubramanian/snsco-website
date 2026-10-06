/* Search + subject filter for /blog/, /legal-news/ and the /search/ page.
   Progressive enhancement: without JS the full listings stay visible and crawlable. */
(function () {
  var lf = document.getElementById('lf');
  if (!lf) return;
  var kind = lf.getAttribute('data-kind');
  var q = document.getElementById('lfq'), sel = document.getElementById('lfc'),
      cnt = document.getElementById('lfn'), rst = document.getElementById('lfr');
  var PAGE = 24;

  function norm(s) { return (s || '').toLowerCase().replace(/[‘’]/g, "'").replace(/&/g, ' and '); }
  function tokens(s) { return norm(s).split(/[^a-z0-9']+/).filter(Boolean); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  function getParam(k) { try { return new URLSearchParams(location.search).get(k) || ''; } catch (e) { return ''; } }
  function setUrl(qv, cv, tv) {
    try {
      var p = new URLSearchParams();
      if (qv) p.set('q', qv); if (cv) p.set('cat', cv); if (tv) p.set('type', tv);
      var s = p.toString();
      history.replaceState(null, '', location.pathname + (s ? '?' + s : ''));
    } catch (e) {}
  }
  function fillSelect(cats, total) {
    sel.innerHTML = '<option value="">All subjects (' + total + ')</option>';
    cats.forEach(function (c) {
      var o = document.createElement('option'); o.value = c[0]; o.textContent = c[0] + ' (' + c[1] + ')'; sel.appendChild(o);
    });
  }
  function countCats(list, key) {
    var m = {}; list.forEach(function (x) { var c = key(x); m[c] = (m[c] || 0) + 1; });
    return Object.keys(m).map(function (k) { return [k, m[k]]; }).sort(function (a, b) {
      if (a[0] === 'Other Subjects') return 1; if (b[0] === 'Other Subjects') return -1;
      return b[1] - a[1] || a[0].localeCompare(b[0]);
    });
  }

  /* ---------- listing pages (blog / news) ---------- */
  if (kind === 'blog' || kind === 'news') {
    var cards = [].slice.call(document.querySelectorAll('a[data-cat]'));
    var hay = cards.map(function (c) { return norm(c.textContent + ' ' + c.getAttribute('data-cat')); });
    fillSelect(countCats(cards, function (c) { return c.getAttribute('data-cat'); }), cards.length);
    var shown = PAGE, empty = null, more = null, panels = [];
    var host = kind === 'blog' ? document.getElementById('lfgrid') : null;
    if (kind === 'blog') {
      more = document.createElement('div'); more.className = 'lf-blogwrap';
      more.innerHTML = '<button type="button" class="lf-more" id="lfmore" hidden></button>';
      host.parentNode.insertBefore(more, host.nextSibling);
      empty = document.createElement('div'); empty.className = 'lf-empty'; empty.hidden = true;
      empty.textContent = 'No articles match your search. Try fewer words or choose All subjects.';
      host.appendChild(empty);
    } else {
      panels = [].slice.call(document.querySelectorAll('.ut-panel-grid')).map(function (g) {
        var head = [], n = g.previousElementSibling;
        while (n && n.tagName !== 'H2') { head.push(n); n = n.previousElementSibling; }
        if (n) head.push(n);
        return {grid: g, head: head};
      });
      empty = document.createElement('div'); empty.className = 'lf-news-empty'; empty.hidden = true;
      empty.textContent = 'No news items match your search. Try fewer words or choose All subjects.';
      lf.parentNode.insertBefore(empty, lf.nextSibling);
    }
    var moreBtn = document.getElementById('lfmore');

    function apply(resetPage) {
      if (resetPage) shown = PAGE;
      var terms = tokens(q.value), cat = sel.value, filtering = !!(terms.length || cat), matched = 0, vis = 0;
      cards.forEach(function (c, i) {
        var ok = (!cat || c.getAttribute('data-cat') === cat) && terms.every(function (t) { return hay[i].indexOf(t) > -1; });
        if (ok) matched++;
        var show = ok && (kind === 'news' || vis < shown);
        if (ok && show) vis++;
        c.hidden = !show;
      });
      if (kind === 'news') {
        panels.forEach(function (p) {
          var any = p.grid.querySelector('a[data-cat]:not([hidden])');
          p.grid.classList.toggle('lf-hide', !any);
          p.head.forEach(function (h) { h.classList.toggle('lf-hide', !any); });
          p.head.forEach(function (h) {
            if (h.id) { var a = document.querySelector('.toc a[href="#' + h.id + '"]'); if (a && a.parentNode) a.parentNode.classList.toggle('lf-hide', !any); }
          });
        });
      } else {
        moreBtn.hidden = matched <= vis;
        moreBtn.textContent = 'Show more (' + (matched - vis) + ' remaining)';
      }
      empty.hidden = matched > 0;
      cnt.textContent = (filtering ? plural(matched, 'result') + ' of ' + cards.length : cards.length + ' articles') +
        (kind === 'blog' && matched > vis ? ', showing the latest ' + vis : '');
      rst.hidden = !filtering;
      setUrl(q.value.trim(), cat, '');
    }
    if (moreBtn) moreBtn.addEventListener('click', function () { shown += PAGE; apply(false); });
    var t; q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { apply(true); }, 120); });
    sel.addEventListener('change', function () { apply(true); });
    rst.addEventListener('click', function () { q.value = ''; sel.value = ''; apply(true); q.focus(); });
    q.value = getParam('q'); var c0 = getParam('cat');
    if (c0) { sel.value = c0; if (sel.value !== c0) sel.value = ''; }
    lf.hidden = false; apply(true);
    return;
  }

  /* ---------- /search/ page ---------- */
  var tsel = document.getElementById('lft'), list = document.getElementById('srl'), more2 = document.getElementById('srm');
  var data = [], idxReady = false, shown2 = PAGE, last = [];
  function monthYear(d) {
    if (!d) return ''; var p = d.split('-'); var m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+p[1] - 1];
    return (+p[2]) + ' ' + m + ' ' + p[0];
  }
  function highlight(text, terms) {
    var out = esc(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
    });
    return out;
  }
  function run(resetPage) {
    if (!idxReady) return;
    if (resetPage) shown2 = PAGE;
    var terms = tokens(q.value), cat = sel.value, ty = tsel.value, res = [];
    data.forEach(function (x) {
      if (cat && x.c !== cat) return; if (ty && x.k !== ty) return;
      var score = 0, ok = true;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i];
        if (x._t.indexOf(t) > -1) score += 10; else if (x._d.indexOf(t) > -1 || x._c.indexOf(t) > -1) score += 4; else if (x._s.indexOf(t) > -1) score += 1; else { ok = false; break; }
      }
      if (ok) res.push({x: x, s: score});
    });
    if (terms.length) res.sort(function (a, b) { return b.s - a.s || (b.x.dt > a.x.dt ? 1 : -1); });
    last = res;
    var filtering = !!(terms.length || cat || ty);
    var view = res.slice(0, shown2);
    list.innerHTML = view.map(function (r) {
      var x = r.x;
      return '<li class="sr-item"><div class="sr-meta"><span class="sr-badge ' + (x.k === 'news' ? 'n' : '') + '">' + (x.k === 'news' ? 'Legal news' : 'Blog') + '</span><span>' + esc(x.c) + '</span><span>' + monthYear(x.dt) + '</span></div>' +
        '<h2 class="sr-title"><a href="' + esc(x.u) + '">' + highlight(x.t, terms) + '</a></h2><p class="sr-desc">' + highlight(x.d, terms) + '</p></li>';
    }).join('') || '<li class="sr-item"><p class="sr-desc">No articles match. Try fewer words, a different spelling or All subjects.</p></li>';
    more2.hidden = res.length <= view.length;
    more2.textContent = 'Show more results (' + (res.length - view.length) + ' remaining)';
    cnt.textContent = filtering ? plural(res.length, 'result') + ' of ' + data.length + ' articles' : 'Search ' + data.length + ' articles';
    rst.hidden = !filtering;
    setUrl(q.value.trim(), cat, ty);
  }
  fetch('/assets/search-index.json?v1').then(function (r) { return r.json(); }).then(function (j) {
    data = j; data.forEach(function (x) { x._t = norm(x.t); x._d = norm(x.d); x._c = norm(x.c); x._s = norm(x.s); });
    fillSelect(countCats(data, function (x) { return x.c; }), data.length);
    idxReady = true; q.value = getParam('q'); var c0 = getParam('cat'); if (c0) { sel.value = c0; if (sel.value !== c0) sel.value = ''; }
    tsel.value = getParam('type'); if (tsel.value !== getParam('type')) tsel.value = '';
    lf.hidden = false; run(true); q.focus();
  }).catch(function () { cnt.textContent = ''; list.innerHTML = '<li class="sr-item"><p class="sr-desc">Search is unavailable right now. Please browse the <a href="/blog/">blog</a> or <a href="/legal-news/">legal news</a>.</p></li>'; lf.hidden = false; });
  var t2; q.addEventListener('input', function () { clearTimeout(t2); t2 = setTimeout(function () { run(true); }, 120); });
  sel.addEventListener('change', function () { run(true); }); tsel.addEventListener('change', function () { run(true); });
  more2.addEventListener('click', function () { shown2 += PAGE; run(false); });
  rst.addEventListener('click', function () { q.value = ''; sel.value = ''; tsel.value = ''; run(true); q.focus(); });
})();
