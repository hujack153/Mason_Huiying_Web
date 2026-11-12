const REPO = "hujack153/Mason_Huiying_Web";
const BRANCH = "cms/studio";
const DRAFT_PATH = ".cms/studio-draft.json";
const COOKIE = "__Host-huiying-studio";
const LANGS = ["zh", "en"];
// Encrypted/base64 draft envelopes stay below GitHub Contents API's 1 MB limit.
const MAX_BYTES = 512 * 1024;
const FILES = ["home", "waterproofing"].flatMap(kind =>
  LANGS.map(lang => ({kind, lang, path: `content/${lang}/${kind}.json`})));

class StudioError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
function json(value, status = 200) {
  return new Response(JSON.stringify(value), {status, headers: {
    "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store",
    "X-Robots-Tag": "noindex, nofollow", "X-Content-Type-Options": "nosniff",
  }});
}
function redirect(path, cookie) {
  const headers = {"Location": path, "Cache-Control": "no-store"};
  if (cookie) headers["Set-Cookie"] = cookie;
  return new Response(null, {status: 303, headers});
}
function encode(value) {
  return bytes64(new TextEncoder().encode(value));
}
function bytes64(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}
function from64(value) { return Uint8Array.from(atob(value.replace(/\s/g, "")), c => c.charCodeAt(0)); }
function decode(value) {
  return new TextDecoder().decode(from64(value));
}
async function draftKey(env) {
  const secret = await crypto.subtle.digest("SHA-256",
    new TextEncoder().encode("huiying-draft-v1:" + env.GITHUB_TOKEN + ":" + env.ADMIN_PASSWORD));
  return crypto.subtle.importKey("raw", secret, "AES-GCM", false, ["encrypt", "decrypt"]);
}
async function encryptDraft(value, env) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt({name: "AES-GCM", iv}, await draftKey(env),
    new TextEncoder().encode(JSON.stringify(value)));
  return {version: 1, iv: bytes64(iv), encrypted: bytes64(new Uint8Array(encrypted))};
}
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  }
  return value;
}
function same(a, b) { return JSON.stringify(canonical(a)) === JSON.stringify(canonical(b)); }
export async function fingerprint(value) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify(canonical(value))));
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("");
}
async function key(env) {
  return crypto.subtle.importKey("raw", new TextEncoder().encode("studio:" + env.ADMIN_PASSWORD),
    {name: "HMAC", hash: "SHA-256"}, false, ["sign", "verify"]);
}
async function sessionCookie(env, origin) {
  const payload = encode(JSON.stringify({expires: Date.now() + 28800000, origin}));
  const signature = await crypto.subtle.sign("HMAC", await key(env), new TextEncoder().encode(payload));
  const hex = Array.from(new Uint8Array(signature), byte => byte.toString(16).padStart(2, "0")).join("");
  return `${COOKIE}=${payload}.${hex}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=28800`;
}
async function authenticated(request, env) {
  if (!env.ADMIN_PASSWORD) return false;
  const cookie = (request.headers.get("Cookie") || "").split(";").map(part => part.trim())
    .find(part => part.startsWith(COOKIE + "="));
  if (!cookie) return false;
  const [payload, signature] = cookie.slice(COOKIE.length + 1).split(".");
  if (!payload || !/^[a-f0-9]{64}$/.test(signature || "")) return false;
  try {
    const valid = await crypto.subtle.verify("HMAC", await key(env),
      Uint8Array.from(signature.match(/../g), byte => parseInt(byte, 16)), new TextEncoder().encode(payload));
    const session = JSON.parse(decode(payload));
    return valid && Number.isFinite(session.expires) && session.expires > Date.now() &&
      session.origin === new URL(request.url).origin;
  } catch { return false; }
}
async function github(env, path, {method = "GET", body, optional = false} = {}) {
  if (!env.GITHUB_TOKEN) throw new StudioError("後台連線尚未設定，請聯絡網站維護人員。", 503);
  const result = await fetch("https://api.github.com/repos/" + REPO + path, {
    method,
    headers: {
      "Authorization": "Bearer " + env.GITHUB_TOKEN, "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Huiying-Studio", "Content-Type": "application/json",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (optional && result.status === 404) return null;
  if (!result.ok) {
    if ([409, 422].includes(result.status)) throw new StudioError("內容已更新，請先備份草稿再重新載入確認。", 409);
    throw new StudioError("暫時無法存取網站內容，請稍後重試或聯絡維護人員。", 502);
  }
  return result.json();
}
async function readMain(env) {
  const ref = await github(env, "/git/ref/heads/main");
  const data = {home: {}, waterproofing: {}};
  await Promise.all(FILES.map(async ({kind, lang, path}) => {
    const file = await github(env, `/contents/${path}?ref=${ref.object.sha}`);
    data[kind][lang] = JSON.parse(decode(file.content));
  }));
  return {data, head: ref.object.sha, baseline: await fingerprint(data)};
}
async function readDraft(env) {
  const file = await github(env, `/contents/${DRAFT_PATH}?ref=${encodeURIComponent(BRANCH)}`, {optional: true});
  if (!file) return {value: null, revision: null};
  try {
    const envelope = JSON.parse(decode(file.content));
    check(envelope.version === 1, "草稿版本不支援。");
    const decrypted = await crypto.subtle.decrypt({name: "AES-GCM", iv: from64(envelope.iv)},
      await draftKey(env), from64(envelope.encrypted));
    return {value: JSON.parse(new TextDecoder().decode(decrypted)), revision: file.sha};
  } catch {
    return {value: null, revision: file.sha, unreadable: true};
  }
}
function activeDraft(draft, source) {
  if (draft.unreadable) return {data: source.data, baseline: "unreadable", unreadable: true};
  return !draft.value?.data || same(draft.value.data, source.data) ? null : draft.value;
}
async function writeDraft(env, value, revision, head) {
  if (!await github(env, "/git/ref/heads/" + BRANCH, {optional: true})) {
    try {
      await github(env, "/git/refs", {method: "POST", body: {ref: "refs/heads/" + BRANCH, sha: head}});
    } catch (error) { if (error.status !== 409) throw error; }
  }
  const result = await github(env, "/contents/" + DRAFT_PATH, {method: "PUT", body: {
    branch: BRANCH, message: "後台儲存草稿", content: encode(JSON.stringify(await encryptDraft(value, env), null, 2) + "\n"),
    ...(revision ? {sha: revision} : {}),
  }});
  return result.content.sha;
}
function check(condition, message) { if (!condition) throw new StudioError(message); }
function text(value) { return typeof value === "string" && value.length <= 6000 && !value.includes("\0"); }
export function validate(data, complete = false) {
  check(data && Object.keys(data).sort().join() === "home,waterproofing", "內容格式錯誤。");
  for (const kind of ["home", "waterproofing"]) {
    check(data[kind] && Object.keys(data[kind]).sort().join() === "en,zh", "需要中文與英文兩份內容。");
  }
  const ids = {}, visibility = {};
  for (const lang of LANGS) {
    const label = lang === "zh" ? "中文" : "英文";
    const home = data.home[lang];
    check(home && Object.keys(home).sort().join() === "h1,lead" && Object.values(home).every(text), "首頁文字格式錯誤或過長。");
    if (complete) check(Object.values(home).every(value => value.trim()), label + "首頁標題與引言需要填寫。");
    const catalog = data.waterproofing[lang];
    check(catalog && Object.keys(catalog).join() === "series" && Array.isArray(catalog.series) && catalog.series.length <= 200,
      "產品清單格式錯誤，最多可管理 200 個系列。");
    ids[lang] = []; visibility[lang] = [];
    for (const item of catalog.series) {
      check(item && typeof item === "object", "產品內容格式錯誤。");
      check(Object.keys(item).every(name => ["id", "name", "tagline", "desc", "use", "feat", "spec", "archived"].includes(name)),
        "產品包含不支援的欄位。");
      check(typeof item.id === "string" && item.id.length <= 64 && /^[a-z0-9]+(-[a-z0-9]+)*$/.test(item.id), "產品代號格式錯誤。");
      check(item.archived === undefined || typeof item.archived === "boolean", "產品顯示設定格式錯誤。");
      check(["name", "tagline", "desc", "use"].every(name => text(item[name])), "產品文字格式錯誤或過長。");
      check(Array.isArray(item.feat) && item.feat.length <= 100 && item.feat.every(text), "產品特點格式錯誤。");
      check(Array.isArray(item.spec) && item.spec.length <= 100 && item.spec.every(row =>
        row && Object.keys(row).sort().join() === "k,v" && text(row.k) && text(row.v)), "產品規格格式錯誤。");
      ids[lang].push(item.id); visibility[lang].push(Boolean(item.archived));
      if (complete && !item.archived) {
        check(["name", "tagline", "desc", "use"].every(name => item[name].trim()),
          (item.name || "未命名系列") + "的" + label + "名稱、簡短介紹、說明與適用部位需要填寫。");
        check(item.spec.every(row => row.k.trim() && row.v.trim()), label + "產品規格的項目與數值需要一起填寫。");
      }
    }
    check(new Set(ids[lang]).size === ids[lang].length, "產品代號重複。");
  }
  if (complete) {
    check(same(ids.zh, ids.en), "中英文產品與排序需要一致。");
    check(same(visibility.zh, visibility.en), "中英文產品顯示設定需要一致。");
  }
}
function escape(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[char]);
}
function rich(value) { return escape(value).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>"); }
async function previewAsset(request, env, path) {
  let url = new URL(path, request.url);
  for (let attempt = 0; attempt < 4; attempt++) {
    const asset = await env.ASSETS.fetch(new Request(url));
    const location = asset.headers.get("Location");
    if (asset.status < 300 || asset.status >= 400 || !location) return asset;
    const next = new URL(location, url);
    if (next.origin !== url.origin || !next.pathname.startsWith("/admin/preview/")) break;
    url = next;
  }
  throw new StudioError("預覽暫時無法載入，請稍後重試。", 503);
}
function seriesRows(series, lang) {
  const labels = lang === "zh" ? ["產品特性", "適用部位", "參考規格"] : ["Characteristics", "Applications", "Reference"];
  return series.map((item, index) => {
    const features = item.feat.map(value => "<li>" + rich(value) + "</li>").join("");
    const spec = item.spec.map(row => "<div><span>" + rich(row.k) + "</span><b>" + rich(row.v) + "</b></div>").join("");
    const separator = lang === "zh" ? "。" : ". ";
    const cut = item.desc.indexOf(separator);
    const brief = cut < 0 ? item.desc : item.desc.slice(0, cut + separator.length);
    return `<details class="acc" id="${item.id}"><summary><span class="k">${String(index + 1).padStart(2, "0")}</span>
      <span class="t"><h3>${rich(item.name)}</h3><span class="role">${rich(item.tagline)}</span></span>
      <span class="brief">${rich(brief)}</span><span class="tg" aria-hidden="true"></span></summary>
      <div class="rb"><p>${rich(item.desc)}</p><div class="cols">
      <div><h5>${labels[0]}</h5><ul class="marks">${features}</ul></div>
      <div><h5>${labels[1]}</h5><p class="use">${rich(item.use)}</p></div>
      <div><h5>${labels[2]}</h5><div class="data">${spec}</div></div></div></div></details>`;
  }).join("");
}
async function preview(request, env, body) {
  check(["home", "waterproofing"].includes(body.page) && LANGS.includes(body.lang), "未知的預覽頁面。");
  const asset = await previewAsset(request, env, `/admin/preview/${body.page}_${body.lang}.html`);
  if (!asset.ok) throw new StudioError("預覽尚未準備完成，請稍後重試。", 503);
  const count = body.data.waterproofing.zh.series.filter(item => !item.archived).length;
  const zhNumbers = "零一二三四五六七八九十";
  const zh = count <= 10 ? zhNumbers[count] : count < 20 ? "十" + zhNumbers[count - 10] : String(count);
  const words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"];
  const en = words[count] || String(count);
  const series = body.data.waterproofing[body.lang].series.filter(item => !item.archived);
  const replacements = {
    "__STUDIO_TITLE__": escape(body.data.home[body.lang].h1).replace(/\r?\n/g, "<br>"),
    "__STUDIO_LEAD__": escape(body.data.home[body.lang].lead),
    "__STUDIO_JUMP__": series.map(item => `<a href="#${item.id}">${rich(item.name)}</a>`).join(""),
    "__STUDIO_ROWS__": seriesRows(series, body.lang),
    "__STUDIO_COUNT__": String(count), "__STUDIO_COUNT_ZH__": zh,
    "__STUDIO_COUNT_EN__": en[0].toUpperCase() + en.slice(1), "__STUDIO_COUNT_EN_LOWER__": en,
  };
  const html = (await asset.text()).replace(/__STUDIO_[A-Z_]+__/g, name => replacements[name] ?? name);
  return new Response(html, {headers: {
    "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store",
    "Content-Security-Policy": "script-src 'none'; object-src 'none'; frame-ancestors 'self'",
    "X-Robots-Tag": "noindex, nofollow",
  }});
}
async function publish(env, source, draft, body) {
  check(draft.value?.data && same(draft.value.data, body.data), "請先儲存目前的草稿。");
  const baseline = await fingerprint(body.data);
  if (source.baseline === baseline) return {commit: source.head, baseline};
  if (body.baseline !== source.baseline || draft.value.baseline !== source.baseline) {
    throw new StudioError("來源內容已更新，請先備份草稿再重新載入。", 409);
  }
  const commit = await github(env, "/git/commits/" + source.head);
  const tree = FILES.filter(({kind, lang}) => !same(body.data[kind][lang], source.data[kind][lang]))
    .map(({kind, lang, path}) => ({path, mode: "100644", type: "blob", content: JSON.stringify(body.data[kind][lang], null, 2) + "\n"}));
  const nextTree = await github(env, "/git/trees", {method: "POST", body: {base_tree: commit.tree.sha, tree}});
  const next = await github(env, "/git/commits", {method: "POST",
    body: {message: "後台發布：首頁與防水產品內容", tree: nextTree.sha, parents: [source.head]}});
  await github(env, "/git/refs/heads/main", {method: "PATCH", body: {sha: next.sha, force: false}});
  return {commit: next.sha, baseline};
}
async function api(request, env) {
  const url = new URL(request.url);
  const action = url.pathname.slice("/admin/api/".length);
  if (request.method === "GET") {
    if (action === "deployment") {
      const asset = await env.ASSETS.fetch(new Request(new URL("/admin/deployment.json", request.url)));
      if (!asset.ok) throw new StudioError("正在準備網站版本資訊，請稍後再確認。", 503);
      return json(await asset.json());
    }
    if (action !== "state") return json({error: "找不到這個操作。"}, 404);
    const [source, draft] = await Promise.all([readMain(env), readDraft(env)]);
    const manifest = await env.ASSETS.fetch(new Request(new URL("/admin/deployment.json", request.url)));
    const references = manifest.ok ? (await manifest.json()).references || {} : {};
    return json({source: source.data, baseline: source.baseline, draft: activeDraft(draft, source),
      revision: draft.revision, references, online: true});
  }
  if (request.method !== "POST") return json({error: "不支援這個操作。"}, 405);
  if (request.headers.get("Origin") !== url.origin) return json({error: "請從後台操作。"}, 403);
  check((request.headers.get("Content-Type") || "").split(";")[0] === "application/json", "請求格式錯誤。");
  check(Number(request.headers.get("Content-Length") || 0) <= MAX_BYTES, "草稿太大，請縮短內容後再儲存。");
  const raw = await request.text();
  check(new TextEncoder().encode(raw).length <= MAX_BYTES, "草稿太大，請縮短內容後再儲存。");
  let body;
  try { body = JSON.parse(raw); } catch { throw new StudioError("請求格式錯誤。"); }
  check(body && typeof body === "object", "請求格式錯誤。");
  if (action === "check" || action === "preview") {
    validate(body.data, action === "check");
    return action === "check" ? json({valid: true}) : preview(request, env, body);
  }
  if (!["save", "discard", "publish"].includes(action)) return json({error: "找不到這個操作。"}, 404);
  const [source, draft] = await Promise.all([readMain(env), readDraft(env)]);
  if (body.revision !== draft.revision) throw new StudioError("草稿已由其他視窗更新，請先備份再重新載入。", 409);
  if (action === "publish") { validate(body.data, true); return json(await publish(env, source, draft, body)); }
  if (body.baseline !== source.baseline) throw new StudioError("來源內容已更新，請先備份再重新載入。", 409);
  const active = activeDraft(draft, source);
  if (action === "save" && active && active.baseline !== source.baseline) {
    throw new StudioError("這份草稿需要先與新版內容確認。", 409);
  }
  if (action === "save") validate(body.data);
  const saved_at = new Date().toISOString();
  const value = {baseline: source.baseline, data: action === "discard" ? null : body.data, saved_at};
  const revision = await writeDraft(env, value, draft.revision, source.head);
  return json(action === "discard" ? {source: source.data, baseline: source.baseline, revision} : {revision, saved_at});
}
export async function handleStudio(request, env, helpers) {
  const url = new URL(request.url);
  try {
    if (url.pathname === "/admin") return redirect("/admin/");
    if (url.pathname === "/admin/login") {
      if (request.method === "GET") {
        return await authenticated(request, env) ? redirect("/admin/") :
          helpers.html(helpers.loginPage("").replace("</head>", '<meta name="huiying-studio" content="online-v1"></head>'));
      }
      if (request.method !== "POST" || request.headers.get("Origin") !== url.origin) return json({error: "請從登入頁操作。"}, 403);
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      if (await helpers.isLocked(ip)) return helpers.html(helpers.loginPage("請 15 分鐘後再試。"), 429);
      if (!env.ADMIN_PASSWORD || !env.GITHUB_TOKEN) return helpers.html(helpers.loginPage("後台尚未完成連線設定，請聯絡維護人員。"), 503);
      const form = await request.formData();
      if (!await helpers.safeEqual(String(form.get("password") || ""), env.ADMIN_PASSWORD)) {
        await helpers.recordFail(ip);
        return helpers.html(helpers.loginPage("密碼錯誤，請重新輸入。"), 401);
      }
      await helpers.clearFails(ip);
      return redirect("/admin/", await sessionCookie(env, url.origin));
    }
    if (!await authenticated(request, env)) {
      return url.pathname.startsWith("/admin/api/") ? json({error: "登入已逾時，請重新登入後再儲存。"}, 401) : redirect("/admin/login");
    }
    if (url.pathname === "/admin/logout" && request.method === "POST") {
      if (request.headers.get("Origin") !== url.origin) return json({error: "請從後台操作。"}, 403);
      return redirect("/admin/login", `${COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`);
    }
    if (url.pathname.startsWith("/admin/api/")) return await api(request, env);
    const asset = await env.ASSETS.fetch(request);
    const headers = new Headers(asset.headers);
    headers.set("Cache-Control", "no-store");
    headers.set("X-Robots-Tag", "noindex, nofollow");
    headers.set("X-Frame-Options", "SAMEORIGIN");
    return new Response(asset.body, {status: asset.status, headers});
  } catch (error) {
    return json({error: error instanceof StudioError ? error.message : "後台暫時無法完成操作，請保留草稿並稍後重試。"},
      error instanceof StudioError ? error.status : 503);
  }
}
