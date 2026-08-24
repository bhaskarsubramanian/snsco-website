document.addEventListener('DOMContentLoaded', function() {

  /* DISCLAIMER — the homepage always shows it (every visit); inner pages remember the
     acknowledgment (localStorage, shared across tabs) so it doesn't reappear on every click. */
  var DISC_KEY = 'snsco_disclaimer_ack';
  var isHome = (location.pathname === '/' || location.pathname === '/index.html');
  var discOv  = document.getElementById('discOv');
  var discChk = document.getElementById('disc-check');
  var discAgr = document.getElementById('discAgreeBtn');
  function hideDisc(skipAnim) {
    if (discOv) {
      if (skipAnim) { discOv.style.display='none'; }
      else { discOv.style.transition='opacity 0.3s'; discOv.style.opacity='0'; setTimeout(function(){ discOv.style.display='none'; },320); }
    }
    document.body.style.overflow='';
    if (discChk) discChk.checked=true;
  }
  if (!isHome) {
    try {
      if (localStorage.getItem(DISC_KEY) === '1') { hideDisc(true); }
    } catch (e) { /* localStorage unavailable (e.g. privacy mode) — disclaimer will show, which is the safe default */ }
  }
  if (discAgr) discAgr.addEventListener('click', function(e){ e.preventDefault(); try { localStorage.setItem(DISC_KEY,'1'); } catch(e){} hideDisc(); });
  if (discChk) discChk.addEventListener('change', function(){ if(this.checked){ try { localStorage.setItem(DISC_KEY,'1'); } catch(e){} hideDisc(); } });

  /* HAMBURGER */
  var hbg=document.getElementById('hamburger');
  var mob=document.getElementById('mobMenu');
  if (hbg && mob) {
    hbg.addEventListener('click', function(){ hbg.classList.toggle('open'); mob.classList.toggle('show'); });
    mob.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ hbg.classList.remove('open'); mob.classList.remove('show'); }); });
    document.addEventListener('click', function(e){ if (mob.classList.contains('show') && !mob.contains(e.target) && !hbg.contains(e.target)){ hbg.classList.remove('open'); mob.classList.remove('show'); } });
  }

  /* LEGAL UPDATES TABS (homepage only) */
  var tabBtns=document.querySelectorAll('.ut-btn');
  var tabPanels=document.querySelectorAll('.ut-panel');
  function activateTab(id) {
    tabBtns.forEach(function(b){ b.classList.remove('active'); });
    tabPanels.forEach(function(p){ p.classList.remove('active'); });
    var panel=document.getElementById('utp-'+id);
    if (panel) panel.classList.add('active');
    tabBtns.forEach(function(b){ if (b.getAttribute('data-tab')===id) b.classList.add('active'); });
  }
  tabBtns.forEach(function(btn){ btn.addEventListener('click', function(){ activateTab(btn.getAttribute('data-tab')); }); });
  var hasActive=false;
  tabPanels.forEach(function(p){ if(p.classList.contains('active')) hasActive=true; });
  if (!hasActive && tabBtns.length>0) activateTab(tabBtns[0].getAttribute('data-tab'));

  /* CONTACT FORM */
  var contactBtn=document.getElementById('contactBtn');
  if (contactBtn) {
    contactBtn.addEventListener('click', function() {
      var n=(document.getElementById('f-name').value||'').trim();
      var ph=(document.getElementById('f-phone').value||'').trim();
      var em=(document.getElementById('f-email').value||'').trim();
      var ar=(document.getElementById('f-area').value||'');
      var ms=(document.getElementById('f-msg').value||'').trim();
      if (!n||!em){ alert('Please fill in your name and email address.'); return; }
      var sub=encodeURIComponent('Legal Enquiry from '+n+' - S&S Co. Website');
      var bod=encodeURIComponent('Name: '+n+'\nPhone: '+ph+'\nEmail: '+em+'\nPractice Area: '+(ar||'Not specified')+'\n\nMessage:\n'+ms);
      window.location.href=('mailto:'+'communications'+'@'+'snsco.in'+'?subject=')+sub+'&body='+bod;
    });
  }

  /* APPLY FORM */
  var applyBtn=document.getElementById('applyBtn');
  if (applyBtn) {
    applyBtn.addEventListener('click', function() {
      var n=(document.getElementById('ap-name').value||'').trim();
      var ph=(document.getElementById('ap-phone').value||'').trim();
      var em=(document.getElementById('ap-email').value||'').trim();
      var role=(document.getElementById('ap-role').value||'');
      var school=(document.getElementById('ap-school').value||'').trim();
      var ms=(document.getElementById('ap-msg').value||'').trim();
      if (!n||!em){ alert('Please fill in your name and email address.'); return; }
      var sub=encodeURIComponent('Application: '+(role||'General')+' - '+n);
      var bod=encodeURIComponent('Applicant: '+n+'\nPhone: '+ph+'\nEmail: '+em+'\nApplying For: '+(role||'Not specified')+'\nLaw School: '+(school||'Not specified')+'\n\nCover Note:\n'+ms);
      window.location.href=('mailto:'+'communications'+'@'+'snsco.in'+'?subject=')+sub+'&body='+bod;
    });
  }

  /* EMAIL LINKS */
  document.querySelectorAll('.em-link').forEach(function(a){
    a.addEventListener('click', function(){
      window.location.href='mailto:'+a.getAttribute('data-u')+'@'+a.getAttribute('data-d');
    });
  });

  /* SMOOTH SCROLL (same-page hash links only, excluding links that open in a new tab) */
  document.querySelectorAll('a[href^="#"]:not([target="_blank"])').forEach(function(a){
    a.addEventListener('click', function(e){
      var t=document.querySelector(this.getAttribute('href'));
      if(t){ e.preventDefault(); t.scrollIntoView({behavior:'smooth',block:'start'}); }
    });
  });

});
