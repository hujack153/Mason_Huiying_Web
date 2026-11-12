import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import worker from "./worker.js";
import {fingerprint} from "./studio.js";

const origin = "https://huiyingmaterials.com";
const original = {home: {}, waterproofing: {}};
for (const kind of Object.keys(original)) {
  for (const lang of ["zh", "en"]) {
    original[kind][lang] = JSON.parse(await readFile(new URL(`../content/${lang}/${kind}.json`, import.meta.url)));
  }
}
const assetRoot = new URL("../dist", import.meta.url);
const answer = (value, status = 200) => new Response(JSON.stringify(value), {status});
const base64 = value => Buffer.from(JSON.stringify(value)).toString("base64");

function setup() {
  const fixture = {
    head: "main0", snapshots: new Map([["main0", structuredClone(original)]]),
    trees: new Map([["tree-main0", structuredClone(original)]]),
    parents: new Map(), draft: null, revision: null, branch: false, sequence: 0,
    updates: [], writes: [], race: false,
  };
  globalThis.caches = {default: {match: async () => null, delete: async () => true, put: async () => {}}};
  const env = {ADMIN_PASSWORD: "test-password", GITHUB_TOKEN: "test-server-token", ASSETS: {
    async fetch(request) {
      try { return new Response(await readFile(new URL("." + new URL(request.url).pathname, assetRoot + "/"))); }
      catch { return new Response("Not found", {status: 404}); }
    },
  }};
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async (url, options = {}) => {
    assert(String(url).startsWith("https://api.github.com/repos/hujack153/Mason_Huiying_Web/"));
    assert.equal(options.headers.Authorization, "Bearer " + env.GITHUB_TOKEN);
    const parsed = new URL(url);
    const path = parsed.pathname.replace("/repos/hujack153/Mason_Huiying_Web", "");
    const method = options.method || "GET";
    const body = options.body ? JSON.parse(options.body) : null;
    if (method !== "GET") fixture.writes.push({path, method, body});
    if (path === "/git/ref/heads/main") return answer({object: {sha: fixture.head}});
    if (path === "/git/ref/heads/cms/studio") return answer(fixture.branch ? {object: {sha: "draft"}} : {}, fixture.branch ? 200 : 404);
    if (path === "/git/refs" && method === "POST") {
      if (fixture.branch) return answer({}, 422);
      fixture.branch = true;
      return answer({}, 201);
    }
    if (path === "/contents/.cms/studio-draft.json") {
      if (method === "GET") return answer(fixture.draft ? {sha: fixture.revision, content: base64(fixture.draft)} : {}, fixture.draft ? 200 : 404);
      if ((body.sha || null) !== fixture.revision) return answer({}, 409);
      fixture.draft = JSON.parse(Buffer.from(body.content, "base64"));
      fixture.revision = "draft-" + ++fixture.sequence;
      return answer({content: {sha: fixture.revision}}, 201);
    }
    if (path.startsWith("/contents/content/")) {
      const [, lang, kind] = path.match(/content\/(zh|en)\/(home|waterproofing)\.json/);
      const snapshot = fixture.snapshots.get(parsed.searchParams.get("ref"));
      assert(snapshot, "Content reads must use a pinned commit");
      return answer({content: base64(snapshot[kind][lang])});
    }
    if (path.startsWith("/git/commits/") && method === "GET") {
      return answer({tree: {sha: "tree-" + path.split("/").at(-1)}});
    }
    if (path === "/git/trees") {
      const data = structuredClone(fixture.trees.get(body.base_tree));
      for (const entry of body.tree) {
        const match = entry.path.match(/^content\/(zh|en)\/(home|waterproofing)\.json$/);
        assert(match, "Only the four allowed content files can be published");
        data[match[2]][match[1]] = JSON.parse(entry.content);
      }
      const sha = "tree-" + ++fixture.sequence;
      fixture.trees.set(sha, data);
      return answer({sha}, 201);
    }
    if (path === "/git/commits") {
      const sha = "commit-" + ++fixture.sequence;
      const data = fixture.trees.get(body.tree);
      fixture.snapshots.set(sha, structuredClone(data));
      fixture.trees.set("tree-" + sha, structuredClone(data));
      fixture.parents.set(sha, body.parents[0]);
      return answer({sha}, 201);
    }
    if (path === "/git/refs/heads/main" && method === "PATCH") {
      assert.equal(body.force, false);
      if (fixture.race) {
        fixture.head = "other-editor";
        fixture.snapshots.set("other-editor", structuredClone(original));
      }
      if (fixture.parents.get(body.sha) !== fixture.head) return answer({}, 422);
      fixture.head = body.sha;
      fixture.updates.push(body.sha);
      return answer({object: {sha: body.sha}});
    }
    throw new Error("Unexpected GitHub request " + method + " " + path);
  };
  let cookie = "";
  async function request(path, {data, method = data ? "POST" : "GET", csrf = origin, session = true} = {}) {
    const headers = {};
    if (session && cookie) headers.Cookie = cookie;
    if (data) { headers.Origin = csrf; headers["Content-Type"] = "application/json"; }
    return worker.fetch(new Request(origin + path, {
      method, headers, body: data ? JSON.stringify(data) : undefined,
    }), env);
  }
  async function login() {
    const result = await worker.fetch(new Request(origin + "/admin/login", {
      method: "POST", headers: {Origin: origin, "Content-Type": "application/x-www-form-urlencoded"},
      body: "password=test-password",
    }), env);
    assert.equal(result.status, 303);
    const header = result.headers.get("Set-Cookie");
    for (const flag of ["HttpOnly", "Secure", "SameSite=Strict", "Path=/"]) assert(header.includes(flag));
    cookie = header.split(";")[0];
    assert(!(await result.text()).includes(env.GITHUB_TOKEN));
  }
  return {...fixture, fixture, env, request, login, restore: () => {globalThis.fetch = previousFetch;}};
}

