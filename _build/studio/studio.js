"use strict";

const byId = id => document.getElementById(id);
const languages = ["zh", "en"];
const labels = {h1: "首頁主標", lead: "首頁引言"};
const productFields = {name: "名稱", tagline: "一句話定位", desc: "說明", use: "適用部位"};
const newProduct = id => ({id, name: "", tagline: "", desc: "", use: "", feat: [], spec: []});
const homeFrame = byId("home-preview");
const catalogFrame = byId("catalog-preview");
const productDialog = byId("product-dialog");
const previewRequests = new WeakMap();
let state, data, product;
let dirty = false;
let busy = false;

function status(message, error = false) {
  byId("status").textContent = message;
  byId("status").classList.toggle("error", error);
}

function controls() {
  byId("save").disabled = busy || !state || !dirty || stale();
  byId("reset").disabled = busy || !state || (!dirty && !state.draft);
  byId("export").disabled = busy || !state?.draft || dirty || stale();
}

function stale() {
  return !!state.draft && state.draft.baseline !== state.baseline;
}

function markChanged() {
  dirty = true;
  status("有尚未儲存的修改。");
  controls();
}

async function request(action, payload) {
  const response = await fetch("/api/" + action, payload === undefined ? {} : {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "無法完成操作。");
  }
  return response;
}

async function loadPreview(frame, page, lang) {
  const current = Symbol();
  previewRequests.set(frame, current);
  try {
    const response = await request("preview", {data, page, lang});
    const html = await response.text();
    if (previewRequests.get(frame) === current) {
      frame.dataset.language = lang;
      frame.srcdoc = html;
    }
  } catch (error) {
    if (previewRequests.get(frame) === current) status(error.message, true);
  }
}

function disableNavigation(frame) {
  for (const link of frame.contentDocument.querySelectorAll("a[href]")) {
    const href = link.getAttribute("href");
    if (!href.startsWith("#")) link.removeAttribute("href");
    else link.addEventListener("click", event => {
      event.preventDefault();
      const target = frame.contentDocument.getElementById(href.slice(1));
      if (target?.tagName === "DETAILS") target.open = true;
      target?.scrollIntoView();
    });
  }
}

function setPreviewText() {
  const lang = byId("page-language").value;
  if (homeFrame.dataset.language !== lang) return;
  const copy = data.home[lang];
  for (const element of homeFrame.contentDocument.querySelectorAll("[data-edit-key]")) {
    const key = element.dataset.editKey;
    const lines = key === "h1" ? copy[key].split(/\r?\n/) : [copy[key]];
    element.replaceChildren();
    lines.forEach((line, index) => {
      if (index) element.append(homeFrame.contentDocument.createElement("br"));
      element.append(line);
    });
    element.classList.toggle("studio-selected", byId("home-field").value === key);
  }
}

function selectField(key, focus = false) {
  byId("home-field").value = key;
  byId("home-label").textContent = labels[key];
  byId("home-text").value = data.home[byId("page-language").value][key];
  byId("home-hint").textContent = key === "h1"
    ? "主標可以換行。修改會即時反映在預覽。"
    : "修改引言時，預覽會即時更新。";
  setPreviewText();
  if (focus) byId("home-text").focus();
}

homeFrame.addEventListener("load", () => {
  if (!data || !homeFrame.contentDocument.querySelector("[data-edit-key]")) return;
  disableNavigation(homeFrame);
  const doc = homeFrame.contentDocument;
  const style = doc.createElement("style");
  style.textContent = `
    [data-edit-key] { cursor: pointer; outline: 2px dashed #f5d181; outline-offset: 4px; min-height: 1em; }
    [data-edit-key]:focus, [data-edit-key].studio-selected { outline-style: solid; }
  `;
  doc.head.append(style);
  for (const element of doc.querySelectorAll("[data-edit-key]")) {
    const key = element.dataset.editKey;
    element.tabIndex = 0;
    element.setAttribute("role", "button");
    element.setAttribute("aria-label", "編輯" + labels[key]);
    element.addEventListener("click", () => selectField(key, true));
    element.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectField(key, true);
      }
    });
  }
  setPreviewText();
});
catalogFrame.addEventListener("load", () => disableNavigation(catalogFrame));

function refreshHome() {
  const lang = byId("page-language").value;
  selectField(byId("home-field").value);
  loadPreview(homeFrame, "home", lang);
}

byId("home-field").addEventListener("change", event => data && selectField(event.target.value));
byId("page-language").addEventListener("change", () => data && refreshHome());
byId("viewport").addEventListener("change", event => homeFrame.classList.toggle("mobile", event.target.value === "mobile"));
byId("home-text").addEventListener("input", event => {
  if (!data) return;
  data.home[byId("page-language").value][byId("home-field").value] = event.target.value;
  markChanged();
  setPreviewText();
});

function products(lang) {
  return data.waterproofing[lang].series;
}

