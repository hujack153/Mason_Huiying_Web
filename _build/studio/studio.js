"use strict";

const byId = id => document.getElementById(id);
const languages = ["zh", "en"];
const labels = {h1: "首頁主標", lead: "首頁引言"};
const productFields = {name: "產品名稱", tagline: "簡短介紹", desc: "產品說明", use: "適用部位"};
const newProduct = id => ({id, name: "", tagline: "", desc: "", use: "", feat: [], spec: []});
const homeFrame = byId("home-preview");
const catalogFrame = byId("catalog-preview");
const productDialog = byId("product-dialog");
const previewRequests = new WeakMap();
let state, data, product;
let dirty = false;
let busy = false;
let savePromise = null;
let saveTimer;
let saveBlocked = false;
let reviewReady = false;
let lastTextEdit = null;
const history = [];
const languageNames = {zh: "中文", en: "英文"};
const online = /^\/admin(?:\/|$)/.test(location.pathname);
const apiRoot = online ? "/admin/api/" : "/api/";
let deploymentTimer;

function status(message, error = false) {
  byId("status").textContent = message;
  byId("status").classList.toggle("error", error);
}

function controls() {
  const saving = busy || !!savePromise;
  byId("save").disabled = saving || !state || !dirty || saveBlocked || stale();
  byId("save").textContent = savePromise ? "儲存中…" : "立即儲存";
  byId("reset").disabled = saving || !state || (!dirty && !state.draft);
  byId("undo").disabled = saving || !history.length || saveBlocked || stale();
  byId("review").disabled = saving || !state || !data || !changes().length || saveBlocked || stale();
  byId("export").disabled = saving || !state?.draft || dirty || !reviewReady || saveBlocked || stale();
}

function stale() {
  return !!state.draft && state.draft.baseline !== state.baseline;
}

function markChanged() {
  reviewReady = false;
  dirty = JSON.stringify(data) !== JSON.stringify(state.draft?.data || state.source);
  status(dirty ? "修改中，將自動儲存…" : "所有修改已儲存。");
  clearTimeout(saveTimer);
  if (dirty && !saveBlocked && !stale()) {
    saveTimer = setTimeout(() => saveDraft().catch(saveError), online ? 1600 : 800);
  }
  controls();
}

function remember() {
  lastTextEdit = null;
  history.push(structuredClone(data));
  if (history.length > 30) history.shift();
}

function saveError(error) {
  if (error.conflict) {
    saveBlocked = true;
    byId("recovery").hidden = false;
  }
  status("草稿尚未儲存。" + error.message, true);
  controls();
}

function saveDraft() {
  clearTimeout(saveTimer);
  if (savePromise) return savePromise;
  if (saveBlocked || stale()) return Promise.reject(new Error("請先處理版本更新提示。"));
  savePromise = (async () => {
    while (dirty) {
      const snapshot = structuredClone(data);
      status("正在儲存草稿…");
      const response = await request("save", {
        data: snapshot, baseline: state.baseline, revision: state.revision,
      });
      const saved = await response.json();
      state.revision = saved.revision;
      state.draft = {baseline: state.baseline, data: snapshot, saved_at: saved.saved_at};
      dirty = JSON.stringify(data) !== JSON.stringify(snapshot);
      if (!dirty) status("草稿已自動儲存 · " + new Date(saved.saved_at).toLocaleTimeString("zh-TW", {
        hour: "2-digit", minute: "2-digit",
      }));
    }
  })().finally(() => {
    savePromise = null;
    controls();
  });
  controls();
  return savePromise;
}