test("online login protects studio, encoded paths and API without exposing credentials", async () => {
  const app = setup();
  try {
    for (const path of ["/admin/", "/%61dmin/index.html", "/admin%2fstudio.js", "//admin/index.html"]) {
      const result = await app.request(path);
      assert.equal(result.status, 303, path);
      assert.equal(result.headers.get("Location"), "/admin/login");
    }
    assert.equal((await app.request("/admin/api/state")).status, 401);
    const login = await app.request("/admin/login");
    assert.equal(login.headers.get("Referrer-Policy"), "same-origin",
      "Login form privacy policy must preserve Origin on same-origin POSTs");
    assert((await login.text()).includes('content="online-v1"'));
    const crossOriginLogin = await worker.fetch(new Request(origin + "/admin/login", {
      method: "POST", headers: {Origin: "https://evil.example", "Content-Type": "application/x-www-form-urlencoded"},
      body: "password=test-password",
    }), app.env);
    assert.equal(crossOriginLogin.status, 403);
    const opaqueOriginLogin = await worker.fetch(new Request(origin + "/admin/login", {
      method: "POST", headers: {Origin: "null", "Content-Type": "application/x-www-form-urlencoded"},
      body: "password=test-password",
    }), app.env);
    assert.equal(opaqueOriginLogin.status, 403);
    await app.login();
    const state = await (await app.request("/admin/api/state")).json();
    assert.equal(state.baseline, await fingerprint(original));
    assert(!JSON.stringify(state).includes(app.env.GITHUB_TOKEN));
    assert.equal((await app.request("/admin/api/save", {data: {}, csrf: "https://evil.example"})).status, 403);
    app.env.ADMIN_PASSWORD = "rotated-password";
    assert.equal((await app.request("/admin/api/state")).status, 401);
  } finally { app.restore(); }
});

