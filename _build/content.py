# -*- coding: utf-8 -*-
"""讀取 content/ 資料檔（後台編輯的內容），轉成產生器使用的結構。

後台存的是一般人看得懂的格式（**粗體**、{k,v} 物件），這裡轉回 HTML 與 tuple。
"""
import os, re, json, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = os.path.join(ROOT, "content")


def _load(rel):
    return json.load(open(os.path.join(C, rel), encoding="utf-8"))


def inline(x):
    """**粗體** → <b>粗體</b>；遞迴處理 list / dict"""
    if isinstance(x, str):
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", x.strip())
    if isinstance(x, list):
        return [inline(i) for i in x]
    if isinstance(x, dict):
        return {k: inline(v) for k, v in x.items()}
    return x


def _spec(items):
    return [(i["k"], i["v"]) for i in items or []]


def _src(path):
    """/assets/img/x.jpg → assets/img/x.jpg（產生器用相對路徑）"""
    return (path or "").lstrip("/")


def _sections(secs):
    out = []
    for s in secs or []:
        s = dict(s)
        s["p"] = [p for p in s.get("p") or [] if p and p.strip()]
        s["list"] = [x for x in s.get("list") or [] if x and x.strip()]
        if not s["list"]:
            s.pop("list")
        t = s.get("table")
        rows = [r.get("cells") or [] for r in (t or {}).get("rows") or [] if isinstance(r, dict)]
        rows = [r for r in rows if any(c.strip() for c in r)]
        if rows:
            s["table"] = {"head": (t.get("head") or []), "rows": rows}
        else:
            s.pop("table", None)
        lk = s.get("link") or {}
        if lk.get("text") and lk.get("href"):
            s["link"] = [lk["text"], lk["href"]]
        else:
            s.pop("link", None)
        out.append(s)
    return out


def _published(d):
    return not d.get("draft")


COMPANY = _load("company.json")

DATA, EPOXY, ARTICLES, SOLUTIONS = {}, {}, {}, {}
for lang in ("zh", "en"):
    wp = _load(f"{lang}/waterproofing.json")
    st = _load(f"{lang}/stone.json")
    DATA[lang] = {
        "SERIES": [dict(inline(s), spec=_spec(s.get("spec"))) for s in wp["series"]],
        "STONE_PRODUCTS": inline(st["products"]),
        "STONE_SWATCHES": [dict(s, img=_src(s["img"])) for s in st["swatches"]],
        "STONE_SYSTEM": inline(st.get("steps", [])),
    }
    e = inline(_load(f"{lang}/epoxy.json"))
    e["series"] = [dict(s, spec=_spec(s.get("spec"))) for s in e["series"]]
    e["faq"] = [(f["q"], f["a"]) for f in e["faq"]]
    EPOXY[lang] = e

    arts = []
    for f in glob.glob(os.path.join(C, lang, "articles", "*.json")):
        a = json.load(open(f, encoding="utf-8"))
        if not _published(a):
            continue
        a = inline(a)
        a["slug"] = os.path.splitext(os.path.basename(f))[0]
        a["hero"] = _src(a["hero"])
        a["sections"] = _sections(a["sections"])
        arts.append(a)
    ARTICLES[lang] = sorted(arts, key=lambda a: (a["date"], a["slug"]))

    sols = []
    for f in glob.glob(os.path.join(C, lang, "solutions", "*.json")):
        s = inline(json.load(open(f, encoding="utf-8")))
        s["slug"] = os.path.splitext(os.path.basename(f))[0]
        s["sections"] = _sections(s["sections"])
        sols.append(s)
    SOLUTIONS[lang] = sorted(sols, key=lambda s: s.get("order", 99))


# ── 數量（首頁卡片、關於頁等處的「七大系列」「15 組色系」自動計算）
_ZH_NUM = "零一二三四五六七八九十"
_EN_NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
           "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def _zh(n):
    if n <= 10:
        return _ZH_NUM[n]
    if n < 20:
        return "十" + (_ZH_NUM[n - 10] if n > 10 else "")
    return str(n)


def _en(n):
    return _EN_NUM[n] if n < len(_EN_NUM) else str(n)


def _counts():
    n_wp = len(DATA["zh"]["SERIES"])
    n_sw = len(DATA["zh"]["STONE_SWATCHES"])
    n_epx = len([s for s in EPOXY["zh"]["series"] if s["id"] not in ("primer", "body")])
    out = {}
    for key, n in (("WP", n_wp), ("SW", n_sw), ("EPX", n_epx)):
        out[f"N_{key}"] = str(n)
        out[f"N_{key}_ZH"] = _zh(n)
        out[f"N_{key}_EN"] = _en(n).capitalize()
        out[f"n_{key}_en"] = _en(n)
    return out


def tokens():
    """產生器原始碼與範本裡的 %%代號%% → 實際值"""
    c = COMPANY
    intl = lambda t: "+886-" + t[1:] if t.startswith("0") else t
    t = {
        "NAME_ZH": c["name_zh"], "NAME_EN": c["name_en"], "TAX": c["tax_id"],
        "TEL1_INTL": intl(c["tel1"]), "TEL2_INTL": intl(c["tel2"]), "FAX_INTL": intl(c["fax"]),
        "TEL1": c["tel1"], "TEL2": c["tel2"], "FAX": c["fax"], "EMAIL": c["email"],
        "ADDR_ZH_FULL": f'{c["postcode"]} {c["address_zh"]}', "ADDR_ZH": c["address_zh"],
        "ADDR_EN_FULL": f'{c["address_en"]} {c["postcode"]}, Taiwan', "ADDR_EN": f'{c["address_en"]}, Taiwan',
        "POSTCODE": c["postcode"], "LD_STREET": c["ld_street"], "LD_DISTRICT": c["ld_district"], "LD_CITY": c["ld_city"],
    }
    t.update(_counts())
    return t


def fill(text):
    for k, v in tokens().items():
        text = text.replace(f"%%{k}%%", v)
    left = re.findall(r"%%[A-Za-z_]+%%", text)
    if left:
        raise ValueError(f"未定義的代號：{sorted(set(left))}")
    return text