async function request(action, payload) {
  const response = await fetch(apiRoot + action, payload === undefined ? {} : {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    if (online && response.status === 401) byId("login-reminder").hidden = false;
    let message = "操作未完成，請確認工作台的啟動視窗仍開著，再試一次。";
    try { message = (await response.json()).error || message; } catch {}
    const error = new Error(message);
    error.conflict = response.status === 409;
    throw error;
  }
  if (online) byId("login-reminder").hidden = true;
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
  lastTextEdit = null;
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
  const lang = byId("page-language").value;
  const key = byId("home-field").value;
  const now = Date.now();
  if (!lastTextEdit || lastTextEdit.field !== lang + key || now - lastTextEdit.at > 1200) remember();
  lastTextEdit = {field: lang + key, at: now};
  data.home[lang][key] = event.target.value;
  markChanged();
  setPreviewText();
});
byId("locate-field").addEventListener("click", () => {
  const element = homeFrame.contentDocument.querySelector('[data-edit-key="' + byId("home-field").value + '"]');
  element?.scrollIntoView({block: "center", behavior: "smooth"});
  element?.focus({preventScroll: true});
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
  remember();
  [order[index], order[next]] = [order[next], order[index]];
  sortProducts(order);
  catalogChanged();
  Array.from(byId("products").querySelectorAll("tr")).find(row => row.dataset.code === code)?.querySelector("button")?.focus();
}

function archiveProduct(code, archived) {
  const refs = Object.hasOwn(state.references, code) ? state.references[code] : [];
  if (archived && refs.length && !confirm("有 " + refs.length + " 處內容連到這個系列，隱藏後需要請維護人員調整連結。確定從預覽隱藏？")) {
    return;
  }
  remember();
  for (const lang of languages) {
    const item = entry(code, lang);
    if (!item) continue;
    if (archived) item.archived = true;
    else delete item.archived;
  }
  catalogChanged();
  status(archived ? "已從草稿預覽隱藏，可按「恢復顯示」或「復原上一步」。" : "已恢復草稿中的顯示。");
}

function renderProducts() {
  const body = byId("products");
  const order = codes();
  const search = byId("product-search").value.trim().toLocaleLowerCase();
  const filter = byId("product-filter").value;
  let visible = 0;
  body.replaceChildren();
  order.forEach((code, index) => {
    const translations = languages.map(lang => entry(code, lang));
    const [zh, en] = translations;
    const name = zh?.name || en?.name || code;
    const missing = languages.filter((lang, i) => !translations[i] ||
      !Object.keys(productFields).every(key => translations[i][key]?.trim()));
    const archived = translations.filter(Boolean).every(item => item.archived);
    const mixed = translations.every(Boolean) && Boolean(zh.archived) !== Boolean(en.archived);
    const names = translations.map(item => item?.name || "").join(" ").toLocaleLowerCase();
    if (!names.includes(search) || (filter === "visible" && archived) ||
        (filter === "archived" && !archived) || (filter === "incomplete" && !missing.length)) return;
    visible++;
    const row = body.insertRow();
    row.dataset.code = code;
    const title = row.insertCell();
    const strong = document.createElement("strong");
    strong.textContent = name;
    const subtitle = document.createElement("div");
    subtitle.className = "muted";
    subtitle.textContent = en?.name || "英文待補";
    title.append(strong, subtitle);
    const completeness = row.insertCell();
    completeness.textContent = missing.length ? "待補 " + missing.map(lang => languageNames[lang]).join("、") : "中英文已填齊";
    if (missing.length) completeness.append(button("補齊內容", () => editProduct(code, missing[0])));
    const badge = document.createElement("span");
    badge.className = archived ? "pill archived" : "pill";
    badge.textContent = mixed ? "雙語顯示設定不同" : archived ? "預覽中隱藏" : "預覽中顯示";
    const stateCell = row.insertCell();
    stateCell.append(badge);
    const originals = languages.map(lang => state.source.waterproofing[lang].series.find(item => item.id === code));
    const changed = originals.some((item, i) => JSON.stringify(item) !== JSON.stringify(translations[i]));
    const changeLabel = document.createElement("div");
    changeLabel.className = changed ? "change-label" : "muted";
    changeLabel.textContent = originals.every(item => !item) ? "新增草稿" : changed ? "內容已修改" : "與來源相同";
    stateCell.append(changeLabel);
    const actions = row.insertCell();
    const group = document.createElement("div");
    group.className = "actions";
    group.append(
      button("編輯", () => editProduct(code), {label: "編輯 " + name}),
      button("上移", () => move(code, -1), {label: "上移 " + name, disabled: index === 0}),
      button("下移", () => move(code, 1), {label: "下移 " + name, disabled: index === order.length - 1}),
      button(archived ? "恢復顯示" : "隱藏", () => archiveProduct(code, !archived), {label: (archived ? "恢復顯示 " : "隱藏 ") + name}),
    );
    actions.append(group);
  });
  if (!visible) {
    const cell = body.insertRow().insertCell();
    cell.colSpan = 4;
    cell.textContent = order.length ? "找不到符合條件的產品，請調整搜尋或顯示範圍。" : "目前沒有產品系列，按「新增產品系列」開始建立。";
  }
  byId("catalog-count").textContent = "顯示 " + visible + " / " + order.length + " 個系列";
}

function editProduct(code, lang = "zh") {
  const archived = languages.some(lang => entry(code, lang)?.archived);
  product = {code, translations: {}};
  for (const lang of languages) {
    const current = entry(code, lang);
    const blank = newProduct(code);
    if (archived) blank.archived = true;
    product.translations[lang] = structuredClone(current || blank);
  }
  product.original = JSON.stringify(product.translations);
  byId("product-heading").textContent = code ? "編輯系列" : "新增系列";
  byId("product-language").value = lang;
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
    wrapper.append(label, input(item[key], label, value => {
      item[key] = value;
      translationProgress();
    }, key === "desc" || key === "use"));
    fields.append(wrapper);
  }
  fields.append(listEditor("特點", item.feat, false), listEditor("規格", item.spec, true));
  translationProgress();
}

