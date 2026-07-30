// 手機版選單 + 語言切換與偵測
(function () {
  var btn = document.getElementById('navToggle');
  var nav = document.getElementById('mainNav');
  if (btn && nav) {
    var open = btn.textContent.trim();
    var close = /[A-Za-z]/.test(open) ? 'Close' : '關閉';
    btn.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('open');
      btn.textContent = isOpen ? close : open;
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }
})();

(function () {
  var KEY = 'hy_lang';
  var isEn = /^\/en(\/|$)/.test(location.pathname);
  var current = isEn ? 'en' : 'zh';

  // 目前頁面在另一語言的對應網址
  function urlFor(lang) {
    var p = location.pathname;
    if (lang === 'en') {
      return isEn ? p : ('/en' + (p === '/' ? '/' : p));
    }
    return isEn ? (p.replace(/^\/en/, '') || '/') : p;
  }

  var sw = document.getElementById('langSwitch');
  if (sw) {
    var target = sw.dataset.target;
    sw.setAttribute('href', urlFor(target));
    sw.addEventListener('click', function (e) {
      e.preventDefault();
      try { localStorage.setItem(KEY, target); } catch (err) {}
      location.href = urlFor(target);
    });
  }

  // 使用者已表態過就不再提示
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (err) {}
  if (saved || sessionStorage.getItem('hy_lang_dismissed')) return;

  // 依瀏覽器語言判斷偏好；中文為預設，不強制轉向
  var langs = navigator.languages || [navigator.language || ''];
  var prefersZh = langs.some(function (l) { return /^zh/i.test(l); });
  var preferred = prefersZh ? 'zh' : 'en';
  if (preferred === current) return;

  var texts = {
    en: { msg: 'This site is also available in English.', go: 'View English version', x: 'Dismiss' },
    zh: { msg: '本網站提供繁體中文版本。', go: '切換至中文版', x: '關閉' }
  }[preferred];

  var bar = document.createElement('div');
  bar.className = 'lang-banner';
  bar.innerHTML = '<div class="wrap"><span>' + texts.msg + '</span>' +
    '<a href="' + urlFor(preferred) + '" hreflang="' + preferred + '">' + texts.go + '</a>' +
    '<button type="button">' + texts.x + '</button></div>';

  bar.querySelector('a').addEventListener('click', function () {
    try { localStorage.setItem(KEY, preferred); } catch (err) {}
  });
  bar.querySelector('button').addEventListener('click', function () {
    try { sessionStorage.setItem('hy_lang_dismissed', '1'); } catch (err) {}
    bar.remove();
  });

  document.body.insertBefore(bar, document.body.firstChild);
})();
