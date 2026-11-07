# -*- coding: utf-8 -*-
"""長仿宋版型：圖紙標題欄、頁首、頁尾"""

SITE = "https://huiyingmaterials.com"

def FONT_PRELOAD(up):
    """只預載數值用的窄體子集（8 KB）；中文一律系統黑體"""
    return (f'<link rel="preload" href="{up}assets/font/num-700.woff2" '
            'as="font" type="font/woff2" crossorigin>')

# 圖號索引 —— 全站共 12 張主要圖（中／英名稱）
SHEETS = {
    "index.html": ("01", "封面", "Cover"),
    "waterproofing.html": ("02", "防水材料", "Waterproofing"),
    "stone.html": ("03", "外牆仿石塗料", "Stone-effect coating"),
    "epoxy.html": ("04", "環氧樹脂地坪", "Epoxy flooring"),
    "roof-waterproofing.html": ("05", "屋頂防水", "Roof waterproofing"),
    "bathroom-waterproofing.html": ("06", "浴室與廚房", "Bathrooms and kitchens"),
    "basement-waterproofing.html": ("07", "地下室與擋土牆", "Basements"),
    "exterior-wall-coating.html": ("08", "外牆防水塗裝", "External walls"),
    "parking-floor.html": ("09", "停車場與廠房地坪", "Car parks and factories"),
    "insights/index.html": ("10", "技術專欄", "Insights"),
    "about.html": ("11", "公司資料", "About"),
    "contact.html": ("12", "詢價單", "Enquiry"),
}
TOTAL = "12"

T = {
 "zh": {
   "lang": "zh-Hant-TW", "locale": "zh_TW",
   "co": "暉盈國際事業有限公司", "co2": "Huiying Int'l Business Co.",
   "nav": [("防水材料", "waterproofing.html"), ("仿石塗料", "stone.html"),
           ("環氧地坪", "epoxy.html"), ("技術專欄", "insights/index.html"),
           ("關於暉盈", "about.html")],
   "ask": ("詢價與洽詢", "contact.html"),
   "menu": "選單", "close": "關閉", "switch": "EN", "switch_t": "Switch to English",
   "addr": "%%ADDR_ZH_FULL%%",
   "sheet_of": "第 {n} 張／共 {t} 張", "rev": "版次 2026.07",
   "f_prod": "產品", "f_info": "資訊", "f_contact": "聯絡我們",
   "f_links": [("防水材料", "waterproofing.html"), ("外牆多彩仿石塗料", "stone.html"),
               ("環氧樹脂地坪", "epoxy.html")],
   "f_info_links": [("技術專欄", "insights/index.html"), ("關於暉盈", "about.html"),
                    ("聯絡與詢價", "contact.html")],
   "tax": "統一編號 %%TAX%%",
   "tel": "%%TEL1%%　%%TEL2%%", "fax": "傳真 %%FAX%%",
   "copy": "© 2026 暉盈國際事業有限公司",
   "ask_h": "有工程要估？把圖說寄給我們",
   "ask_p": "提供施作部位、基材狀況、面積與預計工期，我們回覆完整的材料配套建議與用量估算。",
   "ask_b": "填寫詢價單",
   "more": "閱讀全文", "back": "回技術專欄", "pub": "發表",
   "insights": "技術專欄", "photo": "參考照片",
 },
 "en": {
   "lang": "en", "locale": "en_US",
   "co": "Huiying Int'l Business Co.", "co2": "暉盈國際事業有限公司",
   "nav": [("Waterproofing", "waterproofing.html"), ("Stone coating", "stone.html"),
           ("Epoxy flooring", "epoxy.html"), ("Insights", "insights/index.html"),
           ("About", "about.html")],
   "ask": ("Contact", "contact.html"),
   "menu": "Menu", "close": "Close", "switch": "中文", "switch_t": "切換至中文",
   "addr": "%%ADDR_EN_FULL%%",
   "sheet_of": "Sheet {n} of {t}", "rev": "Rev. 2026.07",
   "f_prod": "Products", "f_info": "Information", "f_contact": "Contact",
   "f_links": [("Waterproofing materials", "waterproofing.html"),
               ("Stone-effect wall coating", "stone.html"),
               ("Epoxy resin flooring", "epoxy.html")],
   "f_info_links": [("Insights", "insights/index.html"), ("About Huiying", "about.html"),
                    ("Contact and enquiry", "contact.html")],
   "tax": "Tax ID %%TAX%%",
   "tel": "%%TEL1_INTL%%　%%TEL2_INTL%%", "fax": "Fax %%FAX_INTL%%",
   "copy": "© 2026 Huiying Int'l Business Co.",
   "ask_h": "Have a project to quote?",
   "ask_p": "Send us the location, substrate condition, area and programme, and we will return a full material specification with quantities.",
   "ask_b": "Open the enquiry form",
   "more": "Read more", "back": "Back to insights", "pub": "Published",
   "insights": "Insights", "photo": "Reference photograph",
 }
}