function translationProgress() {
  byId("translation-progress").textContent = languages.map(lang => {
    const count = Object.keys(productFields).filter(key => product.translations[lang][key].trim()).length;
    return languageNames[lang] + "必填 " + count + " / 4";
  }).join("　·　");
}

function cancelProduct(event) {
  event?.preventDefault();
  if (byId("product-form").inert) return;
  if (JSON.stringify(product.translations) !== product.original &&
      !confirm("這個產品還有未儲存的修改。確定放棄這些修改並返回？")) return;
  productDialog.close();
}

byId("product-language").addEventListener("change", renderProductFields);
byId("add-product").addEventListener("click", () => data && editProduct(null));
byId("close-product").addEventListener("click", cancelProduct);
productDialog.addEventListener("cancel", cancelProduct);
byId("product-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (!languages.some(lang => product.translations[lang].name.trim())) {
    byId("product-error").textContent = "請先填寫中文或英文的產品名稱，再儲存草稿。";
    byId("product-fields").querySelector("input").focus();
    return;
  }
  const code = product.code || "series-" + crypto.randomUUID().replaceAll("-", "").slice(0, 12);
  const order = codes();
  remember();
  if (!product.code) order.push(code);
  for (const lang of languages) {
    const item = product.translations[lang];
    item.id = code;
    const index = products(lang).findIndex(existing => existing.id === code);
    if (index < 0) products(lang).push(structuredClone(item));
    else products(lang)[index] = structuredClone(item);
  }
  product.code = code;
  sortProducts(order);
  catalogChanged();
  byId("product-form").inert = true;
  byId("save-product").textContent = "正在儲存…";
  try {
    await saveDraft();
    productDialog.close();
  } catch (error) {
    saveError(error);
    byId("product-error").textContent = "草稿尚未存好，請保留視窗並重試。" + error.message;
  } finally {
    byId("product-form").inert = false;
    byId("save-product").textContent = "儲存並返回清單";
  }
});
byId("product-search").addEventListener("input", () => data && renderProducts());
byId("product-filter").addEventListener("change", () => data && renderProducts());

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
    if (error.conflict) saveError(error);
    else status(error.message, true);
  } finally {
    busy = false;
    controls();
  }
}

byId("save").addEventListener("click", () => saveDraft().catch(saveError));

byId("undo").addEventListener("click", () => {
  data = history.pop();
  markChanged();
  renderProducts();
  refreshHome();
  if (!byId("catalog-preview-panel").hidden) refreshCatalog();
});

