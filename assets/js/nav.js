/* 手機選單 */
(function () {
  var b = document.getElementById('navBtn'), n = document.getElementById('nav');
  if (!b || !n) return;
  var open = b.textContent.trim(), close = /[A-Za-z]/.test(open) ? 'Close' : '關閉';
  b.addEventListener('click', function () {
    var o = n.classList.toggle('open');
    b.textContent = o ? close : open;
    b.setAttribute('aria-expanded', o ? 'true' : 'false');
  });
})();

/* 滑鼠移上站內連結即預載目標頁，換頁更快 */
(function () {
  if (location.protocol === 'file:') return;
  var done = {};
  function grab(a) {
    var h = a.getAttribute('href') || '';
    if (!h || h.charAt(0) === '#' || /^[a-z]+:/i.test(h) || done[h]) return;
    if (!/\.html($|#)|\/$/.test(h)) return;
    done[h] = 1;
    var l = document.createElement('link');
    l.rel = 'prefetch'; l.href = h; l.as = 'document';
    document.head.appendChild(l);
  }
  document.addEventListener('mouseover', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (a) grab(a);
  }, { passive: true });
  document.addEventListener('touchstart', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (a) grab(a);
  }, { passive: true });
})();

/* 首頁版頭剖面圖輪播：自動輪播＋可滑動，滑鼠移入或觸碰即暫停 */
(function () {
  var s = document.getElementById('figSlider');
  if (!s) return;
  var trk = s.querySelector('.trk'),
      sls = trk.children,
      dots = s.querySelectorAll('.dots button'),
      n = sls.length, i = 0, t = null;
  var auto = !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  function paint() {
    for (var k = 0; k < dots.length; k++) {
      dots[k].setAttribute('aria-current', k === i ? 'true' : 'false');
    }
  }
  function go(k) {
    i = (k + n) % n;
    trk.scrollTo({ left: sls[i].offsetLeft - trk.offsetLeft, behavior: 'smooth' });
    paint();
  }
  function start() { if (auto && !t) t = setInterval(function () { go(i + 1); }, 6000); }
  function stop() { if (t) { clearInterval(t); t = null; } }

  for (var k = 0; k < dots.length; k++) {
    (function (k) {
      dots[k].addEventListener('click', function () { stop(); go(k); });
    })(k);
  }
  trk.addEventListener('scroll', function () {
    var k = Math.round(trk.scrollLeft / trk.clientWidth);
    if (k !== i && k >= 0 && k < n) { i = k; paint(); }
  }, { passive: true });
  s.addEventListener('mouseenter', stop);
  s.addEventListener('mouseleave', start);
  trk.addEventListener('touchstart', stop, { passive: true });
  paint(); start();
})();

/* 色卡：點擊顯示色名（桌機 hover 即可，觸控裝置用點擊） */
(function () {
  var sws = document.querySelectorAll('.swgrid .sw');
  for (var k = 0; k < sws.length; k++) {
    sws[k].addEventListener('click', function () { this.classList.toggle('on'); });
  }
})();

/* 跳轉選單連到收合列時自動展開 */
(function () {
  function open() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (el && el.tagName === 'DETAILS') el.open = true;
  }
  window.addEventListener('hashchange', open);
  open();
})();

/* 語言切換與提示
   對照頁網址從 <link rel="alternate" hreflang> 讀出，換算成相對路徑，
   因此本機直接開 html 檔（file://）與部署到網域後都能正常切換 */
(function () {
  var KEY = 'hy_lang';
  var cur = (document.documentElement.lang || '').indexOf('en') === 0 ? 'en' : 'zh';

  function sitePath(l) {
    var el = document.querySelector(
      'link[rel="alternate"][hreflang="' + (l === 'zh' ? 'zh-Hant' : 'en') + '"]');
    if (!el) return null;
    return el.getAttribute('href').replace(/^https?:\/\/[^\/]+/, '');
  }
  function segs(p) {
    if (p.slice(-1) === '/') p += 'index.html';
    return p.split('/').filter(function (x) { return x; });
  }
  function relTo(l) {
    var f = sitePath(cur), t = sitePath(l);
    if (!f || !t) return null;
    var a = segs(f), b = segs(t);
    a.pop();
    var i = 0;
    while (i < a.length && i < b.length - 1 && a[i] === b[i]) i++;
    var up = '';
    for (var k = i; k < a.length; k++) up += '../';
    return up + b.slice(i).join('/');
  }

  var sw = document.getElementById('langSwitch');
  if (sw) {
    var target = sw.dataset.target;
    var url = relTo(target);
    if (url) sw.setAttribute('href', url);
    sw.addEventListener('click', function () {
      try { localStorage.setItem(KEY, target); } catch (err) {}
    });
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (err) {}
  if (saved || sessionStorage.getItem('hy_lang_x')) return;

  var langs = navigator.languages || [navigator.language || ''];
  var pref = langs.some(function (l) { return /^zh/i.test(l); }) ? 'zh' : 'en';
  if (pref === cur) return;

  var txt = {
    en: { m: 'This site is also available in English.', g: 'View English version', x: 'Dismiss' },
    zh: { m: '本網站提供繁體中文版本。', g: '切換至中文版', x: '關閉' }
  }[pref];
  var url2 = relTo(pref);
  if (!url2) return;

  var bar = document.createElement('div');
  bar.className = 'langbar';
  bar.innerHTML = '<div class="page"><span>' + txt.m + '</span>' +
    '<a href="' + url2 + '" hreflang="' + pref + '">' + txt.g + '</a>' +
    '<button type="button">' + txt.x + '</button></div>';
  bar.querySelector('a').addEventListener('click', function () {
    try { localStorage.setItem(KEY, pref); } catch (err) {}
  });
  bar.querySelector('button').addEventListener('click', function () {
    try { sessionStorage.setItem('hy_lang_x', '1'); } catch (err) {}
    bar.remove();
  });
  document.body.insertBefore(bar, document.body.firstChild);
})();
