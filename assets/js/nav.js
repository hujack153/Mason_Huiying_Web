// 手機版選單
(function () {
  var btn = document.getElementById('navToggle');
  var nav = document.getElementById('mainNav');
  if (!btn || !nav) return;
  btn.addEventListener('click', function () {
    nav.classList.toggle('open');
    btn.textContent = nav.classList.contains('open') ? '關閉' : '選單';
  });
})();