function codes() {
  return [...new Set(languages.flatMap(lang => products(lang).map(item => item.id)))];
}

function entry(code, lang) {
  return products(lang).find(item => item.id === code);
}

function button(text, action, {label, disabled = false} = {}) {
  const element = document.createElement("button");
  element.type = "button";
  element.textContent = text;
  element.disabled = disabled;
  if (label) element.setAttribute("aria-label", label);
  element.addEventListener("click", action);
  return element;
}

function catalogChanged() {
  markChanged();
  renderProducts();
  if (!byId("catalog-preview-panel").hidden) refreshCatalog();
}

function sortProducts(order) {
  const positions = new Map(order.map((code, index) => [code, index]));
  for (const lang of languages) {
    products(lang).sort((a, b) => positions.get(a.id) - positions.get(b.id));
  }
}

function move(code, offset) {
  const order = codes();
  const index = order.indexOf(code);
  const next = index + offset;
  [order[index], order[next]] = [order[next], order[index]];
  sortProducts(order);
  catalogChanged();
  byId("products").querySelectorAll("tr")[next]?.querySelector("button")?.focus();
}

function archiveProduct(code, archived) {
  const refs = Object.hasOwn(state.references, code) ? state.references[code] : [];
  if (archived && refs.length && !confirm("以下檔案引用這個系列，下架後連結會失效。確定下架？\n" + refs.join("\n"))) {
    return;
  }
  for (const lang of languages) {
    const item = entry(code, lang);
    if (!item) continue;
    if (archived) item.archived = true;
    else delete item.archived;
  }
  catalogChanged();
}

function renderProducts() {
  const body = byId("products");
  const order = codes();
  body.replaceChildren();
  if (!order.length) {
    const cell = body.insertRow().insertCell();
    cell.colSpan = 4;
    cell.textContent = "目前沒有系列。可用「新增系列」建立第一筆。";
  }
  order.forEach((code, index) => {
    const translations = languages.map(lang => entry(code, lang));
    const [zh, en] = translations;
    const name = zh?.name || en?.name || code;
    const missing = languages.filter((lang, i) => !translations[i] ||
      !Object.keys(productFields).every(key => translations[i][key]?.trim()));
    const archived = translations.filter(Boolean).every(item => item.archived);
    const mixed = translations.every(Boolean) && Boolean(zh.archived) !== Boolean(en.archived);
    const row = body.insertRow();
    const title = row.insertCell();
    const strong = document.createElement("strong");
    strong.textContent = name;
    const subtitle = document.createElement("div");
    subtitle.className = "muted";
    subtitle.textContent = [code, zh?.name && en?.name].filter(Boolean).join(" · ");
    title.append(strong, subtitle);
    row.insertCell().textContent = missing.length ? "待補 " + missing.map(lang => lang === "zh" ? "中文" : "英文").join("、") : "中英文完整";
    const badge = document.createElement("span");
    badge.className = archived ? "pill archived" : "pill";
    badge.textContent = mixed ? "雙語狀態不一致" : archived ? "已下架" : missing.length ? "內容待補" : "上架";
    row.insertCell().append(badge);
    const actions = row.insertCell();
    const group = document.createElement("div");
    group.className = "actions";
    group.append(
      button("編輯", () => editProduct(code), {label: "編輯 " + name}),
      button("上移", () => move(code, -1), {label: "上移 " + name, disabled: index === 0}),
      button("下移", () => move(code, 1), {label: "下移 " + name, disabled: index === order.length - 1}),
      button(archived ? "恢復" : "下架", () => archiveProduct(code, !archived), {label: (archived ? "恢復 " : "下架 ") + name}),
    );
    actions.append(group);
  });
}

function editProduct(code) {
  const archived = languages.some(lang => entry(code, lang)?.archived);
  product = {code, translations: {}};
  for (const lang of languages) {
    const current = entry(code, lang);
    const blank = newProduct(code);
    if (archived) blank.archived = true;
    product.translations[lang] = structuredClone(current || blank);
  }
  byId("product-heading").textContent = code ? "編輯系列" : "新增系列";
  byId("product-id").value = code || "";
  byId("product-id").readOnly = !!code;
  byId("product-language").value = "zh";
  byId("product-error").textContent = "";
  renderProductFields();
  productDialog.showModal();
}

function input(value, label, update, multiline = false) {
  const field = document.createElement(multiline ? "textarea" : "input");
  field.value = value;
  field.maxLength = 6000;
  if (multiline) field.rows = 3;
  field.setAttribute("aria-label", label);
  field.addEventListener("input", () => update(field.value));
  return field;
}

