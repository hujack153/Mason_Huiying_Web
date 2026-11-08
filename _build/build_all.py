# -*- coding: utf-8 -*-
"""website-v2 全站產生器"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from layout2 import head, titleblock, masthead, ask_band, foot, plate, fig, hero, T, SITE
import figures as F

D = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(D, ".."))
OUT = os.path.join(ROOT, "dist")
# Cloudflare Workers Builds 會帶入 WORKERS_CI_BRANCH；本機建置沒有這個變數，視為正式版
BRANCH = os.environ.get("WORKERS_CI_BRANCH", "main")
PREVIEW = BRANCH != "main"
from content import DATA, fill  # 內容來自 content/（後台編輯）


def ld(*objs):
    return "\n".join('<script type="application/ld+json">\n'
                     + json.dumps(o, ensure_ascii=False, indent=1) + '\n</script>' for o in objs)


def crumb(lang, items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                                for i, (n, u) in enumerate(items)]}


def faq_ld(qas):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}


def list_ld(name, path, items):
    """產品系列的 ItemList 結構化資料：items = [(名稱, 錨點id), ...]"""
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name,
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                 "url": f"{SITE}{path}#{a}"} for i, (n, a) in enumerate(items)]}


def qa_block(qas, title):
    rows = "".join(f'<details><summary>{q}</summary><div class="a">{a}</div></details>' for q, a in qas)
    return (f'<section class="band"><div class="text">'
            f'<div class="cap"><div class="no">FAQ</div><h2>{title}</h2></div>'
            f'<div class="qa">{rows}</div></div></section>')


def write(rel, html):
    p = os.path.join(OUT, rel)
    html = fill(html)
    if PREVIEW and rel.endswith(".html"):
        html = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', html)
        html = html.replace("<body", '<body data-preview="1"', 1)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not html.endswith("\n"):
        html += "\n"
    enc = "utf-8-sig" if rel.endswith(".html") else "utf-8"
    open(p, "w", encoding=enc, newline="\n").write(html)


def uniq_svg_ids(html, ids=("gritr", "h135r", "h45r")):
    """同一頁多張剖面圖時，pattern id 依圖編號加後綴，避免重複 id。"""
    parts = re.split(r"(<svg\b)", html); n = 0; out = [parts[0]]
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        if any(f'id="{x}"' in body for x in ids):
            n += 1; end = body.find("</svg>"); seg = body[:end]
            for x in ids:
                seg = seg.replace(f'id="{x}"', f'id="{x}{n}"').replace(f"url(#{x})", f"url(#{x}{n})")
            body = seg + body[end:]
        out += [parts[i], body]
    return "".join(out)


def pfx(lang):
    return "en/" if lang == "en" else ""


def dep(lang, sub=False):
    return (1 if lang == "en" else 0) + (1 if sub else 0)


# ══════════════════════════════════════════ 首頁

HOME = {
 "zh": dict(
   title="暉盈國際事業有限公司｜防水材料、外牆仿石塗料、環氧樹脂地坪供應商",
   desc="暉盈國際事業有限公司位於新北市新莊區，供應建築防水材料、外牆多彩仿石塗料與環氧樹脂地坪系統，提供材料選配、樣板施作與現場技術支援。電話 %%TEL1%%。",
   kw="防水材料, 外牆仿石塗料, 環氧樹脂地坪, 建材供應商, 新莊 防水材料",
   h1="為每一個工程，<br>配出對的材料",
   lead="從素地封閉、主防水層到面漆保護，我們提供完整的系統配套與技術支援，協助營造、設計與施工單位順利施作。",
   slide_a=("標準三層構成", "五層塗裝結構", "地坪三層構成"),
   slide_s=("防水材料", "仿石塗料", "環氧地坪"),
   lines_no="產品線", lines_h2="三條產品線", lines_p="防水、外牆塗裝與地坪系統，分別對應不同工程條件。",
   lines=[("02", "建築防水材料", "Waterproofing", "waterproofing.html",
           "底漆、複合式防水、彈性水泥、止水與滲透結晶、面漆、透明保護漆與油性 PU 系統。", "%%N_WP%% 大系列",
           "assets/img/photo/hero-4.jpg"),
          ("03", "外牆多彩仿石塗料", "Stone-effect coating", "stone.html",
           "水性多彩仿花崗岩塗料，五層塗裝結構、七道施工工序，仿真度達 90% 以上。", "%%N_SW%% 組色系",
           "assets/img/photo/hero-3.jpg"),
          ("04", "環氧樹脂地坪系統", "Epoxy flooring", "epoxy.html",
           "薄塗面塗、自流平、透明面塗、防靜電、水性地坪與結構補強。", "%%N_EPX%% 套系統",
           "assets/img/floor/epoxy-05.jpg")],
   app_no="施作部位", app_h2="依部位查材料", app_p="從你要施作的部位開始，比從產品分類開始快得多。",
   apps=[("05", "屋頂防水", "roof-waterproofing.html", "平屋頂、鐵皮屋頂的完整配套與參考塗佈量"),
         ("06", "浴室與廚房防水", "bathroom-waterproofing.html", "室內濕區夾層防水的施工順序與細部處理"),
         ("07", "地下室與擋土牆", "basement-waterproofing.html", "迎水面與背水面的差異、既有滲漏處理順序"),
         ("08", "外牆防水與塗裝", "exterior-wall-coating.html", "彈性面漆、隔熱漆、透明保護漆與仿石塗料"),
         ("09", "停車場與廠房地坪", "parking-floor.html", "環氧樹脂地坪系統依場所的選用對照")],
   why_no="服務內容", why_h2="材料只是開始",
   why=[("材料選配", "依施作部位、基材狀況、氣候條件與工期，配出底漆、主防水層與面漆的完整組合，避免不相容的材料混用。"),
        ("樣板與確認", "外牆裝飾工程可先製作樣板，經監造單位與業主確認後，作為施工驗收的比對憑據。"),
        ("供貨與技術支援", "依工程進度分批供貨；開工前可安排施工說明，施作期間持續提供技術協助。")],
   plates=[("assets/img/photo/hero-2.jpg", "外牆塗裝", "PH-01"),
           ("assets/img/floor/epoxy-05.jpg", "停車場地坪", "PH-02"),
           ("assets/img/photo/hero-4.jpg", "屋頂防水", "PH-03")],
 ),
 "en": dict(
   title="Huiying Int'l Business Co.｜Waterproofing, Stone-Effect Coating, Epoxy Flooring｜Taiwan",
   desc="Taiwan supplier of waterproofing materials, stone-effect wall coatings and epoxy flooring. Specification, sample panels and on-site support.",
   kw="waterproofing materials Taiwan, stone effect coating, epoxy flooring Taiwan, building materials supplier",
   h1="The right specification, for every project",
   lead="From substrate sealing through to the protective topcoat, we provide complete system specifications and the technical support to install them correctly.",
   slide_a=("Standard three-layer build-up", "Five-layer coating build-up", "Three-stage floor build-up"),
   slide_s=("Waterproofing", "Stone coating", "Epoxy flooring"),
   lines_no="Product lines", lines_h2="Three product lines",
   lines_p="Waterproofing, wall coating and flooring systems for different project conditions.",
   lines=[("02", "Waterproofing materials", "Waterproofing", "waterproofing.html",
           "Primers, compound membranes, flexible cement, plugging and crystalline systems, topcoats, clear coatings and solvent-based PU.", "%%N_WP%% series",
           "assets/img/photo/hero-4.jpg"),
          ("03", "Stone-effect wall coating", "Stone-effect coating", "stone.html",
           "Water-based multi-colour granite-effect coating; five-layer build-up, seven-step sequence, over 90% visual match.", "%%N_SW%% colourways",
           "assets/img/photo/hero-3.jpg"),
          ("04", "Epoxy resin flooring", "Epoxy flooring", "epoxy.html",
           "Thin-build, self-levelling, clear, anti-static, water-based and structural repair systems.", "%%N_EPX%% systems",
           "assets/img/floor/epoxy-05.jpg")],
   app_no="Applications", app_h2="Find materials by application",
   app_p="Starting from the part of the building is faster than starting from a product category.",
   apps=[("05", "Roof waterproofing", "roof-waterproofing.html", "Build-ups and coverage rates for flat and metal roofs"),
         ("06", "Bathrooms and kitchens", "bathroom-waterproofing.html", "Sequence and detailing for internal wet areas"),
         ("07", "Basements and retaining walls", "basement-waterproofing.html", "Positive versus negative side; remedial sequence"),
         ("08", "External walls", "exterior-wall-coating.html", "Elastomeric, thermal, clear protective and stone-effect"),
         ("09", "Car parks and factory floors", "parking-floor.html", "Epoxy flooring systems mapped to facility type")],
   why_no="Services", why_h2="Materials are where it starts",
   why=[("Material specification", "A complete build-up of primer, membrane and topcoat matched to location, substrate, climate and programme, so incompatible products are never combined."),
        ("Sample panels", "For external decorative work, sample panels can be produced for client and supervisor approval and used as the reference at handover."),
        ("Supply and support", "Phased delivery to programme, pre-start briefings where required, and continuing technical assistance during installation.")],
   plates=[("assets/img/photo/hero-2.jpg", "External wall coating", "PH-01"),
           ("assets/img/floor/epoxy-05.jpg", "Car park flooring", "PH-02"),
           ("assets/img/photo/hero-4.jpg", "Roof waterproofing", "PH-03")],
 )
}


def build_home(lang):
    t, C, up = T[lang], HOME[lang], pfx(lang)
    d = dep(lang)
    u = "../" if lang == "en" else ""
    path = "/en/" if lang == "en" else "/"
    org = {"@context": "https://schema.org", "@type": ["Organization", "LocalBusiness"],
           "@id": SITE + "/#organization", "name": T["zh"]["co"],
           "alternateName": ["暉盈國際", "Huiying Int'l Business Co.", "Huiying Materials"],
           "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/brand/icon-512.png"},
           "image": SITE + "/assets/img/brand/og-image.jpg", "taxID": "%%TAX%%",
           "email": "%%EMAIL%%", "telephone": "%%TEL1_INTL%%",
           "faxNumber": "%%FAX_INTL%%",
           "address": {"@type": "PostalAddress", "streetAddress": "%%LD_STREET%%",
                       "addressLocality": "%%LD_DISTRICT%%", "addressRegion": "%%LD_CITY%%",
                       "postalCode": "%%POSTCODE%%", "addressCountry": "TW"},
           "areaServed": {"@type": "Country", "name": "台灣"},
           "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
               "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
               "opens": "08:30", "closes": "17:30"}],
           "hasOfferCatalog": {"@type": "OfferCatalog", "name": "產品線", "itemListElement": [
               {"@type": "OfferCatalog", "name": n, "url": SITE + "/" + h}
               for _, n, _, h, _, _, _ in C["lines"]]}}
    site = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website",
            "url": SITE + "/", "name": T["zh"]["co"], "inLanguage": t["lang"],
            "publisher": {"@id": SITE + "/#organization"}}

    lines = "".join(
        f'<a class="card" href="{u}{h}">'
        f'<span class="ph"><img src="{u}{img}" alt=""></span>'
        f'<span class="bd"><h3>{n}</h3><span class="en">{en}</span>'
        f'<p>{ds}</p><span class="go">{cnt} →</span></span></a>'
        for no, n, en, h, ds, cnt, img in C["lines"])
    apps = "".join(
        f'<a href="{u}{h}">'
        f'<h3>{n}</h3><span class="desc">{ds}</span><span class="go">→</span></a>'
        for no, n, h, ds in C["apps"])
    why = "".join(
        f'<div style="flex:1 1 280px;min-width:0"><h3 style="font-size:19px;margin-bottom:9px">{h}</h3>'
        f'<p style="color:var(--ink-2);font-size:14.5px">{p}</p></div>' for h, p in C["why"])

    # 版頭輪播：三張剖面圖（防水／仿石／地坪），只留一行小標，自動輪播＋可滑動
    slides = [(F.fig_roof(anim=True, rev=True, labels=False, scale=1.6, lang=lang), C["slide_a"][0], C["slide_s"][0]),
              (F.fig_stone(rev=True, labels=False, scale=1.15, lang=lang), C["slide_a"][1], C["slide_s"][1]),
              (F.fig_floor(rev=True, labels=False, scale=1.6, lang=lang), C["slide_a"][2], C["slide_s"][2])]
    sl = "".join(f'<div class="sl"><figure class="section-fig rev">{svg}'
                 f'<figcaption><b>{a}</b><span>{sub}</span></figcaption></figure></div>'
                 for svg, a, sub in slides)
    dots = "".join(f'<button type="button" aria-label="{a}" aria-current="{"true" if i == 0 else "false"}"></button>'
                   for i, (_, a, _) in enumerate(slides))
    slider = (f'<div class="figslider" id="figSlider"><div class="trk">{sl}</div>'
              f'<div class="dots">{dots}</div></div>')

    o = [head(lang, C["title"], C["desc"], path, ld=ld(org, site), depth=d, kw=C["kw"],
              preload=f'{u}assets/img/photo/hero-2.jpg'),
         titleblock(lang, "index.html"),
         masthead(lang, "index.html", depth=d),
         hero(lang, photo=f'{u}assets/img/photo/hero-2.jpg',
              h1=C["h1"], lead=C["lead"], figure=slider,
              acts=[(C["lines"][0][1], u + C["lines"][0][3], "rev"),
                    (T[lang]["ask"][0], u + "contact.html", "ghost")]),
         f'''
<section class="band">
  <div class="page">
    <div class="cap"><p>{C["lines_p"]}</p></div>
    <div class="cards">{lines}</div>
  </div>
</section>

<section class="band dark">
  <div class="page">
    <div class="cap"><div class="no">{C["app_no"]}</div><h2>{C["app_h2"]}</h2><p>{C["app_p"]}</p></div>
    <div class="index">{apps}</div>
  </div>
</section>

<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{C["why_no"]}</div><h2>{C["why_h2"]}</h2></div>
    <div style="display:flex;flex-wrap:wrap;gap:36px">{why}</div>
  </div>
</section>''',
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "index.html", uniq_svg_ids("\n".join(o)))


# ══════════════════════════════════════════ 產品線頁（防水／環氧）

PROD = {
 "waterproofing": {
   "zh": dict(sheet="waterproofing.html",
     title="防水材料｜屋頂、外牆、浴廁、地下室防水｜暉盈國際",
     desc="建築防水材料%%N_WP_ZH%%大系列：防水底漆、複合式防水塗膜、彈性水泥、止水灰泥與滲透結晶、面漆、透明保護漆與油性 PU 防水系統，含適用部位與參考塗佈量。",
     kw="防水材料, 屋頂防水, 彈性水泥, PU防水, 滲透結晶防水材",
     tag="材料明細", h1="建築防水材料", lead="%%N_WP_ZH%%大系列。從素地封閉、主防水層、彈性水泥到面漆保護與 PU 系統，依部位與基材選出完整配套。",
     figcap="標準三層構成", figcode="大樣 A-01", fig=F.fig_roof,
     cap_no="系列明細", cap_h2="%%N_WP_ZH%%大系列", cap_p="前三項構成主要的防水層次，後四項依部位與既有狀況搭配。",
     h5a="產品特性", h5b="適用部位", h5c="參考規格",
     photo=("assets/img/photo/hero-4.jpg", "屋頂防水施作", "PH-11"),
     faq_h="常見問題"),
   "en": dict(sheet="waterproofing.html",
     title="Waterproofing Materials｜Roofs, Walls, Wet Rooms, Basements｜Huiying",
     desc="%%N_WP_EN%% series of waterproofing materials: primers, compound membranes, flexible cement, plugging and crystalline systems, topcoats and PU.",
     kw="waterproofing materials, roof waterproofing, flexible cement, PU waterproofing",
     tag="Material schedule", h1="Waterproofing materials",
     lead="%%N_WP_EN%% series, from substrate sealing and the main membrane through to topcoat protection and full PU systems.",
     figcap="Standard three-layer build-up", figcode="Detail A-01", fig=F.fig_roof,
     cap_no="Schedule", cap_h2="%%N_WP_EN%% series",
     cap_p="The first three form the principal build-up; the remaining four are selected by location and existing condition.",
     h5a="Characteristics", h5b="Applications", h5c="Reference",
     photo=("assets/img/photo/hero-4.jpg", "Roof waterproofing", "PH-11"),
     faq_h="Frequently asked questions"),
 },
}

FAQ_WP = {
 "zh": [("屋頂防水材料要選哪一種？",
   "先確認四件事：基材種類與狀況、排水是否順暢、屋頂上不上人、以及可施工的天數。一般 RC 平屋頂的標準配置是「底漆 → 複合式防水主材 → 面漆」三層；會積水或上人的屋頂則建議改用油性 PU 系統。"),
  ("彈性水泥和 PU 防水材有什麼差別？",
   "彈性水泥是雙組份的樹脂加骨材，與混凝土基材相容性最好，適合浴室、廚房等室內夾層防水，無氣味。油性 PU 是二液型聚氨酯，塗膜強度、伸長率與耐水性最好，適合會積水、上人或有機械磨損的部位，但單價較高且需要精確配比。"),
  ("防水做完不到兩年又漏水，是材料的問題嗎？",
   "多數情況不是。最常見的原因依序是：基材含水率太高就施作、沒有清除粉化層與失效的舊塗層、裂縫沒有先補強就直接塗覆、女兒牆與落水頭等細部處理不確實、以及塗佈量不足或工序間隔不夠。"),
  ("塗佈量要怎麼估算？",
   "用「施作面積 × 建議塗佈量 × 道數」計算。例如 100 m² 的屋頂使用建議塗佈量 0.6 kg/m² 的材料塗兩道，需要約 120 kg。實際用量會因基材粗糙度而增加，估料時建議多抓 10–15%。"),
  ("潮濕的表面可以施工嗎？",
   "多數水性防水材要求含水率在 10% 以下。但滲透結晶型與部分止水材料可以在潮濕面施作，因為它們是靠與混凝土反應生成結晶來填塞毛孔，本來就需要水分參與反應。"),
  ("有提供技術諮詢或樣板嗎？",
   "有。提供施作部位、基材狀況、面積與預計工期後，我們會回覆完整的材料配套建議與用量估算。外牆裝飾工程可先製作樣板，經監造單位與業主確認後作為施工驗收的比對憑據。")],
 "en": [("How do I choose a roof waterproofing material?",
   "Confirm four things first: substrate type and condition, drainage, whether the roof takes foot traffic, and the number of workable days available. For a standard flat concrete roof the build-up is primer, compound membrane and topcoat. Roofs that pond water or take traffic are better served by a solvent-based PU system."),
  ("What is the difference between flexible cement and PU?",
   "Flexible cement is a two-part resin and aggregate system with the best compatibility with concrete, suited to internal wet areas and free of odour. Solvent-based PU is a two-part polyurethane with the highest film strength, elongation and water resistance, suited to ponding or trafficked areas, but it costs more and requires accurate mixing."),
  ("The roof leaked again within two years. Is that a material fault?",
   "Usually not. The most common causes, in order, are: applying over a substrate that is still too wet; failing to remove chalking and failed coatings; coating over cracks without reinforcement; poor detailing at parapets and outlets; and insufficient coverage or inadequate recoat intervals."),
  ("How do I calculate how much material is needed?",
   "Area × coverage rate × number of coats. For example, 100 m² at 0.6 kg/m² over two coats requires around 120 kg. Rough substrates increase consumption, so allow an additional 10–15% when estimating."),
  ("Can material be applied to a damp surface?",
   "Most water-based products require moisture content below 10%. Crystalline penetrating and plugging materials are the exception — they rely on moisture to react with the concrete and form sealing crystals."),
  ("Do you provide technical advice or sample panels?",
   "Yes. Send us the location, substrate condition, area and programme and we will return a complete material specification with quantity estimates. Sample panels can be produced for external decorative work.")],
}


def brief_split(desc, lang):
    """取第一句作為收合列的簡述，其餘留給展開後的內文"""
    sep = "。" if lang == "zh" else ". "
    i = desc.find(sep)
    if i < 0:
        return desc, ""
    cut = i + len(sep)
    return desc[:cut].strip(), desc[cut:].strip()


def series_rows(lang, series, h5a, h5b, h5c):
    """收合式明細列：summary 露出 名稱＋小標＋一句簡述，展開才有特性與規格"""
    out = []
    n = 0
    for s in series:
        if s.get("k"):          # 指定標記（如「基礎」），不列入編號
            k = s["k"]
        else:
            n += 1; k = f"{n:02d}"
        feats = "".join(f"<li>{x}</li>" for x in s["feat"])
        data = "".join(f'<div><span>{k}</span><b>{v}</b></div>' for k, v in s["spec"])
        b, _ = brief_split(s["desc"], lang)
        role = f'<span class="role">{s["tagline"]}</span>' if s.get("tagline") else ""
        rp = f'<p>{s["desc"]}</p>'
        out.append(f'''<details class="acc" id="{s["id"]}">
  <summary>
    <span class="k">{k}</span>
    <span class="t"><h3>{s["name"]}</h3>{role}</span>
    <span class="brief">{b}</span>
    <span class="tg" aria-hidden="true"></span>
  </summary>
  <div class="rb">
    {rp}
    <div class="cols">
      <div><h5>{h5a}</h5><ul class="marks">{feats}</ul></div>
      <div><h5>{h5b}</h5><p class="use">{s["use"]}</p></div>
      <div><h5>{h5c}</h5><div class="data">{data}</div></div>
    </div>
  </div>
</details>''')
    return "".join(out)


def build_waterproofing(lang):
    C = PROD["waterproofing"][lang]
    d, u, up = dep(lang), ("../" if lang == "en" else ""), pfx(lang)
    path = f"/{up}waterproofing.html"
    series = DATA[lang]["SERIES"]
    jump = "".join(f'<a href="#{s["id"]}">{s["name"]}</a>' for s in series)
    src, cap, code = C["photo"]

    o = [head(lang, C["title"], C["desc"], path, depth=d, kw=C["kw"], preload=u + src,
              ld=ld(crumb(lang, [(T[lang]["nav"][0][0], f"/{up}"), (C["h1"], path)]),
                    faq_ld(FAQ_WP[lang]),
                    list_ld(C["cap_h2"], path, [(s["name"], s["id"]) for s in series]))),
         titleblock(lang, "waterproofing.html"),
         masthead(lang, "waterproofing.html", depth=d),
         hero(lang, photo=u + src, tag=C["tag"], h1=C["h1"], lead=C["lead"], sub=True,
              figure=fig(C["fig"](rev=True, lang=lang), C["figcap"], C["figcode"], rev=True)),
         f'''
<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{C["cap_no"]}</div><h2>{C["cap_h2"]}</h2><p>{C["cap_p"]}</p></div>
    <div class="jump">{jump}</div>
    <div class="schedule">{series_rows(lang, series, C["h5a"], C["h5b"], C["h5c"])}</div>
  </div>
</section>''',
         qa_block(FAQ_WP[lang], C["faq_h"]),
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "waterproofing.html", "\n".join(o))