test("drafts persist separately and publish all changed files atomically to main", async () => {
  const app = setup();
  try {
    await app.login();
    const state = await (await app.request("/admin/api/state")).json();
    const data = structuredClone(state.source);
    data.home.zh.h1 = "測試標題 <script>\n第二行";
    for (const lang of ["zh", "en"]) data.waterproofing[lang].series[0].archived = true;
    let payload = {data, baseline: state.baseline, revision: state.revision};
    const saved = await (await app.request("/admin/api/save", {data: payload})).json();
    assert(saved.saved_at);
    assert.equal(app.fixture.head, "main0");
    assert.equal((await app.request("/admin/api/save", {data: payload})).status, 409);
    payload.revision = saved.revision;
    const preview = await app.request("/admin/api/preview", {data: {data, page: "home", lang: "zh"}});
    assert.equal(preview.status, 200);
    const home = await preview.text();
    assert(home.includes("測試標題 &lt;script&gt;<br>第二行"));
    assert(home.includes("6 大系列"));
    const product = await (await app.request("/admin/api/preview", {data: {data, page: "waterproofing", lang: "en"}})).text();
    assert(!product.includes('id="primer"'));
    assert(product.includes('id="compound"'));
    assert(!product.includes("__STUDIO_ROWS__"));
    const result = await app.request("/admin/api/publish", {data: payload});
    assert.equal(result.status, 200, await result.clone().text());
    const published = await result.json();
    assert.equal(published.baseline, await fingerprint(data));
    assert.deepEqual(app.fixture.snapshots.get(app.fixture.head), data);
    assert.equal(app.fixture.updates.length, 1);
    assert.equal(app.fixture.writes.find(write => write.path === "/git/trees").body.tree.length, 3);
    assert.equal((await app.request("/admin/api/publish", {data: payload})).status, 200, "Publication retry is idempotent");
    assert.equal(app.fixture.updates.length, 1);
    const next = await (await app.request("/admin/api/state")).json();
    assert.equal(next.draft, null);
    assert.equal(next.baseline, published.baseline);
    const manifest = await (await app.request("/admin/api/deployment")).json();
    assert.equal(manifest.baseline, state.baseline, "Deployment status reports the built version, not Git main");
    data.home.zh.lead = "下一次修改";
    assert.equal((await app.request("/admin/api/save", {data: {data, baseline: next.baseline, revision: next.revision}})).status, 200);
  } finally { app.restore(); }
});

test("incomplete drafts are allowed; incomplete publication and concurrent main changes are rejected", async () => {
  const app = setup();
  try {
    await app.login();
    const state = await (await app.request("/admin/api/state")).json();
    const data = structuredClone(state.source);
    data.home.en.h1 = "";
    const payload = {data, baseline: state.baseline, revision: state.revision};
    payload.revision = (await (await app.request("/admin/api/save", {data: payload})).json()).revision;
    assert.equal((await app.request("/admin/api/check", {data: {data}})).status, 400);
    assert.equal((await app.request("/admin/api/publish", {data: payload})).status, 400);
    data.home.en.h1 = "Complete";
    payload.revision = (await (await app.request("/admin/api/save", {data: payload})).json()).revision;
    app.fixture.race = true;
    assert.equal((await app.request("/admin/api/publish", {data: payload})).status, 409);
    assert.equal(app.fixture.head, "other-editor");
    assert.equal(app.fixture.updates.length, 0);
    assert(!JSON.stringify(app.fixture.draft).includes("Complete"), "Stored drafts are encrypted");
    const stored = await (await app.request("/admin/api/state")).json();
    assert.equal(stored.draft.data.home.en.h1, "Complete");
  } finally { app.restore(); }
});

test("rotated connection secrets leave the source usable and allow an explicit draft reset", async () => {
  const app = setup();
  try {
    await app.login();
    const state = await (await app.request("/admin/api/state")).json();
    const data = structuredClone(state.source);
    data.home.zh.h1 = "尚未發布的內容";
    const saved = await (await app.request("/admin/api/save", {data: {
      data, baseline: state.baseline, revision: state.revision,
    }})).json();
    assert(!JSON.stringify(app.fixture.draft).includes(data.home.zh.h1));
    app.env.GITHUB_TOKEN = "rotated-token";
    const unreadable = await (await app.request("/admin/api/state")).json();
    assert.equal(unreadable.draft.unreadable, true);
    assert.deepEqual(unreadable.source, original);
    const reset = await app.request("/admin/api/discard", {data: {
      data: original, baseline: unreadable.baseline, revision: saved.revision,
    }});
    assert.equal(reset.status, 200);
    assert.equal((await (await app.request("/admin/api/state")).json()).draft, null);
    assert.equal((await app.request("/admin/logout", {data: {}})).status, 303);
  } finally { app.restore(); }
});

test("preview rendering follows static asset HTML redirects", async () => {
  const app = setup();
  try {
    await app.login();
    const assets = app.env.ASSETS.fetch;
    app.env.ASSETS.fetch = async request => {
      const url = new URL(request.url);
      if (url.pathname.startsWith("/admin/preview/")) {
        if (url.pathname.endsWith(".html")) return new Response(null, {
          status: 307, headers: {Location: url.pathname.slice(0, -5)},
        });
        url.pathname += ".html";
        return assets(new Request(url));
      }
      return assets(request);
    };
    const preview = await app.request("/admin/api/preview", {data: {data: original, page: "home", lang: "zh"}});
    assert.equal(preview.status, 200);
    assert((await preview.text()).includes(original.home.zh.h1.split("\n")[0]));
  } finally { app.restore(); }
});
