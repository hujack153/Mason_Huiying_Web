import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import {readFile} from "node:fs/promises";
import {webcrypto} from "node:crypto";
import {fingerprint} from "./studio.js";

class Element {
  constructor(tag = "div") {
    this.tag = tag; this.children = []; this.listeners = {}; this.dataset = {};
    this.value = ""; this.hidden = false; this.classList = {toggle() {}};
    this.contentDocument = {querySelectorAll: () => [], querySelector: () => null};
  }
  addEventListener(type, listener) { this.listeners[type] = listener; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute() {}
  showModal() { this.open = true; }
  close() { this.open = false; }
  insertRow() { const row = new Element("tr"); this.append(row); return row; }
  insertCell() { const cell = new Element("td"); this.append(cell); return cell; }
  querySelectorAll(tag) {
    return this.children.flatMap(child => child instanceof Element ?
      [...(child.tag === tag ? [child] : []), ...child.querySelectorAll(tag)] : []);
  }
  querySelector(tag) { return this.querySelectorAll(tag)[0] || null; }
  focus() {}
}

test("online workbench saves, reviews, publishes and verifies the deployed version", async () => {
  const html = await readFile(new URL("../_build/studio/index.html", import.meta.url), "utf8");
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map(match => match[1]));
  const elements = new Map([...ids].map(id => [id, new Element()]));
  for (const id of ["page-language", "product-language", "catalog-language"]) elements.get(id).value = "zh";
  elements.get("home-field").value = "h1";
  elements.get("product-filter").value = "all";
  elements.get("catalog-preview-panel").hidden = true;
  const original = {home: {}, waterproofing: {}};
  for (const kind of Object.keys(original)) {
    for (const lang of ["zh", "en"]) original[kind][lang] = JSON.parse(
      await readFile(new URL(`../content/${lang}/${kind}.json`, import.meta.url)));
  }
  const current = {source: original, baseline: await fingerprint(original), revision: null, draft: null, references: {}};
  const stored = new Map();
  const calls = [];
  const document = {
    getElementById(id) { assert(ids.has(id), "Missing element " + id); return elements.get(id); },
    createElement: tag => new Element(tag),
  };
  const context = vm.createContext({
    document, window: {addEventListener() {}}, console, structuredClone, crypto: webcrypto,
    location: {pathname: "/admin/"},
    localStorage: {
      setItem: (key, value) => stored.set(key, value), getItem: key => stored.get(key),
      removeItem: key => stored.delete(key),
    },
    setTimeout: () => 1, clearTimeout() {}, confirm: () => true, Date,
    fetch: async (url, options) => {
      calls.push(url);
      assert(url.startsWith("/admin/api/"));
      const body = options?.body ? JSON.parse(options.body) : null;
      let value = {};
      if (url.endsWith("/state")) value = structuredClone(current);
      else if (url.endsWith("/save")) {
        assert.equal(body.revision, current.revision);
        current.revision = "revision-" + calls.length;
        current.draft = {data: body.data, baseline: body.baseline};
        value = {revision: current.revision, saved_at: new Date().toISOString()};
      } else if (url.endsWith("/publish")) {
        assert.deepEqual(body.data, current.draft.data);
        current.source = body.data;
        current.baseline = await fingerprint(body.data);
        current.draft = null;
        value = {baseline: current.baseline, commit: "published"};
      } else if (url.endsWith("/deployment")) value = {baseline: current.baseline};
      return {ok: true, json: async () => value, text: async () => "<html></html>"};
    },
  });
  const script = (await readFile(new URL("../_build/studio/studio.js", import.meta.url), "utf8")).replace(/start\(\);\s*$/, "");
  vm.runInContext(script, context);
  await vm.runInContext("start()", context);
  assert.equal(elements.get("advanced-link").hidden, false);
  assert.equal(elements.get("export").textContent, "確認發布到網站");
  vm.runInContext('remember(); data.home.zh.h1 = "新的首頁標題"; markChanged();', context);
  await vm.runInContext("saveDraft()", context);
  assert.equal(vm.runInContext("dirty", context), false);
  await elements.get("review").listeners.click();
  assert.equal(elements.get("review-dialog").open, true);
  assert.equal(elements.get("export").disabled, false);
  await elements.get("export").listeners.click();
  await new Promise(setImmediate);
  assert.equal(current.source.home.zh.h1, "新的首頁標題");
  assert.equal(vm.runInContext("saveBlocked", context), false);
  assert.equal(elements.get("review-dialog").open, false);
  assert(elements.get("deployment-status").children.includes("網站已更新。"));
  assert.equal(stored.size, 0);
  assert(!calls.some(url => url.endsWith("/export")));
});