function listEditor(title, rows, isSpec) {
  const fieldset = document.createElement("fieldset");
  const legend = document.createElement("legend");
  legend.textContent = title;
  fieldset.append(legend);
  rows.forEach((row, index) => {
    const group = document.createElement("div");
    group.className = "list-row";
    if (isSpec) {
      group.append(input(row.k, "規格項目 " + (index + 1), value => { row.k = value; }));
      group.append(input(row.v, "規格數值 " + (index + 1), value => { row.v = value; }));
    } else {
      group.append(input(row, "特點 " + (index + 1), value => { rows[index] = value; }));
    }
    group.append(button("移除", () => {
      rows.splice(index, 1);
      renderProductFields();
      byId("product-fields").querySelectorAll("fieldset")[isSpec ? 1 : 0].querySelector("button:last-child")?.focus();
    }, {label: "移除" + title + " " + (index + 1)}));
    fieldset.append(group);
  });
  fieldset.append(button("新增" + title, () => {
    rows.push(isSpec ? {k: "", v: ""} : "");
    renderProductFields();
    const inputs = byId("product-fields").querySelectorAll("fieldset")[isSpec ? 1 : 0].querySelectorAll("input");
    inputs[inputs.length - (isSpec ? 2 : 1)].focus();
  }));
  return fieldset;
}

function renderProductFields() {
  const lang = byId("product-language").value;
  const item = product.translations[lang];
  const fields = byId("product-fields");
  fields.replaceChildren();
  for (const [key, label] of Object.entries(productFields)) {
    const wrapper = document.createElement("label");
    wrapper.append(label, input(item[key], label, value => { item[key] = value; }, key === "desc" || key === "use"));
    fields.append(wrapper);
  }
  fields.append(listEditor("特點", item.feat, false), listEditor("規格", item.spec, true));
}

byId("product-language").addEventListener("change", renderProductFields);
byId("add-product").addEventListener("click", () => data && editProduct(null));
byId("close-product").addEventListener("click", () => productDialog.close());
byId("product-form").addEventListener("submit", event => {
  event.preventDefault();
  const code = byId("product-id").value.trim();
  const order = codes();
  if (!product.code && order.includes(code)) {
    byId("product-error").textContent = "這個代號已存在，請用另一個代號。";
    byId("product-id").focus();
    return;
  }
  if (!product.code) order.push(code);
  for (const lang of languages) {
    const item = product.translations[lang];
    item.id = code;
    const index = products(lang).findIndex(existing => existing.id === code);
    if (index < 0) products(lang).push(item);
    else products(lang)[index] = item;
  }
  sortProducts(order);
  productDialog.close();
  catalogChanged();
});

function refreshCatalog() {
  loadPreview(catalogFrame, "waterproofing", byId("catalog-language").value);
}

byId("preview-catalog").addEventListener("click", () => {
  if (!data) return;
  byId("catalog-preview-panel").hidden = false;
  refreshCatalog();
  byId("catalog-preview-panel").scrollIntoView({block: "nearest"});
});
byId("catalog-language").addEventListener("change", refreshCatalog);

function workspace(page) {
  for (const tab of ["page", "catalog"]) {
    byId(tab + "-tab").setAttribute("aria-pressed", tab === page);
    byId(tab + "-workspace").hidden = tab !== page;
  }
  if (page === "page" && data) refreshHome();
}
byId("page-tab").addEventListener("click", () => workspace("page"));
byId("catalog-tab").addEventListener("click", () => workspace("catalog"));

async function action(name, done) {
  busy = true;
  controls();
  try {
    const response = await request(name, {data, baseline: state.baseline, revision: state.revision});
    await done(response);
  } catch (error) {
    status(error.message, true);
  } finally {
    busy = false;
    controls();
  }
}

byId("save").addEventListener("click", () => {
  const snapshot = structuredClone(data);
  action("save", async response => {
    state.revision = (await response.json()).revision;
    state.draft = {baseline: state.baseline, data: snapshot};
    dirty = JSON.stringify(data) !== JSON.stringify(snapshot);
    status(dirty ? "已儲存送出時的草稿。畫面上還有新的修改。" : "草稿已儲存在本機。");
  });
});

byId("reset").addEventListener("click", () => {
  if (!confirm("捨棄整份本機草稿及尚未儲存的修改，回到目前來源？")) return;
  action("discard", async response => {
    Object.assign(state, await response.json(), {draft: null});
    data = structuredClone(state.source);
    dirty = false;
    refreshHome();
    renderProducts();
    if (!byId("catalog-preview-panel").hidden) refreshCatalog();
    status("已重設為目前來源。");
  });
});

byId("export").addEventListener("click", () => action("export", async response => {
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = "huiying-content.zip";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  status("已匯出變更的 JSON，可交給維護人員審核。");
}));

window.addEventListener("beforeunload", event => {
  if (dirty) event.preventDefault();
});

async function start() {
  try {
    state = await (await request("state")).json();
    data = structuredClone(state.draft?.data || state.source);
    controls();
    refreshHome();
    renderProducts();
    if (stale()) status("草稿的來源版本已變更。可檢視舊草稿，重設後可從新來源繼續。", true);
    else status(state.draft ? "已載入本機草稿。" : "已載入網站目前內容。");
  } catch (error) {
    status(error.message, true);
  }
}

start();
