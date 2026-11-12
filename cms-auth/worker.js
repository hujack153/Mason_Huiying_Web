/**
 * 網站的 Worker：/auth 是後台的密碼登入，其餘網址都直接回傳 dist/ 的靜態網頁。
 *
 * 取代 GitHub OAuth：使用者輸入共用密碼，通過後把一把只能存取網站 repo 的
 * GitHub 金鑰交給後台（Decap CMS），後台再用它存檔、開 PR、發布。
 *
 * 需要在 Worker 設定兩個 Secret：
 *   ADMIN_PASSWORD  後台密碼（自己設定）
 *   GITHUB_TOKEN    GitHub fine-grained token（只授權 hujack153/Mason_Huiying_Web）
 * 選用的一般變數：
 *   ALLOWED_ORIGINS 允許使用後台的網站，逗號分隔（預設 https://huiyingmaterials.com）
 *                   預覽網址可加 *.workers.dev，例如 https://huiyingmaterials.com,*.workers.dev
 */

import { handleStudio } from "./studio.js";

const MAX_TRIES = 5;          // 同一個 IP 連續輸錯幾次後暫時鎖住
const LOCK_SECONDS = 15 * 60; // 鎖住多久

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let path = url.pathname;
    try {
      for (let i = 0; i < 3 && path.includes("%"); i++) path = decodeURIComponent(path);
    } catch { return new Response("Invalid URL", {status: 400}); }
    url.pathname = path.replace(/\/{2,}/g, "/");
    if (url.pathname === "/admin" || url.pathname.startsWith("/admin/")) {
      return handleStudio(new Request(url, request), env, {html, loginPage, isLocked, safeEqual, recordFail, clearFails});
    }
    if (url.pathname === "/auth" || url.pathname === "/callback") {
      if (request.method === "POST") return handleLogin(request, env);
      return html(loginPage(""));
    }
    return env.ASSETS.fetch(request);
  },
};

// ── 登入
async function handleLogin(request, env) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  if (await isLocked(ip)) {
    return html(loginPage("錯誤次數太多，請 15 分鐘後再試。"), 429);
  }
  const form = await request.formData();
  const pw = String(form.get("password") || "");
  if (!env.ADMIN_PASSWORD || !env.GITHUB_TOKEN) {
    return html(loginPage("登入程式尚未設定完成（缺少 ADMIN_PASSWORD 或 GITHUB_TOKEN）。"), 500);
  }
  if (!(await safeEqual(pw, env.ADMIN_PASSWORD))) {
    await recordFail(ip);
    return html(loginPage("密碼錯誤。"), 401);
  }
  await clearFails(ip);
  return html(successPage(env.GITHUB_TOKEN, env.ALLOWED_ORIGINS || "https://huiyingmaterials.com"));
}

// 固定時間比對，避免從回應時間猜密碼
async function safeEqual(a, b) {
  const enc = new TextEncoder();
  const [ha, hb] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(a)),
    crypto.subtle.digest("SHA-256", enc.encode(b)),
  ]);
  const x = new Uint8Array(ha), y = new Uint8Array(hb);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

// ── 錯誤次數（用 Cloudflare 快取暫存，不需另外建資料庫）
const failKey = (ip) => new Request(`https://cms-auth.internal/fail/${encodeURIComponent(ip)}`);
async function getFails(ip) {
  const r = await caches.default.match(failKey(ip));
  return r ? parseInt(await r.text(), 10) || 0 : 0;
}
async function isLocked(ip) { return (await getFails(ip)) >= MAX_TRIES; }
async function recordFail(ip) {
  const n = (await getFails(ip)) + 1;
  await caches.default.put(failKey(ip), new Response(String(n), {
    headers: { "Cache-Control": `max-age=${LOCK_SECONDS}` },
  }));
}
async function clearFails(ip) { await caches.default.delete(failKey(ip)); }

// ── 頁面
function html(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
      "Referrer-Policy": "no-referrer",
    },
  });
}

const STYLE = `
  :root{color-scheme:light dark}
  body{font-family:system-ui,-apple-system,"Noto Sans TC",sans-serif;margin:0;min-height:100vh;
       display:grid;place-items:center;background:#f4f2ee;color:#1d1d1b}
  @media (prefers-color-scheme:dark){body{background:#161615;color:#ecebe7}
    input{background:#232321;color:inherit;border-color:#444}}
  form{width:min(320px,90vw);display:grid;gap:12px}
  h1{font-size:18px;margin:0 0 4px}
  input{font:inherit;padding:10px 12px;border:1px solid #c9c6bf;border-radius:6px}
  button{font:inherit;padding:10px;border:0;border-radius:6px;background:#1d1d1b;color:#fff;cursor:pointer}
  @media (prefers-color-scheme:dark){button{background:#ecebe7;color:#161615}}
  .err{color:#b3261e;font-size:14px;margin:0}`;

function loginPage(error) {
  return `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>暉盈官網後台登入</title><style>${STYLE}</style></head><body>
<form method="post">
  <h1>暉盈官網後台</h1>
  <input type="password" name="password" placeholder="請輸入密碼" autocomplete="current-password" autofocus required>
  ${error ? `<p class="err">${error}</p>` : ""}
  <button type="submit">登入</button>
</form></body></html>`;
}

// Decap CMS 的登入握手：先告訴後台「正在登入」，後台回應後再把金鑰傳回去
function successPage(token, allowed) {
  const payload = JSON.stringify({ token, provider: "github" });
  const patterns = JSON.stringify(allowed.split(",").map((s) => s.trim()).filter(Boolean));
  return `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow"><title>登入中…</title><style>${STYLE}</style></head>
<body><p>登入成功，正在返回後台…</p><script>
(function () {
  var patterns = ${patterns};
  function allowedOrigin(o) {
    var u;
    try { u = new URL(o); } catch (e) { return false; }
    return patterns.some(function (p) {
      var h = p.replace(/^https?:\\/\\//, "").replace(/\\/$/, "");
      var host = h.indexOf(":") >= 0 ? u.host : u.hostname;  // 規則有寫連接埠才比對連接埠
      if (h.indexOf("*.") === 0) return host === h.slice(2) || host.slice(-(h.length - 1)) === h.slice(1);
      return host === h;
    });
  }
  var msg = "authorization:github:success:" + ${JSON.stringify(payload)};
  window.addEventListener("message", function (e) {
    if (!allowedOrigin(e.origin)) return;
    window.opener.postMessage(msg, e.origin);
    setTimeout(function () { window.close(); }, 300);
  }, false);
  if (window.opener) window.opener.postMessage("authorizing:github", "*");
  else document.body.innerHTML = "<p>請從後台的登入按鈕開啟此頁。</p>";
})();
</script></body></html>`;
}