def head(lang, title, desc, path, *, ld="", depth=0, kw=None, art=False, preload=None):
    t = T[lang]
    up = "../" * depth
    zh = path.replace("/en/", "/") if lang == "en" else path
    en = "/en/" if zh == "/" else "/en" + zh
    o = [f'<!doctype html>\n<html lang="{t["lang"]}">\n<head>',
         '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f'<title>{title}</title>',
         f'<meta name="description" content="{desc}">']
    if kw:
        o.append(f'<meta name="keywords" content="{kw}">')
    o += [f'<link rel="canonical" href="{SITE}{path}">',
          f'<link rel="alternate" hreflang="zh-Hant" href="{SITE}{zh}">',
          f'<link rel="alternate" hreflang="en" href="{SITE}{en}">',
          f'<link rel="alternate" hreflang="x-default" href="{SITE}{zh}">',
          '<meta name="robots" content="index, follow, max-image-preview:large">',
          f'<meta name="author" content="{T["zh"]["co"]}">',
          f'<meta property="og:type" content="{"article" if art else "website"}">',
          f'<meta property="og:site_name" content="{t["co"]}">',
          f'<meta property="og:locale" content="{t["locale"]}">',
          f'<meta property="og:url" content="{SITE}{path}">',
          f'<meta property="og:title" content="{title}">',
          f'<meta property="og:description" content="{desc}">',
          f'<meta property="og:image" content="{SITE}/assets/img/brand/og-image.jpg">',
          '<meta property="og:image:width" content="1200">',
          '<meta property="og:image:height" content="630">',
          '<meta name="twitter:card" content="summary_large_image">',
          f'<meta name="twitter:title" content="{title}">',
          f'<meta name="twitter:description" content="{desc}">',
          f'<meta name="twitter:image" content="{SITE}/assets/img/brand/og-image.jpg">',
          f'<link rel="icon" href="/favicon.ico" sizes="any">',
          f'<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/brand/icon-48.png">',
          f'<link rel="icon" type="image/png" sizes="96x96" href="/assets/img/brand/icon-96.png">',
          f'<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/brand/icon-192.png">',
          f'<link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png">',
          f'<link rel="manifest" href="/site.webmanifest">',
          '<meta name="theme-color" content="#24506B">',
          FONT_PRELOAD(up),
          f'<link rel="stylesheet" href="{up}assets/css/site.css">']
    if preload:
        # 版頭大圖優先載入，改善 LCP
        o.append(f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">')
    if ld:
        o.append(ld)
    o.append('</head>\n<body>')
    return "\n".join(o)


def titleblock(lang, key, extra=None):
    """圖紙標題欄已依需求移除；保留函式簽名讓各產生器不需改動"""
    return ""


def masthead(lang, active, depth=0):
    t = T[lang]
    up = "../" * depth
    other = "en" if lang == "zh" else "zh"
    ON = ' class="on"'
    links = "".join(
        f'<a href="{up}{h}"{ON if h == active else ""}>{l}</a>'
        for l, h in t["nav"])
    al, ah = t["ask"]
    ask_cls = "ask on" if ah == active else "ask"
    return f'''
<header class="masthead">
  <div class="page">
    <a class="mark" href="{up}index.html">
      <img src="{up}assets/img/brand/logo-ink.png" alt="Huiying materials" width="115" height="40">
      <span class="nm">{t["co"]}<small>Huiying materials</small></span>
    </a>
    <button class="navbtn" id="navBtn" aria-label="{t["menu"]}" aria-expanded="false">{t["menu"]}</button>
    <nav class="nav" id="nav">
      {links}
      <a class="{ask_cls}" href="{up}{ah}">{al}</a>
      <a class="lang" id="langSwitch" data-target="{other}" href="#" title="{t["switch_t"]}" hreflang="{other}">{t["switch"]}</a>
    </nav>
  </div>
</header>'''


def ask_band(lang, depth=0):
    t = T[lang]
    up = "../" * depth
    return f'''
<section class="ask-band">
  <div class="page">
    <div><h2>{t["ask_h"]}</h2><p>{t["ask_p"]}</p></div>
    <a class="btn" href="{up}contact.html">{t["ask_b"]}</a>
  </div>
</section>'''


def foot(lang, depth=0):
    t = T[lang]
    up = "../" * depth
    prod = "".join(f'<li><a href="{up}{h}">{l}</a></li>' for l, h in t["f_links"])
    info = "".join(f'<li><a href="{up}{h}">{l}</a></li>' for l, h in t["f_info_links"])
    return f'''
<footer class="foot">
  <div class="page">
    <div class="grid">
      <div>
        <img src="{up}assets/img/brand/logo-ink.png" alt="Huiying materials" width="115" height="40">
        <p>{t["co"]}<br>{t["co2"]}<br>{t["tax"]}</p>
      </div>
      <div><h4>{t["f_prod"]}</h4><ul>{prod}</ul></div>
      <div><h4>{t["f_info"]}</h4><ul>{info}</ul></div>
      <div><h4>{t["f_contact"]}</h4>
        <ul>
          <li class="num" style="font-size:16px">{t["tel"]}</li>
          <li>{t["fax"]}</li>
          <li><a href="mailto:%%EMAIL%%">%%EMAIL%%</a></li>
          <li>{t["addr"]}</li>
        </ul>
      </div>
    </div>
    <div class="end"><span>{t["copy"]}</span><span class="num">HUIYING MATERIALS</span></div>
  </div>
</footer>

<script src="{up}assets/js/nav.js"></script>
</body>
</html>'''


def hero(lang, *, photo, h1, lead, tag=None, figure=None, acts=None, sub=False):
    """深色滿版大圖版頭。sub=True 用於次要頁面：固定框高，讓底圖在
       各產品線／部位頁一律等大，不受標題行數或剖面圖層數影響。"""
    right = f'<div>{figure}</div>' if figure else ""
    a = ""
    if acts:
        a = '<div class="acts">' + "".join(
            f'<a class="btn {c}" href="{h}">{l}</a>' for l, h, c in acts) + '</div>'
    tg = f'<span class="tag">{tag}</span>\n      ' if tag else ""
    inner = f'''<div>
      {tg}<h1>{h1}</h1>
      <p class="lead">{lead}</p>{a}
    </div>{right}'''
    wrap = "hero-2col" if figure else ""
    cls = "hero sub" if sub else "hero"
    return f'''
<div class="{cls}">
  <img src="{photo}" alt="" fetchpriority="high" decoding="async">
  <div class="page {wrap}">
    {inner}
  </div>
</div>'''


def plate(src, cap, code, cls=""):
    """參考照片框"""
    return (f'<figure class="plate {cls}"><img loading="lazy" src="{src}" alt="">'
            f'<figcaption><span>{cap}</span><span>{code}</span></figcaption></figure>')


def fig(svg, cap, code, rev=False):
    """剖面圖框"""
    cls = "section-fig rev" if rev else "section-fig"
    return (f'<figure class="{cls}">{svg}'
            f'<figcaption><b>{cap}</b><span>{code}</span></figcaption></figure>')