byId("reset").addEventListener("click", () => {
  if (!confirm("確定捨棄全部首頁與產品的草稿修改？所有內容將回到來源版本。")) return;
  clearTimeout(saveTimer);
  const previous = structuredClone(data);
  const canUndo = !saveBlocked && !stale();
  action("discard", async response => {
    Object.assign(state, await response.json(), {draft: null});
    data = structuredClone(state.source);
    history.length = 0;
    if (canUndo) history.push(previous);
    saveBlocked = false;
    byId("recovery").hidden = true;
    dirty = false;
    refreshHome();
    renderProducts();
    if (!byId("catalog-preview-panel").hidden) refreshCatalog();
    status("已回到來源版本。");
  });
});

byId("export").addEventListener("click", () => action(online ? "publish" : "export", async response => {
  if (online) {
    const published = await response.json();
    try { localStorage.setItem("huiying-pending-publication", JSON.stringify(published)); } catch {}
    byId("review-dialog").close();
    trackDeployment(published);
    saveBlocked = true;
    try {
      state = await (await request("state")).json();
    } catch {
      byId("recovery").hidden = false;
      throw new Error("發布已提交，請重新載入後台以取得最新內容。");
    }
    data = structuredClone(state.draft?.data || state.source);
    dirty = false;
    history.length = 0;
    saveBlocked = false;
    reviewReady = false;
    renderProducts();
    refreshHome();
    if (!byId("catalog-preview-panel").hidden) refreshCatalog();
    status("發布已送出，正在確認網站更新。");
    if (stale()) byId("recovery").hidden = false;
    return;
  }
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = "huiying-content.zip";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  byId("review-dialog").close();
  status("送審檔已下載，請交給網站維護人員確認與發布。");
}));

window.addEventListener("beforeunload", event => {
  if (dirty || (productDialog.open && JSON.stringify(product.translations) !== product.original)) {
    event.preventDefault();
    event.returnValue = "";
  }
});

function changes() {
  const items = [];
  for (const lang of languages) {
    for (const key of Object.keys(labels)) {
      if (data.home[lang][key] !== state.source.home[lang][key]) {
        items.push(languageNames[lang] + " · 修改" + labels[key]);
      }
    }
  }
  const originalCodes = new Set(languages.flatMap(lang => state.source.waterproofing[lang].series.map(item => item.id)));
  for (const code of new Set([...originalCodes, ...codes()])) {
    const current = languages.map(lang => entry(code, lang));
    const original = languages.map(lang => state.source.waterproofing[lang].series.find(item => item.id === code));
    if (JSON.stringify(current) === JSON.stringify(original)) continue;
    const name = current[0]?.name || current[1]?.name || original[0]?.name || "未命名系列";
    const label = original.every(item => !item) ? "新增" : current.every(item => !item) ? "移除" :
      current.every(item => item?.archived) && original.some(item => item && !item.archived) ? "隱藏" :
      original.every(item => item?.archived) && current.some(item => item && !item.archived) ? "恢復顯示" : "修改";
    items.push(label + "產品系列 · " + name);
  }
  if (languages.some(lang => {
    const oldOrder = state.source.waterproofing[lang].series.map(item => item.id).filter(code => codes().includes(code));
    const newOrder = products(lang).map(item => item.id).filter(code => originalCodes.has(code));
    return JSON.stringify(oldOrder) !== JSON.stringify(newOrder);
  })) items.push("調整產品系列的顯示順序");
  return items;
}

function contentIssues() {
  const issues = [];
  for (const lang of languages) {
    for (const key of Object.keys(labels)) {
      if (!data.home[lang][key].trim()) {
        issues.push({message: languageNames[lang] + labels[key] + "尚未填寫", lang, key});
      }
    }
    for (const code of codes()) {
      const item = entry(code, lang);
      if (item?.archived) continue;
      const name = entry(code, "zh")?.name || entry(code, "en")?.name || "未命名系列";
      const missing = Object.keys(productFields).filter(key => !item?.[key]?.trim());
      if (missing.length) {
        issues.push({message: name + " · " + languageNames[lang] + "待補" +
          missing.map(key => productFields[key]).join("、"), lang, code});
      } else if (item.spec.some(row => !row.k.trim() || !row.v.trim())) {
        issues.push({message: name + " · " + languageNames[lang] + "的規格項目與數值需要一起填寫", lang, code});
      }
    }
  }
  return issues;
}

function fixIssue(issue) {
  byId("review-dialog").close();
  if (issue.code) {
    workspace("catalog");
    editProduct(issue.code, issue.lang);
  } else {
    workspace("page");
    byId("page-language").value = issue.lang;
    refreshHome();
    selectField(issue.key, true);
  }
}

byId("review").addEventListener("click", async () => {
  try {
    await saveDraft();
    busy = true;
    controls();
    const list = byId("change-summary");
    list.replaceChildren();
    for (const message of changes()) {
      const item = document.createElement("li");
      item.textContent = message;
      list.append(item);
    }
    const issues = contentIssues();
    const panel = byId("review-issues");
    panel.replaceChildren();
    reviewReady = false;
    for (const issue of issues) {
      const row = document.createElement("div");
      row.className = "issue-row";
      const text = document.createElement("p");
      text.textContent = issue.message;
      row.append(text, button("前往補齊", () => fixIssue(issue)));
      panel.append(row);
    }
    if (!issues.length) {
      try {
        await request("check", {data});
        panel.textContent = online ? "必填內容已填齊，可以發布到網站。" : "必填內容已填齊，可以下載送審檔。";
        reviewReady = true;
      } catch (error) {
        panel.textContent = error.message;
      }
    }
    byId("review-dialog").showModal();
  } catch (error) {
    saveError(error);
  } finally {
    busy = false;
    controls();
  }
});
byId("close-review").addEventListener("click", () => byId("review-dialog").close());

byId("backup").addEventListener("click", () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify({baseline: state.baseline, data}, null, 2)], {
    type: "application/json",
  }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "huiying-draft-backup.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
byId("reload").addEventListener("click", () => location.reload());

function trackDeployment(published, attempt = 0) {
  clearTimeout(deploymentTimer);
  const panel = byId("deployment-status");
  panel.hidden = false;
  panel.textContent = "發布已提交，網站正在建置更新，請稍候…";
  request("deployment").then(response => response.json()).then(deployed => {
    if (deployed.baseline === published.baseline) {
      try { localStorage.removeItem("huiying-pending-publication"); } catch {}
      panel.replaceChildren("網站已更新。");
      const link = document.createElement("a");
      link.href = "/";
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = "開啟網站查看";
      panel.append(link);
    } else if (attempt < 59) {
      deploymentTimer = setTimeout(() => trackDeployment(published, attempt + 1), 5000);
    } else {
      panel.replaceChildren("網站尚未完成這次更新，請稍後再確認，或聯絡維護人員檢查建置結果。");
      panel.append(button("重新確認", () => trackDeployment(published)));
    }
  }).catch(() => {
    panel.replaceChildren("暫時無法確認網站更新進度。");
    panel.append(button("重新確認", () => trackDeployment(published)));
  });
}

async function start() {
  try {
    if (online) {
      byId("storage-description").textContent = "修改文字或管理產品，草稿會自動儲存。確認預覽後即可發布。";
      byId("publish-step").textContent = "發布到網站";
      byId("review").textContent = "檢查修改並發布";
      byId("review-description").textContent = "請確認這次的修改與預覽，按下發布後，網站會開始更新。";
      byId("export").textContent = "確認發布到網站";
      byId("footer-description").textContent = "草稿自動儲存於後台。按下發布後，網站更新進度會顯示在上方。";
      byId("advanced-link").hidden = false;
      byId("logout").hidden = false;
    }
    state = await (await request("state")).json();
    data = structuredClone(state.draft?.data || state.source);
    controls();
    refreshHome();
    renderProducts();
    if (stale()) {
      byId("recovery").hidden = false;
      status(state.draft?.unreadable ? "後台連線金鑰已更換或草稿無法讀取，請捨棄舊草稿後重新編輯。" :
        "內容已有新版本，請先備份目前草稿。", true);
    } else status(state.draft ? "已載入上次儲存的草稿，繼續編輯即可。" : "已載入來源內容。修改後會自動儲存草稿。");
    if (online) {
      try {
        const pending = JSON.parse(localStorage.getItem("huiying-pending-publication"));
        if (pending?.baseline) trackDeployment(pending);
      } catch {}
    }
  } catch (error) {
    status(error.message, true);
  }
}

start();
